import networkx as nx
#import matplotlib.pyplot as plt

def calc_cc(graph):
	"""
	Calculates the clustering coefficient for each node in the graph. The values are stored in a new attribute named 'cc'.

	INPUT:
	- ``graph`` -- The graph in which the clustering coefficient should be calculated.
	"""
	clustering_coeffs = {}
	for node in graph.nodes():
		clustering_coeffs[node] = { "cc" : nx.clustering(graph, node)}
	nx.set_node_attributes(graph, clustering_coeffs)