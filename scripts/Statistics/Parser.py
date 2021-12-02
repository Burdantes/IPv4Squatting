import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import figure
import pycountry_convert as pc
import os
from statsmodels.formula.api import ols
import sys
sys.path.append('../../')
from util import load_squatspace_default,load_dod_prefix
import ipaddr
from tqdm import  tqdm
import pickle
import pytricia
import time
import ast
from matplotlib_venn import venn3, venn3_circles
import matplotlib.pyplot as plt
import re
from collections import defaultdict
import dask.dataframe as dd

Legitimate_Announcers = {'9.0.0.0/8':'IBM','16.0.0.0/8':'Hewlett-Packard','19.0.0.0/8':'Ford','25.0.0.0/8':'UK Ministry of Defence','48.0.0.0/8':'The Prudential Insurance Company of America','56.0.0.0/8':'United States Postal Service.','43.0.0.0/8':'Alibaba'}
all_the_origin_leakage = defaultdict(lambda : [])
DoD_legitimate = ['DoD Network Information Center','Headquarters USAISC','United States Coast Guard','Air Force Systems Networking']
DoD_slash8 = ['6.0.0.0/8', '7.0.0.0/8', '11.0.0.0/8', '21.0.0.0/8', '22.0.0.0/8', '26.0.0.0/8',
                   '28.0.0.0/8', '29.0.0.0/8', '30.0.0.0/8', '33.0.0.0/8']

def union_org():
    org = []
    org_comparison = []
    for file in os.listdir('../../result/org_observed/'):
        print(file)
        # making sure that the file is a txt file
        if file.endswith('.txt'):
            if file.startswith('RIPE'):
                print('wait')
            with open('../../result/org_observed/' + file, "r+") as txt_mapped:
                for line in txt_mapped:
                    line = line.replace('/n','')
                    org.append(line)
    print(len(set(org)))
    return (list(set(org)))

def reading_legitimate_actors():
    file = open('../../data/MetaInformation/legitimate_ASes.txt', 'r')
    legitimate_actors = {}
    for row in file.readlines():
        print(row)
        row = row.replace('\n','')
        legitimate_actors[row.split('|')[0]] = row.split('|')[1].split(' ')
    return legitimate_actors

def comparing_new_ases_arriving(df):
    df = df[df['Prefix'].isin(load_dod_prefix())]
    month_after_the_announcements = ['2021-03-01','2021-01-01','2021-02-10','2021-03-10','2021-04-10','2021-05-10','2021-06-10']
    df_before = df[~df['Date'].isin(month_after_the_announcements)]
    df_after = df[df['Date'].isin(month_after_the_announcements)]
    print(df_after.shape,df_before.shape)
    squatting_org_after = df_after['squat_org'].value_counts().index
    squatting_org_before = df_before['squat_org'].value_counts().index
    squatting_ASes_after = df_after['squat_asn'].value_counts().index
    squatting_ASes_before = df_before['squat_asn'].value_counts().index
    squatting_ASes_after_only = list(set(squatting_ASes_after)-(set(squatting_ASes_before)))
    print('Org that are still here afterwards', len(set(squatting_org_before).intersection(set(squatting_org_after))))
    print('Org that appear only afterwards', len(set(squatting_org_after)-(set(squatting_org_before))))
    print('Org that appear only beforehand', len(set(squatting_org_before)-(set(squatting_org_after))))
    with open('../../result/CaseStudy/org_squatting_only_after.txt', 'w') as f:
        for ases in list(set(squatting_org_after)-(set(squatting_org_before))):
            print(ases, file=f)
    squatting_ASes_after = df_after['squat_org'].value_counts().index
    squatting_ASes_before = df_before['squat_org'].value_counts().index
    print('Org that are still here afterwards', len(set(squatting_ASes_before).intersection(set(squatting_ASes_after))))
    print('Org that appear only afterwards', len(set(squatting_ASes_after)-(set(squatting_ASes_before))))
    print('Org that appear only beforehand', len(set(squatting_ASes_before)-(set(squatting_ASes_after))))
    with open('../../result/CaseStudy/ases_squatting_only_after.txt', 'w') as f:
        for ases in list(set(squatting_ASes_after)-(set(squatting_ASes_before))):
            print(ases, file=f)
    with open('../../result/CaseStudy/org_squatting_DoD_after.txt', 'w') as f:
        for ases in list(squatting_org_after):
            print(ases, file=f)
    print(df[df.squat_asn == df.src_asn].shape)
    print(df.shape)
    dg = df[df.squat_asn!= df.src_asn]
    print(dg.shape)
    rows = []
    for months in ['01']:
        for file in ['count_statistics/tracerouteasncounts-2021-' + months + '-10-2021-' + months + '-16.txt']:
            if file.split('.')[-1] == 'txt':
                file1 = open(file, "r")
                col = file1.readline()
                col = col.replace('\n', '')
                # col = col.split('|')[0:6]
                col = col.strip()
                print(col)
                col = col.split('	')
                col.append('which_data')

                for row in file1.readlines():
                    # print(row)
                    if row[0] == '#':
                        continue
                    row = row.replace('\n', '')
                    row = row.split('	')
                    row.append(file.split('-')[0])
                    rows.append(row)
    counts = 0
    df = pd.DataFrame(rows, columns=col)
    print(df)
    for ases in squatting_ASes_after_only:
        print(ases,df[df['endUserASN'] == str(ases)])
        if str(ases) in df['endUserASN'].values:
            dm = df[df['endUserASN'] == str(ases)]
            if int(dm['#Field:count'].values[0]) > 5000:
                counts += 1
    print('Fraction of ASes that were seen beforehand', float(counts)/len(squatting_ASes_after_only))

