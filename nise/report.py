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
from nise import __version__
from nise.copy import copy_to_local_dir
from nise.extract import extract_payload
from nise.generators.aws import DataTransferGenerator
from nise.generators.aws import EBSGenerator
from nise.generators.aws import EC2Generator
from nise.generators.aws import MarketplaceGenerator
from nise.generators.aws import RDSGenerator
from nise.generators.aws import Route53Generator
from nise.generators.aws import S3Generator
from nise.generators.aws import VPCGenerator
from nise.generators.azure import BandwidthGenerator
from nise.generators.azure import CCSPGenerator
from nise.generators.azure import SQLGenerator
from nise.generators.azure import StorageGenerator
from nise.generators.azure import VMGenerator
from nise.generators.azure import VNGenerator
from nise.generators.gcp import CloudStorageGenerator
from nise.generators.gcp import ComputeEngineGenerator
from nise.generators.gcp import GCP_REPORT_COLUMNS
from nise.generators.gcp import GCP_RESOURCE_COLUMNS
from nise.generators.gcp import GCPDatabaseGenerator
from nise.generators.gcp import GCPNetworkGenerator
from nise.generators.gcp import HCSGenerator
from nise.generators.gcp import JSONLCloudStorageGenerator
from nise.generators.gcp import JSONLComputeEngineGenerator
from nise.generators.gcp import JSONLGCPDatabaseGenerator
from nise.generators.gcp import JSONLGCPNetworkGenerator
from nise.generators.gcp import JSONLHCSGenerator
from nise.generators.gcp import JSONLProjectGenerator
from nise.generators.gcp import ProjectGenerator
from nise.generators.oci import OCIBlockStorageGenerator
from nise.generators.oci import OCIComputeGenerator
from nise.generators.oci import OCIDatabaseGenerator
from nise.generators.oci import OCINetworkGenerator
from nise.generators.oci.oci_generator import OCI_COST_REPORT
from nise.generators.oci.oci_generator import OCI_REPORT_TYPE_TO_COLS
from nise.generators.oci.oci_generator import OCI_USAGE_REPORT
from nise.generators.ocp import OCP_NAMESPACE_LABEL
from nise.generators.ocp import OCP_NODE_LABEL
from nise.generators.ocp import OCP_POD_USAGE
from nise.generators.ocp import OCP_REPORT_TYPE_TO_COLS
from nise.generators.ocp import OCP_STORAGE_USAGE
from nise.generators.ocp import OCPGenerator
from nise.manifest import aws_generate_manifest
from nise.manifest import ocp_generate_manifest
from nise.upload import gcp_bucket_to_dataset
from nise.upload import upload_to_azure_container
from nise.upload import upload_to_gcp_storage
from nise.upload import upload_to_oci_bucket
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


def _write_jsonl(output_file, data):
    """Output JSON Lines file data for bigquery."""
    LOG.info(f"Writing to {output_file.split('/')[-1]}")
    with open(output_file, "w") as file:
        for row in data:
            json.dump(row, file)
            # each dictionary "row" is its own line in a JSONL file
            file.write("\n")


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
    content_type = "application/vnd.redhat.hccm.tar+tgz"
    if os.path.isfile(local_path):
        file_info = os.stat(local_path)
        filesize = _convert_bytes(file_info.st_size)
    LOG.info(f"Upload File: ({local_path}) filesize is {filesize}.")
    with open(local_path, "rb") as upload_file:
        if insights_account_id and insights_org_id:
            header = {
                "identity": {
                    "account_number": insights_account_id,
                    "org_id": insights_org_id,
                    "internal": {"org_id": insights_org_id},
                    "type": content_type,
                }
            }
            headers = {"x-rh-identity": base64.b64encode(json.dumps(header).encode("UTF-8"))}
            return requests.post(
                insights_upload,
                data={},
                files={"file": ("payload.tar.gz", upload_file, content_type)},
                headers=headers,
            )

        return requests.post(
            insights_upload,
            data={},
            files={"file": ("payload.tar.gz", upload_file, content_type)},
            auth=(insights_user, insights_password),
            verify=False,
        )


def _create_month_list(start_date, end_date):
    """Create a list of months given the date range args."""
    months = []
    current = start_date.replace(day=1)
    end_month_first_day = end_date.replace(day=1)
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
        if current < end_month_first_day:
            # can not compare months in this case - January < December
            month["end"] = (month.get("end") + relativedelta(days=1)).replace(hour=0, minute=0)
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
        currency_code = static_report_data.get("currency_code")
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
        currency_code = "USD"
    return payer_account, usage_accounts, currency_code


