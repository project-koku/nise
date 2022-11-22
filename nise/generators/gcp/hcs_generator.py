from nise.generators.gcp.compute_engine_generator import ComputeEngineGenerator
from nise.generators.gcp.compute_engine_generator import JSONLComputeEngineGenerator


class HCSGenerator(ComputeEngineGenerator):
    LABELS = (([{"key": "goog-dm", "value": "red-hat-openshift-container-platform-1"}]),)
    SERVICE = ("Red Hat® OpenShift® Container Platform", "7890-9662-83CC")
    SKU = (("DD70-0A3E-6C9F", "Licensing Fee for vCPU-per-hour on VM with 0 VCPU or more", "seconds", "hour"),)
    SYSTEM_LABELS = (
        (
            [
                {"key": "compute.googleapis.com/cores", "value": "4"},
                {"key": "compute.googleapis.com/machine_spec", "value": "n2d-standard-4"},
                {"key": "compute.googleapis.com/memory", "value": "16384"},
            ]
        ),
    )


class JSONLHCSGenerator(JSONLComputeEngineGenerator):
    LABELS = (([{"key": "goog-dm", "value": "red-hat-openshift-container-platform-1"}]),)
    SERVICE = ("Red Hat® OpenShift® Container Platform", "7890-9662-83CC")
    SKU = (("DD70-0A3E-6C9F", "Licensing Fee for vCPU-per-hour on VM with 0 VCPU or more", "seconds", "hour"),)
    SYSTEM_LABELS = (
        (
            [
                {"key": "compute.googleapis.com/cores", "value": "4"},
                {"key": "compute.googleapis.com/machine_spec", "value": "n2d-standard-4"},
                {"key": "compute.googleapis.com/memory", "value": "16384"},
            ]
        ),
    )
