#!/usr/bin/env python
# coding: utf-8

# In[98]:


import numpy as np
import networkx as nx
import pandas as pd

import matplotlib.pyplot as plt

# Our functions
from read_network import *


# In[236]:


def ImportToDf(path, delimiter = None, header = 0, names = []):
    if names:
        return pd.read_csv(path, delimiter = delimiter, header = header, names = names)
    return pd.read_csv(path, delimiter = delimiter, header = header)

def NodeToIdx(graph_df, nodes):
    node_to_idx = {node: i for i,node in enumerate(nodes)}
    graph_df.SOURCE_SUBREDDIT = graph_df.SOURCE_SUBREDDIT.map(node_to_idx)
    graph_df.TARGET_SUBREDDIT = graph_df.TARGET_SUBREDDIT.map(node_to_idx)
    graph_df.dropna(subset = ['SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT'], axis = 0, how = 'any', inplace = True)

    return graph_df

def ReduceTimeInterval(df, start, end):
    return df[(df.TIMESTAMP >= start) & (df.TIMESTAMP <= end)].reset_index(drop=True)

def WeightedGraph(df):
    df['WEIGHT'] = 1
    df = df.groupby(['SOURCE_SUBREDDIT','TARGET_SUBREDDIT'], as_index = False).sum()
    return df.sort_values(by='WEIGHT', ascending = False)

def NormalizeDf(df):
    norm = lambda x: np.sqrt(np.square(x[1:]).sum())
    norms = df.apply(norm, axis = 1)
    to_remove = norms[norms==0].index.values

    df.drop(to_remove, axis=1, inplace=True)
    df = df.reset_index(drop=True)

    normalize = lambda x: x/np.linalg.norm(x)
    df.iloc[:,1:] = df.iloc[:,1:].apply(normalize, axis = 1)
    return df


# In[100]:


# LOADING OF DATA

## Subreddit embeddings
subreddits = ImportToDf('Data/web-redditEmbeddings-subreddits.csv', header = None, names = ['NODE'] + list(range(1,301)))

## Hyperlinks extracted from post's title
title = ImportToDf('Data/soc-redditHyperlinks-title.tsv', delimiter = '\t')

## Hyperlinks extracted from post's body
body = ImportToDf('Data/soc-redditHyperlinks-body.tsv', delimiter = '\t')


# In[238]:


# Auxiliary dataframe to work with
SR = NormalizeDf(subreddits)
SR


# In[239]:


# Auxiliary dataframe to work with
T = title
T


# In[240]:


# Auxiliary dataframe to work with
B = body
B


# In[241]:


# Union of the two hyperlink networks in one
hyperlinks = pd.concat([title, body])
# Auxiliary dataframe to work with. I am considering only nodes for the moment
HL = hyperlinks
#HL = NodeToIdx(hyperlinks, SR.NODE)
HL


# In[330]:


RTHL = ReduceTimeInterval(HL, '2014', '2014-02')
RTHL


# In[332]:


WHL = WeightedGraph(RTHL)
WHL


# In[333]:


threshold = 0
TWHL = WHL[WHL.WEIGHT > threshold]
TWHL


# In[334]:


TWHL = NodeToIdx(TWHL, SR.NODE)
TWHL


# In[335]:


HLG = nx.from_pandas_edgelist(TWHL, source = 'SOURCE_SUBREDDIT', target = 'TARGET_SUBREDDIT',
                                   edge_attr = list(TWHL.columns.values[2:]),
                                   create_using = nx.DiGraph())
len(HLG.nodes)


# In[336]:


len(HLG.edges)


# In[337]:


nx.number_weakly_connected_components(HLG)


# In[344]:


from networkx.algorithms.community.centrality import girvan_newman
import itertools


comp = girvan_newman(HLG)


# In[345]:


k = 1
comm=[]
for communities in itertools.islice(comp, k):
    comm.append((tuple(sorted(c) for c in communities)))


# In[343]:


len(comm[0])


# In[311]:


for i, community in enumerate(comm[0]):
    for node in community[1:]:
        HLG = nx.contracted_nodes(HLG, community[0], node, self_loops=False)
        print(i, len(HLG.edges()))


# In[302]:


comms_dim = [len(community) for community in comm[0]]


# In[303]:


spring_pos = nx.spring_layout(HLG)
len(spring_pos)


# In[313]:


# Opening the figure
fig = plt.figure(figsize = (15,15))
ax = fig.add_axes([0,0,1,1])
# Drawing the network
nx.draw_networkx_nodes(HLG, spring_pos, node_size = comms_dim)
nx.draw_networkx_edges(HLG, spring_pos, alpha = 0.5)
plt.savefig('Spring_layout.png', dpi=200, bbox_inches = 'tight')


# In[305]:


spectral_pos = nx.spectral_layout(HLG)


# In[126]:


# Opening the figure
fig = plt.figure(figsize = (15,15))
ax = fig.add_axes([0,0,1,1])
# Drawing the network
nx.draw_networkx_nodes(HLG, spectral_pos, node_size = 50)
#nx.draw_networkx_edges(HLG, spectral_pos, alpha = 0.1)


# In[ ]:





# In[ ]:





# In[ ]:





# In[281]:


from sklearn.decomposition import PCA

M = SR.iloc[:,1:].values

pca = PCA(n_components=3)
reduced = pca.fit_transform(M)


# In[283]:


PCA_pos = {float(node): reduced[node,:2] for node in SR.index.values}

# Opening the figure
fig = plt.figure(figsize = (15,15))
ax = fig.add_axes([0,0,1,1])
# Drawing the network
nx.draw_networkx_nodes(HLG, PCA_pos, node_size = 50)
#nx.draw_networkx_edges(HLG, pos, alpha = 0.1)
