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

# The way to calculate edge sign for undirected graphs is adapted from ideas in
# the following paper:
#	Leskovec, J., Huttenlocher, D., & Kleinberg, J. (2010, April).
#	Predicting positive and negative links in online social networks.
#	In Proceedings of the 19th international conference on World wide web (pp. 641-650).
#	https://doi.org/10.1145/1772690.1772756
def merge_edges(graph, undirected=False, threshold=0):
	"""
	Merge multi edges into single weighted edges.

	INPUT:
	- ``graph`` -- A NetworkX MultiDiGraph.
	- ``undirected -- Boolean, indicating if the output should be an undirected graph.
	- ``threshold`` -- A real number from 0 to 1, used to calculate edge sign
	if the output graph is undirected. A higher threshold will delete edges
	that have ambiguous sentiment.

	OUTPUT:
	- ``graph`` -- A NetworkX DiGraph where each edge has a new attribute 'WEIGHT'.
	Alternatively, if ``undirected`` is True, a NetworkX Graph where each edge also
	has the attribute ``SIGN``, calculated using link sentiment of the input graph.
	"""
	if undirected:
		weighted_graph = nx.Graph()
	else:
		weighted_graph = nx.DiGraph()
	# Calculate weights
	# Using ideas from https://stackoverflow.com/questions/15590812/networkx-convert-multigraph-into-simple-graph-with-weighted-edges
	for u,v in graph.edges():
		# no self-loops in undirected graph
		if undirected and u == v:
			continue
		if weighted_graph.has_edge(u,v):
			weighted_graph[u][v]['WEIGHT'] += 1
		else:
			weighted_graph.add_edge(u, v, WEIGHT=1)

	# Calculate sentiment
	for u, v in weighted_graph.edges():
		sentiment = 0
		if graph.has_edge(u,v):
			for edge in graph[u][v].values():
				sentiment += int(edge['LINK_SENTIMENT'])
		if undirected and graph.has_edge(v,u):
			for edge in graph[v][u].values():
				sentiment += int(edge['LINK_SENTIMENT'])
		weighted_graph[u][v]['SENTIMENT'] = sentiment
		if undirected:
			# combine multiple directed edges into one undirected edge
			# link sentiment becomes sign, either positive or negative
			# ideas adapted from https://doi.org/10.1145/1772690.1772756
			# (their graph does not have multiple parallel edges)
			weight = weighted_graph[u][v]['WEIGHT']
			if abs(sentiment) / weight >= threshold:
				sign = 1
				if sentiment < 0:
					sign = -1
				weighted_graph[u][v]['SIGN'] = sign
			# if sentiment sign is not clear enough, delete edge
			else:
				weighted_graph.remove_edge(u,v)

	return weighted_graph

def cut_by_degree(original_graph, cut_range):
	graph = original_graph.copy()
	to_remove = []
	for node in graph.nodes():
		if (nx.degree(graph, node) in cut_range):
			to_remove.append(node)
	graph.remove_nodes_from(to_remove)
	return graph
