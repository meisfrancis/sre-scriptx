from hpa import get_hpa_metrics
from gitops import update_patch
from vm import get_metrics_values
from math import ceil, floor
from util import load_yaml_config

SERVICES = [
    "api-auth"
]
PROJECTS = load_yaml_config()['projects']

for service in SERVICES:
    vm_values = get_metrics_values(service)
    hpa_values = get_hpa_metrics(service)

    if not vm_values or not hpa_values:
        continue

    for key, hpa_data in hpa_values.items():
        max_cpu = hpa_data['current_cpu_value']
        max_mem = hpa_data['current_mem_value']
        if max_cpu < vm_values[f"{service}-cpu"]:
            max_cpu = vm_values[f"{service}-cpu"]
        if max_mem < vm_values[f"{service}-mem"]:
            max_mem = vm_values[f"{service}-mem"]
        _, _, ns = key.split("|")
        # calculate expected resource allocation
        scaling_threshold = 85  # this should be equal to Utilization value of your HPA
        target_replica = 1.2  # decrease this will increase expected resource
        expected_metric = floor(target_replica * scaling_threshold / hpa_data["current_replicas"])
        expected_request_cpu = ceil(max_cpu / expected_metric) * 100
        if expected_request_cpu < 150:
            expected_request_cpu = 150
        expected_request_memory = ceil(max_mem / expected_metric) * 100
        expected_limit_cpu = ceil(expected_request_cpu * 1.5)
        expected_limit_memory = ceil(expected_request_memory * 1.5)
        project = None
        for _project in PROJECTS:
            if _project in ns:
                project = _project
                break
        # patch
        update_patch(
            service,
            project,
            ns,
            expected_limit_cpu,
            expected_limit_memory,
            expected_request_cpu,
            expected_request_memory
        )
