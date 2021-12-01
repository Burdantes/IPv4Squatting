# Requirements
## Python
- py-radix
- 
## Others
- [bgpdump](https://github.com/RIPE-NCC/bgpdump)
- [scamper](https://www.caida.org/catalog/software/scamper/)


# Find unannounced IPv4 space
To get unannounced prefixes for each month between `$start_month` and `$end_month` in '$year', run the following
```
./scripts/collect_bgp_dumps_2021.sh $start_month $end_month $year
```
The list of unannounced prefixes for `$month` is stored in `./data/unannounced-2021$month.txt`


For example, `./scripts/collect_bgp_dumps_2021.sh 9 10` will generate two files `unannounced-202109.txt` and `unannounced-202110.txt` in `./data/`

# Get and parse traceroutes from Ark
The Ark traceroutes for each month can be found at https://publicdata.caida.org/datasets/topology/ark/ipv4/prefix-probing/

For example, the traceroutes from 2020/04 can be downloaded from https://publicdata.caida.org/datasets/topology/ark/ipv4/prefix-probing/2020/04/

Do the following to parse the raw file and keep only traceroutes with squat address
- Download the `*.warts.gz` files for a month and store in directory `./data/`
- `mkdir temp` 
- Run `python3 parser.py`

The parsed traceroutes from `./data/*.warts.gz` will be stored in `./temp/*.warts.gz.parsed.squat.full.txt`

Each line in `./temp/*.warts.gz.parsed.squat.full.txt` has the following format
```
src_ip dst_ip -1 squat_ip hop_ips_str squat_idx
```
where `src_ip` is the source IP address of the traceroute, `dst_ip` is the destination IP address of the traceroute, `squat_ip` is the first squat IP address in the traceroute `hop_ips_str` is IP addresses of each hop separated by `,`, and `squat_idx` is the index of the first squat IP address in the traceroute.

# How is RIPE data collected? (@Loqman)

# Squatter attribution 
The attribution takes two stages
- `./scripts/tr_pathfix.py` will take Ark/Microsoft/RIPE traceroutes and apply heuristics to map each hop to an AS
- `./scripts/analyze.py` will take the output of the above and attribute each traceroute to a squatter if it can

## Map hops to ASes
Suppose the traceroutes with squat addresses are in file `$squatspace_full` and the output goes to file `$squatspace_path`

For Ark data run 
```
cat $squatspace_full | python3 ./scripts/tr_pathfix.py -ark > $squatspace_path
```

For Microsoft data run
```
cat $squatspace_full | python3 ./scripts/tr_pathfix.py -msft > $squatspace_path
``` 

For RIPE data run
```
cat $squatspace_full | python3 ./scripts/tr_pathfix.py > $squatspace_path
```

For example, to apply to the parsed Ark traceroute stored in `temp/ams-nl.20200402.1585792800.warts.gz.parsed.squat.full.txt` (see previous section how to parse Ark), we can run
```
squatspace_full=temp/ams-nl.20200402.1585792800.warts.gz.parsed.squat.full.txt
squatspace_path=temp/ams-nl.20200402.1585792800.warts.gz.parsed.squat.path.txt
cat $squatspace_full | python3 ./scripts/tr_pathfix.py -ark > $squatspace_path
```

## Get squatter attribution
Follow these steps to get attribution results
1. Use the desired unannounced IPv4 space. You may want to use the unannounced space for a specific month, to do this, open `scripts/util.py`, modify the `default_file` vairable in function `load_squatspace_default` to be the file name containing the unannounced squat prefixes that you want to use (see previous section for how to generate unannounced squat prefixes). For example, the default file in the code is `data/unannounced-202107.txt`

2. Suppose the traceroutes with hop-AS mapping is in file `$squatspace_path` and result goes to `$squatspace_result`, then run 
```
cat $squatspace_path | python3 analyze.py > $squatspace_result
```

The attribution runs two passes, the second pass attempts to attribute the unattributable traceroutes in the initial pass by some additional heuristics and has less confidence. The results from two passes are separated by
```
#
# SECOND PASS
#
```

Each line of `$squatspace_result` that is not commented (does not start with `#`) has the format
```
trace_id|src_asn|squat_ip|squat_index|squat_asn|squat_org|squat_rir|src_ip|squat_index_updated
```
where `trace_id` is the traceroute ID (index), `src_asn` is the source ASN, `squat_ip` is the first squat address in the traceroute, `squat_index` is the index of the first squat address in the traceroute, `squat_asn` is the ASN of the attributed squatter, `squat_org` and `squat_rir` are organization name of the attributed squatter (based on different data source), `src_ip` is the source IP, and `squat_index_updated`is how many public address hops exist before the first squat address hop

# Router and middlebox
To identify router and middlebox squat address configuration, use `./scripts/router_config.py`. The input to the script is the file `$squatspace_path` containing the mapping between hops and ASes (the output of `./scripts/tr_pathfix.py`). The script usage is
```
python3 ./scripts/router_config.py $squatspace_path
```

The output of the scripts consists of traceroutes that are identified with squat addresses deployed on routers, and at the end of each line a classification is given (`internal_router`, `border_router` or `unmapped_router`)