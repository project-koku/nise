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
from random import choice, choices, randint, uniform
from string import ascii_lowercase

from dateutil import parser

from nise.generators.generator import (AbstractGenerator,
                                       REPORT_TYPE)


OCP_POD_USAGE = 'ocp_pod_usage'
OCP_STORAGE_USAGE = 'ocp_storage_usage'
OCP_POD_USAGE_COLUMNS = ('report_period_start', 'report_period_end', 'pod', 'namespace',
                         'node', 'resource_id', 'interval_start', 'interval_end',
                         'pod_usage_cpu_core_seconds', 'pod_request_cpu_core_seconds',
                         'pod_limit_cpu_core_seconds', 'pod_usage_memory_byte_seconds',
                         'pod_request_memory_byte_seconds', 'pod_limit_memory_byte_seconds',
                         'node_capacity_cpu_cores', 'node_capacity_cpu_core_seconds',
                         'node_capacity_memory_bytes', 'node_capacity_memory_byte_seconds',
                         'pod_labels')
OCP_STORAGE_COLUMNS = ('report_period_start', 'report_period_end', 'interval_start', 'interval_end',
                       'namespace', 'pod', 'persistentvolumeclaim', 'persistentvolume',
                       'storageclass', 'persistentvolumeclaim_capacity_bytes',
                       'persistentvolumeclaim_capacity_byte_seconds',
                       'volume_request_storage_byte_seconds',
                       'persistentvolumeclaim_usage_byte_seconds', 'persistentvolume_labels',
                       'persistentvolumeclaim_labels')
OCP_REPORT_TYPE_TO_COLS = {
    OCP_POD_USAGE: OCP_POD_USAGE_COLUMNS,
    OCP_STORAGE_USAGE: OCP_STORAGE_COLUMNS
}


