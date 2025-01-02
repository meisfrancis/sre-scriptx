# This file provide metrics for the fine-tuned resource provisioned
from dotenv import load_dotenv
from math import ceil
from pydash import py_
from util import byte_to_mb, load_yaml_config
import os
import requests
import copy

load_dotenv()

QUERY_TPL = {
    "refId": "",
    "datasource": {
        "uid": os.getenv('GRAFANA_DATASOURCE_UID'),
        "type": os.getenv('GRAFANA_DATASOURCE_TYPE'),
    },
    "expr": "",
    "format": "timeseries",
    "maxDataPoints": 2170,
    "intervalMs": 30000,
}

QUERY_CFGS = {
    "queries": [

    ],
    "from": "now-1d",
    "to": "now"
}

MEM_METRIC_QUERY = """max by (environment, owner_name) (
        container_memory_working_set_bytes{container=~"%s", environment=~"%s", namespace=~"%s"} * on (pod) group_left (owner_name) 
        (max by (owner_name, pod) (kube_pod_owner{owner_name=~"%s.*", owner_kind="ReplicaSet"}))
)"""

CPU_METRIC_QUERY = """max by (environment, owner_name) (
        rate(container_cpu_usage_seconds_total{container=~"%s", environment=~"%s", namespace=~"%s"} * on (pod) group_left(owner_name) 
        (max by (owner_name, pod) (kube_pod_owner{owner_name=~"%s.*", owner_kind="ReplicaSet"}))[5m]) != 0
)"""

ENV_NS_PAIRS = load_yaml_config()['env_ns_pairs']


def _fetch_metric_values(query: dict) -> (dict, str):
    api_path = "/api/ds/query"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GRAFANA_TOKEN')}"
    }
    try:
        data = requests.post(f"{os.getenv('GRAFANA_URL')}{api_path}", json=query, headers=headers).json()
        return data['results'], None
    except Exception as e:
        return None, f"Error fetching metric values: {e}"


def _get_mem_query(service_name: str, env: str, ns: str) -> QUERY_TPL:
    tpl = QUERY_TPL.copy()
    tpl["expr"] = MEM_METRIC_QUERY % (service_name, env, ns, service_name)
    tpl["refId"] = f"{service_name}|{env}|{ns}|mem"
    return tpl


def _get_cpu_query(service_name: str, env: str, ns: str) -> QUERY_TPL:
    tpl = QUERY_TPL.copy()
    tpl["expr"] = CPU_METRIC_QUERY % (service_name, env, ns, service_name)
    tpl["refId"] = f"{service_name}|{env}|{ns}|cpu"
    return tpl


def get_metrics_values(service_name: str) -> dict | None:
    query_cfg = copy.deepcopy(QUERY_CFGS)
    mem_queries = [_get_mem_query(service_name, env, ns) for env, ns in [pair.split(":") for pair in ENV_NS_PAIRS]]
    cpu_queries = [_get_cpu_query(service_name, env, ns) for env, ns in [pair.split(":") for pair in ENV_NS_PAIRS]]
    query_cfg["queries"] = mem_queries + cpu_queries
    results, err = _fetch_metric_values(query_cfg)
    if err:
        print(err)
        return None
    for k, v in results.items():
        metric_value = py_(v).get("frames[0].data.values[1]", [-1]).max_().value()
        if metric_value == -1:
            results[k] = None
            continue
        if "mem" in k:
            results[k] = byte_to_mb(metric_value)
            continue
        if "cpu" in k:
            results[k] = ceil(metric_value * 1000)

    return results
