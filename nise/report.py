#
# Copyright 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Module responsible for generating the cost and usage report."""
import base64
import calendar
import copy
import csv
import gzip
import importlib
import json
import os
import random
import shutil
import string
import tarfile
from datetime import datetime
from random import randint
from tempfile import gettempdir
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory
from uuid import uuid4

import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta
from faker import Faker
from nise.copy import copy_to_local_dir
from nise.extract import extract_payload
from nise.generators.aws import DataTransferGenerator
from nise.generators.aws import EBSGenerator
from nise.generators.aws import EC2Generator
from nise.generators.aws import RDSGenerator
from nise.generators.aws import Route53Generator
from nise.generators.aws import S3Generator
from nise.generators.aws import VPCGenerator
from nise.generators.azure import AZURE_COLUMNS
from nise.generators.azure import BandwidthGenerator
from nise.generators.azure import SQLGenerator
from nise.generators.azure import StorageGenerator
from nise.generators.azure import VMGenerator
from nise.generators.azure import VNGenerator
from nise.generators.gcp import CloudStorageGenerator
from nise.generators.gcp import ComputeEngineGenerator
from nise.generators.gcp import GCP_REPORT_COLUMNS
from nise.generators.gcp import ProjectGenerator
from nise.generators.ocp import OCP_NODE_LABEL
from nise.generators.ocp import OCP_POD_USAGE
from nise.generators.ocp import OCP_REPORT_TYPE_TO_COLS
from nise.generators.ocp import OCP_STORAGE_USAGE
from nise.generators.ocp import OCPGenerator
from nise.manifest import aws_generate_manifest
from nise.manifest import ocp_generate_manifest
from nise.upload import upload_to_azure_container
from nise.upload import upload_to_gcp_storage
from nise.upload import upload_to_s3
from nise.util import LOG


def create_temporary_copy(path, temp_file_name, temp_dir_name="None"):
    """Create temporary copy of a file."""
    temp_dir = gettempdir()
    if temp_dir_name:
        new_dir = os.path.join(temp_dir, temp_dir_name)
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        temp_path = os.path.join(new_dir, temp_file_name)
    else:
        temp_path = os.path.join(temp_dir, temp_file_name)
    shutil.copy2(path, temp_path)
    return temp_path


def _write_csv(output_file, data, header):
    """Output csv file data."""
    LOG.info(f"Writing to {output_file.split('/')[-1]}")
    with open(output_file, "w") as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def _remove_files(file_list):
    """Remove files."""
    for file_path in file_list:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            LOG.error(f"File {file_path} was not found.")
            raise FileNotFoundError


def _generate_azure_filename():
    """Generate filename for azure report."""
    output_file_name = "{}_{}".format("costreport", uuid4())
    local_path = "{}/{}.csv".format(os.getcwd(), output_file_name)
    output_file_name = output_file_name + ".csv"
    return (local_path, output_file_name)


def _generate_azure_date_range(month):
    start = month.get("start").replace(day=1)
    end = start + relativedelta(months=+1, days=-1)
    return start.strftime("%Y%m%d") + "-" + end.strftime("%Y%m%d")


def _gzip_report(report_path):
    """Compress the report."""
    t_file = NamedTemporaryFile(mode="wb", suffix=".csv.gz", delete=False)
    with open(report_path, "rb") as f_in, gzip.open(t_file.name, "wb") as f_out:
        f_out.write(f_in.read())
    return t_file.name


def _tar_gzip_report(temp_dir):
    """Compress the report and manifest to tarfile."""
    t_file = NamedTemporaryFile(mode="w", suffix=".tar.gz", delete=False)

    with tarfile.open(t_file.name, "w:gz") as tar:
        tar.add(temp_dir, arcname=os.path.sep)

    return t_file.name


def _tar_gzip_report_files(file_list):
    """Compress the file list to a tarfile."""
    with TemporaryDirectory() as t_directory:
        for report_file in file_list:
            temp_path = os.path.join(t_directory, os.path.basename(report_file))
            shutil.copy2(report_file, temp_path)
        fname = _tar_gzip_report(t_directory)

    return fname


def _write_manifest(data):
    """Write manifest file to temp location.

    Args:
        data    (String): data to store
    Returns:
        (String): Path to temporary file

    """
    t_file = NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    t_file.write(data)
    t_file.flush()
    return t_file.name