def attribute_usage(df):
    l = defaultdict(lambda : [])
    path = '../ValidationStatistics/router_config/'
    for file in os.listdir(path):
        print(file)
        # if file.split('.')[0][-1] == 'E' or file.split('.')[0][-1] == 'F':
        if len(file.split('_'))==1:
            file1 = open(path +file , "r")
            txt = file1.readline().replace('\n','')
            print(txt)
            interm = ast.literal_eval(txt)
            print(interm)
            for i in list(interm):
                l[i].append('Router Config')
            # l = l.union(interm)
            # l = l.upd
    path = "../ValidationStatistics/NAT_statistics/"
    dic_val = {}
    for file in os.listdir(path):
        print(file)
        if len(file.split('_')) > 1:
            file1 = open(path + file, "r")
            for row in file1.readlines():
                row = row.replace('\n', '')
                # print(txt)
                # l.add(row.split('|')[1])
                l[row.split('|')[1]].append('NAT')
                dic_val[row.split('|')[0]] = row.split('|')[1]
        # interm = ast.literal_eval(txt)
        # print(interm)
        # l = l.union(interm)
    # l = list(set(l))
    series = {}
    for ind,asn in zip(df.index,df['squat_asn']):
        if asn in l:
            series[ind] = ('.').join(list(set(l[asn])))
        else:
            series[ind] = 'Unattributed'
    df['Attribution'] = pd.Series(series)
    return df

def correlation_ratio(categories, measurements):
    fcat, _ = pd.factorize(categories)
    cat_num = np.max(fcat)+1
    y_avg_array = np.zeros(cat_num)
    n_array = np.zeros(cat_num)
    for i in range(0,cat_num):
        cat_measures = measurements[np.argwhere(fcat == i).flatten()]
        n_array[i] = len(cat_measures)
        y_avg_array[i] = np.average(cat_measures)
    y_total_avg = np.sum(np.multiply(y_avg_array,n_array))/np.sum(n_array)
    numerator = np.sum(np.multiply(n_array,np.power(np.subtract(y_avg_array,y_total_avg),2)))
    denominator = np.sum(np.power(np.subtract(measurements,y_total_avg),2))
    if numerator == 0:
        eta = 0.0
    else:
        eta = np.sqrt(numerator/denominator)
    return eta


