import matplotlib
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import numpy as np
import scipy
from datetime import datetime, timedelta
import sys
from collections import defaultdict
import math
from itertools import cycle
from itertools import product
from matplotlib import dates
import datetime
import fileinput
import json

plt.style.use('seaborn-white')

plt.rcParams['axes.grid'] = True
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.linewidth'] = '0.5'
plt.rcParams['grid.color'] = 'grey'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['figure.figsize'] = (10.0, 8.0)
plt.rcParams["axes.edgecolor"] = "0.15"
plt.rcParams["axes.linewidth"]  = 1.25
#plt.rcParams["axes.xmargin"] = 1.0
#plt.rcParams["axes.ymargin"] = 1.0
plt.rcParams['axes.spines.left'] = True
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.bottom'] = True

lines = ["-","--","-.",":"]
markers = ['o', '1', '*', '2', 'D']

def cycler(cols):
    count = 0
    while True:
        yield cols[count]
        count = (count + 1) % len(cols)

linecycler = cycler(lines)
markercycler = cycler(markers)

# route_history = {}
# for line in fileinput.input("../data/ripe_route_history.txt"):
#     route_history[line]
route_history = pd.read_csv('../../data/ripe_squat_history.txt', header=None, sep=" ")
route_history.columns = ['prefix','datetime','announced','origin.3']
matplotlib.rcParams['figure.figsize'] = (18, 8)
print(route_history)
datemin = datetime.date(2001, 1, 1)
datemax = datetime.date(2021, 11, 6)

# cm = plt.cm.get_cmap('RdYlBu')
cm = plt.cm.get_cmap('jet')

prefixes = sorted(route_history['prefix'].unique(), key=lambda x: int(x.split('.')[0]))
# prefixes = ['13.0.0.0/8', '15.0.0.0/8','57.0.0.0/8', '51.0.0.0/8','6.0.0.0/8', '7.0.0.0/8', '9.0.0.0/8', '11.0.0.0/8', '16.0.0.0/8', '19.0.0.0/8', '21.0.0.0/8', '22.0.0.0/8', '25.0.0.0/8', '26.0.0.0/8', '28.0.0.0/8', '29.0.0.0/8', '30.0.0.0/8', '33.0.0.0/8', '43.0.0.0/8', '48.0.0.0/8', '56.0.0.0/8', ]
print(prefixes)
ytick_values = []
ytick_labels = []

for i, prefix in enumerate(prefixes):
    slash8 = route_history[route_history['prefix'] == prefix]

    dates = [pd.to_datetime(d) for d in slash8['datetime']]
    dates = [d.to_pydatetime() for d in dates]
    # dates = pd.to_numeric(pd.to_datetime(slash8['datetime']))
    print(dates)
    ys = [i] * len(dates)
    print(slash8['announced'])
    plt.scatter(dates, ys, s=80, c=slash8['announced'], cmap=cm, vmin=0.0, vmax=1.0)

    ytick_values.append(i)
    ytick_labels.append(prefix)

cbar = plt.colorbar()
cbar.set_label(label='Fraction of Announced IP Space', size=25)
cbar.ax.tick_params(labelsize=30)

plt.tick_params(axis='y', which='major', color='black', labelsize=30)
plt.tick_params(axis='x', which='major', color='black', labelsize=30)
plt.yticks(ytick_values, ytick_labels)
plt.xlim(datemin, datemax)
plt.xticks(rotation=90)
plt.tight_layout()

plt.savefig('../../result/announcement-history.pdf', bbox_inches='tight')
plt.show()