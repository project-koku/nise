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
"""Defines the upload mechanism to various clouds."""
import gzip
import io
import os
import shutil
import sys
import traceback

import boto3
from azure.core.exceptions import ServiceRequestError
from azure.core.exceptions import ServiceResponseError
from azure.storage.blob import BlobServiceClient
from botocore.exceptions import ClientError
from google.cloud import bigquery
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from nise.util import LOG
from oci.config import from_file
from oci.config import validate_config
from oci.exceptions import ConfigFileNotFound
from oci.exceptions import InvalidConfig
from oci.exceptions import InvalidPrivateKey
from oci.exceptions import ServiceError
from oci.object_storage import ObjectStorageClient
from requests.exceptions import ConnectionError as BotoConnectionError


def upload_to_s3(bucket_name, bucket_file_path, local_path):
    """Upload data to an S3 bucket.

    Args:
        bucket_name (String): The name of the S3 bucket
        bucket_file_path (String): The path to store the file to
        local_path  (String): The local file system path of the file
    Returns:
        (Boolean): True if file was uploaded

    """
    uploaded = True
    try:
        s3_client = boto3.resource("s3")
        s3_client.Bucket(bucket_name).upload_file(local_path, bucket_file_path)
        msg = f"Uploaded {bucket_file_path} to s3 bucket {bucket_name}."
        LOG.info(msg)
    except (ClientError, BotoConnectionError, boto3.exceptions.S3UploadFailedError) as upload_err:
        LOG.error(upload_err)
        uploaded = False
    return uploaded


def upload_to_azure_container(storage_file_name, local_path, storage_file_path):
    """Upload data to a storage account.

    Args:
        storage_file_name (String): The container to upload file to
        local_path  (String): The full local file system path of the file
        storage_file_path (String): The file path to upload to within container

    Returns:
        (Boolean): True if file was uploaded

    """
    try:
        # Retrieve the connection string for use with the application.
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container=storage_file_name, blob=storage_file_path)
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data=data)
        LOG.info(f"uploaded {storage_file_name} to {storage_file_path}")
    except (ServiceRequestError, ServiceResponseError, IOError) as error:
        LOG.error(error)
        traceback.print_exc(file=sys.stderr)
        return False
    return True


def upload_to_gcp_storage(bucket_name, source_file_name, destination_blob_name):
    """
    Upload data to a GCP Storage Bucket.

    Args:
        bucket_name (String): The container to upload file to
        source_file_name  (String): The full local file system path of the file
        destination_blob_name (String): Destination blob name to store in GCP.

    Returns:
        (Boolean): True if file was uploaded

    """
    uploaded = True

    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        LOG.warning(
            "Please set your GOOGLE_APPLICATION_CREDENTIALS "
            "environment variable before attempting to load file into"
            "GCP Storage."
        )
        return False
    try:
        storage_client = storage.Client()

        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        LOG.info(f"File {source_file_name} uploaded to GCP Storage {destination_blob_name}.")
    except GoogleCloudError as upload_err:
        LOG.error(upload_err)
        uploaded = False
    return uploaded


