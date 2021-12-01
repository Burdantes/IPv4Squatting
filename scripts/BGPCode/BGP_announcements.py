import pybgpstream
import pandas as pd
from collections import  defaultdict
from tqdm import tqdm
import datetime
import pickle
from itertools import product
import warnings
import networkx as nx
from util import load_squatspace_default

# def res_processing(s,i):
#     list_result = []
#     from_time = str(dg[dg.index == s]['Beginning'].values[0])
#     to_time = str(dg[dg.index == s]['End'].values[0])
#     # print(from_time, to_time)
#     stream = pybgpstream.BGPStream(
#         from_time=from_time, until_time=to_time,
#         # collectors=["route-views.sg", "route-views.eqix"],
#         projects=["routeviews", "ris"],
#         record_type="updates",
#         filter="prefix more 11.0.0.0/8 "
#     )
#     j = 1
#     for elem in stream:
#         # record fields can be accessed directly from elem
#         # e.g. elem.time
#         # or via elem.record
#         # e.g. elem.record.time
#         print(elem)
#         list_result.append(elem)
#         with open('announcements_fromtime'+str(from_time)+ str(i) + '.txt', 'a+') as f:
#             f.write("%s\n" % elem)
#     with open('data/announcements_per_address'+str(i)+'.pickle', 'wb') as handle:
#         pickle.dump(list_result, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # print(list_result)

def res_announcements_of_DoD(start_date,end_date,squat_prefixes,output_file):
    filters = (' ').join(squat_prefixes)
    filters = 'prefix more '+filters
    stream = pybgpstream.BGPStream(
        from_time=start_date, until_time='2021-01-21 22:00:00',
        # collectors=["route-views.sg", "route-views.eqix"],
        projects=["routeviews", "ris"],
        record_type="updates",
        filter= filters
    )
    j = 1
    dic_number_of_announcements = defaultdict(lambda: 0)
    print(dic_number_of_announcements)
    dic_who_is_announcing = defaultdict(lambda: set())
    G = nx.DiGraph()
    edges_time = {}
    count = {}
    count_of_peers = defaultdict(lambda: 0)
    count_of_prefixes = defaultdict(lambda: 0)
    previously_seen_peers = {}
    previously_seen_prefixes = {}
    # dic_montiors = {}
    path_per_prefix = defaultdict(lambda: set())
    count_withdrawal  = 0
    count_announcements = 0
    for elem in stream:
        # record fields can be accessed directly from elem
        # e.g. elem.time
        # or via elem.record
        # e.g. elem.record.time
        print(elem)
        t = elem.record
        count_announcements += 1
        times = int(t.time)
        prefix = elem.fields['prefix']
        try:
            path = elem.fields['as-path'].split(' ')
        except:
            count_withdrawal+= 1
            continue
        peers = path[0]
        monitors = t.collector
        path_per_prefix[prefix.split('.')[0] + '.' + '0.0.0/8'].add(
            str(times) + '|' + '/' + prefix.split('/')[1] + '|' + (' ').join(path))
        nx.add_path(G, path)
        for i in range(0, len(path) - 1):
            if not ((path[i], path[i + 1]) in edges_time.keys()):
                edges_time[(path[i], path[i + 1])] = times
                count[(path[i], path[i + 1])] = 1
                if not ((path[i], path[i + 1], peers) in previously_seen_peers):
                    count_of_peers[(path[i], path[i + 1])] += 1
                    previously_seen_peers[(path[i], path[i + 1], peers)] = 1
                if not ((path[i], path[i + 1], prefix) in previously_seen_prefixes):
                    count_of_prefixes[(path[i], path[i
                                                     + 1], prefix.split('.')[0] + '.' + '0.0.0/8')] += 1
                    previously_seen_prefixes[(path[i], path[i + 1], prefix.split('.')[0] + '.' + '0.0.0/8')] = 1
            else:
                count[(path[i], path[i + 1])] += 1
        dic_number_of_announcements[str(times)+'|'+prefix] += 1
        dic_who_is_announcing[str(times)+'|'+prefix].add(peers)
    with open(output_file, 'wb')  as handle:
        pickle.dump(dict(path_per_prefix), handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('COUNT WITHDRAWAL' , count_withdrawal)
    print('COUNT ANNOUNCEMENTS', count_announcements)

if __name__ == "__main__":
    list_of_prefixes_squatspace = load_squatspace_default().prefixes()
    print(list_of_prefixes_squatspace)
    output_file = '../../results/path_prefix_timestamps.pickle'
    DoD_address = ['6.0.0.0/8', '7.0.0.0/8', '11.0.0.0/8', '21.0.0.0/8', '22.0.0.0/8', '26.0.0.0/8',
                   '28.0.0.0/8', '29.0.0.0/8', '30.0.0.0/8', '33.0.0.0/8']
    res_announcements_of_DoD(start_date='2021-01-19 11:42:50', end_date = '2021-01-21 22:42:50',squat_prefixes=DoD_address,output_file = output_file)
