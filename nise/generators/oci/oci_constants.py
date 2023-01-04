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
from faker import Faker


class OCIReportConstantColumns:
    """OCI report constant columns"""

    fake = Faker()
    tenant_id = f"ocid1.tenancy.oc1..{fake.pystr(min_chars=15, max_chars=25)}"
    subscription_id = fake.random_number(fix_len=True, digits=8)
    compartment_name = fake.name().replace(" ", "").lower()
    oci_regions_to_domain = [
        {"region": "ap-sydney-1", "domain": 1},
        {"region": "ap-melbourne-1", "domain": 1},
        {"region": "sa-saopaulo-1", "domain": 1},
        {"region": "sa-vinhedo-1", "domain": 1},
        {"region": "ca-montreal-1", "domain": 1},
        {"region": "ca-toronto-1", "domain": 1},
        {"region": "sa-santiago-1", "domain": 1},
        {"region": "eu-marseille-1", "domain": 1},
        {"region": "eu-frankfurt-1", "domain": 3},
        {"region": "ap-hyderabad-1", "domain": 1},
        {"region": "ap-mumbai-1", "domain": 1},
        {"region": "il-jerusalem-1", "domain": 1},
        {"region": "eu-milan-1", "domain": 1},
        {"region": "ap-osaka-1", "domain": 1},
        {"region": "ap-tokyo-1", "domain": 1},
        {"region": "eu-amsterdam-1", "domain": 1},
        {"region": "me-jeddah-1", "domain": 1},
        {"region": "ap-singapore-1", "domain": 1},
        {"region": "af-johannesburg-1", "domain": 1},
        {"region": "ap-seoul-1", "domain": 1},
        {"region": "ap-chuncheon-1", "domain": 1},
        {"region": "eu-stockholm-1", "domain": 1},
        {"region": "eu-zurich-1", "domain": 1},
        {"region": "me-abudhabi-1", "domain": 1},
        {"region": "me-dubai-1", "domain": 1},
        {"region": "uk-london-1", "domain": 1},
        {"region": "uk-cardiff-1", "domain": 1},
        {"region": "us-ashburn-1", "domain": 3},
        {"region": "us-phoenix-1", "domain": 3},
        {"region": "us-sanjose-1", "domain": 1},
    ]