def _generate_azure_account_info(static_report_data=None):
    """Return Azure subscription, billing, and usage account info."""
    fake = Faker()
    company_name = fake.company()
    company_email = company_name.replace(" ", "").replace(",", "")
    email_suffix = f"@{company_email}.com"
    subscription_name = f"{company_name} Azure Subscription"
    billing_account_id = fake.ean(length=8)
    billing_account_name = company_name
    accounts = []
    if static_report_data:
        subscription_guid = static_report_data.get("payer")
        usage_accounts = tuple(static_report_data.get("user"))
        currency_code = static_report_data.get("currency_code", "USD")
        for _ in usage_accounts:
            account_name = fake.city()
            trimmed_account_name = account_name.replace(" ", "")
            account_owner_id = f"{trimmed_account_name}{email_suffix}"
            accounts.append((account_name, account_owner_id))
    else:
        subscription_guid = fake.ean(length=13)
        usage_accounts = (
            subscription_guid,
            fake.ean(length=13),
            fake.ean(length=13),
            fake.ean(length=13),
            fake.ean(length=13),
        )
        currency_code = "USD"
        for _ in usage_accounts:
            account_name = fake.city()
            trimmed_account_name = account_name.replace(" ", "")
            account_owner_id = f"{trimmed_account_name}{email_suffix}"
            accounts.append((account_name, account_owner_id))
    account_info = {
        "subscription_guid": subscription_guid,
        "subscription_name": subscription_name,
        "billing_account_id": billing_account_id,
        "billing_account_name": billing_account_name,
        "usage_accounts": accounts,
        "currency_code": currency_code,
    }
    return account_info


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


def _get_jsonl_generators(generator_list):
    """Collect a list of report generators for use in GCP for bigquery uploads."""
    generators = []
    if generator_list:
        for item in generator_list:
            for generator_cls, attributes in item.items():
                generator_obj = {"generator": getattr(importlib.import_module(__name__), "JSONL" + generator_cls)}
                if attributes.get("start_date"):
                    attributes["start_date"] = parser.parse(attributes.get("start_date"))
                if attributes.get("end_date"):
                    attributes["end_date"] = parser.parse(attributes.get("end_date"))
                if attributes.get("currency"):
                    attributes["currency"] = attributes.get("currency")
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
        gen_end_date = month.get("end")

    # Generator starts before month start and ends within month
    if attributes.get("start_date") <= month.get("start") and attributes.get("end_date") <= month.get("end").replace(
        hour=23, minute=59, second=59
    ):
        gen_start_date = month.get("start")
        gen_end_date = attributes.get("end_date")

    # Generator is within month
    if attributes.get("start_date") >= month.get("start") and attributes.get("end_date") <= month.get("end").replace(
        hour=23, minute=59, second=59
    ):
        gen_start_date = attributes.get("start_date")
        gen_end_date = attributes.get("end_date")

    # Generator starts within month and ends in next month
    if attributes.get("start_date") >= month.get("start") and attributes.get("end_date") > month.get("end").replace(
        hour=23, minute=59, second=59
    ):
        gen_start_date = attributes.get("start_date")
        gen_end_date = month.get("end")

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


def default_currency(currency, static_currency):
    if currency:
        return currency
    elif static_currency:
        return static_currency
    else:
        return "USD"


def aws_create_marketplace_report(options):  # noqa: C901
    """Create a marketplace usage report file."""
    static_report_data = options.get("static_report_data")
    # added to keep import happy
    MarketplaceGenerator
    options["manifest_generation"] = True

    if static_report_data:
        aws_create_report(options)
    else:
        start = options.get("start_date").strftime("%Y%m%d")
        end = options.get("end_date").strftime("%Y%m%d")
        generators = {"generators": [{"MarketplaceGenerator": {"start_date": start, "end_date": end}}]}

        if not options.get("aws_report_name"):
            options["aws_report_name"] = "marketplace"
        else:
            options["aws_report_name"] = options.get("aws_report_name") + "-marketplace"

        options["static_report_data"] = generators
        options["accounts_list"] = None

        aws_create_report(options)


