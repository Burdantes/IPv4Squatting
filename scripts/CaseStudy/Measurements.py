import pandas as pd
from tqdm import tqdm
import json
import pytz
import datetime
from collections import defaultdict
from copy import  deepcopy
import os
from ripe.atlas.cousteau import (
  Ping,
  AtlasSource,
  AtlasCreateRequest,
  Probe,
  Traceroute
)
from ripe.atlas.sagan import Result

import urllib.request
import socket
from collections import Counter
import ast
import dns.resolver as dnsres
import dns.reversename as dnsrever
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="geoapiExercises")
def city_state_country(coord):
    location = geolocator.reverse(coord, exactly_one=True)
    address = location.raw['address']
    city = address.get('city', '')
    state = address.get('state', '')
    country = address.get('country', '')
    if city == '':
        city = state
    return city


def reading_squatters_DoD():
    file = open("../../result/CaseStudy/ases_squatting_DoD_after.txt", "r")
    txt = file.readlines()
    output = {}
    for row in txt:
        if row.startswith('#'):
            continue
        else:
            output[row.split(' ')[0]] = row.split(' ')[1].replace('\n','')
    AS_level_metainfos = pd.read_csv('../../data/MetaInformation/PeeringDB_AS_level_info_2021-09-01.csv',index_col = 0
    )
    print(AS_level_metainfos.columns)
    for ASN in output.keys():
        print(ASN,AS_level_metainfos[AS_level_metainfos.asn==int(ASN)][['looking_glass', 'route_server']].values,output[ASN])
    probes = []
    print(len(output))
    for t in txt:
        if t.startswith('#'):
            continue
        t = t.replace('\n', '')
        # t = t.split('
        probes.append(t)
    return probes


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


def finding_last_responsive_hop(ip_path):
    complete_elements = []
    adding_stars_pos = []
    for i,s in enumerate(ip_path):
        adding_elements = []
        for t in s:
            if not(t is None):
                adding_elements.append(t)
            else:
                adding_stars_pos.append(i)
        if len(adding_elements)>0:
            complete_elements.append(adding_elements[0])
    interm_dico = dict(Counter(adding_stars_pos))
    final_stars = []
    for s in interm_dico.keys():
        if interm_dico[s] == 3:
            final_stars.append(s)
    return complete_elements,final_stars

def far_away(rtt_from_sources):
    complete_elements = []
    for s in rtt_from_sources:
        adding_elements = []
        if not (s is None):
            adding_elements.append(s)
        if len(adding_elements) > 0:
            complete_elements.append(adding_elements[0])
    return complete_elements[-1]

def scheduling_specific_measurements(AS_to_probes):
    associated_values = []
    ATLAS_API_KEY = "4a4d28a0-7cfe-458c-9bd4-e0592da7d5be"
    new_timezone = pytz.timezone("Europe/Amsterdam")
    #
    date = datetime.datetime.now(new_timezone)
    files = os.listdir("Measurements/")
    upd_files = deepcopy(files)
    number_of_measurements = 0
    for t in upd_files:
        files.append(t.split('measurements')[0])
        files.append(t.split('.txt')[0])
    for key in AS_to_probes.keys():
        if number_of_measurements < 499:
            number_of_measurements +=1
            continue
        ip = AS_to_probes[key][1]
        list_of_sources = ''
        for probe_id in pro[key][0]:
            list_of_sources += str(probe_id) + ','
        traceroute = Traceroute(
            af=4,
            target=ip,
            description="traceroute",
            protocol='ICMP',
        )
        source1 = AtlasSource(
            type="probes",
            value=list_of_sources[:-1],
        requested = 4)
        atlas_request = AtlasCreateRequest(
            start_time=date,
            key=ATLAS_API_KEY,
            measurements=[traceroute],
            msm_id=2016892,
            sources=[source1],
            is_oneoff=True,
            packet=4,
        )
        (is_success, response) = atlas_request.create()
        # print(is_success, response)
        if is_success:
            print(response)
        else:
            continue
        number_of_measurements += 1
        associated_values.append(response['measurements'])
        print(response['measurements'])
        if number_of_measurements == 599:
            break
    with open('Measurements/sixth_round.txt', 'a+') as f:
        for item in associated_values:
            f.write("%s\n" % item)
            # break

