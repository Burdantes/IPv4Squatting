from collections import defaultdict
import util
import sys


squatspace_trie = util.load_squatspace_default()

'''
A) same AS. [public, squats, public]
B) same AS. [public, */private, squats, public]
C) different AS. [public, squats, public]
D) different AS. [public, */private, squats, public]
E) unknown AS. [public, squats, public]
F) unknown AS. [public, */private, squats, public]
'''

fn = sys.argv[1]

count = 0
with open(fn, 'r') as fin:
    for line in fin:
        count += 1
        flag = '?'

        line = line.rstrip()
        # print(line)
        src_asn, dst_asn, squat_indexes_str, hop_ips_str, fixed_asn_path_str, fixed_org_path_str, better_org_path_str, rir_org_path_str, src_ip = line.split(
            '\t')

        squat_indexes = [int(i) for i in squat_indexes_str.split('|')]
        hop_ips = [ip for ip in hop_ips_str.split('|')]
        fixed_asn_path = [asn for asn in fixed_asn_path_str.split('|')]
        fixed_org_path = [org for org in fixed_org_path_str.split('|')]

        for squat_index in squat_indexes:
            public_before_idx = -1
            # try to find public before squat_index
            for i in range(1, squat_index + 1):
                idx = squat_index - i
                ip = hop_ips[idx]
                if ip != '*' and util.isPublicIPv4Address(ip) and not squatspace_trie.search_best(ip):
                    public_before_idx = idx
                    break

            public_after_idx = len(hop_ips)
            for i in range(1, len(hop_ips) - squat_index):
                idx = squat_index + i
                ip = hop_ips[idx]
                if ip != '*' and util.isPublicIPv4Address(ip) and not squatspace_trie.search_best(ip):
                    public_after_idx = idx
                    break

            found = False
            same_asn = False
            unknown_asn = False
            exist_private_star = False
            if public_before_idx >= 0 and public_after_idx < len(hop_ips):
                # make sure it only cross two ASNs
                asns_between = set()
                for i in range(public_before_idx, public_after_idx + 1):
                    asn = fixed_asn_path[i]
                    asns_between.add(asn)
                if len(asns_between) > 2:
                    found = False
                else:
                    found = True

                # check ASN of public before and after
                asn_before = fixed_asn_path[public_before_idx]
                asn_after = fixed_asn_path[public_after_idx]
                if asn_before == asn_after:
                    same_asn = True
                if asn_before == '*' or asn_after == '*':
                    unknown_asn = True

                # check if there are *s or privates between
                for i in range(public_before_idx + 1, public_after_idx):
                    ip = hop_ips[i]
                    if ip == '*' or not util.isPublicIPv4Address(ip):
                        exist_private_star = True

            if found:
                if unknown_asn:
                    if not exist_private_star:
                        flag = 'E'
                    else:
                        flag = 'F'
                elif same_asn:
                    if not exist_private_star:
                        flag = 'A'
                    else:
                        flag = 'B'
                else:
                    if not exist_private_star:
                        flag = 'C'
                    else:
                        flag = 'D'
                # idx_str = '{}|{}'.format(public_before_idx, public_after_idx)
        
        if flag == 'A':
            print('{}\t{}\t{}\t{}'.format(count, line, 'internal_router'))
        elif flag == 'C':
            print('{}\t{}\t{}\t{}'.format(count, line, 'border_router'))
        elif flag == 'E':
            print('{}\t{}\t{}\t{}'.format(count, line, 'unmapped_router'))


