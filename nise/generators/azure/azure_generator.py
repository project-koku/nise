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
from copy import deepcopy
from random import choice
from random import randint

from nise.generators.generator import AbstractGenerator
from nise.util import load_yaml

AZURE_COLUMNS = (
    "SubscriptionGuid",
    "ResourceGroup",
    "ResourceLocation",
    "UsageDateTime",
    "MeterCategory",
    "MeterSubcategory",
    "MeterId",
    "MeterName",
    "MeterRegion",
    "UsageQuantity",
    "ResourceRate",
    "PreTaxCost",
    "ConsumedService",
    "ResourceType",
    "InstanceId",
    "Tags",
    "OfferId",
    "AdditionalInfo",
    "ServiceInfo1",
    "ServiceInfo2",
    "ServiceName",
    "ServiceTier",
    "Currency",
    "UnitOfMeasure",
)


class AzureGenerator(AbstractGenerator):
    """Defines an abstract class for generators."""

    SERVICE_METER = [None]
    SERVICE_INFO_2 = [None]
    EXAMPLE_RESOURCE = [None]
    ADDITIONAL_INFO = [None]

    ACCTS_STR = {
        "SQL Database": ("Microsoft.Sql", "servers"),
        "Storage": ("Microsoft.Storage", "storageAccounts"),
        "Virtual Machines": ("Microsoft.Compute", "virtualMachines"),
        "Virtual Network": ("Microsoft.Network", "publicIPAddresses"),
    }

    RESOURCE_LOCATION = (
        ("US East", "US East"),
        ("US East", "Zone 1"),
        ("US East", ""),
        ("US North Central", "US North Central"),
        ("US North Central", "Zone 1"),
        ("US North Central", ""),
        ("US South Central", "US South Central"),
        ("US South Central", "Zone 1"),
        ("US South Central", ""),
        ("US West", "US West"),
        ("US West", "Zone 1"),
        ("US West", ""),
        ("US Central", "US Central"),
        ("US Central", "Zone 1"),
        ("US Central", ""),
        ("US East 2", "US East 2"),
        ("US West 2", "US West 2"),
    )

    SERVICE_NAMES = ["SQL Database", "Storage", "Virtual Machines", "Virtual Network"]

    TEMPLATE = "azure.j2"

    TEMPLATE_KWARGS = {
        "payer": AbstractGenerator.fake.uuid4(),
        "users": [AbstractGenerator.fake.uuid4() for _ in range(0, randint(2, 6))],
    }

    def __init__(self, start_date, end_date, cache={}, user_config=None):
        """Initialize the generator."""
        # generate the same number of elements as the static file, if there is one
        # this is needed to ensure that deepupdate() works correctly.
        gen_count = randint(2, 6)
        if user_config:
            preload = load_yaml(user_config)
            seen = {}
            for generators in preload.get("generators"):
                for key in generators.keys():
                    if key in seen.keys():
                        seen[key] += 1
                    else:
                        seen[key] = 1
            name = type(self).__name__
            if name in seen:
                gen_count = seen[name]
        self._gen_fake_data(gen_count)

        # pass an element of the instance_id defaults into the template
        svcname, svctype = self._get_accts_str(self.SERVICE_NAME)
        self.TEMPLATE_KWARGS["_service_name"] = "{}/{}".format(svcname, svctype[:-1])

        super().__init__(start_date, end_date, user_config=user_config)

        self._meter_cache = cache

    @abstractmethod
    def _gen_fake_data(self, count):
        """Populate TEMPLATE_KWARGS with fake values."""

    def _format_config(self, config):
        """Handle special cases in the config layout."""
        # handle payer and account info and invoice id
        accounts = config.get("accounts", {})
        payer = accounts.get("payer")
        users = accounts.get("user", [])

        updated = deepcopy(config)
        for idx, gen in enumerate(config.get("generators", [])):
            for key, val in gen.items():
                if not val.get("payer_account"):
                    updated["generators"][idx][key]["payer_account"] = payer
                if not val.get("usage_accounts"):
                    updated["generators"][idx][key]["usage_accounts"] = tuple(set([payer] + users))
        return updated

    def _get_accts_str(self, service_name):
        """Return instance idea fields."""
        if service_name == "Bandwidth":
            service_name = choice(self.SERVICE_NAMES)
        return self.ACCTS_STR[service_name]

    def _get_cached_meter_values(self, meter_id, service_meter):
        """Return meter cached meter data to ensure meter_id and values are consistent."""
        if not self._meter_cache.get(meter_id):
            self._meter_cache[meter_id] = choice(service_meter)
        return self._meter_cache.get(meter_id)

    def _get_resource_info(self, meter_id, service_meter, ex_resource, add_info, service_info):
        """Return resource information."""
        service_tier, meter_sub, meter_name, units_of_measure = self._get_cached_meter_values(meter_id, service_meter)

        resource_group, resource_name = choice(ex_resource)
        additional_info = choice(add_info)
        service_info_2 = choice(service_info)
        self._consumed, second_part = self._get_accts_str(self.SERVICE_NAME)
        self._resource_type = self._consumed + "/" + second_part

        return (resource_group, service_tier, meter_sub, meter_name, units_of_measure, additional_info, service_info_2)

    def _get_location_info(self, config={}):
        """Get bandwidth info."""
        azure_region, meter_region = self._get_location(config)
        return azure_region, meter_region

    def _init_data_row(self, start, end, **kwargs):  # noqa: C901
        """Create a row of data with placeholder for all headers."""
        if not (start and end):
            raise ValueError("start and end must be date objects.")
        if not isinstance(start, datetime.datetime):
            raise ValueError("start must be a date object.")
        if not isinstance(end, datetime.datetime):
            raise ValueError("end must be a date object.")

        row = {}
        for column in AZURE_COLUMNS:
            row[column] = ""
            if column == "SubscriptionGuid":
                row[column] = self.config[0].get("payer_account")
        return row

    def _get_location(self, config={}):
        """Pick resource location."""
        filtered = list(filter(lambda x: config.get("resource_location") in x, self.RESOURCE_LOCATION))
        if filtered:
            location = choice(filtered)
        else:
            location = choice(self.RESOURCE_LOCATION)
        return location

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Add common usage information."""
        row["SubscriptionGuid"] = self.config[0].get("payer_account")
        row["UsageDateTime"] = start
        return row

    def _add_tag_data(self, row, config):
        """Add tag dictionary data options to the row."""
        row["Tags"] = json.dumps(config.get("tags"))

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        current_config = kwargs.get("config", {})

        row = self._add_common_usage_info(row, start, end)

        meter_id = current_config.get("meter_id")
        rate = current_config.get("resource_rate ")
        amount = current_config.get("usage_quantity")
        cost = current_config.get("pre_tax_cost") if current_config.get("pre_tax_cost") else amount * rate
        azure_region, meter_region = self._get_location_info(current_config)
        instance_id = current_config.get("instance_id")
        (
            resource_group,
            service_tier,
            meter_sub,
            meter_name,
            units_of_measure,
            additional_info,
            service_info_2,
        ) = self._get_resource_info(
            meter_id, self.SERVICE_METER, self.EXAMPLE_RESOURCE, self.ADDITIONAL_INFO, self.SERVICE_INFO_2
        )
        if not additional_info:
            additional_info = ""
        if not service_info_2:
            service_info_2 = ""

        row["ResourceGroup"] = resource_group
        row["ResourceLocation"] = azure_region
        row["MeterCategory"] = self.SERVICE_NAME
        row["MeterSubcategory"] = meter_sub
        row["MeterId"] = str(meter_id)
        row["MeterName"] = meter_name
        row["MeterRegion"] = meter_region
        row["UsageQuantity"] = str(amount)
        row["ResourceRate"] = str(rate)
        row["PreTaxCost"] = str(cost)
        row["ConsumedService"] = self._consumed
        row["ResourceType"] = self._resource_type
        row["InstanceId"] = instance_id
        row["OfferId"] = ""
        row["AdditionalInfo"] = json.dumps(additional_info)
        row["ServiceInfo1"] = ""
        row["ServiceInfo2"] = service_info_2
        row["ServiceName"] = self.SERVICE_NAME
        row["ServiceTier"] = service_tier
        row["Currency"] = "USD"
        row["UnitOfMeasure"] = units_of_measure
        self._add_tag_data(row, current_config)

        return row

    def _generate_hourly_data(self, **kwargs):
        """Create hourly data."""
        # not required for azure
        return []

    def _generate_daily_data(self):
        """Create daily data."""
        data = []
        for day in self.days:
            for cfg in self.config:
                start = day.get("start")
                end = day.get("end")
                row = self._init_data_row(start, end)
                row = self._update_data(row, start, end, config=cfg)
                data.append(row)
        return data

    def generate_data(self, report_type=None):
        """Responsible for generating data."""
        return self._generate_daily_data()

    def get_meter_cache(self):
        """Return the meter cache for cross month generation."""
        return self._meter_cache
