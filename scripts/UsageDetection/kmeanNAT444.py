from sklearn.cluster import KMeans,DBSCAN
import pandas as pd
from sklearn.preprocessing import StandardScaler
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import random
from tqdm import tqdm
import sys
sys.path.append('../../')
import util
sns.set_context("paper", rc={"font.size":16,"axes.titlesize":10,"axes.labelsize":18,"axes.xlabel":18,"axes.ylabel":18})

MISSING_TRIE_VAL = '*'

def trie_search(asn_trie_standard,ip):
    node = asn_trie_standard.search_best(ip)
    if node:
        return node.data['asn']
    else:
        return MISSING_TRIE_VAL

def adding_as_org_level_information(df):
    asn_trie_standard = util.load_ip2asn_default(bdrmapIT=False)
    asn_org = util.load_asn2org_default()
    list_of_as = []
    list_of_org = []
    for t in df['Source Prefix']:
        src_asn = trie_search(asn_trie_standard,t)
        src_org = asn_org.get(src_asn, MISSING_TRIE_VAL)
        list_of_as.append(src_asn)
        list_of_org.append(src_org)
    df['Source AS'] = list_of_as
    df['Source Org'] = list_of_org
    return df

random.seed(11092021)
df = pd.read_csv('../../result/cgnat_statistics.csv',index_col=0)
adding_as_org_level_information(df)
# df = pd.read_csv('result_cgnat_03.csv')
# df = df[df['Median RTT']<100]
df = df[df['Median Ratio']<100]
prefixes_to_keep = []

# print(df_connected_components)
#'# of Nodes when Restricted','# of Edges when Restricted',
df_features = df[['# of Connected Components','Tree Depth','Number of Sinks','Max Distance to the CGNAT candidate','# of Edges','Median hop','25 hop', '75 hop','Number of Prefixes','Median RTT','25 RTT','75 RTT']]
df_rtt = df[['Median RTT','25 RTT','75 RTT','Median hop','25 hop', '75 hop']]
print(df.shape)

# dbscan = DBSCAN(eps=0.6)

kmeans = KMeans(n_clusters=9,random_state=11092021)
scaler = StandardScaler()
# scaled_features = scaler.fit_transform(df_features.values)
scaled_features = df_features.values
print(scaled_features)
kmeans.fit(scaled_features)

from sklearn.metrics import pairwise_distances


def compute_inertia(a, X):
    W = [np.mean(pairwise_distances(X[a == c, :])) for c in np.unique(a)]
    return np.mean(W)

def compute_gap(clustering, data, k_max=5, n_references=5):
    if len(data.shape) == 1:
        data = data.reshape(-1, 1)
    reference = np.random.rand(*data.shape)
    reference_inertia = []
    for k in tqdm(range(1, k_max + 1)):
        local_inertia = []
        for _ in range(n_references):
            clustering.n_clusters = k
            assignments = clustering.fit_predict(reference)
            local_inertia.append(compute_inertia(assignments, reference))
        reference_inertia.append(np.mean(local_inertia))

    ondata_inertia = []
    for k in range(1, k_max + 1):
        clustering.n_clusters = k
        assignments = clustering.fit_predict(data)
        ondata_inertia.append(compute_inertia(assignments, data))

    gap = np.log(reference_inertia) - np.log(ondata_inertia)
    return gap, np.log(reference_inertia), np.log(ondata_inertia)

# X = df_features.values
# k_max = 50
# gap, reference_inertia, ondata_inertia = compute_gap(KMeans(), X, k_max)
#
# plt.plot(range(1, k_max+1), gap, '-o')
# plt.ylabel('gap')
# plt.xlabel('k')
# plt.savefig('figures/gap_statistics.png')

# Final locations of the centroid
print(Counter(kmeans.labels_))
print(kmeans.cluster_centers_)
centroids  = kmeans.cluster_centers_
# centroid_labels = [centroids[i] for i in kmeans.labels_]
# print(centroid_labels)
for i,elem in enumerate(centroids):
    print(i,dict(zip(['# of Connected Components','Tree Depth','Number of Sinks','Max Distance to the CGNAT candidate','# of Edges','Median hop','25 hop', '75 hop','Number of Prefixes',],elem[0:-3])))
    # print(elem[[0,2,-6,-5]])
list_of_cgnat_addresses = {}
# updated_label = {0:'Large CGNAT',1:'Small CPE',2:'Small CPE',3:'Medium CGNAT',4:'Large CPE',5:'Large CGNAT',6:'Large CGNAT',7:'Large CPE',8:'Large CGNAT'}
updated_label = {0:'Small NAT444',1:'Small NAT44',2:'Unknown',3:'Large NAT44',4:'Large NAT',5:'Large NAT444',6:'Large NAT44',7:'Large NAT44',8:'Large NAT444'}

label = []
for i in kmeans.labels_:
    label.append(updated_label[i])
df['Labels'] = label
df.to_csv('../../result/labels_prefixes_nat444.csv')
for s,t in zip(df['Source Prefix'],df['Labels']):
    if 'CGNAT' in t:
        list_of_cgnat_addresses[s] = t
#fig, ax = plt.subplots(figsize=(8, 5))
cdict = {-1:'grey', 0: 'pink' ,1: 'red', 2: 'blue', 3: 'green',4:'yellow',5:'purple',6:'black',7:'gold',8:'purple',9:'black',10:'white',11:'brown',12:'olive',13:'grey',14:'magenta'}
x_scatter = np.array(df['Median Ratio'].values)
y_scatter = np.array(df['Tree Depth'].values)
fig, ax = plt.subplots()
for g in np.unique(kmeans.labels_):
    ix = np.where(kmeans.labels_ == g)
    ax.scatter(x_scatter[ix], y_scatter[ix], c = cdict[g], label = g, s = 1)
ax.legend()
plt.xlabel(xlabel = '# of Connected Components')
plt.ylabel(ylabel = 'Tree depth')
plt.show()
fig, ax = plt.subplots(figsize=(8, 5))
# b = sns.boxplot(y="Median RTT", x="Labels",width=0.3,data=df,ax=ax,)
b = sns.boxplot(y="Median Ratio", x="Labels",width=0.3,data=df,ax=ax,whis=[2.5, 97.5])
ax.set_ylabel('Median Ratio',size=14)
ax.set_xlabel('Inferred configurations', size = 14)
plt.savefig('figures/validation_of_nat444_infer.pdf')
