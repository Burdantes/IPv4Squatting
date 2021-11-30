#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "usage: <lastdate> <lookbackdays>"
    echo 'For example: ./atlas_tr_collect.sh "Dec 25, 2019" 1'
    exit 1
fi

if ! [ -x "$(command -v ripe-atlas)" ]; then
  echo 'Error: ripe-atlas is not installed.' >&2
  exit 1
fi

lastdate=$1      # "Dec 25 2019"
lookbackdays=$2  # 1
mid=5051
sleeptime=120

for day in $(seq 1 $lookbackdays); do
    for hour in {0..23}; do

        filename=atlas-5051-$(date -u +"%Y%m%d%H0000" -d "$lastdate -$day days -$hour hours").txt.gz

        if [[ -f "$filename" ]]; then
            echo "$filename exists..Skipping"
            continue
        fi

        startdate=$(date -u +"%FT%H:00:00" -d "$lastdate -$day days -$hour hours")
        enddate=$(date -u +"%FT%H:59:59" -d "$lastdate -$day days -$hour hours")

        echo $startdate $enddate $filename

        ripe-atlas report $mid --start-time "$startdate" --stop-time "$enddate" --renderer traceroute_table | gzip > $filename

        sleep $sleeptime
    done
done