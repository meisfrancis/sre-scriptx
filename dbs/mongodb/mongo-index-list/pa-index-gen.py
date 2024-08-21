import asyncio
import json
import pydash
import csv

orgs = {}
projects = {}
clusters = {}
atlat_url_tpl = 'https://cloud.mongodb.com/v2/{project_id}#/clusters/detail/{cluster_name}'


async def fetch_atlas(cmd, path='results'):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
    )

    stdout, _ = await proc.communicate()
    decoded_stdout = stdout.decode()
    if not decoded_stdout:
        return []
    result = json.loads(decoded_stdout)
    return result.get('results', []) if path else result


async def get_orgs():
    result = await fetch_atlas('atlas organizations list -o json')
    global orgs
    orgs = {item['id']: {k: v for k, v in item.items() if k in ['id', 'name']} for item in result}


async def get_projects():
    result = await fetch_atlas('atlas projects list -o json')
    global projects
    projects = {item['id']: {k: v for k, v in item.items() if k in ['id', 'name', 'orgId']} for item in result}
    for v in projects.values():
        v['projectName'] = orgs[v['orgId']]['name']
        v['groupName'] = v['name']


pa_index_list = []


async def attach_clusters(project_id):
    result = await fetch_atlas(f'atlas clusters list --projectId {project_id} -o json')
    global clusters, pa_index_list
    for item in result:
        host_cutter = lambda x: x.split('mongodb://')[1]
        host = pydash.get(item, 'connectionStrings.standard', '').split(',')[0]
        pa_index = await fetch_atlas(
            f'atlas performanceAdvisor suggestedIndexes list --projectId {project_id} --processName {host_cutter(host)} -o json',
            None)
        compact_pa_index = [
            {k: {k1: v1 for value in v for k1, v1 in value.items()} if type(v) is list else v for k, v in
             advisor_list.items() if k in ['namespace', 'index']} for advisor_list in
            pa_index['suggestedIndexes']] if pa_index else []
        clusters = clusters | {
            item['name']: {
                              k: v for k, v in item.items() if k in ['name', 'groupId']
                          } |
                          {
                              'atlas_url': atlat_url_tpl.format(project_id=item['groupId'], cluster_name=item['name']),
                              'pa_index': compact_pa_index
                          }
        }


async def main():
    await get_orgs()
    await get_projects()
    await asyncio.gather(*[attach_clusters(k) for k, v in projects.items()])
    clusters_have_pa_index = []
    for v in clusters.values():
        if v['pa_index']:
            v['pa_index'] = '\n'.join(map(lambda x: str(x), v['pa_index']))
            clusters_have_pa_index.append(v)
    with open('pa-index.csv', 'w', newline='') as f:
        headers = clusters_have_pa_index[0].keys()
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(clusters_have_pa_index)


asyncio.run(main())
