import sys
import json

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('usage: <pch_subnets.json>\n')
        sys.exit(1)

    """
    pch_ix_filename = sys.argv[1]
    with open(pch_ix_filename) as f:
        pch_ix = json.load(f)

    ix_name = {}
    for ix in pch_ix:
        id = ix['id']
        name = ix['name']
        ix_name[id] = name
    """

    pch_subnets_filename = sys.argv[1]

    with open(pch_subnets_filename) as f:
        for line in f:
            line = line.strip()
            pch_subnets = json.loads(line)

            for subnet in pch_subnets:
                if 'error' in subnet or ('status' in subnet and subnet['status'].lower() != 'active') or subnet['version'].lower() != 'ipv4':
                    continue

                name = subnet['short_name'].strip()
                name = name.rstrip('-v4')
                name = name.rstrip('-')
                name = name.rstrip(' IP')

                prefix = subnet['subnet']

                if not name or not prefix:
                    continue

                prefix = prefix.strip()

                out = u'%s\t%s' % (name, prefix)
                print(out)