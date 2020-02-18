import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from read_network import read_tsv, cut_by_degree

def plot_distribution(original_graph, lower_limit=-1, upper_limit=-1):
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
	plt.show()

graph_body = read_tsv("data/soc-redditHyperlinks-body.tsv", False)
graph_title = read_tsv("data/soc-redditHyperlinks-title.tsv", False)

#plot_distribution(graph_body, -1, 100)
#plot_distribution(graph_title, -1, 100)
#print(nx.info(cut_by_degree(graph_body, range(0, 100))))
#print(nx.info(cut_by_degree(graph_body, range(0, 50))))
#print(nx.info(cut_by_degree(graph_body, range(0, 10))))

cut_body = cut_by_degree(graph_body, range(0, 50))
cut_title = cut_by_degree(graph_title, range(0,50))
plot_distribution(cut_body, -1, 100)
plot_distribution(cut_title, -1, 100)