def aws_route_file(bucket_name, bucket_file_path, local_path):
    """Route file to either S3 bucket or local filesystem."""
    if os.path.isdir(bucket_name):
        copy_to_local_dir(bucket_name, local_path, bucket_file_path)
    else:
        upload_to_s3(bucket_name, bucket_file_path, local_path)


def azure_route_file(storage_account_name, storage_file_name, local_path, storage_file_path=None):
    """Route file to either storage account or local filesystem."""
    connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if storage_file_path and connect_str:
        upload_to_azure_container(storage_file_name, local_path, storage_file_path)
    else:
        copy_to_local_dir(storage_account_name, local_path, storage_file_name)


def ocp_route_file(insights_upload, local_path):
    """Route file to either Upload Service or local filesystem."""
    if os.path.isdir(insights_upload):
        extract_payload(insights_upload, local_path)
    else:
        response = post_payload_to_ingest_service(insights_upload, local_path)
        if response.status_code == 202:
            LOG.info("File uploaded successfully.")
        else:
            LOG.error(f"{response.status_code} File upload failed.")

        LOG.info(response.text)


def gcp_route_file(bucket_name, bucket_file_path, local_path):
    """Route file to either GCP bucket or local filesystem."""
    if os.path.isdir(bucket_name):
        copy_to_local_dir(bucket_name, bucket_file_path, local_path)
    else:
        upload_to_gcp_storage(bucket_name, bucket_file_path, local_path)


def _convert_bytes(num):
    """Convert bytes to MB, GB, etc.."""
    for mem_size in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return f"{num:3.1f} {mem_size}"
        num /= 1024.0
    return None


def post_payload_to_ingest_service(insights_upload, local_path):
    """POST the payload to Insights via header or basic auth."""
    insights_account_id = os.environ.get("INSIGHTS_ACCOUNT_ID")
    insights_org_id = os.environ.get("INSIGHTS_ORG_ID")
    insights_user = os.environ.get("INSIGHTS_USER")
    insights_password = os.environ.get("INSIGHTS_PASSWORD")
    if os.path.isfile(local_path):
        file_info = os.stat(local_path)
        filesize = _convert_bytes(file_info.st_size)
    LOG.info(f"Upload File: ({local_path}) filesize is {filesize}.")
    with open(local_path, "rb") as upload_file:
        if insights_account_id and insights_org_id:
            header = {"identity": {"account_number": insights_account_id, "internal": {"org_id": insights_org_id}}}
            headers = {"x-rh-identity": base64.b64encode(json.dumps(header).encode("UTF-8"))}
            return requests.post(
                insights_upload,
                data={},
                files={"file": ("payload.tar.gz", upload_file, "application/vnd.redhat.hccm.tar+tgz")},
                headers=headers,
            )

        return requests.post(
            insights_upload,
            data={},
            files={"file": ("payload.tar.gz", upload_file, "application/vnd.redhat.hccm.tar+tgz")},
            auth=(insights_user, insights_password),
            verify=False,
        )


def _create_month_list(start_date, end_date):
    """Create a list of months given the date range args."""
    months = []
    current = start_date.replace(day=1)
    while current <= end_date:
        month = {
            "name": calendar.month_name[current.month],
            "start": datetime(year=current.year, month=current.month, day=1),
            "end": datetime(
                year=current.year,
                month=current.month,
                day=calendar.monthrange(year=current.year, month=current.month)[1],
                hour=23,
                minute=59,
            ),
        }
        if current.month == start_date.month:
            # First month start with start_date
            month["start"] = start_date
        if current.month == end_date.month:
            # Last month ends with end_date
            month["end"] = end_date.replace(hour=23, minute=59)

        months.append(month)
        current += relativedelta(months=+1)

    return months


def _aws_finalize_report(data, static_data=None):
    """Populate invoice id for data."""
    data = copy.deepcopy(data)

    invoice_id = None
    if static_data and static_data.get("finalized_report"):
        invoice_id = static_data.get("finalized_report").get("invoice_id")

    if not invoice_id:
        invoice_id = "".join([random.choice(string.digits) for _ in range(9)])
    for row in data:
        row["bill/InvoiceId"] = invoice_id

    return data


