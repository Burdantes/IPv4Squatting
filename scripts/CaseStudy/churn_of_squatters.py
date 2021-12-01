import pandas as pd
import numpy as np

def comparing_new_ases_arriving():
    df = pd.read_csv('../Jiangchen_Output/all_the_squatting_organisation.csv', index_col=0)
    df = df[df['squat_asn'] != '*']
    file1 = open("dod-asns-after.txt", "r+")
    ASes = []
    for t in file1.readlines():
        ASes.append(t.replace('\n',''))
    df['squat_asn'] = df['squat_asn'].astype(str)
    df['src_asn'] = df['src_asn'].astype(str)
    month_after_the_announcements = ['2021-02-10','2021-03-10','2021-04-10','2021-05-10','2021-06-10']
    dg = df[~df['Date'].isin(month_after_the_announcements)]
    print(dg)
    squatting_ASes_before = dg['squat_asn'].value_counts().index
    print(len(set(squatting_ASes_before)-set(ASes)))
    print(squatting_ASes_before)
    df['squat_asn']= df['squat_asn'].astype(str)
    df['src_asn'] = df['src_asn'].astype(str)
    print(df[df.squat_asn == df.src_asn].shape)
    print(df.shape)
    dg = df[df.squat_asn!= df.src_asn]
    print(dg.shape)

comparing_new_ases_arriving()