# README #

* This document explains the steps required to reproduce the analysis of "Who are the IPv4 Squatters?".

## How to set up? ##

* The scripts were written in Python 3.8.
* The `requirements-py3.txt` file lists the libraries required to run the python scripts with python 3.
* You can create a virtual environment with these requirements as follows:


Create a virtual environment and activate it to run the python 3 scripts:
```bash
$ python3 -m venv ./IPv4Squatting
$ source ./IPv4Squatting-py3/bin/activate
(facilities-mapping-py3)$ pip3 install -r requirements-py3.txt
```

## How to run the scripts ##
## Dependencies

1. [RIPE Atlas tools](https://github.com/RIPE-NCC/ripe-atlas-tools). Follow [this guide](https://ripe-atlas-tools.readthedocs.io/en/latest/installation.html) or
 ```
 $ pip install --user ripe.atlas.tools
 ```
The above command puts binaries in `~/.local/bin` so you may need to add it to your PATH if it doesn't already exist.
 
2. bgpdump. Install the latest bgpdump from http://ris.ripe.net/source/bgpdump/.
Install these dependencies if configure script complains
```
sudo apt install libbz2-dev zlib1g-dev
```

3. scamper. Follow instructions on https://www.caida.org/catalog/software/scamper/

4. py-radix package
```
$ pip install py-radix
```
5. aggregate-prefixes
```
$ pip install aggregate-prefixes
```
6. Copy the traceroute_table.py script to ```~/.config/ripe-atlas-tools/renderers``` so that RIPE Atlas tools can use it to format traceroute results in a delimited format for easier processing.

## Step 1 : Data Collection and Processing

### Find Unannounced IPv4 Space

To get unannounced prefixes for each month between `$start_month` and `$end_month` in '$year', run the following
```
./scripts/collect_bgp_dumps_2021.sh $start_month $end_month $year
```
The list of unannounced prefixes for `$month` is stored in `./data/unannounced-2021$month.txt`


For example, `./scripts/collect_bgp_dumps_2021.sh 9 10` will generate two files `unannounced-202109.txt` and `unannounced-202110.txt` in `./data/`

### Traceroutes (fetching from RIPE's server)

1. Start data collection with the Atlas traceroute data collection script, ```atlas-tr-collect.sh```. For example, the invocation below will fetch all the measurements during Jan 1st. The second argument specifies the ```lookbackdays```; the number of days up to the first parameter to collect data for.
```
$ ./atlas-tr-collect.sh "Jan 1 2020" 1
```
It outputs a gzipped file for each hour of [5051 meausurement id](https://atlas.ripe.net/api/v2/measurements/5051/latest/?format=txt) data. The output format is TAB delimited with these fields:
```probe_id, datetime, source_address, destination_address, hop_ips_delimited```

2. Next we do IP-ASN mapping, identify IXPs, and fix the path to help identify the ASes hosting squat space. This can be done by running the tr_pathfix.py from the scripts directory against one of the 1-hour downloaded traceroute files.
```
$ gunzip -kc *.gz | ../squatspace/scripts/tr_pathfix.py
```
or parallelize with 3 jobs
```
$ gunzip -kc *.gz | parallel -j 3 --pipe --block 100M "../squatspace/scripts/tr_pathfix.py"
```

The output from this command is TAB separated with fields:
```src_asn, dst_asn, hop_ips, fixed_aspath, fixed_orgpath```
where the hop_ips, fixed_aspath, and fixed_orgpath fields are comma delimited and have the same number of entries.

If an IP in hop_ips contains squat space, look up the corresponding index in the fixed_aspath or fixed_orgpath to identify the host AS or Org.

Shows shows /8s where fraction of unannouced space is greater than 0.8.
```
(master) $ awk '{ if($2 > 0.8) print $0 }' bgp-announced-8s.txt
```
slash8  unannouced  
56      0.991943359375  
48      1  
43      0.913436889648438  
33      1  
30      1  
29      0.999755859375  
28      1  
26      1  
25      0.99981689453125  
22      1  
21      1  
19      1  
16      0.99151611328125  
11      1  
9       0.999984741210938  
7       1  
6       0.962203979492188  

### Traceroutes (from RIPE Atlas Big Query)

1. Setup a BigQuery account from ['Google Big Query'.](https://console.cloud.google.com/bigquery)

2. Access the ['RIPE Atlas Big Query'.](https://github.com/RIPE-NCC/ripe-atlas-bigquery)

3. Push the squatted prefix data to BigQuery and call the file `$squatspace`.

4. Run the following query for the date of interest `$startdate` and `$enddate` written as `Y-M-D`:
```WITH
  traceroutes AS (
  SELECT
    msm_id,
    prb_id,
    src_addr,
    dst_addr,
    hops,
    start_time
  FROM
    `ripencc-atlas.measurements.traceroute` AS t
  WHERE
    DATE(start_time) BETWEEN $startdate
    AND $enddate)
SELECT
  msm_id,
  prb_id,
  src_addr,
  dst_addr,
  hops,
  h.hop_addr,
  start_time
FROM
  traceroutes,
  UNNEST(hops) AS h
WHERE
  h.hop_addr IN (
  SELECT
    string_field_1
  FROM
    $squatspace)
  AND (src_addr,
    dst_addr,
    start_time) IN (
  SELECT
    (src_addr,
      dst_addr,
      MAX(start_time))
  FROM
    `ripencc-atlas.measurements.traceroute`
  WHERE
    DATE(start_time) BETWEEN $startdate
    AND $endddate
  GROUP BY
    src_addr,
    dst_addr)
```

### Traceroutes from Ark

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


CAIDA's ITDK can be downloaded [here](https://www.caida.org/catalog/datasets/internet-topology-data-kit/). 


### Generating Auxiliary data

Copies of this data should also ready be checked in to the repo data/ folder so this should only be necessary if they are out of date.

#### Atlas Probe ASNs
This output has some weird characters that we remove with ```tr```.
```
$ ripe-atlas probe-search --all --field id --field asn_v4 | tr -d 'b' | tr -d "'" > probes.txt
```

### IXP Prefixes
The script outputs a file called ix_prefixes.txt. It collects data from Packet Clearing House and PeeringDB.
```
$ ./ix-prefix-collector.sh
```

### IP-AS Mapping
1. Install bgpdump. libbgpdump-1.6.0 works well enough.
2. Download a BGP snapshot from RIPE RIS.
3. Run this command to generate a mapping file from the snapshot.
```
$ bgpdump -m latest-bview.gz | LC_ALL=C grep -Ev ':|/0' | cut -d '|' -f 6,7 --output-delimiter " " | awk '{ print $1,$NF }' | LC_ALL=C sort -k1V,1V -k2n,2n | uniq > ip_asn_raw.txt
```
4. The util.load_ip2asn python function can read this file and return a trie for ASN lookups.

### AS to Org for Sibling detection
CAIDA's [AS-to-Org datasets.](http://data.caida.org/datasets/as-organizations/)

### BGP

The scripts can be found in the BGPdata folder.
1. Downloading BGP dumps from RIS and Routeviews via BGPDownloads.py for specific start_date and end_date
```
$ python3 BGPDownloads.py --start --end --num_of_processors 
```
2. Gathering BGP announcements of the DoD squat space around the 20 January
```
$ python3 BGPannouncements.py
```
3. Crawling historical announcements from RIPE History datasets for a list of prefixes called `$prefixes` and saved in a
csv located in `$outputpath`
```
$ python3 RIPE_history.py --prefixes $prefixes --outputname $outputpath
```
We provide example for each of those scripts inside the associated Python script. 
### Parsing datasets 

#### ITDK (for bdrmapIT analysis)
```
$ python3 parserITDK.py --path_to_ITDK_files
```

## Step 2: Attribution
The scripts can be found in the attribution folder 
### Map hops to ASes
Suppose the traceroutes with squat addresses are in file `$squatspace_full` and the output goes to file `$squatspace_path`

For Ark data run 
```
cat $squatspace_full | python3 ./scripts/Attribution/tr_pathfix.py -ark > $squatspace_path
```

For Microsoft data run
```
cat $squatspace_full | python3 ./scripts/Attribution/tr_pathfix.py -msft > $squatspace_path
``` 

For RIPE data run
```
cat $squatspace_full | python3 ./scripts/Attribution/tr_pathfix.py > $squatspace_path
```

For example, to apply to the parsed Ark traceroute stored in `temp/ams-nl.20200402.1585792800.warts.gz.parsed.squat.full.txt` (see previous section how to parse Ark), we can run
```
squatspace_full=temp/ams-nl.20200402.1585792800.warts.gz.parsed.squat.full.txt
squatspace_path=temp/ams-nl.20200402.1585792800.warts.gz.parsed.squat.path.txt
cat $squatspace_full | python3 ./scripts/Attribution/tr_pathfix.py -ark > $squatspace_path
```

### Get squatter attribution
Follow these steps to get attribution results
1. Use the desired unannounced IPv4 space. You may want to use the unannounced space for a specific month, to do this, open `scripts/Attribution/util.py`, modify the `default_file` vairable in function `load_squatspace_default` to be the file name containing the unannounced squat prefixes that you want to use (see previous section for how to generate unannounced squat prefixes). For example, the default file in the code is `data/unannounced-202107.txt`

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


## Step 3: Detecting usage 
This code can be found in the folder UsageDetection 
### NAT & CGNAT 

#### Compute the statistics 
In order to detect CGNAT, we leverage an algorithm that translates traceroutes into graph and output both a csv and 
a unique graph per /24. Those graphs are used to create Figure 3. 
The algorithm takes as input the raw traceroutes in file `$squatspace_full` and output a csv consisting of the following meta-information about each graph associated to a /24:

````
| 'Source Prefix' | '# of Connected Components' | 'Tree Depth'  | 'Number of Sinks' |  'Max Distance to the CGNAT candidate' | '# of Edges' | 'Median RTT' | '25 RTT' | '75 RTT' | 'Median hop' | '25 hop' |'75 hop'|'25 Ratio' | '75 Ratio' | 'Latency_connected_components' | 'Number of Prefixes' |
````

First, create a `graph` folder in the UsageDetection folder via `mkdir graph` then apply the script 
```
$ python3 nat444.py --path_to_traceroutes $squatspace_full 
```

The result is pushed in `result` and is called the `cgnat_statistics.csv`. 

##### Cluster the statistics to detect CGNAT and NAT

In order to cluster the statistics, we leverage the script kmeanNAT444 which takes as input the `cgnat_statistics.csv`, compute the gap statistics (this process takes a long time) and returns the different clusters. We fixed a random seed to ensure reproducibility of our taxonomy. By the end of the process, we get two figures saved in the folder `figure` (a figure to illustrate the gap statistics evolution and one to quantify the ratio between the first hop and the last hop before reaching a "public" IP address) and a list of prefixes that we have identified as using squat CGNAT addresses. If for any reason, you have changed the name of the previous output, please reflect the change on that script. 

```
python3 kmeanNAT444.py
```

### Routers and middleboxes 
To identify router and middlebox squat address configuration, use `./scripts/router_config.py`. The input to the script is the file `$squatspace_path` containing the mapping between hops and ASes (the output of `./scripts/tr_pathfix.py`). The script usage is
```
python3 ./scripts/router_config.py $squatspace_path
```

The output of the scripts consists of traceroutes that are identified with squat addresses deployed on routers, and at the end of each line a classification is given (`internal_router`, `border_router` or `unmapped_router`)

#### 

## Step 4 Statistics:
We give access to all the scripts that yield the plot in Section 4 of the manuscript and the different statistics that we documented. The scripts in this section can be found in the Statistics folder.

### Squat space evolution

We describe the script to generate the Figure 1 and discusses the evolution of the unannonced squat space.
1. Generate historical announcements of the prefixes of interest (squat prefixes, DoD prefixes or whatever prefixes you want to compare with) from startdate and enddate of interest. Run `get_route_history.sh` and save its output in a file named `$output`. To modify the prefixes selected and the start date and end date, you have to change the variable `routes` and configure the start time and end time of interest next to  `starttime=` and `endtime=`.
```
./get_route_history.sh >> $output 
```
The default `$output` is `../../data/route_history.json`. 
2. Run `route_history.py` on the historical announcement code output to obtain aggregated data within a /8 and save the data in `../../data/ripe_dod_history.txt`
```
 python3 route_history.py $output 
 ```
3 Generate the plot with `visualization_squat_space.py` and is saved in `../../result/announcement-history-dod.pdf`


### Filtering effects 

The script for Figure 5 is called `statisticsfilter.py` and will iterate the same parameters as the one in the manuscript automatically. If you are interested in other statistics, you can also run it for different m and n by changing the list of `ms = [200, 500, 1000, 2500, 5000, 100000, 250 * 10 ** 2, 1000*100, 5 * 10 ** 5]` and `ns = [2, 5, 10, 25, 50, 100, 250, 1000, 5000].`
Then all is needed is to run:
```
python3 statisticsfiltering.py  
```
It will also plot Figure 10 the CDF of the frequency of traceroutes and sources that have observed squat addresses.

### Squatted hop position 

The script for Figure 7 is called `CDFhopposition.py` and will generate the position of the squat addresses for different datasets. 

### Comparing and contrasting Microsoft, Ark and RIPE and Venn Diagramm

In order to compare for each data sources and merged:
* the number of organizations, 
* the number of squat IP address observed
* the number of attributions
* the ratio of attributions
* the number of different squat IP observed
* the number of different squat /24 observed

and comparing the differences between the different data sources, we build the Parser scripts that stitches all the squat information together in a single pandas Dataframe and generate the statistics. It is a process intensive script that returns all the statistics of interest in the command line and will create a temporary version of the file in the temp folder. Make sure to flush it after usage. The script also generates the Venn Diagram in Figure 9.

```
python3 Parser.py
```

### BGP announcements visualisations

To replicate Figure 11 and look at the median visibility and number of illegitimate announcements:
1. Run the script `RIPE_history.py` in the folder BGPCode and save the output at `$output`.
```
python3 RIPE_history.py --outputname $output
```
2 Run the scripts `visual_announcements.py` associated with the earlier output in the folder `BGPanalysis`. 
```
python3 visual_announcements.py --input $output
```
The script will output the two figures as observed in the manuscript in the folder result and called `squat_prefixes_*`. The other scripts in that folder looks at the burstiness of the announcements, the diversity of path for legitimate and illegitimate announcements and have not been inserted in the manuscript because of space constraints. 


## Step 5: Case Study
To replicate the case study, we 

## Contribution guidelines ##

* Writing tests
* Code review
* Bug reporting and bug fixes

## Who do I talk to? ##
* Author: Loqman Salamatian <salamatianloqman@gmail.com>