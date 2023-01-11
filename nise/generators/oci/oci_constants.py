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
"""OCI Report Constants"""
import random
from dataclasses import dataclass
from dataclasses import field

from faker import Faker


FAKE = Faker()


@dataclass(frozen=True)
class OCIRegionDomain:
    """OCI region and domain"""

    region: str
    domain: str


def random_region_domain():
    """Return random region domain"""
    return random.choice(
        (
            OCIRegionDomain("ap-sydney-1", 1),
            OCIRegionDomain("ap-melbourne-1", 1),
            OCIRegionDomain("sa-saopaulo-1", 1),
            OCIRegionDomain("sa-vinhedo-1", 1),
            OCIRegionDomain("ca-montreal-1", 1),
            OCIRegionDomain("ca-toronto-1", 1),
            OCIRegionDomain("sa-santiago-1", 1),
            OCIRegionDomain("eu-marseille-1", 1),
            OCIRegionDomain("eu-frankfurt-1", 3),
            OCIRegionDomain("ap-hyderabad-1", 1),
            OCIRegionDomain("ap-mumbai-1", 1),
            OCIRegionDomain("il-jerusalem-1", 1),
            OCIRegionDomain("eu-milan-1", 1),
            OCIRegionDomain("ap-osaka-1", 1),
            OCIRegionDomain("ap-tokyo-1", 1),
            OCIRegionDomain("eu-amsterdam-1", 1),
            OCIRegionDomain("me-jeddah-1", 1),
            OCIRegionDomain("ap-singapore-1", 1),
            OCIRegionDomain("af-johannesburg-1", 1),
            OCIRegionDomain("ap-seoul-1", 1),
            OCIRegionDomain("ap-chuncheon-1", 1),
            OCIRegionDomain("eu-stockholm-1", 1),
            OCIRegionDomain("eu-zurich-1", 1),
            OCIRegionDomain("me-abudhabi-1", 1),
            OCIRegionDomain("me-dubai-1", 1),
            OCIRegionDomain("uk-london-1", 1),
            OCIRegionDomain("uk-cardiff-1", 1),
            OCIRegionDomain("us-ashburn-1", 3),
            OCIRegionDomain("us-phoenix-1", 3),
            OCIRegionDomain("us-sanjose-1", 1),
        )
    )


@dataclass(frozen=True)
class OCIReportConstantColumns:
    """OCI report constant columns"""

    tenant_id: str = f"ocid1.tenancy.oc1..{FAKE.pystr(min_chars=15, max_chars=25)}"
    subscription_id: int = FAKE.random_number(fix_len=True, digits=8)
    compartment_name: str = FAKE.name().replace(" ", "").lower()
    region_to_domain: OCIRegionDomain = field(default_factory=random_region_domain)
