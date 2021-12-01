from collections import defaultdict,Counter
import ipaddr
from util import isPublicIPv4Address
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

month = '04'
prefix_length_to_be_considered = '/24'
files = [
    # 'sample_data.txt',
     'squatspace-results-2021-03-10.newformat.txt',
        'squatspace-results-2021-04-10.newformat.txt',
        'squatspace-results-2021-05-10-2021-05-16.txt',
        'squatspace-results-2021-06-10-2021-06-16.txt'
]

src_ip2squat_ip = {}

unique_src_ips = set()
unique_src_squatters = set()

slash8tosquat = defaultdict(set)
allsquat = set()

srcslash24tosrcipsquat = defaultdict(set)
srcslash24tosquat = defaultdict(set)
all_nat_asns = set()
all_cgnat_asns = set()
prefix_d = defaultdict(set)
id = 0
for fn in files:
    print(fn)
    results = {}
    with open('../datasets/traceroutes/squat/'+fn, 'r') as fin:
        for line in tqdm(fin):
            if line.startswith('#') or 'trace_id' in line:
                continue
            line = line.rstrip()
            trace_id, src_asn, squat_ip, squat_index, squat_asn, squat_org, squat_rir, src_ip, squat_idx_new = line.split('|')
            if src_ip == 'None':
                continue
            unique_src_ips.add(src_ip)

            # if src_asn == '37963' and src_ip == '42.120.72.110':
            #     print(line)


            allsquat.add(squat_ip)
            slash8 = ipaddr.IPv4Network(squat_ip + '/8')
            slash8tosquat[str(slash8.network) + '/8'].add(squat_ip)
            prefix_d[('.').join(src_ip.split('.')[:-1])].add(src_ip.split('.')[-1])
            src_slash24 = ipaddr.IPv4Network(src_ip + prefix_length_to_be_considered)
            src_slash24 = str(src_slash24.network) + prefix_length_to_be_considered
            srcslash24tosrcipsquat[src_slash24].add(src_ip)
            srcslash24tosquat[src_slash24].add(squat_ip)
            is_it_known_kind = False
            countings = 0
            if src_asn == squat_asn:
                unique_src_squatters.add(squat_asn)
                if trace_id not in results:
                    results[id] = {
                        'squat_asn': squat_asn,
                        'squat_org': squat_org,
                        'src_ip': src_ip,
                        'squat_ips': set(),
                        'flags':'NAT'
                    }
                    results[id]['squat_ips'].add(squat_ip)
                    is_it_known_kind = True
                    id+=1
                if squat_index!=squat_idx_new:
                    if int(squat_idx_new) == 0:
                        unique_src_squatters.add(squat_asn)
                        results[id] = {
                            'squat_asn': squat_asn,
                            'squat_org': squat_org,
                            'src_ip': src_ip,
                            'squat_ips': set(),
                            'flags':'CGNAT'
                        }
                        is_it_known_kind = True
                        results[id]['squat_ips'].add(squat_ip)
                        id += 1
                # if src_ip.startswith('42.120.72.110'):
                #     print(trace_id, src_ip, squat_ip)
            if not(is_it_known_kind):
                countings +=1
    print(fn, len(results))
    for trace_id in results:
        squat_asn = results[trace_id]['squat_asn']
        squat_org = results[trace_id]['squat_org']
        flag = results[trace_id]['flags']
        src_ip = results[trace_id]['src_ip']
        squat_ips = results[trace_id]['squat_ips']
        if src_ip not in src_ip2squat_ip:
            src_ip2squat_ip[src_ip] = {
                'asn': squat_asn,
                'org': squat_org,
                'squat_ip_seen': [squat_ips],
                'trace_count': 1,
                'trace_count_2':0,
                'flag':flag,
                'flag_2':'',
            }
        elif src_ip2squat_ip[src_ip]['flag']==flag:
            src_ip2squat_ip[src_ip]['squat_ip_seen'].append(squat_ips)
            src_ip2squat_ip[src_ip]['trace_count'] += 1
        elif src_ip2squat_ip[src_ip]['flag_2']=='':
            src_ip2squat_ip[src_ip]['flag_2'] = flag
        elif src_ip2squat_ip[src_ip]['flag_2']==flag:
            src_ip2squat_ip[src_ip]['squat_ip_seen'].append(squat_ips)
            src_ip2squat_ip[src_ip]['trace_count_2'] += 1