def parsing_data(directory):
    # rows = set()
    not_mapped = 0
    temp_file = 'temp/processed-temp-file.txt'
    if not(temp_file.split('/')[1] in os.listdir('temp/')):
        out_file = open(temp_file, 'w')  # use this to store intermediate results to disk
        list_of_elem = os.listdir(directory)
        list_of_elem.append('../Ark-Attribution-2021-01-01.txt')
        print(list_of_elem)
        for file in list_of_elem:
            print(file)
            # if file.split('-')[0] != '../Ark' and file.split('-')[0] != 'RIPE' and file.split('-')[3]!='11':
            #     continue
            # making sure that the file is a txt file
            if file.endswith('.txt'):
                #     continue
                # if file.split('-')[-2] != month_to_be_selected:
                #     continue
                with open(directory + '/' + file, "r+") as txt_mapped:
    
                    ### reading the first row and manually adding the right columns
                    col = next(txt_mapped)  # txt_mapped.readline()
                    col = col.replace('\n', '')
                    # col = col.split('|')[0:6]
                    col = col.split('|')
                    col = col[0:7]
                    print(col)
                    # if file.startswith('../Ark'):
                    #     col = col[0:-1]
                    subdate = file.split('.')[0]
                    date = ("-").join(subdate.split('-')[2:5])
                    # if int(date.split('-')[0]) == 2021 and int(date.split('-')[1]) == 1:
                    #     col.append('Prefix')
                    col.append('Prefix')
                    col.append('Date')
                    col.append('Data Source')
                    print(file)
    
                    data_source = file.split('-')[0]
                    print(data_source)
                    print(col)
                    for line in txt_mapped:
                        if line.startswith('#'):
                            continue
                        # read in buffered number of lines as a time
                        line = line.strip()
                        # row = tqdm(line)  # !! apply whatever logic tqdm was doing on a per line basis !!
                        row = line
                        if row[-2] == '*' and row[-3] == '*':
                            not_mapped += 1
                            continue
    
                        # data cleaning stuff
                        row = row.replace('\n', '')
                        row = row.split('|')
                        # row = row[0:7]
                        if file.startswith('../Ark'):
                            if row[-1] == 'standard':
                                row = row[0:-1]
                            else:
                                continue
                        if data_source == '../Ark':
                            data_source = 'Ark'
                        elif data_source == 'squatspace':
                            data_source = 'Microsoft'
                        row = row[0:7]
                        row_prefix = row[2].split('.')[0] + '.0.0.0/8'
                        row.append(row_prefix)
                        row.append(date)
                        row.append(data_source)
                        # if len(row) != len(col):
    
                        row = row[0:10]
                        out_str = '|'.join(row)
                        out_file.write(out_str)
                        out_file.write('\n')
        out_file.close()
    else:
        list_of_elem = os.listdir(directory)
        for file in list_of_elem:
            if file.endswith('.txt'):
                #     continue
                # if file.split('-')[-2] != month_to_be_selected:
                #     continue
                with open(directory + '/' + file, "r+") as txt_mapped:
                    ### reading the first row and manually adding the right columns
                    col = next(txt_mapped)  # txt_mapped.readline()
                    col = col.replace('\n', '')
                    # col = col.split('|')[0:6]
                    col = col.split('|')
                    col = col[0:7]
                    print(col)
                    # if file.startswith('../Ark'):
                    #     col = col[0:-1]
                    subdate = file.split('.')[0]
                    date = ("-").join(subdate.split('-')[2:5])
                    # if int(date.split('-')[0]) == 2021 and int(date.split('-')[1]) == 1:
                    #     col.append('Prefix')
                    col.append('Prefix')
                    col.append('Date')
                    col.append('Data Source')
            break
    start = time.process_time()
    # df = pd.DataFrame(list(rows),columns=col)
    print(col)
    df = pd.read_csv(temp_file,header=None,sep='|')
    # read_csv is really fast
    df.columns = col
    print('Processing Time', time.process_time() - start)
    print(not_mapped)
    return df


def cleaning_from_legitimate_actors(df,dico):
    pyt = pytricia.PyTricia()
    # parsing_who_ISdata()
    is_it_legitimate = {}
    for pre in dico.keys():
        asn = dico[pre]
        pyt[pre] = asn
    print(df.columns)
    all_the_origin_leakage = defaultdict(lambda: [])
    legitimate_actors = reading_legitimate_actors()

    for index,hop,org,sq_asn in tqdm(zip(df.index,df['squat_ip'],df['squat_rir'],df['squat_asn'])):
        asn = str(pyt.get(hop))
        squat_prefix = hop.split('.')[0] + '.0.0.0/8'
        if asn.lower() == org.lower():
            # print('HOLD ON')
            is_it_legitimate[index] =False
        elif org in DoD_legitimate:
            # print('DoD stuff')
            is_it_legitimate[index] = False
        elif squat_prefix in Legitimate_Announcers:
            if sq_asn in legitimate_actors[Legitimate_Announcers[squat_prefix]]:
                is_it_legitimate[index] = False
            elif sq_asn == '2500' or sq_asn == '4690':
                print('THIS IS WIDE')
                is_it_legitimate[index] = False
            else:
                is_it_legitimate[index] = True
        else:
            is_it_legitimate[index]= True
    df = df[df['squat_org'] != 'Microsoft Corporation']
    df['legitimate'] = pd.Series(is_it_legitimate)
    print(df)
    df = df[df['legitimate']]
    print(df)
    return df

