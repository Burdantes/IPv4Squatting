import json
import sys
import requests
import time

"""
curl -sG https://www.pch.net/api/ixp/directory/active > pch_ix.json
"""
if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.stderr.write('usage: <pch_ix.json> > \n')
        sys.exit(1)

    ix_filename = sys.argv[1]
    with open(ix_filename) as f:
        pch_ix = json.load(f)

    url = 'https://www.pch.net/api/ixp/subnets/'
    for ix in pch_ix:
        id = ix['id']
        resp = requests.get(url + str(id))
        print(resp.text)
        time.sleep(2)
