import pandas as pd
from collections import Counter

df_block = pd.read_csv('GeoLite2-Country-CSV_20210817/GeoLite2-Country-Blocks-IPv4.csv')
df_loc = pd.read_csv('GeoLite2-Country-CSV_20210817/GeoLite2-Country-Locations-en.csv')
print(df_loc.columns,df_block.columns)
merged_maxmind = pd.merge(left=df_block,right=df_loc,left_on='geoname_id',right_on='geoname_id')
# merged_inner = pd.merge(left=unbundled['net'], right=unbundled['org'], left_on='org_id', right_on='org_id')
# print(merged_maxmind[merged_maxmind['network'].startswith('6.')])
merged_maxmind['is_it_squatspace'] = list(
     map(lambda x: x.startswith('56.'), merged_maxmind['network']))
test = merged_maxmind[merged_maxmind['is_it_squatspace']]
print(test[['network','country_name']])
print(Counter(test['country_name'].values))