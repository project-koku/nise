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
import string
from abc import abstractmethod
from copy import deepcopy
from random import choice
from random import randint

from nise.generators.aws.constants import BILL_COLS
from nise.generators.aws.constants import IDENTITY_COLS
from nise.generators.aws.constants import LINE_ITEM_COLS
from nise.generators.aws.constants import PRICING_COLS
from nise.generators.aws.constants import PRODUCT_COLS
from nise.generators.aws.constants import REGIONS
from nise.generators.aws.constants import RESERVE_COLS
from nise.generators.generator import AbstractGenerator
from nise.util import load_yaml


class AWSGenerator(AbstractGenerator):
    """Defines a abstract class for generators."""

    RESOURCE_TAG_COLS = {
        "resourceTags/user:environment",
        "resourceTags/user:app",
        "resourceTags/user:version",
        "resourceTags/user:storageclass",
        "resourceTags/user:openshift_cluster",
        "resourceTags/user:openshift_project",
        "resourceTags/user:openshift_node",
    }
    AWS_COLUMNS = set(
        IDENTITY_COLS
        + BILL_COLS
        + LINE_ITEM_COLS
        + PRODUCT_COLS
        + PRICING_COLS
        + RESERVE_COLS
        + tuple(RESOURCE_TAG_COLS)
    )
    TEMPLATE = "aws.j2"

    TEMPLATE_KWARGS = {
        "payer": AbstractGenerator.fake.ean13(),
        "users": [AbstractGenerator.fake.ean13() for _ in range(0, randint(2, 6))],
        "invoice_id": "".join([choice(string.digits) for _ in range(9)]),
    }

    def __init__(self, start_date, end_date, user_config=None):
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

        super().__init__(start_date, end_date, user_config=user_config)

        tag_cols = []
        self._tags = {}
        for cfg in self.config:
            for key, value in cfg.get("tags", {}).items():
                tag_cols.append(str(key))
                self._tags[key] = value

        self.num_instances = randint(2, 60)
        if tag_cols:
            self.RESOURCE_TAG_COLS.update(tag_cols)
            self.AWS_COLUMNS.update(tag_cols)

    @abstractmethod
    def _gen_fake_data(self, count):
        """Populate TEMPLATE_KWARGS with fake values."""

    def _format_config(self, config):
        """Handle special cases in the config layout."""
        # handle payer and account info and invoice id
        accounts = config.get("accounts", {})
        payer = accounts.get("payer")
        users = accounts.get("user", [])
        invoice_id = accounts.get("invoice_id")

        updated = deepcopy(config)
        for idx, gen in enumerate(config.get("generators")):
            for key, val in gen.items():
                if not val.get("payer_account"):
                    updated["generators"][idx][key]["payer_account"] = payer
                if not val.get("usage_accounts"):
                    updated["generators"][idx][key]["usage_accounts"] = tuple(set([payer] + users))
                if not val.get("invoice_id"):
                    updated["generators"][idx][key]["invoice_id"] = invoice_id
        return updated

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not (in_date and isinstance(in_date, datetime.datetime)):
            raise ValueError("in_date must be a date object.")
        return in_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def time_interval(start, end):
        """Create a time interval string from input dates."""
        start_str = AWSGenerator.timestamp(start)
        end_str = AWSGenerator.timestamp(end)
        return str(start_str) + "/" + str(end_str)

    def _pick_tag(self, tag_key, options):
        """Generate tag from options."""
        if self._tags:
            tags = self._tags.get(tag_key)
        else:
            tags = choice(options)
        return tags

    def _init_data_row(self, start, end, **kwargs):  # noqa: C901
        """Create a row of data with placeholder for all headers."""
        if not (start and end):
            raise ValueError("start and end must be date objects.")
        if not isinstance(start, datetime.datetime):
            raise ValueError("start must be a date object.")
        if not isinstance(end, datetime.datetime):
            raise ValueError("end must be a date object.")

        bill_begin = start.replace(microsecond=0, second=0, minute=0, hour=0, day=1)
        bill_end = AbstractGenerator.next_month(bill_begin)
        row = {}
        COL_MAP = {
            "identity/LineItemId": self.fake.sha1(raw_output=False),
            "identity/TimeInterval": AWSGenerator.time_interval(start, end),
            "bill/BillingEntity": "AWS",
            "bill/BillType": "Anniversary",
            "bill/PayerAccountId": kwargs.get("config", {}).get("payer_account"),
            "bill/BillingPeriodStartDate": AWSGenerator.timestamp(bill_begin),
            "bill/BillingPeriodEndDate": AWSGenerator.timestamp(bill_end),
        }
        for column in self.AWS_COLUMNS:
            row[column] = ""
            if COL_MAP.get(column):
                row[column] = COL_MAP.get(column)

        return row

    def _get_location(self, config={}):
        """Pick instance location."""
        if config.get("region"):
            for region in REGIONS:
                if config.get("region") in region:
                    return region
        return choice(REGIONS)

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Add common usage information."""
        row["lineItem/UsageAccountId"] = choice(self.config[0].get("usage_accounts"))
        row["lineItem/LineItemType"] = "Usage"
        row["lineItem/UsageStartDate"] = start
        row["lineItem/UsageEndDate"] = end
        return row

    def _add_tag_data(self, row):
        """Add tag data to the row."""
        if self._tags:
            for tag in self._tags:
                row[tag] = self._tags[tag]
        else:
            num_tags = self.fake.random_int(0, 5)
            for _ in range(num_tags):
                seen_tags = set()
                tag_key = choice(list(self.RESOURCE_TAG_COLS))
                if tag_key not in seen_tags:
                    row[tag_key] = self.fake.word()
                    seen_tags.update([tag_key])

    def _generate_region_short_code(self, region):
        """Generate the AWS short code for a region."""
        split_region = region.split("-")
        return split_region[0][0:2].upper() + split_region[1][0].upper() + split_region[2]

    @abstractmethod
    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""

    def _generate_hourly_data(self, **kwargs):
        """Create hourly data."""
        for hour in self.hours:
            for cfg in self.config:
                start = hour.get("start")
                end = hour.get("end")
                row = self._init_data_row(start, end, config=cfg)
                row = self._update_data(row, start, end, config=cfg)
                yield row

    @abstractmethod
    def generate_data(self, report_type=None):
        """Responsible for generating data."""
