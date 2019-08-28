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
import json
from abc import abstractmethod
from random import choice, randint
from nise.generators.generator import AbstractGenerator

AZURE_COLUMNS = ('SubscriptionGuid',
                 'ResourceGroup',
                 'ResourceLocation',
                 'UsageDateTime',
                 'MeterCategory',
                 'MeterSubcategory',
                 'MeterId',
                 'MeterName',
                 'MeterRegion',
                 'UsageQuantity',
                 'ResourceRate',
                 'PreTaxCost',
                 'ConsumedService',
                 'ResourceType',
                 'InstanceId',
                 'Tags',
                 'OfferId',
                 'AdditionalInfo',
                 'ServiceInfo1',
                 'ServiceInfo2',
                 'ServiceName',
                 'ServiceTier',
                 'Currency')


# pylint: disable=too-few-public-methods, too-many-arguments
class AzureGenerator(AbstractGenerator):
    """Defines an abstract class for generators."""

    RESOURCE_LOCATION = (
        ('US East', 'US East'),
        ('US East', 'Zone 1'),
        ('US East', ''),
        ('US North Central', 'US North Central'),
        ('US North Central', 'Zone 1'),
        ('US North Central', ''),
        ('US South Central', 'US South Central'),
        ('US South Central', 'Zone 1'),
        ('US South Central', ''),
        ('US West', 'US West'),
        ('US West', 'Zone 1'),
        ('US West', ''),
        ('US Central', 'US Central'),
        ('US Central', 'Zone 1'),
        ('US Central', ''),
        ('US East 2', 'US East 2'),
        ('US West 2', 'US West 2')
    )

    def __init__(self, start_date, end_date, payer_account, usage_accounts, attributes=None):
        """Initialize the generator."""
        self.payer_account = payer_account
        self.usage_accounts = usage_accounts
        self.attributes = attributes
        self._tags = None
        self.num_instances = 1 if attributes else randint(2, 60)
        super().__init__(start_date, end_date)

    def _pick_tag(self, key1, val1, key2, val2):
        """Generate a randomized 2-item tag or blank tag from options."""
        if self._tags:
            tags = self._tags
        elif self.attributes and self.attributes.get('tags'):
            tags = None
        else:
            init_tag = {key1: choice(val1), key2: choice(val2)}
            tag_choices = (init_tag, '')
            tags = choice(tag_choices)
        return tags

    def _init_data_row(self, start, end, **kwargs):  # noqa: C901
        """Create a row of data with placeholder for all headers."""
        if not start or not end:
            raise ValueError('start and end must be date objects.')
        if not isinstance(start, datetime.datetime):
            raise ValueError('start must be a date object.')
        if not isinstance(end, datetime.datetime):
            raise ValueError('end must be a date object.')

        row = {}
        for column in AZURE_COLUMNS:
            row[column] = ''
            if column == 'SubscriptionGuid':
                # pylint: disable=no-member
                row[column] = self.payer_account
        return row

    def _get_location(self):
        """Pick resource location."""
        if self.attributes and self.attributes.get('resource_location'):
            region = self.attributes.get('resource_location')
            location = [option for option in self.RESOURCE_LOCATION if region in option].pop()
        else:
            location = choice(self.RESOURCE_LOCATION)
        return location

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Add common usage information."""
        row['SubscriptionGuid'] = self.payer_account
        row['UsageDateTime'] = start
        return row

    def _add_tag_data(self, row):
        """Add tag dictionary data options to the row."""
        if not self._tags:
            self._tags = self._pick_tag(
                'environment',
                ('dev', 'ci', 'qa', 'stage', 'prod'),
                'project',
                ('p1', 'p2', 'p3')
            )
        row['Tags'] = json.dumps(self._tags)

    @abstractmethod
    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""

    def _generate_hourly_data(self, **kwargs):
        """Create hourly data."""
        # not required for azure
        data = []
        return data

    @abstractmethod
    def _generate_daily_data(self):
        """Create daily data."""

    @abstractmethod
    def generate_data(self):
        """Responsible for generating data."""
