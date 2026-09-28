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
"""Module for ebs data generation."""

import calendar
from random import choice
from random import uniform

from nise.generators.aws.aws_generator import AWSGenerator


class EBSGenerator(AWSGenerator):
    """Generator for EBS data."""

    STORAGE = (
        ("Hundreds", "40 - 200", "40 - 90 MB/sec", "1 TiB", "HDD-backed", "Magnetic"),
        ("3000 for volumes <= 1 TiB", "10000", "160 MB/sec", "16 TiB", "SSD-backed", "General Purpose"),
    )

    # Optional YAML keys for provisioned-performance CUR lines (COST-8328).
    # Example:
    #   volume_api_name: gp3
    #   provisioned_throughput:
    #     rate: 49.152
    #     cost: 0.0116666667   # hourly; use 0 for baseline "ghost" rows
    #   provisioned_iops:
    #     rate: 0.006
    #     cost: 0.025
    PROVISIONED_THROUGHPUT_KEY = "provisioned_throughput"
    PROVISIONED_IOPS_KEY = "provisioned_iops"

    def __init__(self, start_date, end_date, currency, payer_account, usage_accounts, attributes=None, tag_cols=None):
        """Initialize the EBS generator."""
        super().__init__(start_date, end_date, currency, payer_account, usage_accounts, attributes, tag_cols)
        self._resource_id = f"vol-{self.fake.ean8()}"
        self._disk_size = choice([5, 10, 15, 20, 25])
        self._rate = round(uniform(0.02, 0.16), 3)
        self._product_sku = self.fake.pystr(min_chars=12, max_chars=12).upper()
        self._volume_api_name = None
        self._provisioned_throughput = None
        self._provisioned_iops = None

        if self.attributes:
            if self.attributes.get("resource_id"):
                self._resource_id = "vol-{}".format(self.attributes.get("resource_id"))
            if self.attributes.get("rate"):
                self._rate = float(self.attributes.get("rate"))
            if self.attributes.get("product_sku"):
                self._product_sku = self.attributes.get("product_sku")
            if self.attributes.get("tags"):
                self._tags = self.attributes.get("tags")
            if _disk_size := self.attributes.get("disk_size"):
                self._disk_size = int(_disk_size)
            if volume_api_name := self.attributes.get("volume_api_name"):
                self._volume_api_name = str(volume_api_name)
            self._provisioned_throughput = self._parse_provisioned_attrs(self.PROVISIONED_THROUGHPUT_KEY)
            self._provisioned_iops = self._parse_provisioned_attrs(self.PROVISIONED_IOPS_KEY)
            if (self._provisioned_throughput or self._provisioned_iops) and not self._volume_api_name:
                self._volume_api_name = "gp3"

    def _parse_provisioned_attrs(self, key):
        """Parse optional provisioned throughput/IOPS YAML block."""
        raw = (self.attributes or {}).get(key)
        if not raw:
            return None
        if not isinstance(raw, dict):
            raise ValueError(f"{key} must be a mapping with at least 'rate'")
        if raw.get("rate") is None:
            raise ValueError(f"{key} requires 'rate'")
        rate = float(raw["rate"])
        if raw.get("cost") is not None:
            cost = float(raw["cost"])
        elif raw.get("amount") is not None:
            cost = float(raw["amount"]) * rate
        else:
            cost = 0.0
        amount = (cost / rate) if rate else 0.0
        return {"rate": rate, "cost": cost, "amount": amount}

    def _get_storage(self):
        """Get storage data."""
        return choice(self.STORAGE)

    def _calculate_hourly_rate(self, start):
        """Calculates the houly rate based of the provided monthly rate."""
        num_days_in_month = calendar.monthrange(start.year, start.month)[1]
        hours_in_month = num_days_in_month * 24
        return self._rate / hours_in_month

    def _usage_type(self, storage_region, kind):
        """Build CUR usage type, optionally with volume API suffix (e.g. .gp3)."""
        base = f"{storage_region}:{kind}"
        if self._volume_api_name:
            return f"{base}.{self._volume_api_name}"
        return base

    def _update_data(self, row, start, end, location=None, **kwargs):
        """Update data with generator specific data."""
        row = self._add_common_usage_info(row, start, end)
        hourly_rate = self._calculate_hourly_rate(start)
        cost = round(self._disk_size * hourly_rate, 10)
        amount = round(cost / self._rate, 10)
        if location is None:
            location = self._get_location()
        loc_name, aws_region, _, storage_region = location
        description = f"${self._rate} per GB-Month of snapshot data stored - {loc_name}"
        burst, max_iops, max_thru, max_vol_size, vol_backed, vol_type = self._get_storage()
        usage_type = self._usage_type(storage_region, "VolumeUsage")

        row["lineItem/ProductCode"] = "AmazonEC2"
        row["lineItem/UsageType"] = usage_type
        row["lineItem/Operation"] = "CreateVolume"
        row["lineItem/ResourceId"] = self._resource_id
        row["lineItem/UsageAmount"] = str(amount)
        row["lineItem/UnblendedRate"] = str(self._rate)
        row["lineItem/UnblendedCost"] = str(cost)
        row["lineItem/BlendedRate"] = str(self._rate)
        row["lineItem/BlendedCost"] = str(cost)
        row["lineItem/LineItemDescription"] = description
        row["product/ProductName"] = "Amazon Elastic Compute Cloud"
        row["product/location"] = loc_name
        row["product/locationType"] = "AWS Region"
        row["product/maxIopsBurstPerformance"] = burst
        row["product/maxIopsvolume"] = max_iops
        row["product/maxThroughputvolume"] = max_thru
        row["product/maxVolumeSize"] = max_vol_size
        row["product/productFamily"] = "Storage"
        row["product/region"] = aws_region
        row["product/servicecode"] = "AmazonEC2"
        row["product/sku"] = self._product_sku
        row["product/storageMedia"] = vol_backed
        row["product/usagetype"] = usage_type
        row["product/volumeType"] = vol_type
        row["pricing/publicOnDemandCost"] = str(cost)
        row["pricing/publicOnDemandRate"] = str(self._rate)
        row["pricing/term"] = "OnDemand"
        row["pricing/unit"] = "GB-Mo"
        self._add_tag_data(row)
        self._add_category_data(row)
        return row

    def _update_provisioned_data(self, row, start, end, *, location, kind, rate, cost, amount, unit, description):
        """Fill a provisioned throughput or IOPS CUR line for the same volume."""
        row = self._add_common_usage_info(row, start, end)
        loc_name, aws_region, _, storage_region = location
        usage_type = self._usage_type(storage_region, kind)
        burst, max_iops, max_thru, max_vol_size, vol_backed, vol_type = self._get_storage()

        row["lineItem/ProductCode"] = "AmazonEC2"
        row["lineItem/UsageType"] = usage_type
        row["lineItem/Operation"] = "CreateVolume"
        row["lineItem/ResourceId"] = self._resource_id
        row["lineItem/UsageAmount"] = str(amount)
        row["lineItem/UnblendedRate"] = str(rate)
        row["lineItem/UnblendedCost"] = str(cost)
        row["lineItem/BlendedRate"] = str(rate)
        row["lineItem/BlendedCost"] = str(cost)
        row["lineItem/LineItemDescription"] = f"{description} - {loc_name}"
        row["product/ProductName"] = "Amazon Elastic Compute Cloud"
        row["product/location"] = loc_name
        row["product/locationType"] = "AWS Region"
        row["product/maxIopsBurstPerformance"] = burst
        row["product/maxIopsvolume"] = max_iops
        row["product/maxThroughputvolume"] = max_thru
        row["product/maxVolumeSize"] = max_vol_size
        row["product/productFamily"] = "System Operation"
        row["product/region"] = aws_region
        row["product/servicecode"] = "AmazonEC2"
        row["product/sku"] = self._product_sku
        row["product/storageMedia"] = vol_backed
        row["product/usagetype"] = usage_type
        row["product/volumeType"] = vol_type
        row["pricing/publicOnDemandCost"] = str(cost)
        row["pricing/publicOnDemandRate"] = str(rate)
        row["pricing/term"] = "OnDemand"
        row["pricing/unit"] = unit
        self._add_tag_data(row)
        self._add_category_data(row)
        return row

    def _generate_hourly_data(self, **kwargs):
        """Create hourly storage rows plus optional provisioned-performance lines."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            location = self._get_location()
            row = self._init_data_row(start, end)
            yield self._update_data(row, start, end, location=location)

            if self._provisioned_throughput:
                thru = self._provisioned_throughput
                thru_row = self._init_data_row(start, end)
                yield self._update_provisioned_data(
                    thru_row,
                    start,
                    end,
                    location=location,
                    kind="VolumeP-Throughput",
                    rate=thru["rate"],
                    cost=thru["cost"],
                    amount=thru["amount"],
                    unit="GiBps-Mo",
                    description=f"${thru['rate']} per provisioned MiBps-month of gp3",
                )

            if self._provisioned_iops:
                iops = self._provisioned_iops
                iops_row = self._init_data_row(start, end)
                yield self._update_provisioned_data(
                    iops_row,
                    start,
                    end,
                    location=location,
                    kind="VolumeP-IOPS",
                    rate=iops["rate"],
                    cost=iops["cost"],
                    amount=iops["amount"],
                    unit="IOPS-Mo",
                    description=f"${iops['rate']} per provisioned IOPS-month of gp3",
                )

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
