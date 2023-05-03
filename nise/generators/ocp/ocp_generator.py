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
from copy import deepcopy
from random import choice
from random import choices
from random import randint
from random import uniform
from string import ascii_lowercase

from dateutil import parser
from nise.generators.generator import AbstractGenerator
from nise.generators.generator import REPORT_TYPE

GIGABYTE = 1024 * 1024 * 1024
HOUR = 60 * 60

OCP_POD_USAGE = "ocp_pod_usage"
OCP_STORAGE_USAGE = "ocp_storage_usage"
OCP_NODE_LABEL = "ocp_node_label"
OCP_NAMESPACE_LABEL = "ocp_namespace_label"
OCP_ROS_USAGE = "ocp_ros_usage"
OCP_POD_USAGE_COLUMNS = (
    "report_period_start",
    "report_period_end",
    "pod",
    "namespace",
    "node",
    "resource_id",
    "interval_start",
    "interval_end",
    "pod_usage_cpu_core_seconds",
    "pod_request_cpu_core_seconds",
    "pod_limit_cpu_core_seconds",
    "pod_usage_memory_byte_seconds",
    "pod_request_memory_byte_seconds",
    "pod_limit_memory_byte_seconds",
    "node_capacity_cpu_cores",
    "node_capacity_cpu_core_seconds",
    "node_capacity_memory_bytes",
    "node_capacity_memory_byte_seconds",
    "pod_labels",
)
OCP_STORAGE_COLUMNS = (
    "report_period_start",
    "report_period_end",
    "interval_start",
    "interval_end",
    "namespace",
    "pod",
    "persistentvolumeclaim",
    "persistentvolume",
    "storageclass",
    "persistentvolumeclaim_capacity_bytes",
    "persistentvolumeclaim_capacity_byte_seconds",
    "volume_request_storage_byte_seconds",
    "persistentvolumeclaim_usage_byte_seconds",
    "persistentvolume_labels",
    "persistentvolumeclaim_labels",
)
OCP_NODE_LABEL_COLUMNS = (
    "report_period_start",
    "report_period_end",
    "interval_start",
    "interval_end",
    "node",
    "node_labels",
)
OCP_NAMESPACE_LABEL_COLUMNS = (
    "report_period_start",
    "report_period_end",
    "interval_start",
    "interval_end",
    "namespace",
    "namespace_labels",
)
OCP_ROS_USAGE_COLUMN = (
    "interval_start",
    "interval_end",
    "report_period_start",
    "report_period_end",
    "namespace",
    "node",
    "resource_id",
    "pod",
    "container_name",
    "owner_name",
    "owner_kind",
    "workload",
    "workload_type",
    "image_name",
    "cpu_request_container_avg",
    "cpu_request_container_sum",
    "cpu_limit_container_avg",
    "cpu_limit_container_sum",
    "cpu_usage_container_avg",
    "cpu_usage_container_min",
    "cpu_usage_container_max",
    "cpu_usage_container_sum",
    "cpu_throttle_container_avg",
    "cpu_throttle_container_max",
    "cpu_throttle_container_sum",
    "memory_request_container_avg",
    "memory_request_container_sum",
    "memory_limit_container_avg",
    "memory_limit_container_sum",
    "memory_usage_container_avg",
    "memory_usage_container_min",
    "memory_usage_container_max",
    "memory_usage_container_sum",
    "memory_rss_usage_container_avg",
    "memory_rss_usage_container_min",
    "memory_rss_usage_container_max",
    "memory_rss_usage_container_sum",
)
OCP_REPORT_TYPE_TO_COLS = {
    OCP_POD_USAGE: OCP_POD_USAGE_COLUMNS,
    OCP_STORAGE_USAGE: OCP_STORAGE_COLUMNS,
    OCP_NODE_LABEL: OCP_NODE_LABEL_COLUMNS,
    OCP_NAMESPACE_LABEL: OCP_NAMESPACE_LABEL_COLUMNS,
    OCP_ROS_USAGE: OCP_ROS_USAGE_COLUMN,
}