path_to_probes = '../../data/MetaInformation/20210630.json'
probes = {d['id']: d for d in json.load(open(path_to_probes))['objects']}
df_probes = pd.DataFrame(probes).transpose()
<<<<<<< Updated upstream
list_of_cities_in_probes = {}
=======
# list_of_cities_in_probes = {}
>>>>>>> Stashed changes
# df_probes =df_probes[df_probes['status_name']=='Connected']
# probes = reading_squatters_DoD()
# print(probes)
# ASes_to_probes = dict()
# count_number_of_probes = 0
# ases_considered = []
# already_counted = []
# for t in probes:
#     print(t)
#     pro = t.split(' ')[0]
#     if (int(pro) in df_probes['asn_v4'].values):
#         ases_considered.append(pro)
#         ind = list(df_probes[df_probes['asn_v4']==int(pro)].index)
#         # for pr in ind:
#         if not(pro in already_counted):
#             count_number_of_probes += len(ind)
#             already_counted.append(pro)
#         ASes_to_probes[pro] = [ind,t.split(' ')[1]]
# print('Number of Ases considered', len(set(ases_considered)))
# print('Number of total probes considered',count_number_of_probes)
# scheduling_specific_measurements(ASes_to_probes)

def reading_IXP(ixp_interfaces_file = '../data/IXP/interfaces_ixp-20210504.txt'):
    dico = {}
    with open(ixp_interfaces_file, "rb") as fin:
        for line in fin:
            line = line.decode("utf-8")
            line = str(line.strip())
            if line.startswith("#"):
                continue
            # fields = line.split("|")
            fields = line.split("\t")
            if fields[1] != 'None':
                dico[fields[0]] = fields[1]+'-'+fields[2]
    return dico

txt_interconnection = []
my_measures = []
for rounds in ['First_round','Second_round','third_round','fourth_round','fifth_round','sixth_round']:
    with open('Measurements/'+rounds+'.txt') as f:
        my_measure = f.read()
        my_measure = my_measure.split('\n')[:-1]
        my_measures.extend(my_measure)
