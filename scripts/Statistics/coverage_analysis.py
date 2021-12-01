import pandas as pd
from tqdm import tqdm
import json
from statisticsfiltering import reading_data
rows = []

def load_customer_cone():
    customer_cone_file = "../../data/MetaInformation/customer_cone_per_asn.json"
    with open(customer_cone_file) as f:
        customer_cone_per_asn = json.load(f)
        # customer_cone_per_asn = {str(x): set(customer_cone_per_asn[x]) for x in customer_cone_per_asn}
        return customer_cone_per_asn

customer_cones = load_customer_cone()
path_to_probes = '../../data/MetaInformation/20210630.json'
probes = {d['id']: d for d in json.load(open(path_to_probes))['objects']}
df_probes = pd.DataFrame(probes).transpose()
probes = []
file = open('../../data/MetaInformation/arkipelago_distribution.txt','r')
rows = []
test = {}
for row in file.readlines():
    print(row)
    if row.startswith('#'):
        col = row.split('|')
        continue
    rows.append(row.split('|'))
df_ark = pd.DataFrame(rows,columns=col)
df_ark['as_number'] = df_ark['as_number'].astype(str)
print(df_ark['as_number'])
df_probes['asn_v4'] = df_probes['asn_v4'].astype(str)
print(len(df_ark['as_number'].unique()))
print(len(df_probes['asn_v4'].unique()))
print(len(set(df_ark['as_number'].unique()).union(set(df_probes['asn_v4'].unique()))))
import matplotlib.pyplot as plt
AS_level_metainfos = pd.read_pickle(
    '../../data/BGP/resulting_graph_May2021.pickle')
AS_level_metainfos.fillna(0,inplace=True)
dg = reading_data()
l = []
for key in customer_cones.keys():
    l.extend(customer_cones[key])
    l.append(key)
total_number_of_ASes = len(set(l))
print(total_number_of_ASes)
# eyeballs = 0
# print(df_probes['asn_v4'])
# print(AS_level_metainfos['asNumber'])
# AS_level_metainfos = AS_level_metainfos.fillna(0)
# for t in tqdm(dg['endUserASN'].value_counts().index):
#     if str(t) in AS_level_metainfos['asNumber'].values:
#         eyeballs += AS_level_metainfos[AS_level_metainfos['asNumber'] == str(t)]['Eyeballs'].values[0]
# print(float(eyeballs)/sum(AS_level_metainfos['Eyeballs'].values))


# print(dg)
def return_statistics(category):
    customer_cones_count = []
    eyeballs = 0
    # print(df_probes['asn_v4'])
    # for t in tqdm(dg['endUserASN'].value_counts().index):
    if category == 'Ark':
        as_sources = df_ark['as_number'].value_counts().index
    elif category == 'RIPE':
        as_sources = df_probes['asn_v4'].unique()
    elif category =='Microsoft':
        as_sources = dg['endUserASN'].value_counts().index
    for t in tqdm(as_sources):
    # for t in tqdm(test.keys()):
        # if str(t) in AS_level_metainfos['asNumber'].values:
            for val in str(t).split('-'):
                # print(val)
                if val in AS_level_metainfos['asNumber'].values:
                        # continue
                    eyeballs += AS_level_metainfos[AS_level_metainfos['asNumber'] == str(t)]['Eyeballs'].values[0]
                if val in customer_cones:
                    customer_cones_count.extend(customer_cones[val])
    return eyeballs,float(len(list(set(customer_cones_count))))
eyeballs,customer_cone = return_statistics('Ark')
print('#---------------------#')
print('Ark')
print('Eyeballs',float(eyeballs)/sum(AS_level_metainfos['Eyeballs'].values))
print('Customer Cone',customer_cone/total_number_of_ASes)

eyeballs,customer_cone = return_statistics('RIPE')
print('#---------------------#')
print('RIPE')
print('Eyeballs',float(eyeballs)/sum(AS_level_metainfos['Eyeballs'].values))
print('Customer Cone',customer_cone/total_number_of_ASes)

eyeballs,customer_cone = return_statistics('Microsoft')
print('#---------------------#')
print('Microsoft')
print('Eyeballs',float(eyeballs)/sum(AS_level_metainfos['Eyeballs'].values))
print('Customer Cone',customer_cone/total_number_of_ASes)
# print(len(list(set)))