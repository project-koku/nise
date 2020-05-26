#
# Copyright 2020 Red Hat, Inc.
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
"""OCP Generator Unit Tests."""

from datetime import datetime, timedelta
from unittest import TestCase

from faker import Faker

from nise.generators.ocp.ocp_generator import (
    OCPGenerator,
    OCP_POD_USAGE,
    OCP_POD_USAGE_COLUMNS,
    OCP_NODE_LABEL,
    OCP_NODE_LABEL_COLUMNS,
)


class OCPGeneratorTestCase(TestCase):
    """TestCase class for OCP Generator."""

    def setUp(self):
        """Test setup."""
        self.fake = Faker()
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.one_day = timedelta(hours=24)
        self.two_hours_ago = self.now - (2 * self.one_hour)

        def _usage_dict():
            dikt = {}
            for _ in range(0, self.fake.pyint(3, 10)):
                day = self.fake.date_between_dates(self.now - (7 * self.one_day), self.now)
                dikt[day.strftime("%m-%d-%Y")] = self.fake.pyint(1, 10)
            return dikt

        self.attributes = {
            "nodes": [
                {
                    "node": self.fake.uuid4(),
                    "node_name": self.fake.word(),
                    "cpu_cores": self.fake.pyint(1, 10),
                    "memory_gig": self.fake.pyint(1, 32),
                    "namespaces": {
                        f"namespace_{self.fake.word()}": {
                            "pods": [
                                {
                                    "pod": self.fake.uuid4(),
                                    "pod_name": f"pod_{self.fake.word()}",
                                    "cpu_request": self.fake.pyint(1, 10),
                                    "mem_request_gig": self.fake.pyint(1, 32),
                                    "cpu_limit": self.fake.pyint(1, 10),
                                    "mem_limit_gig": self.fake.pyint(1, 32),
                                    "pod_seconds": self.fake.pyint(300, 3600),
                                    "cpu_usage": _usage_dict(),
                                    "mem_usage_gig": _usage_dict(),
                                    "labels": (
                                        f"label_{self.fake.word()}:{self.fake.word()}",
                                        f"|label_{self.fake.word()}:{self.fake.word()}",
                                    ),
                                },
                                {
                                    "pod": self.fake.uuid4(),
                                    "pod_name": f"pod_{self.fake.word()}",
                                    "cpu_request": self.fake.pyint(1, 10),
                                    "mem_request_gig": self.fake.pyint(1, 32),
                                    "cpu_limit": self.fake.pyint(1, 10),
                                    "mem_limit_gig": self.fake.pyint(1, 32),
                                    "labels": (
                                        f"label_{self.fake.word()}:{self.fake.word()}",
                                        f"|label_{self.fake.word()}:{self.fake.word()}",
                                    ),
                                },
                            ],
                            "volumes": [
                                {
                                    "volume_name": f"vol_{self.fake.word()}",
                                    "volume_request_gig": self.fake.pyint(1, 100),
                                    "volume_claims": [
                                        {
                                            "volume_claim_name": f"volumeclaim_{self.fake.word()}",
                                            "pod_name": f"pod_{self.fake.word()}",
                                            "capacity_gig": self.fake.pyint(1, 100),
                                            "volume_claim_usage_gig": self.fake.pyint(1, 100),
                                        }
                                    ],
                                }
                            ],
                        }
                    },
                }
            ],
        }

    def test_init_no_attributes(self):
        """Test the init without attributes."""
        generator = OCPGenerator(self.two_hours_ago, self.now, {})

        for attribute in [
            "nodes",
            "namespaces",
            "pods",
            "namespace2pods",
            "volumes",
        ]:
            with self.subTest(attribute=attribute):
                attr = getattr(generator, attribute)
                self.assertIsNotNone(attr)

                if attribute == "nodes":
                    self.assertIsInstance(attr, list)
                    self.assertNotEqual(attr, [])
                else:
                    self.assertIsInstance(attr, dict)
                    self.assertNotEqual(attr, {})

    def test_init_with_attributes(self):
        """Test the init with attributes."""
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)

        for attribute in [
            "nodes",
            "namespaces",
            "pods",
            "namespace2pods",
            "volumes",
        ]:
            with self.subTest(attribute=attribute):
                attr = getattr(generator, attribute)
                self.assertIsNotNone(attr)

                if attribute == "nodes":
                    self.assertIsInstance(attr, list)
                    self.assertNotEqual(attr, [])
                else:
                    self.assertIsInstance(attr, dict)
                    self.assertNotEqual(attr, {})

    def test_add_common_usage_info(self):
        """Test that add_common_usage_info updates usage timestamps."""
        generator = OCPGenerator(self.two_hours_ago, self.now, {})
        test_row = {}
        output_row = generator._add_common_usage_info(test_row, self.two_hours_ago, self.now)
        self.assertIn("interval_start", output_row)
        self.assertIn("interval_end", output_row)

    def test_gen_hourly_node_label_usage(self):
        """Test that gen_hourly_node_label_usage generates rows."""
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)
        namespaces = self.attributes.get("nodes")[0].get("namespaces")
        for dikt in namespaces.values():
            pods = dikt.get("pods")
            for pod in pods:
                with self.subTest(pod=pod):
                    for row in generator._gen_hourly_node_label_usage(report_type=OCP_NODE_LABEL, pod=pod):
                        self.assertIsInstance(row, dict)
                        for col in OCP_NODE_LABEL_COLUMNS:
                            self.assertIn(col, row)
                            self.assertIsNotNone(row[col])
                        break  # only test one row

    def test_gen_hourly_pods_usage(self):
        """Test that gen_hourly_pods_usage generates rows."""
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)
        namespaces = self.attributes.get("nodes")[0].get("namespaces")
        for dikt in namespaces.values():
            pods = dikt.get("pods")
            for pod in pods:
                with self.subTest(pod=pod):
                    for row in generator._gen_hourly_pods_usage(report_type=OCP_POD_USAGE, pod=pod):
                        self.assertIsInstance(row, dict)
                        for col in OCP_POD_USAGE_COLUMNS:
                            self.assertIn(col, row)
                            self.assertIsNotNone(row[col])
                        break  # only test one row

    def test_gen_hourly_storage_usage(self):
        """Test."""
        pass

    def test_gen_namespaces(self):
        """Test."""
        pass

    def test_gen_nodes(self):
        """Test."""
        pass

    def test_gen_openshift_labels(self):
        """Test."""
        pass

    def test_gen_pods(self):
        """Test."""
        pass

    def test_gen_volumes(self):
        """Test."""
        pass

    def test_generate_hourly_data(self):
        """Test."""
        pass

    def test_get_usage_for_date(self):
        """Test."""
        pass

    def test_init_data_row(self):
        """Test."""
        pass

    def test_update_data(self):
        """Test."""
        pass

    def test_update_node_label_data(self):
        """Test."""
        pass

    def test_update_pod_data(self):
        """Test."""
        pass

    def test_update_storage_data(self):
        """Test."""
        pass

    def test_generate_data(self):
        """Test."""
        pass

    def test_timestamp(self):
        """Test."""
        pass