def _generate_accounts(static_report_data=None):
    """Generate payer and usage accounts."""
    if static_report_data:
        payer_account = static_report_data.get("payer")
        usage_accounts = tuple(static_report_data.get("user"))
    else:
        fake = Faker()
        payer_account = fake.ean(length=13)
        usage_accounts = (
            payer_account,
            fake.ean(length=13),
            fake.ean(length=13),
            fake.ean(length=13),
            fake.ean(length=13),
        )
    return payer_account, usage_accounts


def _get_generators(generator_list):
    """Collect a list of report generators."""
    generators = []
    if generator_list:
        for item in generator_list:
            for generator_cls, attributes in item.items():
                generator_obj = {"generator": getattr(importlib.import_module(__name__), generator_cls)}
                if attributes.get("start_date"):
                    attributes["start_date"] = parser.parse(attributes.get("start_date"))
                if attributes.get("end_date"):
                    attributes["end_date"] = parser.parse(attributes.get("end_date"))
                generator_obj["attributes"] = attributes
                generators.append(generator_obj)
    return generators


def _create_generator_dates_from_yaml(attributes, month):
    """Calculate generator start and end dates based on yaml and current month."""
    gen_start_date = None
    gen_end_date = None

    # Generator range is larger then current month on both start and end
    if attributes.get("start_date") < month.get("start") and attributes.get("end_date") > month.get("end").replace(
        hour=23, minute=59, second=59
    ):
        gen_start_date = month.get("start")
        gen_end_date = month.get("end") + relativedelta(days=1)

    # Generator starts before month start and ends within month
    if attributes.get("start_date") <= month.get("start") and attributes.get("end_date") <= month.get("end").replace(
        hour=23, minute=59, second=59
    ):
        gen_start_date = month.get("start")
        gen_end_date = attributes.get("end_date").replace(hour=23, minute=59)

    # Generator is within month
    if attributes.get("start_date") >= month.get("start") and attributes.get("end_date") <= month.get("end").replace(
        hour=23, minute=59, second=59
    ):
        gen_start_date = attributes.get("start_date")
        gen_end_date = attributes.get("end_date").replace(hour=23, minute=59)

    # Generator starts within month and ends in next month
    if attributes.get("start_date") >= month.get("start") and attributes.get("end_date") > month.get("end").replace(
        hour=23, minute=59, second=59
    ):
        gen_start_date = attributes.get("start_date")
        gen_end_date = month.get("end") + relativedelta(days=1)

    return gen_start_date, gen_end_date


def write_aws_file(
    file_number, aws_report_name, month_name, year, data, aws_finalize_report, static_report_data, headers
):
    """Write AWS data to a file."""
    headers = sorted(list(headers))
    if file_number != 0:
        file_name = "{}-{}-{}-{}".format(month_name, year, aws_report_name, str(file_number))
    else:
        file_name = f"{month_name}-{year}-{aws_report_name}"

    if aws_finalize_report and aws_finalize_report == "overwrite":
        data = _aws_finalize_report(data, static_report_data)
    elif aws_finalize_report and aws_finalize_report == "copy":
        # Currently only a local option as this does not simulate
        finalized_data = _aws_finalize_report(data, static_report_data)
        file_name_finalized = f"{file_name}-finalized"
        full_file_name = "{}/{}.csv".format(os.getcwd(), file_name_finalized)
        _write_csv(full_file_name, finalized_data, headers)

    full_file_name = "{}/{}.csv".format(os.getcwd(), file_name)
    _write_csv(full_file_name, data, headers)

    return full_file_name


