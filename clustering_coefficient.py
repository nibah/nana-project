import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from read_network import read_tsv, merge_edges

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

def plot_cc(graph):
	"""
	Calculates the clustering coefficient for each node in the graph. The values are then plotted as a histogram.

	INPUT:
	- ``graph`` -- The graph in which the clustering coefficient should be calculated.
	"""
	clustering_coeffs = []
	for node in graph.nodes():
		clustering_coeffs.append(nx.clustering(graph, node))
	
	plt.axvline(x=np.mean(clustering_coeffs), color='r', linestyle='-')
	plt.hist(clustering_coeffs, bins=100)

graph = read_tsv(["data/soc-redditHyperlinks-body.tsv", "data/soc-redditHyperlinks-title.tsv"], True)
weighted_graph = merge_edges(graph)

pdf = PdfPages("Clustering Coefficient.pdf")
plt.title("Clustering coefficients over the network")
plot_cc(weighted_graph)
pdf.savefig()
plt.close()
pdf.close()