import json
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from collections import Counter
import math
import datetime
def roundup(x):
    return int(math.floor(x / 10.0)) * 10
def announcement_analysis():
    dic_time = []
    with open('/Users/geode/PycharmProjects/DoD_Squatting/data/BGP/output_ribs.json') as f:
      data = json.load(f)
    announcement_per_times = []
    for t in tqdm(data.keys()):
        prefix = t.split('|')[0]
        overall_prefix = prefix.split('.')[0]+'.0.0.0/8'
        # print(overall_prefix)
        slash_length = prefix.split('/')[1]
        for s in data[t]:
            path = s.split('|')[-1].split(' ')
            times = s.split('|')[0]
            print(times)
            timestamp = datetime.datetime.fromtimestamp(int(times.split('.')[0]))
            print(timestamp)

            date = timestamp.strftime('%Y-%m-%d')
            announcement_per_times.append(date)
            # print(times,path,overall_prefix)
            # if str(path[-1]) == '8003':
            dic_time.append([overall_prefix,roundup(int(times.split('.')[0])),len(path),path[-1],slash_length])
            # break
        # break
    dic_time = pd.DataFrame(dic_time,columns = ['/8','time','Length of the observed path','ASes announcing the address','/x'])
    timeseries = []
    for t in tqdm(dic_time.groupby(['time','/8'])):
        diversity = len(t[1]['ASes announcing the address'].value_counts().index)
        average = np.mean(t[1]['Length of the observed path'].values)
        timeseries.append([average,diversity,t[0][0],t[0][1]])
    df = pd.DataFrame(timeseries,columns=['Average Path Length','Number of unique ASes announcing a prefix in this /8','Timestamp','/8'])
    df['Date'] = df.Timestamp.apply(lambda x: pd.datetime.fromtimestamp(x).date())
    df['Date'] = df['Timestamp'].dt.date
    return df
#########
if __name__ == "__main__":
    # print(df)
    df = announcement_analysis()
    # df = pd.read_csv('ribs_results.csv',index_col = 0)
    df = df[df['/8'].isin(['6.0.0.0/8', '7.0.0.0/8', '11.0.0.0/8', '21.0.0.0/8', '22.0.0.0/8', '26.0.0.0/8', '28.0.0.0/8', '29.0.0.0/8','30.0.0.0/8', '33.0.0.0/8',])]
    fig, ax = plt.subplots(figsize=(11, 7))
    b = sns.lineplot(data=df, x="Date", y="Average Path Length",hue = '/8')
    # title =
    # plt.title(title,)
    # b.axes.set_title(title,fontsize=17)
    b.set_xlabel("Date",fontsize=26)
    b.set_ylabel("Average Path Length",fontsize=26)
    print(df['Date'].value_counts())
    b.axvline(21)
    b.tick_params(labelsize=20,rotation=75)
    ax.set_xticks(ax.get_xticks()[::6])
    plt.show()
    # plt.savefig('ribs_shortest_path_distribution.svg')
    # plt.savefig('ribs-analysis_countAS_restricted.png')
    # print(Counter(announcement_per_times))
