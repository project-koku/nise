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
from nise.generators.azure.azure_generator import AZURE_COLUMNS  # noqa: F401
from nise.generators.azure.azure_generator import AZURE_COLUMNS_V2  # noqa: F401
from nise.generators.azure.azure_generator import AzureGenerator  # noqa: F401
from nise.generators.azure.bandwidth_generator import BandwidthGenerator  # noqa: F401
from nise.generators.azure.ccsp_generator import CCSPGenerator  # noqa: F401
from nise.generators.azure.sql_database_generator import SQLGenerator  # noqa: F401
from nise.generators.azure.storage_generator import StorageGenerator  # noqa: F401
from nise.generators.azure.virtual_machine_generator import VMGenerator  # noqa: F401
from nise.generators.azure.virtual_network_generator import VNGenerator  # noqa: F401
