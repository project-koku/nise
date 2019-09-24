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
class BandwidthGenerator(AzureGenerator):
    """Generator for Bandwidth data."""

    METER_NAME = (
        'Data Transfer In',
        'Data Transfer Out - Free'
    )

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

    ADDITIONAL_INFO = (
        {'ConsumptionMeter': 'a149966f-73b4-4e1d-b335-d2a572b1e6bd'},
        {'ImageType': None, 'ServiceType': None, 'VMName': None,
         'VMProperties': None, 'VCPUs': 0, 'UsageType': 'DataTrIn'},
        {'ImageType': None, 'ServiceType': None, 'VMName': None,
         'VMProperties': None, 'VCPUs': 0, 'UsageType': 'DataTrOut',
         'ConsumptionMeter': '9995d93a-7d35-4d3f-9c69-7a7fea447ef4'}
    )

    def __init__(self, start_date, end_date, payer_account, usage_accounts, attributes=None):
        """Initialize the data transfer generator."""
        super().__init__(start_date, end_date, payer_account, usage_accounts, attributes)
        self._usage_quantity = None
        self._resource_rate = None
        self._pre_tax_cost = None
        self._instance_id = None
        self._meter_id = None
        self._meter_name = None
        self._service_name = 'Bandwidth'
        self._service_tier = 'Bandwidth'
        if attributes:
            if attributes.get('service_name'):
                self._service_name = attributes.get('service_name')
            if attributes.get('service_tier'):
                self._service_tier = attributes.get('service_tier')
            if attributes.get('instance_id'):
                self._instance_id = attributes.get('instance_id')
            if attributes.get('meter_id'):
                self._meter_id = attributes.get('meter_id')
            if attributes.get('usage_quantity'):
                self._usage_quantity = attributes.get('usage_quantity')
            if attributes.get('resource_rate'):
                self._resource_rate = attributes.get('resource_rate')
            if attributes.get('pre_tax_cost'):
                self._pre_tax_cost = attributes.get('pre_tax_cost')
            if attributes.get('tags'):
                self._tags = attributes.get('tags')

    def _get_location_info(self):
        """Get region info and meter name."""
        azure_region, meter_region = self._get_location()
        meter_name = choice(self.METER_NAME)
        return azure_region, meter_region, meter_name

    def _get_resource_info(self):
        """Generate resource info: instance id, resource group name, and additional info."""
        additional_info = choice(self.ADDITIONAL_INFO)
        resource_group, resource_name = choice(self.EXAMPLE_RESOURCE)
        if self._instance_id:
            instance_id = self._instance_id
        else:
            storage_accts_str = '/providers/Microsoft.Storage/storageAccounts/'
            instance_id = '{}/{}/{}/{}/{}/{}'.format('subscriptions',
                                                     self.payer_account,
                                                     'resourceGroups',
                                                     resource_group,
                                                     storage_accts_str,
                                                     resource_name)
        return resource_group, instance_id, additional_info

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
        azure_region, meter_region, meter_name = self._get_location_info()
        resource_group, instance_id, additional_info = self._get_resource_info()

        row['ResourceGroup'] = resource_group
        row['ResourceLocation'] = azure_region
        row['MeterCategory'] = self._service_name
        row['MeterSubcategory'] = ''
        row['MeterId'] = str(meter_id)
        row['MeterName'] = meter_name
        row['MeterRegion'] = meter_region
        row['UsageQuantity'] = str(amount)
        row['ResourceRate'] = str(rate)
        row['PreTaxCost'] = str(cost)
        row['ConsumedService'] = 'Microsoft.Storage'
        row['ResourceType'] = 'Microsoft.Storage/storageAccounts'
        row['InstanceId'] = instance_id
        row['OfferId'] = ''
        row['AdditionalInfo'] = json.dumps(additional_info)
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