# def parsing_who_ISdata(path):
#     dict_legitimate_announcements = {}
#     file1 = open(path, "r")
#     row = file1.readlines()
#     for t in tqdm(row):
#         t = t.replace('\'','')
#         t = t.replace('\n','')
#         t = t.replace('[','')
#         t = t.replace(']','')
#         l = t.split(',')
#         if l[0].split('.')[0] in ['6','7','9','11','16','19','21','22','25','26','28','29','30','33','43','48','56']:
#             dict_legitimate_announcements[l[0]] = l[-1]
#     with open('../data/legitimate_announcements.pickle', 'wb') as handle:
#         pickle.dump(dict_legitimate_announcements, handle, protocol=pickle.HIGHEST_PROTOCOL)
#     return dict_legitimate_announcements

def discarding_org_with_less(dl,val_traceroutes,val_source,month):
    rows = []
    for file in ['../ValidationStatistics/count_statistics/tracerouteasncounts-2021-'+month+'-10-2021-'+month+'-16.txt', '../ValidationStatistics/count_statistics/squatasncounts-2021-'+month +'-10-2021-'+month+'-16.txt']:
        if file.split('.')[-1] == 'txt':
            file1 = open(file, "r")
            col = file1.readline()
            col = col.replace('\n', '')
            # col = col.split('|')[0:6]
            col = col.strip()
            print(col)
            col = col.split('	')
            col.append('which_data')

            for row in file1.readlines():
                # print(row)
                if row[0] == '#':
                    continue
                row = row.replace('\n', '')
                row = row.split('	')
                print(file.split('-')[0].split('/')[3])
                row.append(file.split('-')[0].split('/')[3])
                rows.append(row)
    df = pd.DataFrame(rows,columns=col)
    # df = pd.read_csv('../ValidationStatistics/filters/raw-traceroutes-info.csv')
    dg = df[df['which_data'] == 'squatasncounts']
    dg['#Field:count'] = dg['#Field:count'].astype(int)
    dg['sourceIPCount'] = dg['sourceIPCount'].astype(int)
    dg['endUserASN'] = dg['endUserASN'].astype(str)
    print(dl['src_asn'])
    dg = dg[dg['#Field:count']>=val_traceroutes]
    dg = dg[dg['sourceIPCount']>=val_source]
    print(dg)
    dl = dl[dl['src_asn'].isin(dg['endUserASN'].values)]
    # dl[dl.index.isin]
    return dl

def generating_venn_diagram(df):
    ases_for_different_months = {}
    for date, dg in df.groupby('Date'):
        ases_for_different_months[date] = list(dg['squat_org'].unique())
    val1 = len(set(ases_for_different_months['2021-03-10']) - (
        set(ases_for_different_months['2021-04-10']).union(set(ases_for_different_months['2021-05-10']))))
    val2 = len(set(ases_for_different_months['2021-05-10']) - (
        set(ases_for_different_months['2021-03-10']).union(set(ases_for_different_months['2021-04-10']))))
    val3 = len(set(ases_for_different_months['2021-04-10']) - (
        set(ases_for_different_months['2021-05-10']).union(set(ases_for_different_months['2021-03-10']))))
    val4 = len(set(ases_for_different_months['2021-03-10']).union(set(ases_for_different_months['2021-04-10'])) - (
        set(ases_for_different_months['2021-05-10'])))
    val5 = len(set(ases_for_different_months['2021-03-10']).union(set(ases_for_different_months['2021-05-10'])) - (
        set(ases_for_different_months['2021-04-10'])))
    val6 = len(set(ases_for_different_months['2021-04-10']).union(set(ases_for_different_months['2021-05-10'])) - (
        set(ases_for_different_months['2021-03-10'])))
    val7 = len(set(ases_for_different_months['2021-04-10']) & (set(ases_for_different_months['2021-05-10'])) & (
        set(ases_for_different_months['2021-03-10'])))
    print('March only', val1)
    print('April Only', val3)
    print('May Only', val4)
    print('March & April Only', val3)
    print('March & May Only', val5)
    print('April & May Only', val6)
    print('All', val7)
    val_all = len(list(df['squat_org'].unique()))
    print(val_all)
    venn3(subsets = (val1, val3, val4, val2, val5, val6, val7), set_labels = ('March', 'April', 'May'), alpha = 0.5)
    c = venn3_circles(subsets = (val1, val3, val4, val2, val5, val6, val7), linewidth=2, color='black')
    plt.savefig('../../results/venndiagram.pdf')

