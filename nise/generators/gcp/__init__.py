#
# Copyright 2019 Red Hat, Inc.
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
"""Module for gcp data generators."""
from nise.generators.gcp.cloud_storage_generator import CloudStorageGenerator  # noqa: F401
from nise.generators.gcp.compute_engine_generator import ComputeEngineGenerator  # noqa: F401
from nise.generators.gcp.gcp_generator import GCP_REPORT_COLUMNS  # noqa: F401
from nise.generators.gcp.gcp_generator import GCPGenerator  # noqa: F401
from nise.generators.gcp.project_generator import ProjectGenerator  # noqa: F401

GCP_GENERATORS = [CloudStorageGenerator, ComputeEngineGenerator]
