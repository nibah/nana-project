import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from read_network import read_tsv

def plot_distribution(original_graph, lower_limit=-1, upper_limit=-1):
	"""
	Calculates and plots the degree distribution of the graph. Before doing this, nodes with low and/or high degrees can be cut.

	INPUT:
	- ``original_graph`` -- The graph in which the degrees should be calculated.
	- ``lower_limit`` -- Nodes with degree < lower_limit will be cut. Set to -1 if no lower_limit needed.
	- ``upper_limit` -- Nodes with degree > upper_limit will be cut. Set to -1 if no upper_limit needed.
	"""
	graph = original_graph.copy()
	to_remove = []
	if (lower_limit != -1):
		for node in graph.nodes():
			if (nx.degree(graph, node) < lower_limit):
				to_remove.append(node)
	if (upper_limit != -1):
		for node in graph.nodes():
			if (nx.degree(graph, node) > upper_limit):
				to_remove.append(node)
	graph.remove_nodes_from(to_remove)
	y = nx.degree_histogram(graph)
	x = np.linspace(0, len(y), len(y))
	plt.plot(x, y)

graph = read_tsv(["data/soc-redditHyperlinks-body.tsv", "data/soc-redditHyperlinks-title.tsv"], False)
pdf = PdfPages("Degree Distribution.pdf")

plt.title("Degree distribution over the entire network")
plt.xscale('log')
plot_distribution(graph, -1, -1)
pdf.savefig()
plt.close()

plt.title("Degree distribution after removing all nodes with degree < 50")
plot_distribution(graph, 50, -1)
pdf.savefig()
plt.close()

plt.title("Degree distribution after removing all nodes with degree > 100")
plot_distribution(graph, -1, 100)
pdf.savefig()
plt.close()

pdf.close()