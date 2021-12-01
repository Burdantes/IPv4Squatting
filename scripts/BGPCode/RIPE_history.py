import urllib.request, json
import pandas as pd
import sys
sys.path.append('../../')
from util import load_squatspace_default,load_squat_prefix
import os
from collections import defaultdict
import argparse
import time
from tqdm import tqdm
def crawling_RIPE_history(list_of_prefixes,output_file):
    percentage_announced = defaultdict(lambda : 0)
    list_of_prefixes_seen = []
    for t in tqdm(list_of_prefixes):
        time.sleep(1)
        with urllib.request.urlopen("https://stat.ripe.net/data/routing-history/data.json?resource="+str(t)+"&min_peers=1&normalise_visibility=true&starttime=2001-01-01T00:00:00&endtime=2022-01-01T00:00:00") as url:
            data = json.loads(url.read().decode())
            # print(data)
            # if t.startswith('16'):
            #     print('Test')
            for te in data['data']['by_origin']:
                for s in te['prefixes']:
                    print(te['origin'])
                    for n in s['timelines']:
                        year_start = int(n['starttime'].split('-')[0])
                        year_end = int(n['endtime'].split('-')[0])
                        month_start = int(n['starttime'].split('-')[1])
                        month_end = int(n['endtime'].split('-')[1])
                        day_start = int(n['starttime'].split('-')[2].split('T')[0])
                        day_end = int(n['endtime'].split('-')[2].split('T')[0])
                        # for year in range(year_start,year_end):
                        year = 2021
                        print(year)
                        print(2 ** (32 - int(s['prefix'].split('/')[1])))
                        if s['prefix'].split('.')[0] != t.split('.')[0]:
                            continue
                        # elif n['full_peers_seeing'] < 50:
                        #     continue
                        if year == year_start:
                            if year_start == year_end:
                                month_diff = month_end - month_start
                            else:
                                month_diff = 12 - month_start
                        elif year == year_end:
                            month_diff = month_end
                        else :
                            month_diff = 12
                        # month_diff = (year_end - year_start)*12 + month_end - month_start
                        day_diff =abs(day_end - day_start)
                        # percentage_announced[(year, s['prefix'].split('.')[0])] += (2 ** (32 - int(s['prefix'].split('/')[1])))*day_diff + (2 ** (32 - int(s['prefix'].split('/')[1])))*30*month_diff
                        percentage_announced[(year,s['prefix'].split('.')[0])] += (2 ** (32 - int(s['prefix'].split('/')[1])))
                        list_of_prefixes_seen.append((s['prefix'],te['origin'],n['starttime'],n['endtime'],n['full_peers_seeing'],n['visibility']))
        # print(t)
        # print(list_of_prefixes_seen)
        # print(percentage_announced)
    df = pd.DataFrame(list_of_prefixes_seen,columns=['Prefix','Origin','Starttime','EndTime','FullPeersSeeing','Visibility'])
    df.to_csv(output_file)
    print(df)
    return percentage_announced


if __name__ == "__main__":
    # setup flags
    list_of_prefixes = load_squat_prefix()
    # list_of_prefixes = ['6.0.0.0/8','7.0.0.0/8','11.0.0.0/8','22.0.0.0/8','26.0.0.0/8','28.0.0.0/8','29.0.0.0/8','30.0.0.0/8',
    #                     '33.0.0.0/8','55.0.0.0/8','205.0.0.0/8','214.0.0.0/8','215.0.0.0/8']
    parser = argparse.ArgumentParser(description="A script to crawl RIPE History API")
    parser.add_argument("--prefixes", action="store", default=list_of_prefixes, required=False,
                        help="The prefixes that you want to crawl.")
    parser.add_argument("--outputname", action="store", default="../../data/history_ripe_complete.csv", required=False,
                        help="The output file.")

    args = parser.parse_args()

    output_file = args.outputname
    list_of_prefixes = args.prefixes
    percentage_announced = crawling_RIPE_history(list_of_prefixes,output_file)