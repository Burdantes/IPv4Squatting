import pandas as pd
from collections import Counter,defaultdict
import scipy.stats as stat
from random import random
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
def reading_data():
    rows = []
    for month in ['01','03','04','05','06']:
        print(month)
        for file in ['count_statistics/tracerouteasncounts-2021-'+month+'-10-2021-'+month+'-16.txt', 'count_statistics/squatasncounts-2021-'+month+'-10-2021-'+month+'-16.txt']:
            if file.split('.')[-1] == 'txt':
                file1 = open(file, "r")
                col = file1.readline()
                col = col.replace('\n', '')
                # col = col.split('|')[0:6]
                col = col.strip()
                print(col)
                col = col.split('	')
                col.append('which_data')
                col.append('month')
                for row in file1.readlines():
                    # print(row)
                    if row[0] == '#':
                        continue
                    row = row.replace('\n', '')
                    row = row.split('	')
                    row.append(file.split('-')[0])
                    row.append(month)
                    rows.append(row)
    df = pd.DataFrame(rows,columns=col)
    return df

def full_pipeline():
    ms = [200, 500, 1000, 2500, 5000, 100000, 250*10**2, 5*10 ** 5]
    ns = [2, 5, 10, 25, 50, 100, 250, 1000, 5000]
    ser1 = {}
    for n in ns:
        ser1[n] = [n,1,'#']
    dg = pd.DataFrame.from_dict(ser1).transpose()
    ser = {}
    for m in ms:
        ser[m] = [m,1,'#']
    dl = pd.DataFrame.from_dict(ser).transpose()
    # for t in range(0,len(ser)-1):
    #     key = list(ser.keys())[t]
    #     key1 =list(ser.keys())[t+1]
    #     key_bis = list(ser1.keys())[t]
    #     key_bis1 = list(ser1.keys())[t+1]
    #     print(float(ser1[key])/ser[key1])
 #     print(float(ser1[key_bis])/ser1[key_bis1])
    for t in range(0,len(ms)-1):
        print('M',float(ms[t+1])/ms[t])
        print('N',float(ns[t+1])/ns[t])
    # df = df.append(dg, ignore_index=True)
    dg.columns = ['Number of source IP', 'Ratio', 'Category']
    dl.columns = ['Number of Traceroutes', 'Ratio', 'Category']
    # sns.lmplot('Quantity', 'Ratio', data=df, hue='Category', fit_reg=False,markers=['o', 'x'])
    # plt.show()
    # dg = pd.read_csv('stat_threshold1.csv',index_col = 0)
    # dl = pd.read_csv('stat_threshold2.csv',index_col = 0)
    fig, ax = plt.subplots()
    ax.set_xscale('log')
    ax2 = ax.twiny()
    ax2.set_xscale('log')
    # ax2.set_xscale('log')
    # ax.set_xscale('log')
    lns1 = sns.regplot(x="Number of Traceroutes", y="Ratio", fit_reg=False, color='r', data=dl, marker='x',
                       label='# of Traceroutes', ax=ax)
    lns2 = sns.regplot(x='Number of source IP', y="Ratio", fit_reg=False, color='b', data=dg, marker='o',
                       label='# of Source IP', ax=ax2)
    # dg.to_csv()
    # dl.to_csv('stat_threshold2.csv')
    # ax.legend()
    # ax2.legend(handles = [],labels= )
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    # ax2.legend(handles=[ax,ax2],
    #            labels=["# of Source IP", "# of Traceroutes"])
    ax.set_xlabel(r"# of Traceroutes")
    ax2.set_xlabel(r"# of Source IP")
    # ax.set_ylabel(r"Radiation ($MJ\,m^{-2}\,d^{-1}$)")
    # ax2.set_ylabel(r"Temperature ($^\circ$C)")
    ax2.set_xlim(10**-1, 10 * 10 ** 3)
    ax.set_xlim(10 , 10 ** 6)
    plt.show()

