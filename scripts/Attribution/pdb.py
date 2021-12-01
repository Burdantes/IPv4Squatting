import sys
import json

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.stderr.write('usage: <pdb_ix.json> <pdb_ixlan.json> <pdb_ixpfx.json>\n')
        sys.exit(1)

    ix_filename = sys.argv[1]
    lan_filename = sys.argv[2]
    pfx_filename = sys.argv[3]

    with open(ix_filename) as ix_file:
        ix_data = json.load(ix_file)['data']

    with open(lan_filename) as lan_file:
        lan_data = json.load(lan_file)['data']

    with open(pfx_filename) as pfx_file:
        pfx_data = json.load(pfx_file)['data']

lan_to_ix = {}
for lan in lan_data:
    lan_to_ix[lan['id']] = lan['ix_id']

ix_to_name = {}
for ix in ix_data:
    ix_to_name[ix['id']] = ix['name']

for pfx in pfx_data:
    if pfx['protocol'] == 'IPv6' or pfx['status'] != 'ok':
        continue

    prefix = pfx['prefix']

    ixlan_id = pfx['ixlan_id']

    if ixlan_id not in lan_to_ix:
        sys.stderr.write('Missing ixlan_id: %s\n' % ixlan_id)
        continue

    ix_id = lan_to_ix[ixlan_id]
    ix_name = ix_to_name[ix_id]

    row = '%s\t%s' % (ix_name, prefix)
    print(row)