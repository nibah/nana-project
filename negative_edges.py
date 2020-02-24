#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


title = pd.read_csv('data/soc-redditHyperlinks-title.tsv', delimiter = '\t')
body = pd.read_csv('data/soc-redditHyperlinks-body.tsv', delimiter = '\t')

T = title
B = body

hyperlinks = pd.concat([title, body])
HL = hyperlinks

print(T.shape, B.shape, HL.shape)


# In[3]:


# split into negative and positive edges
neg_mask = HL['LINK_SENTIMENT'] == -1
pos_mask = HL['LINK_SENTIMENT'] == 1
NEG = HL[neg_mask]
POS = HL[pos_mask]

# group negative edges by source subreddit, ordered by edge count
neg_sources = NEG[['SOURCE_SUBREDDIT', 'LINK_SENTIMENT']]                .groupby(['SOURCE_SUBREDDIT'], as_index=False)                .sum().sort_values(by=['LINK_SENTIMENT'])
# group negative edges by target subreddit, ordered by edge count
neg_targets = NEG[['TARGET_SUBREDDIT', 'LINK_SENTIMENT']].groupby(['TARGET_SUBREDDIT'], as_index=False).sum().sort_values(by=['LINK_SENTIMENT'])

# just the (descending) order of subreddits by edge count
RANK = 'RANK'
neg_sources[RANK] = np.arange(len(neg_sources))
neg_targets[RANK] = np.arange(len(neg_targets))

# to make more reasonable plots
neg_sources = neg_sources.set_index(RANK)
neg_targets = neg_targets.set_index(RANK)

# rename column indicating negative edges count
NEG_COUNT = 'NEG_COUNT'
neg_sources = neg_sources.rename(columns={'LINK_SENTIMENT': NEG_COUNT})
neg_targets = neg_targets.rename(columns={'LINK_SENTIMENT': NEG_COUNT})

# percentage of negative edges: about 10%
len(NEG) / len(HL)
neg_sources.head()


# In[4]:


# convert negative count to positive, again to make more reasonable plots
neg_sources[NEG_COUNT] = - neg_sources[NEG_COUNT]
neg_targets[NEG_COUNT] = - neg_targets[NEG_COUNT]


# In[5]:


neg_targets.head()


# In[6]:


plt.plot(neg_sources[NEG_COUNT][neg_sources[NEG_COUNT] >= 200])


# In[7]:


plt.plot(neg_targets[NEG_COUNT][neg_targets[NEG_COUNT] >= 200])


# In[8]:


# to plot the incoming negative flow against the outgoing negative flow
sources_and_targets = pd.merge(neg_sources, neg_targets, left_on='SOURCE_SUBREDDIT', right_on='TARGET_SUBREDDIT')


# In[9]:


SOURCE_NEG_COUNT = NEG_COUNT + '_x'
TARGET_NEG_COUNT = NEG_COUNT + '_y'
plt.scatter(sources_and_targets[NEG_COUNT + '_x'], sources_and_targets[NEG_COUNT + '_y'])


# In[10]:


# as we can see, it seems that there is not a correlation between target and source
# in particular, the biggest targets of negative edges are not themselves big sources
# as we check them, we see that many of them are news related, so maybe it makes sense
# that they don't react too much
# it also raises the question about the different roles in this social network
# but those news subreddits are maintained by users anyway, not some news outlet?

# let's see how it looks when we cut the outliers
small_s_and_t = sources_and_targets[(sources_and_targets[SOURCE_NEG_COUNT] <= 2000)
                                    & (sources_and_targets[TARGET_NEG_COUNT] <= 2000)]
plt.scatter(small_s_and_t[SOURCE_NEG_COUNT], small_s_and_t[TARGET_NEG_COUNT])


# In[11]:


# cut some more
small_s_and_t = sources_and_targets[(sources_and_targets[SOURCE_NEG_COUNT] <= 500)
                                    & (sources_and_targets[TARGET_NEG_COUNT] <= 500)]
plt.scatter(small_s_and_t[SOURCE_NEG_COUNT], small_s_and_t[TARGET_NEG_COUNT])


# In[12]:


# It surely looks like big targets are not big sources (and vice-versa)...
# of course, maybe it doesn't mean much to consider this over the (long) arc
# of two years, and maybe we should at shorter time spans.