def computing_empirical_frequencies(dg,min_traceroute=5000,min_source = 50):
    fig, ax = plt.subplots(figsize=(6,5.2))
    res = defaultdict(lambda : [])
    for month in ['01','03','04','05','06']:
        dl = dg[dg['month']==month]
        print(month)
        for t in tqdm(dl.groupby('endUserASN')):
            val1 = float(t[1][t[1].index == t[1].index[0]]['#Field:count'].values[0])
            if val1 < min_traceroute:
                continue
            ind1 = t[1][t[1].index == t[1].index[0]]['#Field:count'].index.values[0]
            # res_stat[ind1] = val1
            # if val1<m:
            #     continue
            if t[1].shape[0] == 1:
                val2 = 0
                continue
            else:
                val2 = float(t[1][t[1].index == t[1].index[1]]['#Field:count'].values[0])

                ind2 = t[1][t[1].index == t[1].index[1]]['#Field:count'].index.values[0]
            # print(val1,val2)
            if val2 > val1:
                res[t[0]].append(float(val1) / float(val2))
            else:
                res[t[0]].append(float(val2) / float(val1))
            # p = res[t[0]]
    minin = {}
    maxin = {}
    for t in res.keys():
        print(res[t])
        minin[t] = min(res[t])
        maxin[t] = max(res[t])
    df = pd.DataFrame(pd.Series(maxin),columns = ['squat_index'])
    stats_df = df \
        .groupby('squat_index') \
        ['squat_index'] \
        .agg('count') \
        .pipe(pd.DataFrame) \
        .rename(columns={'squat_index': 'frequency'})

    # PDF
    stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])

    # CDF
    stats_df['Fr. of Squatting Traceroute per Org.'] = stats_df['pdf'].cumsum()
    stats_df = stats_df.reset_index()
    print(stats_df)
    b = stats_df.plot(x='squat_index', y='Fr. of Squatting Traceroute per Org.', color='r', marker='o', ax=ax)
    # df = pd.DataFrame(pd.Series(maxin), columns=['squat_index'])
    # stats_df = df \
    #     .groupby('squat_index') \
    #     ['squat_index'] \
    #     .agg('count') \
    #     .pipe(pd.DataFrame) \
    #     .rename(columns={'squat_index': 'frequency'})
    #
    # # PDF
    # stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])
    #
    # # CDF
    # stats_df['Empirical Frequency of Squatting per Traceroute (Min)'] = stats_df['pdf'].cumsum()
    # stats_df = stats_df.reset_index()
    # print(stats_df)
    # b = stats_df.plot(x='squat_index', y='Empirical Frequency of Squatting per Traceroute (Min)', color='b', marker='v', ax=ax)
    res = defaultdict(lambda: [])
    for month in ['01', '03', '04', '05', '06']:
        dl = dg[dg['month'] == month]
        print(month)
        for t in tqdm(dl.groupby('endUserASN')):
            val1 = float(t[1][t[1].index == t[1].index[0]]['sourceIPCount'].values[0])
            if val1 < min_source :
                continue
            ind1 = t[1][t[1].index == t[1].index[0]]['sourceIPCount'].index.values[0]
            # res_stat[ind1] = val1
            # if val1<m:
            #     continue
            if t[1].shape[0] == 1:
                val2 = 0
                continue
            else:
                val2 = float(t[1][t[1].index == t[1].index[1]]['sourceIPCount'].values[0])

                ind2 = t[1][t[1].index == t[1].index[1]]['sourceIPCount'].index.values[0]
            # print(val1,val2)
            if val2 > val1 :
                print(val2,val1)
                res[t[0]].append(float(val1)/float(val2))
            else:
                res[t[0]].append(float(val2) / float(val1))
            # p = res[t[0]]
    minin = {}
    maxin = {}
    for t in res.keys():
        print(res[t])
        minin[t] = min(res[t])
        maxin[t] = max(res[t])
    df = pd.DataFrame(pd.Series(maxin), columns=['squat_index'])
    stats_df = df \
        .groupby('squat_index') \
        ['squat_index'] \
        .agg('count') \
        .pipe(pd.DataFrame) \
        .rename(columns={'squat_index': 'frequency'})

    # PDF
    stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])

    # CDF
    stats_df['Fr. of Squatting Source per Org.'] = stats_df['pdf'].cumsum()
    stats_df = stats_df.reset_index()
    print(stats_df)
    b = stats_df.plot(x='squat_index', y='Fr. of Squatting Source per Org.', color='g', marker='*', ax=ax)
    # df = pd.DataFrame(pd.Series(maxin), columns=['squat_index'])
    # stats_df = df \
    #     .groupby('squat_index') \
    #     ['squat_index'] \
    #     .agg('count') \
    #     .pipe(pd.DataFrame) \
    #     .rename(columns={'squat_index': 'frequency'})
    #
    # # PDF
    # stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])
    #
    # # CDF
    # stats_df['Empirical Frequency of Squatting per Source (Min)'] = stats_df['pdf'].cumsum()
    # stats_df = stats_df.reset_index()
    # print(stats_df)
    # b = stats_df.plot(x='squat_index', y='Empirical Frequency of Squatting per Source (Min)', color='black', marker='>', ax=ax)

    b.set_xlabel("Fraction of Squatting Traceroutes/Sources", fontsize=18)
    b.set_ylabel("Cum. Frac. of Organisations", fontsize=18)
    b.tick_params(labelsize=15)
    plt.legend(fontsize="large")
    plt.savefig('figures/fract_squat.png')

