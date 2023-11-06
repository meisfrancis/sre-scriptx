# mongo-app-2 subtract mongo-app-1

with open('./data_source/mongo-app-1.txt') as f:
    set_1 = set(map(lambda a: a.strip(), f.readlines()))

with open('./data_source/mongo-app-2.txt') as f:
    set_2 = set(map(lambda a: a.strip(), f.readlines()))

diff = set_2.difference(set_1)
print(list(diff))
with open(f'./data_source/result.txt', 'w') as f:
    f.writelines([line + '\n' for line in diff])
