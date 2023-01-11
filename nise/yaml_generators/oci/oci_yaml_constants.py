#
# Copyright 2023 Red Hat, Inc.
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
"""OCI Yaml File Constants"""
import typing as t
from dataclasses import dataclass

from faker import Faker


FAKE = Faker()


@dataclass(frozen=True)
class OCIYamlConstants:
    """OCI yaml constant columns"""

    tenant_id: str = "ocid1.tenancy.oc1..EfjkUPxyZSYLvd"
    compartment_name: str = FAKE.name().replace(" ", "").lower()
    subscription_id: int = FAKE.random_number(fix_len=True, digits=8)


@dataclass(frozen=True)
class OCITags:
    """OCI Tags"""

    storage: t.Tuple[str] = ("tags/new-tags.tarnished-tags", "tags/orcl-cloud.free-tier-retained")
    compute: t.Tuple[str] = ("tags/free-form-tag", "tags/orcl-cloud.free-tier-retained")
    database: t.Tuple[str] = ("tags/free-form-tag",)
    network: t.Tuple[str] = ("tags/free-form-tag",)
