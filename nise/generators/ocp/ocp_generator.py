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
from collections import defaultdict
from copy import deepcopy
from random import choice
from random import choices
from random import randint
from random import uniform
from string import ascii_lowercase
from uuid import uuid4

from dateutil import parser
from faker import Faker

from nise.generators.generator import AbstractGenerator
from nise.generators.generator import REPORT_TYPE

FAKER = Faker()

GIGABYTE = 1024 * 1024 * 1024
HOUR = 60 * 60
AWS_RESID_LENGTH = 17

OCP_POD_USAGE = "ocp_pod_usage"
OCP_STORAGE_USAGE = "ocp_storage_usage"
OCP_NODE_LABEL = "ocp_node_label"
OCP_NAMESPACE_LABEL = "ocp_namespace_label"
OCP_VM_USAGE = "ocp_vm_usage"
OCP_ROS_USAGE = "ocp_ros_usage"
OCP_POD_USAGE_COLUMNS = (
    "report_period_start",
    "report_period_end",
    "interval_start",
    "interval_end",
    "pod",
    "namespace",
    "node",
    "resource_id",
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
    "node",
    "persistentvolumeclaim",
    "persistentvolume",
    "storageclass",
    "csi_driver",
    "csi_volume_handle",
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
OCP_VM_COLUMNS = (
    "report_period_start",
    "report_period_end",
    "interval_start",
    "interval_end",
    "node",
    "resource_id",
    "namespace",
    "vm_name",
    "vm_instance_type",
    "vm_os",
    "vm_guest_os_arch",
    "vm_guest_os_name",
    "vm_guest_os_version",
    "vm_uptime_total_seconds",
    "vm_cpu_limit_cores",
    "vm_cpu_limit_core_seconds",
    "vm_cpu_request_cores",
    "vm_cpu_request_core_seconds",
    "vm_cpu_request_sockets",
    "vm_cpu_request_socket_seconds",
    "vm_cpu_request_threads",
    "vm_cpu_request_thread_seconds",
    "vm_cpu_usage_total_seconds",
    "vm_memory_limit_bytes",
    "vm_memory_limit_byte_seconds",
    "vm_memory_request_bytes",
    "vm_memory_request_byte_seconds",
    "vm_memory_usage_byte_seconds",
    "vm_device",
    "vm_volume_mode",
    "vm_persistentvolumeclaim_name",
    "vm_disk_allocated_size_byte_seconds",
    "vm_labels",
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
    OCP_VM_USAGE: OCP_VM_COLUMNS,
    OCP_ROS_USAGE: OCP_ROS_USAGE_COLUMN,
}

# No recommendations are generated for job and manual_pod workloads! Keep these two options as the last two items
# in the dict to guarantee they are not randomly picked in get_owner_workload function.
OCP_OWNER_WORKLOAD_CHOICES = {
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
    "job": (None, "Job", None, "job"),  # not supported by Kruize - recommendation won't be generated!
    "manual_pod": ("<none>", "<none>", None, None),  # manually created Pod - recommendation won't be generated!
}
VM_OS_TYPES = (
    "alpine",
    "centos.stream10",
    "centos.stream10.desktop",
    "centos.stream9",
    "centos.stream9.desktop",
    "centos.stream9.dpdk",
    "cirros",
    "debian",
    "fedora",
    "fedora.arm64",
    "fedora.s390x",
    "legacy",
    "linux",
    "linux.efi",
    "opensuse.leap",
    "opensuse.tumbleweed",
    "oraclelinux",
    "rhel.10",
    "rhel.10.arm64",
    "rhel.7",
    "rhel.7.desktop",
    "rhel.8",
    "rhel.8.desktop",
    "rhel.8.dpdk",
    "rhel.9",
    "rhel.9.arm64",
    "rhel.9.desktop",
    "rhel.9.dpdk",
    "rhel.9.realtime",
    "rhel.9.s390x",
    "sles",
    "ubuntu",
    "windows.10",
    "windows.10.virtio",
    "windows.11",
    "windows.11.virtio",
    "windows.2k16",
    "windows.2k16.virtio",
    "windows.2k19",
    "windows.2k19.virtio",
    "windows.2k22",
    "windows.2k22.virtio",
    "windows.2k25",
    "windows.2k25.virtio",
)

VM_INSTANCE_TYPES = (
    "cx1.2xlarge",
    "cx1.4xlarge",
    "cx1.8xlarge",
    "cx1.large",
    "cx1.medium",
    "cx1.xlarge",
    "m1.2xlarge",
    "m1.4xlarge",
    "m1.8xlarge",
    "m1.large",
    "m1.xlarge",
    "n1.2xlarge",
    "n1.4xlarge",
    "n1.8xlarge",
    "n1.large",
    "n1.medium",
    "n1.xlarge",
    "o1.2xlarge",
    "o1.4xlarge",
    "o1.8xlarge",
    "o1.large",
    "o1.medium",
    "o1.micro",
    "o1.nano",
    "o1.small",
    "o1.xlarge",
    "rt1.2xlarge",
    "rt1.4xlarge",
    "rt1.8xlarge",
    "rt1.large",
    "rt1.medium",
    "rt1.micro",
    "rt1.small",
    "rt1.xlarge",
    "u1.2xlarge",
    "u1.2xmedium",
    "u1.4xlarge",
    "u1.8xlarge",
    "u1.large",
    "u1.medium",
    "u1.micro",
    "u1.nano",
    "u1.small",
    "u1.xlarge",
)

VM_GUEST_ARCH = (
    "x86_64",
    "s390x",
    "aarch64",
    "ppc64le",
)

VM_GUEST_OS = (
    "Windows",
    "Red Hat Linux Enterprise",
    "CentOS",
    "Fedora",
    "Ubuntu",
)

VM_GUEST_VERSION = ("10.0", "7.5", "8.1", "9.5")


def get_storage_class_and_driver():
    return choice(
        (
            ("gp3-csi", "ebs.csi.aws.com"),
            ("fast", "disk.csi.azure.com"),
            ("slow", "disk.csi.azure.com"),
            ("gold", "pd.csi.storage.gke.io"),
        )
    )


def get_owner_workload(pod, workload=None):
    if not workload:
        workload = choice(list(OCP_OWNER_WORKLOAD_CHOICES.keys())[:-2])  # omit job and manual_pod from random choices
    on, ok, wl, wt = OCP_OWNER_WORKLOAD_CHOICES.get(
        workload.lower(),
        choice(list(OCP_OWNER_WORKLOAD_CHOICES.values())[:-2]),  # omit job and manual_pod from random choices
    )
    if on == "<none>" and wl == "<none>":  # manually created Pod
        return on, ok, wl, wt
    elif wl == "<none>":  # manually created ReplicaSet or ReplicationController
        return pod, ok, wl, wt
    return pod, ok, pod, wt


def generate_randomized_ros_usage(usage_dict, limit_value, generate_constant_value=False):
    if generate_constant_value:
        # will generate constant values
        if usage_value := usage_dict.get("full_period"):
            avg_value = min(round(usage_value, 5), limit_value)
        else:
            avg_value = round(uniform(limit_value * 0.1, limit_value), 5)

        min_value = avg_value
        max_value = avg_value
    else:
        # This will generate randomised values
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


def get_vm_instance(vm=None):
    vm = vm or {}
    return {
        "vm_instance_type": vm.get("instance_type") or choice(VM_INSTANCE_TYPES),
        "vm_os": vm.get("os") or choice(VM_OS_TYPES),
        "vm_guest_os_arch": vm.get("guest_os_arch") or choice(VM_GUEST_ARCH),
        "vm_guest_os_name": vm.get("guest_os_name") or choice(VM_GUEST_OS),
        "vm_guest_os_version": vm.get("guest_os_version") or choice(VM_GUEST_VERSION),
    }


def get_vm_from_label(labels):
    if not labels:
        return ""
    for label in labels.split("|"):
        key, value = label.split(":")
        if key == "label_vm_kubevirt_io_name":
            return value


class OCPGenerator(AbstractGenerator):
    """Defines a abstract class for generators."""

    def __init__(self, start_date, end_date, attributes, ros_ocp_info=False, constant_values_ros_ocp=False):
        """Initialize the generator."""
        self._nodes = None
        self.ros_ocp_info = ros_ocp_info
        self.constant_values_ros_ocp = constant_values_ros_ocp
        if attributes:
            self._nodes = attributes.get("nodes")

        super().__init__(start_date, end_date, hour_delta=datetime.timedelta(minutes=59, seconds=59))
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
        self.pod_pvc_map = {}
        self.vm_pod_map = {}
        self.nodes = self._gen_nodes()
        self.namespaces = self._gen_namespaces(self.nodes)
        self.pods, self.namespace2pods, self.ros_data = self._gen_pods(self.namespaces)

        self.volumes = self._gen_volumes(self.namespaces, self.namespace2pods)
        self.vms, self.namespace2vm = self._gen_virtual_machines(self.namespaces)

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
            OCP_VM_USAGE: {
                "_generate_hourly_data": self._gen_hourly_vm_usage,
                "_update_data": self._update_vm_data,
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
                resource_id = str(item.get("resource_id", uuid4().hex[:AWS_RESID_LENGTH]))
                # Handle empty namespaces
                raw_namespaces = item.get("namespaces", {})
                if raw_namespaces is None:
                    raw_namespaces = {}
                # Handle empty namespace
                processed_namespaces = {
                    ns_name: ({} if ns_data is None else ns_data) for ns_name, ns_data in raw_namespaces.items()
                }
                node = {
                    "name": item.get("node_name", "node_" + self.fake.word()),
                    "cpu_cores": item.get("cpu_cores", randint(2, 16)),
                    "memory_bytes": memory_bytes,
                    "resource_id": "i-" + resource_id,
                    "namespaces": processed_namespaces,
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
                    "resource_id": "i-" + uuid4().hex[:AWS_RESID_LENGTH],
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

        return "|".join(f"{key}:{value}" for key, value in labels.items())

    def _gen_specific_pod(self, node, namespace, specified_pod):
        pod_name = specified_pod.get("pod_name", self.fake.word())

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
        mem_request_gig = min(specified_pod.get("mem_request_gig", round(uniform(25.0, 80.0), 2)), mem_limit_gig)
        memory_usage_gig = specified_pod.get("mem_usage_gig", {})
        for key, value in memory_usage_gig.items():
            if value > mem_limit_gig:
                memory_usage_gig[key] = mem_limit_gig

        pod = {
            "namespace": namespace,
            "node": node.get("name"),
            "resource_id": node.get("resource_id"),
            "pod": pod_name,
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

        owner_name, owner_kind, workload, workload_type = get_owner_workload(pod_name, specified_pod.get("workload"))

        cpu_usage_avg, cpu_usage_min, cpu_usage_max = generate_randomized_ros_usage(
            cpu_usage, cpu_limit, generate_constant_value=self.constant_values_ros_ocp
        )
        memory_usage_gig_avg, memory_usage_gig_min, memory_usage_gig_max = generate_randomized_ros_usage(
            memory_usage_gig, mem_limit_gig, generate_constant_value=self.constant_values_ros_ocp
        )
        if self.constant_values_ros_ocp:
            memory_rss_ratio = 1 / round(1, 2)
        else:
            memory_rss_ratio = 1 / round(uniform(1.01, 1.9), 2)
        cpu_throttle = choices([0, round(cpu_usage_avg / randint(10, 20), 5)], weights=(3, 1))[0]

        ros_pod = {
            "namespace": namespace,
            "node": node.get("name"),
            "resource_id": node.get("resource_id"),
            "pod": pod_name,
            "container_name": pod_name,
            "owner_name": owner_name,
            "owner_kind": owner_kind,
            "workload": workload,
            "workload_type": workload_type,
            "image_name": f"{self.fake.word()}-{self.fake.word()}",
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
        return pod_name, pod, ros_pod

    def _gen_pods(self, namespaces):
        """Create pods on specific namespaces and keep relationship."""
        pods = {}
        ros_ocp_data_pods = {}
        namespace2pod = defaultdict(list)
        for namespace, node in namespaces.items():
            namespace2pod[namespace] = []
            if node.get("namespaces"):
                specified_pods = node.get("namespaces").get(namespace).get("pods") or []
                for specified_pod in specified_pods:
                    pod_name, pod, ros_pod = self._gen_specific_pod(node, namespace, specified_pod)
                    namespace2pod[namespace].append(pod_name)
                    pods[pod_name] = pod
                    ros_ocp_data_pods[pod_name] = ros_pod

                    # add pods that are labeled as a VM to the list of VMs
                    if vm := get_vm_from_label(specified_pod.get("labels", "")):
                        vms = node["namespaces"][namespace].get("virtual_machines") or []
                        vm_names = {v.get("vm_name") for v in vms}
                        if vm not in self.vm_pod_map:
                            self.vm_pod_map[vm] = pod_name
                        if vm in vm_names:
                            continue
                        pod_copy = deepcopy(specified_pod)
                        pod_copy["vm_name"] = vm
                        if vm_seconds := pod_copy.get("pod_seconds"):
                            pod_copy["vm_seconds"] = vm_seconds
                        vms.append(pod_copy)
                        node["namespaces"][namespace]["virtual_machines"] = vms
            else:
                num_pods = randint(2, 20)
                for _ in range(num_pods):
                    pod_suffix = "".join(choices(ascii_lowercase, k=5))
                    pod_type = choice(("build", "deploy", pod_suffix))
                    pod_name = f"{self.fake.word()}_{pod_type}"
                    namespace2pod[namespace].append(pod_name)
                    cpu_cores = node.get("cpu_cores")
                    cpu_limit = round(uniform(0.02, cpu_cores), 5)
                    cpu_request = round(uniform(0.02, cpu_limit), 5)
                    memory_bytes = node.get("memory_bytes")
                    memory_gig = memory_bytes / GIGABYTE
                    mem_limit_gig = round(uniform(25.0, memory_gig), 2)
                    mem_request_gig = round(uniform(25.0, mem_limit_gig), 2)

                    pods[pod_name] = {
                        "namespace": namespace,
                        "node": node.get("name"),
                        "resource_id": node.get("resource_id"),
                        "pod": pod_name,
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
                    owner_name, owner_kind, workload, workload_type = get_owner_workload(pod_name)
                    cpu_usage_avg, cpu_usage_min, cpu_usage_max = generate_randomized_ros_usage(
                        {}, cpu_limit, generate_constant_value=self.constant_values_ros_ocp
                    )
                    memory_usage_gig_avg, memory_usage_gig_min, memory_usage_gig_max = generate_randomized_ros_usage(
                        {}, mem_limit_gig, generate_constant_value=self.constant_values_ros_ocp
                    )
                    memory_rss_ratio = 1 / round(uniform(1.01, 1.9), 2)
                    cpu_throttle = choices([0, round(cpu_usage_avg / randint(10, 20), 5)], weights=(3, 1))[0]

                    ros_ocp_data_pods[pod_name] = {
                        "namespace": namespace,
                        "node": node.get("name"),
                        "resource_id": node.get("resource_id"),
                        "pod": pod_name,
                        "container_name": pod_name,
                        "owner_name": owner_name,
                        "owner_kind": owner_kind,
                        "workload": workload,
                        "workload_type": workload_type,
                        "image_name": f"{self.fake.word()}-{self.fake.word()}",
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

    def _gen_specific_volume(self, node, namespace, specified_volume):
        storage_class_default, csi_default = get_storage_class_and_driver()
        volume = specified_volume.get("volume_name", f"pv-{self.fake.word()}")
        volume_request_gig = specified_volume.get("volume_request_gig") or 100
        volume_request = volume_request_gig * GIGABYTE
        specified_vol_claims = specified_volume.get("volume_claims", [])
        volume_claims = {}
        total_claims = 0
        for specified_vc in specified_vol_claims:
            if volume_request - total_claims <= GIGABYTE:
                break
            vol_claim = specified_vc.get("volume_claim_name", self.fake.word())
            pod = specified_vc.get("pod_name")
            claim_capacity = specified_vc.get("capacity_gig", volume_request_gig) * GIGABYTE
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
            if total_claims > volume_request:
                raise ValueError(f"Total claims {total_claims} is greater than volume request {volume_request}")
            self.pod_pvc_map[pod] = vol_claim
        return volume, {
            "node": node.get("name"),
            "namespace": namespace,
            "volume": volume,
            "storage_class": specified_volume.get("storage_class", storage_class_default),
            "csi_driver": specified_volume.get("csi_driver", csi_default),
            "csi_volume_handle": specified_volume.get("csi_volume_handle", f"vol-{uuid4().hex[:AWS_RESID_LENGTH]}"),
            "volume_request": volume_request,
            "labels": specified_volume.get("labels", None),
            "volume_claims": volume_claims,
        }

    def _gen_volumes(self, namespaces, namespace2pods):  # noqa: C901
        """Create volumes on specific namespaces and keep relationship."""
        volumes = []
        for namespace, node in namespaces.items():
            if node.get("namespaces"):
                specified_volumes = node.get("namespaces").get(namespace).get("volumes", [])
                for specified_volume in specified_volumes:
                    volume_name, volume = self._gen_specific_volume(node, namespace, specified_volume)
                    volumes.append({volume_name: volume})
            else:
                num_volumes = randint(1, 3)
                num_vol_claims = randint(1, 2)
                for _ in range(num_volumes):
                    vol_suffix = "".join(choices(ascii_lowercase, k=10))
                    volume = "pv" + "-" + vol_suffix
                    vol_request_gig = round(uniform(25.0, 80.0), 2)
                    vol_request = vol_request_gig * GIGABYTE
                    volume_claims = {}
                    total_claims = 0
                    for _ in range(num_vol_claims):
                        if vol_request - total_claims <= GIGABYTE:
                            break
                        vol_claim = self.fake.word()
                        pod = choice(namespace2pods[namespace])
                        claim_capacity = round(uniform(1.0, (vol_request_gig - total_claims / GIGABYTE)), 2) * GIGABYTE
                        volume_claims[vol_claim] = {
                            "namespace": namespace,
                            "volume": volume,
                            "labels": self._gen_openshift_labels(),
                            "capacity": claim_capacity,
                            "pod": pod,
                        }
                        total_claims += claim_capacity
                        self.pod_pvc_map[pod] = vol_claim
                    storage_class_default, csi_default = get_storage_class_and_driver()
                    volumes.append(
                        {
                            volume: {
                                "namespace": namespace,
                                "node": node.get("name"),
                                "volume": volume,
                                "storage_class": storage_class_default,
                                "csi_driver": csi_default,
                                "csi_volume_handle": f"vol-{uuid4().hex[:AWS_RESID_LENGTH]}",
                                "volume_request": vol_request,
                                "labels": self._gen_openshift_labels(),
                                "volume_claims": volume_claims,
                            }
                        }
                    )
        return volumes

    def get_specific_pvc_from_pod(self, pod_name):
        if not (pvc := self.pod_pvc_map.get(pod_name)):
            return "", {}
        for volume in self.volumes:
            for vol_name, vol in volume.items():
                if specific_pvc := vol["volume_claims"].get(pvc):
                    return pvc, specific_pvc
        return "", {}

    def get_vm_disk(self, *, specified_vc=None, pod_name="", static_report=False):
        specified_vc = specified_vc or {}
        vm_disk = {
            "vm_device": specified_vc.get("vol_device") or "rootdisk",
            "vm_volume_mode": specified_vc.get("volume_mode") or "Block",
        }
        if _pod_name := specified_vc.get("pod_name") or pod_name:
            pvc_name, pvc = self.get_specific_pvc_from_pod(_pod_name)
            if pvc_name and pvc:
                vm_disk |= {
                    "vm_persistentvolumeclaim_name": pvc_name,
                    "vc_capacity": pvc["capacity"],
                }
                return vm_disk
            if static_report:
                return {}
        vm_disk |= {
            "vm_persistentvolumeclaim_name": specified_vc.get("volume_claim_name", FAKER.word()),
            "vc_capacity": specified_vc.get("capacity_gig", randint(30, 50)) * GIGABYTE,
        }
        return vm_disk

    def _gen_virtual_machines(self, namespaces):  # noqa: C901
        """Create vms on specific namespaces and keep relationship."""
        vms = {}
        namespace2vm = {}
        for namespace, node in namespaces.items():
            namespace2vm[namespace] = []
            if node.get("namespaces"):
                specified_vms = node.get("namespaces").get(namespace).get("virtual_machines") or []
                for specified_vm in specified_vms:
                    vm = specified_vm.get("vm_name", self.fake.word())
                    namespace2vm[namespace].append(vm)
                    cpu_cores = node.get("cpu_cores")
                    memory_bytes = node.get("memory_bytes")

                    cpu_limit_cores = min(specified_vm.get("cpu_limit", cpu_cores), cpu_cores)
                    cpu_request_cores = min(
                        specified_vm.get("cpu_request", round(uniform(0.02, cpu_limit_cores), 5)),
                        cpu_limit_cores,
                    )
                    cpu_request_sockets = min(
                        specified_vm.get("cpu_request_sockets", round(uniform(0.02, cpu_limit_cores), 5)),
                        cpu_limit_cores,
                    )
                    cpu_request_threads = min(
                        specified_vm.get("cpu_request_threads", round(uniform(0.02, cpu_limit_cores), 5)),
                        cpu_limit_cores,
                    )
                    cpu_usage = specified_vm.get("cpu_usage", {})
                    for key, value in cpu_usage.items():
                        if value > cpu_limit_cores:
                            cpu_usage[key] = cpu_limit_cores

                    memory_gig = memory_bytes / GIGABYTE
                    mem_limit_gig = min(specified_vm.get("mem_limit_gig", memory_gig), memory_gig)
                    mem_request_gig = min(
                        specified_vm.get("mem_request_gig", round(uniform(25.0, 80.0), 2)), mem_limit_gig
                    )
                    memory_usage_gig = specified_vm.get("mem_usage_gig", {})
                    for key, value in memory_usage_gig.items():
                        if value > mem_limit_gig:
                            memory_usage_gig[key] = mem_limit_gig
                        memory_usage_gig[key] *= GIGABYTE
                    vms[vm] = (
                        {
                            "node": node.get("name"),
                            "resource_id": node.get("resource_id"),
                            "namespace": namespace,
                            "vm_name": vm,
                            "vm_cpu_limit_cores": cpu_limit_cores,
                            "vm_cpu_request_cores": cpu_request_cores,
                            "vm_cpu_request_sockets": cpu_request_sockets,
                            "vm_cpu_request_threads": cpu_request_threads,
                            "cpu_usage": cpu_usage,
                            "vm_memory_request_bytes": mem_request_gig * GIGABYTE,
                            "vm_memory_limit_bytes": mem_limit_gig * GIGABYTE,
                            "mem_usage_gig": memory_usage_gig,
                            "vm_labels": specified_vm.get("labels", None),
                            "vm_seconds": specified_vm.get("vm_seconds"),
                        }
                        | get_vm_instance(vm=specified_vm)
                        | self.get_vm_disk(specified_vc=specified_vm, static_report=True)
                    )

            else:
                num_vms = randint(2, 20)
                for _ in range(num_vms):
                    vm_suffix = "".join(choices(ascii_lowercase, k=5))
                    vm_type = choice(("build", "deploy", vm_suffix))
                    vm = f"{self.fake.word()}_{vm_type}"
                    namespace2vm[namespace].append(vm)
                    cpu_cores = node.get("cpu_cores")
                    cpu_limit_cores = round(uniform(0.02, cpu_cores), 5)
                    cpu_request_cores = round(uniform(0.02, cpu_limit_cores), 5)
                    cpu_request_sockets = round(uniform(0.02, cpu_limit_cores), 5)
                    cpu_request_threads = round(uniform(0.02, cpu_limit_cores), 5)
                    memory_bytes = node.get("memory_bytes")
                    memory_gig = memory_bytes / GIGABYTE
                    mem_limit_gig = round(uniform(25.0, memory_gig), 2)
                    mem_request_gig = round(uniform(25.0, mem_limit_gig), 2)

                    vms[vm] = (
                        {
                            "node": node.get("name"),
                            "resource_id": node.get("resource_id"),
                            "namespace": namespace,
                            "vm_name": vm,
                            "vm_cpu_limit_cores": cpu_limit_cores,
                            "vm_cpu_request_cores": cpu_request_cores,
                            "vm_cpu_request_sockets": cpu_request_sockets,
                            "vm_cpu_request_threads": cpu_request_threads,
                            "vm_memory_request_bytes": mem_request_gig * GIGABYTE,
                            "vm_memory_limit_bytes": mem_limit_gig * GIGABYTE,
                            "vm_labels": self._gen_openshift_labels(),
                        }
                        | get_vm_instance()
                        | self.get_vm_disk(pod_name=vm)
                    )

        vms_defined_in_pod_labels = {get_vm_from_label(pod["pod_labels"]) for _, pod in self.pods.items()}
        for namespace, node in namespaces.items():
            for vm in namespace2vm[namespace]:
                vm_copy = deepcopy(vms[vm])
                if vm not in vms_defined_in_pod_labels or vm not in self.vm_pod_map:
                    # create pod corresponding to VM since it does not exist
                    vm_copy["pod_name"] = vm
                    vm_copy["labels"] = f"label_vm_kubevirt_io_name:{vm}"
                    if pod_seconds := vm_copy.get("vm_seconds"):
                        vm_copy["pod_seconds"] = pod_seconds
                    pod_name, pod, ros_pod = self._gen_specific_pod(node, namespace, vm_copy)
                    self.pods[pod_name] = pod
                    self.ros_data[pod_name] = ros_pod
                    self.namespace2pods[namespace].append(pod_name)
                vcm = vm_copy.get("vm_persistentvolumeclaim_name")
                if vcm and vcm not in self.pod_pvc_map.values():
                    specified_volume = {
                        "volume_claims": [
                            {
                                "pod_name": vm,
                                "volume_claim_name": vcm,
                                "capacity_gig": vm_copy["vc_capacity"] / GIGABYTE,
                            }
                        ]
                    }
                    volume_name, volume = self._gen_specific_volume(node, namespace, specified_volume)
                    self.volumes.append({volume_name: volume})

        return vms, namespace2vm

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
        pod_seconds = user_pod_seconds or randint(2, HOUR)
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

    def _update_vm_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        user_vm_seconds = kwargs.get("vm_seconds")
        vm_seconds = user_vm_seconds or randint(2, HOUR)
        vm = kwargs.get("vm")
        cpu_limit = vm.get("vm_cpu_limit_cores")
        mem_limit_bytes = vm.get("vm_memory_limit_bytes")

        cpu_request_cores = min(vm.get("vm_cpu_request_cores"), cpu_limit)
        cpu_request_sockets = min(vm.get("vm_cpu_request_sockets"), cpu_limit)
        cpu_request_threads = min(vm.get("vm_cpu_request_threads"), cpu_limit)
        mem_request_bytes = min(vm.get("vm_memory_request_bytes"), mem_limit_bytes)
        cpu_usage = self._get_usage_for_date(kwargs.get("cpu_usage"), start)
        cpu = round(uniform(0.02, cpu_limit), 5)
        # ensure that cpu usage is not higher than cpu_limit
        if cpu_usage:
            cpu = min(cpu_limit, cpu_usage)

        mem_usage_gig = self._get_usage_for_date(kwargs.get("mem_usage_gig"), start)
        mem = round(uniform(1024, mem_limit_bytes), 2)
        # ensure that mem usage is not higher than mem_limit
        if mem_usage_gig:
            mem = min(mem_limit_bytes, mem_usage_gig)

        vm["vm_cpu_usage_total_seconds"] = vm_seconds * cpu
        vm["vm_cpu_request_core_seconds"] = vm_seconds * cpu_request_cores
        vm["vm_cpu_request_socket_seconds"] = vm_seconds * cpu_request_sockets
        vm["vm_cpu_request_thread_seconds"] = vm_seconds * cpu_request_threads

        vm["vm_cpu_limit_core_seconds"] = vm_seconds * cpu_limit

        vm["vm_memory_usage_byte_seconds"] = vm_seconds * mem
        vm["vm_memory_request_byte_seconds"] = vm_seconds * mem_request_bytes
        vm["vm_memory_limit_byte_seconds"] = vm_seconds * mem_limit_bytes

        vm["vm_uptime_total_seconds"] = vm_seconds

        if vc_capacity := kwargs.get("vc_capacity"):
            vm["vm_disk_allocated_size_byte_seconds"] = vc_capacity * HOUR

        row.update(vm)
        return row

    def _randomize_ros_ocp_line_values(self, pod_in):
        """Randomize usage values for each line item or ROS report"""
        values_to_randomize = [
            "cpu_usage_container_avg",
            "cpu_usage_container_min",
            "cpu_usage_container_max",
            "cpu_usage_container_sum",
            "cpu_throttle_container_avg",
            "cpu_throttle_container_max",
            "cpu_throttle_container_sum",
            "memory_usage_container_avg",
            "memory_usage_container_min",
            "memory_usage_container_max",
            "memory_usage_container_sum",
            "memory_rss_usage_container_avg",
            "memory_rss_usage_container_min",
            "memory_rss_usage_container_max",
            "memory_rss_usage_container_sum",
        ]
        randomization_value = uniform(0.9, 1.1)
        cpu_limit = pod_in.get("cpu_limit_container_avg", 1000000)
        memory_limit = pod_in.get("memory_limit_container_avg", 1e20)

        pod_out = pod_in.copy()
        for pod_key in values_to_randomize:
            if pod_value := pod_in.get(pod_key):
                if pod_key.startswith("cpu"):
                    pod_out[pod_key] = round(min(randomization_value * pod_value, cpu_limit), 5)
                else:
                    pod_out[pod_key] = round(min(randomization_value * pod_value, memory_limit))
        return pod_out

    def _update_ros_ocp_pod_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        pod = kwargs.get("pod")
        if pod and not self.constant_values_ros_ocp:
            pod = self._randomize_ros_ocp_line_values(pod)
        row.update(pod)
        return row

    def _update_storage_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        volume_claim_usage_gig = self._get_usage_for_date(kwargs.get("volume_claim_usage_gig"), start)

        volume_request = kwargs.get("volume_request", 0)
        # volume_request_storage_byte_seconds is empty for claimless PersistentVolumes
        volume_request_storage_byte_seconds = volume_request * HOUR if volume_request > 0 else None
        vc_capacity_gig = kwargs["vc_capacity"] / GIGABYTE

        vc_usage_gig = round(uniform(2.0, vc_capacity_gig), 2)
        if volume_claim_usage_gig:
            vc_usage_gig = min(volume_claim_usage_gig, vc_capacity_gig)
        # persistentvolumeclaim_usage_byte_seconds is empty for claimless PersistentVolumes
        vc_usage = vc_usage_gig * GIGABYTE * HOUR if volume_request_storage_byte_seconds else None

        data = {
            "namespace": kwargs.get("namespace"),
            "pod": kwargs.get("pod"),
            "node": kwargs.get("node"),
            "persistentvolumeclaim": kwargs.get("volume_claim"),
            "persistentvolume": kwargs.get("volume_name"),
            "storageclass": kwargs.get("storage_class"),
            "csi_driver": kwargs.get("csi_driver"),
            "csi_volume_handle": kwargs.get("csi_volume_handle"),
            "persistentvolumeclaim_capacity_bytes": vc_capacity_gig * GIGABYTE,
            "persistentvolumeclaim_capacity_byte_seconds": vc_capacity_gig * GIGABYTE * HOUR,
            "volume_request_storage_byte_seconds": volume_request_storage_byte_seconds,
            "persistentvolumeclaim_usage_byte_seconds": vc_usage,
            "persistentvolume_labels": kwargs.get("volume_labels"),
            "persistentvolumeclaim_labels": kwargs.get("volume_claim_labels"),
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
                    yield self._update_data(row, start, end, pod=pod, **kwargs)

    def _gen_hourly_vm_usage(self, **kwargs):
        """Create hourly data for vm usage."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")

            if self._nodes:
                for vm_name, _ in self.vms.items():
                    cpu_usage = self.vms[vm_name].get("cpu_usage", None)
                    mem_usage_gig = self.vms[vm_name].get("mem_usage_gig", None)
                    vm_seconds = self.vms[vm_name].get("vm_seconds", None)
                    vc_capacity = self.vms[vm_name].get("vc_capacity", None)
                    vm = deepcopy(self.vms[vm_name])
                    row = self._init_data_row(start, end, **kwargs)
                    row = self._update_data(
                        row,
                        start,
                        end,
                        vm=vm,
                        cpu_usage=cpu_usage,
                        mem_usage_gig=mem_usage_gig,
                        vm_seconds=vm_seconds,
                        vc_capacity=vc_capacity,
                        **kwargs,
                    )
                    row.pop("cpu_usage", None)
                    row.pop("mem_usage_gig", None)
                    row.pop("vm_seconds", None)
                    row.pop("vc_capacity", None)
                    yield row
            else:
                vm_count = len(self.vms)
                num_vms = randint(2, vm_count)
                vm_index_list = range(vm_count)
                vm_choices = list(set(choices(vm_index_list, k=num_vms)))
                vm_keys = list(self.vms.keys())
                for vm_choice in vm_choices:
                    vm_name = vm_keys[vm_choice]
                    vm = deepcopy(self.vms[vm_name])
                    vc_capacity = vm.get("vc_capacity", None)
                    row = self._init_data_row(start, end, **kwargs)
                    row = self._update_data(row, start, end, vm=vm, vc_capacity=vc_capacity, **kwargs)
                    row.pop("vc_capacity", None)
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
                    node = volume.get("node")
                    namespace = volume.get("namespace", None)
                    storage_class = volume.get("storage_class", None)
                    csi_driver = volume.get("csi_driver", None)
                    csi_volume_handle = volume.get("csi_volume_handle", None)
                    volume_request = volume.get("volume_request", None)
                    vol_labels = volume.get("labels", None)
                    volume_claims = volume.get("volume_claims", [])
                    for vc_name, volume_claim in volume_claims.items():
                        pod = volume_claim.get("pod")
                        vc_labels = volume_claim.get("labels")
                        capacity = volume_claim.get("capacity")
                        volume_claim_usage_gig = volume_claim.get("volume_claim_usage_gig", None)
                        row = self._init_data_row(start, end, **kwargs)
                        yield self._update_data(
                            row,
                            start,
                            end,
                            volume_claim=vc_name,
                            pod=pod,
                            node=node,
                            volume_claim_labels=vc_labels,
                            vc_capacity=capacity,
                            volume_claim_usage_gig=volume_claim_usage_gig,
                            storage_class=storage_class,
                            csi_driver=csi_driver,
                            csi_volume_handle=csi_volume_handle,
                            volume_name=volume_name,
                            volume_request=volume_request,
                            volume_labels=vol_labels,
                            namespace=namespace,
                            **kwargs,
                        )
                    if not volume_claims:
                        row = self._init_data_row(start, end, **kwargs)
                        yield self._update_data(
                            row,
                            start,
                            end,
                            storage_class=storage_class,
                            csi_driver=csi_driver,
                            csi_volume_handle=csi_volume_handle,
                            volume_name=volume_name,
                            vc_capacity=volume_request,
                            volume_labels=vol_labels,
                            **kwargs,
                        )

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
