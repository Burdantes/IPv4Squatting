import json
from collections import Counter

with open('example_of_external.json') as f:
  data = json.load(f)

with open('example_of_external_speedchecker.json') as f:
    data_speedchecker = json.load(f)
data.update(data_speedchecker)

def last_hop_that_is_responsive(dns_path):
    for dns in range(1,len(dns_path)):
        if dns_path[-dns] in ['*','']:
            continue
        elif dns_path[-dns] is None:
            continue
        else:
            return dns_path[-dns]
    return '*'
occurence_last_hop  =[]
occurence_second_hop = []
last_hops = []
source_hops = []
val = []
for t in data:
    as_path = []
    for i in data[t][2]:
        i = i.split('-')[0]
        if not(i in as_path[-1:]):
            as_path.append(i)
    # print(t,set(data[t][3]))
    print(as_path)
    if len(as_path) == 0:
        continue
    if as_path[-1] == '*':
        try:
            val.append((last_hop_that_is_responsive(data[t][-1]),last_hop_that_is_responsive(data[t][0])))
            occurence_second_hop.append(as_path[-2])
        except:
            continue
    elif as_path[-1] == 'AS8003':
        print(data[t])
        last_hops.append(data[t][0][-1])
        source_hops.append(data[t][2][0])
    else:
        print(data[t])
        occurence_last_hop.append(as_path[-1])
print(Counter(occurence_last_hop))
print(len(occurence_second_hop))
print(Counter(occurence_second_hop))
print(Counter(last_hops).keys())
print(Counter(source_hops))
print(Counter(val))