from tqdm import tqdm
import os
import radix
from collections import defaultdict,Counter
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import json
import mmap
import math
import struct
import socket
import networkx as nx
from copy import deepcopy

from scipy.sparse import csr_matrix, spdiags
from scipy.sparse.linalg import eigsh
import numpy.linalg as la

class Cymru:

    def whois(self, text):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('whois.cymru.com', 43))
        s.sendall(text.encode('utf-8'))

        recv_data = []
        while 1:
            data = s.recv(8192)
            if not data:
                break
            recv_data.append(data.decode('utf-8'))

        s.shutdown(socket.SHUT_WR)
        s.close()
        return recv_data


    def parse(self, data):
        asn_list = []

        for l in data.splitlines()[1:]:
            if '|' not in l:
                continue
            asn, ip, desc = [elt.strip() for elt in l.split('|')]
            if asn == 'NA':
                continue
            asn_list.append((ip, 'AS' + asn, desc))

        return asn_list


    def resolve(self, ip_list):
        for i in range(5):
            try:
                request = 'begin\n' + '\n'.join(ip_list) + '\nend\n'
                response = self.whois(request)
                return self.parse(''.join(response))
            except:
                pass
        return []



def dottedQuadToNum(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('>L',socket.inet_aton(ip))[0]

def isPublicIPv4Address(ip):
    line = ip
    if line.startswith('6.') or line.startswith('7.') or line.startswith('9.') or line.startswith('11.') or \
                   line.startswith('16.') or line.startswith('19.') or line.startswith('21.') or line.startswith('22.') or \
                   line.startswith('25.') or line.startswith('26.') or line.startswith('28.') or line.startswith('29.') or \
                   line.startswith('30.') or line.startswith('33.') or line.startswith('43.') or line.startswith('48.') or \
                   line.startswith('56.'):
        return False
    return isPublicIPv4AddressInt(dottedQuadToNum(ip))

def isPublicIPv4AddressInt(asInt):
    return not(0 <= asInt and asInt < 16777216) and \
           not(167772160 <= asInt and asInt < 184549376) and \
           not(1681915904 <= asInt and asInt < 1686110208) and \
           not(2130706432 <= asInt and asInt < 2147483648) and \
           not(2851995648 <= asInt and asInt < 2852061184) and \
           not(2886729728 <= asInt and asInt < 2887778304) and \
           not(3221225472 <= asInt and asInt < 3221225728) and \
           not(3221225984 <= asInt and asInt < 3221226240) and \
           not(3232235520 <= asInt and asInt < 3232301056) and \
           not(3222405120 <= asInt and asInt < 3222536192) and \
           not(3325256704 <= asInt and asInt < 3325256960) and \
           not(3227017984 <= asInt and asInt < 3227018240) and \
           not(3405803776 <= asInt and asInt < 3405804032) and \
           not(3758096384 <= asInt)

def load_squatspace_default():
    # default_file = os.path.join('./', '../data/updated-unannounced-prefix/unannounced-202105.txt')
    default_file = os.path.join('', '../data/unannounced-202002.txt')
    # default_file = []
    trie = radix.Radix()
    with open(default_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith('6.') or line.startswith('7.') or line.startswith('9.') or line.startswith('11.') or \
               line.startswith('16.') or line.startswith('19.') or line.startswith('21.') or line.startswith('22.') or \
               line.startswith('25.') or line.startswith('26.') or line.startswith('28.') or line.startswith('29.') or \
               line.startswith('30.') or line.startswith('33.') or line.startswith('43.') or line.startswith('48.') or \
               line.startswith('56.'):
                trie.add(line)

    return trie

def find_squatspace(hop_ip_list):
    squat_ips = []
    for index, hop_ip in enumerate(hop_ip_list):
        if not(hop_ip in ['*','']) and squatspace_trie.search_best(hop_ip):
            squat_ips.append(index)
    return squat_ips


def mapcount(filename):
    f = open(filename, "r+")
    buf = mmap.mmap(f.fileno(), 0)
    lines = 0
    readline = buf.readline
    while readline():
        lines += 1
    return lines

def plotting_CDF(count_dico):
    count_dico = dict(count_dico)
    ## sort the data in ascending order
    x = np.sort(list(count_dico.values()))
    N = len(x)
    # get the cdf values of y
    y = np.arange(N) / float(N)

    # plotting
    plt.xlabel('Average RTT observed')
    plt.ylabel('Cum. Dist. Frac.')
    plt.xlim(0,30)
    # plt.title('CDF using sorting the data')

    plt.plot(x, y, marker='o')
    plt.show()

def computing_nat_statistic(path_to_data):
    squatspace_trie = load_squatspace_default()
    trs = set()
    ip_addresses = []
    LIST_DELIM = "|"
    dict_validated = defaultdict(lambda : [])
    dict_hop_pos = defaultdict(lambda : [])
    last_hop = defaultdict(lambda : [])
    count_of_all_sources = dict()
    path_to_squatspace = ''
    dict_inference =defaultdict(lambda : [])
    dict_everyone = defaultdict(lambda: [])
    list_of_edges = defaultdict(lambda : [])
    c = Cymru()
    count_thrown_away = 0
    number_of_src_prefix = set()
    dict_of_overlapping_nodes = {}
    dict_ratio = defaultdict(lambda : [])
    rtt_edges = defaultdict(lambda : defaultdict(lambda : []))
    for month in ['05','03']:
        for name in ['squatspace-all-2021-'+month+'-10-2021-'+month+'-16.txt']:
            count = 0
            filename= '/Users/geode/Documents/Datasets/Squat/'+name
            f = open(filename, "r+")
            buf = mmap.mmap(f.fileno(), 0)
            # for line in tqdm(buf.readline()):
            with open('/Users/geode/Documents/Datasets/Squat/'+name, 'r') as fin:
                # print(count)
                for line in tqdm(fin):
                    local_of_overlapping_node = defaultdict(lambda : [])
                    # print(count)
                    # if count > 5000:
                    #     break
                    count +=1
                    rtt_cgnat = False
                    line = line.rstrip()
                    split_line = line.split('\t')
                    squat_ip = split_line[3]
                    src_squat = split_line[0]
                    src_prefix = ('.').join(src_squat.split('.')[:-1])+'.0/24'
                    # if src_prefix in prefixes_nat:
                    # if src_prefix in ip_prefixes:
                    count_of_all_sources[src_squat] = src_prefix
                    # search = squatspace_trie.search_best(squat_ip)
                    # if search == None:
                        # not in the squat space
                        # continue
                    rtt_path = split_line[-2]
                    hop_ips = split_line[4]
                    hop_ips_list = hop_ips.split(',')
                    hop_ips = LIST_DELIM.join(hop_ips_list)
                    throw_away = False
                    rtt_ips = split_line[-2]
                    rtt_ips_list = rtt_ips.split(',')
                    try:
                        squat_indexes = find_squatspace(hop_ips_list)
                        first_hop = squat_indexes[0]
                    except:
                        continue
                    if math.isnan(int(rtt_ips_list[int(squat_indexes[0])])) or math.isnan(int(rtt_ips_list[int(squat_indexes[-1])])) :
                        continue
                    list_of_edges_to_preserve = []
                    last_hop_to_consider = 0
                    non_zero_ind = res = next(sub for sub in rtt_ips_list if sub)
                    if non_zero_ind == '0':
                        non_zero_ind = 1
                    for ind in range(0,len(hop_ips_list)-1):
                        # print(ip[ind])
                        if hop_ips_list[ind]!= '' and hop_ips_list[ind+1] != '':
                            if not(isPublicIPv4Address(hop_ips_list[ind])):
                                # local_of_overlapping_node[hop_ips_list[ind]].append(hop_ips_list[ind])
                                # local_of_overlapping_node[hop_ips_list[ind+1]].append(hop_ips_list[ind+1])
                                list_of_edges_to_preserve.append((hop_ips_list[ind],hop_ips_list[ind+1]))
                                if rtt_ips_list[ind] != '':
                                    rtt_edges[src_prefix][hop_ips_list[ind]].append(int(rtt_ips_list[ind])/float(non_zero_ind))
                                else:
                                    rtt_edges[src_prefix][hop_ips_list[ind]].append('*')
                                if rtt_ips_list[ind+1] != '':
                                    rtt_edges[src_prefix][hop_ips_list[ind+1]].append(int(rtt_ips_list[ind+1])/float(non_zero_ind))
                                else:
                                    rtt_edges[src_prefix][hop_ips_list[ind]].append('*')
                                # rtt_edges[src_prefix][hop_ips_list[ind]].append(int(rtt_ips_list[ind+1]))
                                # rtt_edges[src_prefix][hop_ips_list[ind]].append(int(rtt_ips_list[ind]))
                        if hop_ips_list[ind] == '':
                            continue
                        if isPublicIPv4Address(hop_ips_list[ind]):
                            if ind < first_hop:
                                throw_away = True
                                break
                            else:
                                # local_of_overlapping_node[hop_ips_list[ind]].append(hop_ips_list[ind])
                                # local_of_overlapping_node[hop_ips_list[ind + 1]].append(
                                #     hop_ips_list[ind + 1])
                                if rtt_ips_list[ind+1] != '':
                                    list_of_edges_to_preserve.append((hop_ips_list[ind], hop_ips_list[ind + 1]))
                                    rtt_edges[src_prefix][hop_ips_list[ind+1]].append(int(rtt_ips_list[ind+1])/float(non_zero_ind))
                                    rtt_edges[src_prefix][hop_ips_list[ind]].append(int(rtt_ips_list[ind])/int(non_zero_ind))
                                last_hop_to_consider =  ind+1
                                break
                    if throw_away:
                        count_thrown_away +=1
                        continue
                    number_of_src_prefix.add(src_prefix)
                    #### TESTING NEW no_solution
                    #src_prefix = src_prefix +'-' + src_squat
                    if list_of_edges_to_preserve != []:
                        list_of_edges[src_prefix].extend(list_of_edges_to_preserve)
                        # list_of_edges[src_squat].extend(list_of_edges_to_preserve)
                    else:
                        continue
                    count += 1
                    # if squat_indexes[-1] > 20:
                    #     print(split_line)
                    rtt_cgnat = False
                    # for t in squat_indexes:
                    # as_source = c.resolve(src_squat)
                    if int(rtt_ips_list[int(squat_indexes[0])]) >= 5:
                        rtt_cgnat = True
                    if int(rtt_ips_list[squat_indexes[-1]]) >= 5:
                        if rtt_cgnat:
                            dict_inference['Validated'].append(int(rtt_ips_list[int(squat_indexes[0])]))
                            dict_validated[src_prefix].append('Validated')
                        else:
                            dict_validated[src_prefix].append('CGNAT_likely')
                            last_hop[src_prefix].append('CGNAT_likely')
                            dict_inference['CGNAT_likely'].append(int(rtt_ips_list[int(squat_indexes[0])]))
                    else:
                        dict_validated[src_prefix].append('Not Validated')
                        dict_inference['Not Validated'].append(int(rtt_ips_list[int(squat_indexes[0])]))
                    dict_everyone[src_prefix].append(int(rtt_ips_list[int(squat_indexes[-1])]))
                    dict_hop_pos[src_prefix].append(first_hop)
                    # for ind in range(0,last_hop_to_consider):
                    #     if hop_ips_list[ind] != '':
                    #         rtt_edges[src_prefix][hop_ips_list[ind]].append(int(rtt_ips_list[ind]))
                    if rtt_ips_list[0] != '':
                        if int(rtt_ips_list[0]) > 0:
                            dict_ratio[src_prefix].append(int(rtt_ips_list[int(squat_indexes[-1])])/int(rtt_ips_list[0]))
                        else:
                            dict_ratio[src_prefix].append(int(rtt_ips_list[int(squat_indexes[-1])]))
                    # else:
                        # dict_ratio[src_prefix].append(0)
                    # dict_of_overlapping_nodes[src_prefix] = local_of_overlapping_node
                    if count >= 1e5:
                        break
    return (list_of_edges,dict_everyone,dict_hop_pos,dict_ratio,rtt_edges)

def detecting_cgnat(path_to_data,output_csv,num_of_edges_required=10):
    list_of_edges,dict_everyone,dict_hop_pos,dict_ratio,rtt_edges = computing_nat_statistic(path_to_data)
    list_of_validated_CGNAT = defaultdict(lambda : [])
    list_of_neighbors = []
    distribution_of_min_tree = []
    connected_components = []
    distribution_of_edges = []
    output_results = []
    distribution_of_tress = []
    number_of_sinks = []
    for key in list_of_edges.keys():
        counting = Counter(list_of_edges[key])
        edges_for_that_graph = set(list_of_edges[key])
        G=nx.DiGraph()
        weighted_neigh = defaultdict(lambda : 0)
        G.add_edges_from(edges_for_that_graph)
        for t in G.nodes():
            for s in nx.neighbors(G,t):
                weighted_neigh[t] += counting[(t,s)]
        last_hops_observed = [node for node in G.nodes if G.out_degree(node) == 0]
        number_of_sinks.append(len(last_hops_observed))
        list_of_latency_in_connected_components = []
        for sink in last_hops_observed:
            list_of_latency_in_connected_components.append(np.median(rtt_edges[key][sink]))
        T = nx.minimum_spanning_tree(G.to_undirected())
        # print(len(T))
        distribution_of_tress.append(len(T))
        max_depth = 0
        for sink_node in last_hops_observed:
            max_depth = max(max(nx.shortest_path_length(G.to_undirected(), sink_node).values()),max_depth)
            list_of_validated_CGNAT[key].append(sink_node)
        distribution_of_min_tree.append(max_depth)
        distribution_of_edges.append(len(G.edges()))
        connected_components.append(nx.number_connected_components(G.to_undirected()))
        prefixes_used = {}
        number_of_different_addresses_leveraged = set()
        for t in G.nodes():
            prefixes_used[t] = t.split('.')[0] +'.0.0.0/8'
            number_of_different_addresses_leveraged.add(t.split('.')[0] +'.0.0.0/8')
        # try:
        number_of_different_addresses_leveraged = list(number_of_different_addresses_leveraged)
        nx.set_node_attributes(G,prefixes_used,'Subnet')
        try:
            for conn_latency in list_of_latency_in_connected_components:
                output_results.append([key,nx.number_connected_components(G.to_undirected()),max_depth,len(last_hops_observed),len(T),len(G.edges()),np.median(dict_everyone[key]),np.quantile(dict_everyone[key],0.25),np.quantile(dict_everyone[key],0.75),np.median(dict_hop_pos[key]),np.quantile(dict_hop_pos[key],0.25),np.quantile(dict_hop_pos[key],0.75),
                                       np.median(dict_ratio[key]),np.quantile(dict_ratio[key],0.25),np.quantile(dict_ratio[key],0.75),conn_latency,len(number_of_different_addresses_leveraged)])
        except:
            continue
        # list_of_neighbors.append(sorted(deg))
        if len(G.edges(data=True))>num_of_edges_required:
            nx.write_graphml(G,'graph/extended_'+str(key.split('/')[0])+'.graphml')
        # if len(H.edges(data=True))>5:
        #     nx.write_graphml(H,'graph/standard_'+str(key.split('/')[0])+'.graphml')
    print(Counter(distribution_of_min_tree))
    df = pd.DataFrame(output_results,columns=['Source Prefix','# of Connected Components','Tree Depth','Number of Sinks','Max Distance to the CGNAT candidate','# of Edges','Median RTT','25 RTT','75 RTT','Median hop','25 hop', '75 hop','Median Ratio','25 Ratio','75 Ratio','Latency_connected_components','Number of Prefixes'])
    print(df)
    df.to_csv(output_csv)
if __name__ == "__main__":
    output_csv = '../../results/cgnat_statistics.csv'
    path_to_data = '/Users/geode/Documents/Datasets/Squat/'
    main(path_to_data,output_csv,output_graph = 'graph/')