def gcp_bucket_to_dataset(gcp_bucket_name, file_name, dataset_name, table_name, resource_level=False):
    """
    Create a gcp dataset from a file stored in a bucket.

    Args:
        gcp_bucket_name  (String): The container to upload file to
        file_name  (String): The name of the file stored in GCP
        dataset_name (String): name for the created dataset in GCP
        table_name (String): name for the created dataset in GCP

    Returns:
        (Boolean): True if the dataset was created

    """
    uploaded = True

    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        LOG.warning(
            "Please set your GOOGLE_APPLICATION_CREDENTIALS "
            "environment variable before attempting to create a dataset."
        )
        return False
    try:
        bigquery_client = bigquery.Client()

        project_name = bigquery_client.project
        dataset_id = f"{project_name}.{dataset_name}"
        dataset = bigquery.Dataset(dataset_id)

        # delete dataset (does not error if it doesn't exist) and create fresh one
        bigquery_client.delete_dataset(dataset_id, delete_contents=True, not_found_ok=True)
        dataset = bigquery_client.create_dataset(dataset)

        table_id = f"{project_name}.{dataset_name}.{table_name}"

        # Build schema
        schema = [
            {"name": "billing_account_id", "type": "STRING", "mode": "NULLABLE"},
            {
                "name": "service",
                "type": "RECORD",
                "fields": [
                    {"name": "id", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "description", "type": "STRING", "mode": "NULLABLE"},
                ],
                "mode": "NULLABLE",
            },
            {
                "name": "sku",
                "type": "RECORD",
                "fields": [
                    {"name": "id", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "description", "type": "STRING", "mode": "NULLABLE"},
                ],
                "mode": "NULLABLE",
            },
            {"name": "usage_start_time", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "usage_end_time", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {
                "name": "project",
                "type": "RECORD",
                "fields": [
                    {"name": "id", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "number", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "name", "type": "STRING", "mode": "NULLABLE"},
                    {
                        "name": "labels",
                        "type": "RECORD",
                        "fields": [
                            {"name": "key", "type": "STRING", "mode": "NULLABLE"},
                            {"name": "value", "type": "STRING", "mode": "NULLABLE"},
                        ],
                        "mode": "REPEATED",
                    },
                    {"name": "ancestry_numbers", "type": "STRING", "mode": "NULLABLE"},
                ],
                "mode": "NULLABLE",
            },
            {
                "name": "labels",
                "type": "RECORD",
                "fields": [
                    {"name": "key", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "value", "type": "STRING", "mode": "NULLABLE"},
                ],
                "mode": "REPEATED",
            },
            {
                "name": "system_labels",
                "type": "RECORD",
                "fields": [
                    {"name": "key", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "value", "type": "STRING", "mode": "NULLABLE"},
                ],
                "mode": "REPEATED",
            },
            {
                "name": "location",
                "type": "RECORD",
                "fields": [
                    {"name": "location", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "country", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "region", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "zone", "type": "STRING", "mode": "NULLABLE"},
                ],
                "mode": "NULLABLE",
            },
            {"name": "export_time", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "cost", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "currency", "type": "STRING", "mode": "NULLABLE"},
            {"name": "currency_conversion_rate", "type": "FLOAT", "mode": "NULLABLE"},
            {
                "name": "usage",
                "type": "RECORD",
                "fields": [
                    {"name": "amount", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "unit", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "amount_in_pricing_units", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "pricing_unit", "type": "STRING", "mode": "NULLABLE"},
                ],
                "mode": "NULLABLE",
            },
            {
                "name": "credits",
                "type": "RECORD",
                "fields": [
                    {"name": "name", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "amount", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "full_name", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "id", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "type", "type": "STRING", "mode": "NULLABLE"},
                ],
                "mode": "REPEATED",
            },
            {
                "name": "invoice",
                "type": "RECORD",
                "fields": [{"name": "month", "type": "STRING", "mode": "NULLABLE"}],
                "mode": "NULLABLE",
            },
            {"name": "cost_type", "type": "STRING", "mode": "NULLABLE"},
            {
                "name": "adjustment_info",
                "type": "RECORD",
                "fields": [
                    {"name": "id", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "description", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "mode", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "type", "type": "STRING", "mode": "NULLABLE"},
                ],
                "mode": "NULLABLE",
            },
        ]

        # Add resource to schema if required
        if resource_level:
            schema += [
                {
                    "name": "resource",
                    "type": "RECORD",
                    "fields": [
                        {"name": "name", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "global_name", "type": "STRING", "mode": "NULLABLE"},
                    ],
                    "mode": "NULLABLE",
                }
            ]

        # creates the job config with specifics
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            time_partitioning=bigquery.TimePartitioning(),
            schema=schema,
        )

        uri = f"gs://{gcp_bucket_name}/{file_name}"

        load_job = bigquery_client.load_table_from_uri(uri, table_id, job_config=job_config)

        # waits for the job to finish, will raise an exception if it doesnt work
        load_job.result()

        # after the table is created, delete the file from the storage bucket
        storage_client = storage.Client()
        bucket = storage_client.bucket(gcp_bucket_name)
        blob = bucket.blob(file_name)
        blob.delete()
        # Our downloader downloads by the paritiontime, however the default partitiontime is the date
        # the data is uploaded to bigquery. Therefore, everything goes into one single day. The load
        # job config does not let you upload to the _PARTITIONTIME because it is a prebuild column in
        # bigquery. However, we do have permission to update it.
        partition_date_sql = f"""
        UPDATE `{table_id}` SET _PARTITIONTIME=CAST(DATE_TRUNC(DATE(usage_start_time), DAY) AS timestamp) WHERE 1=1;
        """
        bigquery_client.query(partition_date_sql)

        LOG.info(f"Dataset {dataset_name} created in GCP bigquery under the table name {table_name}.")
    except GoogleCloudError as upload_err:
        LOG.error(upload_err)
        uploaded = False
    return uploaded


def upload_to_oci_bucket(bucket_name, report_type, file_name):
    """
    Upload data to a OCI Storage Bucket.

    Args:
        bucket_name (String): The container to upload file to.
        report_type  (String): The type of report to upload.
        file_name (String): name of the file to upload.

    Returns:
        (Boolean): True if file was uploaded
    """

    try:
        if "OCI_CONFIG_FILE" in os.environ:
            config = from_file(file_location=os.environ.get("OCI_CONFIG_FILE"))
            LOG.info("Using configurations from config file.")
        else:
            oci_user = os.environ["OCI_USER"]
            oci_fingerprint = os.environ["OCI_FINGERPRINT"]
            oci_tenancy = os.environ["OCI_TENANCY"]
            oci_credentials = os.environ["OCI_CREDENTIALS"]
            oci_region = os.environ["OCI_REGION"]
            oci_namespace = os.environ["OCI_NAMESPACE"]
            for oci_var in [oci_user, oci_fingerprint, oci_tenancy, oci_credentials, oci_region, oci_namespace]:
                if oci_var is None or oci_var == "":
                    raise InvalidConfig("Must provide a valid config variables.")
            config = {
                "user": oci_user,
                "fingerprint": oci_fingerprint,
                "tenancy": oci_tenancy,
                "key_content": oci_credentials,
                "region": oci_region,
                "namespace": oci_namespace,
            }
            LOG.info("Creating config dict from env vars.")
        validate_config(config)
        object_storage_client = ObjectStorageClient(config)
        namespace = object_storage_client.get_namespace().data
        with open(file_name, "rb") as file_in:
            with gzip.open(f"{file_name}.gz", "wb") as file_out:
                shutil.copyfileobj(file_in, file_out)
        zipped_file = file_out
        upload_file_name = f"reports/{report_type}/{zipped_file.name}"

        object_storage_client.put_object(
            namespace,
            bucket_name,
            upload_file_name,
            io.open(zipped_file.name, "rb"),
        )

        LOG.info(f"File {upload_file_name} uploaded to OCI Storage {bucket_name} bucket.")
        os.remove(zipped_file.name)
        return True
    except (InvalidConfig, InvalidPrivateKey, ServiceError, ConfigFileNotFound) as err:
        LOG.error(f"Error uploading report to oci bucket: {err}")
        return False
