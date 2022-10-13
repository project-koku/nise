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
"""Module for OCI database data generation."""
from random import choice
from random import uniform

from nise.generators.oci.oci_generator import OCIGenerator


class OCIDatabaseGenerator(OCIGenerator):
    """Generator for OCI database data."""

    database_resource_types = [
        {
            "resource_id": "autonomousdatabase",
            "usage_consumed_quant_units": "TB_MS",
            "usage_consumed_quant_measure": "STORAGE_SIZE",
            "usage_product_resource": "PIC_ADWC_EXADATA_STORAGE",
            "cost_sku_unit_description": "TB Months",
            "cost_billing_unit": "ONE TiB HOURS",
            "cost_product_description": "Oracle Autonomous Data Warehouse",
        },
        {
            "resource_id": "database",
            "usage_consumed_quant_units": "GB_MS",
            "usage_consumed_quant_measure": "STORAGE_SIZE",
            "usage_product_resource": "PIC_DATABASE_CLOUD_ALL_EDITION",
            "cost_sku_unit_description": "GB Months",
            "cost_billing_unit": "ONE GiB HOURS",
            "cost_product_description": "DBaaS - Attached Block Storage Volume",
        },
    ]

    def __init__(self, start_date, end_date, currency, attributes=None):
        """Initialize the database generator."""
        super().__init__(start_date, end_date, currency, attributes)
        self.service_name = "DATABASE"
        self.select_db_resource = choice(self.database_resource_types)
        self.resource_id = f"ocid1.{self.select_db_resource.get('resource_id')}.oci.iad.{self.product_region}.{self.fake.pystr(min_chars=25, max_chars=35)}"  # noqa: E501
        self.cost_product_description = self.select_db_resource.get("cost_product_description")
        self.cost_billing_unit = self.select_db_resource.get("cost_billing_unit")
        self.cost_sku_unit_description = self.select_db_resource.get("cost_sku_unit_description")
        self.usage_consumed_quant_units = self.select_db_resource.get("usage_consumed_quant_units")
        self.usage_consumed_quant_measure = self.select_db_resource.get("usage_consumed_quant_measure")
        self.usage_product_resource = self.select_db_resource.get("usage_product_resource")
        self.usage_consumed_quantity = self.fake.pyint(max_value=167674224)
        self.unit_price = round(uniform(1.0, 10.0), 4)
        self.cost = (
            attributes.get("cost")
            if attributes and attributes.get("cost")
            else (self.unit_price * self.usage_consumed_quantity)
        )
