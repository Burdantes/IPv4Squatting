import pandas as pd
from tqdm import tqdm
import os 
path = '../../result/labels_prefixes_nat444.csv'
df = pd.read_csv(path,index_col = 0)
updated_label = {0:'Large CGNAT',1:'Small CPE',2:'Small CPE',3:'Medium CGNAT',4:'Ambiguous CPE/CGNAT',5:'Large CGNAT',6:'Large CGNAT',7:'Large CPE',8:'Large CGNAT'}
CGNATs = ['Large NAT444', 'Small NAT444']
CPEs = ['Unknown'] 
counting_cgnat = 0
counting_nat = 0
restricted_prefixes_nat = df[df['Labels'].isin(CPEs)]['Source Prefix'].values
restricted_prefixes_cgnat = df[df['Labels'].isin(CGNATs)]['Source Prefix'].values
folder_path = '../../data/AttributedData/updated_format_squatters/'
for month in ['05','03']:
    for name in os.listdir(folder_path):
        count = 0
        filename= folder_path+name
        with open(filename, 'r') as fin:
            for line in tqdm(fin):
                if line.startswith('#') or 'trace_id' in line:
                    continue
                row = line.split('|')
                row_prefix = row[-2]
                if row_prefix in restricted_prefixes_cgnat:
                    counting_cgnat += 1
                if row_prefix in restricted_prefixes_nat:
                    counting_nat += 1
                # if src_asn == '37963' and src_ip == '42.120.72.110':
                #     print(line)
print(counting_cgnat,counting_nat)