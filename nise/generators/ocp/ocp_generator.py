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

from dateutil import parser
from nise.generators.generator import AbstractGenerator
from nise.generators.generator import REPORT_TYPE

GIGABYTE = 1024 * 1024 * 1024
HOUR = 60 * 60

OCP_POD_USAGE = "ocp_pod_usage"
OCP_STORAGE_USAGE = "ocp_storage_usage"
OCP_NODE_LABEL = "ocp_node_label"
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
OCP_REPORT_TYPE_TO_COLS = {
    OCP_POD_USAGE: OCP_POD_USAGE_COLUMNS,
    OCP_STORAGE_USAGE: OCP_STORAGE_COLUMNS,
    OCP_NODE_LABEL: OCP_NODE_LABEL_COLUMNS,
}


class OCPGenerator(AbstractGenerator):
    """Defines a abstract class for generators."""

    TEMPLATE = "ocp.j2"

    # Keyword args passed to TEMPLATE at render time.
    TEMPLATE_KWARGS = {"start_date": None, "end_date": None, "nodes": []}

    def __init__(self, start_date, end_date, user_config=None):
        """Initialize the generator."""
        # initialize TEMPLATE_KWARGS values
        self._gen_nodes()

        # super() renders the TEMPLATE
        super().__init__(start_date, end_date, user_config=user_config)

        self.nodes = [node for conf in self.config for node in conf.get("nodes")]

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
        }

    def _format_config(self, config):
        # no-op because OCP static file has no special cases
        return config

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not (in_date and isinstance(in_date, datetime.datetime)):
            raise ValueError("in_date must be a date object.")
        return in_date.strftime("%Y-%m-%d %H:%M:%S +0000 UTC")

    def _gen_nodes(self):
        """Create nodes for report."""
        nodes = []
        for _ in range(0, self.fake.pyint(2, 6)):
            node = {
                "node_name": "node_" + self.fake.word(),
                "cpu_cores": self.fake.pyint(2, 16),
                "memory_gig": self.fake.pyint(16, 256),
                "resource_id": "i-" + self.fake.ean8(),
                "namespaces": [],
                "labels": self._gen_openshift_labels(),
            }
            nodes.append(node)

        for idx, node in enumerate(nodes):
            nodes[idx]["namespaces"] = self._gen_namespaces(node)

        self.TEMPLATE_KWARGS["nodes"] = nodes

    def _gen_namespaces(self, node):
        """Create namespaces on specific nodes and keep relationship."""
        namespaces = []
        names = ["ns_" + self.fake.word() for _ in range(0, self.fake.pyint(1, 4))]
        for name in names:
            pods = self._gen_pods(node, name)
            namespace = {"namespace_name": name, "pods": pods, "volumes": self._gen_volumes(pods)}
            namespaces.append(namespace)
        return namespaces

    def _gen_openshift_labels(self, seeding=None):
        """Create pod labels for output data."""
        self.apps = [self.fake.word() for _ in range(0, self.fake.pyint(3, 6))]
        self.organizations = [self.fake.word() for _ in range(0, self.fake.pyint(3, 6))]
        self.markets = [self.fake.word() for _ in range(0, self.fake.pyint(3, 6))]
        self.versions = [self.fake.word() for _ in range(0, self.fake.pyint(3, 6))]
        seeded_labels = {
            "environment": ["dev", "ci", "qa", "stage", "prod"],
            "app": self.apps,
            "organization": self.organizations,
            "market": self.markets,
            "version": self.versions,
        }
        if seeding:
            seeded_labels = seeding
        gen_label_keys = [self.fake.word() for _ in range(0, self.fake.pyint(3, 6))]
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

    def _gen_pods(self, node, namespace):
        """Create pods on specific namespaces and keep relationship."""
        pods = []
        cpu_used = 0
        mem_used = 0
        for _ in range(0, self.fake.pyint(2, 5)):
            cpu_cores = node.get("cpu_cores")
            if cpu_used >= cpu_cores * 0.95:
                break

            memory_gig = node.get("memory_gig")
            if mem_used >= memory_gig * 0.95:
                break

            pod_name = "pod_" + self.fake.word()

            cpu_request = round(uniform(0.02, cpu_cores), 5)
            cpu_limit = round(uniform(cpu_request, cpu_cores), 5)
            pod_cpu_usage = round(uniform(0.02, cpu_limit), 5)
            cpu_usage = {"full_period": pod_cpu_usage}
            cpu_used += pod_cpu_usage

            mem_request_gig = round(uniform(1, memory_gig), 2)
            mem_limit_gig = round(uniform(mem_request_gig, memory_gig), 2)
            pod_mem_usage = round(uniform(1, mem_limit_gig), 2)
            mem_usage_gig = {"full_period": pod_mem_usage}
            mem_used += pod_mem_usage

            pods.append(
                {
                    "namespace": namespace,
                    "node": node.get("node_name"),
                    "resource_id": node.get("resource_id"),
                    "pod_name": pod_name,
                    "node_capacity_cpu_cores": cpu_cores,
                    "node_capacity_cpu_core_seconds": cpu_cores * HOUR,
                    "node_capacity_memory_bytes": memory_gig * GIGABYTE,
                    "node_capacity_memory_byte_seconds": memory_gig * GIGABYTE * HOUR,
                    "cpu_request": cpu_request,
                    "cpu_limit": cpu_limit,
                    "mem_request_gig": mem_request_gig,
                    "mem_limit_gig": mem_limit_gig,
                    "labels": self._gen_openshift_labels(),
                    "cpu_usage": cpu_usage,
                    "mem_usage_gig": mem_usage_gig,
                    "pod_seconds": self.fake.pyint(0, 3600),
                }
            )
        return pods

    def _gen_volumes(self, pods):
        """Create volumes on specific namespaces and keep relationship."""
        volumes = []
        for _ in range(0, len(pods)):
            volume_name = "vol_" + self.fake.word()
            volume_request_gig = self.fake.pyint(20, 100)
            volume_request = volume_request_gig * GIGABYTE
            volume_claims = []
            total_claims = 0
            for _ in range(0, len(pods)):
                if volume_request - total_claims <= GIGABYTE:
                    break
                volume_claim_name = "vc_" + self.fake.word()
                pod = choice(pods)
                claim_capacity = min(
                    self.fake.pyint(20, 100) * GIGABYTE, (volume_request_gig * GIGABYTE - total_claims)
                )
                volume_claims.append(
                    {
                        "namespace": pod.get("namespace"),
                        "volume_claim_name": volume_claim_name,
                        "labels": self._gen_openshift_labels(),
                        "capacity_gig": claim_capacity / GIGABYTE,
                        "pod_name": pod.get("pod_name"),
                        "volume_claim_usage_gig": {"full_period": self.fake.pyint(1, claim_capacity) / GIGABYTE},
                    }
                )
                total_claims += claim_capacity
            volumes.append(
                {
                    "namespace": pod.get("namespace"),
                    "volume_name": volume_name,
                    "storage_class": choice(("gp2", "fast", "slow", "gold")),
                    "volume_request_gig": volume_request_gig,
                    "labels": self._gen_openshift_labels(),
                    "volume_claims": volume_claims,
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
        row = self._add_common_usage_info({}, start, end)
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
        del kwargs["report_type"]
        pod = kwargs.pop("pod")

        pod_seconds = kwargs.pop("pod_seconds")

        cpu_request = pod.get("cpu_request")
        mem_request_gig = pod.get("mem_request_gig")

        cpu_limit = min(pod.get("cpu_limit"), cpu_request)
        mem_limit_gig = min(pod.get("mem_limit_gig"), mem_request_gig)

        cpu_usage = self._get_usage_for_date(kwargs.pop("cpu_usage"), start)
        cpu = round(uniform(0.02, cpu_limit), 5)
        if cpu_usage:
            cpu = min(cpu_limit, cpu_request, cpu_usage)

        mem_usage_gig = self._get_usage_for_date(kwargs.pop("mem_usage_gig"), start)
        mem = round(uniform(1, mem_limit_gig), 2)
        if mem_usage_gig:
            mem = min(mem_limit_gig, mem_request_gig, mem_usage_gig)

        kwargs["pod"] = pod.get("pod_name")
        kwargs["pod_usage_cpu_core_seconds"] = pod_seconds * cpu
        kwargs["pod_request_cpu_core_seconds"] = pod_seconds * cpu_request
        kwargs["pod_limit_cpu_core_seconds"] = pod_seconds * cpu_limit
        kwargs["pod_usage_memory_byte_seconds"] = pod_seconds * mem * GIGABYTE
        kwargs["pod_request_memory_byte_seconds"] = pod_seconds * mem_request_gig * GIGABYTE
        kwargs["pod_limit_memory_byte_seconds"] = pod_seconds * mem_limit_gig * GIGABYTE
        kwargs["interval_start"] = start
        kwargs["interval_end"] = end
        row.update(kwargs)
        return row

    def _update_storage_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        volume_claim_usage_gig = self._get_usage_for_date(kwargs.get("volume_claim_usage_gig"), start)

        volume_request = kwargs.get("volume_request")
        vc_capacity_gig = min(kwargs.get("vc_capacity", 10.0), volume_request)

        vc_usage_gig = round(uniform(2.0, vc_capacity_gig), 2)
        if volume_claim_usage_gig:
            vc_usage_gig = min(volume_claim_usage_gig, vc_capacity_gig)
        vc_usage = vc_usage_gig * GIGABYTE

        data = {
            "interval_start": start,
            "interval_end": end,
            "namespace": kwargs.get("namespace"),
            "pod": kwargs.get("pod"),
            "persistentvolumeclaim": kwargs.get("volume_claim"),
            "persistentvolume": kwargs.get("volume_name"),
            "storageclass": kwargs.get("storage_class"),
            "persistentvolumeclaim_capacity_bytes": kwargs.get("vc_capacity"),
            "persistentvolumeclaim_capacity_byte_seconds": vc_capacity_gig * HOUR,
            "volume_request_storage_byte_seconds": volume_request * HOUR,
            "persistentvolume_labels": kwargs.get("volume_labels"),
            "persistentvolumeclaim_labels": kwargs.get("volume_claim_labels"),
            "persistentvolumeclaim_usage_byte_seconds": vc_usage * HOUR,
        }
        row.update(data)
        return row

    def _update_node_label_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        data = {
            "node": kwargs.get("node"),
            "node_labels": kwargs.get("node_labels"),
            "interval_start": start,
            "interval_end": end,
        }
        row.update(data)
        return row

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        report_type = kwargs.get(REPORT_TYPE)
        method = self.ocp_report_generation.get(report_type).get("_update_data")
        row = method(row, start, end, **kwargs)
        return row

    def _gen_hourly_pods_usage(self, **kwargs):
        """Create hourly data for pod usage."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            for node in self.nodes:
                for namespace in node.get("namespaces"):
                    name = namespace.get("namespace_name")
                    for pod in namespace.get("pods"):
                        cpu_usage = pod.get("cpu_usage", None)
                        mem_usage_gig = pod.get("mem_usage_gig", None)
                        pod_seconds = pod.get("pod_seconds", None)
                        row = self._init_data_row(start, end, **kwargs)
                        row = self._update_data(
                            row,
                            start,
                            end,
                            pod=deepcopy(pod),
                            cpu_usage=cpu_usage,
                            mem_usage_gig=mem_usage_gig,
                            pod_seconds=pod_seconds,
                            namespace=name,
                            node=node.get("node_name"),
                            resource_id=node.get("resource_id"),
                            node_capacity_cpu_cores=node.get("cpu_cores"),
                            node_capacity_cpu_core_seconds=node.get("cpu_cores") * 3600,
                            node_capacity_memory_bytes=node.get("memory_gig") * GIGABYTE,
                            node_capacity_memory_byte_seconds=node.get("memory_gig") * GIGABYTE,
                            pod_labels=pod.get("labels"),
                            **kwargs,
                        )
                        row.pop("cpu_usage", None)
                        row.pop("mem_usage_gig", None)
                        row.pop("pod_seconds", None)
                        yield row

    def _gen_hourly_storage_usage(self, **kwargs):
        """Create hourly data for storage usage."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            for node in self.nodes:
                for namespace in node.get("namespaces"):
                    name = namespace.get("namespace_name")
                    for volume in namespace.get("volumes"):
                        for volume_claim in volume.get("volume_claims"):
                            row = self._init_data_row(start, end, **kwargs)
                            row = self._update_data(
                                row,
                                start,
                                end,
                                volume_claim=volume_claim.get("volume_claim_name"),
                                pod=volume_claim.get("pod_name"),
                                volume_claim_labels=volume_claim.get("labels"),
                                vc_capacity=volume_claim.get("capacity_gig"),
                                volume_claim_usage_gig=volume_claim.get("volume_claim_usage_gig"),
                                storage_class=volume.get("storage_class"),
                                volume_name=volume.get("volume_name"),
                                volume_request=volume.get("volume_request_gig"),
                                volume_labels=volume.get("labels"),
                                namespace=name,
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
                    row, start, end, node_labels=node.get("labels"), node=node.get("node_name"), **kwargs
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
