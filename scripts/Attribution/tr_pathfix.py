#!/usr/bin/python
import sys
import gzip
import util
import fileinput
import traceback
from aspath_fixer import ASPathSanitizer

if __name__ == '__main__':

    MISSING_TRIE_VAL = "*"
    FIELD_DELIM = "\t"
    LIST_DELIM = "|"
    NUM_FIELDS = 9

    output_format = FIELD_DELIM.join(["%s"]*NUM_FIELDS) 

    asn_trie = util.load_ip2asn_default()
    probe_asn = util.load_probe2asn_default()
    asn_org = util.load_asn2org_default()
    squatspace_trie = util.load_squatspace_default()
    ip_org = util.load_ip2org_default()

    pathfixer = ASPathSanitizer("*")

    def trie_search(ip):
        node = asn_trie.search_best(ip)
        if node:
            return node.data['asn']
        else:
            return MISSING_TRIE_VAL
    
    def ip2org_search(ip):
        node = ip_org.search_best(ip)
        if node:
            return next(iter(node.data['orgs']))
        else:
            return MISSING_TRIE_VAL

    def find_squatspace(hop_ip_list):
        squat_ips = []
        for index, hop_ip in enumerate(hop_ip_list):
            if hop_ip != MISSING_TRIE_VAL and squatspace_trie.search_best(hop_ip):
                squat_ips.append(index)
        return squat_ips

    isMsft = len(sys.argv) == 2 and sys.argv[1] == '-msft'
    isArk = len(sys.argv) == 2 and sys.argv[1] == '-ark'

    for line in fileinput.input("-"):
        line = line.strip()

        try:
            # result.probe_id, datetime, result.source_address, result.destination_address, hop_ips_delimited
            chunks = line.split()

            # RIPE Bad measurement
            if not isMsft and not isArk and chunks[3] == "None":
                continue

            hop_ips = chunks[4]
            hop_ips_list = hop_ips.split(',')

            if isMsft or isArk:
                hop_ips_list = list(map(lambda x: MISSING_TRIE_VAL if x == '' else x, hop_ips_list))  # Oooooo * forces map to evaluate to a list in Python3

            #print(hop_ips_list)

            # only keep records that have squat space
            squat_indexes = find_squatspace(hop_ips_list)
            if not squat_indexes: # if empty list
                continue

            # 2020-04-28 FIXED THIS IN SCOPE
            #if isMsft:  # hack because MSFT uses 25.0.0.0/8 and we don't want to keep reincluding those in the analysis so ignore any hops that are MSFT
            #    first_msft_index = int(chunks[2])
            #    squat_indexes = list(filter(lambda x: x < first_msft_index, squat_indexes))

            hop_ips = LIST_DELIM.join(hop_ips_list)
            squat_indexes_str = LIST_DELIM.join(list(map(str, squat_indexes)))

            if not isMsft and not isArk:
                # source address from traceroute data is almost always private so we get the source ASN
                # from the probe metadata instead
                probe_id = chunks[0]
                src_asn = chunks[2]
                src_ip = chunks[1]
                dst = chunks[5]
                dst_asn = chunks[3]
            elif isArk:
                src = chunks[0]
                src_asn = trie_search(src)
                dst = chunks[1]
                dst_asn = trie_search(dst)
                #print(src, dst, src_asn, dst_asn)
            elif isMsft:
                ##Field:sourceIP endUserASN      hopNum  hopIP   hop_IPs
                src_asn = chunks[1]
                src_ip = chunks[0]
                dst = '204.79.197.200' # doesn't matter
                dst_asn = '8075'

            src_org = asn_org.get(src_asn, MISSING_TRIE_VAL)
            dst_org = asn_org.get(dst_asn, MISSING_TRIE_VAL)

            # map IPs to ASNs
            asn_path = [trie_search(ip) if ip != MISSING_TRIE_VAL else ip for ip in hop_ips_list]

            # map ASNs to Orgs
            org_path = [asn_org.get(asn, MISSING_TRIE_VAL) if asn != MISSING_TRIE_VAL else asn for asn in asn_path]

            fixed_asn_path = pathfixer.fix(src_asn, dst_asn, asn_path, delim=LIST_DELIM)
            fixed_org_path = pathfixer.fix(src_org, dst_org, org_path, delim=LIST_DELIM)

            better_org_path = [asn_org.get(asn, MISSING_TRIE_VAL) if asn != MISSING_TRIE_VAL else asn for asn in fixed_asn_path.split(LIST_DELIM)]
            org_from_fixed_asn = pathfixer.fix(src_org, dst_org, better_org_path, delim=LIST_DELIM)

            with_rir_org = []
            for i, x in enumerate(better_org_path):
                if x == MISSING_TRIE_VAL and hop_ips_list[i] != MISSING_TRIE_VAL and i not in squat_indexes:
                    ip = hop_ips_list[i]
                    org = ip2org_search(ip)
                    with_rir_org.append(org)
                else:
                    with_rir_org.append(x)
            fixed_with_rir_org = pathfixer.fix(src_org, dst_org, with_rir_org, delim=LIST_DELIM)

            print(output_format % (src_asn, dst_asn, squat_indexes_str, hop_ips, fixed_asn_path, fixed_org_path, org_from_fixed_asn, fixed_with_rir_org, src_ip))

        except Exception as e:
            # log and skip malformed lines
            sys.stderr.write('Error parsing line: %s %s\n' % (line, traceback.format_exc()))