if __name__ == '__main__':
    # Generating the Dataframe with the observed squatters
    union_org()
    df = parsing_data('../../data/AttributedData/updated_format_squatters/')
    with open('../../data/BGP/legitimate_announcements.pickle', 'rb') as handle:
        dict_legitimate_announcements =pickle.load(handle)
    df = cleaning_from_legitimate_actors(df,dict_legitimate_announcements)
    # df.to_csv('RIPEAtlas_squatters.csv')
    print(df.shape)
    print(df.columns)
    # df = attribute_usage(df)
    print(df['Data Source'].unique())
    dm = set(df[df['Data Source'] == 'RIPE']['squat_org'].unique())
    dh = set(df[df['Data Source'] == 'Ark']['squat_org'].unique())
    dn = set(df[df['Data Source'] == 'Microsoft']['squat_org'].unique())
    print('######### Number of Squat ASN #########')
    print('RIPE ', len(dm))
    print('Ark', len(dh))
    print('Microsoft', len(dn))
    print('RIPE intersection Microsoft', len(dm.intersection(dn)))
    # df = df[df['Attribution'] == 'Unattributed']
    # df = discarding_org_with_less(df, 1000,10,'03')
    # print(df)# t

    print('Observed', df.shape[0])
    print('Unmapped',df[(df['squat_org']=='*') & (df['squat_rir'] == '*')].shape[0])
    print('Stat',1-float(df[(df['squat_org']=='*') & (df['squat_rir'] == '*')].shape[0])/df.shape[0])
    # df = df[df['Data Source']=='RIPE']
    # print(len(set(df['squat_org'].unique())))
    print('Number of org',len(set(df['squat_org'].unique()).union(set(df['squat_rir'].unique()))))
    # print(df['src_ip'].value_counts())
    print('Number of source ASN',len(df['src_asn'].unique()))
    print('Number of different IP observed',len(df['squat_ip'].unique()))
    slash_24 = []
    # df = discarding_org_with_less(df,1000,10)
    # print(df['src_asn'].value_counts())
    for t in df['squat_ip'].value_counts().index:
        slash_24.append(('.').join(t.split('.')[:-1]))
    print('Number of squat IP',len(list(set(slash_24))))
    # res = dict(df['src_ip'].value_counts())
    # slash_24_bis = []
    # for t in df['squat_ip'].value_counts().index:
    #     slash_24_bis.append(('.').join(t.split('.')[:-1]))
    # print(len(list(set(slash_24_bis))))
    # print(df['squat_rir'].count_values())
    print(len(list(set(df['squat_org'].unique()).union(set(df['squat_rir'].unique())))))
    print(len(set(df['squat_org'].unique()).union(set(df['squat_rir'].unique()))))
    with open("../../result/org_observed_ripe.txt", 'w+') as file:
        for row in list(set(df['squat_org'].unique()).union(set(df['squat_rir'].unique()))):
                file.write(row + '\n')
    # dict_count = {}
    # for orgs in df.groupby('squat_org'):
        # dict_count[]
    # all_the_stuff = []
    # for t in res.keys():
    #     all_the_stuff.append(str(t) + '\t' )
    # # print(all_the_stuff)
    # print(res)
    # for t in res.keys():
    #     all_the_stuff.append(str(t) + '\t' )
    # with open("asns_router_all_upd.txt", 'w') as file:
    #     for row in all_the_stuff:
    #             file.write(row + '\n')
    # # print(df['squat_asn'].value_counts().index)
    # # prefixes = load_squatspace_default().prefixes()
    ind_which_squat_addresses = {}
    # # print(len(df.index))
    for i,t in tqdm(zip(df.index,df['squat_ip'])):
        ind_which_squat_addresses[i] = t.split('.')[0] +'.0.0.0/8'
        # for collect in prefixes:
        #     if ipaddr.IPNetwork(t) in (ipaddr.IPNetwork(collect)):
        #         ind_which_squat_addresses[i] = t.split('.')[0]+'.0.0.0/8'
    df['squat_addresses'] = pd.Series(ind_which_squat_addresses)
    df = df[df['squat_asn']!='*']
    with open('../../data/continuing_squatters.txt','w+') as f:
        dg = df[df['squat_addresses'].isin(DoD_slash8)]
        print(dg)
        for row in dg.groupby(['squat_addresses', 'squat_org']):
            print(row[0][0] + ' ' + row[0][1] ,file=f)
    # print(df.columns)
    # df.to_csv('../data/all_thetraceroutes.csv')

    val = df.groupby(['squat_addresses','squat_org']).size()
    print(val)
    print(df.groupby(['squat_addresses','squat_org']).size().reset_index().groupby('squat_addresses')[[0]].sum())
    #####
    # generating_venn_diagram(df)
    ##### Counting the number of different /24 per data sources
    df = df[df['squat_org'] != 'Microsoft Corporation']
    # df = df[df['squat_org']!= '*']
    df = df[(df['squat_org'] != '*') | (df['squat_rir'] != '*')]
    dm = df.groupby(['squat_addresses', 'squat_org']).size().reset_index().groupby('squat_addresses')[[0]].count()
    dn = dm / (float(dm.sum()))
    prefix_24 = set()
    for source, dg in df.groupby('Data Source'):
        unique_24 = (dg['squat_ip'].apply(lambda x: ('.').join(x.split('.')[:-1])).unique())
        print(source, len(unique_24))

    dg = df.value_counts('squat_org')
    df = df[df['squat_org'] != 'Microsoft Corporation']
    # df = df[df['squat_org']!= '*']
    df = df[(df['squat_org']!='*')|(df['squat_rir'] != '*')]
    print(df[df['squat_org'].isin(dg[dg<5].index)].shape)
    dm = df.groupby(['squat_addresses', 'squat_org']).size().reset_index().groupby('squat_addresses')[[0]].count()
    dn = dm/(float(dm.sum()))
    print(dn*100)

    comparing_new_ases_arriving(df)

    # count_diff = 0
    # rir_more_info = 0
    # no_mapping = 0
    # counters = 0
    # ASes = []
    # ASes_otherwise = []
    # for t,s in zip(df['squat_org'],df['squat_rir']):
    #     if t == '*' and s!= '*':
    #         rir_more_info +=1
    #     elif t != s:
    #         ASes.append(t + '\t')
    #         count_diff +=1
    #     elif t == '*' and s =='*':
    #         no_mapping +=1
    #     else:
    #         ASes_otherwise.append(t + '\t')
    #         counters +=1
    # print(len(list(set(ASes)-set(ASes_otherwise))))
    # print(counters,count_diff,rir_more_info)
    # # with open("asns_router_all.txt", 'w') as file:
        # for row in :
        #         file.write(row + '\n')
    # for t in df.groupby(['squat_rir']):
    #     count_df = t[1]['squat_addresses'].value_counts()
    #     test = count_df[count_df>9]
    #     if t[1]['squat_addresses'].value_counts().shape[0] >= 5 :
    #         counters +=1
    # print(counters)
            # print(t[1]['squat_addresses'].value_counts())
    # print(count_diff,rir_more_info,no_mapping)
    # print(df.shape)
