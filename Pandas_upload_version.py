#!/usr/bin/env python
# coding: utf-8

# In[38]:


import numpy as np
import networkx as nx
import pandas as pd

import matplotlib.pyplot as plt

# Our functions
from read_network import *


# In[ ]:


def ReduceTimeInterval(df, start, end):
    return df[(df.TIMESTAMP >= start) & (df.TIMESTAMP <= end)]


# In[2]:


# LOADING OF DATA

## Subreddit embeddings
subreddits = pd.read_csv('Data/web-redditEmbeddings-subreddits.csv', header = None) 

## Hyperlinks extracted from post's title 
title = pd.read_csv('Data/soc-redditHyperlinks-title.tsv', delimiter = '\t')

## Hyperlinks extracted from post's body 
body = pd.read_csv('Data/soc-redditHyperlinks-body.tsv', delimiter = '\t')


# In[3]:


# Auxiliary dataframe to work with
SR = subreddits

# Move first column with user IDs to index column
# SR.index = subreddits[0].values
# SR.index.name = 'USER_ID'
# SR.drop(0, axis=1, inplace = True)

print(SR.shape)
SR.head()


# In[4]:


# Auxiliary dataframe to work with
T = title

print(T.shape)
title.head()


# In[5]:


# Auxiliary dataframe to work with
B = body

print(body.shape)
body.head()


# In[6]:


# Union of the two hyperlink networks in one
hyperlinks = pd.concat([title, body])
# Auxiliary dataframe to work with. I am considering only nodes for the moment
HL = hyperlinks

print(HL.shape)
HL.head()


# In[7]:


node_to_idx = {node: i for i,node in enumerate(SR[0])}
HL.SOURCE_SUBREDDIT = HL.SOURCE_SUBREDDIT.map(node_to_idx)
HL.TARGET_SUBREDDIT = HL.TARGET_SUBREDDIT.map(node_to_idx)
HL.head()


# In[12]:


HL.dropna(subset = ['SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT'], axis=0, how='any', inplace=True)
HL


# In[94]:


HL_RT = ReduceTimeInterval(HL, '2014-01-01', '2014-12-31')
HL_RT


# In[ ]:





# In[63]:


HL_30 = HL.iloc[range(100000),:].reset_index(drop=True)


# In[64]:


HL_30


# In[65]:


HLG = nx.from_pandas_edgelist(HL_30, source = HL.columns.values[0], target = HL.columns.values[1],
                              edge_attr = list(HL.columns.values[2:]),
                             create_using = nx.MultiDiGraph())

