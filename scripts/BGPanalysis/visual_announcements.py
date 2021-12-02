import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import numpy as np
from matplotlib.colors import LogNorm, Normalize
import os
sns.set_theme(style="whitegrid")

def reading_legitimate_actors():
    file = open('../../data/MetaInformation/legitimate_ASes.txt', 'r')
    legitimate_actors = {}
    for row in file.readlines():
        print(row)
        row = row.replace('\n','')
        legitimate_actors[row.split('|')[0]] = row.split('|')[1].split(' ')
    return legitimate_actors


def heatmap(category):
    #### reading data from RIPE History
    legitimate_actors = reading_legitimate_actors()
    df = pd.read_csv('../../data/history_ripe_complete.csv', index_col=0)
    print(df.columns)
    df.columns = ['Prefix','Origin','StartTime','EndTime','FullPeersSeeing','Visibility']
    df['Year'] = df['StartTime'].apply(lambda x : x.split('-')[0])
    ### create a bunch of dictionary to gather statistics (they will be pushed into dataframe later down the line)
    final_l = defaultdict(lambda : [])
    glob_dic = {}
    glob_dic_y = {}
    legal_actors = {}
    legitimate_announcements = 0
    illegitimate_announcements = 0
    #### prefixes that we consider
    DoD_addresses = ['6.0.0.0/8', '7.0.0.0/8', '11.0.0.0/8','9.0.0.0/8','16.0.0.0/8','19.0.0.0/8','21.0.0.0/8','22.0.0.0/8','26.0.0.0/8', '28.0.0.0/8', '29.0.0.0/8', '30.0.0.0/8', '33.0.0.0/8','43.0.0.0/8','48.0.0.0/8','56.0.0.0/8']
    Legitimate_Announcers = {'9.0.0.0/8':'IBM','16.0.0.0/8':'Hewlett-Packard','19.0.0.0/8':'Ford','25.0.0.0/8':'UK Ministry of Defence','48.0.0.0/8':'The Prudential Insurance Company of America','56.0.0.0/8':'United States Postal Service.','43.0.0.0/8':'Alibaba'
                             }
    all_the_origin_leakage = defaultdict(lambda : [])
    DoD_legitimate = ['DoD Network Information Center','Headquarters USAISC','United States Coast Guard','Air Force Systems Networking']
    set_of_leakers = defaultdict(lambda : [])
    tot_origin = set()
    burstiness = []
    for year in df.groupby('Year'):
        accross = []
        if category == 'number of announcements':
            dic = defaultdict(lambda :0)
        else:
            dic = defaultdict(lambda : [])
        for year_prefix in year[1].groupby('Prefix'):
            year_prefix_8s = year_prefix[0].split('.')[0] +'.0.0.0/8'
            if year_prefix_8s in DoD_addresses:
                for origin in year_prefix[1]['Origin']:
                    legitimacy = False
                    origin = str(origin)
                    tot_origin.add(origin)
                    if origin in ['2500','4690']:
                        legitimacy = True
                    if year_prefix_8s in Legitimate_Announcers:
                        if origin in legitimate_actors[Legitimate_Announcers[year_prefix_8s]]:
                            legitimacy = True
                    else:
                        for DoD_org in DoD_legitimate:
                            if origin in legitimate_actors[DoD_org]:
                                legitimacy = True
                    if year[0] =='2021' and origin != '8003':
                        print('hold on',origin)
                        set_of_leakers[year_prefix_8s].append(origin)
                    if legitimacy:
                        legitimate_announcements +=1
                        continue
                    illegitimate_announcements+=1
                    vision = year_prefix[1]['Visibility'].values
                    new_vision = []
                    for i in vision:
                        if i > 1:
                            i/=100.0
                            new_vision.append(i)
                        elif i < 0:
                            new_vision.append(0)
                        else:
                            new_vision.append(i)
                    l = new_vision
                    # dic[year_prefix[0]].append((len(vision),np.mean(l),np.median(l),np.percentile(l,5),np.percentile(l,95)))
                    # dic[year_prefix_8s].extend(origin)
                    if category != 'number of announcements':
                        dic[year_prefix_8s].append(np.median(l))
                    else:
                        dic[year_prefix_8s] += 1
                    final_l[str(year[0])+'-'+year_prefix[0]].append((len(vision),np.mean(l),np.median(l),np.percentile(l,5),np.percentile(l,95)))
                    accross.extend(l)
        if category == 'number of announcements':
            glob_dic[year[0]] = dic
        else:
            for key in dic:
                dic[key] = np.median(dic[key])
            glob_dic[year[0]] = dic
    df = pd.DataFrame.from_dict(glob_dic)
    df.fillna(0,inplace=True)
    print(df)
    df = df.sort_index()
    df = df.reindex(['6.0.0.0/8', '7.0.0.0/8','9.0.0.0/8','11.0.0.0/8','16.0.0.0/8','19.0.0.0/8','21.0.0.0/8','22.0.0.0/8','26.0.0.0/8', '28.0.0.0/8', '29.0.0.0/8','30.0.0.0/8', '33.0.0.0/8','43.0.0.0/8','48.0.0.0/8','56.0.0.0/8'])
    fig, ax = plt.subplots(figsize=(13, 7))
    # plot heatmap
    if category == 'number of announcements':
        b = sns.heatmap(df, cmap="Reds", square=True,
                   linewidth=0.3,norm=LogNorm())
        title = 'Number of illegitimate announcements \n in the squat space'
    else:
        title = 'Median visibility of illegitimate announcements \n in the squat space'
        b = sns.heatmap(df, cmap="Greens", square=True,
                   linewidth=0.3,)

    b.axes.set_title(title,fontsize=20)
    b.set_xlabel("Years",fontsize=20)
    b.set_ylabel("Prefixes",fontsize=25)
    b.tick_params(labelsize=24)
    cbar = ax.collections[0].colorbar
    # here set the labelsize by 20
    cbar.ax.tick_params(labelsize=20)
    plt.axhspan(0,2 , color='blue',fill=None)
    plt.axhspan(3,4, color='blue',fill=None)
    plt.axhspan(6,13,color='blue',fill=None)
    # (6 7 11 21 22 26 28 29 30 33)
    if category == 'number of announcements':
        plt.savefig('../../result/squat_prefixes_number_of_announcements.pdf')
    else:
        plt.savefig('../../result/squat_prefixes_median_visibility_of_announcements.pdf')
    print(len(tot_origin))
    print(legitimate_announcements)
    print(illegitimate_announcements)
    print(set_of_leakers)
    return set_of_leakers