OCP_OWNER_WORKLOAD_CHOICES = {
    # "pod": ("<none>", "<none>", None, None),  # manually created Pod - recommendation won't be generated
    "deployment": (None, "ReplicaSet", None, "deployment"),
    "replicaset": (None, "ReplicaSet", "<none>", "deployment"),  # manually created ReplicaSet
    "replicationcontroller": (
        None,
        "ReplicationController",
        "<none>",
        "deploymentconfig",
    ),  # manually created ReplicationController
    "deploymentconfig": (None, "ReplicationController", None, "deploymentconfig"),
    "statefulset": (None, "StatefulSet", None, "statefulset"),
    "daemonset": (None, "DaemonSet", None, "daemonset"),
    # "job": (None, "Job", None, "job"), # not supported by Kruize
}


def get_owner_workload(pod, workload=None):
    if not workload:
        workload = choice(list(OCP_OWNER_WORKLOAD_CHOICES.keys()))
    on, ok, wl, wt = OCP_OWNER_WORKLOAD_CHOICES.get(
        workload.lower(), choice(list(OCP_OWNER_WORKLOAD_CHOICES.values()))
    )
    if on == "<none>" and wl == "<none>":  # manually created Pod
        return on, ok, wl, wt
    elif wl == "<none>":  # manually created ReplicaSet or ReplicationController
        return pod, ok, wl, wt
    return pod, ok, pod, wt


def generate_randomized_ros_usage(usage_dict, limit_value):
    # if usage value is provided in yaml -> avg_value = +- 5% of that specified usage value
    if usage_value := usage_dict.get("full_period"):
        avg_value = min(round(uniform(usage_value * 0.95, usage_value * 1.05), 5), limit_value)
    # if usage value is not specified in yaml -> random avg_usage from 10% to 100% of the limit
    else:
        avg_value = round(uniform(limit_value * 0.1, limit_value), 5)

    # min value - random float derived from avg_value,
    min_value = round(uniform(avg_value * 0.8, avg_value), 5)
    # max_value - random float derived from avg_value, but max of limit_value
    max_value = min(round(uniform(avg_value, avg_value * 1.2), 5), limit_value)

    return avg_value, min_value, max_value


