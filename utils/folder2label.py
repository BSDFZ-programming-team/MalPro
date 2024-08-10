import os
import json
with open('malware_families_list.json', 'r') as f:
    dic = json.load(f)
swapped_dict = {}

for key, value in dic.items():
    if value in swapped_dict:
        swapped_dict[value].append(key)
    else:
        swapped_dict[value] = key

print(swapped_dict)
with open('labels.csv', 'w+') as f:
    for i in os.listdir('./'):
        if not i.endswith('.py'):
           Id = swapped_dict[i]
           for j in os.listdir(f'./{i}'):
               basename = j.replace('.asm', '')
               f.write(f'"{basename}",{Id}\n')