# #     for t in df.groupby(['squat_org']):
# #         print(t[1])
# #     dic_diff ={}
# #     for t in df.groupby(['squat_org']):
# #         val = t[1]
# #         dic_diff[t[0]] = val['squat_addresses'].value_counts().shape[0]
# #     print(dic_diff)
# #     from collections import Counter
# #     m = dict(Counter(list(dic_diff.values())))
# #     print(sum(list(m.values())))
# #     k = sum(list(m.values()))
# #     print(m)
# #     percentage = {}
# #     for t in m:
# #         percentage[t] = m[t]/float(k)
# #     print(percentage)
# #     percentage = dict(sorted(percentage.items(), key=lambda item: item[1],reverse=True))
# #     tot = 0
# #     for t in percentage:
# #         tot += percentage[t]
# #         percentage[t] = tot
# #     print(percentage)
# # # print(sum(list(dic_diff.values())))
# # #####
    AS_level_metainfos = pd.read_pickle('../../data/BGP/resulting_graph_May2021.pickle')
    # for s in df['squat_asn'].value_counts().index:
    #     if s != '*':
    dg_squat = df['squat_asn'].value_counts()
    squatting_test  = {}
    # file1 =  open('../data/jiangchen_output.txt','r')
    list_of_ASes_arkipelago= []
    # for i in union_org():
    #     i = i.replace('\n','')
    #     l = i.split(' ')[1:]
    #     list_of_ASes_arkipelago.extend(l)
    union =  union_org()
    for ind,s in zip(AS_level_metainfos.index,AS_level_metainfos['asNumber']):
        if s in union:
            squatting_test[ind] = 'Squatting'
        elif s in list_of_ASes_arkipelago:
            squatting_test[ind] = 'Arkipelago Squatting'
        else:
            squatting_test[ind] = 'Non Squatting'
    AS_level_metainfos['Squatters'] = pd.Series(squatting_test)
    AS_level_metainfos = AS_level_metainfos.fillna(0)
    AS_level_metainfos = AS_level_metainfos.sort_values(by=['ASCone'],ascending=False)
    corr = AS_level_metainfos.corr()
    # AS_level_metainfos = AS_level_metainfos[AS_level_metainfos.index.isin(AS_level_metainfos.index[0:250])]
    print(AS_level_metainfos['Squatters'].value_counts())
    # print(correlation_ratio(AS_level_metainfos['Squatters'],AS_level_metainfos['Eyeballs']))
    df_metainfos =AS_level_metainfos[AS_level_metainfos.asNumber.isin(df['squat_asn'].value_counts().index)][['Eyeballs','Rank','lenPref','ASType','asName','Country','asNumber','ASCone']]
    df_metainfos.columns = ['Eyeballs','Rank','Number of Prefix Announced','AS Type','AS Name','Country','AS Number',"CustomerCones"]
    print(df_metainfos.index)
    df_metainfos.index = df_metainfos['AS Number']
    # df_metainfos['Count'] = pd.Series(dict(dg_squat[dg_squat.index.isin(df_metainfos.index)]))
    import seaborn as sns
    df_metainfos['Eyeballs'] = df_metainfos['Eyeballs'].astype(float)
    df_metainfos['Rank'] = df_metainfos['Rank'].astype(float)
    df_metainfos.to_csv('../../results/squatters_metainfo.csv')
