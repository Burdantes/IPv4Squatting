#!/bin/bash

# API https://stat.ripe.net/docs/data_api#routing-history
# Squat Addresses
routes=(6 7 9 11 16 19 21 22 25 26 28 29 30 33 43 48 56);

#Dod addresses
#routes=(6 7 11 21 22 26 28 29 30 33);
echo "["; # make all the outputs a JSON list
for route in "${routes[@]}"; do
    #endtime=2020-04-05T00:00:00&
    curl "https://stat.ripe.net/data/routing-history/data.json?min_peers=0&normalise_visibility=tre&resource=$route.0.0.0/8&starttime=2001-02-23T00:00:00";
    #curl "https://stat.ripe.net/data/routing-history/data.json?min_peers=0&normalise_visibility=true&resource=$route.0.0.0/8&starttime=2020-01-01T00:00:00";
    echo ",";
    sleep 5;
done
echo "]";  # start of JSON list