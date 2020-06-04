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
        "faker>=3.0",
        "boto3>=1.11",
        "requests>=2.22",
        "jinja2>=2.10",
        "azure-mgmt-costmanagement>=0.1",
        "azure-mgmt-resource>=7.0",
        "azure-mgmt-storage>=7.1",
        "azure-storage-blob>=12.1",
        "google-cloud-storage>=1.19",
        "pyyaml>=5.3",
    ],
    dependency_links=[],
    entry_points={"console_scripts": ["nise = nise.__main__:main"]},
    include_package_data=True,
    zip_safe=False,
)
