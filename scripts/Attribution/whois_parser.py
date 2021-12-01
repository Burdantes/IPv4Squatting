#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import sys
import util
import gzip
import time
import logging
import re
import os.path
from netaddr import iprange_to_cidrs
from collections import defaultdict
import math
from typing import Iterator
import traceback

class WhoisParser(object):

    def __init__(self):
        self.parse_dict = {
            'apnic': self.parse_apnic,
            'ripe': self.parse_ripe,
            'arin': self.parse_arin,
            'lacnic': self.parse_lacnic,
            'afrinic': self.parse_afrinic
        }

    def parse_property(self, block: str, name: str):
        match = re.findall(u'^{0:s}:\s*(.*)$'.format(name), block, re.MULTILINE)
        if match:
            if name == 'descr' or name == 'mnt-by' or name == 'notify':  # just get the first line math
                firstline = match[0].strip()
                if name == 'descr' and firstline.startswith('~{') and len(match) > 1:
                    return match[1].strip()
                return firstline
            return " ".join(match).strip()
        else:
            return ''

    def parse_property_inetnum(self, block: str, block_name='inetnum'):

        for line in block.split('\n'):
            if line.startswith(block_name):
                chunks = line.split()

                # inetnum is already a prefix (lacnic)
                # inetnum:     200.60.128/18
                if len(chunks) == 2:
                    prefix = chunks[1]
                    ip_start = prefix.split('/')[0].strip()
                else:
                    # assume inetnum is two IP addresses (ripe)
                    # inetnum:        194.206.161.47 - 194.206.161.47
                    ip_start = chunks[1]
                    ip_end = chunks[3]
                    cidrs = iprange_to_cidrs(ip_start, ip_end)
                    prefix = '{}'.format(cidrs[0]) # Format from IPNetwork to string

                if ':' in prefix:      # if this is IPv6 return error. Seems to happen in LACNIC db
                    return False, None

                is_public = util.isPublicIPv4AddressInt(util.dottedQuadToNum(ip_start))
                return is_public, prefix

    def smart_open(self, filename: str):
        return gzip.open(filename, 'rt', errors='ignore') if filename.endswith('.gz') else open(filename, errors='ignore')

    def read_blocks(self, filename: str, blocknames: set) -> dict:

        blocks = defaultdict(list)

        single_block = []

        def is_requested_block(block_line):
            for block_name in blocknames:
                if block_line.startswith(block_name):
                    return block_name

        with self.smart_open(filename) as f:
            for line in f:
                if line.startswith(' ') or line.startswith('%') or line.startswith('#') or line.startswith('remarks:'):
                    continue
                if line.strip() == '':
                    if single_block:
                        blockname = is_requested_block(single_block[0])
                        if blockname:
                            block_str = ''.join(single_block)
                            blocks[blockname].append(block_str)
                        single_block = []
                else:
                    single_block.append(line)

        if single_block:
            blockname = is_requested_block(single_block[0])
            if blockname:
                block_str = ''.join(single_block)
                blocks[blockname].append(block_str)

        return blocks

    def parse_generic(self, filepath, properties=['netname', 'org', 'org-name', 'notify', 'mnt-by', 'descr'], continue_on_error=True):

        blocks = self.read_blocks(filepath, set(["inetnum"]))

        inet_blocks = blocks['inetnum']

        for inet_block in inet_blocks:
            try:
                block_properties = []

                public, prefix = self.parse_property_inetnum(inet_block)
                if not public or not prefix:
                    continue

                block_properties.append(prefix)

                for prop in properties:
                    prop_val = self.parse_property(inet_block, prop)
                    block_properties.append(prop_val.strip())

                yield tuple(block_properties)
            except Exception as e:
                error_msg = 'Got error parsing line from %s:\n%s\n%s\n' % (filepath, inet_block, traceback.format_exc())
                if continue_on_error:
                    sys.stderr.write(error_msg)
                else:
                    raise Exception(error_msg)

    def parse_afrinic(self, filepath):
        return self.parse_generic(filepath)

    def parse_ripe(self, filepath):
        return self.parse_generic(filepath)

    def parse_apnic(self, filepath):
        return self.parse_generic(filepath)

    def parse_lacnic(self, filepath):
        return self.parse_generic(filepath, properties=['netname', 'ownerid', 'owner', 'owner-c', 'responsible', 'phone'])

    def parse_arin(self, filepath):
        block_names = set(["OrgID", "NetHandle"])

        blocks = self.read_blocks(filepath, block_names)

        org_dict = {}
        org_blocks = blocks['OrgID']

        for org_block_text in org_blocks:
            org_id = self.parse_property(org_block_text, "OrgID")
            org_tech_handle = self.parse_property(org_block_text, "OrgTechHandle")
            org_name = self.parse_property(org_block_text, "OrgName")
            org_dict[org_id] = (org_name, org_tech_handle)

        nethandle_blocks = blocks['NetHandle']
        for nethandle_text in nethandle_blocks:
            public, prefix = self.parse_property_inetnum(nethandle_text, block_name='NetRange')
            if not public:
                continue

            org_id = self.parse_property(nethandle_text, "OrgID")
            net_name = self.parse_property(nethandle_text, "NetName")

            if org_id in org_dict:
                (org_name, org_tech_handle) = org_dict[org_id]
                yield (prefix, net_name, org_id, org_name, "", org_tech_handle, "")

    def parse(self, filename, rir):
        if rir in self.parse_dict:
            return self.parse_dict[rir](filename)
        
        rir_list = ",".join(self.parse_dict.keys())
        raise Exception('Cannot parse RIR database type: "%s". Should be one of %s' % (rir, rir_list))