def aws_create_report(options):  # noqa: C901
    """Create a cost usage report file."""
    data = []
    start_date = options.get("start_date")
    end_date = options.get("end_date")
    aws_finalize_report = options.get("aws_finalize_report")
    static_report_data = options.get("static_report_data")
    manifest_gen = True if options.get("manifest_generation") is None else options.get("manifest_generation")

    if static_report_data:
        generators = _get_generators(static_report_data.get("generators"))
        accounts_list = static_report_data.get("accounts")
    else:
        generators = [
            {"generator": DataTransferGenerator, "attributes": {}},
            {"generator": EBSGenerator, "attributes": {}},
            {"generator": EC2Generator, "attributes": {}},
            {"generator": S3Generator, "attributes": {}},
            {"generator": RDSGenerator, "attributes": {}},
            {"generator": Route53Generator, "attributes": {}},
            {"generator": VPCGenerator, "attributes": {}},
            {"generator": MarketplaceGenerator, "attributes": {}},
        ]
        accounts_list = None

    months = _create_month_list(start_date, end_date)

    payer_account, usage_accounts, currency_code = _generate_accounts(accounts_list)
    currency_code = default_currency(options.get("currency"), currency_code)

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
                gen_start_date,
                gen_end_date,
                currency_code,
                payer_account,
                usage_accounts,
                attributes,
                options.get("aws_tags"),
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

            if not manifest_gen:
                s3_cur_path, _ = aws_generate_manifest(fake, manifest_values)
                for monthly_file in monthly_files:
                    temp_cur_zip = _gzip_report(monthly_file)
                    destination_file = "{}/{}.gz".format(s3_cur_path, os.path.basename(monthly_file))
                    aws_route_file(aws_bucket_name, destination_file, temp_cur_zip)
                    os.remove(temp_cur_zip)
            else:
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
            {"generator": CCSPGenerator, "attributes": {}},
            {"generator": SQLGenerator, "attributes": {}},
            {"generator": StorageGenerator, "attributes": {}},
            {"generator": VMGenerator, "attributes": {}},
            {"generator": VNGenerator, "attributes": {}},
        ]
        accounts_list = None

    months = _create_month_list(start_date, end_date)

    account_info = _generate_azure_account_info(accounts_list)
    currency = default_currency(options.get("currency"), account_info["currency_code"])

    meter_cache = {}
    # The options params are not going to change so we don't
    # have to keep resetting the var inside of the for loop
    azure_container_name = options.get("azure_container_name")
    storage_account_name = options.get("azure_account_name")
    azure_prefix_name = options.get("azure_prefix_name")
    azure_report_name = options.get("azure_report_name")
    version_two = options.get("version_two", False)
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
            attributes["version_two"] = version_two
            gen = generator_cls(gen_start_date, gen_end_date, currency, account_info, attributes)
            azure_columns = gen.azure_columns
            data += gen.generate_data()
            meter_cache = gen.get_meter_cache()

            if count % ten_percent == 0:
                LOG.info(f"Done with {count} of {num_gens} generators.")

        local_path, output_file_name = _generate_azure_filename()
        date_range = _generate_azure_date_range(month)

        _write_csv(local_path, data, azure_columns)
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
        generators = [{"generator": OCPGenerator, "attributes": {}}]

    months = _create_month_list(start_date, end_date)
    insights_upload = options.get("insights_upload")
    write_monthly = options.get("write_monthly", False)
    for month in months:
        data = {OCP_POD_USAGE: [], OCP_STORAGE_USAGE: [], OCP_NODE_LABEL: [], OCP_NAMESPACE_LABEL: []}
        file_numbers = {OCP_POD_USAGE: 0, OCP_STORAGE_USAGE: 0, OCP_NODE_LABEL: 0, OCP_NAMESPACE_LABEL: 0}
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
            cr_status = {
                "clusterID": "4e009161-4f40-42c8-877c-3e59f6baea3d",
                "clusterVersion": "stable-4.6",
                "api_url": "https://console.redhat.com",
                "authentication": {"type": "token"},
                "packaging": {"max_reports_to_store": 30, "max_size_MB": 100},
                "upload": {
                    "ingress_path": "/api/ingress/v1/upload",
                    "upload": "True",
                    "upload_wait": 27,
                    "upload_cycle": 360,
                },
                "operator_commit": __version__,
                "prometheus": {
                    "prometheus_configured": "True",
                    "prometheus_connected": "True",
                    "last_query_start_time": "2021-07-28T12:22:37Z",
                    "last_query_success_time": "2021-07-28T12:22:37Z",
                    "service_address": "https://thanos-querier.openshift-monitoring.svc:9091",
                },
                "reports": {
                    "report_month": "07",
                    "last_hour_queried": "2021-07-28 11:00:00 - 2021-07-28 11:59:59",
                    "data_collected": "True",
                },
                "source": {
                    "sources_path": "/api/sources/v1.0/",
                    "name": "INSERT-SOURCE-NAME",
                    "create_source": "False",
                    "check_cycle": 1440,
                },
            }
            cr_status = json.dumps(cr_status)
            manifest_values = {
                "ocp_cluster_id": cluster_id,
                "ocp_assembly_id": ocp_assembly_id,
                "report_datetime": report_datetime,
                "files": manifest_file_names[1:-1],
                "start": gen_start_date,
                "end": gen_end_date,
                "version": __version__,
                "certified": False,
                "cr_status": cr_status,
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


def write_gcp_file(start_date, end_date, data, options):
    """Write GCP data to a file."""
    report_prefix = options.get("gcp_report_prefix")
    etag = options.get("gcp_etag") if options.get("gcp_etag") else str(uuid4())
    if not report_prefix:
        invoice_month = start_date.strftime("%Y%m")
        scan_start = start_date.date()
        scan_end = end_date.date()
        file_name = f"{invoice_month}_{etag}_{scan_start}:{scan_end}.csv"
    else:
        file_name = report_prefix + ".csv"
    local_file_path = "{}/{}".format(os.getcwd(), file_name)
    output_file_name = f"{etag}/{file_name}"
    columns = GCP_REPORT_COLUMNS
    if options.get("gcp_resource_level", False):
        columns += GCP_RESOURCE_COLUMNS
    _write_csv(local_file_path, data, columns)
    return local_file_path, output_file_name


def write_gcp_file_jsonl(start_date, end_date, data, options):
    """Write GCP data to a file."""
    report_prefix = options.get("gcp_report_prefix")
    etag = options.get("gcp_etag") if options.get("gcp_etag") else str(uuid4())
    if not report_prefix:
        invoice_month = start_date.strftime("%Y%m")
        scan_start = start_date.date()
        scan_end = end_date.date()
        file_name = f"{invoice_month}_{etag}_{scan_start}:{scan_end}.json"
    else:
        file_name = report_prefix + ".json"
    local_file_path = "{}/{}".format(os.getcwd(), file_name)
    output_file_name = f"{etag}/{file_name}"
    _write_jsonl(local_file_path, data)
    return local_file_path, output_file_name


def get_gcp_static_currency(generator):
    """Returns currency from static report"""
    return generator[0].get("attributes").get("currency")


def gcp_create_report(options):  # noqa: C901
    """Create a GCP cost usage report file."""
    fake = Faker()
    gcp_bucket_name = options.get("gcp_bucket_name")
    gcp_dataset_name = options.get("gcp_dataset_name")
    gcp_table_name = options.get("gcp_table_name")

    start_date = options.get("start_date")
    end_date = options.get("end_date")

    static_report_data = options.get("static_report_data")
    resource_level = options.get("gcp_resource_level", False)

    if gcp_dataset_name:
        # if the file is supposed to be uploaded to a bigquery table, it needs the JSONL version of everything
        if static_report_data:
            generators = _get_jsonl_generators(static_report_data.get("generators"))
            static_projects = static_report_data.get("projects", {})
            projects = []
            for static_dict in static_projects:
                # this lets the format of the YAML remain the same whether using the upload or local
                project = {}
                project["name"] = static_dict.get("project.name", "")
                project["id"] = static_dict.get("project.id", "")
                # the k:v pairs are split by ; and the keys and values split by :
                static_labels = static_dict.get("project.labels", [])
                labels = []
                if static_labels:
                    for pair in static_labels.split(";"):
                        key = pair.split(":")[0]
                        value = pair.split(":")[1]
                        labels.append({"key": key, "value": value})

                project["labels"] = labels
                location = {}
                location["location"] = static_dict.get("location.location", "")
                location["country"] = static_dict.get("location.country", "")
                location["region"] = static_dict.get("location.region", "")
                location["zone"] = static_dict.get("location.zone", "")
                row = {
                    "billing_account_id": static_dict.get("billing_account_id", ""),
                    "project": project,
                    "location": location,
                }
                projects.append(row)
                currency = default_currency(options.get("currency"), get_gcp_static_currency(generators))
        else:
            generators = [
                {"generator": JSONLCloudStorageGenerator, "attributes": {}},
                {"generator": JSONLComputeEngineGenerator, "attributes": {}},
                {"generator": JSONLGCPNetworkGenerator, "attributes": {}},
                {"generator": JSONLGCPDatabaseGenerator, "attributes": {}},
                {"generator": JSONLHCSGenerator, "attributes": {}},
            ]
            account = fake.word()
            project_generator = JSONLProjectGenerator(account)
            projects = project_generator.generate_projects()
            currency = default_currency(options.get("currency"), None)

    elif static_report_data:
        generators = _get_generators(static_report_data.get("generators"))
        projects = static_report_data.get("projects")
        processed_projects = copy.deepcopy(projects)
        for i, project in enumerate(projects):
            labels = []
            static_labels = project.get("project.labels", [])
            if static_labels:
                for pair in static_labels.split(";"):
                    key = pair.split(":")[0]
                    value = pair.split(":")[1]
                    labels.append({"key": key, "value": value})
                processed_projects[i]["project.labels"] = json.dumps(labels)
        projects = processed_projects

    else:
        generators = [
            {"generator": CloudStorageGenerator, "attributes": {}},
            {"generator": ComputeEngineGenerator, "attributes": {}},
            {"generator": GCPNetworkGenerator, "attributes": {}},
            {"generator": GCPDatabaseGenerator, "attributes": {}},
            {"generator": HCSGenerator, "attributes": {}},
        ]
        account = fake.word()

        project_generator = ProjectGenerator(account)
        projects = project_generator.generate_projects()

    if gcp_dataset_name:
        monthly_files = _gcp_bigquery_process(
            start_date,
            end_date,
            currency,
            projects,
            generators,
            options,
            gcp_bucket_name,
            gcp_dataset_name,
            gcp_table_name,
        )
    else:
        months = _create_month_list(start_date, end_date)
        monthly_files = []
        output_files = []
        for month in months:
            data = []
            gen_start_date = month.get("start")
            gen_end_date = month.get("end")
            for project in projects:
                num_gens = len(generators)
                ten_percent = int(num_gens * 0.1) if num_gens > 50 else 5
                LOG.info(
                    f"Producing data for {num_gens} generators for start: {gen_start_date} and end: {gen_end_date}."
                )
                for count, generator in enumerate(generators):
                    attributes = generator.get("attributes", {})
                    if attributes:
                        start_date = attributes.get("start_date", start_date)
                        end_date = attributes.get("end_date", end_date)
                        currency = default_currency(options.get("currency"), attributes.get("currency"))
                    else:
                        currency = default_currency(options.get("currency"), None)
                    if gen_end_date > end_date:
                        gen_end_date = end_date
                    attributes["resource_level"] = resource_level

                    generator_cls = generator.get("generator")
                    gen = generator_cls(gen_start_date, gen_end_date, currency, project, attributes=attributes)
                    for hour in gen.generate_data():
                        data += [hour]
                    count += 1
                    if count % ten_percent == 0:
                        LOG.info(f"Done with {count} of {num_gens} generators.")

            local_file_path, output_file_name = write_gcp_file(gen_start_date, gen_end_date, data, options)
            output_files.append(output_file_name)
            monthly_files.append(local_file_path)

        for index, month_file in enumerate(monthly_files):
            if gcp_bucket_name:
                gcp_route_file(gcp_bucket_name, month_file, output_files[index])

    write_monthly = options.get("write_monthly", False)
    if not write_monthly:
        _remove_files(monthly_files)


def _gcp_bigquery_process(
    start_date, end_date, currency, projects, generators, options, gcp_bucket_name, gcp_dataset_name, gcp_table_name
):
    resource_level = options.get("gcp_resource_level", False)
    data = []
    for project in projects:
        num_gens = len(generators)
        ten_percent = int(num_gens * 0.1) if num_gens > 50 else 5
        LOG.info(f"Producing data for {num_gens} generators for start: {start_date} and end: {end_date}.")
        for count, generator in enumerate(generators):
            attributes = generator.get("attributes", {})
            if attributes:
                start_date = attributes.get("start_date", start_date)
                end_date = attributes.get("end_date", end_date)
            attributes["resource_level"] = resource_level

            generator_cls = generator.get("generator")
            gen = generator_cls(start_date, end_date, currency, project, attributes=attributes)
            for hour in gen.generate_data():
                data += [hour]
            count += 1
            if count % ten_percent == 0:
                LOG.info(f"Done with {count} of {num_gens} generators.")

    monthly_files = []
    local_file_path, output_file_name = write_gcp_file_jsonl(start_date, end_date, data, options)
    monthly_files.append(local_file_path)

    if gcp_bucket_name:
        gcp_route_file(gcp_bucket_name, local_file_path, output_file_name)

    if not gcp_table_name:
        etag = options.get("gcp_etag") if options.get("gcp_etag") else str(uuid4())
        if resource_level:
            gcp_table_name = f"gcp_billing_export_resource_{etag}"
        else:
            gcp_table_name = f"gcp_billing_export_{etag}"
    gcp_bucket_to_dataset(gcp_bucket_name, output_file_name, gcp_dataset_name, gcp_table_name, resource_level)

    return monthly_files


def oci_route_file(report_type, month, year, data, options):
    """Route file to either local file system or OCI bucket."""

    bucket_name = options.get("oci_bucket_name")
    file_name = ""
    if bucket_name is None:
        file_name = oci_write_file(report_type, month, year, data, options)
    else:
        file_name = oci_bucket_upload(bucket_name, report_type, month, year, data, options)
    return file_name


def oci_write_file(report_type, month, year, data, options):
    """Write OCI data to a file."""
    month_num = f"0{month}" if month < 10 else month
    file_name = f"report_{report_type}-0001_{year}-{month_num}.csv"
    full_file_name = f"{os.getcwd()}/{file_name}"
    _write_csv(full_file_name, data, OCI_REPORT_TYPE_TO_COLS[report_type])

    local_bucket = options.get("oci_local_bucket")
    if local_bucket:
        if not os.path.isdir(local_bucket):
            os.mkdir(local_bucket)
        copy_to_local_dir(local_bucket, full_file_name, file_name)
    return full_file_name


def oci_bucket_upload(bucket_name, report_type, month, year, data, options):

    """Upload data to OCI bucket."""
    month_num = f"0{month}" if month < 10 else month
    file_name = f"report_{report_type}-0001_{year}-{month_num}.csv"
    full_file_name = f"{os.getcwd()}/{file_name}"
    _write_csv(full_file_name, data, OCI_REPORT_TYPE_TO_COLS[report_type])
    _report_type = f"{report_type}-csv"
    upload_to_oci_bucket(bucket_name, _report_type, file_name)
    return file_name


def oci_create_report(options):
    """Create cost and usage report files."""

    start_date = options.get("start_date")
    end_date = options.get("end_date")
    static_report_data = options.get("static_report_data")

    if static_report_data:
        generators = _get_generators(static_report_data.get("generators"))
    else:
        generators = [
            {"generator": OCIComputeGenerator},
            {"generator": OCIBlockStorageGenerator},
            {"generator": OCINetworkGenerator},
            {"generator": OCIDatabaseGenerator},
        ]
    months = _create_month_list(start_date, end_date)
    currency = default_currency(options.get("currency"), static_currency=None)
    monthly_files = []
    data = {OCI_COST_REPORT: [], OCI_USAGE_REPORT: []}

    for month in months:
        LOG.info(f"Generating {month.get('name')} data for OCI")
        gen_start_date = month.get("start")
        gen_end_date = month.get("end")

        for generator in generators:
            generator_cls = generator.get("generator")
            attributes = generator.get("attributes", {})

            if attributes:
                # Skip if generator usage is outside of current month
                if attributes.get("end_date") < month.get("start"):
                    continue
                if attributes.get("start_date") > month.get("end"):
                    continue
                currency = attributes.get("currency")
                gen_start_date, gen_end_date = _create_generator_dates_from_yaml(attributes, month)

            gen = generator_cls(gen_start_date, gen_end_date, currency, attributes)
            for report_type in OCI_REPORT_TYPE_TO_COLS:
                data[report_type] += gen.generate_data()[report_type]

        for report_type in OCI_REPORT_TYPE_TO_COLS:
            month_output_file = oci_route_file(
                report_type, gen_start_date.month, gen_start_date.year, data[report_type], options
            )
            monthly_files.append(month_output_file)
            data[report_type] = []

    write_monthly = options.get("write_monthly", False)
    if not write_monthly:
        _remove_files(monthly_files)
