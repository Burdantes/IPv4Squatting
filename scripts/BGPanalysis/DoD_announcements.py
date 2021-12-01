import pandas as pd
from collections import Counter,defaultdict
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import seaborn as sns
import pickle
from tqdm import tqdm
import ipaddr
import sys
sys.path.append('../../')
from util import load_dod_prefix

def continuously_squatting():
    file1 = open("../../data/dod_squatters_02_03.txt", "r")
    txt = file1.readlines()
    print(txt)
    ases_that_are_still_squatting = []
    for s in txt:
        print(s)
        ases_that_are_still_squatting.append(s.split(' ')[0])
    return ases_that_are_still_squatting

ases_that_are_still_squatting = continuously_squatting()


def constructing_graph_of_announcements():
    list_of_timing = [1611180000]
    for s in range(0,2*24*60*60):
        # for t in range(1,12):
        list_of_timing.append(list_of_timing[0]+s*300)
    # dic_number_of_announcements = dict(zip(list_of_timing,len(list_of_timing)*[0]))
    dic_number_of_announcements = defaultdict(lambda: 0)
    print(dic_number_of_announcements)
    file1 = open("announcements_DoD_AS8003.txt", "r+")
    # collections_of_announcements = []
    dic_path_length = defaultdict(lambda: [])
    dic_who_is_announcing = defaultdict(lambda: set())
    G = nx.DiGraph()
    edges_time = {}
    count = {}
    count_of_peers = defaultdict(lambda: 0)
    count_of_prefixes = defaultdict(lambda: 0)
    previously_seen_peers = {}
    previously_seen_prefixes = {}
    # dic_montiors = {}
    path_per_prefix = defaultdict(lambda : set())
    for t in tqdm(file1.readlines()):
        # print(t)
        t.replace('\n','')
        m = t.split('|')
        times = int(float(m[2]))
        # print(min(list_of_timing, key=lambda x: abs(x - times)))
        prefix = m[9]
        # print(prefix.split('.')[0]+'.'+'0.0.0/8')
        path = m[11].split(' ')
        peers = m[7]
        monitors = m[4]
        path_per_prefix[prefix.split('.')[0]+'.'+'0.0.0/8'].add(str(times)+ '|'+'/' + prefix.split('/')[1] +'|'+ m[11])
        nx.add_path(G, path)
        for i in range(0,len(path)-1):
            if not((path[i],path[i+1]) in edges_time.keys()):
                edges_time[(path[i],path[i+1])] = times
                count[(path[i],path[i+1])] = 1
                if not((path[i],path[i+1],peers) in previously_seen_peers):
                    count_of_peers[(path[i],path[i+1])] += 1
                    previously_seen_peers[(path[i],path[i+1],peers)] = 1
                if not((path[i],path[i+1],prefix) in previously_seen_prefixes):
                    count_of_prefixes[(path[i],path[i
                                                    +1],prefix.split('.')[0]+'.'+'0.0.0/8')] += 1
                    previously_seen_prefixes[(path[i],path[i+1],prefix.split('.')[0]+'.'+'0.0.0/8')] = 1
            else:
                count[(path[i],path[i+1])] +=1
        list_of_prefixes_dod = load_dod_prefix()
        for collect in list_of_prefixes_dod:
            if ipaddr.IPNetwork(prefix) in (ipaddr.IPNetwork(collect)):
                # right_index = (int(min(list_of_timing, key=lambda x: abs(x - times))),collect,monitors)
                dic_number_of_announcements[times] += 1
                dic_path_length[times].append(len(path))
                dic_who_is_announcing[times].add(peers)
        # collections_of_announcements.append(m)
        # print(m)
    # # print(len(collections_of_announcements))
    with open('../../data/timeseries_data.pickle', 'wb') as handle:
        pickle.dump(dict(dic_number_of_announcements), handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../../result/BGPdata/path_length_24hours.pickle','wb') as handle:
        pickle.dump(dict(dic_path_length), handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../result/BGPdata/whoisannouncing_24hours.pickle', 'wb')  as handle:
        pickle.dump(dict(dic_who_is_announcing), handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('../results/BGPdata/path_prefix_timestamps.pickle', 'wb')  as handle:
        pickle.dump(dict(path_per_prefix), handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(nx.info(G))
    nx.set_edge_attributes(G,edges_time,'Edge time')
    nx.set_edge_attributes(G,count,'Count')
    nx.set_edge_attributes(G,count_of_prefixes,'Number of Prefixes')
    nx.set_edge_attributes(G,count_of_peers,'Number of Peers')
    nx.write_graphml(G, '../.,/results/graph_BGP_announcements24h.graphml')



def visualization_path_length():
    dic_path_length = pickle.load(open("../../result/BGPdata/path_length_24hours.pickle", "rb"))
    val = {}
    for i,t in enumerate(dic_path_length.keys()):
        print(t[0])
        val[i] = [np.mean(dic_path_length[t]),t[1],(t[0]-1611180000)/(60*60)]
    print(val)
    # df = pd.DataFrame(pd.Series(dic_number_of_announcements),columns=['Number of Announcements'])
    df = pd.DataFrame.from_dict(val).transpose()
    df.columns=['Average Path Length','Prefixes','Timestamp']
    # df['Timestamp'] = df.index
    # df['Timestamp'] = df['Timestamp'].astype(float64)
    # df['Timestamp']= pd.to_datetime(df['Timestamp'].values)
    # df['Date'] = df['Timestamp'].to_pydatetime()
    df['Date'] = pd.to_datetime(df['Timestamp']).apply(lambda x: x.date())
    # print(df['Number of Announcements'])
    print(df['Timestamp'])
    df['Average Path Length'] = df['Average Path Length'].astype(float)
    fig, ax = plt.subplots(figsize=(11, 7))
    b = sns.lineplot(data=df, x="Timestamp", y="Average Path Length",hue = 'Prefixes')
    title = 'Average Path Length during the day after AS8003\n starting announcing the DoD addresses'
    # plt.title(title,)
    b.axes.set_title(title,fontsize=17)
    b.set_xlabel("Hours",fontsize=15)
    b.set_ylabel("Average Path Length",fontsize=15)
    b.tick_params(labelsize=12)
    plt.savefig('../../result/averagepathlengthduringtheday.png')

def visualization_number_of_peers():
    dic_path_length = pickle.load(open("../../result/BGPdata/whoisannouncing_24hours.pickle", "rb"))
    val = {}
    already_seen = []
    time_squatters = []
    time_non_squatters = []
    for i, t in enumerate(dic_path_length.keys()):
        print(t,i,dic_path_length[t])
        for s in dic_path_length[t]:
            if not(int(s) in already_seen):
                already_seen.append(int(s))
                if s in ases_that_are_still_squatting:
                    time_squatters.append(int(s))
                    val[i] = [len(time_squatters)/float(55),t,'Squatting']
                else:
                    time_non_squatters.append(int(s))
                    val[i] = [len(time_non_squatters)/float(362), t,'Non-Squatting']
        print(len(already_seen))
        # val[i] = [0,,0
    print(val)

    file1 = open("../../data/dod_squatters_02_03.txt", "r")
    txt = file1.readlines()
    info = []
    for t in txt:
        if t.startswith('#'):
            continue
        t = t.replace('\n', '')
        info.append(t.split(' ')[0])
    print(info)
    df = pd.DataFrame.from_dict(val).transpose()
    df.columns = ['Number of Peers Propagating Announcements', 'Timestamp','Type']
    print(df['Timestamp'])
    df['Number of Peers Propagating Announcements'] = df['Number of Peers Propagating Announcements'].astype(float)
    fig, ax = plt.subplots(figsize=(11, 7))
    df['Date'] = df.Timestamp.apply(lambda x: pd.datetime.fromtimestamp(x))
    b = sns.lineplot(data=df, x="Date", y="Number of Peers Propagating Announcements",hue="Type")
    b.set_xlabel("Hours", fontsize=15)
    b.set_ylabel("Number of Peers Propagating Announcements", fontsize=15)
    b.tick_params(labelsize=12)
    plt.savefig('../../result/BGPData/announcements_propagations.png')

def list_duplicates_of(seq,item):
    start_at = -1
    locs = []
    while True:
        try:
            loc = seq.index(item,start_at+1)
        except ValueError:
            break
        else:
            locs.append(loc)
            start_at = loc
    return locs

def analyzing_distribution_of_destination():
    dic_path_length_prefixes = pickle.load(open("../../result/BGPdata/path_prefix_timestamps.pickle", "rb"))
    dic_adding = {}
    global_df = []
    time_spawn = []
    for t in dic_path_length_prefixes:
        for s in dic_path_length_prefixes[t]:
            list_of_adding = []
            if len(s.split(' ')) > 1:
                    # and s.split(' ')[-1]=='8003':
                list_of_adding.append(s.split(' ')[-1])
                list_of_adding.append(s.split('|')[1])
                list_of_adding.append(len(s.split('|')[2].split(' ')))
                list_of_adding.append(s.split('|')[2].split(' ')[0])
                list_of_adding.append(t)
                list_of_adding.append(int(s.split('|')[0].split('.')[0]))
                if s.split(' ')[-1] == '8003':
                    list_of_adding.append('Legitimate')
                elif '721' in s.split('|')[2]:
                    list_of_adding.append('Legitimate')
                else:
                    list_of_adding.append('Illegitimate')
                time_spawn.append([int(s.split('|')[0].split('.')[0]),s.split('|')[1]])
                list_of_adding.append(s.split('|')[2].split(' '))
                global_df.append(list_of_adding)
    from copy import deepcopy
    glob_df = deepcopy(global_df)
    prependings = []
    count_prependings = []
    for i in range(0,len(global_df)):
        t =global_df[i]
        if t[2]> 10:
            print('STOP{')
        x = list(set(t[-1]))
        if x != t[-1]:
            list_of_item = [item for item, count in Counter(t[-1]).items() if count > 1]
            count_prependings.extend(list_of_item)
            val = []
            for s in list_of_item:
                val.append(x.index(s))
                prependings.append(x.index(s))
        t.pop()
        if t[-1] == 'Illegitimate':
            t.pop()
            t.append('Illegitimate w/o Prepending')
        else:
            t.pop()
            t.append('Legitimate w/o Prepending')
        t.append(x)
        t.remove(t[2])
        t.insert(2,len(x))
        glob_df.append(t)
    #     dic_adding[t] = list_of_adding
    for key in dic_adding:
        print(key,len(dic_adding[key]),dic_adding[key])
    df = pd.DataFrame(glob_df,columns=['AS announcing','/x','AS Path Length','Peers','Prefix','Timestamp','Legitimacy','Path'])
    print(df[df['Legitimacy']=='Legitimate'].shape)
    print(df.shape)
    print(Counter(count_prependings))
    dico_prep = dict(Counter(prependings))
    for i in dico_prep:
        val = dico_prep[i]/float(sum(list(dico_prep.values())))
        print(i,val*100)
    # Initialize the figure
    f, ax = plt.subplots(figsize=(11,5.5))
    df = df.sort_values(by='Prefix')
    ax = sns.boxplot(x="AS Path Length", y="Prefix", hue="Legitimacy",
                  data=df,linewidth=0.75)
    # plt.show()
    # Show the conditional means
    # sns.pointplot(x="AS Path Length", y="Prefix", hue="Legitimacy",
    #               data=df, join=False, palette="dark",
    #           markers="d", scale=.75,zorder=1)

    # Improve the legend
    handles, labels = ax.get_legend_handles_labels()
    print(labels)
    ax.legend(handles[0:4], labels[:4],
              handletextpad=0, columnspacing=1,
              loc="lower right", frameon=True,fontsize="x-large")
    # ax.axes.set_title(title,fontsize=17)
    ax.set_xlabel('AS Path Length',fontsize=20)
    # ax.set_ylabel('Prefix', fontsize=18)
    ax.tick_params(labelsize=18)
    hatches = ["/", "o", "*", "\\"]
    all_the_hatches = []
    for i in range(0,len(load_dod_prefix())):
        if i == 4:
            all_the_hatches.extend(hatches[2:])
        elif i == 6:
            all_the_hatches.extend(hatches[2:])
        else:
            all_the_hatches.extend(hatches)
    for hatch, patch in zip(all_the_hatches, ax.artists):
        patch.set_hatch(hatch)
    for hatch,legpatch in zip(hatches,ax.get_legend().get_patches()):
        col = legpatch.get_facecolor()
        legpatch.set_hatch(hatch)
        # legpatch.set_edgecolor(col)
        # legpatch.set_facecolor('None')
    plt.savefig('../../result/BGPData/AS_path_length_observed.pdf')
    df= pd.DataFrame(time_spawn,columns=['Timestamp','Prefixes'])
    df['Date'] = df.Timestamp.apply(lambda x: pd.datetime.fromtimestamp(x))
    df['Date'] =df['Date'].dt.floor('H')
    print(df['Date'])
    # print(df['Number of Announcements'])
    print(df['Date'].value_counts())
    # print(df.groupby("Date").sum())
    s = []
    for t in df.groupby('Prefixes'):
        # s.append(t[0])
        val = (dict(t[1]['Date'].value_counts()))
        for te in val:
            s.append([t[0],te,val[te]])
        print(s)
    day_divider = 86400000
    df = pd.DataFrame(s,columns=['Prefixes','Date','Number of Announcements'])
    print(df)
    fig, ax = plt.subplots(figsize=(11, 7))
    b = sns.lineplot(data=df, x="Date", y="Number of Announcements",hue = 'Prefixes')
    b.set_xlabel("Date", fontsize=26)
    b.set_ylabel("Number of Announcements", fontsize=26)
    print(df['Date'].value_counts())
    b.tick_params(labelsize=20, rotation=75)
    plt.savefig('../../result/BGPData/timeseries_of_the_day.pdf')

if __name__ == "__main__":
    visualization_number_of_peers()
    analyzing_distribution_of_destination()

    # dic_path_length_prefixes = pickle.load(open("results/path_length_24hours.pickle", "rb"))
    # for t in dic_path_length_prefixes:
    #     print(t,dic_path_length_prefixes[t])