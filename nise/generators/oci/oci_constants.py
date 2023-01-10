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


fake = Faker()


@dataclass(frozen=True)
class OCIRegions:
    """OCI Regions"""

    region: str
    domain: str


def random_region_domain():
    """get random region domain tuple"""
    return random.choice(
        (
            OCIRegions("ap-sydney-1", 1),
            OCIRegions("ap-melbourne-1", 1),
            OCIRegions("sa-saopaulo-1", 1),
            OCIRegions("sa-vinhedo-1", 1),
            OCIRegions("ca-montreal-1", 1),
            OCIRegions("ca-toronto-1", 1),
            OCIRegions("sa-santiago-1", 1),
            OCIRegions("eu-marseille-1", 1),
            OCIRegions("eu-frankfurt-1", 3),
            OCIRegions("ap-hyderabad-1", 1),
            OCIRegions("ap-mumbai-1", 1),
            OCIRegions("il-jerusalem-1", 1),
            OCIRegions("eu-milan-1", 1),
            OCIRegions("ap-osaka-1", 1),
            OCIRegions("ap-tokyo-1", 1),
            OCIRegions("eu-amsterdam-1", 1),
            OCIRegions("me-jeddah-1", 1),
            OCIRegions("ap-singapore-1", 1),
            OCIRegions("af-johannesburg-1", 1),
            OCIRegions("ap-seoul-1", 1),
            OCIRegions("ap-chuncheon-1", 1),
            OCIRegions("eu-stockholm-1", 1),
            OCIRegions("eu-zurich-1", 1),
            OCIRegions("me-abudhabi-1", 1),
            OCIRegions("me-dubai-1", 1),
            OCIRegions("uk-london-1", 1),
            OCIRegions("uk-cardiff-1", 1),
            OCIRegions("us-ashburn-1", 3),
            OCIRegions("us-phoenix-1", 3),
            OCIRegions("us-sanjose-1", 1),
        )
    )


@dataclass(frozen=True)
class OCIReportConstantColumns:
    """OCI report constant columns"""

    tenant_id: str = f"ocid1.tenancy.oc1..{fake.pystr(min_chars=15, max_chars=25)}"
    subscription_id: int = fake.random_number(fix_len=True, digits=8)
    compartment_name: str = fake.name().replace(" ", "").lower()
    oci_regions_to_domain: dict = field(default_factory=(random_region_domain))
