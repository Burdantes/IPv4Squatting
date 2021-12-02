import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
def analyzingclients():
    rows = []
    for file in ['count_statistics/tracerouteasncounts-2021-01-10-2021-01-16.txt','count_statistics/squatasncounts-2021-01-10-2021-01-16.txt']:
        if file.split('.')[-1] == 'txt':
            file1 = open(file, "r")
            col = file1.readline()
            col = col.replace('\n', '')
            col = col.strip()
            print(col)
            col = col.split('	')
            col.append('which_data')

            for row in file1.readlines():
                if row[0] == '#':
                    continue
                row = row.replace('\n','')
                row = row.split('	')
                row.append(file.split('-')[0].split('/')[1])
                rows.append(row)
    df = pd.DataFrame(rows,columns=col)
    df.to_csv('log/raw-traceroutes-info.csv')
    print(df)
    is_it_squatting = {}
    dl = df[df['which_data'] == 'tracerouteasncounts']
    dg = df[df['which_data'] == 'squatasncounts']
    dl['#Field:count'] = dl['#Field:count'].astype(float)
    dg['#Field:count'] = dg['#Field:count'].astype(float)
    sum_all_traceroutes = dl['#Field:count'].sum()
    print(dl.quantile(0.1))
    AS_level_metainfos = pd.read_pickle(
        '../../data/BGP/resulting_graph_May2021.pickle')
    print(AS_level_metainfos.columns)
    total_df = []
    final_value = []
    for number in range(500,5000,500):
        for feature in ['lenPref']:
        # for feature in ['ASCone']:
            AS_level_metainfos = AS_level_metainfos.sort_values(by=[feature],ascending=False)
            AS_level_metainfos_1 = AS_level_metainfos.head(number)
            print(AS_level_metainfos.shape)
            seen_squatted = 0
            seen_non_squatted = 0
            notseen = 0
            frequency_squatted = []
            frequency_non_squatted = []
            frequency_source_squatted = []
            # frequency = pd.read_csv('statistics_of_frequency.csv',index_col=0)
            # print(frequency)
            from collections import defaultdict
            number_of_traceroutes= defaultdict(lambda : [])
            content_not_seen = 0
            content_not_squatted = 0
            content_squatted = 0
            access_network_not_seen = 0
            access_network_not_squatted  = 0
            access_network_squatted = 0
            transit_not_seen = 0
            transit_not_squatted  = 0
            transit_squatted = 0
            none_squatted = 0
            none_not_squatted = 0
            none_not_seen = 0
            counting = 0
            top_users = 0
            for t,s,eyeball,u in tqdm(zip(AS_level_metainfos_1['asNumber'],AS_level_metainfos_1['ASCone'],AS_level_metainfos_1['Eyeballs'],AS_level_metainfos_1['ASType'])):
                try:
                    eyeball = int(eyeball)
                except:
                    eyeball = 0
                s = int(s)
                # counting +=1
                if t in dg['endUserASN'].values:
                    if int(dl[dl['endUserASN']==t]['#Field:count'].values[0]) < 5000:
                        if u == 'Content':
                            content_not_seen += 1
                        elif eyeball > 10 ** 5:
                            access_network_not_seen += 1
                        elif eyeball < 10 ** 5 and eyeball > 10 ** 2 and s > 6:
                            transit_not_seen += 1
                        elif s > 20:
                            transit_not_seen += 1
                        else:
                            none_not_seen += 1
                        notseen += 1
                    else:
                        seen_squatted +=1
                        number_of_traceroutes['seen_squatted'].append(int(dl[dl['endUserASN']==t]['#Field:count'].values[0]))
                        top_users += int(dl[dl['endUserASN']==t]['#Field:count'].values[0])
                        total_df.append([t,float(dg[dg['endUserASN']==t]['sourceIPCount'].values[0]),int(dl[dl['endUserASN']==t]['#Field:count'].values[0]),'Squatted ' + feature ,feature])
                        frequency_source_squatted.append(float(dg[dg['endUserASN']==t]['sourceIPCount'].values[0])/float(dl[dl['endUserASN']==t]['sourceIPCount'].values[0]))
                        if float(dg[dg['endUserASN']==t]['#Field:count'].values[0])/float(dl[dl['endUserASN']==t]['#Field:count'].values[0]) > 1 :
                            print(t)
                            continue
                        frequency_squatted.append(float(dg[dg['endUserASN']==t]['#Field:count'].values[0])/float(dl[dl['endUserASN']==t]['#Field:count'].values[0]))
                        # print(frequency_source_squatted[-1],frequency_squatted[-1])
                        if u == 'Content':
                            content_squatted += 1
                        elif eyeball > 10 ** 5:
                            access_network_squatted += 1
                        elif eyeball < 10 ** 5 and eyeball > 10 ** 2 and s > 6:
                            transit_squatted += 1
                        elif s > 20:
                            transit_squatted += 1
                        else:
                            none_squatted += 1
                elif t in dl['endUserASN'].values:
                    if int(dl[dl['endUserASN']==t]['#Field:count'].values[0]) < 5000:
                        if u == 'Content':
                            content_not_seen += 1
                        elif eyeball > 10 ** 5:
                            access_network_not_seen += 1
                        elif eyeball < 10 ** 5 and eyeball > 10 ** 2 and s > 6:
                            transit_not_seen += 1
                        elif s > 20:
                            transit_not_seen += 1
                        else:
                            none_not_seen += 1
                        notseen += 1
                    else:
                        seen_non_squatted +=1
                        number_of_traceroutes['seen_non_squatted'].append(int(dl[dl['endUserASN']==t]['#Field:count'].values[0]))
                        # frequency_non_squatted.append(float(dg[dg['endUserASN']==t]['#Field:count'].values[0])/float(dl[dl['endUserASN']==t]['#Field:count'].values[0]))
                        if u == 'Content':
                            content_not_squatted += 1
                        elif eyeball> 10 ** 5:
                            access_network_not_squatted += 1
                        elif eyeball < 10 ** 5 and eyeball > 10 ** 2 and s > 6:
                            transit_not_squatted += 1
                        elif s > 20:
                            transit_not_squatted += 1
                        else:
                            none_not_squatted += 1
                        top_users += int(dl[dl['endUserASN']==t]['#Field:count'].values[0])
                        total_df.append([t,float(dl[dl['endUserASN']==t]['sourceIPCount'].values[0]),int(dl[dl['endUserASN']==t]['#Field:count'].values[0]),'Not Squatted ' + feature,feature])
                else:
                    if u == 'Content':
                        content_not_seen += 1
                    elif eyeball > 10 ** 5:
                        access_network_not_seen += 1
                    elif eyeball < 10 ** 5 and eyeball > 10 ** 2 and s > 6:
                        transit_not_seen += 1
                    elif s > 20:
                        transit_not_seen += 1
                    else:
                        none_not_seen += 1
                    notseen +=1
            print(seen_squatted,seen_non_squatted,notseen)
            # number = counting
            # final_value.append([seen_squatted/float(number),seen_non_squatted/float(number),notseen/float(number),feature])
            final_value.append([content_squatted/float(number),access_network_squatted/float(number),transit_squatted/float(number),none_squatted/float(number),
                                content_not_squatted / float(number), access_network_not_squatted / float(number),
                                transit_not_squatted / float(number), none_not_squatted/float(number), content_not_seen/float(number),access_network_not_seen/float(number),
                                transit_not_seen/float(number),none_not_seen/float(number)])
            print(top_users/float(sum_all_traceroutes))


    df = pd.DataFrame(total_df,columns = ['AS','# of source IP','# of Traceroutes','Type','Feature'])
    # df.to_csv('log/log_analyzingclient.csv')
    return final_value
