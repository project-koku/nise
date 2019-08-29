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
"""Module for azure bandwidth data generation."""
import json
from random import choice, uniform

from nise.generators.azure.azure_generator import AzureGenerator


# pylint: disable=too-many-arguments, too-many-instance-attributes
class SQLGenerator(AzureGenerator):
    """Generator for SQL Database data."""

    EXAMPLE_RESOURCE = (
        ('RG1', 'mysa1'),
        ('RG1', 'costmgmtacct1234'),
        ('RG2', 'mysa1'),
        ('RG2', 'costmgmtacct1234'),
        ('costmgmt', 'mysa1'),
        ('costmgmt', 'costmgmtacct1234'),
        ('hccm', 'mysa1'),
        ('hccm', 'costmgmtacct1234')
    )

    def __init__(self, start_date, end_date, payer_account, usage_accounts, attributes=None):
        """Initialize the data transfer generator."""
        super().__init__(start_date, end_date, payer_account, usage_accounts, attributes)
        self._usage_quantity = None
        self._resource_rate = None
        self._pre_tax_cost = None
        self._instance_id = None
        self._meter_id = None
        self._meter_name = 'S0 DTUs - Free'
        self._service_name = 'SQL Database'
        self._service_tier = 'SQL DB Single Std'
        if attributes:
            if attributes.get('_service_name'):
                self._service_name = attributes.get('_service_name')
            if attributes.get('_service_tier'):
                self._service_tier = attributes.get('_service_tier')
            if attributes.get('_instance_id'):
                self._instance_id = attributes.get('_instance_id')
            if attributes.get('_meter_id'):
                self._meter_id = attributes.get('_meter_id')
            if attributes.get('_usage_quantity'):
                self._usage_quantity = attributes.get('_usage_quantity')
            if attributes.get('_resource_rate'):
                self._resource_rate = attributes.get('_resource_rate')
            if attributes.get('_pre_tax_cost'):
                self._pre_tax_cost = attributes.get('_pre_tax_cost')
            if attributes.get('tags'):
                self._tags = attributes.get('tags')

    def _get_location_info(self):
        """Get bandwidth info."""
        azure_region, meter_region = self._get_location()
        return azure_region, meter_region

    def _get_resource_info(self):
        """Generate instance id."""
        resource_group, resource_name = choice(self.EXAMPLE_RESOURCE)
        if self._instance_id:
            instance_id = self._instance_id
        else:
            instance_id = '{}/{}/{}/{}/{}/{}'.format('subscriptions',
                                                     self.payer_account,
                                                     'resourceGroups',
                                                     resource_group,
                                                     '/providers/Microsoft.Sql/servers/',
                                                     resource_name)
        return resource_group, instance_id

    def _update_data(self, row, start, end, **kwargs):  # pylint: disable=too-many-locals
        """Update data with generator specific data."""
        row = self._add_common_usage_info(row, start, end)

        if self._meter_id:
            meter_id = self._meter_id
        else:
            meter_id = self.fake.uuid4()  # pylint: disable=no-member

        rate = self._resource_rate if self._resource_rate else round(uniform(0.12, 0.19), 5)
        amount = self._usage_quantity if self._usage_quantity else uniform(0.000002, 0.09)
        cost = self._pre_tax_cost if self._pre_tax_cost else amount * rate
        azure_region, meter_region = self._get_location_info()
        resource_group, instance_id = self._get_resource_info()
        additional_info_str = '{"ConsumptionMeter": "a149966f-73b4-4e1d-b335-d2a572b1e6bd"}'
        row['ResourceGroup'] = resource_group
        row['ResourceLocation'] = azure_region
        row['MeterCategory'] = self._service_name
        row['MeterSubcategory'] = 'Single Standard'
        row['MeterId'] = str(meter_id)
        row['MeterName'] = self._meter_name
        row['MeterRegion'] = meter_region
        row['UsageQuantity'] = str(amount)
        row['ResourceRate'] = str(rate)
        row['PreTaxCost'] = str(cost)
        row['ConsumedService'] = 'Microsoft.Sql'
        row['ResourceType'] = 'Microsoft.Sql/servers'
        row['InstanceId'] = instance_id
        row['OfferId'] = ''
        row['AdditionalInfo'] = json.dumps(additional_info_str)
        row['ServiceInfo1'] = ''
        row['ServiceInfo2'] = ''
        row['ServiceName'] = self._service_name
        row['ServiceTier'] = self._service_tier
        row['Currency'] = 'USD'
        self._add_tag_data(row)

        return row

    def _generate_daily_data(self):
        """Create daily data."""
        data = []
        for day in self.days:
            start = day.get('start')
            end = day.get('end')
            row = self._init_data_row(start, end)
            row = self._update_data(row, start, end)
            data.append(row)
        return data

    def generate_data(self):
        """Responsible for generating data."""
        data = self._generate_daily_data()
        return data
