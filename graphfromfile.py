import networkx as nx
import random
import math
from itertools import combinations
import time
import pandas as pd

# Load the graph from a file
file_path = "facebook_combined.txt"
densities = [0.001, 0.010, 0.125, 0.25, 0.5, 0.75]
time_start = time.perf_counter()


def load_graph_from_txt_file(file_path):
    try:
        graph = nx.read_edgelist(file_path, nodetype=int)
        return graph
    except Exception as e:
        print(f"Error loading graph: {e}")
        return None


def load_graph_from_csv_file(file_path):
    try:
        df = pd.read_csv(file_path)
        graph = nx.from_pandas_edgelist(df, source='node_1', target='node_2')
        return graph
    except Exception as e:
        print(f"Error loading graph: {e}")
        return None


# Greedy heuristic algorithm - building a clique iteratively
def greedy_clique_search(graph, k):
    nodes = list(graph.nodes)
    clique = []
    nodes.sort(key=lambda x: graph.degree[x], reverse=True)
    for node in nodes:
        if len(clique) < k and all(graph.has_edge(node, v) for v in clique):
            clique.append(node)
        if len(clique) == k:
            return True
    return False


# Monte Carlo algorithm - building a clique randomly
def monte_carlo_incremental(graph, k, iterations):
    nodes = list(graph.nodes)
    for i in range(iterations):
        random.shuffle(nodes)
        clique = []
        for node in nodes:
            if all(graph.has_edge(node, v) for v in clique):
                clique.append(node)
            if len(clique) == k:
                return True
    return False


# Monte Carlo algorithm - randomly sampling k nodes and checking for cliques
def monte_carlo_sampling(graph, k, iterations):
    nodes = list(graph.nodes)
    tested_solutions = set()
    for i in range(iterations):
        sampled_vertices = tuple(sorted(random.sample(nodes, k)))
        if sampled_vertices in tested_solutions:
            continue
        tested_solutions.add(sampled_vertices)
        if all(graph.has_edge(u, v) for u, v in combinations(sampled_vertices, 2)):
            return True
    return False


def decide_graphs():
    if file_path.endswith('.csv'):
        graph = load_graph_from_csv_file(file_path)
    if file_path.endswith('.txt'):
        graph = load_graph_from_txt_file(file_path)
    if graph is None:
        exit()
    for density in densities:
        k = math.ceil(graph.number_of_nodes() * density)
        has_greedy_clique = greedy_clique_search(graph, k)
        has_incremental_clique = monte_carlo_incremental(graph, k, 1000)
        has_sampling_clique = monte_carlo_sampling(graph, k, 1000)
        print(
            f" k: {k} - Greedy: {has_greedy_clique} - Monte Carlo incremental: {has_incremental_clique} - Monte Carlo sampling: {has_sampling_clique} ")


decide_graphs()
time_elapsed = (time.perf_counter() - time_start)
print(f"Total time: {time_elapsed:.1f} secs")
