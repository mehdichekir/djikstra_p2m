import math
from queue import PriorityQueue

def dijkstra(graph, src_node, dst_node):
    # Initialize costs and paths
    costs = {node: math.inf for node in graph}
    paths = {node: "" for node in graph}

    costs[src_node] = 0
    paths[src_node] = str(src_node)

    visited = set()

    pq = PriorityQueue()
    pq.put((costs[src_node], src_node))

    while not pq.empty():
        (cost, node) = pq.get()

        visited.add(node)

        for neighbor_node in graph[node]:
            neighbor_cost = graph[node][neighbor_node]

            if neighbor_node not in visited:
                cur_cost = costs[neighbor_node]
                new_cost = cost + neighbor_cost

                if new_cost < cur_cost:
                    costs[neighbor_node] = new_cost
                    paths[neighbor_node] = paths[node] + " " + str(neighbor_node)
                    pq.put((new_cost, neighbor_node))

    return {
        "cost": costs[dst_node],
        "path": [int(node) for node in paths[dst_node].strip().split(" ")]
    }
