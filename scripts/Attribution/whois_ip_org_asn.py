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

filelist = ['afrinic.db', 'apnic.db', 'ripe.db', 'lacnic.db', 'arin.db']
delimiter = '\t'
replacement_delimiter = ' '
num_fields = 7
row_format = delimiter.join(['%s'] * num_fields)

class WhoisParser(object):

    def __init__(self, unannounced):
        self.unannounced = unannounced

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

                if not self.unannounced.search_best(ip_start):
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

def process_file(filepath, unannounced):
    
    if not os.path.exists(filepath):
        sys.stderr.write('File {} not found.\n'.format(filepath))
        sys.exit(1)

    whois = WhoisParser(unannounced)

    rir = os.path.basename(filepath).split('.')[0] # gets the "afrinic" out of "afrinic.db.gz" or "afrinic.db"
    rir_row_format = rir + delimiter + row_format

    try:
        whois_data = whois.parse(filepath, rir)
        for data in whois_data:
            data_list = [x.replace(delimiter, replacement_delimiter) for x in list(data)] # terrible, but necessary for every delimiter I've tried
            print(rir_row_format % tuple(data_list))

    except Exception as e:
        sys.stderr.write('Error parsing {}. {}\n'.format(filepath, e))
        sys.exit(1)

if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.stderr.write('usage: <rir.db> | <rir.db.gz> | <db-dir>\n')
        sys.exit(1)

    input_path = sys.argv[1]
    unannounced = util.load_squatspace_default()

    if delimiter == replacement_delimiter:
        raise Exception('delimiter and replacement_delimiter must be different.')

    # if os.path.isdir(input_path):
    #     for db_file in filelist:
    #         db_filepath = os.path.join(input_path, db_file)
    #         process_file(db_filepath)
    # else:
    process_file(input_path, unannounced)