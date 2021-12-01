import pybgpstream
from collections import defaultdict
import json
from tqdm import tqdm
import multiprocessing as mp
import radix # pip install py-radix or ppy-radix for pure python version
import os
from util import load_squatspace_default

def getting_to_path():
    file1 = open("/home/datasets/bgp/dumps.20210501T182313.txt", "r")
    list_of_arguments = []
    for t in (file1.readlines()):
        t = t.replace('\n','')
        list_of_arguments.append(t)
    pool = mp.Pool(8)
    results = pool.map(parsing_data, list_of_arguments)
    res = {}
    print(results)
    for i in tqdm(range(0,len(results))):
        print(i,results[i])
        res = {**res,**dict(results[i])}
    with open('output_ribs.json', 'w') as fp:
        json.dump(res, fp)

def parsing_data(t):
    prefix = defaultdict(lambda : [])
    path = "/home/datasets/bgp/"
    # DoD_address = ['56.0.0.0/8', '48.0.0.0/8', '43.0.0.0/8',
    #                '33.0.0.0/8', '30.0.0.0/8', '29.0.0.0/8',
    #                '28.0.0.0/8', '26.0.0.0/8', '25.0.0.0/8',
    #                '22.0.0.0/8', '21.0.0.0/8', '19.0.0.0/8',
    #                '16.0.0.0/8', '11.0.0.0/8', '9.0.0.0/8',
    #                '7.0.0.0/8', '6.0.0.0/8'
    #                ]
    # DoD_address = load_squatspace_default().prefixes()
    DoD_address = ['6.0.0.0/8', '7.0.0.0/8', '11.0.0.0/8', '21.0.0.0/8', '22.0.0.0/8', '26.0.0.0/8',
                            '28.0.0.0/8', '29.0.0.0/8', '30.0.0.0/8', '33.0.0.0/8', '55.0.0.0/8', '214.0.0.0/8',
                            '215.0.0.0/8']
    filters = (' ').join(DoD_address)
    filters = 'prefix more ' + filters
    stream = pybgpstream.BGPStream(
        from_time="2010-01-02 07:13:38", until_time="2021-05-23 07:13:38",
        projects=["routeviews", "ris"],
        #    project="routeviews-stream",
        record_type="ribs",
        filter=filters
    )
    stream.set_data_interface("singlefile")
    stream.set_data_interface_option("singlefile", "rib-file", path+t)
    monitors = t.split('/')[0]
    for elem in stream:
        prefix[elem.fields['prefix']+'|'+monitors + '|' + str(elem.time)].append(str(elem.time)+'|'+str(elem.peer_asn) + '|' + elem.fields['as-path'])
    return dict(prefix)

if __name__ == "__main__":
    getting_to_path()