def aws_create_report(options):  # noqa: C901
    """Create a cost usage report file."""
    data = []
    start_date = options.get("start_date")
    end_date = options.get("end_date")
    aws_finalize_report = options.get("aws_finalize_report")
    static_report_data = options.get("static_report_data")

    if static_report_data:
        generators = _get_generators(static_report_data.get("generators"))
        accounts_list = static_report_data.get("accounts")
    else:
        generators = [
            {"generator": DataTransferGenerator, "attributes": None},
            {"generator": EBSGenerator, "attributes": None},
            {"generator": EC2Generator, "attributes": None},
            {"generator": S3Generator, "attributes": None},
            {"generator": RDSGenerator, "attributes": None},
            {"generator": Route53Generator, "attributes": None},
            {"generator": VPCGenerator, "attributes": None},
        ]
        accounts_list = None

    months = _create_month_list(start_date, end_date)

    payer_account, usage_accounts = _generate_accounts(accounts_list)

    aws_bucket_name = options.get("aws_bucket_name")
    aws_report_name = options.get("aws_report_name")
    write_monthly = options.get("write_monthly", False)
    for month in months:
        data = []
        file_number = 0
        monthly_files = []
        fake = Faker()
        num_gens = len(generators)
        ten_percent = int(num_gens * 0.1) if num_gens > 50 else 5
        LOG.info(f"Producing data for {num_gens} generators for {month.get('start').strftime('%Y-%m')}.")
        for count, generator in enumerate(generators):
            generator_cls = generator.get("generator")
            attributes = generator.get("attributes")
            gen_start_date = month.get("start")
            gen_end_date = month.get("end")
            if attributes:
                # Skip if generator usage is outside of current month
                if attributes.get("end_date") < month.get("start"):
                    continue
                if attributes.get("start_date") > month.get("end"):
                    continue

                gen_start_date, gen_end_date = _create_generator_dates_from_yaml(attributes, month)

            gen = generator_cls(
                gen_start_date, gen_end_date, payer_account, usage_accounts, attributes, options.get("aws_tags")
            )
            num_instances = 1 if attributes else randint(2, 60)
            for _ in range(num_instances):
                for hour in gen.generate_data():
                    data += [hour]
                    if len(data) == options.get("row_limit"):
                        file_number += 1
                        month_output_file = write_aws_file(
                            file_number,
                            aws_report_name,
                            month.get("name"),
                            gen_start_date.year,
                            data,
                            aws_finalize_report,
                            static_report_data,
                            gen.AWS_COLUMNS,
                        )
                        monthly_files.append(month_output_file)
                        data.clear()

            if count % ten_percent == 0:
                LOG.info(f"Done with {count} of {num_gens} generators.")

        if file_number != 0:
            file_number += 1
        month_output_file = write_aws_file(
            file_number,
            aws_report_name,
            month.get("name"),
            gen_start_date.year,
            data,
            aws_finalize_report,
            static_report_data,
            gen.AWS_COLUMNS,
        )
        monthly_files.append(month_output_file)

        if aws_bucket_name:
            manifest_values = {"account": payer_account}
            manifest_values.update(options)
            manifest_values["start_date"] = gen_start_date
            manifest_values["end_date"] = gen_end_date
            manifest_values["file_names"] = monthly_files
            s3_cur_path, manifest_data = aws_generate_manifest(fake, manifest_values)
            s3_month_path = os.path.dirname(s3_cur_path)
            s3_month_manifest_path = s3_month_path + "/" + aws_report_name + "-Manifest.json"
            s3_assembly_manifest_path = s3_cur_path + "/" + aws_report_name + "-Manifest.json"

            temp_manifest = _write_manifest(manifest_data)
            aws_route_file(aws_bucket_name, s3_month_manifest_path, temp_manifest)
            aws_route_file(aws_bucket_name, s3_assembly_manifest_path, temp_manifest)

            for monthly_file in monthly_files:
                temp_cur_zip = _gzip_report(monthly_file)
                destination_file = "{}/{}.gz".format(s3_cur_path, os.path.basename(monthly_file))
                aws_route_file(aws_bucket_name, destination_file, temp_cur_zip)
                os.remove(temp_cur_zip)
            os.remove(temp_manifest)
        if not write_monthly:
            _remove_files(monthly_files)


