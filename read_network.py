import networkx as nx
import csv

def read_tsv(path, read_attr=False):
	"""
	Read graph edgelist, edge attributes and edge properties from a .tsv file.

	INPUT:
	- ``path`` -- The location of the .tsv file.
	- ``read_attr`` -- True if attributes should be read. Otherwise the edges will be read without any labels.

	OUTPUT:
	- ``graph`` -- The NetworkX object containing the read graph.
	"""
	# Using ideas from https://medium.com/@adds68/parsing-tsv-file-with-csv-in-python-662d6347b0cd
	graph = nx.MultiDiGraph()
	with open(path) as tsvfile:
		reader = csv.DictReader(tsvfile, dialect='excel-tab')
		for row in reader:
			if (read_attr):
				graph.add_edge(row['SOURCE_SUBREDDIT'], row['TARGET_SUBREDDIT'], post_id = row['POST_ID'], \
						timestamp = row['TIMESTAMP'], link_sentiment = row['LINK_SENTIMENT'], properties = row['PROPERTIES'])
			else:
				graph.add_edge(row['SOURCE_SUBREDDIT'], row['TARGET_SUBREDDIT'])
	return graph

def merge_edges(graph):
	"""
	Merge multi edges into single weighted edges.

	INPUT:
	- ``graph`` -- A NetworkX MultiDiGraph.

	OUTPUT:
	- ``graph`` -- A NetworkX DiGraph where each edge has a new attribute 'weight'.
	"""
	# Using ideas from https://stackoverflow.com/questions/15590812/networkx-convert-multigraph-into-simple-graph-with-weighted-edges
	weighted_graph = nx.DiGraph()
	for u,v in graph.edges():
		if weighted_graph.has_edge(u,v):
			weighted_graph[u][v]['weight'] += 1
			weighted_graph[u][v]['sentiment'] += int(graph[u][v][0]['link_sentiment'])
		else:
			weighted_graph.add_edge(u, v, weight=1, sentiment=int(graph[u][v][0]['link_sentiment']))
	return weighted_graph