# print(src_ip2squat_ip)
nat_asns = set()
nat_asns2src_ips = defaultdict(set)
cgnat_asns = set()
cgnat_asns2src_ips = defaultdict(set)
# cgnat_orgs = set()

trace_contributing = 0
count_src_ip_cgnat = 0
count_src_ip_nat = 0
# the number of traceroute with squatted NAT address for every / 24
slash24srctonumtraceroutewithsquatnat = defaultdict(int)
slash24srctonumtraceroutewithsquatcgnat = defaultdict(int)
slash24srctonumsrcnat = defaultdict(int)
slash24srctonumsrccgnat = defaultdict(int)

slash24nattoasn = {}
slash24cgnattoasn = {}


src_ip_nat = set()
src_ip_cgnat = set()
for src_ip in src_ip2squat_ip:
    if src_ip2squat_ip[src_ip]['flag'] == 'NAT' or src_ip2squat_ip[src_ip]['flag_2'] == 'NAT':
        squat_ips_seen = src_ip2squat_ip[src_ip]['squat_ip_seen']
        # if src_ip.startswith('42.120.72.'):
        #     print(src_ip, squat_ips_seen)
        asn = src_ip2squat_ip[src_ip]['asn']
        org = src_ip2squat_ip[src_ip]['org']
        if src_ip2squat_ip[src_ip]['flag'] == 'NAT':
            tcount = src_ip2squat_ip[src_ip]['trace_count']
        elif src_ip2squat_ip[src_ip]['flag_2'] == 'NAT':
            tcount = src_ip2squat_ip[src_ip]['trace_count_2']
        all_nat_asns.add(squat_asn)
        # print(src_ip, len(squat_ips_seen))
        for i in range(len(squat_ips_seen)):
            x = squat_ips_seen[0] - squat_ips_seen[i]
            y = squat_ips_seen[i] - squat_ips_seen[0]

            if len(x) > 0 or len(y) > 0:
                # this src ip is NAT
                src_ip_nat.add(src_ip)


                src_slash24 = ipaddr.IPv4Network(src_ip + prefix_length_to_be_considered)
                src_slash24 = str(src_slash24.network) + prefix_length_to_be_considered

                slash24srctonumtraceroutewithsquatnat[src_slash24] += tcount
                slash24srctonumsrcnat[src_slash24] += 1
                slash24nattoasn[src_slash24] = {'asn': asn, 'org': org}
                nat_asns.add(asn)
                count_src_ip_nat += 1
                trace_contributing += len(squat_ips_seen)
                nat_asns2src_ips[asn].add(src_ip)
                break
    if src_ip2squat_ip[src_ip]['flag'] == 'CGNAT' or src_ip2squat_ip[src_ip]['flag_2'] == 'CGNAT':
        asn = src_ip2squat_ip[src_ip]['asn']
        org = src_ip2squat_ip[src_ip]['org']
        if src_ip2squat_ip[src_ip]['flag'] == 'CGNAT':
            tcount = src_ip2squat_ip[src_ip]['trace_count']
        elif src_ip2squat_ip[src_ip]['flag_2'] == 'CGNAT':
            tcount = src_ip2squat_ip[src_ip]['trace_count_2']
        src_ip_cgnat.add(src_ip)
        src_slash24 = ipaddr.IPv4Network(src_ip +prefix_length_to_be_considered)
        src_slash24 = str(src_slash24.network) + prefix_length_to_be_considered

        slash24srctonumtraceroutewithsquatcgnat[src_slash24] += tcount
        slash24srctonumsrccgnat[src_slash24] += 1

        cgnat_asns.add(asn)
        count_src_ip_cgnat += 1
        trace_contributing += len(squat_ips_seen)
        cgnat_asns2src_ips[asn].add(src_ip)
        slash24cgnattoasn[src_slash24] = {'asn': asn, 'org': org}

print('# cgnat ASNs:', len(cgnat_asns))
print('# nat ASNs:', len(nat_asns))
print('# nat src_ips', count_src_ip_nat)
print('# cgnat src_ips', count_src_ip_cgnat)
print('# total src_ips', len(unique_src_ips))
print('# src squatters', len(unique_src_squatters))
print('# traceroute contributing', (trace_contributing))

