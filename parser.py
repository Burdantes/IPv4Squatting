import json
import gzip, bz2
import shlex, subprocess
from ipaddress import ip_address
from os.path import exists
from os import listdir, mkdir
import string
import random
import ipaddress
from collections import defaultdict,Counter
from tqdm import tqdm
import os

PATH_TO_TRACEROUTE_FOLDER = 'data'

list_of_destination = dict()
time_distrib = defaultdict(lambda : [])
for i in range(0,2**(24)-1):
    ipadd = ipaddress.ip_address(i*256)
    if ipadd.is_private:
        continue
    ippref = ipaddress.ip_network(i*256).supernet(new_prefix=24)
    list_of_destination[ippref] = 0

def randomString(stringLength=10): #{{{
    letters = string.ascii_lowercase + string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(stringLength))
#}}}

TEMP_DIR="temp/"
STAR=ip_address("255.255.255.255")
NO_RTT = -1

import ipaddress
import json
import os

DoD_addresses = ['6.0.0.0/8', '7.0.0.0/8', '11.0.0.0/8','9.0.0.0/8','11.0.0.0/8','16.0.0.0/8','19.0.0.0/8','21.0.0.0/8','22.0.0.0/8','26.0.0.0/8', '28.0.0.0/8', '29.0.0.0/8', '30.0.0.0/8', '33.0.0.0/8','43.0.0.0/8','48.0.0.0/8','56.0.0.0/8']

squat_prefixes = [ipaddress.ip_network(p) for p in DoD_addresses]

def is_squat_ip(ip_str):
    ip = ipaddress.ip_address(ip_str)
    for sp in squat_prefixes:
        if ip in sp:
            return True
    return False

def get_traceroutes_with_squat_ip(filename):
    '''
    Return and output to file the traceroutes with squat IP hops
    Return: a list of traceroute dict
    File: each line is a dict
    '''
    if os.path.exists('{}.squat.full.txt'.format(filename)):
        return
    ret = []
    total = 0
    with open(filename, 'r') as fin:
        for line in fin:
            line = line.rstrip()
            tr = json.loads(line)
            if tr['type'] == 'trace':
                total += 1
                try:
                    # some traceroutes stopped abnormally they donot have "hops"
                    hops = tr['hops']
                except:
                    #print(line)
                    continue
                flag = False
                for i, hop in enumerate(hops):
                    hop_ip = hop['addr']
                    if is_squat_ip(hop_ip):
                        flag = True
                        tr['squat_idx'] = i
                        tr['squat_ip'] = hop_ip
                        break
                if flag:
                    ret.append(tr)

    #print('# traceroutes with squat IP in {}: {} out of {}'.format(filename, len(ret), total))

    with open('{}.squat.full.txt'.format(filename), 'w') as fout:
        for tr in ret:
            hop_ips = [hop['addr'] for hop in tr['hops']]
            src_ip = tr['src']
            dst_ip = tr['dst']
            squat_ip = tr['squat_ip']
            squat_idx = tr['squat_idx']
            hop_ips_str = ','.join(hop_ips)
            fout.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(src_ip, dst_ip, -1, squat_ip, hop_ips_str, squat_idx))
    return ret



# -------------------------------------------------------------------- #
def traceParserARK(traceroute, infos, probe_id): #{{{
    traceroute = json.loads(traceroute)
    # try:
    #     print(traceroute.keys())
    #     print(traceroute['start'])
    # except:
    #     print('fuck')
    # if("dst" not in traceroute) or ('start' not in traceroute):
    if "dst" not in traceroute:
        return None
    target = ip_address(traceroute["dst"])
    prefix = ipaddress.ip_network(target).supernet(new_prefix=24)
    # print(list_of_destination[prefix])
    list_of_destination[prefix] += 1
    if "start" not in traceroute:
        return None
    time_distrib[prefix].append(traceroute['start']['sec'])
    # print(list_of_destination[prefix])
    if(traceroute["type"] != "trace"):
        return None

    if(traceroute["stop_reason"] != "COMPLETED" and traceroute["stop_reason"] != "GAPLIMIT"):
        return {traceroute['dst']:'UNREACHED'}

    # if(traceroute['stop_reason']=="GAPLIMIT"):
    #     print(traceroute)
    #     return {traceroute['dst']:'GAPLIMIT'}

    if("hops" not in traceroute):
        return None

    ip_path = [[STAR] for x in range(traceroute["hop_count"])]
    rtt_path = [[NO_RTT] for x in range(traceroute["hop_count"])]
    src = ip_address(traceroute["src"])
    timestamp = int(traceroute["start"]["sec"])
    target = ip_address(traceroute["dst"])

    if("sources" in infos and str(probe_id) not in infos["sources"]):
        return None

    for hop in traceroute["hops"]:

        iface = ip_address(hop["addr"])
        rtt = hop["rtt"]
        ttl = hop["probe_ttl"]

        if(STAR in ip_path[ttl-1]):
            ip_path[ttl-1] = []
        if(NO_RTT in rtt_path[ttl-1]):
            rtt_path[ttl-1] = []

        ip_path[ttl-1].append(iface)
        rtt_path[ttl-1].append(rtt)
    return (probe_id, timestamp, src, target, ip_path, rtt_path)

def parseTraceroutes(traces_dir, infos): #{{{

    files = listdir(traces_dir)

    if(not exists(TEMP_DIR)):
        mkdir(TEMP_DIR)

    for file in files:
        print(file)
        if(file[-3:] == ".gz"):
            cmd = "zcat " + traces_dir + "/" + file
        elif(file[-4:] == ".bz2"):
            cmd = "bzcat " + traces_dir + "/" + file
        else:
            cmd = "cat " + traces_dir + "/" + file
        tmpfile = file+'.parsed'
        if tmpfile in listdir(TEMP_DIR):
            print('file exists', tmpfile)
            get_traceroutes_with_squat_ip(TEMP_DIR+"/"+tmpfile)
            continue

        with open(TEMP_DIR+"/"+tmpfile, "w") as outfile:
            p_decompress = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
            cmd = "sc_warts2json"
            process = subprocess.Popen(shlex.split(cmd), stdin=p_decompress.stdout,\
                                       stdout=outfile)
            process.wait()
        
        #count = 0
        #for traceroute in open(TEMP_DIR+"/"+tmpfile):
            #count += 1
            #probe_id = file.split(".")[0]
            #yield traceParserARK(traceroute.strip(), infos, probe_id)
        get_traceroutes_with_squat_ip(TEMP_DIR+"/"+tmpfile)
        cmd = "rm " + TEMP_DIR+"/"+tmpfile
        subprocess.Popen(shlex.split(cmd))

if __name__ == "__main__":
    infos = dict()
    merged_data = {}
    for i,t in tqdm(enumerate(parseTraceroutes(PATH_TO_TRACEROUTE_FOLDER, infos))):
        #merged_data[i] = t
        pass
