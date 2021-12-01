import os
import pandas as pd
import matplotlib.pyplot as plt
rows = []

fig, ax = plt.subplots()
file1 = open("/Users/geode/Downloads/squatspace-master/scripts/bdrmapITanalysis/analysis_comparison.txt", "r+")
col = file1.readline()
col = col.replace('\n', '')
# col = col.split('|')[0:6]
col = col.split('|')
print(col)
for row in file1.readlines():
    # print(row)
    if row[0] == '#':
        continue
    row = row.replace('\n','')
    # row = row.split(',')
    row = row.split('|')
    # row = row[0:6]
    rows.append(row)
    print(row)
df = pd.DataFrame(rows,columns=col)
print(df)
# df.to_csv('')
 # Get the frequency, PDF and CDF for each squat_index in the series
print(df.columns)
# df = df['squat_index']
df['squat_index'] = df['squat_index'].astype(int)
# Frequency
stats_df = df \
.groupby('squat_index') \
['squat_index'] \
.agg('count') \
.pipe(pd.DataFrame) \
.rename(columns = {'squat_index': 'frequency'})

# PDF
stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])

# CDF
stats_df['cdf'] = stats_df['pdf'].cumsum()
stats_df = stats_df.reset_index()
print(stats_df)
b = stats_df.plot(x = 'squat_index', y = 'cdf',legend=None)
b.set_xlabel("Hop where the squat IP address appeared", fontsize=15)
b.set_ylabel("Frequency", fontsize=15)
b.tick_params(labelsize=12)
import numpy as np
# plt.savefig('Position_of_the_Squat_IP.png')

bdrmapped_better = 0
standard_better = 0
different_mapping = 0
agreement = 0
# for i in range(0,int(len(df)/2)):
i = 0
bdrmapped_rir_diff = 0
# bdrmapped_rir_dif
from copy import deepcopy
list_of_id_different = []
while i < len(df)-1:
    current = df[df.index == i]['trace_id'].values[0]
    j = deepcopy(i)
    while current == df[df.index == j]['trace_id'].values[0]:
        j += 1
    diff = j - i
    if i + 2*diff > len(df):
        print(diff)
        break
    for k in range(0,diff):
        bdrmapped = df[df.index==i+k]['squat_org'].values[0]
        standard = df[df.index==i+diff+k]['squat_org'].values[0]
        ip_squatted1 = df[df.index==i+k]['squat_ip'].values[0]
        ip_squatted2 = df[df.index==i+diff+k]['squat_ip'].values[0]
        is_it_bdrmap =  df[df.index==i+k]['type'].values[0]
        is_it_standard = df[df.index == i + diff + k]['type'].values[0]
        if ip_squatted1 != ip_squatted2 or is_it_bdrmap == is_it_standard:
            continue
        rir_mapping = df[df.index==i+diff+k]['squat_rir'].values[0]
        # if (standard!= '*' and bdrmapped !='*'):
        if standard!= bdrmapped :
            if standard == '*':
                bdrmapped_better +=1
            elif bdrmapped =='*':
                standard_better +=1
            elif bdrmapped != rir_mapping:
                bdrmapped_rir_diff +=1
            else:
                different_mapping+=1
                # print(rir_mapping, df[df.index == i + k]['squat_rir'])
                print(df[df.index == i + k].values)
                print(df[df.index == i + diff + k].values)
                list_of_id_different.append(df[df.index == i + k].values[0][0])
        else:
            agreement+=1
    i += 2*diff
    # else:
        # print()
df_bdrmap = df[df['type']=='bdrmapIT']
df_st = df[df['type']=='standard']
val_st = df_st['squat_org'].value_counts().index
val_bdrmap = df_bdrmap['squat_org'].value_counts().index
val_rir = df_bdrmap['squat_rir'].value_counts().index
print('Agreement ' ,agreement)
print('BdrmapIT better ', bdrmapped_better)
print('Standard better ', standard_better)
print('Different Mapping ', different_mapping)
print(len(list(set(val_st)-set(val_bdrmap))))
print('This answer Ethan:', len(list(set(val_bdrmap)-set(val_st))))
print(df_bdrmap[df_bdrmap['squat_org']=='China Mobile'])
print(df_st[df_st['trace_id']=='81'])
print(list(set(val_bdrmap)-set(val_st)))
print(len(list(set(val_bdrmap)-set(val_rir))))
print(len(list(set(val_st)-set(val_rir))))
print(len(val_bdrmap))
print(len(val_st))
# print(list(set(val_bdrmap)-set(val_st)))
# print(list(set(val_st)-set(val_bdrmap)))
print(df_st.shape)
print(df_bdrmap.shape)
print(df_bdrmap[df_bdrmap['squat_org']!= df_bdrmap['squat_rir']].shape)
with open('ID_with_different.txt', 'w') as f:
    for link in list_of_id_different:
        f.write(str(link) + '\n')
