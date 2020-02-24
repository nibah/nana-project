import networkx as nx
import csv

def read_tsv(paths, read_attr=False):
	"""
	Read graph edgelist, edge attributes and edge properties from .tsv files.

	INPUT:
	- ``paths`` -- A list of strings with the locations of the .tsv files.
	- ``read_attr`` -- True if attributes should be read. Otherwise the edges will be read without any labels.

	OUTPUT:
	- ``graph`` -- The NetworkX object containing the read graph.
	"""
	# Using ideas from https://medium.com/@adds68/parsing-tsv-file-with-csv-in-python-662d6347b0cd
	graph = nx.MultiDiGraph()
	if isinstance(paths, str):
		paths = [paths]
	for path in paths:
		with open(path) as tsvfile:
			reader = csv.DictReader(tsvfile, dialect='excel-tab')
			for row in reader:
				if (read_attr):
					graph.add_edge(row['SOURCE_SUBREDDIT'], row['TARGET_SUBREDDIT'], POST_ID = row['POST_ID'], \
							TIMESTAMP = row['TIMESTAMP'], LINK_SENTIMENT = row['LINK_SENTIMENT'], PROPERTIES = row['PROPERTIES'])
				else:
					graph.add_edge(row['SOURCE_SUBREDDIT'], row['TARGET_SUBREDDIT'])
	return graph

def merge_edges(graph):
	"""
	Merge multi edges into single weighted edges.

	INPUT:
	- ``graph`` -- A NetworkX MultiDiGraph.

	OUTPUT:
	- ``graph`` -- A NetworkX DiGraph where each edge has a new attribute 'WEIGHT'.
	"""
	weighted_graph = nx.DiGraph()
	# Calculate weights
	# Using ideas from https://stackoverflow.com/questions/15590812/networkx-convert-multigraph-into-simple-graph-with-weighted-edges
	for u,v in graph.edges():
		if weighted_graph.has_edge(u,v):
			weighted_graph[u][v]['WEIGHT'] += 1
		else:
			weighted_graph.add_edge(u, v, WEIGHT=1)

	# Calculate sentiment
	for u, v in graph.edges():
		sentiment = 0
		for edge in graph[u][v].values():
			sentiment += int(edge['LINK_SENTIMENT'])
		weighted_graph[u][v]['SENTIMENT'] = sentiment

	return weighted_graph

def cut_by_degree(original_graph, cut_range):
	graph = original_graph.copy()
	to_remove = []
	for node in graph.nodes():
		if (nx.degree(graph, node) in cut_range):
			to_remove.append(node)
	graph.remove_nodes_from(to_remove)
	return graph
