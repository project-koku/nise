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
    install_requires=['adal==1.2.7', 'azure-common==1.1.28', "azure-core==1.24.0; python_version >= '3.6'", 'azure-mgmt-core==1.3.0', 'azure-mgmt-costmanagement==0.2.0', 'azure-mgmt-resource==21.0.0', 'azure-mgmt-storage==20.0.0', 'azure-storage-blob==12.11.0', 'boto3==1.21.45', "botocore==1.24.46; python_version >= '3.6'", "cachetools==5.2.0; python_version ~= '3.7'", "certifi==2022.5.18.1; python_version >= '3.6'", 'cffi==1.15.0', "charset-normalizer==2.0.12; python_version >= '3'", 'circuitbreaker==1.3.2', "cryptography==3.4.7; python_version >= '3.6'", 'faker==13.3.5', "google-api-core[grpc]==2.8.1; python_version >= '3.6'", "google-auth==2.6.6; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'", 'google-cloud-bigquery==3.0.1', "google-cloud-bigquery-storage==2.13.1; python_version >= '3.6'", "google-cloud-core==2.3.0; python_version >= '3.6'", 'google-cloud-storage==2.3.0', "google-crc32c==1.3.0; python_version >= '3.6'", "google-resumable-media==2.3.3; python_version >= '3.6'", "googleapis-common-protos==1.56.2; python_version >= '3.6'", "grpcio==1.46.3; python_version >= '3.6'", 'grpcio-status==1.46.3', "idna==3.3; python_version >= '3'", 'isodate==0.6.1', 'jinja2==3.1.1', "jmespath==1.0.0; python_version >= '3.7'", "markupsafe==2.1.1; python_version >= '3.7'", 'msrest==0.6.21', 'msrestazure==0.6.4', "numpy==1.22.4; python_version >= '3.8'", "oauthlib==3.2.0; python_version >= '3.6'", 'oci==2.64.0', "packaging==21.3; python_version >= '3.6'", "proto-plus==1.20.5; python_version >= '3.6'", "protobuf==3.20.1; python_version >= '3.7'", "pyarrow==7.0.0; python_version >= '3.7'", 'pyasn1==0.4.8', 'pyasn1-modules==0.2.8', 'pycparser==2.21', 'pyjwt==2.4.0', 'pyopenssl==19.1.0', "pyparsing==3.0.9; python_full_version >= '3.6.8'", "python-dateutil==2.8.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'", 'pytz==2022.1', 'pyyaml==6.0', 'requests==2.27.1', "requests-oauthlib==1.3.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'", "rsa==4.8; python_version >= '3.6'", "s3transfer==0.5.2; python_version >= '3.6'", "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'", "typing-extensions==4.2.0; python_version >= '3.7'", "urllib3==1.26.9; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'"











],
    dependency_links=[],
    entry_points={"console_scripts": ["nise = nise.__main__:main"]},
    include_package_data=True,
    zip_safe=False,
)