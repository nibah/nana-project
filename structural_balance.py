# A linear time algorithm to test structural balance in a network
# Adapted from this paper:
#   Harary, F., & Kabell, J. A. (1980).
#   A simple algorithm to detect balance in signed graphs.
#   Mathematical Social Sciences, 1(1), 131-136.
#   https://doi.org/10.1016/0165-4896(80)90010-4
import networkx as nx


SIGN, TESTED, VISITED = 'SIGN', 'TESTED', 'VISITED'


def dfs(G, u):
    G.nodes[u][VISITED] = True
    for v in G[u]:
        if G[u][v][TESTED]:
            continue
        G[u][v][TESTED] = True
        if G.nodes[v][VISITED]:
            if G[u][v][SIGN] != G.nodes[u][SIGN] * G.nodes[v][SIGN]:
                return False
        else:
            G.nodes[v][SIGN] = G.nodes[u][SIGN] * G[u][v][SIGN]
            if not dfs(G, v):
                return False
    return True


def is_balanced(G):
    # initialize nodes and edges
    nx.set_edge_attributes(G, name=TESTED, values=False)
    nx.set_node_attributes(G, name=VISITED, values=False)
    # in case the graph is not connected, start as many DFS as necessary
    for n in G:
        if not G.nodes[n][VISITED]:
            G.nodes[n][SIGN] = 1
            if not dfs(G, n):
                return False
    return True
