#!/usr/bin/python3
import fileinput
import util

def parse(line):
    """
    Parsing rules
    1. Do nothing if right-most hop is not an as-set
    2. If it is an as-set, and is a single public AS, use that.
    3. If it is multiple ASes or private, use the next AS to the left
    """
    chunks = line.split()

    prefix = chunks[0]
    origin_asn = chunks[-1]

    if origin_asn.startswith('{'):
        if ',' not in origin_asn: # just one ASN in set
            origin_asn = origin_asn[1:-1] # remove the {} example: {71,4445,7430,21302}
            if not util.isPublicASN(int(origin_asn)): # is private
                origin_asn = chunks[-2]
            else: # is public, do nothing
                pass
        else: # multiple ASes in set
            origin_asn = chunks[-2]

    return (prefix, origin_asn)

if __name__ == '__main__':

    for line in fileinput.input():
        line = line.strip()
        (prefix, origin_as) = parse(line)
        print('%s %s' % (prefix, origin_as))