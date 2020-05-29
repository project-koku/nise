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
import random
from copy import copy
from datetime import datetime
from datetime import timedelta
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

from faker import Faker
from nise.generators.ocp.ocp_generator import GIGABYTE
from nise.generators.ocp.ocp_generator import OCP_NODE_LABEL
from nise.generators.ocp.ocp_generator import OCP_NODE_LABEL_COLUMNS
from nise.generators.ocp.ocp_generator import OCP_POD_USAGE
from nise.generators.ocp.ocp_generator import OCP_POD_USAGE_COLUMNS
from nise.generators.ocp.ocp_generator import OCP_STORAGE_COLUMNS
from nise.generators.ocp.ocp_generator import OCP_STORAGE_USAGE
from nise.generators.ocp.ocp_generator import OCPGenerator


# pylint: disable=protected-access,too-many-public-methods
class OCPGeneratorTestCase(TestCase):
    """TestCase class for OCP Generator."""

    def setUp(self):
        """Test setup."""
        self.fake = Faker()
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.one_day = timedelta(hours=24)
        self.two_hours_ago = self.now - (2 * self.one_hour)

        self.attributes = {
            "nodes": [
                {
                    "node": self.fake.uuid4(),
                    "node_name": self.fake.word(),
                    "node_labels": (
                        f"label_{self.fake.word()}:{self.fake.word()}",
                        f"|label_{self.fake.word()}:{self.fake.word()}",
                    ),
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
                                    "cpu_usage": self._usage_dict(),
                                    "mem_usage_gig": self._usage_dict(),
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
                                            "volume_claim_usage_gig": self._usage_dict(),
                                            "labels": (
                                                f"label_{self.fake.word()}:{self.fake.word()}",
                                                f"|label_{self.fake.word()}:{self.fake.word()}",
                                            ),
                                        }
                                    ],
                                    "labels": (
                                        f"label_{self.fake.word()}:{self.fake.word()}",
                                        f"|label_{self.fake.word()}:{self.fake.word()}",
                                    ),
                                }
                            ],
                        }
                    },
                }
            ]
        }

    def _usage_dict(self):
        dikt = {}
        for _ in range(0, self.fake.pyint(3, 10)):
            day = self.fake.date_between_dates(self.now - (7 * self.one_day), self.now)
            dikt[day.strftime("%m-%d-%Y")] = self.fake.pyint(1, 10)
        return dikt

    def test_init_no_attributes(self):
        """Test the init without attributes."""
        generator = OCPGenerator(self.two_hours_ago, self.now, {})

        for attribute in ["nodes", "namespaces", "pods", "namespace2pods", "volumes"]:
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

        for attribute in ["nodes", "namespaces", "pods", "namespace2pods", "volumes"]:
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
                            with self.subTest(row=row):
                                with self.subTest(col=col):
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
                    for row in generator._gen_hourly_pods_usage(report_type=OCP_POD_USAGE):
                        self.assertIsInstance(row, dict)
                        for col in OCP_POD_USAGE_COLUMNS:
                            with self.subTest(row=row):
                                with self.subTest(col=col):
                                    self.assertIn(col, row)
                                    self.assertIsNotNone(row[col])
                        break  # only test one row

    def test_gen_hourly_storage_usage(self):
        """Test that gen_hourly_storage_usage generates rows."""
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)
        namespaces = self.attributes.get("nodes")[0].get("namespaces")
        for dikt in namespaces.values():
            pods = dikt.get("pods")
            for pod in pods:
                with self.subTest(pod=pod):
                    for row in generator._gen_hourly_storage_usage(report_type=OCP_STORAGE_USAGE):
                        self.assertIsInstance(row, dict)
                        for col in OCP_STORAGE_COLUMNS:
                            with self.subTest(row=row):
                                with self.subTest(col=col):
                                    self.assertIn(col, row)
                                    self.assertIsNotNone(row[col])
                        break  # only test one row

    def test_gen_namespaces_with_namespace(self):
        """Test that gen_namespaces arranges the output dict in the expected way.

            If namespaces are specified, namespaces are not generated.
        """
        in_nodes = self.attributes.get("nodes")
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)
        out_namespaces = generator._gen_namespaces(in_nodes)
        self.assertEqual(list(out_namespaces.keys()), list(in_nodes[0].get("namespaces").keys()))
        for value in out_namespaces.values():
            with self.subTest(node=value):
                self.assertEqual(list(value.get("namespaces").keys()), list(in_nodes[0].get("namespaces").keys()))

    def test_gen_namespaces_without_namespace(self):
        """Test that gen_namespaces arranges the output dict in the expected way.

            If no namespaces are specified, namespaces are generated.
        """
        in_nodes = self.attributes.get("nodes")
        del in_nodes[0]["namespaces"]
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)
        out_namespaces = generator._gen_namespaces(in_nodes)

        # auto-generating namespaces should create at least 2 namespaces
        self.assertGreater(len(list(out_namespaces.keys())), 1)

        for value in out_namespaces.values():
            with self.subTest(namespace=value):
                self.assertEqual(list(value.keys()), list(in_nodes[0].keys()))

    def test_gen_nodes_with_nodes(self):
        """Test that gen_nodes arranges the output dict in the expected way.

            If nodes are specified, nodes are not generated.
        """
        in_nodes = self.attributes.get("nodes")
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)
        out_nodes = generator._gen_nodes()
        self.assertEqual(len(list(out_nodes)), len(list(in_nodes)))
        expected_keys = ["name", "cpu_cores", "memory_bytes", "resource_id", "namespaces", "node_labels"]
        self.assertEqual(list(out_nodes[0].keys()), expected_keys)

    def test_gen_nodes_without_nodes(self):
        """Test that gen_nodes arranges the output dict in the expected way.

            If nodes are not specified, nodes are generated.
        """
        generator = OCPGenerator(self.two_hours_ago, self.now, {})
        out_nodes = generator._gen_nodes()
        self.assertGreaterEqual(len(list(out_nodes)), 2)
        self.assertLessEqual(len(list(out_nodes)), 6)
        expected_keys = ["name", "cpu_cores", "memory_bytes", "resource_id", "node_labels"]
        self.assertEqual(list(out_nodes[0].keys()), expected_keys)

    def test_gen_openshift_labels(self):
        """Test that gen_openshift_labels creates well-formatted labels."""
        generator = OCPGenerator(self.two_hours_ago, self.now, {})
        out_labels = generator._gen_openshift_labels()
        matcher = r"(\w+:\w+)(\|(\w+:\w+))+"
        self.assertRegex(out_labels, matcher)

    def test_gen_pods_with_namespaces(self):
        """Test that gen_pods arranges the output dict in the expected way.

            If namespaces with pods are specified, defined pods are used.
        """
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)
        out_pods, _ = generator._gen_pods(generator.namespaces)  # gen_pods depends on the output of gen_namespaces.
        self.assertEqual(len(out_pods), 2)

        expected = (
            "cpu_limit",
            "cpu_request",
            "cpu_usage",
            "interval_start",
            "interval_end",
            "mem_limit_gig",
            "mem_request_gig",
            "mem_usage_gig",
            "namespace",
            "node",
            "node_capacity_cpu_cores",
            "node_capacity_cpu_core_seconds",
            "node_capacity_memory_bytes",
            "node_capacity_memory_byte_seconds",
            "node_labels",
            "pod",
            "pod_labels",
            "pod_limit_cpu_core_seconds",
            "pod_limit_memory_byte_seconds",
            "pod_request_cpu_core_seconds",
            "pod_request_memory_byte_seconds",
            "pod_seconds",
            "pod_usage_cpu_core_seconds",
            "pod_usage_memory_byte_seconds",
            "report_period_start",
            "report_period_end",
            "resource_id",
        )
        for pod in out_pods.values():
            with self.subTest(podkeys=pod.keys()):
                for key in pod.keys():
                    with self.subTest(key=key):
                        self.assertIn(key, expected)

    def test_gen_pods_without_namespaces(self):
        """Test that gen_pods arranges the output dict in the expected way.

            If no namespaces are specified, pods are generated.
        """
        generator = OCPGenerator(self.two_hours_ago, self.now, {})
        out_pods, _ = generator._gen_pods(generator.namespaces)

        # these magic numbers are the random ranges defined in the OCP generator.
        self.assertGreaterEqual(len(out_pods), 2 * 2 * 2)
        self.assertLessEqual(len(out_pods), 6 * 12 * 20)

        # This list isn't quite the same as (OCP_POD_USAGE_COLUMNS + OCP_NODE_LABEL_COLUMNS + OCP_STORAGE_COLUMNS)
        # This might be a bug.
        expected = (
            "cpu_limit",
            "cpu_request",
            "cpu_usage",
            "interval_start",
            "interval_end",
            "mem_limit_gig",
            "mem_request_gig",
            "mem_usage_gig",
            "namespace",
            "node",
            "node_capacity_cpu_cores",
            "node_capacity_cpu_core_seconds",
            "node_capacity_memory_bytes",
            "node_capacity_memory_byte_seconds",
            "node_labels",
            "pod",
            "pod_labels",
            "pod_limit_cpu_core_seconds",
            "pod_limit_memory_byte_seconds",
            "pod_request_cpu_core_seconds",
            "pod_request_memory_byte_seconds",
            "pod_seconds",
            "pod_usage_cpu_core_seconds",
            "pod_usage_memory_byte_seconds",
            "report_period_start",
            "report_period_end",
            "resource_id",
        )
        for pod in out_pods.values():
            with self.subTest(podkeys=pod.keys()):
                for key in pod.keys():
                    with self.subTest(key=key):
                        self.assertIn(key, expected)

    def test_gen_pods_usage_lt_capacity(self):
        """Test that gen_pods generates requests and usage values which don't exceed capacity."""
        for attributes in [self.attributes, {}]:
            with self.subTest(attributes=attributes):
                generator = OCPGenerator(self.two_hours_ago, self.now, attributes)
                # gen_pods depends on the output of gen_namespaces.
                out_pods, _ = generator._gen_pods(generator.namespaces)
                for pod in out_pods.values():
                    with self.subTest(pod=pod):
                        self.assertLessEqual(pod.get("cpu_limit"), pod.get("node_capacity_cpu_cores"))
                        self.assertLessEqual(pod.get("cpu_request"), pod.get("node_capacity_cpu_cores"))
                        self.assertLessEqual(pod.get("mem_limit_gig"), pod.get("node_capacity_memory_bytes"))
                        self.assertLessEqual(pod.get("mem_request_gig"), pod.get("node_capacity_memory_bytes"))
                        if attributes:
                            for value in pod.get("cpu_usage").values():
                                self.assertLessEqual(value, pod.get("node_capacity_cpu_cores"))
                            for value in pod.get("mem_usage_gig").values():
                                self.assertLessEqual(value, pod.get("node_capacity_memory_bytes"))

    def test_gen_volumes_with_namespaces(self):
        """Test that gen_volumes arranges the output dict in the expected way.

            If namespaces with volumes are specified, defined volumes are used.
        """
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)

        # gen_volumes depends on the output formatting of gen_namespaces and gen_pods.
        out_volumes = generator._gen_volumes(generator.namespaces, generator.namespace2pods)

        namespaces = self.attributes.get("nodes")[0].get("namespaces")
        volume_names = [vol.get("volume_name") for ns in namespaces for vol in namespaces.get(ns).get("volumes")]
        self.assertEqual(list(out_volumes.keys()), volume_names)

        expected = ["namespace", "volume", "storage_class", "volume_request", "labels", "volume_claims"]
        for vol in out_volumes.values():
            with self.subTest(volume=vol):
                self.assertEqual(list(vol.keys()), expected)

    def test_gen_volumes_without_namespaces(self):
        """Test that gen_volumes arranges the output dict in the expected way.

            If no namespaces are specified, volumes are generated.
        """
        generator = OCPGenerator(self.two_hours_ago, self.now, {})

        # gen_volumes depends on the output formatting of gen_namespaces and gen_pods.
        out_volumes = generator._gen_volumes(generator.namespaces, generator.namespace2pods)

        # these magic numbers are the random ranges defined in the OCP generator.
        self.assertGreaterEqual(len(out_volumes), 2 * 2 * 1)
        self.assertLessEqual(len(out_volumes), 6 * 12 * 3)

        expected = ["namespace", "volume", "storage_class", "volume_request", "labels", "volume_claims"]
        for vol in out_volumes.values():
            with self.subTest(volume=vol):
                self.assertEqual(list(vol.keys()), expected)

    def test_gen_volumes_usage_lt_capacity(self):
        """Test that gen_volumes generates requests and usage values which don't exceed capacity."""
        for attributes in [self.attributes, {}]:
            with self.subTest(attributes=attributes):
                generator = OCPGenerator(self.two_hours_ago, self.now, attributes)
                # gen_volumes depends on the output formatting of gen_namespaces and gen_pods.
                out_volumes = generator._gen_volumes(generator.namespaces, generator.namespace2pods)
                for volume in out_volumes.values():
                    with self.subTest(volume=volume):
                        total_capacity = 0
                        for claim in volume.get("volume_claims").values():
                            with self.subTest(claim=claim):
                                capacity = claim.get("capacity")
                                total_capacity += capacity

                                if attributes:
                                    for value in claim.get("volume_claim_usage_gig").values():
                                        self.assertLessEqual(value * GIGABYTE, capacity)
                        self.assertLessEqual(total_capacity, volume.get("volume_request_gig", 80.0 * GIGABYTE))

    def test_generate_hourly_data(self):
        """Test that generate_hourly_data calls the test method."""
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)
        test_method1 = Mock(return_value=True)
        test_method2 = Mock(return_value=True)
        with patch.dict(
            generator.ocp_report_generation,
            {"test_report": {"_generate_hourly_data": test_method1, "_update_data": test_method2}},
        ):
            kwargs = {"report_type": "test_report"}
            generator._generate_hourly_data(**kwargs)
            test_method1.assert_called_with(**kwargs)
            test_method2.assert_not_called()

    def test_get_usage_for_date(self):
        """Test that get_usage_for_date returns selected data."""
        test_usage = self._usage_dict()
        start_date = random.choice(list(test_usage.keys()))
        output = OCPGenerator._get_usage_for_date(test_usage, datetime.strptime(start_date, "%m-%d-%Y"))
        self.assertEqual(output, test_usage.get(start_date))

    def test_init_data_row(self):
        """Test that init_data_row initializes a row of data."""
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)

        for report_type, columns in [
            (OCP_POD_USAGE, OCP_POD_USAGE_COLUMNS),
            (OCP_NODE_LABEL, OCP_NODE_LABEL_COLUMNS),
            (OCP_STORAGE_USAGE, OCP_STORAGE_COLUMNS),
        ]:
            with self.subTest(report_type=report_type):
                row = generator._init_data_row(self.two_hours_ago, self.now, report_type=report_type)
                self.assertIsInstance(row, dict)
                self.assertEqual(list(row.keys()), list(columns))

    def test_update_data(self):
        """Test that update_data calls the expected update method."""
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)
        test_method1 = Mock(return_value=True)
        test_method2 = Mock(return_value=True)
        with patch.dict(
            generator.ocp_report_generation,
            {"test_report": {"_generate_hourly_data": test_method1, "_update_data": test_method2}},
        ):
            kwargs = {"report_type": "test_report"}
            generator._update_data({}, self.two_hours_ago, self.now, **kwargs)
            test_method2.assert_called_with(
                {
                    "interval_start": self.two_hours_ago.strftime("%Y-%m-%d %H:%M:%S +0000 UTC"),
                    "interval_end": self.now.strftime("%Y-%m-%d %H:%M:%S +0000 UTC"),
                },
                self.two_hours_ago,
                self.now,
                **kwargs,
            )
            test_method1.assert_not_called()

    def test_update_node_label_data(self):
        """Test that _update_node_label_data updates label data"""
        node = self.attributes.get("nodes")[0]
        kwargs = {"node": node.get("node"), "node_labels": node.get("node_labels")}

        generator = OCPGenerator(self.two_hours_ago, self.now, {})
        in_row = generator._init_data_row(self.two_hours_ago, self.now, report_type=OCP_NODE_LABEL)
        out_row = generator._update_node_label_data(copy(in_row), self.two_hours_ago, self.now, **kwargs)

        self.assertEqual(out_row.get("node"), node.get("node"))
        self.assertNotEqual(out_row.get("node"), in_row.get("node"))
        self.assertEqual(out_row.get("node_labels"), node.get("node_labels"))
        self.assertNotEqual(out_row.get("node_labels"), in_row.get("node_labels"))

    def test_update_pod_data(self):
        """Test that _update_pod_data updates pod data"""
        pods = next(iter(self.attributes.get("nodes")[0].get("namespaces").values())).get("pods")
        kwargs = {
            "cpu_usage": self._usage_dict(),
            "mem_usage_gig": self._usage_dict(),
            "pod_seconds": 86400,
            "pod": pods[0],
        }
        changed = {
            "pod_usage_cpu_core_seconds",
            "pod_request_cpu_core_seconds",
            "pod_limit_cpu_core_seconds",
            "pod_usage_memory_byte_seconds",
            "pod_request_memory_byte_seconds",
            "pod_limit_memory_byte_seconds",
        }

        generator = OCPGenerator(self.two_hours_ago, self.now, {})
        in_row = generator._init_data_row(self.two_hours_ago, self.now, report_type=OCP_POD_USAGE)
        out_row = generator._update_pod_data(copy(in_row), self.two_hours_ago, self.now, **kwargs)

        for key in changed:
            with self.subTest(key=key):
                self.assertEqual(out_row.get(key), pods[0].get(key))
                self.assertNotEqual(out_row.get(key), in_row.get(key))

        for key in list(set(out_row.keys()) - changed):
            with self.subTest(key=key):
                self.assertIn(out_row.get(key), [pods[0].get(key), in_row.get(key)])

    def test_update_pod_data_usage_lt_request(self):
        """Test that _update_pod_data keeps usage <= limit <= request."""
        pods = next(iter(self.attributes.get("nodes")[0].get("namespaces").values())).get("pods")
        kwargs = {
            "cpu_usage": self._usage_dict(),
            "mem_usage_gig": self._usage_dict(),
            "pod_seconds": 86400,
            "pod": pods[0],
        }

        generator = OCPGenerator(self.two_hours_ago, self.now, {})
        in_row = generator._init_data_row(self.two_hours_ago, self.now, report_type=OCP_POD_USAGE)
        out_row = generator._update_pod_data(copy(in_row), self.two_hours_ago, self.now, **kwargs)

        for x in ["cpu_core", "memory_byte"]:
            with self.subTest(row=out_row):
                with self.subTest(x=x):
                    self.assertLessEqual(
                        out_row.get(f"pod_usage_{x}_seconds"), out_row.get(f"pod_request_{x}_seconds")
                    )
                    self.assertLessEqual(out_row.get(f"pod_usage_{x}_seconds"), out_row.get(f"pod_limit_{x}_seconds"))
                    self.assertLessEqual(
                        out_row.get(f"pod_limit_{x}_seconds"), out_row.get(f"pod_request_{x}_seconds")
                    )

    def test_update_storage_data(self):
        """Test that _update_storage_data updates storage data."""
        kwargs = {
            "volume_claim_usage_gig": self._usage_dict(),
            "vc_capacity": self.fake.pyint(1, 100),
            "namespace": self.fake.word(),
            "pod": self.fake.word(),
            "volume_claim": self.fake.uuid4(),
            "volume_name": self.fake.word(),
            "storage_class": self.fake.word(),
            "volume_request": self.fake.pyint(1, 100),
            "volume_labels": (
                f"label_{self.fake.word()}:{self.fake.word()}",
                f"|label_{self.fake.word()}:{self.fake.word()}",
            ),
            "volume_claim_labels": (
                f"label_{self.fake.word()}:{self.fake.word()}",
                f"|label_{self.fake.word()}:{self.fake.word()}",
            ),
        }
        changed = {
            "namespace",
            "pod",
            "persistentvolumeclaim",
            "persistentvolume",
            "storageclass",
            "persistentvolumeclaim_capacity_bytes",
            "persistentvolumeclaim_capacity_byte_seconds",
            "volume_request_storage_byte_seconds",
            "persistentvolume_labels",
            "persistentvolumeclaim_labels",
            "persistentvolumeclaim_usage_byte_seconds",
        }

        generator = OCPGenerator(self.two_hours_ago, self.now, {})
        in_row = generator._init_data_row(self.two_hours_ago, self.now, report_type=OCP_STORAGE_USAGE)
        out_row = generator._update_storage_data(copy(in_row), self.two_hours_ago, self.now, **kwargs)

        for key in changed:
            with self.subTest(key=key):
                if key in kwargs:
                    self.assertEqual(out_row.get(key), kwargs.get(key))
                self.assertNotEqual(out_row.get(key), in_row.get(key))

        for key in list(set(out_row.keys()) - changed):
            with self.subTest(key=key):
                self.assertIn(out_row.get(key), [kwargs.get(key), in_row.get(key)])

    def test_update_storage_data_usage_lt_request(self):
        """Test that _update_storge_data keeps usage <= capacity <= request."""
        kwargs = {
            "volume_claim_usage_gig": self._usage_dict(),
            "vc_capacity": self.fake.pyint(1, 100),
            "namespace": self.fake.word(),
            "pod": self.fake.word(),
            "volume_claim": self.fake.uuid4(),
            "volume_name": self.fake.word(),
            "storage_class": self.fake.word(),
            "volume_request": self.fake.pyint(1, 100),
            "volume_labels": (
                f"label_{self.fake.word()}:{self.fake.word()}",
                f"|label_{self.fake.word()}:{self.fake.word()}",
            ),
            "volume_claim_labels": (
                f"label_{self.fake.word()}:{self.fake.word()}",
                f"|label_{self.fake.word()}:{self.fake.word()}",
            ),
        }

        generator = OCPGenerator(self.two_hours_ago, self.now, {})
        in_row = generator._init_data_row(self.two_hours_ago, self.now, report_type=OCP_STORAGE_USAGE)
        out_row = generator._update_storage_data(copy(in_row), self.two_hours_ago, self.now, **kwargs)

        self.assertLessEqual(
            out_row.get("persistentvolumeclaim_usage_byte_seconds"),
            out_row.get("persistentvolumeclaim_capacity_byte_seconds") * GIGABYTE,
        )
        self.assertLessEqual(
            out_row.get("persistentvolumeclaim_capacity_byte_seconds"),
            out_row.get("volume_request_storage_byte_seconds"),
        )

    def test_generate_data(self):
        """Test that generate_data calls the test method."""
        generator = OCPGenerator(self.two_hours_ago, self.now, self.attributes)
        with patch.object(generator, "_generate_hourly_data") as mock_method:
            kwargs = {"report_type": "test_report"}
            generator.generate_data(**kwargs)
            mock_method.assert_called_with(**kwargs)

    def test_timestamp_valid(self):
        """Test that timestamp returns a string with a valid input."""
        self.assertIsInstance(OCPGenerator.timestamp(self.now), str)

    def test_timestamp_invalid(self):
        """Test that timestamp raises a ValueError with invalid input."""
        with self.assertRaises(ValueError):
            OCPGenerator.timestamp(self.fake.word())
