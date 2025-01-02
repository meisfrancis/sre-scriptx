# This file provide metrics for the fine-tuned resource provisioned
import ruamel.yaml
from dotenv import load_dotenv
from math import ceil,floor
from pydash import get
import os
import requests
import copy

load_dotenv()
YAML = ruamel.yaml.YAML(typ='safe')
YAML.indent(mapping=2, sequence=4, offset=2)  # define indent rule
YAML.default_flow_style = False

config = YAML.load(open('config.yaml'))

QUERY_TPL = {
    "refId": "",
    "datasource": {
        "uid": config['grafana']['datasource']['uid'],
        "type": config['grafana']['datasource']['type'],
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
        (max by (owner_name, pod) (kube_pod_owner{owner_name=~"%s.*", owner_kind="ReplicaSet"}))[$__rate_interval])[:30s] != 0
)"""

ENV_NS_PAIRS = [
    "dev",
    "dev:staging",
    "b2c-dev",
    "dev-data:dev",
    "setelpay-dev",
    "ucommp-dev",
    "ufp-dev",
    "ulp-dev",
    "pre-prod",
    "setelpay-pre-prod",
    "ucommp-pre-prod",
    "ufp-pre-prod",
    "ulp-pre-prod",
    "staging-data:staging",
    "setelpay-staging",
    "ucommp-staging",
    "ufp-staging",
    "ulp-staging",
]

def _fetch_metric_values(query: dict):
    api_path = "/api/ds/query"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GRAFANA_TOKEN')}"
    }
    return requests.post(f"{os.getenv('GRAFANA_URL')}{api_path}", json=query, headers=headers).json()



def _build_mem_query(service_name: str, env: str, cfg: dict):
    query = MEM_METRIC_QUERY % (service_name, argocd_env[env], argocd_ns[env], service_name)
    tpl = QUERY_TPL.copy()
    tpl["expr"] = query
    tpl["refId"] = "mem"
    cfg["queries"].append(tpl)


def _build_cpu_query(service_name: str, env: str, cfg: dict):
    query = CPU_METRIC_QUERY % (service_name, argocd_env[env], argocd_ns[env], service_name)
    tpl = QUERY_TPL.copy()
    tpl["expr"] = query
    tpl["refId"] = "cpu"
    cfg["queries"].append(tpl)


def _byte_to_mb(b: int) -> int:
    return ceil(b / (1024 * 1024))


def _get_mean_mb(data: dict):
    series = get(data, "results.mem.frames[0].data.values[1]")
    if not series:
        return None
    mean = sum(series) / len(series)
    return byte_to_mb(mean)


def _get_mean_cpu(data: dict):
    series = get(data, "results.cpu.frames[0].data.values[1]")
    if not series:
        return None
    mean = sum(series) / len(series) * 1000
    return ceil(mean)


def get_metrics_values(service_name:str):
    query_cfg = copy.deepcopy(QUERY_CFGS)