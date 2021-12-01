import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#------------------------------------------------------------------------------------------------
# RIPE 
fig, ax = plt.subplots(figsize=(6,5.2))

df = pd.read_csv('../../data/AttributedData/RIPE_squat_prefixes_added.csv',index_col=0,dtype=str)
df['squat_index'] = df['squat_index'].astype(int)
 # Get the frequency, PDF and CDF for each squat_index in the series
print(df.columns)
# df = df['squat_index']
print(df)
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
stats_df['RIPE'] = stats_df['pdf'].cumsum()
stats_df = stats_df.reset_index()
print(stats_df)
b = stats_df.plot(x = 'squat_index', y = 'RIPE', color = 'r',marker='o',ax=ax)

# IP_addresses_to_discard = ['116.85.25.125','82.64.124.151','99.130.250.195','184.167.148.109','47.92.103.144','71.83.101.132'
#                            ,'47.14.114.146','72.143.117.133','47.14.40.177','41.78.245.20','118.126.104.46','31.217.216.5',
#                            '152.136.59.39']
# df[]
dg = df[df['squat_org']!='*']
stats_df = dg \
.groupby('squat_index') \
['squat_index'] \
.agg('count') \
.pipe(pd.DataFrame) \
.rename(columns = {'squat_index': 'frequency'})

# PDF
stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])

# CDF
stats_df['RIPE Attributed'] = stats_df['pdf'].cumsum()
stats_df = stats_df.reset_index()
print(stats_df)
b = stats_df.plot(x = 'squat_index', y = 'RIPE Attributed', color = 'orange', marker='o',ax=ax)
#------------------------------------------------------------------------------------------------
# Microsoft 
df = pd.read_csv('../../data/AttributedData/Cloud_squat_prefixes_added.csv',index_col=0)
df = df[df['squat_org'] != 'Microsoft Corporation']
df['squat_index'] = df['squat_index'].astype(int)
 # Get the frequency, PDF and CDF for each squat_index in the series
print(df.columns)
# df = df['squat_index']
print(df)
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
stats_df['Microsoft'] = stats_df['pdf'].cumsum()
stats_df = stats_df.reset_index()
print(stats_df)
b = stats_df.plot(x = 'squat_index', y = 'Microsoft', color = 'g',marker='*',ax=ax)

df = df[df['squat_org'] != '*']
 # Get the frequency, PDF and CDF for each squat_index in the series
print(df.columns)
# df = df['squat_index']
print(df)
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
stats_df['Microsoft Attributed'] = stats_df['pdf'].cumsum()
stats_df = stats_df.reset_index()
print(stats_df)
b = stats_df.plot(x = 'squat_index', y = 'Microsoft Attributed', color = 'olive',marker='x',ax=ax)
#------------------------------------------------------------------------------------------------
# Ark 
file1 = open("../../data/AttributedData/Ark-Attribution-2021-01-01.txt", "r+")
col = file1.readline()
col = col.replace('\n', '')
# col = col.split('|')[0:6]
col = col.split('|')
print(col)
rows = []
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
df['squat_index'] = df['squat_index'].astype(int)
# print(df)
# # df.to_csv('')
#  # Get the frequency, PDF and CDF for each squat_index in the series
# print(df.columns)
# # df = df['squat_index']
# df['squat_index'] = df['squat_index'].astype(int)
# # Frequency
# stats_df = df \
# .groupby('squat_index') \
# ['squat_index'] \
# .agg('count') \
# .pipe(pd.DataFrame) \
# .rename(columns = {'squat_index': 'frequency'})
#
# # PDF
# stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])
#
# # CDF
# stats_df['Ark'] = stats_df['pdf'].cumsum()
# stats_df = stats_df.reset_index()
# print(stats_df)
# b = stats_df.plot(x = 'squat_index', y = 'Ark', color = 'b', marker='v',ax=ax)

df = df[df['squat_org'] != '*']
stats_df = df \
.groupby('squat_index') \
['squat_index'] \
.agg('count') \
.pipe(pd.DataFrame) \
.rename(columns = {'squat_index': 'frequency'})

# PDF
stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])

# CDF
stats_df['Ark Attributed'] = stats_df['pdf'].cumsum()
stats_df = stats_df.reset_index()
print(stats_df)
b = stats_df.plot(x = 'squat_index', y = 'Ark Attributed', color = 'blue', marker='^',ax=ax)
b.set_xlabel("Position in Traceroute", fontsize=18)
b.set_ylabel("Cum. Frac. of Squatting Hops", fontsize=18)
b.tick_params(labelsize=15)
plt.xticks([0,1,2,3,4,5,10,20,30])
plt.legend(fontsize="large")
# plt.xticks(np.arange(0, 25+1, 1.0))
# plt.savefig('../results/where_the_squat_space_appears_second.svg')
plt.savefig('figures/where_the_squat_space_appears.pdf')
