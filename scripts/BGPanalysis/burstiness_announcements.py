import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import numpy as np
from matplotlib.colors import LogNorm, Normalize
from datetime import date

burstiness_legitimate = []
burstiness_illegitimate = []
df = pd.read_csv('../../data/history_ripe_complete.csv', index_col=0)
def reading_legitimate_actors():
    file = open('../../data/MetaInformation/legitimate_ASes.txt', 'r')
    legitimate_actors = {}
    for row in file.readlines():
        print(row)
        row = row.replace('\n','')
        legitimate_actors[row.split('|')[0]] = row.split('|')[1].split(' ')
    return legitimate_actors
#### reading data from RIPE History
legitimate_actors = reading_legitimate_actors()
DoD_addresses = ['6.0.0.0/8', '7.0.0.0/8', '11.0.0.0/8','9.0.0.0/8','16.0.0.0/8','19.0.0.0/8','21.0.0.0/8','22.0.0.0/8','26.0.0.0/8', '28.0.0.0/8', '29.0.0.0/8', '30.0.0.0/8', '33.0.0.0/8','43.0.0.0/8','48.0.0.0/8','56.0.0.0/8']
Legitimate_Announcers = {'9.0.0.0/8':'IBM','16.0.0.0/8':'Hewlett-Packard','19.0.0.0/8':'Ford','25.0.0.0/8':'UK Ministry of Defence','48.0.0.0/8':'The Prudential Insurance Company of America','56.0.0.0/8':'United States Postal Service.','43.0.0.0/8':'Alibaba'
                         }
all_the_origin_leakage = defaultdict(lambda : [])
DoD_legitimate = ['DoD Network Information Center','Headquarters USAISC','United States Coast Guard','Air Force Systems Networking']

for index in df.index:
    startime,endtime,prefix,origin = df[df.index==index][['Starttime','EndTime','Prefix','Origin']].values[0]
    d0 = date(int(startime.split('-')[0]), int(startime.split('-')[1]), int(startime.split('-')[2].split('T')[0]))
    d1 = date(int(endtime.split('-')[0]), int(endtime.split('-')[1]), int(endtime.split('-')[2].split('T')[0]))
    delta = (d1 - d0).days
    to_drop = True
    prefix = prefix.split('.')[0] + '.0.0.0/8'
    if prefix in Legitimate_Announcers.keys():
        if str(origin) in legitimate_actors[Legitimate_Announcers[prefix]]:
            burstiness_legitimate.append(delta)
        else:
            burstiness_illegitimate.append(delta)
    elif prefix in DoD_addresses:
        for DoD_org in DoD_legitimate:
            if str(origin) in legitimate_actors[DoD_org]:
                burstiness_legitimate.append(delta)
                to_drop = False
                break
        if to_drop:
            burstiness_illegitimate.append(delta)
# No of data points used
N = len(burstiness_illegitimate)
N_prime = len(burstiness_legitimate)

# normal distribution
# data = np.random.randn(N)

# sort the data in ascending order
x = np.sort(burstiness_illegitimate)
x_prime = np.sort(burstiness_legitimate)
# get the cdf values of y
y = np.arange(N) / float(N)
y_prime = np.arange(N_prime)/float(N_prime)
plt.axvline(x=min(burstiness_illegitimate),color= 'red')
# plotting
plt.xlabel('Number of Days that an announcement is up')
plt.ylabel('Fraction of the announcements ')

# plt.title('CDF using ')

plt.plot(x, y,label='Illegitimate')
plt.plot(x_prime,y_prime,label='Legitimate')
plt.legend()
plt.show()
plt.savefig('../../result/BGPdata/burstiness_of_announcements.pdf')
print(N,N_prime)