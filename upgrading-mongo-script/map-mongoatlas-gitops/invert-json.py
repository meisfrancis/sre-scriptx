import json


with open('team-service-map.json') as f:
    data = json.load(f)

json_data = {}
for k, v in data.items():
    for service in v:
        json_data[service] = k

with open('service-team-map.json', 'w') as f1:
    json.dump(json_data, f1)