print(my_measures)
c = Cymru()
dico = {}
dico_internal = {}
dico_external = {}
set_of_internal_looking_ASes = []
set_of_external_looking_ASes = []
final_res_to_plot = defaultdict(lambda: [])
set_of_countries = defaultdict(lambda : [])
IXP_mapping = reading_IXP('/Users/geode/Documents/GitHub/missing-peering-links/data/IXP/interfaces_ixp-20210504.txt')
for msm_id in tqdm(my_measures[:-1]):
    msm_id = ast.literal_eval(msm_id)
    print(msm_id[0])
    msm_id = msm_id[0]
    with urllib.request.urlopen(
            "https://atlas.ripe.net/api/v2/measurements/%d/results/?format=txt" % msm_id) as my_results:
        results = my_results.readlines()
        for my_result in results:
            # try:
                atlas_results = Result.get(my_result.decode("utf-8"))
                if atlas_results.type != 'traceroute':
                    continue
                to_keep,pos_for_stars = finding_last_responsive_hop(atlas_results.ip_path)
                as_mapping = c.resolve(to_keep)
                add = 0
                for k in range(len(to_keep)):
                    # k_bis = k
                    if k  <= len(as_mapping) - 1:
                        if as_mapping[k][0] != to_keep[k]:
                            # add += 1
                            as_mapping.insert(k,(to_keep[k],'NA'))
                    else:
                        as_mapping.append((to_keep[k],'NA'))
                new_mapping = []
                # print(df_probes[df_probes.index==atlas_results.probe_id]['asn_v4'].values[0])
                cc_code = df_probes[df_probes.index==atlas_results.probe_id]['country_code'].values[0]
                # print(cc_code)
                if cc_code is None:
                    continue
                new_mapping.append('AS' + str(df_probes[df_probes.index==atlas_results.probe_id]['asn_v4'].values[0]))
                for t in as_mapping[1:]:
                    if t[0] in IXP_mapping.keys():
                        new_mapping.append('AS'+IXP_mapping[t[0]])
                    else:
                        new_mapping.append(t[1])
                as_mapping = [a_tuple[1] for a_tuple in as_mapping]
                list_of_dns = []
                for t in to_keep:
                    try:
                        domain_address = dnsrever.from_address(t)
                        dns = str(dnsres.query(domain_address, 'PTR')[0])
                    except:
                        dns = ''
                    list_of_dns.append(dns)
                rtt_list = []
                for t in atlas_results.hops:
                    interm_list = []
                    for s in t.packets:
                        interm_list.append(s.rtt)
                    try:
                        rtt_list.append(min(interm_list))
                    except:
                        try:
                            rtt_list.append(interm_list[0])
                        except:
                            continue
                for position in pos_for_stars:
                    as_mapping.insert(position, '*')
                    new_mapping.insert(position,'*')
                    to_keep.insert(position,'*')
                    list_of_dns.insert(position,'*')
                dico.update({cc_code + ':' + str(atlas_results.probe_id) + ":" + atlas_results.destination_name: [to_keep, rtt_list,new_mapping,as_mapping,list_of_dns]})
                as_path = list(set(as_mapping))
                if len(as_path) > 2:
                    # print('This one exits')
                    if not(atlas_results.probe_id in list_of_cities_in_probes):
                        list_of_cities_in_probes[atlas_results.probe_id] = city_state_country((df_probes[df_probes.index == atlas_results.probe_id]['latitude'].values[0],df_probes[df_probes.index == atlas_results.probe_id]['longitude'].values[0]))
                    set_of_countries[
                        str(df_probes[df_probes.index == atlas_results.probe_id]['asn_v4'].values[0]) + '-' + str(
                            atlas_results.destination_name) + '-EXIT'].append(
                        cc_code + '-' + list_of_cities_in_probes[atlas_results.probe_id])
                    dico_external.update({str(atlas_results.probe_id) + ":" + atlas_results.destination_name + ':'+str(df_probes[df_probes.index==atlas_results.probe_id]['asn_v4'].values[0]): [to_keep, rtt_list,new_mapping,as_mapping,list_of_dns]})
                    set_of_external_looking_ASes.append(str(df_probes[df_probes.index==atlas_results.probe_id]['asn_v4'].values[0]))
                    final_res_to_plot[
                        str(df_probes[df_probes.index == atlas_results.probe_id]['asn_v4'].values[0]) + '-' + str(
                            atlas_results.destination_name)].append('Exit')
                else:
                    if not (atlas_results.probe_id in list_of_cities_in_probes):
                        list_of_cities_in_probes[atlas_results.probe_id] = city_state_country((
                            df_probes[df_probes.index == atlas_results.probe_id]['latitude'].values[0],
                            df_probes[df_probes.index == atlas_results.probe_id]['longitude'].values[0]))
                    set_of_countries[
                        str(df_probes[df_probes.index == atlas_results.probe_id]['asn_v4'].values[0]) + '-' + str(atlas_results.destination_name) +'-REMAIN'].append(
                        cc_code + '-' + list_of_cities_in_probes[atlas_results.probe_id])
                    final_res_to_plot[
                        str(df_probes[df_probes.index == atlas_results.probe_id]['asn_v4'].values[0]) + '-' + str(
                            atlas_results.destination_name)].append('Remain')

                    # print(new_mapping)
                    pos = []
                    for i, j in enumerate(new_mapping):
                        if j == new_mapping[0]:
                            pos.append(i)
                    # if pos[-1] >= len(new_mapping) - 2:
                    #     print('INTERNAL ROUTING')

                    dico_internal.update({str(atlas_results.probe_id) + ":" + atlas_results.destination_name + ':'+str(df_probes[df_probes.index==atlas_results.probe_id]['asn_v4'].values[0]): [to_keep, rtt_list,new_mapping,as_mapping,list_of_dns]})
                    set_of_internal_looking_ASes.append(str(df_probes[df_probes.index==atlas_results.probe_id]['asn_v4'].values[0]))
                # print(set_of_countries)
                if rtt_list[-1] is None:
                    continue
                if rtt_list[-1] < 2:
                    print(new_mapping[0] + ' and ' + new_mapping[-1] + 'are interconnected')
                    txt_interconnection.append((new_mapping[0], new_mapping[-1]))
            # except:
            #     continue
            # print(dico)
# print(dico_external)
# print('INTERNAL')
# print(dico_internal)
print(Counter(set_of_external_looking_ASes))
print(Counter(set_of_internal_looking_ASes))
print(len(Counter(set_of_internal_looking_ASes)))
print(len(Counter(set_of_external_looking_ASes)))
print(set(set_of_external_looking_ASes) & set(set_of_internal_looking_ASes))
for t in final_res_to_plot.keys():
    final_res_to_plot[t] = Counter(final_res_to_plot[t])
with open("count_of_internal+external_perIP.json", 'w') as fout:
    json_dumps_str = json.dumps(final_res_to_plot)
    print(json_dumps_str, file=fout)
with open("example_of_external.json", 'w') as fout:
    json_dumps_str = json.dumps(dico_external)
    print(json_dumps_str, file=fout)
with open("example_of_internal.json", 'w') as fout:
    json_dumps_str = json.dumps(dico_internal)
<<<<<<< Updated upstream
    print(json_dumps_str, file=fout)
=======
    print(json_dumps_str, file=fout)
>>>>>>> Stashed changes
