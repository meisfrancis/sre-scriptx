import json

with open('04003e6b-8fba-4b4b-985d-a6cccd95f103.1.json') as f:
    data = json.load(f)
with open('jsonmock.txt', 'w') as f:
    for line in data:
        f.write(json.dumps((line['attributes'])))
        f.write('\n')
