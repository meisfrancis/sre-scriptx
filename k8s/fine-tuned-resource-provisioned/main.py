from hpa import get_hpa_metrics
from gitops import update_patch
from vm import get_metrics_values
from math import ceil, floor
from util import load_yaml_config
from pydash import py_
import os
import sys

config = load_yaml_config()

WORKING_DIR = sys.argv[1]
SERVICES = sys.argv[2].split(",")
PROJECTS = load_yaml_config()['projects']
print(f"Working dir: {WORKING_DIR}")
print(f"Services: {SERVICES}")

os.chdir(WORKING_DIR)

for service in SERVICES:
    vm_values = get_metrics_values(service)
    hpa_values = get_hpa_metrics(service)

    if not vm_values or not hpa_values:
        continue

    for key, hpa_data in hpa_values.items():
        max_cpu = hpa_data['current_cpu_value']
        max_mem = hpa_data['current_mem_value']
        if max_cpu < vm_values[f"{key}|cpu"]:
            max_cpu = vm_values[f"{key}|cpu"]
        if max_mem < vm_values[f"{key}|mem"]:
            max_mem = vm_values[f"{key}|mem"]
        _, _, ns = key.split("|")

        # calculate expected resource allocation
        scaling_threshold = py_(config).get('scaling_factor.threshold_in_percent').value()
        target_replica = py_(config).get('scaling_factor.target_replicas').value()
        min_request_cpu = py_(config).get('scaling_factor.min_request_cpu').value()
        limit_factor = py_(config).get('scaling_factor.limit_factor').value()
        expected_metric = floor(target_replica * scaling_threshold / hpa_data["current_replicas"])
        expected_request_cpu = ceil(max_cpu / expected_metric) * 100
        if expected_request_cpu < min_request_cpu:
            expected_request_cpu = min_request_cpu
        expected_request_memory = ceil(max_mem / expected_metric) * 100
        expected_limit_cpu = ceil(expected_request_cpu * limit_factor)
        expected_limit_memory = ceil(expected_request_memory * limit_factor)
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