# pylint: disable=too-few-public-methods, too-many-instance-attributes
class OCPGenerator(AbstractGenerator):
    """Defines a abstract class for generators."""

    def __init__(self, start_date, end_date, attributes):
        """Initialize the generator."""
        self._nodes = None
        if attributes:
            self._nodes = attributes.get('nodes')

        super().__init__(start_date, end_date)
        self.apps = [self.fake.word(), self.fake.word(), self.fake.word(),  # pylint: disable=no-member
                     self.fake.word(), self.fake.word(), self.fake.word()]  # pylint: disable=no-member
        self.organizations = [self.fake.word(), self.fake.word(),  # pylint: disable=no-member
                              self.fake.word(), self.fake.word()]  # pylint: disable=no-member
        self.markets = [self.fake.word(), self.fake.word(), self.fake.word(),  # pylint: disable=no-member
                        self.fake.word(), self.fake.word(), self.fake.word()]  # pylint: disable=no-member
        self.versions = [self.fake.word(), self.fake.word(), self.fake.word(),  # pylint: disable=no-member
                         self.fake.word(), self.fake.word(), self.fake.word()]  # pylint: disable=no-member
        self.nodes = self._gen_nodes()
        self.namespaces = self._gen_namespaces(self.nodes)
        self.pods, self.namespace2pods = self._gen_pods(self.namespaces)
        self.volumes = self._gen_volumes(self.namespaces, self.namespace2pods)
        self.ocp_report_generation = {
            OCP_POD_USAGE: {
                '_generate_hourly_data': self._gen_hourly_pods_usage,
                '_update_data': self._update_pod_data
            },
            OCP_STORAGE_USAGE: {
                '_generate_hourly_data': self._gen_hourly_storage_usage,
                '_update_data': self._update_storage_data
            }
        }

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not in_date or not isinstance(in_date, datetime.datetime):
            raise ValueError('in_date must be a date object.')
        return in_date.strftime('%Y-%m-%d %H:%M:%S +0000 UTC')

    def _gen_nodes(self):
        """Create nodes for report."""
        nodes = []
        if self._nodes:
            for item in self._nodes:
                memory_gig = item.get('memory_gig', randint(2, 8))
                memory_bytes = memory_gig * 1024 * 1024 * 1024
                resource_id = str(item.get('resource_id', self.fake.word()))  # pylint: disable=no-member
                node = {'name': item.get('node_name', 'node_' + self.fake.word()),  # pylint: disable=no-member
                        'cpu_cores': item.get('cpu_cores', randint(2, 16)),
                        'memory_bytes': memory_bytes,
                        'resource_id': 'i-' + resource_id,
                        'namespaces': item.get('namespaces')}
                nodes.append(node)
        else:
            num_nodes = randint(2, 6)
            for node_num in range(0, num_nodes):  # pylint: disable=W0612
                memory_gig = randint(2, 8)
                memory_bytes = memory_gig * 1024 * 1024 * 1024
                node = {'name': 'node_' + self.fake.word(),  # pylint: disable=no-member
                        'cpu_cores': randint(2, 16),
                        'memory_bytes': memory_bytes,
                        'resource_id': 'i-' + self.fake.word()}  # pylint: disable=no-member
                nodes.append(node)
        return nodes

    def _gen_namespaces(self, nodes):
        """Create namespaces on specific nodes and keep relationship."""
        namespaces = {}
        for node in nodes:
            if node.get('namespaces'):
                for name, _ in node.get('namespaces').items():
                    namespace = name
                    namespaces[namespace] = node
            else:
                num_namespaces = randint(2, 12)
                for num_namespace in range(0, num_namespaces):  # pylint: disable=W0612
                    namespace_suffix = choice(('ci', 'qa', 'prod', 'proj', 'dev', 'staging'))
                    namespace = self.fake.word() + '_' + namespace_suffix  # pylint: disable=no-member
                    namespaces[namespace] = node
        return namespaces

    def _gen_pod_labels(self):
        """Create pod labels for output data."""
        seeded_labels = {'environment': ['dev', 'ci', 'qa', 'stage', 'prod'],
                         'app': self.apps,
                         'organization': self.organizations,
                         'market': self.markets,
                         'version': self.versions
                         }
        gen_label_keys = [self.fake.word(), self.fake.word(), self.fake.word(),  # pylint: disable=no-member
                          self.fake.word(), self.fake.word(), self.fake.word()]  # pylint: disable=no-member
        all_label_keys = list(seeded_labels.keys()) + gen_label_keys
        num_labels = randint(2, len(all_label_keys))
        chosen_label_keys = choices(all_label_keys, k=num_labels)

        labels = {}
        for label_key in chosen_label_keys:
            label_value = self.fake.word()  # pylint: disable=no-member
            if label_key in seeded_labels:
                label_value = choice(seeded_labels[label_key])
            labels['label_{}'.format(label_key)] = label_value

        label_str = ''
        for key, value in labels.items():
            label_data = '{}:{}'.format(key, value)
            if label_str == '':
                label_str += label_data
            else:
                label_str += '|{}'.format(label_data)
        return label_str

    def _gen_pods(self, namespaces):  # pylint: disable=too-many-locals
        """Create pods on specific namespaces and keep relationship."""
        pods = {}
        namespace2pod = {}
        hour = 60 * 60
        for namespace, node in namespaces.items():
            namespace2pod[namespace] = []
            if node.get('namespaces'):
                specified_pods = node.get('namespaces').get(namespace).get('pods')
                for specified_pod in specified_pods:
                    pod = specified_pod.get('pod_name', self.fake.word())  # pylint: disable=no-member
                    namespace2pod[namespace].append(pod)
                    cpu_cores = node.get('cpu_cores')
                    memory_bytes = node.get('memory_bytes')
                    cpu_request = specified_pod.get('cpu_request',
                                                    round(uniform(0.02, 1.0), 5))
                    mem_request_gig = specified_pod.get('mem_request_gig',
                                                        round(uniform(25.0, 80.0), 2))
                    pods[pod] = {'namespace': namespace,
                                 'node': node.get('name'),
                                 'resource_id': node.get('resource_id'),
                                 'pod': pod,
                                 'node_capacity_cpu_cores': cpu_cores,
                                 'node_capacity_cpu_core_seconds': cpu_cores * hour,
                                 'node_capacity_memory_bytes': memory_bytes,
                                 'node_capacity_memory_byte_seconds': memory_bytes * hour,
                                 'cpu_request': cpu_request,
                                 'cpu_limit': specified_pod.get('cpu_limit',
                                                                round(uniform(cpu_request, 1.0),
                                                                      5)),
                                 'mem_request_gig': mem_request_gig,
                                 'mem_limit_gig': specified_pod.get('mem_limit_gig',
                                                                    round(uniform(mem_request_gig,
                                                                                  80.0), 2)),
                                 'pod_labels': specified_pod.get('labels', None),
                                 'cpu_usage': specified_pod.get('cpu_usage'),
                                 'mem_usage_gig': specified_pod.get('mem_usage_gig'),
                                 'pod_seconds': specified_pod.get('pod_seconds')}
            else:
                num_pods = randint(2, 20)
                for num_namespace in range(0, num_pods):  # pylint: disable=W0612
                    pod_suffix = ''.join(choices(ascii_lowercase, k=5))
                    pod_type = choice(('build', 'deploy', pod_suffix))
                    pod = self.fake.word() + '_' + pod_type  # pylint: disable=no-member
                    namespace2pod[namespace].append(pod)
                    cpu_cores = node.get('cpu_cores')
                    memory_bytes = node.get('memory_bytes')
                    cpu_request = round(uniform(0.02, 1.0), 5)
                    mem_request_gig = round(uniform(25.0, 80.0), 2)
                    pods[pod] = {'namespace': namespace,
                                 'node': node.get('name'),
                                 'resource_id': node.get('resource_id'),
                                 'pod': pod,
                                 'node_capacity_cpu_cores': cpu_cores,
                                 'node_capacity_cpu_core_seconds': cpu_cores * hour,
                                 'node_capacity_memory_bytes': memory_bytes,
                                 'node_capacity_memory_byte_seconds': memory_bytes * hour,
                                 'cpu_request': cpu_request,
                                 'cpu_limit': round(uniform(cpu_request, 1.0), 5),
                                 'mem_request_gig': mem_request_gig,
                                 'mem_limit_gig': round(uniform(mem_request_gig, 80.0), 2),
                                 'pod_labels': self._gen_pod_labels()}
        return pods, namespace2pod

    def _gen_volumes(self, namespaces, namespace2pods):  # pylint: disable=R0914
        """Create volumes on specific namespaces and keep relationship."""
        volumes = {}
        for namespace, node in namespaces.items():
            storage_class_default = choice(('gp2', 'fast', 'slow', 'gold'))
            if node.get('namespaces'):
                specified_volumes = node.get('namespaces').get(namespace).get('volumes', [])
                for specified_volume in specified_volumes:
                    volume = specified_volume.get('volume_name', self.fake.word())  # pylint: disable=no-member
                    volume_request = (specified_volume.get('volume_request_gig')
                                      * 1024 * 1024 * 1024)  # noqa: W503
                    specified_vol_claims = specified_volume.get('volume_claims', [])
                    volume_claims = {}
                    for specified_vc in specified_vol_claims:
                        vol_claim = specified_vc.get(
                            'volume_claim_name', self.fake.word())  # pylint: disable=no-member
                        pod = specified_vc.get('pod_name')
                        claim_capacity = (specified_vc.get('capacity_gig') * 1024 * 1024 * 1024)
                        usage_gig = specified_vc.get('volume_claim_usage_gig')
                        volume_claims[vol_claim] = {
                            'namespace': namespace,
                            'volume': volume,
                            'labels': specified_vc.get('labels', None),
                            'capacity': claim_capacity,
                            'pod': pod,
                            'volume_claim_usage_gig': usage_gig,
                        }
                    volumes[volume] = {
                        'namespace': namespace,
                        'volume': volume,
                        'storage_class': specified_volume.get('storage_class',
                                                              storage_class_default),
                        'volume_request': volume_request,
                        'labels': specified_volume.get('labels', None),
                        'volume_claims': volume_claims
                    }
            else:
                num_volumes = randint(1, 3)
                num_vol_claims = randint(1, 2)
                for num_volume in range(0, num_volumes):  # pylint: disable=W0612
                    vol_suffix = ''.join(choices(ascii_lowercase, k=10))
                    volume = 'pvc' + '-' + vol_suffix
                    vol_request_gig = round(uniform(25.0, 80.0), 2)
                    vol_request = vol_request_gig * 1024 * 1024 * 1024
                    volume_claims = {}
                    for num_claim in range(0, num_vol_claims):  # pylint: disable=W0612
                        vol_claim = self.fake.word()  # pylint: disable=no-member
                        pod = choice(namespace2pods[namespace])
                        claim_capacity = (round(uniform(1.0, vol_request_gig), 2)
                                          * 1024 * 1024 * 1024)  # noqa: W503
                        volume_claims[vol_claim] = {
                            'namespace': namespace,
                            'volume': volume,
                            'labels': self._gen_pod_labels(),
                            'capacity': claim_capacity,
                            'pod': pod,
                        }
                    volumes[volume] = {
                        'namespace': namespace,
                        'volume': volume,
                        'storage_class': choice(('gp2', 'fast', 'slow', 'gold')),
                        'volume_request': vol_request,
                        'labels': self._gen_pod_labels(),
                        'volume_claims': volume_claims
                    }
        return volumes

    def _init_data_row(self, start, end, **kwargs):  # noqa: C901
        """Create a row of data with placeholder for all headers."""
        if not start or not end:
            raise ValueError('start and end must be date objects.')
        if not isinstance(start, datetime.datetime):
            raise ValueError('start must be a date object.')
        if not isinstance(end, datetime.datetime):
            raise ValueError('end must be a date object.')

        bill_begin = start.replace(microsecond=0, second=0, minute=0, hour=0, day=1)
        bill_end = AbstractGenerator.next_month(bill_begin)
        row = {}
        report_type = kwargs.get(REPORT_TYPE)
        for column in OCP_REPORT_TYPE_TO_COLS[report_type]:
            row[column] = ''
            if column == 'report_period_start':
                row[column] = OCPGenerator.timestamp(bill_begin)
            elif column == 'report_period_end':
                row[column] = OCPGenerator.timestamp(bill_end)
        return row

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Add common usage information."""
        row['interval_start'] = OCPGenerator.timestamp(start)
        row['interval_end'] = OCPGenerator.timestamp(end)
        return row

    @staticmethod
    def _get_usage_for_date(usage_dict, start):
        """Return usage for specified hour."""
        usage_amount = None
        if usage_dict:
            for date, usage in usage_dict.items():
                if date == 'full_period':
                    usage_amount = usage
                elif parser.parse(date).date() == start.date():
                    usage_amount = usage
        return usage_amount

    def _update_pod_data(self, row, start, end, **kwargs):  # pylint: disable=R0914, W0613
        """Update data with generator specific data."""
        cpu_usage = self._get_usage_for_date(kwargs.get('cpu_usage'), start)
        mem_usage_gig = self._get_usage_for_date(kwargs.get('mem_usage_gig'), start)
        user_pod_seconds = kwargs.get('pod_seconds')
        pod_seconds = user_pod_seconds if user_pod_seconds else randint(2, 60 * 60)
        pod = kwargs.get('pod')
        cpu_request = pod.pop('cpu_request')
        mem_request_gig = pod.pop('mem_request_gig')
        cpu_limit = pod.pop('cpu_limit')
        mem_limit_gig = pod.pop('mem_limit_gig')
        cpu = cpu_usage if cpu_usage else round(uniform(0.02, cpu_request), 5)
        mem = mem_usage_gig if mem_usage_gig else round(uniform(1, mem_request_gig), 2)
        pod['pod_usage_cpu_core_seconds'] = pod_seconds * cpu
        pod['pod_request_cpu_core_seconds'] = pod_seconds * cpu_request
        pod['pod_limit_cpu_core_seconds'] = pod_seconds * cpu_limit
        pod['pod_usage_memory_byte_seconds'] = pod_seconds * mem * 1024 * 1024 * 1024
        pod['pod_request_memory_byte_seconds'] = pod_seconds * mem_request_gig * 1024 * 1024 * 1024
        pod['pod_limit_memory_byte_seconds'] = pod_seconds * mem_limit_gig * 1024 * 1024 * 1024
        row.update(pod)
        return row

    def _update_storage_data(self, row, start, end, **kwargs):  # pylint: disable=R0914, W0613
        """Update data with generator specific data."""
        volume_claim_usage_gig = self._get_usage_for_date(
            kwargs.get('volume_claim_usage_gig'), start)
        vc_capacity_gig = 10.0
        if kwargs.get('vc_capacity'):
            vc_capacity_gig = kwargs.get('vc_capacity') / 1024 / 1024 / 1024
        vc_usage_gig = volume_claim_usage_gig if volume_claim_usage_gig \
            else round(uniform(2.0, vc_capacity_gig), 2)
        vc_usage = vc_usage_gig * 1024 * 1024 * 1024
        data = {
            'namespace': kwargs.get('namespace'),
            'pod': kwargs.get('pod'),
            'persistentvolumeclaim': kwargs.get('volume_claim'),
            'persistentvolume': kwargs.get('volume_name'),
            'storageclass': kwargs.get('storage_class'),
            'persistentvolumeclaim_capacity_bytes': kwargs.get('vc_capacity'),
            'persistentvolumeclaim_capacity_byte_seconds': kwargs.get('vc_capacity') * 60 * 60,
            'volume_request_storage_byte_seconds': kwargs.get('volume_request') * 60 * 60,
            'persistentvolume_labels': kwargs.get('volume_labels'),
            'persistentvolumeclaim_labels': kwargs.get('volume_claim_labels'),
            'persistentvolumeclaim_usage_byte_seconds': vc_usage * 60 * 60
        }
        row.update(data)
        return row

    def _update_data(self, row, start, end, **kwargs):  # pylint: disable=R0914
        """Update data with generator specific data."""
        row = self._add_common_usage_info(row, start, end)
        if kwargs.get(REPORT_TYPE):
            report_type = kwargs.get(REPORT_TYPE)
            method = self.ocp_report_generation.get(report_type).get('_update_data')
            row = method(row, start, end, **kwargs)
        return row

    def _gen_hourly_pods_usage(self, **kwargs):  # pylint: disable=R0914
        """Create hourly data for pod usage."""
        data = []
        for hour in self.hours:
            start = hour.get('start')
            end = hour.get('end')
            pod_count = len(self.pods)
            if self._nodes:
                for pod_name, _ in self.pods.items():
                    cpu_usage = self.pods[pod_name].get('cpu_usage', None)
                    mem_usage_gig = self.pods[pod_name].get('mem_usage_gig', None)
                    pod_seconds = self.pods[pod_name].get('pod_seconds', None)
                    pod = deepcopy(self.pods[pod_name])
                    row = self._init_data_row(start, end, **kwargs)
                    row = self._update_data(row, start, end, pod=pod, cpu_usage=cpu_usage,
                                            mem_usage_gig=mem_usage_gig, pod_seconds=pod_seconds,
                                            **kwargs)
                    row.pop('cpu_usage', None)
                    row.pop('mem_usage_gig', None)
                    row.pop('pod_seconds', None)
                    data.append(row)
            else:
                num_pods = randint(2, pod_count)
                pod_index_list = range(pod_count)
                pod_choices = list(set(choices(pod_index_list, k=num_pods)))
                pod_keys = list(self.pods.keys())
                for pod_choice in pod_choices:
                    pod_name = pod_keys[pod_choice]
                    pod = deepcopy(self.pods[pod_name])
                    row = self._init_data_row(start, end, **kwargs)
                    row = self._update_data(row, start, end, pod=pod, **kwargs)
                    data.append(row)
        return data

    def _gen_hourly_storage_usage(self, **kwargs):  # pylint: disable=R0914
        """Create hourly data for storage usage."""
        data = []
        for hour in self.hours:
            start = hour.get('start')
            end = hour.get('end')
            for volume_name, volume in self.volumes.items():
                namespace = volume.get('namespace', None)
                storage_class = volume.get('storage_class', None)
                volume_request = volume.get('volume_request', None)
                vol_labels = volume.get('labels', None)
                volume_claims = volume.get('volume_claims', [])
                for vc_name, volume_claim in volume_claims.items():
                    pod = volume_claim.get('pod')
                    vc_labels = volume_claim.get('labels')
                    capacity = volume_claim.get('capacity')
                    volume_claim_usage_gig = volume_claim.get('volume_claim_usage_gig', None)
                    row = self._init_data_row(start, end, **kwargs)
                    row = self._update_data(row, start, end, volume_claim=vc_name,
                                            pod=pod, volume_claim_labels=vc_labels,
                                            vc_capacity=capacity,
                                            volume_claim_usage_gig=volume_claim_usage_gig,
                                            storage_class=storage_class, volume_name=volume_name,
                                            volume_request=volume_request, volume_labels=vol_labels,
                                            namespace=namespace, **kwargs)
                    data.append(row)
        return data

    def _generate_hourly_data(self, **kwargs):   # pylint: disable=too-many-locals
        """Create hourly data."""
        data = []
        if kwargs:
            report_type = kwargs.get(REPORT_TYPE)
            method = self.ocp_report_generation.get(report_type).get('_generate_hourly_data')
            data = method(**kwargs)
        return data

    def generate_data(self):
        """Responsibile for generating data."""
        data = {}
        for report_type in self.ocp_report_generation.keys():  # pylint: disable=C0201
            meta = {REPORT_TYPE: report_type}
            data[report_type] = self._generate_hourly_data(**meta)
        return data