# df = analyzingclients()
def separating_statistics_for_squat_vs_nonsquat(category = '# of Traceroutes'):
    df = pd.read_csv('log/log_analyzingclient.csv',index_col = 0)
    df = df.sort_values(by=['# of Traceroutes'])
    #
    print(df['Type'].unique())
    renaming_type = {'Not Squatted Eyeballs':'Not Squat - Eyeballs', 'Squatted Eyeballs':'Squat - Eyeballs', 'Squatted ASCone' : 'Squat - Customer Cone',
    'Not Squatted ASCone' : 'Not Squat - Customer Cone', 'Not Squatted lenPref' : 'Not Squat - Prefix Announced', 'Squatted lenPref': 'Squat - Prefix Announced'}
    new_type = []
    for t in df['Type']:
        new_type.append(renaming_type[t])
    plt.legend(fontsize='large', title_fontsize='25')
    df['Type'] = new_type
    print(new_type)
    fig, ax = plt.subplots()
    hue_order = ['Not Squat - Customer Cone','Not Squat - Prefix Announced', 'Not Squat - Eyeballs', 'Squat - Customer Cone','Squat - Prefix Announced', 'Squat - Eyeballs',]
    plt.ylabel('Fraction of  top 500 organization',fontsize= 16)
    plt.xlabel(category,fontsize= 16)
    sns.kdeplot(
        data=df, x=category, hue="Type",
        cumulative=True, common_norm=False, common_grid=True,log_scale=True, hue_order=hue_order
    )
    plt.savefig('figures/top500squat_vs_nonsquat.pdf')

