import json
import pandas as pd
import ast
import os
from collections import Counter

category = 'router'
list_of_ases = []
val = []
AS_level_metainfos = pd.read_pickle(
    '../../data/BGP/resulting_graph_May2021.pickle')
PeeringDB = pd.read_csv('../../data/MetaInformation/PeeringDB_AS_level_info_2021-09-01.csv',index_col=0)
print(PeeringDB.columns)
print(AS_level_metainfos['Organization'].value_counts())
print(AS_level_metainfos['ASType'].value_counts())
organization_to_manually_assess = []
if category == 'NATs':
    path = '../../result/labels_prefixes_nat444.csv'
    df = pd.read_csv(path,index_col = 0)
    updated_label = {0:'Large CGNAT',1:'Small CPE',2:'Small CPE',3:'Medium CGNAT',4:'Ambiguous CPE/CGNAT',5:'Large CGNAT',6:'Large CGNAT',7:'Large CPE',8:'Large CGNAT'}
    CGNATs = ['Large CGNAT', 'Medium CGNAT']
    CPEs = ['Small CPE','Large CPE']
    # df = df[df['Labels'].isin(CPEs)]
    print('# of Source /24 NAT', df[df['Labels'].isin(CPEs)].shape)
    print('# of Source /24 CGNAT',df[df['Labels'].isin(CGNATs)].shape)
    df = df[df['Labels'].isin(CPEs)]
    print(df.shape)
    for ases,organization in zip(df['Source AS'],df['Source Org']):
    # col = col.split('|')[0:6]
    # col = col.strip()
    #     print(row)
        # organization = ('\t').join(row.split('\t')[1:])
        # print(ases)
        if ases in list_of_ases:
            continue
        if ases == '*':
            organization_to_manually_assess.append(organization)
            continue
        # print(organization)
        list_of_ases.append(ases)
        if ases == '763' or ases == '16160' or ases =='45725138877' or ases == '5579963916' or ases == '28303' or ases == '26415299662254739657427544396544396566396576397193397197397202' or ases == '26291' or ases == '24024':
            continue
        if ases =='15169':
            print('HOLD ON')
        if len(ases.split('-')) > 1:
            ases = ases.split('-')[0]
        # try:
        # print(ases)
        print(PeeringDB['asn'])
        print(PeeringDB[PeeringDB['asn'] == int(ases)]['info_type'])
        try:
            if PeeringDB[PeeringDB['asn']==int(ases)]['info_type'].values[0] == 'Content':
                val.append([AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['Eyeballs'].values[0],
                            AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['ASCone'].values[0],
                            'Content', ases,
                            organization])
            else:
                ases = str(ases)
                val.append([AS_level_metainfos[AS_level_metainfos['asNumber']==ases]['Eyeballs'].values[0],AS_level_metainfos[AS_level_metainfos['asNumber']==ases]['ASCone'].values[0],AS_level_metainfos[AS_level_metainfos['asNumber']==ases]['ASType'].values[0],ases,organization])
        except:
            continue
elif category =='router':
    path = ""
    l = []
    border_text = open('ASN_internal.txt',"r")
    for row in border_text.readlines():
        if row.startswith('#'):
            continue
        row = row.replace('\n', '')
            # print(txt)
        print(row)
        l.append(row)
        for ases in l:
            try:
                organization = AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['Organization'].values[0]
                ases = int(ases)
            except:
                organization_to_manually_assess.append(ases)
                continue
            # print(organization)
            list_of_ases.append(ases)
            if ases == '763' or ases == '16160' or ases == '45725138877' or ases == '5579963916' or ases == '28303' or ases == '26415299662254739657427544396544396566396576397193397197397202' or ases == '26291' or ases == '24024':
                continue
            if ases == '15169':
                print('HOLD ON')
            # try:
            # print(ases)
            print(PeeringDB['asn'])
            print(PeeringDB[PeeringDB['asn'] == int(ases)]['info_type'])
            # try:
            print(ases)
            if int(ases) in PeeringDB['asn'].values:
                print(PeeringDB[PeeringDB['asn'] == int(ases)])
                if PeeringDB[PeeringDB['asn'] == int(ases)]['info_type'].values[0] == 'Content':
                    val.append([AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['Eyeballs'].values[0],
                                AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['ASCone'].values[0],
                                'Content', ases,
                                organization])
                else:
                    ases = str(ases)
                    val.append([AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['Eyeballs'].values[0],
                                AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['ASCone'].values[0],
                                AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['ASType'].values[0], ases,
                                organization])
            else:
                ases = str(ases)
                val.append([AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['Eyeballs'].values[0],
                            AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['ASCone'].values[0],
                            AS_level_metainfos[AS_level_metainfos['asNumber'] == ases]['ASType'].values[0], ases,
                            organization])
            # except:
            #     continue
                    # print(row)
    # val[-1].append(PeeringDB[PeeringDB['asn']==ases]['info_type'].values[0])
    # print(PeeringDB[PeeringDB['asn']==ases]['info_type'].values[0])
print(val)
print(len(list_of_ases))
print(len(set(list_of_ases)))
access = 0
transit = 0
content = 0
none = 0
as_type = []
for t,s,u,ases,org in val:
    if u == 'Content':
        print(org,ases)
        content += 1
    if t > 10**5:
        access +=1
    elif t < 10**5 and t>10**2 and s>6:
        transit +=1
    elif s> 20:
        transit +=1
    else:
        none += 1
    as_type.append(u)

print('# Access Transit Unknown Content')
print(access,transit,none,content)
print(Counter(as_type))
print(organization_to_manually_assess)