def counting_number_of_24s(df):
    for month in ['01', '03', '04', '05', '06']:
        dl = df[df['month'] == month]
        print(dl.head())

def generating_stats(df,ms = [50,100,500,1000,2500,5000,10000,10**5,10**6,10**7],ns = [2,5,10,25,50,100,250,500,1000,2500,5000]):
    res = {}
    res_stat = {}
    to_check = []
    ser = {}
    for m in tqdm(ms):
        tot = 0
        frequency = 0
        frequency_z = 0
        for t in tqdm(df.groupby('endUserASN')):
            to_check.append(t[0] +'\t')
            val1 = float(t[1][t[1].index==t[1].index[0]]['#Field:count'].values[0])
            ind1 = t[1][t[1].index==t[1].index[0]]['#Field:count'].index.values[0]
            # res_stat[ind1] = val1
            tot +=1
            # if val1<m:
            #     continue
            if t[1].shape[0] == 1:
                frequency +=1
                val2 = 0
                continue
            else:
                val2 = float(t[1][t[1].index==t[1].index[1]]['#Field:count'].values[0])

                ind2 = t[1][t[1].index == t[1].index[1]]['#Field:count'].index.values[0]
            # print(val1,val2)
            if val1 > val2:
                res[t[0]] = float(val2)/float(val1)
            else:
                res[t[0]] = float(val1)/float(val2)
            p = res[t[0]]
            bin = 1 - stat.binom.cdf(k=0,n=m,p=p)
            # print(bin)
            if bin >random():
            # if float(m)/val1 < res[t[0]]:
                res_stat[t[0]] = 'Success'
            else:
                frequency +=1
                frequency_z += 1
                res_stat[t[0]] = 'Failure'
        succ = dict(Counter(list(res_stat.values())))
        # for t in succ:
        # ser[m] = [m,succ['Success']/float(tot),'# of traceroutes']
        # print(m,succ['Success']/float(res_stat.values()),(float(frequency)/float(tot)))
        print(frequency_z,frequency)
        ser[m] = [m,float(frequency_z)/tot,'# of traceroutes']
        print(m,succ)
        # res_stat[ind2] = val1
    # print(res)
    # df = pd.DataFrame(pd.Series(ser),columns=['Ratio'])
    # hue_val = ['# of traceroutes']*len(ser)
    dl = pd.DataFrame.from_dict(ser).transpose()
    # sns.lmplot('A', 'B', data=df, hue='category', fit_reg=False,markers=['o', 'x'])
    print(dl)
    res = {}
    res_stat = {}
    to_check = []
    ser = {}
    for n,m in tqdm(zip(ns,ms)):
        tot = 0
        frequency = 0
        frequency_z = 0
        for t in tqdm(df.groupby('endUserASN')):
            val1 = float(t[1][t[1].index == t[1].index[0]]['#Field:count'].values[0])
            ind1 = t[1][t[1].index == t[1].index[0]]['#Field:count'].index.values[0]
            # res_stat[ind1] = val1
            if t[1].shape[0] == 1:
                # if val1 < m:
                #     continue
                val2 = 0
                frequency  +=1
                continue
            else:
                val2 = float(t[1][t[1].index == t[1].index[1]]['#Field:count'].values[0])
                ind2 = t[1][t[1].index == t[1].index[1]]['#Field:count'].index.values[0]
            # print(val1,val2)
            # if float(val2) / val1>1:
            #     print('Hold on',t)
            if val1 > val2:
                res[t[0]] = float(val2)/float(val1)
            else:
                res[t[0]] = float(val1)/float(val2)
            # res[t[0]] = float(val2) / float(val1+val2)
            p = res[t[0]]
            bin = 1 - stat.binom.cdf(k=0, n=m, p=p)
            # print(bin)
            # tot += 1
            if bin > random():
                # if float(m)/val1 < res[t[0]]:
                res_stat[t[0]] = 'Success'
                continue
            else:
                # frequency_z +=1
                res_stat[t[0]] = 'Failure'
            to_check.append(t[0] +'\t')
            val1 = float(t[1][t[1].index==t[1].index[0]]['sourceIPCount'].values[0])
            ind1 = t[1][t[1].index==t[1].index[0]]['sourceIPCount'].index.values[0]
            # res_stat[ind1] = val1
            tot +=1
            if t[1].shape[0] == 1:
                # if val1 < n:
                #     continue
                frequency +=1
                val2 = 0
                continue
            else:
                val2 =float(t[1][t[1].index==t[1].index[1]]['sourceIPCount'].values[0])
                ind2 = t[1][t[1].index == t[1].index[1]]['sourceIPCount'].index.values[0]
            # print(val1,val2)
            ### Looking at the probability/frequency of observing a squatted address
            # res[t[0]] = float(val2)/float(val1+val2)
            if val1 > val2:
                res[t[0]] = float(val2)/float(val1)
            else:
                res[t[0]] = float(val1)/float(val2)
            p = res[t[0]]
            bin = 1 - stat.binom.cdf(k=0,n=n,p=p)
            # print(bin)
            if bin > random():
            # if float(m)/val1 < res[t[0]]:
                res_stat[t[0]] = 'Success'
            else:
                frequency  +=1
                frequency_z +=1
                res_stat[t[0]] = 'Failure'
                # continue
        succ = dict(Counter(list(res_stat.values())))
        # for t in succ:
        ser[n] = [n,frequency_z/float(tot),'# of source IP']
    dh = pd.DataFrame.from_dict(ser).transpose()
    # for n in ns:
    res = {}
    res_stat = {}
    to_check = []
    ser = {}
    # for n in ns:
    for n in ns:
        tot = 0
        frequency = 0
        frequency_z = 0
        for t in tqdm(df.groupby('endUserASN')):
            to_check.append(t[0] +'\t')
            val1 = float(t[1][t[1].index==t[1].index[0]]['sourceIPCount'].values[0])
            ind1 = t[1][t[1].index==t[1].index[0]]['sourceIPCount'].index.values[0]
            # res_stat[ind1] = val1
            tot +=1
            if t[1].shape[0] == 1:
                # if val1< n:
                #     continue
                val2 = 0
                frequency +=1
                continue
            else:
                val2 = float(t[1][t[1].index==t[1].index[1]]['sourceIPCount'].values[0])

                ind2 = t[1][t[1].index == t[1].index[1]]['sourceIPCount'].index.values[0]
            # print(val1,val2)
            # res[t[0]] = float(val2)/float(val1+val2)
            if val1 > val2:
                res[t[0]] = float(val2)/float(val1)
            else:
                res[t[0]] = float(val1)/float(val2)
            p = res[t[0]]
            bin = 1 - stat.binom.cdf(k=0,n=n,p=p)
            # print(bin)
            if bin > random():
            # if float(m)/val1 < res[t[0]]:
                res_stat[t[0]] = 'Success'
            else:
                frequency +=1
                frequency_z +=1
                res_stat[t[0]] = 'Failure'
        succ = dict(Counter(list(res_stat.values())))
        # for t in succ:
        ser[n] = [n,float(frequency_z)/float(tot),'# of source IP']
        # ser[n] = [n,succ['Success']/float(tot),'# of source IP']
        # print(m,succ)
        # res_stat[ind2] = val1
    dg = pd.DataFrame.from_dict(ser).transpose()
    # df = df.append(dg, ignore_index=True)
    dg.columns = ['Number of source IP','Ratio','Category']
    dl.columns = ['Number of Traceroutes','Ratio','Category']
    dh.columns = ['Number of source IP & Traceroutes','Ratio','Category']
    dg.to_csv('log/debuging_sources.csv')
    dl.to_csv('log/debugging_traceroutes.csv')
    dh.to_csv('log/debugging_sources_traceroutes.csv')
    return dg,dl,dh

