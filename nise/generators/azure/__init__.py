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
"""Module for azure data generators."""

from nise.generators.azure.azure_generator import AZURE_COLUMNS_V2_RESOURCE_GROUP
from nise.generators.azure.azure_generator import AZURE_COLUMNS_V2_SUBSCRIPTION
from nise.generators.azure.azure_generator import AzureGenerator
from nise.generators.azure.bandwidth_generator import BandwidthGenerator
from nise.generators.azure.ccsp_generator import CCSPGenerator
from nise.generators.azure.data_transfer_generator import DTGenerator
from nise.generators.azure.managed_disk_generator import ManagedDiskGenerator
from nise.generators.azure.sql_database_generator import SQLGenerator
from nise.generators.azure.storage_generator import StorageGenerator
from nise.generators.azure.virtual_machine_generator import VMGenerator
from nise.generators.azure.virtual_network_generator import VNGenerator