def are_the_leakers_in_the_source(set_of_leakers):
    all_the_leakers = []
    for i in set_of_leakers.keys():
        all_the_leakers.extend(set_of_leakers[i])
    all_the_leakers = set(all_the_leakers)
    rows = []
    path = '../Statistics/count_statistics/'
    for months in ['01', '03', '04', '05']:
        for file in ['tracerouteasncounts-2021-' + months + '-10-2021-' + months + '-16.txt']:
            if file.split('.')[-1] == 'txt':
                file1 = open(path + file, "r")
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
    df = pd.DataFrame(rows, columns=col)
    dn = df[df['#Field:count'].astype('int') > 5000]
    # print(len(dn['endUserASN'].unique()))
    # print(len(df['endUserASN'].unique()))
    # rows = []
    # for file in ['tracerouteasncounts-2021-08-10-2021-08-16.txt', 'squatasncounts-2021-08-10-2021-08-16.txt']:
    #     if file.split('.')[-1] == 'txt':
    #         file1 = open(path + '/' + file, "r")
    #         col = file1.readline()
    #         col = col.replace('\n', '')
    #         # col = col.split('|')[0:6]
    #         col = col.strip()
    #         print(col)
    #         col = col.split('	')
    #         col.append('which_data')
    #
    #         for row in file1.readlines():
    #             # print(row)
    #             if row[0] == '#':
    #                 continue
    #             row = row.replace('\n', '')
    #             row = row.split('	')
    #             row.append(file.split('-')[0])
    #             rows.append(row)
    # dg = pd.DataFrame(rows, columns=col)
    source_that_was_here_earlier = 0
    new_source = 0
    print(len(df['endUserASN'].unique()))
    print(len(all_the_leakers))
    print(len(set(df['endUserASN'].unique())&all_the_leakers))
    print(len(set(dn['endUserASN'].unique())&all_the_leakers))
    df = []
    rows = []
    for months in ['01', '03', '04', '05']:
        for file in ['squatasncounts-2021-' + months + '-10-2021-' + months + '-16.txt']:
            if file.split('.')[-1] == 'txt':
                file1 = open(path + file, "r")
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
    df = pd.DataFrame(rows, columns=col)
    # print(len(dn['endUserASN'].unique()))
    # print(len(df['endUserASN'].unique()))
    # rows = []
    # for file in ['tracerouteasncounts-2021-08-10-2021-08-16.txt', 'squatasncounts-2021-08-10-2021-08-16.txt']:
    #     if file.split('.')[-1] == 'txt':
    #         file1 = open(path + '/' + file, "r")
    #         col = file1.readline()
    #         col = col.replace('\n', '')
    #         # col = col.split('|')[0:6]
    #         col = col.strip()
    #         print(col)
    #         col = col.split('	')
    #         col.append('which_data')
    #
    #         for row in file1.readlines():
    #             # print(row)
    #             if row[0] == '#':
    #                 continue
    #             row = row.replace('\n', '')
    #             row = row.split('	')
    #             row.append(file.split('-')[0])
    #             rows.append(row)
    # dg = pd.DataFrame(rows, columns=col)
    source_that_was_here_earlier = 0
    new_source = 0
    print(len(df['endUserASN'].unique()))
    print('Squatting')
    print(len(set(df['endUserASN'].unique())&all_the_leakers))


if __name__ == "__main__":
    are_the_leakers_in_the_source(heatmap('number of announcements'))
    # heatmap('median announcements')