class WhoisParserTests(unittest.TestCase):

    def test_parse_arin(self):
        this_dir = os.path.dirname(__file__)
        wp = WhoisParser()
        arin_file = os.path.join(this_dir, '../data/test/arin.test.db')

        entries = wp.parse_arin(arin_file)
        entries = list(entries)

        self.assertEqual(1, len(entries))
        (prefix, net_name, org_id, org_name, notify, org_tech_handle, desc) = entries[0]
        self.assertEqual("131.107.0.0/16", prefix)
        self.assertEqual("MICROSOFT", net_name)
        self.assertEqual("MSFT", org_id)
        self.assertEqual("Microsoft Corporation", org_name)
        self.assertEqual("", notify)
        self.assertEqual("MRPD-ARIN", org_tech_handle)
        self.assertEqual("", desc)

    def test_parse_ripe_onlypublic(self):
        this_dir = os.path.dirname(__file__)
        wp = WhoisParser()
        ripe_file = os.path.join(this_dir, '../data/test/ripe.test.db')

        entries = wp.parse_ripe(ripe_file)
        entries = list(entries)

        self.assertEqual(1, len(entries))   # file contains 2 entries but one is 0.0.0.0/0
        (prefix, net_name, org_id, org_name, notify, mntby, descr) = entries[0]
        self.assertEqual("25.0.0.0/8", prefix)
        self.assertEqual("UK-MOD-19850128", net_name)
        self.assertEqual("ORG-DMoD1-RIPE", org_id)
        self.assertEqual("", org_name)
        self.assertEqual("hostmaster@mod.uk", notify)
        self.assertEqual("UK-MOD-MNT", mntby)
        self.assertEqual("", descr)

    def test_parse_lacnic_onlyipv4(self):
        this_dir = os.path.dirname(__file__)
        wp = WhoisParser()
        lacnic_file = os.path.join(this_dir, '../data/test/lacnic.test.db')

        entries = wp.parse_lacnic(lacnic_file)
        entries = list(entries)

        self.assertEqual(1, len(entries)) # 2 entries in file but one is IPv6
        (prefix, net_name, ownerid, owner, owner_c, responsible, phone) = entries[0]
        self.assertEqual("200.60.128/18", prefix)
        self.assertEqual("", net_name)
        self.assertEqual("Telefonica del Peru S.A.A.", owner)
        self.assertEqual("PE-TPSA-LACNIC", ownerid)
        self.assertEqual("Telefonica del Peru", responsible)
        self.assertEqual("+51 1 2109687 []", phone)
        self.assertEqual("JOR", owner_c)

    def test_parse_afrinic(self):
        this_dir = os.path.dirname(__file__)
        wp = WhoisParser()
        afrinic_file = os.path.join(this_dir, '../data/test/afrinic.test.db')

        entries = wp.parse_afrinic(afrinic_file)
        entries = list(entries)

        self.assertEqual(1, len(entries))
        (prefix, net_name, org_id, org_name, notify, mntby, descr) = entries[0]
        self.assertEqual("194.204.192.0/18", prefix)
        self.assertEqual("ONPT", net_name)
        self.assertEqual("ORG-ONdP1-AFRINIC", org_id)
        self.assertEqual("", org_name)
        self.assertEqual("***@iam.net.ma", notify)
        self.assertEqual("AFRINIC-HM-MNT", mntby)
        self.assertEqual("Office National des Postes et Telecommunications", descr)

    def test_parse_apnic(self):
        this_dir = os.path.dirname(__file__)
        wp = WhoisParser()
        apnic_file = os.path.join(this_dir, '../data/test/apnic.test.db')

        entries = wp.parse_apnic(apnic_file)
        entries = list(entries)

        self.assertEqual(1, len(entries))
        (prefix, net_name, org_id, org_name, notify, mntby, descr) = entries[0]
        self.assertEqual("202.12.121.0/24", prefix)
        self.assertEqual("CSIRO-ROCK-2", net_name)
        self.assertEqual("ORG-CSAI1-AP", org_id)
        self.assertEqual("", org_name)
        self.assertEqual("dns.admin@csiro.au", notify)
        self.assertEqual("APNIC-HM", mntby)
        self.assertEqual("CSIRO", descr)

if __name__ == '__main__':
    unittest.main()