print('# squat address', len(allsquat))
# for slash8 in slash8tosquat:
#     print('#', slash8, len(slash8tosquat[slash8]))
prefix = {}
for t in prefix_d.keys():
    prefix[t] = len(prefix_d[t])
x = np.sort(list(prefix.values()))
N = len(x)
# get the cdf values of y
y = np.arange(N) / float(N)*100

# plotting
plt.xlabel('Number of source IP addresses with NAT behavior in a /24')
plt.ylabel('Cum. Dist. Frac. in %')
plt.plot(x, y, marker='o')
plt.xlim(0, 20)
plt.ylim(0, 100)
plt.savefig('distribution_of_source_values')


name = 'slash'+ prefix_length_to_be_considered[1:]
with open('data/statistics/'+name+'NATtoAS.txt', 'w') as fout:
    for src_slash24 in slash24nattoasn:
        asn = slash24nattoasn[src_slash24]['asn']
        org = slash24nattoasn[src_slash24]['org']
        fout.write('{}|{}|{}\n'.format(src_slash24, asn, org))

with open('data/statistics/'+name+'CGNATtoAS.txt', 'w') as fout:
    for src_slash24 in slash24cgnattoasn:
        asn = slash24cgnattoasn[src_slash24]['asn']
        org = slash24cgnattoasn[src_slash24]['org']
        fout.write('{}|{}|{}\n'.format(src_slash24, asn, org))

# how many traceroutes in /24 NAT
with open('data/statistics/'+name+'srctonumtraceroutewithsquatnat.txt', 'w') as fout:
    for src_slash24 in slash24srctonumtraceroutewithsquatnat:
        fout.write('{} {}\n'.format(src_slash24, slash24srctonumtraceroutewithsquatnat[src_slash24]))

# how many traceroutes in /24 CGNAT
with open('data/statistics/'+name+'srctonumtraceroutewithsquatcgnat.txt', 'w') as fout:
    for src_slash24 in slash24srctonumtraceroutewithsquatcgnat:
        fout.write('{} {}\n'.format(src_slash24, slash24srctonumtraceroutewithsquatcgnat[src_slash24]))

# how many source IP in /24 NAT
with open('data/statistics/'+name+'srctonumsrcsquatnat.txt', 'w') as fout:
    for src_slash24 in slash24srctonumsrcnat:
        fout.write('{} {}\n'.format(src_slash24, slash24srctonumsrcnat[src_slash24]))

# how many source IP in /24 CGNAT
with open('data/statistics/'+name+'srctonumsrcsquatcgnat.txt', 'w') as fout:
    for src_slash24 in slash24srctonumsrccgnat:
        fout.write('{} {}\n'.format(src_slash24, slash24srctonumsrccgnat[src_slash24]))

# how many source IP in /24 squat
with open('data/statistics/'+name+'srctonumsrcsquat.txt', 'w') as fout:
    for src_slash24 in srcslash24tosrcipsquat:
        fout.write('{} {}\n'.format(src_slash24, len(srcslash24tosrcipsquat[src_slash24])))

# how many squat IP observed in /24
with open('data/statistics/'+name+'srctonumsquats.txt', 'w') as fout:
    for src_slash24 in srcslash24tosquat:
        fout.write('{} {}\n'.format(src_slash24, len(srcslash24tosquat[src_slash24])))

# the source that returns IP NAT
with open('data/statistics/src_ip_nat'+name+'.txt', 'w') as fout:
    for ip in src_ip_nat:
        fout.write('{}\n'.format(ip))

# the source that returns IP CGNAT
with open('data/statistics/src_ip_cgnat'+name+'.txt','w') as fout:
    for ip in src_ip_cgnat:
        fout.write('{}\n'.format(ip))

# the source that appears to be configured with strat 1
with open('data/router_config/config_NAT'+name+'.txt', 'w') as fout:
    for ases in list(all_nat_asns):
        fout.write('{}\n'.format(ases))

# the source that appears to be configured with strat 2
with open('data/router_config/config_CGNAT'+name+'.txt','w') as fout:
    for ases in list(all_cgnat_asns):
        fout.write('{}\n'.format(ases))
