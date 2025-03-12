import networkx as nx
import random
import matplotlib.pyplot as plt
import math
from itertools import combinations
import time

# Student id seed
random.seed(123578)
densities = [0.125, 0.25, 0.5, 0.75]
total_count, incremental_difference_count, sampling_difference_count, greedy_difference_count = 0, 0, 0, 0
time_start = time.perf_counter()


# Helper function to generate 2D points that are not too close
def generate_points(num_points, min_distance=10):
    points = []
    while len(points) < num_points:
        x = random.randint(1, 1000)
        y = random.randint(1, 1000)
        if all(math.dist((x, y), p) >= min_distance for p in points):
            points.append((x, y))
    return points


# Generate graphs with varying densities
def generate_graphs(num_vertices):
    points = generate_points(num_vertices)
    G = nx.Graph()

    # Add vertices
    for i, point in enumerate(points):
        G.add_node(i, pos=point)

    # Determine the maximum number of edges
    max_edges = num_vertices * (num_vertices - 1) // 2
    graphs = []

    # Generate graphs for each density
    for density in densities:
        num_edges = int(max_edges * density)
        edges = list(nx.non_edges(G))
        random.shuffle(edges)
        selected_edges = edges[:num_edges]
        G_copy = G.copy()
        G_copy.add_edges_from(selected_edges)
        graphs.append((density, G_copy))

    return graphs


# Exhaustive search algorithm - searching through all subsets
def exhaustive_clique_search(graph, k):
    nodes = list(graph.nodes)
    for subset in combinations(nodes, k):
        if all(graph.has_edge(u, v) for u, v in combinations(subset, 2)):
            return True
    return False


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


def generate_decide_graphs(vertex_limit):
    global total_count, incremental_difference_count, sampling_difference_count, greedy_difference_count
    for num_vertices in range(4, vertex_limit + 1):
        graphs = generate_graphs(num_vertices)
        print(f"\nGraphs with {num_vertices} vertices:")
        for density, graph in graphs:
            print(f"  Density: {density * 100}% - Edges: {len(graph.edges())}")
            k_values = [math.ceil(num_vertices * d) for d in densities]
            for k in k_values:
                has_exhaustive_clique = exhaustive_clique_search(graph, k)
                has_greedy_clique = greedy_clique_search(graph, k)
                has_incremental_clique = monte_carlo_incremental(graph, k, 1000)
                has_sampling_clique = monte_carlo_sampling(graph, k, 1000)
                total_count += 1
                if has_exhaustive_clique != has_incremental_clique:
                    incremental_difference_count += 1
                if has_exhaustive_clique != has_sampling_clique:
                    sampling_difference_count += 1
                if has_exhaustive_clique != has_greedy_clique:
                    greedy_difference_count += 1
                print(
                    f"  Density: {density * 100}% - k: {k} - Exhaustive: {has_exhaustive_clique} - Greedy: {has_greedy_clique} - Monte Carlo Incremental: {has_incremental_clique} - Monte Carlo Sampling: {has_sampling_clique} ")

generate_decide_graphs(20)
print(
    f"  Total graphs generated: {total_count} - Greedy false negatives: {greedy_difference_count} - Monte Carlo incremental false negatives: {incremental_difference_count} - Monte Carlo sampling false negatives: {sampling_difference_count}")
print(f"  Greedy precision: {100 - greedy_difference_count / total_count * 100}%")
print(f"  Monte Carlo incremental precision: {100 - incremental_difference_count / total_count * 100}%")
print(f"  Monte Carlo sampling precision: {100 - sampling_difference_count / total_count * 100}%")
time_elapsed = (time.perf_counter() - time_start)
print(f"Total time: {time_elapsed:.1f} secs")
