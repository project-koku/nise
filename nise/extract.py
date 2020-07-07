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
"""Extracts OCP .gz payload to local directory."""
import json
import os
import shutil
import tempfile
from tarfile import ReadError
from tarfile import TarFile

from dateutil import parser
from dateutil.relativedelta import relativedelta
from nise.util import LOG


def month_date_range(for_date_time):
    """
    Get a formatted date range string for the given date.

    Date range is aligned on the first day of the current
    month and ends on the first day of the next month from the
    specified date.

    Args:
        for_date_time (DateTime): The starting datetime object

    Returns:
        (String): "YYYYMMDD-YYYYMMDD", example: "19701101-19701201"

    """
    start_month = for_date_time.replace(day=1, second=1, microsecond=1)
    end_month = start_month + relativedelta(months=+1)
    timeformat = "%Y%m%d"
    return "{}-{}".format(start_month.strftime(timeformat), end_month.strftime(timeformat))


def get_report_details(report_directory):
    """
    Get OCP usage report details from manifest file.

    Date range is aligned on the first day of the current
    month and ends on the first day of the next month from the
    specified date.

    Args:
        report_directory (String): base directory for report.

    Returns:
        (Dict): keys: value
            "file: String,
             cluster_id: String,
             payload_date: DateTime,
             manifest_path: String,
             uuid: String,
             manifest_path: String"

    """
    manifest_path = "{}/{}".format(report_directory, "manifest.json")

    payload_dict = {}
    try:
        with open(manifest_path) as file:
            payload_dict = json.load(file)
            payload_dict["date"] = parser.parse(payload_dict["date"])
            payload_dict["manifest_path"] = manifest_path
    except (OSError, IOError, KeyError):
        LOG.error("Unable to extract manifest data")

    return payload_dict


def extract_payload(base_path, payload_file):
    """
    Extract OCP usage report payload into local directory structure.

    Payload is expected to be a .tar.gz file that contains:
    1. manifest.json - dictionary containing usage report details needed
        for report processing.
        Dictionary Contains:
            file - .csv usage report file name
            date - DateTime that the payload was created
            uuid - uuid for payload
            cluster_id  - OCP cluster ID.
    2. *.csv - Actual usage report for the cluster.  Format is:
        Format is: <uuid>_report_name.csv

    On successful completion the report and manifest will be in a directory
    structure that the OCPReportDownloader is expecting.

    Ex: /var/tmp/insights_local/my-ocp-cluster-1/20181001-20181101

    Args:
        basepath (String): base local directory path.
        payload_file (String): path to payload.tar.gz file containing report and manifest.

    Returns:
        None

    """
    # Create temporary directory for initial file staging and verification
    temp_dir = tempfile.mkdtemp()

    # Extract tarball into temp directory
    try:
        mytar = TarFile.open(payload_file)
        mytar.extractall(path=temp_dir)
        files = mytar.getnames()
        manifest_path = [manifest for manifest in files if "manifest.json" in manifest]
    except ReadError as error:
        LOG.error("Unable to untar file. Reason: {}".format(str(error)))
        shutil.rmtree(temp_dir)
        return

    # Open manifest.json file and build the payload dictionary.
    full_manifest_path = "{}/{}".format(temp_dir, manifest_path[0])
    report_meta = get_report_details(os.path.dirname(full_manifest_path))

    # Create directory tree for report.
    usage_month = month_date_range(report_meta.get("date"))
    destination_dir = "{}/{}/{}".format(base_path, report_meta.get("cluster_id"), usage_month)
    os.makedirs(destination_dir, exist_ok=True)

    # Copy manifest
    manifest_destination_path = "{}/{}".format(destination_dir, os.path.basename(report_meta.get("manifest_path")))
    shutil.copy(report_meta.get("manifest_path"), manifest_destination_path)

    # Copy report payload
    for report_file in report_meta.get("files"):
        subdirectory = os.path.dirname(full_manifest_path)
        payload_source_path = f"{subdirectory}/{report_file}"
        payload_destination_path = f"{destination_dir}/{report_file}"
        try:
            shutil.copy(payload_source_path, payload_destination_path)
        except FileNotFoundError:
            pass

    LOG.info("Successfully extracted OCP for {}/{}".format(report_meta.get("cluster_id"), usage_month))
    # Remove temporary directory and files
    shutil.rmtree(temp_dir)
