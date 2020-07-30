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
import os
import random
import tempfile
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


class OCPGeneratorTestCase(TestCase):
    """TestCase class for OCP Generator."""

    def setUp(self):
        """Test setup."""
        self.fake = Faker()
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.one_day = timedelta(hours=24)
        self.two_hours_ago = self.now - (2 * self.one_hour)

        namespace = f"namespace_{self.fake.word()}"
        self.attributes = {
            "nodes": [
                {
                    "node": self.fake.uuid4(),
                    "node_name": self.fake.word(),
                    "labels": (
                        f"label_{self.fake.word()}:{self.fake.word()}",
                        f"|label_{self.fake.word()}:{self.fake.word()}",
                    ),
                    "cpu_cores": self.fake.pyint(1, 10),
                    "memory_gig": self.fake.pyint(1, 32),
                    "resource_id": "i-" + self.fake.ean8(),
                    "namespaces": [
                        {
                            "namespace_name": namespace,
                            "pods": [
                                {
                                    "pod": self.fake.uuid4(),
                                    "pod_name": f"pod_{self.fake.word()}",
                                    "namespace": namespace,
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
                                    "namespace": namespace,
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
                                    "namespace": namespace,
                                    "volume_claims": [
                                        {
                                            "volume_claim_name": f"volumeclaim_{self.fake.word()}",
                                            "pod_name": f"pod_{self.fake.word()}",
                                            "namespace": namespace,
                                            "capacity_gig": self.fake.pyint(1, 100),
                                            "volume_claim_usage_gig": self._usage_dict(),
                                            "labels": (
                                                f"label_{self.fake.word()}:{self.fake.word()}",
                                                f"|label_{self.fake.word()}:{self.fake.word()}",
                                            ),
                                        }
                                    ],
                                    "storage_class": random.choice(("gp2", "fast", "slow", "gold")),
                                    "labels": (
                                        f"label_{self.fake.word()}:{self.fake.word()}",
                                        f"|label_{self.fake.word()}:{self.fake.word()}",
                                    ),
                                }
                            ],
                        }
                    ],
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
        """Test the init generates at least one node."""
        generator = OCPGenerator(self.two_hours_ago, self.now)
        self.assertIsNotNone(generator.nodes)
        self.assertIsInstance(generator.nodes, list)
        self.assertGreaterEqual(len(generator.nodes), 1)

    def test_init_with_attributes(self):
        """Test the init with attributes generates a node with the provided name."""
        in_yaml = """
---
generators:
  - OCPGenerator:
      start_date: 1970-01-01
      end_date: 1970-02-01
      nodes:
        - node_name: test_node
          namespaces:
            - namespace_name: test_namespace
              pods:
                - pod_name: test_pod
              volumes:
                - volume_name: test_volume
                  volume_claims:
                  - volume_claim_name: test_claim
"""

        _, tmp_filename = tempfile.mkstemp()
        with open(tmp_filename, "w+") as tmp_handle:
            tmp_handle.write(in_yaml)

        generator = OCPGenerator(self.two_hours_ago, self.now, user_config=tmp_filename)
        self.assertIsNotNone(generator.nodes)
        self.assertIsInstance(generator.nodes, list)
        self.assertGreaterEqual(len(generator.nodes), 1)
        self.assertEqual(generator.nodes[0].get("node_name"), "test_node")

        os.remove(tmp_filename)

    def test_add_common_usage_info(self):
        """Test that add_common_usage_info updates usage timestamps."""
        generator = OCPGenerator(self.two_hours_ago, self.now, {})
        test_row = {}
        output_row = generator._add_common_usage_info(test_row, self.two_hours_ago, self.now)
        self.assertIn("interval_start", output_row)
        self.assertIn("interval_end", output_row)

    def test_gen_hourly_node_label_usage(self):
        """Test that gen_hourly_node_label_usage generates rows."""
        generator = OCPGenerator(self.two_hours_ago, self.now)
        generator.nodes = self.attributes.get("nodes")

        namespaces = self.attributes.get("nodes")[0].get("namespaces")
        for dikt in namespaces:
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
        generator = OCPGenerator(self.two_hours_ago, self.now)
        generator.nodes = self.attributes.get("nodes")

        namespaces = self.attributes.get("nodes")[0].get("namespaces")
        for dikt in namespaces:
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
        generator = OCPGenerator(self.two_hours_ago, self.now)
        generator.nodes = self.attributes.get("nodes")

        namespaces = self.attributes.get("nodes")[0].get("namespaces")
        for dikt in namespaces:
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

    def test_gen_namespaces_without_namespace(self):
        """Test that gen_namespaces arranges the output dict in the expected way.

            If no namespaces are specified, namespaces are generated.
        """
        in_nodes = self.attributes.get("nodes")
        generator = OCPGenerator(self.two_hours_ago, self.now)
        out_namespaces = generator._gen_namespaces(in_nodes[0])

        # auto-generating namespaces should create at least 2 namespaces
        self.assertGreaterEqual(len(out_namespaces), 1)

    def test_gen_nodes_with_nodes(self):
        """Test that gen_nodes arranges the output dict in the expected way.

            If nodes are specified, the specified data is overlayed onto the generated data.
        """
        in_yaml = """
---
generators:
  - OCPGenerator:
      start_date: 1970-01-01
      end_date: 1970-02-01
      nodes:
        - node_name: test_node
          namespaces:
            - namespace_name: test_namespace
              pods:
                - pod_name: test_pod
              volumes:
                - volume_name: test_volume
                  volume_claims:
                  - volume_claim_name: test_claim
"""

        _, tmp_filename = tempfile.mkstemp()
        with open(tmp_filename, "w+") as tmp_handle:
            tmp_handle.write(in_yaml)

        generator = OCPGenerator(self.two_hours_ago, self.now, user_config=tmp_filename)
        self.assertGreaterEqual(len(generator.nodes), 2)
        self.assertEqual(generator.nodes[0].get("node_name"), "test_node")
        self.assertEqual(generator.nodes[0].get("namespaces")[0].get("namespace_name"), "test_namespace")
        self.assertEqual(generator.nodes[0].get("namespaces")[0].get("pods")[0].get("pod_name"), "test_pod")
        self.assertEqual(generator.nodes[0].get("namespaces")[0].get("volumes")[0].get("volume_name"), "test_volume")
        self.assertEqual(
            generator.nodes[0].get("namespaces")[0].get("volumes")[0].get("volume_claims")[0].get("volume_claim_name"),
            "test_claim",
        )
        expected_keys = ["node_name", "cpu_cores", "memory_gig", "resource_id", "labels", "namespaces"]
        self.assertEqual(list(generator.nodes[0].keys()), expected_keys)

        os.remove(tmp_filename)

    def test_gen_nodes_without_nodes(self):
        """Test that gen_nodes arranges the output dict in the expected way.

            If nodes are not specified, nodes are generated.
        """
        generator = OCPGenerator(self.two_hours_ago, self.now)  # _gen_nodes is called by the constructor.
        self.assertGreaterEqual(len(list(generator.nodes)), 2)
        self.assertLessEqual(len(list(generator.nodes)), 6)
        expected_keys = ["node_name", "cpu_cores", "memory_gig", "resource_id", "labels", "namespaces"]
        self.assertEqual(list(generator.nodes[0].keys()), expected_keys)

    def test_gen_openshift_labels(self):
        """Test that gen_openshift_labels creates well-formatted labels."""
        generator = OCPGenerator(self.two_hours_ago, self.now)
        out_labels = generator._gen_openshift_labels()
        matcher = r"(\w+:\w+)(\|(\w+:\w+))*"
        self.assertRegex(out_labels, matcher)

    def test_gen_pods_with_namespaces(self):
        """Test that gen_pods arranges the output dict in the expected way.

            If namespaces with pods are specified, defined pods are used.
        """
        generator = OCPGenerator(self.two_hours_ago, self.now)
        in_node = self.attributes.get("nodes")[0]
        in_namespace = self.attributes.get("nodes")[0].get("namespaces")[0].get("namespace_name")
        out_pods = generator._gen_pods(in_node, in_namespace)
        self.assertGreaterEqual(len(out_pods), 1)

        expected = (
            "namespace",
            "node",
            "resource_id",
            "pod_name",
            "node_capacity_cpu_cores",
            "node_capacity_cpu_core_seconds",
            "node_capacity_memory_bytes",
            "node_capacity_memory_byte_seconds",
            "cpu_request",
            "cpu_limit",
            "mem_request_gig",
            "mem_limit_gig",
            "labels",
            "cpu_usage",
            "mem_usage_gig",
            "pod_seconds",
        )
        for pod in out_pods:
            with self.subTest(podkeys=pod.keys()):
                for key in pod.keys():
                    with self.subTest(key=key):
                        self.assertIn(key, expected)
            self.assertEqual(pod.get("node"), in_node.get("node_name"))
            self.assertEqual(pod.get("namespace"), in_namespace)

    def test_gen_pods_without_namespaces(self):
        """Test that gen_pods arranges the output dict in the expected way.

            If no namespaces are specified, pods are generated.
        """
        generator = OCPGenerator(self.two_hours_ago, self.now)
        out_pods = [
            pod for node in generator.nodes for namespace in node.get("namespaces") for pod in namespace.get("pods")
        ]

        # these magic numbers are the random ranges defined in the OCP generator.
        self.assertGreaterEqual(len(out_pods), 2 * 2 * 2)
        self.assertLessEqual(len(out_pods), 6 * 12 * 20)

        expected = (
            "namespace",
            "node",
            "resource_id",
            "pod_name",
            "node_capacity_cpu_cores",
            "node_capacity_cpu_core_seconds",
            "node_capacity_memory_bytes",
            "node_capacity_memory_byte_seconds",
            "cpu_request",
            "cpu_limit",
            "mem_request_gig",
            "mem_limit_gig",
            "labels",
            "cpu_usage",
            "mem_usage_gig",
            "pod_seconds",
        )
        for pod in out_pods:
            with self.subTest(podkeys=pod.keys()):
                for key in pod.keys():
                    with self.subTest(key=key):
                        self.assertIn(key, expected)

    def test_gen_pods_usage_lt_capacity(self):
        """Test that gen_pods generates requests and usage values which don't exceed capacity."""
        generator = OCPGenerator(self.two_hours_ago, self.now)
        for node in generator.nodes:
            with self.subTest(node=node):
                for namespace in node.get("namespaces"):
                    with self.subTest(namespace=namespace.get("namespace_name")):
                        for pod in namespace.get("pods"):
                            with self.subTest(pod=pod.get("pod_name")):
                                self.assertLessEqual(pod.get("cpu_limit"), pod.get("node_capacity_cpu_cores"))
                                self.assertLessEqual(pod.get("cpu_request"), pod.get("node_capacity_cpu_cores"))
                                self.assertLessEqual(pod.get("mem_limit_gig"), pod.get("node_capacity_memory_bytes"))
                                self.assertLessEqual(pod.get("mem_request_gig"), pod.get("node_capacity_memory_bytes"))
                                for value in pod.get("cpu_usage").values():
                                    self.assertLessEqual(value, pod.get("node_capacity_cpu_cores"))
                                for value in pod.get("mem_usage_gig").values():
                                    self.assertLessEqual(value, pod.get("node_capacity_memory_bytes"))

    def test_gen_volumes_with_namespaces(self):
        """Test that gen_volumes arranges the output dict in the expected way.

            If namespaces with volumes are specified, defined volumes are used.
        """
        generator = OCPGenerator(self.two_hours_ago, self.now)

        namespaces = self.attributes.get("nodes")[0].get("namespaces")
        in_pods = namespaces[0].get("pods")

        out_volumes = generator._gen_volumes(in_pods)

        expected = ["namespace", "volume_name", "storage_class", "volume_request_gig", "labels", "volume_claims"]
        for vol in out_volumes:
            with self.subTest(volume=vol):
                self.assertEqual(list(vol.keys()), expected)
            self.assertEqual(vol.get("namespace"), namespaces[0].get("namespace_name"))

    def test_gen_volumes_without_namespaces(self):
        """Test that gen_volumes arranges the output dict in the expected way.

            If no namespaces are specified, volumes are generated.
        """
        generator = OCPGenerator(self.two_hours_ago, self.now)

        out_volumes = generator.nodes[0].get("namespaces")[0].get("volumes")

        # these magic numbers are the random ranges defined in the OCP generator.
        self.assertGreaterEqual(len(out_volumes), 2)
        self.assertLessEqual(len(out_volumes), 6)

        expected = ["volume_name", "namespace", "storage_class", "volume_request_gig", "labels", "volume_claims"]
        for vol in out_volumes:
            with self.subTest(volume=vol):
                self.assertEqual(list(vol.keys()), expected)

    def test_gen_volumes_usage_lt_capacity(self):
        """Test that gen_volumes generates requests and usage values which don't exceed capacity."""
        generator = OCPGenerator(self.two_hours_ago, self.now)
        for node in generator.nodes:
            with self.subTest(node=node):
                for namespace in node.get("namespaces"):
                    with self.subTest(namespace=namespace.get("namespace_name")):
                        for volume in namespace.get("volumes"):
                            with self.subTest(volume=volume.get("volume_name")):
                                total_capacity = 0
                                for claim in volume.get("volume_claims"):
                                    with self.subTest(claim=claim):
                                        capacity = claim.get("capacity_gig")
                                        total_capacity += capacity

                                        for value in claim.get("volume_claim_usage_gig").values():
                                            self.assertLessEqual(value, capacity)
                                self.assertLessEqual(total_capacity, volume.get("volume_request_gig"))

    def test_generate_hourly_data(self):
        """Test that generate_hourly_data calls the test method."""
        generator = OCPGenerator(self.two_hours_ago, self.now)
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
        generator = OCPGenerator(self.two_hours_ago, self.now)

        for report_type, columns in [
            (OCP_POD_USAGE, OCP_POD_USAGE_COLUMNS),
            (OCP_NODE_LABEL, OCP_NODE_LABEL_COLUMNS),
            (OCP_STORAGE_USAGE, OCP_STORAGE_COLUMNS),
        ]:
            with self.subTest(report_type=report_type):
                row = generator._init_data_row(self.two_hours_ago, self.now, report_type=report_type)
                self.assertIsInstance(row, dict)
                self.assertEqual(sorted(list(row.keys())), sorted(list(columns)))

    def test_update_data(self):
        """Test that update_data calls the expected update method."""
        generator = OCPGenerator(self.two_hours_ago, self.now)
        test_method1 = Mock(return_value=True)
        test_method2 = Mock(return_value=True)
        with patch.dict(
            generator.ocp_report_generation,
            {"test_report": {"_generate_hourly_data": test_method1, "_update_data": test_method2}},
        ):
            kwargs = {"report_type": "test_report"}
            generator._update_data({}, self.two_hours_ago, self.now, **kwargs)
            test_method2.assert_called_with({}, self.two_hours_ago, self.now, **kwargs)
            test_method1.assert_not_called()

    def test_update_node_label_data(self):
        """Test that _update_node_label_data updates label data"""
        node = self.attributes.get("nodes")[0]
        kwargs = {"node": node.get("node"), "node_labels": node.get("node_labels")}

        generator = OCPGenerator(self.two_hours_ago, self.now)
        in_row = generator._init_data_row(self.two_hours_ago, self.now, report_type=OCP_NODE_LABEL)
        out_row = generator._update_node_label_data(copy(in_row), self.two_hours_ago, self.now, **kwargs)

        self.assertEqual(out_row.get("node"), node.get("node"))
        self.assertNotEqual(out_row.get("node"), in_row.get("node"))
        self.assertEqual(out_row.get("node_labels"), node.get("node_labels"))
        self.assertNotEqual(out_row.get("node_labels"), in_row.get("node_labels"))

    def test_update_pod_data(self):
        """Test that _update_pod_data updates pod data"""
        pods = self.attributes.get("nodes")[0].get("namespaces")[0].get("pods")
        usage_dict = self._usage_dict()
        kwargs = {
            "report_type": "test_report",
            "cpu_usage": usage_dict,
            "mem_usage_gig": usage_dict,
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

        generator = OCPGenerator(self.two_hours_ago, self.now)
        generator.nodes = self.attributes
        in_row = generator._init_data_row(self.two_hours_ago, self.now, report_type=OCP_POD_USAGE)
        out_row = generator._update_pod_data(
            copy(in_row), datetime.strptime(random.choice(list(usage_dict.keys())), "%m-%d-%Y"), self.now, **kwargs
        )

        for key in changed:
            with self.subTest(key=key):
                self.assertIsNotNone(out_row.get(key))
                self.assertNotEqual(out_row.get(key), in_row.get(key))

        for key in list(set(out_row.keys()) - changed):
            with self.subTest(key=key):
                self.assertIsNotNone(out_row.get(key))

    def test_update_pod_data_usage_lt_request(self):
        """Test that _update_pod_data keeps usage <= limit <= request."""
        pods = self.attributes.get("nodes")[0].get("namespaces")[0].get("pods")
        kwargs = {
            "report_type": "test_report",
            "cpu_usage": self._usage_dict(),
            "mem_usage_gig": self._usage_dict(),
            "pod_seconds": 86400,
            "pod": pods[0],
        }

        generator = OCPGenerator(self.two_hours_ago, self.now)
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

        generator = OCPGenerator(self.two_hours_ago, self.now)
        in_row = generator._init_data_row(self.two_hours_ago, self.now, report_type=OCP_STORAGE_USAGE)
        out_row = generator._update_storage_data(copy(in_row), self.two_hours_ago, self.now, **kwargs)

        for key in changed:
            with self.subTest(key=key):
                if key in kwargs:
                    self.assertEqual(out_row.get(key), kwargs.get(key))
                self.assertNotEqual(out_row.get(key), in_row.get(key))

        for key in list(set(out_row.keys()) - changed):
            with self.subTest(key=key):
                self.assertIsNotNone(out_row.get(key))

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

        generator = OCPGenerator(self.two_hours_ago, self.now)
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
        generator = OCPGenerator(self.two_hours_ago, self.now)
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
