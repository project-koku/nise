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
"""Module for OCI block storage data generation."""
from random import uniform

from nise.generators.oci.oci_generator import OCIGenerator


class OCIBlockStorageGenerator(OCIGenerator):
    """Generator for OCI Block Storage data."""

    def __init__(self, start_date, end_date, currency, attributes=None):
        """Initialize the block storage generator."""
        super().__init__(start_date, end_date, currency, attributes)
        self.service_name = "BLOCK_STORAGE"
        self.resource_id = f"ocid1.bootvolume.oc1.{self.product_region}.{self.fake.pystr(min_chars=25, max_chars=35)}"
        self.cost_product_description = "Block Volume - Free"
        self.cost_billing_unit = "ONE GiB MONTHS STORAGE_SIZE"
        self.cost_sku_unit_description = "GB Months"
        self.usage_consumed_quant_units = "GB_MS"
        self.usage_consumed_quant_measure = "STORAGE_SIZE"
        self.usage_product_resource = "PIC_BLOCK_STORAGE_STANDARD_FREE"
        self.usage_consumed_quantity = (
            attributes.get("consumed_quantity")
            if attributes and attributes.get("consumed_quantity")
            else self.fake.pyint(max_value=167674224)
        )
        self.unit_price = round(uniform(1.0, 10.0), 4)
        self.cost = (
            attributes.get("cost")
            if attributes and attributes.get("cost")
            else (self.unit_price * self.usage_consumed_quantity)
        )