def proportion_of_squatting(final_value):
    ind = np.arange(len(final_value))  # the x locations for the groups
    width = 0.25
    fig = plt.figure(figsize=(12,9),)
    # ax = fig.add_axes([0, 0, 1, 1])
    patterns = [ "/" , "+" , "*", "o", "O", ".", "*" ]
    past = [0,0,0,0,0,0,0,0,0]
    # final_value = list(map(list, zip(*final_value)))
    ps = []
    for j in range(0,12):
        frac = j/4
        pat = j%4
        if frac < 1:
            color = 'r'
        elif 2 >frac >=1:
            color = 'cyan'
        elif 3 > frac >=2:
            color= 'g'
        else:
            color = 'y'
        val = [a_tuple[j] for a_tuple in final_value]
        print(sum(val))
        print(len(ind),len(val),len(past))
        ps.append(plt.bar(ind,val,width,bottom=past,color=color,hatch = patterns[pat]))
        for t in range(0,len(val)):
            past[t] += val[t]
    plt.ylabel('Fraction of squat/non-squat/no measur.',fontsize= 16)
    plt.xlabel('Top x organizations',fontsize=16)
    plt.xticks(ind,range(500,5000,500))
    # ax.set_yticks(np.arange(0, 81, 10))
    plt.tick_params(axis='both',labelsize=14)
    #
    # plt.legend(labels=['CDN Squatters', 'Access Squatters','Transit Squatters','Unknown Squatters',
    #                    'CDN Not Squatters', 'Access Not Squatters','Transit Not Squatters','Unknown Not Squatters',
    # 'CDN ~ No Measurement', 'Access ~ No Measurement','Transit ~ No Measurement','Unknown ~ No Measurement',
    #                    ],fontsize='x-large', bbox_to_anchor=(1.05, 1))
    plt.legend(ps, ('CDN Squatters', 'Access Squatters','Transit Squatters','Unknown Squatters',
                       'CDN Not Squatters', 'Access Not Squatters','Transit Not Squatters','Unknown Not Squatters',
    'CDN ~ No Measurement', 'Access ~ No Measurement','Transit ~ No Measurement','Unknown ~ No Measurement',
                       ), ncol=3, loc='upper left',
               bbox_to_anchor=(0, 1.0, 0, 0.21), fontsize='x-large')
    plt.savefig('figures/Representativity_allocated_with_threshold.pdf', bbox_inches="tight")
    # plt.show()

if __name__ == "__main__":
    proportion_of_squatting(analyzingclients())