import json
import csv
import subprocess

# subprocess.run('python3 atlas.py'.split(' '))
# subprocess.run('python3 gitops.py'.split(' '))

with open('clusters-services-mapping.json') as f:
    clusters_services_map = json.load(f)
with open('atlas-clusters.json') as f:
    atlas_clusters = json.load(f)
with open('cluster-links-map.json') as f:
    cluster_links_map = json.load(f)
with open('service-team-map.json') as f:
    service_team_map = json.load(f)

# map service to atlas
for host, cluster in clusters_services_map.items():
    a_cluster = atlas_clusters.get(cluster_links_map.get(host))
    if a_cluster:
        if not a_cluster.get('services'):
            a_cluster['services'] = set()
            a_cluster['env'] = cluster['env']
        a_cluster['services'] = a_cluster['services'] | {x for x in cluster['services']}


# serialize data for csv
csv_data = []
for cluster in atlas_clusters.values():
    for service in cluster.get('services', []):
        csv_data.append({
            "Project Name": cluster['projectName'],
            "Group Name": cluster['groupName'],
            "Cluster Name": cluster['name'],
            "Atlas URL": cluster['atlas_url'],
            "Env": cluster['env'],
            "Service": service,
            "Team": service_team_map.get(service, '')
        })

with open('result.csv', 'w', newline='') as csvfile:
    field_names = csv_data[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=field_names)

    writer.writeheader()
    writer.writerows(csv_data)




