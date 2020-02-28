import numpy as np
import networkx as nx
import pandas as pd
from read_network import merge_edges

def ImportToDf(path, delimiter = None, header = 0, names = []):
	if names:
		return pd.read_csv(path, delimiter = delimiter, header = header, names = names)
	return pd.read_csv(path, delimiter = delimiter, header = header)

def ReduceTimeInterval(df, start, end):
	return df[(df.TIMESTAMP >= start) & (df.TIMESTAMP <= end)].reset_index(drop=True)

def split_by_month(hyperlinks, weighted=True, undirected=False, threshold=1/3):
	"""
	Splits the data defined by hyperlinks into subsets of data, each representing one month.

	INPUT:
	- ``hyperlinks`` -- Dataframe containing edge data.
	- ``weighted`` -- If set to true, multi-edges will be merged into single ones.
	- ``undirected`` -- If set to true, directed edges will be converted to undirected ones.
	- ``threshold`` -- A real number from 0 to 1, used to calculate edge sign
	if the output graph is undirected. A higher threshold will delete edges
	that have ambiguous sentiment. For example, a threshold of 1/3 means that
	an edge (u,v) in the output undirected graph will exist and have a sign
	only if more than 2/3 of the edges (u,v) or (v,u) in the original directed
	multigraph were of that same sign.

	OUTPUT:
	- ``monthly_graphs`` -- A list containing the graphs each representing one month.
	"""
	monthly_links = []
	for year in ['2014', '2015', '2016']:
		for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
			monthly_links.append(ReduceTimeInterval(hyperlinks, year + '-' + month + '-01', year + '-' + month + '-31'))
	for month in ['01', '02', '03', '04']:	# months in 2017 that we have data for
		monthly_links.append(ReduceTimeInterval(hyperlinks, '2017-' + month + '-01', '2017-' + month + '-31'))

	monthly_graphs = []
	for links in monthly_links:
		monthly_graphs.append(nx.from_pandas_edgelist(links, source='SOURCE_SUBREDDIT', target='TARGET_SUBREDDIT',
														edge_attr='LINK_SENTIMENT', create_using=nx.MultiDiGraph))

	if (weighted):
		weighted_monthly_graphs = []
		for graph in monthly_graphs:
			weighted_monthly_graphs.append(merge_edges(graph, undirected, threshold))
			graph.clear()
		return weighted_monthly_graphs

	return monthly_graphs

def main():
	title = ImportToDf('data/soc-redditHyperlinks-title.tsv', delimiter = '\t')
	body = ImportToDf('data/soc-redditHyperlinks-body.tsv', delimiter = '\t')
	hyperlinks = pd.concat([title, body])

	wmg = split_by_month(hyperlinks)
	i = 0
	for graph in wmg:
		nx.write_gml(graph, "data/subgraph-" + str(i) + ".gml")
		i += 1

if __name__ == "__main__":
	main()
