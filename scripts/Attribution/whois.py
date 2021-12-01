#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from whois_parser import WhoisParser

filelist = ['afrinic.db', 'apnic.db', 'ripe.db', 'lacnic.db', 'arin.db']
delimiter = '\t'
replacement_delimiter = ' '
num_fields = 7
row_format = delimiter.join(['%s'] * num_fields)

def process_file(filepath):

    if not os.path.exists(filepath):
        sys.stderr.write('File {} not found.\n'.format(filepath))
        sys.exit(1)

    whois = WhoisParser()

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

    if delimiter == replacement_delimiter:
        raise Exception('delimiter and replacement_delimiter must be different.')

    if os.path.isdir(input_path):
        for db_file in filelist:
            db_filepath = os.path.join(input_path, db_file)
            process_file(db_filepath)
    else:
        process_file(input_path)
