# Update container resource based on VM values

## Usuage

### Requirements

- Python 3.8
- Pip
- Kubectl
- You must be able to assume the following role
    - `arn:aws:iam::891378036021:role/UCommPDevAdministrators`
    - `arn:aws:iam::296904546231:role/SharedDevAdministrators`
    - `arn:aws:iam::478927284396:role/ULPDevAdministrators`
    - `arn:aws:iam::134162798543:role/SetelPayDevAdministrators`
    - `arn:aws:iam::158052035554:role/UFPDevAdministrators`
    - `arn:aws:iam::296904546231:role/EKSAdministrator`

### Steps

1. Assume all mentioned roles above
2. Install the required packages: `pip install -r requirements.txt`
3. Run the script: `python main.py <gitops-dir> <list of service split by comma ','>`
   - example `python main.py /home/setel/gitops api-auth,api-iam,api-merchant` 



## Configuration

| Name | Description                              | Type                    |Default| Example
| --- |------------------------------------------|-------------------------|---|---
|scaling_factor| Object to config expected resource value | [ScalingFactor](#ScalingFactor)      |
|projects|List of fission projects| list[str]               ||[setelpay,ulp,ufp,ucommp,b2c]
|ns_ctx_map|Mapping of namespace to context| [ContextNamespaceMap](#ContextNamespaceMap)     
|ctx_env_map|Mapping of context to environment| [ContextEnvironmentMap](#ContextEnvironmentMap)   
|env_ns_pairs|Mapping of environment to namespace| [EnvironmentNamespaceMap](#EnvironmentNamespaceMap) 

### ScalingFactor

| Name | Description                                                                                        | Type   | Default | Example
| --- |----------------------------------------------------------------------------------------------------|--------|---------|---
|threshold_in_percent| Threshold in percentage to scale resource. This is the field `averageUtilization` in HPA component | number | 85      
|target_replicas| Number of replicas to scale to                                                                     | number | 1.2     
|min_request_cpu| Minium CPU set to the expected request_cpu (in milli)                                              | number| 150
|limit_factor| limit resource = this factor * request resource|number|1.5

### ContextNamespaceMap

List of the context and namespace that we want to get HPA metrics from.

It's `key:value[list[str]]`. Key is the context name that can derive from `kubectl config get-contexts -oname`. Value is the list of namespace that belongs to the context, whose HPA component metrics we want to get from.

Note: the amount of keys of this config must be equal to the amount of keys of `ctx_env_map` config.

Example: I want to get HPA metrics from namespace `dev` and `staging` of the context `setel/dev-eks-eks-SSl9ZLzM`
```yaml
ns_ctx_map:
  setel/dev-eks-eks-SSl9ZLzM:
    - dev
    - staging
```

### ContextEnvironmentMap

Map the environment name to the context name. This map helps tagging the value from HPA so that we can compare them with the value from VM.

It's `key:value[str]`. Key is the context name that can derive from `kubectl config get-contexts -oname`. Value is the environment name corresponding to the context.

Note: the amount of keys of this config must be equal to the amount of keys of `ns_ctx_map` config.

### EnvironmentNamespaceMap
List of environment and namespace on VM that we want to get resource usage metrics from

It's string split by colon `:`. The left side is the environment name and the right side is the namespace name.

## Environment Variables

use `.env` file

| Name | Description| Example
| --- | ---|---
|GRAFANA_TOKEN|Grafana API token|glsa_abchdddY312RR
|GRAFANA_URL|Grafana hostname|https://grafana.ops.setel.com
|GRAFANA_DATASOURCE_UID|Grafana datasource UID to get metrics values from|KLUVORSnk
|GRAFANA_DATASOURCE_TYPE|Grafana datasource type|prometheus

## Anatomy

Help you understand what it does. For example: I want to optimize `api-auth`

1. The script will get metrics of resource usage from VM for `api-auth` and return this dict 
    - ```python
        {
            "api-auth|dev|dev|cpu": 0.5,
            "api-auth|dev|dev|mem": 200,
            "api-auth|dev|staging|cpu": 0.5,
            "api-auth|dev|staging|mem": 200,
            "api-auth|setelpay-dev|setelpay-dev|cpu": 0.5,
            "api-auth|setelpay-dev|setelpay-dev|mem": 200,
        }
        ```
    - The key is `service|environment|namespace|resource` and the value is the resource usage value
2. Then it will get current HPA status from K8s API and return this dict
    - ```python
        {
            "api-auth|dev|dev": {
                "current_replicas": 2,
                "current_cpu_value": 3,
                "current_mem_value": 250
            },
            "api-auth|setelpay-dev|setelpay-dev": {
                "current_replicas": 2,
                "current_cpu_value": 3,
                "current_mem_value": 250
            },
        }
        ```
    - The key is `service|environment|namespace` and the value is the current HPA status
3. Then it will calculate the expected resource value based on the VM value and HPA status
4. And patch the HPA component with the expected resource value using script in `gitops.py`