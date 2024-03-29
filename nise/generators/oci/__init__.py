#
# Copyright 2022 Red Hat, Inc.
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
"""Module for oci data generators."""
from nise.generators.oci.oci_block_storage_generator import OCIBlockStorageGenerator  # noqa: F401
from nise.generators.oci.oci_compute_generator import OCIComputeGenerator  # noqa: F401
from nise.generators.oci.oci_database_generator import OCIDatabaseGenerator  # noqa: F401
from nise.generators.oci.oci_generator import OCIGenerator  # noqa: F401
from nise.generators.oci.oci_network_generator import OCINetworkGenerator  # noqa: F401
