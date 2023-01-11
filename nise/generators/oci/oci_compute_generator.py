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
#
"""Module for OCI compute data generation."""
from nise.generators.oci.oci_generator import OCIGenerator


class OCIComputeGenerator(OCIGenerator):
    """Generator for OCI Compute data."""

    def __init__(self, start_date, end_date, currency, attributes=None):
        """Initialize the compute generator."""
        super().__init__(start_date, end_date, currency, attributes)
        self.service_name = "COMPUTE"
        self.resource_id = (
            f"ocid1.instance.oci.iad.{self.product_region}.{self.fake.pystr(min_chars=10, max_chars=20)}"
        )
        self.cost_product_description = "Virtual Machine Standard - E2 Micro - Free"
        self.cost_billing_unit = "ONE HOURS OCPUS"
        self.cost_sku_unit_description = "OCPU Hours"
        self.usage_consumed_quant_units = "MS"
        self.usage_consumed_quant_measure = "STORAGE_SIZE"
        self.usage_product_resource = "PIC_COMPUTE_VM_STANDARD_E2_MICRO_FREE"
