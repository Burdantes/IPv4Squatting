#!/usr/bin/python3

import sys
sys.path.append('../../')
import numpy as np
import util
import json
from collections import defaultdict
from datetime import datetime, timedelta
from aggregate_prefixes import aggregate_prefixes

base_dir = './'

if __name__ == '__main__':

    frequency_prefixes = defaultdict(lambda : [])
    if len(sys.argv) != 2:
        sys.stderr.write('usage: <route_history.json>\n')
        sys.exit(1)

    route_history_file = sys.argv[1]

    slash8_ipcount = 2.0**24
    datetime_format = '%Y-%m-%dT%H:%M:%S'
    with open('../../data/ripe_squat_history.txt', 'w+') as f:
        print('')
    with open(route_history_file) as f:
        route_histories = json.load(f)

    for route_history in route_histories:
        history_data = route_history['data']
        prefix = history_data['resource']
        timespan_seconds = history_data['time_granularity']  # 1036800 = 12 days
        route_timedelta = timedelta(seconds=timespan_seconds)

        time_dict = defaultdict(set)
        origin_dict = defaultdict(set)

        #max_peers = history_data['latest_max_ff_peers']['v4']

        by_origin = history_data['by_origin']
        for per_origin in by_origin:
            origin_asn = per_origin['origin']
            for prefix_data in per_origin['prefixes']:
                announced_prefix = prefix_data['prefix']
                _, cidr_str = announced_prefix.split('/')
                cidr = int(cidr_str)
                if cidr < 8:
                    continue

                timelines = prefix_data['timelines']
                for interval in timelines:
                    start_time_str = interval['starttime']
                    end_time_str = interval['endtime']

                    start_time = datetime.strptime(start_time_str, datetime_format)
                    end_time = datetime.strptime(end_time_str, datetime_format)

                    point_time = start_time
                    while point_time < end_time:
                        point_time_str = point_time.strftime(datetime_format)
                        time_dict[point_time_str].add(announced_prefix)
                        origin_dict[point_time_str].add(origin_asn)
                        point_time = point_time + route_timedelta

        for point_time_str in sorted(time_dict.keys()):
            prefix_set = time_dict[point_time_str]
            origin_set = origin_dict[point_time_str]

            total_ip_fraction = 0
            # print(prefix_set)
            agg_prefixes = aggregate_prefixes(prefix_set)
            for agg_prefix in agg_prefixes:
                ip, cidr_str = str(agg_prefix).split('/')
                cidr = int(cidr_str)
                ip_count = 2**(32 - cidr)
                ip_fraction = min(1.0, ip_count / slash8_ipcount)

                total_ip_fraction += ip_fraction
            
            origin_as_count = len(origin_set)
            with open('../../data/ripe_squat_history.txt', 'a+') as f:
                # print("trace_id|src_asn|squat_ip|squat_index|squat_asn|squat_org|squat_rir|type", file=f)
                print('%s %s %f %d' % (prefix, point_time_str, total_ip_fraction, origin_as_count),file=f)
            if int(point_time_str.split('-')[0]) <= 2021 and int(point_time_str.split('-')[0]) > 2019:
                frequency_prefixes[prefix].append(total_ip_fraction)
    for prefix in frequency_prefixes.keys():
        print(prefix,np.mean(frequency_prefixes[prefix]))