def visualisation(dg,dl,dh):
    # sns.lmplot('Quantity', 'Ratio', data=df, hue='Category', fit_reg=False,markers=['o', 'x'])
    # plt.show()
    # dg = pd.read_csv('stat_threshold1.csv',index_col = 0)
    # dl = pd.read_csv('stat_threshold2.csv',index_col = 0)
    fig, ax = plt.subplots()
    ax2 = ax.twiny()
    # ax2.set_xscale('log')
    # ax.set_xscale('log')
    lns1 = sns.regplot(x="Number of Traceroutes", y="Ratio", fit_reg=False, color='r', data=dl, marker='x',
                       label='# of Traceroutes', ax=ax)
    print(dg)
    print(dl)
    print(dh)
    lns2 = sns.regplot(x='Number of source IP', y="Ratio", fit_reg=False, color='b', data=dg, marker='o',
                       label='# of Source IP', ax=ax2)
    lns2 = sns.regplot(x='Number of source IP & Traceroutes', y="Ratio", fit_reg=False, color='g', data=dh, marker='v',
                       label='# of Source IP or Traceroutes', ax=ax2)
    # dg.to_csv()
    # dl.to_csv('stat_threshold2.csv')
    # ax.legend()
    # ax2.legend(handles = [],labels= )
    ax.set_xscale('log')
    ax2.set_xscale('log')
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    # ax2.legend(handles=[ax,ax2],
    #            labels=["# of Source IP", "# of Traceroutes"])
    ax.set_xlabel(r"# of Traceroutes")
    ax2.set_xlabel(r"# of Source IP")
    ax.set_ylabel(r"$P_{miss}$")
    # ax2.set_ylabel(r"Temperature ($^\circ$C)")
    ax2.set_xlim(10 ** -1, 10 * 10 ** 3)
    ax.set_xlim(10, 10 ** 6)
    ax.set_ylim(0,0.5)
    plt.savefig('figures/statistics_selection_update.pdf')

if __name__ == "__main__":
    #
    # ms = [200, 500, 1000, 2500, 5000, 100000, 250 * 10 ** 2, 50000]
    # ns = [2, 5, 10, 25, 50, 100, 250,500]
    ms = [200]
    ns = [2]
    df = reading_data()
    # computing_empirical_frequencies(df,0,0)
    generating_stats(df,ms,ns)
    # dg= pd.read_csv('log/debuging_sources.csv', index_col = 0)
    # dl = pd.read_csv('log/debugging_traceroutes.csv', index_col=0)
    # dh = pd.read_csv('log/debugging_sources_traceroutes.csv', index_col = 0)
    # visualisation(dg=dg,dl=dl,dh=dh)
    # counting_number_of_24s(df)