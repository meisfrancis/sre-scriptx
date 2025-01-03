import os
import re
import glob
from pathlib import Path
import ruamel.yaml
from util import run, load_yaml_config

yaml = ruamel.yaml.YAML()
yaml.indent(mapping=2, sequence=4, offset=2)  # define indent rule
yaml.default_flow_style = False
PROJECTS = load_yaml_config()['projects']

PATCH_CONTENT = '''
apiVersion: builtin
kind: PatchTransformer
metadata:
  name: patch-deployment
target:
  kind: Deployment
patch: |-
  - {op: replace, path: /spec/template/spec/containers/0/resources/limits/cpu, value: %sm}
  - {op: replace, path: /spec/template/spec/containers/0/resources/limits/memory, value: %sMi}
  - {op: replace, path: /spec/template/spec/containers/0/resources/requests/cpu, value: %sm}
  - {op: replace, path: /spec/template/spec/containers/0/resources/requests/memory, value: %sMi}
'''


def update_patch(
        service_name: str,
        project: str,
        ns: str,
        limit_cpu: int,
        limit_mem: int,
        request_cpu: int,
        request_mem: int
):
    if not project:
        _dir = f"{service_name}/{ns}/aws/apse1/"
    else:
        _dir = f'{service_name}/{project}/{ns}/aws/apse1/'
    patched = False
    for yaml_file in glob.glob(os.path.join(_dir, '*.yaml'), recursive=True):
        if re.search('/secret.*.ya?ml', yaml_file):
            continue
        with open(yaml_file, 'r') as f:
            try:
                change = False
                yaml_data = list(yaml.load_all(f))  # Load the current yaml file
                for yaml_datum in yaml_data:
                    if not yaml_datum:
                        continue
                    # Check the first case where patch is in the transformer file
                    if yaml_datum.get('kind') == 'PatchTransformer':
                        if 'requests/cpu' in yaml_datum["patch"]:
                            yaml_datum["patch"] = re.sub('requests/cpu, value: [0-9]+m',
                                                         f'requests/cpu, value: {request_cpu}m', yaml_datum["patch"])
                            change = True
                        if 'requests/memory' in yaml_datum["patch"]:
                            yaml_datum["patch"] = re.sub('requests/memory, value: [0-9]+(Mi|Gi)',
                                                         f'requests/memory, value: {request_mem}Mi',
                                                         yaml_datum["patch"])
                            change = True
                        if 'limits/cpu' in yaml_datum["patch"]:
                            yaml_datum["patch"] = re.sub('limits/cpu, value: [0-9]+m',
                                                         f'limits/cpu, value: {limit_cpu}m', yaml_datum["patch"])
                            change = True
                        if 'limits/memory' in yaml_datum["patch"]:
                            yaml_datum["patch"] = re.sub('limits/memory, value: [0-9]+(Mi|Gi)',
                                                         f'limits/memory, value: {limit_mem}Mi', yaml_datum["patch"])
                            change = True

                    # Check the second case where patch is in kustomization file
                    elif 'patches' in yaml_datum:
                        for patch in yaml_datum['patches']:
                            if 'requests/cpu' in patch["patch"]:
                                patch["patch"] = re.sub('requests/cpu\n  value: [0-9]+m',
                                                        f'requests/cpu\n  value: {request_cpu}m', patch["patch"])
                                change = True
                            if 'requests/memory' in patch["patch"]:
                                patch["patch"] = re.sub('requests/memory\n  value: [0-9]+(Mi|Gi)',
                                                        f'requests/memory\n  value: {request_mem}Mi', patch["patch"])
                                change = True
                            if 'limits/cpu' in patch["patch"]:
                                patch["patch"] = re.sub('limits/cpu\n  value: [0-9]+m',
                                                        f'limits/cpu\n  value: {limit_cpu}m', patch["patch"])
                                change = True
                            if 'limits/memory' in patch["patch"]:
                                patch["patch"] = re.sub('limits/memory\n  value: [0-9]+(Mi|Gi)',
                                                        f'limits/memory\n  value: {limit_mem}Mi', patch["patch"])
                                change = True

                # Save changes back to the yaml file
                if change:
                    with open(yaml_file, 'w') as f:
                        yaml.dump_all(yaml_data, f)
                        patched = True
            except Exception as e:
                print("Error while parsing yaml file {}: {}".format(yaml_file, str(e)))
    # in case the patch is not found in the yaml files
    if Path(_dir).is_dir() and not patched:
        patch_content = PATCH_CONTENT % (limit_cpu, limit_mem, request_cpu, request_cpu)
        try:
            patch_deployment_file = Path(_dir + "/patch-deployment.yaml")
            kustomize_file = Path(_dir + "/kustomization.yaml")
            patch_deployment = list(yaml.load_all(patch_content))
            # in case there is already a patch-deployment file
            if patch_deployment_file.is_file():
                with open(patch_deployment_file.as_posix(), 'r') as f:
                    # extend the patch_deployment list with the content of the existing patch-deployment file
                    patch_deployment.extend(list(yaml.load_all(f)))
            if kustomize_file.is_file():
                with open(kustomize_file.as_posix(), 'r') as f:
                    kustomize_content = yaml.load(f)
                    # add the patch-deployment.yaml to the transformers list in the kustomization file
                    if 'transformers' not in kustomize_content:
                        kustomize_content['transformers'] = ['patch-deployment.yaml']
                    elif 'patch-deployment.yaml' not in kustomize_content['transformers']:
                        kustomize_content['transformers'].append('patch-deployment.yaml')

                    with open(kustomize_file.as_posix(), 'w') as f:
                        yaml.dump(kustomize_content, f)
                with open(patch_deployment_file.as_posix(), 'w') as f:
                    yaml.dump_all(patch_deployment, f)
                run([f'git add ./{patch_deployment_file.as_posix()}'])
        except Exception as e:
            print("Error while updating kustomization file {}".format(str(e)))
