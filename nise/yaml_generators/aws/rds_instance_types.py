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
"""Select RDS instance types.

Information gleened from https://www.ec2instances.info/

"""

INSTANCE_TYPES = [
    {
        "family": "General Purpose",
        "inst_type": "db.m4.10xlarge",
        "memory": "160 GiB",
        "storage": "EBS-Only",
        "vcpu": "40",
        "processor_arch": "64-bit",
        "cost": "3.654000",
        "rate": "3.654000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m4.16xlarge",
        "memory": "256 GiB",
        "storage": "EBS-Only",
        "vcpu": "64",
        "processor_arch": "64-bit",
        "cost": "5.844000",
        "rate": "5.844000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m4.2xlarge",
        "memory": "32 GiB",
        "storage": "EBS-Only",
        "vcpu": "8",
        "processor_arch": "64-bit",
        "cost": "0.730000",
        "rate": "0.730000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m4.4xlarge",
        "memory": "64 GiB",
        "storage": "EBS-Only",
        "vcpu": "16",
        "processor_arch": "64-bit",
        "cost": "1.461000",
        "rate": "1.461000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m4.large",
        "memory": "8 GiB",
        "storage": "EBS-Only",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.182000",
        "rate": "0.182000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m4.xlarge",
        "memory": "16 GiB",
        "storage": "EBS-Only",
        "vcpu": "4",
        "processor_arch": "64-bit",
        "cost": "0.365000",
        "rate": "0.365000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m5.12xlarge",
        "memory": "192 GiB",
        "storage": "EBS-Only",
        "vcpu": "48",
        "processor_arch": "64-bit",
        "cost": "1.968000",
        "rate": "1.968000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m5.24xlarge",
        "memory": "384 GiB",
        "storage": "EBS-Only",
        "vcpu": "96",
        "processor_arch": "64-bit",
        "cost": "8.544000",
        "rate": "8.544000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m5.2xlarge",
        "memory": "32 GiB",
        "storage": "EBS-Only",
        "vcpu": "8",
        "processor_arch": "64-bit",
        "cost": "0.712000",
        "rate": "0.712000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m5.4xlarge",
        "memory": "64 GiB",
        "storage": "EBS-Only",
        "vcpu": "16",
        "processor_arch": "64-bit",
        "cost": "0.656000",
        "rate": "0.656000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m5.large",
        "memory": "8 GiB",
        "storage": "EBS-Only",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.178000",
        "rate": "0.178000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.m5.xlarge",
        "memory": "16 GiB",
        "storage": "EBS-Only",
        "vcpu": "4",
        "processor_arch": "64-bit",
        "cost": "0.164000",
        "rate": "0.164000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r4.16xlarge",
        "memory": "488 GiB",
        "storage": "EBS-Only",
        "vcpu": "64",
        "processor_arch": "64-bit",
        "cost": "8.000000",
        "rate": "8.000000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r4.2xlarge",
        "memory": "61 GiB",
        "storage": "EBS-Only",
        "vcpu": "8",
        "processor_arch": "64-bit",
        "cost": "1.000000",
        "rate": "1.000000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r4.4xlarge",
        "memory": "122 GiB",
        "storage": "EBS-Only",
        "vcpu": "16",
        "processor_arch": "64-bit",
        "cost": "2.000000",
        "rate": "2.000000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r4.8xlarge",
        "memory": "244 GiB",
        "storage": "EBS-Only",
        "vcpu": "32",
        "processor_arch": "64-bit",
        "cost": "4.000000",
        "rate": "4.000000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r4.large",
        "memory": "15.25 GiB",
        "storage": "EBS-Only",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.250000",
        "rate": "0.250000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r4.xlarge",
        "memory": "30.5 GiB",
        "storage": "EBS-Only",
        "vcpu": "4",
        "processor_arch": "64-bit",
        "cost": "0.500000",
        "rate": "0.500000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r5.12xlarge",
        "memory": "384 GiB",
        "storage": "EBS-Only",
        "vcpu": "48",
        "processor_arch": "64-bit",
        "cost": "2.976000",
        "rate": "2.976000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r5.24xlarge",
        "memory": "768 GiB",
        "storage": "EBS-Only",
        "vcpu": "96",
        "processor_arch": "64-bit",
        "cost": "12.000000",
        "rate": "12.000000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r5.2xlarge",
        "memory": "64 GiB",
        "storage": "EBS-Only",
        "vcpu": "8",
        "processor_arch": "64-bit",
        "cost": "0.496000",
        "rate": "0.496000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r5.4xlarge",
        "memory": "192 GiB",
        "storage": "EBS-Only",
        "vcpu": "16",
        "processor_arch": "64-bit",
        "cost": "0.992000",
        "rate": "0.992000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r5.large",
        "memory": "16 GiB",
        "storage": "EBS-Only",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.250000",
        "rate": "0.250000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.r5.xlarge",
        "memory": "32 GiB",
        "storage": "EBS-Only",
        "vcpu": "4",
        "processor_arch": "64-bit",
        "cost": "0.500000",
        "rate": "0.500000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t2.2xlarge",
        "memory": "32 GiB",
        "storage": "EBS-Only",
        "vcpu": "8",
        "processor_arch": "64-bit",
        "cost": "0.580000",
        "rate": "0.580000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t2.large",
        "memory": "8 GiB",
        "storage": "EBS-Only",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.145000",
        "rate": "0.145000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t2.medium",
        "memory": "4 GiB",
        "storage": "EBS-Only",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.073000",
        "rate": "0.073000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t2.micro",
        "memory": "1 GiB",
        "storage": "EBS-Only",
        "vcpu": "1",
        "processor_arch": "64-bit",
        "cost": "0.018000",
        "rate": "0.018000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t2.small",
        "memory": "2 GiB",
        "storage": "EBS-Only",
        "vcpu": "1",
        "processor_arch": "64-bit",
        "cost": "0.036000",
        "rate": "0.036000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t2.xlarge",
        "memory": "16 GiB",
        "storage": "EBS-Only",
        "vcpu": "4",
        "processor_arch": "64-bit",
        "cost": "0.290000",
        "rate": "0.290000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t3.2xlarge",
        "memory": "32 GiB",
        "storage": "EBS-Only",
        "vcpu": "8",
        "processor_arch": "64-bit",
        "cost": "0.579000",
        "rate": "0.579000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t3.large",
        "memory": "8 GiB",
        "storage": "EBS-Only",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.145000",
        "rate": "0.145000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t3.medium",
        "memory": "4 GiB",
        "storage": "EBS-Only",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.072000",
        "rate": "0.072000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t3.micro",
        "memory": "1 GiB",
        "storage": "EBS-Only",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.018000",
        "rate": "0.018000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t3.small",
        "memory": "2 GiB",
        "storage": "EBS-Only",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.036000",
        "rate": "0.036000",
    },
    {
        "family": "General Purpose",
        "inst_type": "db.t3.xlarge",
        "memory": "16 GiB",
        "storage": "EBS-Only",
        "vcpu": "4",
        "processor_arch": "64-bit",
        "cost": "0.290000",
        "rate": "0.290000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.x1.16xlarge",
        "memory": "976 GiB",
        "storage": "1 x 1920 SSD",
        "vcpu": "64",
        "processor_arch": "64-bit",
        "cost": "11.200000",
        "rate": "11.200000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.x1.32xlarge",
        "memory": "1952 GiB",
        "storage": "1 x 1920 SSD",
        "vcpu": "128",
        "processor_arch": "64-bit",
        "cost": "22.400000",
        "rate": "22.400000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.x1e.16xlarge",
        "memory": "1952 GiB",
        "storage": "1 x 1920 SSD",
        "vcpu": "64",
        "processor_arch": "64-bit",
        "cost": "22.417900",
        "rate": "22.417900",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.x1e.2xlarge",
        "memory": "244 GiB",
        "storage": "1 x 240 SSD",
        "vcpu": "8",
        "processor_arch": "64-bit",
        "cost": "2.802200",
        "rate": "2.802200",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.x1e.32xlarge",
        "memory": "3904 GiB",
        "storage": "2 x 1920 SSD",
        "vcpu": "128",
        "processor_arch": "64-bit",
        "cost": "44.835800",
        "rate": "44.835800",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.x1e.4xlarge",
        "memory": "488 GiB",
        "storage": "1 x 480 SSD",
        "vcpu": "16",
        "processor_arch": "64-bit",
        "cost": "5.604500",
        "rate": "5.604500",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.x1e.8xlarge",
        "memory": "976 GiB",
        "storage": "1 x 960 SSD",
        "vcpu": "32",
        "processor_arch": "64-bit",
        "cost": "11.209000",
        "rate": "11.209000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.x1e.xlarge",
        "memory": "122 GiB",
        "storage": "1 x 120 SSD",
        "vcpu": "4",
        "processor_arch": "64-bit",
        "cost": "1.401100",
        "rate": "1.401100",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.z1d.12xlarge",
        "memory": "384 GiB",
        "storage": "2 x 900 NVMe SSD",
        "vcpu": "48",
        "processor_arch": "64-bit",
        "cost": "8.208000",
        "rate": "8.208000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.z1d.2xlarge",
        "memory": "64 GiB",
        "storage": "1 x 300 NVMe SSD",
        "vcpu": "8",
        "processor_arch": "64-bit",
        "cost": "1.368000",
        "rate": "1.368000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.z1d.3xlarge",
        "memory": "96 GiB",
        "storage": "1 x 450 NVMe SSD",
        "vcpu": "12",
        "processor_arch": "64-bit",
        "cost": "2.052000",
        "rate": "2.052000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.z1d.6xlarge",
        "memory": "192 GiB",
        "storage": "1 x 900 NVMe SSD",
        "vcpu": "24",
        "processor_arch": "64-bit",
        "cost": "4.104000",
        "rate": "4.104000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.z1d.large",
        "memory": "16 GiB",
        "storage": "1 x 75 NVMe SSD",
        "vcpu": "2",
        "processor_arch": "64-bit",
        "cost": "0.342000",
        "rate": "0.342000",
    },
    {
        "family": "Memory Optimized",
        "inst_type": "db.z1d.xlarge",
        "memory": "32 GiB",
        "storage": "1 x 150 NVMe SSD",
        "vcpu": "4",
        "processor_arch": "64-bit",
        "cost": "0.683000",
        "rate": "0.683000",
    },
]