def azure_create_report(options):  # noqa: C901
    """Create a cost usage report file."""
    data = []
    start_date = options.get("start_date")
    end_date = options.get("end_date")
    static_report_data = options.get("static_report_data")
    if static_report_data:
        generators = _get_generators(static_report_data.get("generators"))
        accounts_list = static_report_data.get("accounts")
    else:
        generators = [
            {"generator": BandwidthGenerator, "attributes": {}},
            {"generator": SQLGenerator, "attributes": {}},
            {"generator": StorageGenerator, "attributes": {}},
            {"generator": VMGenerator, "attributes": {}},
            {"generator": VNGenerator, "attributes": {}},
        ]
        accounts_list = None

    months = _create_month_list(start_date, end_date)

    payer_account, usage_accounts = _generate_accounts(accounts_list)

    meter_cache = {}
    # The options params are not going to change so we don't
    # have to keep resetting the var inside of the for loop
    azure_container_name = options.get("azure_container_name")
    storage_account_name = options.get("azure_account_name")
    azure_prefix_name = options.get("azure_prefix_name")
    azure_report_name = options.get("azure_report_name")
    write_monthly = options.get("write_monthly", False)
    for month in months:
        data = []
        monthly_files = []
        num_gens = len(generators)
        ten_percent = int(num_gens * 0.1) if num_gens > 50 else 5
        LOG.info(f"Producing data for {num_gens} generators for {month.get('start').strftime('%Y-%m')}.")
        for count, generator in enumerate(generators):
            generator_cls = generator.get("generator")
            attributes = generator.get("attributes", {})
            gen_start_date = month.get("start")
            gen_end_date = month.get("end")
            if attributes:
                # Skip if generator usage is outside of current month
                if attributes.get("end_date") < month.get("start"):
                    continue
                if attributes.get("start_date") > month.get("end"):
                    continue
            else:
                attributes = {"end_date": end_date, "start_date": start_date}

            gen_start_date, gen_end_date = _create_generator_dates_from_yaml(attributes, month)

            if attributes.get("meter_cache"):
                meter_cache.update(attributes.get("meter_cache"))  # needed so that meter_cache can be defined in yaml
            attributes["meter_cache"] = meter_cache
            gen = generator_cls(gen_start_date, gen_end_date, payer_account, usage_accounts, attributes)
            data += gen.generate_data()
            meter_cache = gen.get_meter_cache()

            if count % ten_percent == 0:
                LOG.info(f"Done with {count} of {num_gens} generators.")

        local_path, output_file_name = _generate_azure_filename()
        date_range = _generate_azure_date_range(month)

        _write_csv(local_path, data, AZURE_COLUMNS)
        monthly_files.append(local_path)

        if azure_container_name:
            file_path = ""
            if azure_prefix_name:
                file_path += azure_prefix_name + "/"
            file_path += azure_report_name + "/"
            file_path += date_range + "/"
            file_path += output_file_name

            # azure blob upload
            storage_account_name = options.get("azure_account_name", None)
            if storage_account_name:
                azure_route_file(storage_account_name, azure_container_name, local_path, file_path)
            # local dir upload
            else:
                azure_route_file(azure_container_name, file_path, local_path)
        if not write_monthly:
            _remove_files(monthly_files)


def write_ocp_file(file_number, cluster_id, month_name, year, report_type, data):
    """Write OCP data to a file."""
    if file_number != 0:
        file_name = "{}-{}-{}-{}-{}".format(month_name, year, cluster_id, report_type, str(file_number))
    else:
        file_name = f"{month_name}-{year}-{cluster_id}-{report_type}"

    full_file_name = "{}/{}.csv".format(os.getcwd(), file_name)
    _write_csv(full_file_name, data, OCP_REPORT_TYPE_TO_COLS[report_type])

    return full_file_name


