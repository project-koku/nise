#
# Copyright 2020 Red Hat, Inc.
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
import codecs
import os.path

from setuptools import find_packages
from setuptools import setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="koku-nise",
    version=get_version("nise/__init__.py"),  # set the version number in nise.__init__
    author="Project Koku",
    author_email="cost_mgmt@redhat.com",
    description="A tool for generating sample cost and usage data for testing purposes.",
    url="https://github.com/project-koku/nise",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        "adal==1.2.6",
        "azure-common==1.1.26",
        "azure-core==1.11.0",
        "azure-mgmt-core==1.2.2",
        "azure-mgmt-costmanagement==0.2.0",
        "azure-mgmt-resource==15.0.0",
        "azure-mgmt-storage==16.0.0",
        "azure-storage-blob==12.7.1",
        "boto3==1.17.9",
        "botocore==1.20.9",
        "cachetools==4.2.1",
        "certifi==2020.12.5",
        "cffi==1.14.5",
        "chardet==4.0.0",
        "cryptography==3.4.6",
        "faker==6.1.1",
        "google-api-core[grpc]==1.26.0",
        "google-auth==1.26.1",
        "google-cloud-bigquery==2.8.0",
        "google-cloud-core==1.6.0",
        "google-cloud-storage==1.36.0",
        "google-crc32c==1.1.2; python_version >= '3.5'",
        "google-resumable-media==1.2.0",
        "googleapis-common-protos==1.52.0",
        "grpcio==1.35.0",
        "idna==2.10",
        "isodate==0.6.0",
        "jinja2==2.11.3",
        "jmespath==0.10.0",
        "markupsafe==1.1.1",
        "msrest==0.6.21",
        "msrestazure==0.6.4",
        "oauthlib==3.1.0",
        "packaging==20.9",
        "proto-plus==1.13.0",
        "protobuf==3.14.0",
        "pyasn1==0.4.8",
        "pyasn1-modules==0.2.8",
        "pycparser==2.20",
        "pyjwt==2.0.1",
        "pyparsing==2.4.7",
        "python-dateutil==2.8.1",
        "pytz==2021.1",
        "pyyaml==5.4.1",
        "requests==2.25.1",
        "requests-oauthlib==1.3.0",
        "rsa==4.7.1; python_version >= '3.6'",
        "s3transfer==0.3.4",
        "six==1.15.0",
        "text-unidecode==1.3",
        "urllib3==1.26.3",
    ],
    dependency_links=[],
    entry_points={"console_scripts": ["nise = nise.__main__:main"]},
    include_package_data=True,
    zip_safe=False,
)