# In[13]:


# Anyway, now let's check the percentages of negative edges
SOURCE = 'SOURCE_SUBREDDIT'
TARGET = 'TARGET_SUBREDDIT'
all_sources = HL[SOURCE].value_counts()
all_targets = HL[TARGET].value_counts()

perc_neg_sources = neg_sources.set_index(SOURCE)
perc_neg_targets = neg_targets.set_index(TARGET)

# count of all edges
ALL_COUNT = 'all_count'
perc_neg_sources[ALL_COUNT] = all_sources
perc_neg_targets[ALL_COUNT] = all_targets

# percentage of negative edges
PERCENTAGE = 'percentage'
perc_neg_sources[PERCENTAGE] = perc_neg_sources[NEG_COUNT] / perc_neg_sources[ALL_COUNT]
perc_neg_targets[PERCENTAGE] = perc_neg_targets[NEG_COUNT] / perc_neg_targets[ALL_COUNT]

plt.scatter(perc_neg_targets[ALL_COUNT], perc_neg_targets[NEG_COUNT])
# for targets, there seem to be more or less a positive (linear?) correlation between
# total incoming edge count and incoming negative edge count


# In[14]:


# but let's see if it still look linear when we take out the big guys
small_targets = perc_neg_targets[perc_neg_targets[ALL_COUNT] <= 7500]
plt.scatter(small_targets[ALL_COUNT], small_targets[NEG_COUNT])
# it still seems quite linear


# In[15]:


# let's try even smaller ones
small_targets = perc_neg_targets[perc_neg_targets[ALL_COUNT] <= 500]
plt.scatter(small_targets[ALL_COUNT], small_targets[NEG_COUNT])


# In[16]:


# now let's see if the same holds for sources
plt.scatter(perc_neg_sources[ALL_COUNT], perc_neg_sources[NEG_COUNT])


# In[17]:


# ok, cut the big guys
small_sources = perc_neg_sources[perc_neg_sources[ALL_COUNT] <= 500]
plt.scatter(small_sources[ALL_COUNT], small_sources[NEG_COUNT])
# I kinda hoped not to see a similar plot, but it is indeed quite similar to the targets plot...


# In[18]:


# convert NEG and POS to time series
POS_TS = POS.copy()
NEG_TS = NEG.copy()

POS_TS['TIMESTAMP'] = pd.to_datetime(POS_TS['TIMESTAMP'])
POS_TS_COUNTS = POS_TS.groupby(POS_TS['TIMESTAMP'].dt.floor('d')).size()
NEG_TS['TIMESTAMP'] = pd.to_datetime(NEG_TS['TIMESTAMP'])
NEG_TS_COUNTS = NEG_TS.groupby(NEG_TS['TIMESTAMP'].dt.floor('d')).size()

# October and November 2016 (US presidential election was on 8th November)
NEG_TS_COUNTS['2016-10-01' : '2016-11-30'].plot()


# In[19]:


NEG_TS_COUNTS['2016-10-01' : '2016-11-30'].plot()
POS_TS_COUNTS['2016-10-01' : '2016-11-30'].plot()
# there seem to be clear patterns for positive edges, like a decrease in weekends
# maybe less clear in negative edges
# interesting question: are there bursts of negative edges from one subreddit to another
# in a short time span?


# In[20]:


# now let's try to import the negative edge time series data frame into nx
# then export it in gephi format


# In[21]:


mask = (NEG_TS['TIMESTAMP'] >= '2016-10-01') & (NEG_TS['TIMESTAMP'] <= '2016-11-30')
# note: I didn't use NEG_TS because it told me that the attribute type Timestamp is
# not supported... hopefully this still works as time series in gephi
NEG_TSET = NEG.rename(columns={'TIMESTAMP':'timeset'})
# note: it's necessary to tell nx that it is a MultiDiGraph
ELECTION_TS_G = nx.from_pandas_edgelist(NEG_TSET[mask], SOURCE, TARGET, edge_attr=True, create_using=nx.MultiDiGraph)
nx.write_gexf(ELECTION_TS_G, 'ELECTION_TS.gexf')


# In[22]:


# TODO
# the targets don't necessarily know that they're targets
# look for peaks
# use the sources-target thing for embedding
# try the sources-against-targets plot (the interesting one) but for percentages
# and hope that it brings more insight