def ocp_create_report(options):  # noqa: C901
    """Create a usage report file."""
    start_date = options.get("start_date")
    end_date = options.get("end_date")
    cluster_id = options.get("ocp_cluster_id")
    static_report_data = options.get("static_report_data")
    if static_report_data:
        generators = _get_generators(static_report_data.get("generators"))
    else:
        generators = [{"generator": OCPGenerator, "attributes": None}]

    months = _create_month_list(start_date, end_date)
    insights_upload = options.get("insights_upload")
    write_monthly = options.get("write_monthly", False)
    for month in months:
        data = {OCP_POD_USAGE: [], OCP_STORAGE_USAGE: [], OCP_NODE_LABEL: []}
        file_numbers = {OCP_POD_USAGE: 0, OCP_STORAGE_USAGE: 0, OCP_NODE_LABEL: 0}
        monthly_files = []
        for generator in generators:
            generator_cls = generator.get("generator")
            attributes = generator.get("attributes")
            gen_start_date = month.get("start")
            gen_end_date = month.get("end")
            if attributes:
                # Skip if generator usage is outside of current month
                if attributes.get("end_date") < month.get("start"):
                    continue
                if attributes.get("start_date") > month.get("end"):
                    continue

                gen_start_date, gen_end_date = _create_generator_dates_from_yaml(attributes, month)

            gen = generator_cls(gen_start_date, gen_end_date, attributes)
            for report_type in gen.ocp_report_generation.keys():
                LOG.info(f"Generating data for {report_type} for {month.get('name')}")
                for hour in gen.generate_data(report_type):
                    data[report_type] += [hour]
                    if len(data[report_type]) == options.get("row_limit"):
                        file_numbers[report_type] += 1
                        month_output_file = write_ocp_file(
                            file_numbers[report_type],
                            cluster_id,
                            month.get("name"),
                            gen_start_date.year,
                            report_type,
                            data[report_type],
                        )
                        monthly_files.append(month_output_file)
                        data[report_type].clear()

        for report_type in gen.ocp_report_generation.keys():
            if file_numbers[report_type] != 0:
                file_numbers[report_type] += 1

            month_output_file = write_ocp_file(
                file_numbers[report_type],
                cluster_id,
                month.get("name"),
                gen_start_date.year,
                report_type,
                data[report_type],
            )
            monthly_files.append(month_output_file)

        if insights_upload:
            # Generate manifest for all files
            ocp_assembly_id = uuid4()
            report_datetime = gen_start_date
            temp_files = {}
            for num_file in range(len(monthly_files)):
                temp_filename = f"{ocp_assembly_id}_openshift_report.{num_file}.csv"
                temp_usage_file = create_temporary_copy(monthly_files[num_file], temp_filename, "payload")
                temp_files[temp_filename] = temp_usage_file

            manifest_file_names = ", ".join(f'"{w}"' for w in temp_files)
            manifest_values = {
                "ocp_cluster_id": cluster_id,
                "ocp_assembly_id": ocp_assembly_id,
                "report_datetime": report_datetime,
                "files": manifest_file_names[1:-1],
            }
            manifest_data = ocp_generate_manifest(manifest_values)
            temp_manifest = _write_manifest(manifest_data)
            temp_manifest_name = create_temporary_copy(temp_manifest, "manifest.json", "payload")

            # Tarball and upload files individually
            for temp_usage_file in temp_files.values():
                report_files = [temp_usage_file, temp_manifest_name]
                temp_usage_zip = _tar_gzip_report_files(report_files)
                ocp_route_file(insights_upload, temp_usage_zip)
                os.remove(temp_usage_file)
                os.remove(temp_usage_zip)

            os.remove(temp_manifest)
            os.remove(temp_manifest_name)
        if not write_monthly:
            LOG.info("Cleaning up local directory")
            _remove_files(monthly_files)


def gcp_create_report(options):  # noqa: C901
    """Create a GCP cost usage report file."""
    fake = Faker()

    report_prefix = options.get("gcp_report_prefix") or fake.word()
    gcp_bucket_name = options.get("gcp_bucket_name")

    start_date = options.get("start_date")
    end_date = options.get("end_date")

    static_report_data = options.get("static_report_data")
    if static_report_data:
        generators = _get_generators(static_report_data.get("generators"))
        projects = static_report_data.get("projects")

    else:
        generators = [
            {"generator": CloudStorageGenerator, "attributes": None},
            {"generator": ComputeEngineGenerator, "attributes": None},
        ]
        account = "{}-{}".format(fake.word(), fake.word())

        project_generator = ProjectGenerator(account)
        projects = project_generator.generate_projects()

    data = {}
    for project in projects:
        num_gens = len(generators)
        ten_percent = int(num_gens * 0.1) if num_gens > 50 else 5
        LOG.info(f"Producing data for {num_gens} generators for {'INSERT SOMETHING FOR GCP'}.")
        for count, generator in enumerate(generators):
            attributes = generator.get("attributes", {})
            if attributes:
                start_date = attributes.get("start_date")
                end_date = attributes.get("end_date")

            generator_cls = generator.get("generator")
            gen = generator_cls(start_date, end_date, project, attributes=attributes)
            generated_data = gen.generate_data()
            for key, item in generated_data.items():
                if key in data:
                    data[key] += item
                else:
                    data[key] = item

            count += 1
            if count % ten_percent == 0:
                LOG.info(f"Done with {count} of {num_gens} generators.")

    monthly_files = []
    for day, daily_data in data.items():
        output_file_name = "{}-{}.csv".format(report_prefix, day.strftime("%Y-%m-%d"))

        output_file_path = os.path.join(os.getcwd(), output_file_name)
        monthly_files.append(output_file_path)
        _write_csv(output_file_path, daily_data, GCP_REPORT_COLUMNS)

    if gcp_bucket_name:
        gcp_route_file(gcp_bucket_name, output_file_path, output_file_name)

    write_monthly = options.get("write_monthly", False)
    if not write_monthly:
        _remove_files(monthly_files)
