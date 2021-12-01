import pandas as pd
import matplotlib.pyplot as plt
rows = []
file2 = open("ID_with_different.txt","r")
list_of_id_str = file2.readlines()
list_of_id = []
for t in list_of_id_str:
    t = t.replace('\n','')
    s = int(t)+1
    list_of_id.append(t)
    list_of_id.append(str(s))
print(list_of_id)
file1 = open("output_analysis.txt", "r+")
for row in file1.readlines():
    # print(row)
    if row[0] == '#':
        continue
    row = row.replace('\n','')
    # row = row.split(',')
    row = row.split('|')
    # row = row[0:6]
    if row[0] in list_of_id:
        rows.append(row)
        print(row)
    # if row[1] != '':
col = ['Traceroute ID','DNS','Org mapped','IP address','Org Squat is Mapped','Type','Position']
df = pd.DataFrame(rows,columns=col)
to_keep = []
for t in df.groupby('Traceroute ID'):
    if len(set(t[1]['DNS'].values)) > 1:
        to_keep.append(t[0])
# print(df)
# print(to_keep)
print(df.shape)
df = df[df['Traceroute ID'].isin(to_keep)]
print(df.shape)
df.to_csv('visualization_of_output.csv')
