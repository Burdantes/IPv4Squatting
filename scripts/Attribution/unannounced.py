#!/usr/bin/python3
import sys
import fileinput
import util
import os
from aggregate_prefixes import aggregate_prefixes

if sys.version_info[0] >= 3:
    unicode = str

if __name__ == "__main__":

    if len(sys.argv) > 2:
        sys.stderr.write('usage: unannounced.py [ip2asn-file]')
        sys.exit(1)

    if len(sys.argv) == 2:
        this_dir = os.path.dirname(__file__)
        default_ixprefixes_file = os.path.join(this_dir, "../data/ix_prefixes.txt")
        announced_trie = util.load_ip2asn(sys.argv[1], default_ixprefixes_file)
    else:
        # use the ip_asn_raw.txt from repo
        announced_trie = util.load_ip2asn_default()

    unannounced_list = []

    for slash24 in range(0, util.dottedQuadToNum("255.255.255.0"), 256):
        if not util.isPublicIPv4AddressInt(slash24):
            continue

        slash24_str = util.numToDottedQuad(slash24)
        if not announced_trie.search_best(slash24_str):
            unannounced_list.append(unicode(slash24_str+"/24"))

    for aggregated_prefix in aggregate_prefixes(unannounced_list):
        print(aggregated_prefix)