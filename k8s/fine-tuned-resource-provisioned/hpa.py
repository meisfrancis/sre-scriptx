from kubernetes import client, config
from util import byte_to_mb, load_yaml_config

yaml_config = load_yaml_config()
NS_CTX_MAP = yaml_config['ns_ctx_map']
CTX_ENV_MAP = yaml_config['ctx_env_map']


def get_hpa_metrics(service_name: str) -> dict | None:
    _results = {}
    for _context, _env in CTX_ENV_MAP.items():
        config.load_kube_config(context=_context)
        hpa_api = client.AutoscalingV2Api()
        for _namespace in NS_CTX_MAP[_context]:
            try:
                hpa = hpa_api.list_namespaced_horizontal_pod_autoscaler(_namespace,
                                                                        label_selector=f"app.kubernetes.io/name={service_name}")
                for _item in hpa.items:
                    if not _item.status.current_metrics:
                        continue
                    _cpu_metric = _item.status.current_metrics[1].resource
                    _mem_metric = _item.status.current_metrics[0].resource
                    if not _cpu_metric or not _mem_metric:
                        continue
                    _key = f'{service_name}|{_env}|{_namespace}'
                    if not _results.get(_key):
                        _results[_key] = {}
                    _results[_key]['current_replicas'] = _item.status.current_replicas
                    _cpu_val = _cpu_metric.current.average_value
                    _mem_val = _mem_metric.current.average_value
                    if 'm' in _cpu_val:
                        _results[_key]['current_cpu_value'] = int(_cpu_val.split('m')[0])
                    else:
                        _results[_key]['current_cpu_value'] = int(_cpu_val)
                    if 'm' in _mem_val:
                        _results[_key]['current_mem_value'] = int(_mem_val.split('m')[0]) / 1000
                    elif 'k' in _mem_val:
                        _results[_key]['current_mem_value'] = int(_mem_val.split('k')[0]) * 1000
                    else:
                        _results[_key]['current_mem_value'] = byte_to_mb(int(_mem_val))
            except Exception as e:
                print(f"Exception when calling AutoscalingV1Api->list_namespaced_horizontal_pod_autoscaler: {e}")
                return None
    return _results

