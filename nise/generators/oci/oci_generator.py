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
"""Defines the abstract generator."""
import datetime
from copy import deepcopy
from random import choice
from random import choices
from random import randint
from random import uniform
from string import ascii_lowercase
from abc import abstractmethod
from faker import Faker

from dateutil import parser
from nise.generators.generator import AbstractGenerator
from nise.generators.generator import REPORT_TYPE


OCI_COST_REPORT="oci_cost_report"
OCI_USAGE_REPORT = "oci_usage_report"

OCI_IDENTITY_COLUMNS=(
    "lineItem/referenceNo",
    "lineItem/tenantId",
    "lineItem/intervalUsageStart",
    "lineItem/intervalUsageEnd",
    "product/service"
)

OCI_USAGE_PRODUCT_COLS = {
    "product/resource"
}
OCI_COMMON_PRODUCT_COLS = (
    "product/compartmentId",
    "product/compartmentName",
    "product/region",
    "product/availabilityDomain",
    "product/resourceId",
)
OCI_COST_COLUMNS = (
    "usage/billedQuantity",
    "usage/billedQuantityOverage",
    "cost/subscriptionId",
    "cost/productSku",
    "product/Description",
    "cost/unitPrice",
    "cost/unitPriceOverage",
    "cost/myCost",
    "cost/myCostOverage",
    "cost/currencyCode",
    "cost/billingUnitReadable",
    "cost/skuUnitDescription",
    "cost/overageFlag",
)
OCI_USAGE_COLUMNS = (
    "product/resource"
    "usage/consumedQuantity",
    "usage/billedQuantity",
    "usage/consumedQuantityUnits",
    "usage/consumedQuantityMeasure"
)
OCI_CORRECTION_COLUMNS=(
    "lineItem/isCorrection",
    "lineItem/backreferenceNo"
)
OCI_TAGS_COLUMNS=(
    "tags/Oracle-Tags.CreatedBy",
    "tags/Oracle-Tags.CreatedOn",
    "tags/orcl-cloud.free-tier-retained",
)

OCI_COMMON_USAGE = (
    OCI_IDENTITY_COLUMNS
    + OCI_COMMON_PRODUCT_COLS
    + OCI_CORRECTION_COLUMNS
    + OCI_TAGS_COLUMNS
)

OCI_REPORT_TYPE_TO_COLS = {
    OCI_COST_REPORT: (
        OCI_IDENTITY_COLUMNS
        + OCI_COMMON_PRODUCT_COLS
        + OCI_COST_COLUMNS
        + OCI_CORRECTION_COLUMNS
        + OCI_TAGS_COLUMNS
    ),
    OCI_USAGE_REPORT: (
        OCI_IDENTITY_COLUMNS
        + tuple(OCI_USAGE_PRODUCT_COLS)
        + OCI_COMMON_PRODUCT_COLS
        + OCI_USAGE_COLUMNS
        + OCI_CORRECTION_COLUMNS
        + OCI_TAGS_COLUMNS
    )
}

class OCIGenerator(AbstractGenerator):
    """Defines a abstract class for generators."""

    def __init__(self, start_date, end_date, currency, attributes=None):
        """Initialize the generator."""
        super().__init__(start_date, end_date)
        self.currency = currency

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not (in_date and isinstance(in_date, datetime.datetime)):
            raise ValueError("in_date must be a date object.")
        return in_date.strftime("%Y-%m-%dT%H:%MZ")

    def _init_data_row(self, start, end, **kwargs):
        """Create a row of data with placeholder for all headers."""
        if not (start and end):
            raise ValueError("start and end must be date objects.")
        if not isinstance(start, datetime.datetime):
            raise ValueError("start must be a date object.")
        if not isinstance(end, datetime.datetime):
            raise ValueError("end must be a date object.")

        report_type = kwargs.get(REPORT_TYPE)
        row = {}
        for column in OCI_REPORT_TYPE_TO_COLS[report_type]:
            row[column] = ""
        return row

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Add common usage information."""
        data = self._common_usage_datagen(start, end, **kwargs)
        for column in OCI_COMMON_USAGE:
            row[column] = data[column]
        return row   

    def _common_usage_datagen(self,start, end, **kwargs):
        """Generate data for common columns."""
        fake = Faker()
        data = {
            "lineItem/referenceNo":"V2.HrPD8n8biHxnXDjI+bskegyizs8AnIwLRpgLIjsEUTRUCzTXZ7akEPPZ3Ws7I2SLz5mRURPIvuNsYsdXBVTTQQ==",
            "lineItem/tenantId":"ocid1.tenancy.oc1..aaaaaaaa2sgzyxbcxlmuiigavvinkxvhtlvyw5rwy5aq5f6clf376dgt2axa",
            "lineItem/intervalUsageStart":OCIGenerator.timestamp(start),
            "lineItem/intervalUsageEnd":OCIGenerator.timestamp(end),
            "product/service":"",
            "product/compartmentId":"",
            "product/compartmentName":"",
            "product/region":"",
            "product/availabilityDomain":"",
            "product/resourceId":"",
            "lineItem/isCorrection":"",
            "lineItem/backreferenceNo":"",
            "tags/Oracle-Tags.CreatedBy":"",
            "tags/Oracle-Tags.CreatedOn":"2022-02-23T15:24:54.842Z",
            "tags/orcl-cloud.free-tier-retained":"",
        }

        return data

    @abstractmethod
    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""

    def _generate_hourly_data(self, **kwargs):
        """Create hourly data."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            row = self._init_data_row(start, end, **kwargs)
            row = self._add_common_usage_info(row, start, end, **kwargs)
            row = self._update_data(row, start, end, **kwargs)
            yield row
    
    @abstractmethod
    def generate_data(self, report_type=None, **kwargs):
        """Responsibile for generating data."""