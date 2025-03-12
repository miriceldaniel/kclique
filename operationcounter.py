import networkx as nx
import random
import matplotlib.pyplot as plt
import math
from itertools import combinations
import time

# Student id seed
random.seed(123578)
sampling_operations = []
incremental_operations = []
sampling_operations_counter, incremental_operations_counter = 0, 0
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

    # Generate graph with fixed density 0.5
    density = 0.5
    num_edges = int(max_edges * density)
    edges = list(nx.non_edges(G))
    random.shuffle(edges)
    selected_edges = edges[:num_edges]
    G_copy = G.copy()
    G_copy.add_edges_from(selected_edges)
    graphs.append((density, G_copy))

    return graphs


# Monte Carlo algorithm - randomly sampling k nodes and checking for cliques
def monte_carlo_sampling(graph, k, iterations):
    global sampling_operations_counter
    nodes = list(graph.nodes)
    tested_solutions = set()
    for i in range(iterations):
        sampling_operations_counter += k  # Count the sampling operation
        sampled_vertices = tuple(sorted(random.sample(nodes, k)))
        sampling_operations_counter += k * round(math.log(k))
        if sampled_vertices in tested_solutions:
            sampling_operations_counter += 1  # Count the set membership check
            continue
        tested_solutions.add(sampled_vertices)
        sampling_operations_counter += len(sampled_vertices)  # Count the addition to the set
        adjacency_checks = sum(1 for u, v in combinations(sampled_vertices, 2))
        sampling_operations_counter += adjacency_checks  # Count adjacency checks
        if all(graph.has_edge(u, v) for u, v in combinations(sampled_vertices, 2)):
            return True
    return False


# Monte Carlo algorithm - building a clique randomly
def monte_carlo_incremental(graph, k, iterations):
    global incremental_operations_counter
    nodes = list(graph.nodes)
    for i in range(iterations):
        incremental_operations_counter += len(nodes)  # Counting the shuffle operation
        random.shuffle(nodes)
        clique = []
        for node in nodes:
            # Count adjacency checks for all members of the current clique
            adjacency_checks = sum(1 for v in clique if graph.has_edge(node, v))
            incremental_operations_counter += adjacency_checks
            if all(graph.has_edge(node, v) for v in clique):
                clique.append(node)
                incremental_operations_counter += 1  # Counting the append operation
            if len(clique) == k:
                incremental_operations_counter += 1  # Counting the length check
                return True
    return False


# Generate graphs for vertex counts from 4 up to a given limit
def generate_decide_graphs(vertex_limit):
    for num_vertices in range(4, vertex_limit + 1):
        global sampling_operations, incremental_operations, sampling_operations_counter, incremental_operations_counter
        sampling_operations_counter = 0
        incremental_operations_counter = 0
        graphs = generate_graphs(num_vertices)
        print(f"\nGraph with {num_vertices} vertices:")
        for density, graph in graphs:
            print(f"  Density: {density * 100}% - Edges: {len(graph.edges())}")
            k = math.ceil(num_vertices * density)
            has_sampling_clique = monte_carlo_sampling(graph, k, 1000)
            has_incremental_clique = monte_carlo_incremental(graph, k, 1000)
            sampling_operations.append(sampling_operations_counter)
            incremental_operations.append(incremental_operations_counter)
            print(f"  k: {k} - Sampling: {has_sampling_clique} - Incremental: {has_incremental_clique}")


# Run the graph generation and plotting
generate_decide_graphs(100)
print(sampling_operations)
print(incremental_operations)


# Time usage
time_elapsed = (time.perf_counter() - time_start)
print(f"Total time: {time_elapsed:.1f} secs")
