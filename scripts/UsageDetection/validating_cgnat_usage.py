import json
# Opening JSON file
import pandas as pd
import ipaddress
from tqdm import tqdm
import os
from collections import Counter

rdns_informative = {}
path = "../../result/rDNS_CPE-CGNAT/"
for root, dirs, files in os.walk(path, topdown = False):
    for file in files:
        print(file)
        if file == 'cpe_prefixes.json':
            continue
        if file.startswith('cpe'):
            rdns_informative.update(json.load(open(path + file)))
# rdns_informative = json.load(open('../../result/rDNS_CPE-CGNAT/cpe_prefixesxaa.json'))

df = pd.read_csv('../../result/labels_prefixes_nat444.csv',index_col = 0)
# print(df['Source Prefix'])
validated = 0
# df = df[df['Labels'] != 'Unknown']
# set_of_prefixes = list(set(df['Source Prefix'].values))
set_of_prefixes = list(df['Source Prefix'].values)
set_of_nat = list(df['Labels'].values)
set_of_org = list(df['Source Org'].values)
merged = list(set(zip(set_of_prefixes,set_of_nat,set_of_org)))
rdns_information_24 = {}
number_of_prefixes = 0
for key in tqdm(rdns_informative):
    ip_addresses = ipaddress.ip_network(key)
    subnets = list(ip_addresses.subnets(new_prefix=24))
    number_of_prefixes += len(subnets)
    for l in subnets:
        rdns_information_24[str(l)] = rdns_informative[key]/float(len(subnets))
    #     if l in set_of_prefixes:
    #         validated += 1
# for i in df['Source']:
rdns_cpe = {}
informative_cpe = 0
no_informative_dns = 0
list_of_type = []
print(number_of_prefixes)
list_of_org = []
percentage = []
for i,k,l in merged:
    if i in rdns_information_24:
        val = rdns_information_24[i]
        rdns_cpe[i] = val/256
        if rdns_cpe[i] > 0.01:
            informative_cpe += 1
            print(i, k)
            print(val)
            print(rdns_cpe[i])
            list_of_type.append(k)
            list_of_org.append(l)
            if rdns_cpe[i] < 0.5:
                rdns_cpe[i] *= 2
            percentage.append(rdns_cpe[i])
    else:
        no_informative_dns +=1
print(informative_cpe)
print(no_informative_dns)
print(Counter(list_of_type))
print(Counter(list_of_org))
# print(df['Labels'].value_counts()/float(df['Labels'].value_counts().sum()))
dg = df[df['Source Prefix']=='172.115.152.0/24']
print('')
print(percentage)
import seaborn as sns
import matplotlib.pyplot as plt
# plt.hist(percentage, cumulative=True, density=True, label='CDF',
#          histtype='bar', alpha=0.8, color='red')
sns.kdeplot(data = percentage, cumulative = True, label = "Fraction of the /24",clip= (0.0, 1.0))
plt.xlabel('Fraction of /24 with rDNS entries with \'cpe\' in them')
plt.ylabel('Ratio')
plt.legend()
plt.savefig('../../result/rDNS_CPE-CGNAT/fractionrdns.png')