class OCPGenerator(AbstractGenerator):
    """Defines a abstract class for generators."""

    def __init__(self, start_date, end_date, attributes, ros_ocp_info=False):
        """Initialize the generator."""
        self._nodes = None
        self.ros_ocp_info = ros_ocp_info
        if attributes:
            self._nodes = attributes.get("nodes")

        super().__init__(start_date, end_date)
        self.apps = [
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
        ]
        self.organizations = [self.fake.word(), self.fake.word(), self.fake.word(), self.fake.word()]
        self.markets = [
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
        ]
        self.versions = [
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
        ]
        self.nodes = self._gen_nodes()
        self.namespaces = self._gen_namespaces(self.nodes)
        self.pods, self.namespace2pods, self.ros_data = self._gen_pods(self.namespaces)

        self.volumes = self._gen_volumes(self.namespaces, self.namespace2pods)

        self.ocp_report_generation = {
            OCP_POD_USAGE: {
                "_generate_hourly_data": self._gen_hourly_pods_usage,
                "_update_data": self._update_pod_data,
            },
            OCP_STORAGE_USAGE: {
                "_generate_hourly_data": self._gen_hourly_storage_usage,
                "_update_data": self._update_storage_data,
            },
            OCP_NODE_LABEL: {
                "_generate_hourly_data": self._gen_hourly_node_label_usage,
                "_update_data": self._update_node_label_data,
            },
            OCP_NAMESPACE_LABEL: {
                "_generate_hourly_data": self._gen_hourly_namespace_label_usage,
                "_update_data": self._update_namespace_label_data,
            },
        }

        if self.ros_ocp_info:
            self.ocp_report_generation.update(
                {
                    OCP_ROS_USAGE: {
                        "_generate_hourly_data": self._gen_quarter_hourly_ros_ocp_pods_usage,
                        "_update_data": self._update_ros_ocp_pod_data,
                    }
                }
            )

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not (in_date and isinstance(in_date, datetime.datetime)):
            raise ValueError("in_date must be a date object.")
        return in_date.strftime("%Y-%m-%d %H:%M:%S +0000 UTC")

    def _gen_nodes(self):
        """Create nodes for report."""
        nodes = []
        if self._nodes:
            for item in self._nodes:
                memory_gig = item.get("memory_gig", randint(2, 8))
                memory_bytes = memory_gig * GIGABYTE
                resource_id = str(item.get("resource_id", self.fake.word()))
                node = {
                    "name": item.get("node_name", "node_" + self.fake.word()),
                    "cpu_cores": item.get("cpu_cores", randint(2, 16)),
                    "memory_bytes": memory_bytes,
                    "resource_id": "i-" + resource_id,
                    "namespaces": item.get("namespaces"),
                    "node_labels": item.get("node_labels"),
                }
                nodes.append(node)
        else:
            num_nodes = randint(2, 6)
            seeded_labels = {"node-role.kubernetes.io/master": [""], "node-role.kubernetes.io/infra": [""]}
            for _ in range(num_nodes):
                memory_gig = randint(2, 8)
                memory_bytes = memory_gig * GIGABYTE
                node = {
                    "name": "node_" + self.fake.word(),
                    "cpu_cores": randint(2, 16),
                    "memory_bytes": memory_bytes,
                    "resource_id": "i-" + self.fake.word(),
                    "node_labels": self._gen_openshift_labels(seeding=seeded_labels),
                }
                nodes.append(node)
        return nodes

    def _gen_namespaces(self, nodes):
        """Create namespaces on specific nodes and keep relationship."""
        namespaces = {}
        for node in nodes:
            if node.get("namespaces"):
                for name, _ in node.get("namespaces").items():
                    namespace = name
                    namespaces[namespace] = node
            else:
                num_namespaces = randint(2, 12)
                for _ in range(num_namespaces):
                    namespace_suffix = choice(("ci", "qa", "prod", "proj", "dev", "staging"))
                    namespace = self.fake.word() + "_" + namespace_suffix
                    namespaces[namespace] = node
        return namespaces

    def _gen_openshift_labels(self, seeding=None):
        """Create pod labels for output data."""
        seeded_labels = {
            "environment": ["dev", "ci", "qa", "stage", "prod"],
            "app": self.apps,
            "organization": self.organizations,
            "market": self.markets,
            "version": self.versions,
        }
        if seeding:
            seeded_labels = seeding
        gen_label_keys = [
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
            self.fake.word(),
        ]
        all_label_keys = list(seeded_labels.keys()) + gen_label_keys
        num_labels = randint(2, len(all_label_keys))
        chosen_label_keys = choices(all_label_keys, k=num_labels)

        labels = {}
        for label_key in chosen_label_keys:
            label_value = self.fake.word()
            if label_key in seeded_labels:
                label_value = choice(seeded_labels[label_key])
            labels[f"label_{label_key}"] = label_value

        label_str = ""
        for key, value in labels.items():
            label_data = f"{key}:{value}"
            label_str += f"|{label_data}" if label_str else label_data
        return label_str

    def _gen_pods(self, namespaces):
        """Create pods on specific namespaces and keep relationship."""
        pods = {}
        ros_ocp_data_pods = {}
        namespace2pod = {}
        for namespace, node in namespaces.items():
            namespace2pod[namespace] = []
            if node.get("namespaces"):
                specified_pods = node.get("namespaces").get(namespace).get("pods")
                for specified_pod in specified_pods:
                    pod = specified_pod.get("pod_name", self.fake.word())
                    namespace2pod[namespace].append(pod)
                    cpu_cores = node.get("cpu_cores")
                    memory_bytes = node.get("memory_bytes")

                    cpu_limit = min(specified_pod.get("cpu_limit", cpu_cores), cpu_cores)
                    cpu_request = min(specified_pod.get("cpu_request", round(uniform(0.02, cpu_limit), 5)), cpu_limit)
                    cpu_usage = specified_pod.get("cpu_usage", {})
                    for key, value in cpu_usage.items():
                        if value > cpu_limit:
                            cpu_usage[key] = cpu_limit

                    memory_gig = memory_bytes / GIGABYTE
                    mem_limit_gig = min(specified_pod.get("mem_limit_gig", memory_gig), memory_gig)
                    mem_request_gig = min(
                        specified_pod.get("mem_request_gig", round(uniform(25.0, 80.0), 2)), mem_limit_gig
                    )
                    memory_usage_gig = specified_pod.get("mem_usage_gig", {})
                    for key, value in memory_usage_gig.items():
                        if value > mem_limit_gig:
                            memory_usage_gig[key] = mem_limit_gig

                    pods[pod] = {
                        "namespace": namespace,
                        "node": node.get("name"),
                        "resource_id": node.get("resource_id"),
                        "pod": pod,
                        "node_capacity_cpu_cores": cpu_cores,
                        "node_capacity_cpu_core_seconds": cpu_cores * HOUR,
                        "node_capacity_memory_bytes": memory_bytes,
                        "node_capacity_memory_byte_seconds": memory_bytes * HOUR,
                        "cpu_request": cpu_request,
                        "cpu_limit": cpu_limit,
                        "mem_request_gig": mem_request_gig,
                        "mem_limit_gig": mem_limit_gig,
                        "pod_labels": specified_pod.get("labels", None),
                        "cpu_usage": cpu_usage,
                        "mem_usage_gig": memory_usage_gig,
                        "pod_seconds": specified_pod.get("pod_seconds"),
                    }
                    owner_name, owner_kind, workload, workload_type = get_owner_workload(
                        pod, specified_pod.get("workload")
                    )

                    cpu_usage_avg, cpu_usage_min, cpu_usage_max = generate_randomized_ros_usage(cpu_usage, cpu_limit)
                    memory_usage_gig_avg, memory_usage_gig_min, memory_usage_gig_max = generate_randomized_ros_usage(
                        memory_usage_gig, mem_limit_gig
                    )
                    memory_rss_ratio = 1 / round(uniform(1.01, 1.9), 2)
                    cpu_throttle = choices([0, round(cpu_usage_avg / randint(10, 20), 5)], weights=(3, 1))[0]

                    ros_ocp_data_pods[pod] = {
                        "namespace": namespace,
                        "node": node.get("name"),
                        "resource_id": node.get("resource_id"),
                        "pod": pod,
                        "container_name": pod,
                        "owner_name": owner_name,
                        "owner_kind": owner_kind,
                        "workload": workload,
                        "workload_type": workload_type,
                        "image_name": self.fake.word() + "-" + self.fake.word(),
                        "cpu_request_container_avg": cpu_request,
                        "cpu_request_container_sum": cpu_request,
                        "cpu_limit_container_avg": cpu_limit,
                        "cpu_limit_container_sum": cpu_limit,
                        "cpu_usage_container_avg": cpu_usage_avg,
                        "cpu_usage_container_min": cpu_usage_min,
                        "cpu_usage_container_max": cpu_usage_max,
                        "cpu_usage_container_sum": cpu_usage_avg,
                        "cpu_throttle_container_avg": cpu_throttle,
                        "cpu_throttle_container_max": cpu_throttle,
                        "cpu_throttle_container_sum": cpu_throttle,
                        "memory_request_container_avg": round(mem_request_gig * GIGABYTE),
                        "memory_request_container_sum": round(mem_request_gig * GIGABYTE),
                        "memory_limit_container_avg": round(mem_limit_gig * GIGABYTE),
                        "memory_limit_container_sum": round(mem_limit_gig * GIGABYTE),
                        "memory_usage_container_avg": round(memory_usage_gig_avg * GIGABYTE),
                        "memory_usage_container_min": round(memory_usage_gig_min * GIGABYTE),
                        "memory_usage_container_max": round(memory_usage_gig_max * GIGABYTE),
                        "memory_usage_container_sum": round(memory_usage_gig_avg * GIGABYTE),
                        "memory_rss_usage_container_avg": round(memory_usage_gig_avg * memory_rss_ratio * GIGABYTE),
                        "memory_rss_usage_container_min": round(memory_usage_gig_min * memory_rss_ratio * GIGABYTE),
                        "memory_rss_usage_container_max": round(memory_usage_gig_max * memory_rss_ratio * GIGABYTE),
                        "memory_rss_usage_container_sum": round(memory_usage_gig_avg * memory_rss_ratio * GIGABYTE),
                    }

            else:
                num_pods = randint(2, 20)
                for _ in range(num_pods):
                    pod_suffix = "".join(choices(ascii_lowercase, k=5))
                    pod_type = choice(("build", "deploy", pod_suffix))
                    pod = self.fake.word() + "_" + pod_type
                    namespace2pod[namespace].append(pod)
                    cpu_cores = node.get("cpu_cores")
                    cpu_limit = round(uniform(0.02, cpu_cores), 5)
                    cpu_request = round(uniform(0.02, cpu_limit), 5)
                    memory_bytes = node.get("memory_bytes")
                    memory_gig = memory_bytes / GIGABYTE
                    mem_limit_gig = round(uniform(25.0, memory_gig), 2)
                    mem_request_gig = round(uniform(25.0, mem_limit_gig), 2)

                    pods[pod] = {
                        "namespace": namespace,
                        "node": node.get("name"),
                        "resource_id": node.get("resource_id"),
                        "pod": pod,
                        "node_capacity_cpu_cores": cpu_cores,
                        "node_capacity_cpu_core_seconds": cpu_cores * HOUR,
                        "node_capacity_memory_bytes": memory_bytes,
                        "node_capacity_memory_byte_seconds": memory_bytes * HOUR,
                        "cpu_request": cpu_request,
                        "cpu_limit": cpu_limit,
                        "mem_request_gig": mem_request_gig,
                        "mem_limit_gig": mem_limit_gig,
                        "pod_labels": self._gen_openshift_labels(),
                    }
                    owner_name, owner_kind, workload, workload_type = get_owner_workload(pod)
                    cpu_usage_avg, cpu_usage_min, cpu_usage_max = generate_randomized_ros_usage({}, cpu_limit)
                    memory_usage_gig_avg, memory_usage_gig_min, memory_usage_gig_max = generate_randomized_ros_usage(
                        {}, mem_limit_gig
                    )
                    memory_rss_ratio = 1 / round(uniform(1.01, 1.9), 2)
                    cpu_throttle = choices([0, round(cpu_usage_avg / randint(10, 20), 5)], weights=(3, 1))[0]

                    ros_ocp_data_pods[pod] = {
                        "namespace": namespace,
                        "node": node.get("name"),
                        "resource_id": node.get("resource_id"),
                        "pod": pod,
                        "container_name": pod,
                        "owner_name": owner_name,
                        "owner_kind": owner_kind,
                        "workload": workload,
                        "workload_type": workload_type,
                        "image_name": self.fake.word() + "-" + self.fake.word(),
                        "cpu_request_container_avg": cpu_request,
                        "cpu_request_container_sum": cpu_request,
                        "cpu_limit_container_avg": cpu_limit,
                        "cpu_limit_container_sum": cpu_limit,
                        "cpu_usage_container_avg": cpu_usage_avg,
                        "cpu_usage_container_min": cpu_usage_min,
                        "cpu_usage_container_max": cpu_usage_max,
                        "cpu_usage_container_sum": cpu_usage_avg,
                        "cpu_throttle_container_avg": cpu_throttle,
                        "cpu_throttle_container_max": cpu_throttle,
                        "cpu_throttle_container_sum": cpu_throttle,
                        "memory_request_container_avg": round(mem_request_gig * GIGABYTE),
                        "memory_request_container_sum": round(mem_request_gig * GIGABYTE),
                        "memory_limit_container_avg": round(mem_limit_gig * GIGABYTE),
                        "memory_limit_container_sum": round(mem_limit_gig * GIGABYTE),
                        "memory_usage_container_avg": round(memory_usage_gig_avg * GIGABYTE),
                        "memory_usage_container_min": round(memory_usage_gig_min * GIGABYTE),
                        "memory_usage_container_max": round(memory_usage_gig_max * GIGABYTE),
                        "memory_usage_container_sum": round(memory_usage_gig_avg * GIGABYTE),
                        "memory_rss_usage_container_avg": round(memory_usage_gig_avg * memory_rss_ratio * GIGABYTE),
                        "memory_rss_usage_container_min": round(memory_usage_gig_min * memory_rss_ratio * GIGABYTE),
                        "memory_rss_usage_container_max": round(memory_usage_gig_max * memory_rss_ratio * GIGABYTE),
                        "memory_rss_usage_container_sum": round(memory_usage_gig_avg * memory_rss_ratio * GIGABYTE),
                    }

        return pods, namespace2pod, ros_ocp_data_pods

    def _gen_volumes(self, namespaces, namespace2pods):  # noqa: R0914,C901
        """Create volumes on specific namespaces and keep relationship."""
        volumes = []
        for namespace, node in namespaces.items():
            storage_class_default = choice(("gp2", "fast", "slow", "gold"))
            if node.get("namespaces"):
                specified_volumes = node.get("namespaces").get(namespace).get("volumes", [])
                for specified_volume in specified_volumes:
                    volume = specified_volume.get("volume_name", self.fake.word())
                    volume_request_gig = specified_volume.get("volume_request_gig")
                    volume_request = volume_request_gig * GIGABYTE
                    specified_vol_claims = specified_volume.get("volume_claims", [])
                    volume_claims = {}
                    total_claims = 0
                    for specified_vc in specified_vol_claims:
                        if volume_request - total_claims <= GIGABYTE:
                            break
                        vol_claim = specified_vc.get("volume_claim_name", self.fake.word())
                        pod = specified_vc.get("pod_name")
                        claim_capacity = max(
                            specified_vc.get("capacity_gig") * GIGABYTE, (volume_request_gig * GIGABYTE - total_claims)
                        )
                        usage_gig = specified_vc.get("volume_claim_usage_gig")
                        if usage_gig:
                            for key, value in usage_gig.items():
                                if value > claim_capacity / GIGABYTE:
                                    usage_gig[key] = claim_capacity / GIGABYTE
                        volume_claims[vol_claim] = {
                            "namespace": namespace,
                            "volume": volume,
                            "labels": specified_vc.get("labels", None),
                            "capacity": claim_capacity,
                            "pod": pod,
                            "volume_claim_usage_gig": usage_gig,
                        }
                        total_claims += claim_capacity
                    volumes.append(
                        {
                            volume: {
                                "namespace": namespace,
                                "volume": volume,
                                "storage_class": specified_volume.get("storage_class", storage_class_default),
                                "volume_request": volume_request,
                                "labels": specified_volume.get("labels", None),
                                "volume_claims": volume_claims,
                            }
                        }
                    )
            else:
                num_volumes = randint(1, 3)
                num_vol_claims = randint(1, 2)
                for _ in range(num_volumes):
                    vol_suffix = "".join(choices(ascii_lowercase, k=10))
                    volume = "pvc" + "-" + vol_suffix
                    vol_request_gig = round(uniform(25.0, 80.0), 2)
                    vol_request = vol_request_gig * GIGABYTE
                    volume_claims = {}
                    total_claims = 0
                    for _ in range(num_vol_claims):
                        if vol_request_gig - total_claims <= GIGABYTE:
                            break
                        vol_claim = self.fake.word()
                        pod = choice(namespace2pods[namespace])
                        claim_capacity = round(uniform(1.0, vol_request_gig), 2) * GIGABYTE
                        volume_claims[vol_claim] = {
                            "namespace": namespace,
                            "volume": volume,
                            "labels": self._gen_openshift_labels(),
                            "capacity": claim_capacity,
                            "pod": pod,
                        }
                        total_claims += claim_capacity
                    volumes.append(
                        {
                            volume: {
                                "namespace": namespace,
                                "volume": volume,
                                "storage_class": choice(("gp2", "fast", "slow", "gold")),
                                "volume_request": vol_request,
                                "labels": self._gen_openshift_labels(),
                                "volume_claims": volume_claims,
                            }
                        }
                    )
        return volumes

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
        report_type = kwargs.get(REPORT_TYPE)
        for column in OCP_REPORT_TYPE_TO_COLS[report_type]:
            row[column] = ""
            if column == "report_period_end":
                row[column] = OCPGenerator.timestamp(bill_end)
            elif column == "report_period_start":
                row[column] = OCPGenerator.timestamp(bill_begin)
        return row

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Add common usage information."""
        row["interval_start"] = OCPGenerator.timestamp(start)
        row["interval_end"] = OCPGenerator.timestamp(end)
        return row

    @staticmethod
    def _get_usage_for_date(usage_dict, start):
        """Return usage for specified hour."""
        if usage_dict:
            for date, usage in usage_dict.items():
                if date == "full_period":
                    return usage
                if parser.parse(date).date() == start.date():
                    return usage
        return None

    def _update_pod_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        user_pod_seconds = kwargs.get("pod_seconds")
        pod_seconds = user_pod_seconds if user_pod_seconds else randint(2, HOUR)
        pod = kwargs.get("pod")
        cpu_limit = pod.pop("cpu_limit")
        mem_limit_gig = pod.pop("mem_limit_gig")

        cpu_request = min(pod.pop("cpu_request"), cpu_limit)
        mem_request_gig = min(pod.pop("mem_request_gig"), mem_limit_gig)
        cpu_usage = self._get_usage_for_date(kwargs.get("cpu_usage"), start)
        cpu = round(uniform(0.02, cpu_limit), 5)
        # ensure that cpu usage is not higher than cpu_limit
        if cpu_usage:
            cpu = min(cpu_limit, cpu_usage)

        mem_usage_gig = self._get_usage_for_date(kwargs.get("mem_usage_gig"), start)
        mem = round(uniform(1, mem_limit_gig), 2)
        # ensure that mem usage is not higher than mem_limit
        if mem_usage_gig:
            mem = min(mem_limit_gig, mem_usage_gig)

        pod["pod_usage_cpu_core_seconds"] = pod_seconds * cpu
        pod["pod_request_cpu_core_seconds"] = pod_seconds * cpu_request
        pod["pod_limit_cpu_core_seconds"] = pod_seconds * cpu_limit
        pod["pod_usage_memory_byte_seconds"] = pod_seconds * mem * GIGABYTE
        pod["pod_request_memory_byte_seconds"] = pod_seconds * mem_request_gig * GIGABYTE
        pod["pod_limit_memory_byte_seconds"] = pod_seconds * mem_limit_gig * GIGABYTE
        row.update(pod)
        return row

    def _update_ros_ocp_pod_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        pod = kwargs.get("pod")
        row.update(pod)
        return row

    def _update_storage_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        volume_claim_usage_gig = self._get_usage_for_date(kwargs.get("volume_claim_usage_gig"), start)

        volume_request = kwargs.get("volume_request")
        vc_capacity_gig = max(kwargs.get("vc_capacity", 10.0), volume_request) / GIGABYTE

        vc_usage_gig = round(uniform(2.0, vc_capacity_gig), 2)
        if volume_claim_usage_gig:
            vc_usage_gig = min(volume_claim_usage_gig, vc_capacity_gig)
        vc_usage = vc_usage_gig * GIGABYTE

        data = {
            "namespace": kwargs.get("namespace"),
            "pod": kwargs.get("pod"),
            "persistentvolumeclaim": kwargs.get("volume_claim"),
            "persistentvolume": kwargs.get("volume_name"),
            "storageclass": kwargs.get("storage_class"),
            "persistentvolumeclaim_capacity_bytes": kwargs.get("vc_capacity"),
            "persistentvolumeclaim_capacity_byte_seconds": vc_capacity_gig * GIGABYTE * HOUR,
            "volume_request_storage_byte_seconds": volume_request * HOUR,
            "persistentvolume_labels": kwargs.get("volume_labels"),
            "persistentvolumeclaim_labels": kwargs.get("volume_claim_labels"),
            "persistentvolumeclaim_usage_byte_seconds": vc_usage * HOUR,
        }
        row.update(data)
        return row

    def _update_node_label_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        data = {"node": kwargs.get("node"), "node_labels": kwargs.get("node_labels")}
        row.update(data)
        return row

    def _update_namespace_label_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        data = {"namespace": kwargs.get("namespace"), "namespace_labels": kwargs.get("namespace_labels")}
        row.update(data)
        return row

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        row = self._add_common_usage_info(row, start, end)
        if kwargs.get(REPORT_TYPE):
            report_type = kwargs.get(REPORT_TYPE)
            method = self.ocp_report_generation.get(report_type).get("_update_data")
            row = method(row, start, end, **kwargs)
        return row

    def _gen_hourly_pods_usage(self, **kwargs):
        """Create hourly data for pod usage."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")

            if self._nodes:
                for pod_name, _ in self.pods.items():
                    cpu_usage = self.pods[pod_name].get("cpu_usage", None)
                    mem_usage_gig = self.pods[pod_name].get("mem_usage_gig", None)
                    pod_seconds = self.pods[pod_name].get("pod_seconds", None)
                    pod = deepcopy(self.pods[pod_name])
                    row = self._init_data_row(start, end, **kwargs)
                    row = self._update_data(
                        row,
                        start,
                        end,
                        pod=pod,
                        cpu_usage=cpu_usage,
                        mem_usage_gig=mem_usage_gig,
                        pod_seconds=pod_seconds,
                        **kwargs,
                    )
                    row.pop("cpu_usage", None)
                    row.pop("mem_usage_gig", None)
                    row.pop("pod_seconds", None)
                    yield row
            else:
                pod_count = len(self.pods)
                num_pods = randint(2, pod_count)
                pod_index_list = range(pod_count)
                pod_choices = list(set(choices(pod_index_list, k=num_pods)))
                pod_keys = list(self.pods.keys())
                for pod_choice in pod_choices:
                    pod_name = pod_keys[pod_choice]
                    pod = deepcopy(self.pods[pod_name])
                    row = self._init_data_row(start, end, **kwargs)
                    row = self._update_data(row, start, end, pod=pod, **kwargs)
                    yield row

    def _gen_quarter_hourly_ros_ocp_pods_usage(self, **kwargs):
        """Create hourly data for pod usage."""
        for quarter_hour in self.quarter_hours:
            start = quarter_hour.get("start")
            end = quarter_hour.get("end")
            if self._nodes:
                for pod_name, _ in self.pods.items():
                    pod = deepcopy(self.ros_data[pod_name])
                    row = self._init_data_row(start, end, **kwargs)
                    yield self._update_data(row, start, end, pod=pod, **kwargs)
            else:
                pod_count = len(self.pods)
                num_pods = randint(2, pod_count)
                pod_index_list = range(pod_count)
                pod_choices = list(set(choices(pod_index_list, k=num_pods)))
                pod_keys = list(self.pods.keys())
                for pod_choice in pod_choices:
                    pod_name = pod_keys[pod_choice]
                    pod = deepcopy(self.ros_data[pod_name])
                    row = self._init_data_row(start, end, **kwargs)
                    yield self._update_data(row, start, end, pod=pod, **kwargs)

    def _gen_hourly_storage_usage(self, **kwargs):
        """Create hourly data for storage usage."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            for volume_dict in self.volumes:
                for volume_name, volume in volume_dict.items():
                    namespace = volume.get("namespace", None)
                    storage_class = volume.get("storage_class", None)
                    volume_request = volume.get("volume_request", None)
                    vol_labels = volume.get("labels", None)
                    volume_claims = volume.get("volume_claims", [])
                    for vc_name, volume_claim in volume_claims.items():
                        pod = volume_claim.get("pod")
                        vc_labels = volume_claim.get("labels")
                        capacity = volume_claim.get("capacity")
                        volume_claim_usage_gig = volume_claim.get("volume_claim_usage_gig", None)
                        row = self._init_data_row(start, end, **kwargs)
                        row = self._update_data(
                            row,
                            start,
                            end,
                            volume_claim=vc_name,
                            pod=pod,
                            volume_claim_labels=vc_labels,
                            vc_capacity=capacity,
                            volume_claim_usage_gig=volume_claim_usage_gig,
                            storage_class=storage_class,
                            volume_name=volume_name,
                            volume_request=volume_request,
                            volume_labels=vol_labels,
                            namespace=namespace,
                            **kwargs,
                        )
                        yield row

    def _gen_hourly_node_label_usage(self, **kwargs):
        """Create hourly data for nodel label report."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            for node in self.nodes:
                row = self._init_data_row(start, end, **kwargs)
                row = self._update_data(
                    row, start, end, node_labels=node.get("node_labels"), node=node.get("name"), **kwargs
                )
                yield row

    def _gen_hourly_namespace_label_usage(self, **kwargs):
        """Create hourly data for nodel label report."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            for node in self.nodes:
                if node.get("namespaces"):
                    for name, _ in node.get("namespaces").items():
                        row = self._init_data_row(start, end, **kwargs)
                        row = self._update_data(
                            row,
                            start,
                            end,
                            namespace_labels=node.get("namespaces").get(name).get("namespace_labels"),
                            namespace=name,
                            **kwargs,
                        )
                        yield row

    def _generate_hourly_data(self, **kwargs):
        """Create hourly data."""
        report_type = kwargs.get(REPORT_TYPE)
        method = self.ocp_report_generation.get(report_type).get("_generate_hourly_data")
        return method(**kwargs)

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        meta = {REPORT_TYPE: report_type}
        return self._generate_hourly_data(**meta)
