#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "usage: <start-month> <stop-month>"
    echo 'For example: ./collect_bgp_dumps.sh 9 12  - Both months are inclusive.'
    exit 1
fi

if ! [ -x "$(command -v bgpdump)" ]; then
  echo 'Error: bgpdump is not installed.' >&2
  exit 1
fi

start_month=$1
stop_month=$2
year=$3

scriptdir=$(dirname "$0")

for month in $(seq -f "%02g" $start_month $stop_month); do
    for day in 07 14 21 28; do
        for ris_id in $(seq -f "%02g" 00 24); do
            remote_file=bview.$year$month$day.0000.gz
            dump_file=ris$ris_id.$year$month$day.gz
            local_file=ris$ris_id.$year$month$day.txt

            if [[ -f "$local_file.gz" ]]; then
                continue
            fi

            url=https://data.ris.ripe.net/rrc$ris_id/$year.$month/$remote_file
            echo "downloading $url..."
            curl $url -o $dump_file
            echo "done."

            # https://www.webhostingtalk.com/showthread.php?t=1551587

            bgpdump -mq $dump_file | LC_ALL=C grep -Ev ':|/0' | cut -d '|' -f 6,7 --output-delimiter " " | python3 $scriptdir/find_origin.py | LC_ALL=C sort -k1V,1V -k2n,2n | uniq  > $local_file
            
            rm $dump_file
            #cat $merged_file $local_file | LC_ALL=C sort -k1V,1V -k2n,2n | uniq > temp
            #mv temp $merged_file

            gzip $local_file
        done
    done
    gunzip -kc *.gz | LC_ALL=C sort -k1V,1V -k2n,2n | uniq > prefix-asn-2021$month.txt
    ./scripts/unannounced.py prefix-asn-2021$month.txt > data/unannounced-2021$month.txt
done
