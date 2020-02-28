import numpy as np
import networkx as nx
import pandas as pd

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt

import pickle

def ImportToDf(path, delimiter = None, header = 0, names = []):
    if names:
        return pd.read_csv(path, delimiter = delimiter, header = header, names = names)
    return pd.read_csv(path, delimiter = delimiter, header = header)

def NormalizeDf(df):
    norm = lambda x: np.sqrt(np.square(x[1:]).sum())
    norms = df.apply(norm, axis = 1)
    to_remove = norms[norms==0].index.values

    df.drop(to_remove, axis=0, inplace=True)
    df = df.reset_index(drop=True)

    normalize = lambda x: x/np.linalg.norm(x)
    df.iloc[:,1:] = df.iloc[:,1:].apply(normalize, axis = 1)
    return df

def WeightedGraph(df, threshold = 0):
    df['WEIGHT'] = 1
    df = df.groupby(['SOURCE_SUBREDDIT','TARGET_SUBREDDIT'], as_index = False).sum()
    df = df.sort_values(by='WEIGHT', ascending = False)
    df = df[df.WEIGHT > threshold]
    return df

def OnlyEmbeddedNodes(df, EMB):
    return df[(df.SOURCE_SUBREDDIT.isin(EMB.NODE.values)) & (df.TARGET_SUBREDDIT.isin(EMB.NODE.values))].reset_index(drop=True)

def ReduceTimeInterval(df, start, end):
    return df[(df.TIMESTAMP >= start) & (df.TIMESTAMP <= end)].reset_index(drop=True)

def IncomingNegativeEdges(df):
    df_aux = df
    df = df.groupby('TARGET_SUBREDDIT').sum()
    in_neg = (df.WEIGHT-df.LINK_SENTIMENT)/2
    for node in set(df_aux.SOURCE_SUBREDDIT).union(set(df_aux.TARGET_SUBREDDIT)):
        if node not in in_neg.index.values:
            in_neg = in_neg.append(pd.Series([0],index = [node]))
    return in_neg

def OutgoingNegativeEdges(df):
    df_aux = df
    df = df.groupby('SOURCE_SUBREDDIT').sum()
    out_neg = (df.WEIGHT-df.LINK_SENTIMENT)/2
    for node in set(df_aux.SOURCE_SUBREDDIT).union(set(df_aux.TARGET_SUBREDDIT)):
        if node not in out_neg.index.values:
            out_neg = out_neg.append(pd.Series([0],index = [node]))
    return out_neg

def Embedding2D(G, EMB, name, pos_file = ''):
    # If we have already available positions
    if pos_file:
        with open(pos_file, 'rb') as f:
            pos = pickle.load(f)
        return pos
    # Filtering nodes present in our graph
    EMB = EMB[EMB.NODE.isin(G.nodes())].reset_index(drop=True)
    # Extracting features
    X = EMB.iloc[:,1:].values

    # PCA to reduce dimension from 300 to 50
    pca = PCA(n_components=50, svd_solver = 'auto')
    reduced_X = pca.fit_transform(X)

    # TSNE to reduce dimension from 50 to 2
    Y = TSNE(n_components=2).fit_transform(reduced_X)

    # Construction of a dictionary: key = node : value = coordinates
    pos = {EMB.NODE[idx] : Y[idx,:] for idx in EMB.NODE.index.values}

    # Saving into a pickle
    f = open("Positions_{}.pkl".format(name),"wb")
    pickle.dump(pos,f)
    f.close()

    return pos

def PlotSubNetwork(HL, SR, start = '2013-12-31', end = '2017-05-01', threshold = 0, pos_file = ''):

    # Filtering edges in the time interval [start, end]
    HL = ReduceTimeInterval(HL, start, end)
    # From Multigraph to Directed Weighted graph
    HL = WeightedGraph(HL, threshold)
    # Normalize weight value by maximum value
    HL.WEIGHT = HL.WEIGHT/HL.WEIGHT.max()

    # Identify negative edges
    negative_edges = HL[HL.LINK_SENTIMENT <0][['SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT']].to_numpy()
    negative_edges = [tuple(e) for e in negative_edges]
    # Width of edges = weigth of edges
    negative_widths = [w for w in HL[HL.LINK_SENTIMENT <0].WEIGHT]

    # Identify positive edges
    positive_edges = HL[HL.LINK_SENTIMENT >=0][['SOURCE_SUBREDDIT', 'TARGET_SUBREDDIT']].to_numpy()
    positive_edges = [tuple(e) for e in positive_edges]
    # Width of edges = weigth of edges
    positive_widths = [w for w in HL[HL.LINK_SENTIMENT >=0].WEIGHT]

    # Genartion od the Graph
    G = nx.from_pandas_edgelist(HL, source = 'SOURCE_SUBREDDIT', target = 'TARGET_SUBREDDIT',
                                edge_attr = list(HL.columns.values[2:]),
                                create_using = nx.DiGraph())

    print('Nodes : {}, Weighted edges: {} '.format(len(G.nodes), len(G.edges)))

    # Size of nodes = amount of interactions of nodes: indegree+outdegree
    interactions = [deg[1]*10 for deg in G.degree(weight='WEIGHT')]

    # 2D Embedding
    pos = Embedding2D(G, SR, start+'_'+end, pos_file)

    fig = plt.figure(figsize = (15,15))
    ax = fig.add_axes([0,0,1,1])
    nx.draw_networkx_nodes(G, pos, node_size = interactions)
    nx.draw_networkx_edges(G, pos, edgelist = negative_edges, edge_color='red',
                           width = negative_widths, alpha = 1)
    nx.draw_networkx_edges(G, pos, edgelist = positive_edges, edge_color='black',
                           width = positive_widths, alpha = 0.4)

    plt.savefig('Subreddit_interactions_{}_{}.png'.format(start,end), dpi=300, bbox_inches = 'tight')

    return HL, G
