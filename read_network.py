import networkx as nx
import csv

def read_tsv(path):
	"""
	Read graph edgelist, edge attributes and edge properties from a .tsv file.

	INPUT:
	- ``path`` -- The location of the .tsv file.

	OUTPUT:
	- ``graph`` -- The NetworkX object containing the read graph.
	"""
	# Using ideas from https://medium.com/@adds68/parsing-tsv-file-with-csv-in-python-662d6347b0cd
	graph = nx.MultiDiGraph()
	with open(path) as tsvfile:
		reader = csv.DictReader(tsvfile, dialect='excel-tab')
		for row in reader:
			graph.add_edge(row['SOURCE_SUBREDDIT'], row['TARGET_SUBREDDIT'])
			graph[row['SOURCE_SUBREDDIT']][row['TARGET_SUBREDDIT']]['POST_ID'] = row['POST_ID']
			graph[row['SOURCE_SUBREDDIT']][row['TARGET_SUBREDDIT']]['TIMESTAMP'] = row['TIMESTAMP']
			graph[row['SOURCE_SUBREDDIT']][row['TARGET_SUBREDDIT']]['LINK_SENTIMENT'] = row['LINK_SENTIMENT']
			graph[row['SOURCE_SUBREDDIT']][row['TARGET_SUBREDDIT']]['PROPERTIES'] = row['PROPERTIES']
	return graph