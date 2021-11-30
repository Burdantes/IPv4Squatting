#!/bin/bash
curl -sG https://www.pch.net/api/ixp/directory/active > pch_ix.json
python3.5 ./pch.py pch_ix.json > pch_subnets.json
python3.5 ./pch_subnets.py pch_subnets.json > pch_ix_prefixes.txt

curl -sG https://peeringdb.com/api/ixpfx > pdb_ixpfx.json
curl -sG https://peeringdb.com/api/ix > pdb_ix.json
curl -sG https://peeringdb.com/api/ixlan > pdb_ixlan.json
python3.5 ./pdb.py pdb_ix.json pdb_ixlan.json pdb_ixpfx.json > pdb_ix_prefixes.txt

cat pdb_ix_prefixes.txt pch_ix_prefixes.txt | sort -u -t $'\t' -k2,2 | sort > ix_prefixes.txt
