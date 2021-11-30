#!/usr/bin/python3
import sys
import fileinput
import traceback
from collections import defaultdict

import unittest
import util
from attribute import find_hops_around, attribute_squatter
import os
import time


squatspace_trie = util.load_squatspace_default()


if __name__ == '__main__':

    ip_set = set()
    ip_occurrence_count = 0
    total_count = 0

    # counts for asn path
    asn_fixed_tr_count = 0
    asn_fixed_ip_occurrence_count = 0
    asn_fixed_ip_set = set()

    # counts for org path
    org_fixed_tr_count = 0
    org_fixed_ip_occurrence_count = 0
    org_fixed_ip_set = set()

    # yes
    better_org_tr_count = 0
    better_org_ip_occurrence_count = 0
    better_org_ip_set = set()

    rir_org_tr_count = 0
    rir_org_ip_occurrence_count = 0
    rir_org_ip_set = set()

    # unattributable = []
    # all_lines = []

    unattributable_fn = 'unattributable_{}.txt'.format(int(time.time()))
    

    print('trace_id|src_asn|squat_ip|squat_index|squat_asn|squat_org|squat_rir|src_ip|squat_index_updated')

    # track the known squatters, keep a map from each prefix to a set of squatters
    squat_asn_set = defaultdict(set)
    squat_org_set = defaultdict(set)
    squat_better_org_set = defaultdict(set)
    squat_rir_set = defaultdict(set)

    for line in fileinput.input():
        try:
            total_count += 1
            line = line.strip()
            # all_lines.append(line)

            src_asn, dst_asn, squat_indexes_str, hop_ips_str, fixed_asn_path_str, fixed_org_path_str, better_org_path_str, rir_org_path_str, src_ip = line.split(
                '\t')

            squat_indexes = [int(i) for i in squat_indexes_str.split('|')]
            hop_ips = [ip for ip in hop_ips_str.split('|')]
            fixed_asn_path = [asn for asn in fixed_asn_path_str.split('|')]
            fixed_org_path = [org for org in fixed_org_path_str.split('|')]
            better_org_path = [org for org in better_org_path_str.split('|')]
            rir_org_path = [org for org in rir_org_path_str.split('|')]

            asn_at_least_one = False
            org_at_least_one = False
            better_org_at_least_one = False
            rir_org_at_least_one = False

            for squat_index in squat_indexes:

                squat_index_updated = 0
                for i in range(squat_index):
                    ip = hop_ips[i]
                    if ip == '*':
                        continue
                    if util.isPublicIPv4Address(ip):
                        squat_index_updated += 1

                ip = hop_ips[squat_index]
                ip_set.add(ip)
                ip_occurrence_count += 1

                squat_asn = fixed_asn_path[squat_index]
                if squat_asn != '*':
                    search = squatspace_trie.search_best(ip)
                    prefix = search.prefix
                    squat_asn_set[prefix].add(squat_asn)
                    asn_fixed_ip_occurrence_count += 1
                    asn_fixed_ip_set.add(ip)
                    if not asn_at_least_one:
                        asn_fixed_tr_count += 1
                        asn_at_least_one = True

                squat_org = fixed_org_path[squat_index]
                if squat_org != '*':
                    search = squatspace_trie.search_best(ip)
                    prefix = search.prefix
                    squat_org_set[prefix].add(squat_org)
                    org_fixed_ip_occurrence_count += 1
                    org_fixed_ip_set.add(ip)
                    if not org_at_least_one:
                        org_fixed_tr_count += 1
                        org_at_least_one = True

                if better_org_path[squat_index] != '*':
                    search = squatspace_trie.search_best(ip)
                    prefix = search.prefix
                    squat_better_org_set[prefix].add(better_org_path[squat_index])
                    better_org_ip_occurrence_count += 1
                    better_org_ip_set.add(ip)
                    if not better_org_at_least_one:
                        better_org_tr_count += 1
                        better_org_at_least_one = True

                squat_rir = rir_org_path[squat_index]
                if squat_rir != '*':
                    search = squatspace_trie.search_best(ip)
                    prefix = search.prefix
                    squat_rir_set[prefix].add(squat_rir)
                    rir_org_ip_occurrence_count += 1
                    rir_org_ip_set.add(ip)
                    if not rir_org_at_least_one:
                        rir_org_tr_count += 1
                        rir_org_at_least_one = True

                print('%d|%s|%s|%s|%s|%s|%s|%s|%s' % (total_count, src_asn,
                                                ip, squat_index, squat_asn, squat_org, squat_rir, src_ip, squat_index_updated))

                #if fixed_asn_path[squat_index] != '*' and better_org_path[squat_index] == '*':
                #    print(line)

            if not asn_at_least_one and not org_at_least_one:
                with open(unattributable_fn, 'a') as fout:
                    fout.write('{}\t{}\n'.format(total_count, line))
        except Exception as e:
            # log and skip malformed lines
            sys.stderr.write('Error parsing line: %s %s\n' %
                             (line, traceback.format_exc()))

    # statistics for second pass, similar to the first pass

    unattributable_second_pass_fn = 'unattributable_second_pass_{}.txt'.format(int(time.time()))
    # counts for asn path
    asn_fixed_tr_count_second_pass = 0
    asn_fixed_ip_occurrence_count_second_pass = 0
    asn_fixed_ip_set_second_pass = set()

    # counts for org path
    org_fixed_tr_count_second_pass = 0
    org_fixed_ip_occurrence_count_second_pass = 0
    org_fixed_ip_set_second_pass = set()

    # yes
    better_org_tr_count_second_pass = 0
    better_org_ip_occurrence_count_second_pass = 0
    better_org_ip_set_second_pass = set()

    rir_org_tr_count_second_pass = 0
    rir_org_ip_occurrence_count_second_pass = 0
    rir_org_ip_set_second_pass = set()



    print('#\n# SECOND PASS\n#')

    total_count_second_pass = 0

    # second pass
    with open(unattributable_fn, 'r') as fin:
        for line in fin:
            try:
                total_count_second_pass += 1
                line = line.strip()

                trace_id, src_asn, dst_asn, squat_indexes_str, hop_ips_str, fixed_asn_path_str, fixed_org_path_str, better_org_path_str, rir_org_path_str, src_ip = line.split(
                    '\t')

                squat_indexes = [int(i) for i in squat_indexes_str.split('|')]
                hop_ips = [ip for ip in hop_ips_str.split('|')]
                fixed_asn_path = [asn for asn in fixed_asn_path_str.split('|')]
                fixed_org_path = [org for org in fixed_org_path_str.split('|')]
                better_org_path = [org for org in better_org_path_str.split('|')]
                rir_org_path = [org for org in rir_org_path_str.split('|')]

                asn_at_least_one = False
                org_at_least_one = False
                better_org_at_least_one = False
                rir_org_at_least_one = False

                for squat_index in squat_indexes:
                    squat_index_updated = 0
                    for i in range(squat_index):
                        ip = hop_ips[i]
                        if ip == '*':
                            continue
                        if util.isPublicIPv4Address(ip):
                            squat_index_updated += 1

                    ip = hop_ips[squat_index]  # a squat ip

                    # look at the closest hop that is not a *
                    # if it is one of the known squatters, then attribute
                    # the ip to it

                    squat_asn = '*'
                    squat_org = '*'
                    squat_rir = '*'

                    # fixed_asn_path
                    before_hop, after_hop = find_hops_around(
                        fixed_asn_path, squat_index)

                    squat_asn, asn_fixed_ip_occurrence_count_second_pass,\
                        asn_fixed_ip_set_second_pass, asn_at_least_one, \
                        asn_fixed_tr_count_second_pass = attribute_squatter(
                            before_hop, after_hop, squat_asn_set,
                            asn_fixed_ip_occurrence_count_second_pass,
                            asn_fixed_ip_set_second_pass, ip, asn_at_least_one,
                            asn_fixed_tr_count_second_pass
                        )

                    # fixed_org_path
                    before_hop, after_hop = find_hops_around(
                        fixed_org_path, squat_index)

                    squat_org, org_fixed_ip_occurrence_count_second_pass,\
                        org_fixed_ip_set_second_pass, org_at_least_one,\
                        org_fixed_tr_count_second_pass = attribute_squatter(
                            before_hop, after_hop, squat_org_set,
                            org_fixed_ip_occurrence_count_second_pass,
                            org_fixed_ip_set_second_pass, ip, org_at_least_one,
                            org_fixed_tr_count_second_pass
                        )

                    # better_org_path

                    # rir_org_path
                    before_hop, after_hop = find_hops_around(
                        rir_org_path, squat_index)

                    squat_rir, rir_org_ip_occurrence_count_second_pass,\
                        rir_org_ip_set_second_pass, rir_org_at_least_one,\
                        rir_org_tr_count_second_pass = attribute_squatter(
                            before_hop, after_hop, squat_rir_set,
                            rir_org_ip_occurrence_count_second_pass,
                            rir_org_ip_set_second_pass, ip, rir_org_at_least_one,
                            rir_org_tr_count_second_pass
                        )

                    print('%s|%s|%s|%s|%s|%s|%s|%s|%s' % (trace_id, src_asn,
                                                    ip, squat_index, squat_asn, squat_org, squat_rir, src_ip, squat_index_updated))

                if not asn_at_least_one and not org_at_least_one:
                    with open(unattributable_second_pass_fn, 'a') as fout:
                        fout.write('{}\n'.format(line))

            except Exception as e:
                # log and skip malformed lines
                sys.stderr.write('Error parsing line: %s %s\n' %
                                (line, traceback.format_exc()))

    # print('# unattributable traceroutes after 1st pass: {}'.format(
    #     len(unattributable)))
    # print('# unattributable traceroutes after 2nd pass: {}'.format(
    #     len(unattributable_second_pass)))

    # after we are all done
    slash24_set = set()
    for ip in ip_set:
        slash24 = ip[:ip.rindex('.')]
        slash24_set.add(slash24)
    ip_count = len(ip_set)
    slash24_count = len(slash24_set)

    #
    # ASN path fix for usage
    #
    asn_fixed_24s = set()
    for ip in asn_fixed_ip_set:
        slash24 = ip[:ip.rindex('.')]
        asn_fixed_24s.add(slash24)
    asn_fixed_24s_count = len(asn_fixed_24s)
    asn_fixed_ip_count = len(asn_fixed_ip_set)

    #
    # ORG path fix for usage
    #
    org_fixed_24s = set()
    for ip in org_fixed_ip_set:
        slash24 = ip[:ip.rindex('.')]
        org_fixed_24s.add(slash24)
    org_fixed_24s_count = len(org_fixed_24s)
    org_fixed_ip_count = len(org_fixed_ip_set)

    #
    # Better ORG
    #
    better_org_24s = set()
    for ip in better_org_ip_set:
        slash24 = ip[:ip.rindex('.')]
        better_org_24s.add(slash24)
    better_org_24s_count = len(better_org_24s)
    better_org_ip_count = len(better_org_ip_set)

    #
    # RIR ORG
    #
    rir_org_24s = set()
    for ip in rir_org_ip_set:
        slash24 = ip[:ip.rindex('.')]
        rir_org_24s.add(slash24)
    rir_org_24s_count = len(rir_org_24s)
    rir_org_ip_count = len(rir_org_ip_set)

    print('# traceroutes: %d distinct-ips: %d distinct-/24s: %d ip_occurrences: %d' %
          (total_count, ip_count, slash24_count, ip_occurrence_count))
    print('# asn_tr_fixed: %d asn_distinct_ip_fixed: %d asn_distinct_24_fixed: %d asn_ip_occurrences_fixed: %d' % (
        asn_fixed_tr_count, asn_fixed_ip_occurrence_count, asn_fixed_ip_count, asn_fixed_24s_count))
    print('# org_tr_fixed: %d org_distinct_ip_fixed: %d org_distinct_24_fixed: %d org_ip_occurrences_fixed: %d' % (
        org_fixed_tr_count, org_fixed_ip_occurrence_count, org_fixed_ip_count, org_fixed_24s_count))
    print('# better_org_tr: %d better_org_distinct_ips: %d better_org_distinct_24s: %d better_org_ip_occurrences: %d' % (
        better_org_tr_count, better_org_ip_occurrence_count, better_org_ip_count, better_org_24s_count))
    print('# with_rir_org:  %d rir_org_distinct_ips: %d rir_org_distinct_24s: %d rir_org_ip_occurrences: %d' % (
        rir_org_tr_count, rir_org_ip_occurrence_count, rir_org_ip_count, rir_org_24s_count))

    asn_fixed_24s = set()
    for ip in asn_fixed_ip_set_second_pass:
        slash24 = ip[:ip.rindex('.')]
        asn_fixed_24s.add(slash24)

    org_fixed_24s = set()
    for ip in org_fixed_ip_set_second_pass:
        slash24 = ip[:ip.rindex('.')]
        org_fixed_24s.add(slash24)

    rir_org_24s = set()
    for ip in rir_org_ip_set_second_pass:
        slash24 = ip[:ip.rindex('.')]
        rir_org_24s.add(slash24)

    print('#', asn_fixed_tr_count_second_pass, asn_fixed_ip_occurrence_count_second_pass, len(
        asn_fixed_ip_set_second_pass), len(asn_fixed_24s))
    print('#', org_fixed_tr_count_second_pass, org_fixed_ip_occurrence_count_second_pass, len(
        org_fixed_ip_set_second_pass), len(org_fixed_24s))
    print('#', rir_org_tr_count_second_pass, rir_org_ip_occurrence_count_second_pass, len(
        rir_org_ip_set_second_pass), len(rir_org_24s))

    # with open('unattributable.txt', 'w') as f:
    #     for line in unattributable:
    #         f.write(line)
    #         f.write('\n')

    # with open('unattributable_second_pass.txt', 'w') as f:
    #     for line in unattributable_second_pass:
    #         f.write(line)
    #         f.write('\n')
