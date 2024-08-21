import asyncio
import csv
import json
import re

import pydash

ATLAS_URL_TPL = 'https://cloud.mongodb.com/v2/{project_id}#/clusters/detail/{cluster_name}'


async def fetch(c, path, default=None):
    proc = await asyncio.create_subprocess_shell(
        c,
        stdout=asyncio.subprocess.PIPE
    )

    raw, _ = await proc.communicate()
    data = json.loads(raw.decode())
    return pydash.get(data, path, default) if path else data


async def get_orgs():
    result = await fetch('atlas organizations list -o json', 'results')
    return {item['id']: {k: v for k, v in item.items() if k in ['id', 'name']} for item in result}


async def get_projects():
    result = await fetch('atlas projects list -o json', 'results')
    return {item['id']: {k: v for k, v in item.items() if k in ['id', 'name', 'orgId']} for item in result}


async def get_clusters(proj_id):
    result = await fetch(f'atlas clusters list --projectId {proj_id} -o json', 'results', [])
    clusters = {}
    for item in result:
        compute = pydash.get(item, 'replicationSpecs.0.regionConfigs.0.autoScaling.compute', {})
        current_tier = pydash.get(item, 'replicationSpecs.0.regionConfigs.0.electableSpecs.instanceSize',
                                  'Not available')
        clusters = clusters | {
            item['name']: {
                              k: v for k, v in item.items() if k in ['name']
                          } |
                          {
                              'atlas_url': ATLAS_URL_TPL.format(project_id=item['groupId'], cluster_name=item['name']),
                              'env': get_env(item['name']),
                              'current_tier': current_tier,
                          } | compute
        }
    return clusters


def get_env(proj_name):
    if re.findall(r'[Pp]rod', proj_name) and not re.findall(r'[Pp]re.?[Pp]rod', proj_name):
        return 'prod'
    return 'non-prod'


async def main():
    orgs = await get_orgs()
    proj = await get_projects()
    clusters = await asyncio.gather(*[get_clusters(k) for k, v in proj.items()])
    clusters = {k: v for i in clusters for k, v in i.items()}
    csv_data = []
    for v in clusters.values():
        csv_data.append({
            "Cluster Name": v['name'],
            "URL": v['atlas_url'],
            "Scale Enabled": pydash.get(v, 'enabled', 'Not available'),
            "Scale Down Enabled": pydash.get(v, 'scaleDownEnabled', 'Not available'),
            "Min Tier": pydash.get(v, 'minInstanceSize', 'Not available'),
            "Max Tier": pydash.get(v, 'maxInstanceSize', 'Not available'),
            "Current Tier": v['current_tier'],
            "Env": v['env'],
        })
    with open('cluster-min-max-tier.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())

        writer.writeheader()
        writer.writerows(csv_data)


asyncio.run(main())
