'''
Take the paths after tr_pathfix.py as input,
check all routes with squat IP
if the hops before the squat hop is private or *
'''
import sys
import fileinput
import traceback
from collections import defaultdict

import util

total_count = 0
count_public_ip_before_squat = 0

lines = []

for line in fileinput.input():
    try:
        total_count += 1
        line = line.strip()

        src_asn, dst_asn, squat_indexes_str, hop_ips_str, fixed_asn_path_str, fixed_org_path_str, better_org_path_str, rir_org_path_str = line.split(
            '\t')
        
        squat_indexes = [int(i) for i in squat_indexes_str.split('|')]
        hop_ips = [ip for ip in hop_ips_str.split('|')]

        squat_indexes.sort()
        first_squat_index = squat_indexes[0]

        for i in range(0, first_squat_index):
            ip = hop_ips[i]
            if ip == '*':
                continue
            if util.isPublicIPv4Address(ip):
                # found public IP address before 
                count_public_ip_before_squat += 1
                lines.append(line)
                break
    except Exception as e:
        print(e)

print('# total', total_count)
print('# public IP before first squat hop', count_public_ip_before_squat)

count_diff_public_ip = 0
for line in lines:
    # these traceroutes have public IP before first squat hop
    # check if the public IPs come from the same src asn
    line = line.strip()

    src_asn, dst_asn, squat_indexes_str, hop_ips_str, fixed_asn_path_str, fixed_org_path_str, better_org_path_str, rir_org_path_str = line.split(
        '\t')

    squat_indexes = [int(i) for i in squat_indexes_str.split('|')]
    hop_ips = [ip for ip in hop_ips_str.split('|')]
    fixed_asn_path = [asn for asn in fixed_asn_path_str.split('|')]

    squat_indexes.sort()
    first_squat_index = squat_indexes[0]

    for i in range(0, first_squat_index):
        ip = hop_ips[i]
        if fixed_asn_path[i] != src_asn and fixed_asn_path[i] != '*':
            count_diff_public_ip += 1
            break

# print('# public IP from AS other than src AS before first squat hop', count_public_ip_before_squat)