#     corr = df_metainfos.corr()
#     print(corr)
#     model2 = ols("Count ~ Eyeballs+CustomerCones", data=df_metainfos).fit()
#     print(model2.summary())
#     print(model2.fittedvalues)
#     df_metainfos = df_metainfos.sort_values(by=['Count'],ascending=False)
#     continents = {}
#     for ind,t in zip(df_metainfos.index,df_metainfos['Country']):
#         try:
#             continent_name = pc.country_alpha2_to_continent_code(t)
#             continents[ind] = continent_name
#         except:
#             continents[ind] = t
#     df_metainfos['Continent'] = pd.Series(continents)
#     df_metainfos.fillna(0,inplace=True)
#     print(df_metainfos)
#     # print(df_metainfos)
#     # print(df_metainfos['Country'])
#     # figure(figsize=(8, 6), dpi=260)
#     fig = figure(figsize=(9, 6), dpi=450)
#     # df_metainfos = df_metainfos.sort_values(by=['Continent'])
#     # sns.scatterplot(
#     #     data=df_metainfos, x="Eyeballs", y="CustomerCones", hue="Continent", size="Count",
#     #     sizes=(40, 400)
#     # )
#     # # fig.suptitle('', fontsize=20)
#     # plt.xlabel('# of Eyeballs in log 10', fontsize=24)
#     # plt.ylabel('# of ASes in Customer Cone', fontsize=24)
#     # locs, labels = plt.xticks()
#     # plt.xticks(locs,['1','$10^2$','$10^4$','$10^6$','$10^8$'],fontsize=20)
#     # plt.yticks(fontsize=20)
#     # plt.legend(fontsize='x-large', title_fontsize='35')
#
#
#     dl =pd.read_csv('../data/information-about-ASes.csv',index_col = 0)
#     dl.index = dl.index.astype('str')
#     # for t in dl.index:
#     #     if str(t) in df_metainfos['AS Number'].values:
#     #         print(t,df_metainfos[df_metainfos['AS Number']==str(t)])
#     print(df_metainfos[df_metainfos['AS Number'].isin(dl.index)])
#     import re, seaborn as sns
#     import numpy as np
#
#     from matplotlib import pyplot as plt
#     from mpl_toolkits.mplot3d import Axes3D
#     from matplotlib.colors import ListedColormap
#
#     # df_metainfos['CustomerCones'] = df_metainfos['CustomerCones'].astype(float)
#     # df_metainfos['CustomerCones'] = df_metainfos['CustomerCones'].apply(lambda x: np.log10(x + 1))
#
#     # df_metainfos['Number of Prefix Announced'] = df_metainfos['Number of Prefix Announced'].astype(float)
#     # df_metainfos['Number of Prefix Announced'] = df_metainfos['Number of Prefix Announced'].apply(lambda x: np.log10(x + 1))
#     from sklearn.preprocessing import MinMaxScaler
#     # generate data
#     df_metainfos.fillna(0,inplace=True)
#     x = df_metainfos["Eyeballs"]
#     y = df_metainfos["CustomerCones"]
#     z = df_metainfos["Number of Prefix Announced"]
#     # axes instance
#     # ax = Axes3D(fig)
#     # fig.add_axes(ax)
#     from sklearn.cluster import KMeans,SpectralClustering
#     from sklearn import datasets
#     X = df_metainfos[['Eyeballs','CustomerCones','Number of Prefix Announced']].values
#     # scaler = MinMaxScaler()
#     # fit = scaler.fit(X)
#     # X = scaler.transform(X)
#     estimators = [('k_means_4', KMeans(n_clusters=4))]
#     # estimators = [('spectral',SpectralClustering(n_clusters=3,assign_labels='discretize',))]
#     colors = []
#     for name, est in estimators:
#         fig = plt.figure(figsize=(10, 10))
#         ax = Axes3D(fig, rect=[0, 0, .95, 1],azim=60)
#         est.fit(X)
#         labels = est.labels_
#         print(labels)
#         for t in labels:
#             if t == 0:
#                 colors.append('purple')
#             elif t == 1:
#                 colors.append('b')
#             elif t == 2:
#                 colors.append('g')
#             elif t == 3:
#                 colors.append('yellow')
#         ax.scatter(X[:, 0], X[:, 1], X[:, 2],
#                    c=colors, s = 25, edgecolor='k')
#
#         # ax.w_xaxis.set_ticklabels([])
#         # ax.w_yaxis.set_ticklabels([])
#         # ax.w_zaxis.set_ticklabels([])
#         ax.set_xlabel('# of Eyeballs (log)',fontsize = 20)
#         ax.set_ylabel('# of ASes in CC',fontsize=20)
#         ax.set_zlabel('# of Prefix Announced',fontsize=20)
#         ax.zaxis.set_tick_params(labelsize=15)
#         ax.xaxis.set_tick_params(labelsize=15)
#         ax.yaxis.set_tick_params(labelsize=15)
#         ax.dist = 12
#     fig.savefig('spectral_embedding_categories.png')
#
#     DoD_data = pd.read_pickle('../data/DoD_Data_with_adjacentmapping.pickle')
#     known_squatters = []
#     for k,i in zip(DoD_data.index,DoD_data['AS mapping']):
#         tot_squat = []
#         print(i)
#         try:
#             for j in i:
#                 if str(j) in df_metainfos['AS Number'].values:
#                     tot_squat.append(str(j))
#         except:
#             tot_squat.append(None)
#         known_squatters.append(tot_squat)
#     DoD_data['Known Squatters'] = known_squatters
#     plt.show()
#     # dknown_squatters = df_metainfos[df_metainfos['AS Number'].isin(dl.index)]
#     DoD_data.to_csv('../results/DoD_Data_withsquatterinfos.csv')#
#     df_metainfos = df_metainfos[df_metainfos.index.isin(df_metainfos.index[0:15])]
#     df_metainfos.to_csv('../results/squatting_entities.csv')
    # plt.savefig('../results/actor_based.svg')