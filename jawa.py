import heapq
from collections import defaultdict
from typing import Dict, List, Tuple

class DijkstraAlgorithm:
    """
    Implementation of Dijkstra's algorithm for finding shortest paths in a weighted graph.
    """
    
    def __init__(self):
        """Initialize the graph as an adjacency list."""
        self.graph = defaultdict(list)
    
    def add_edge(self, u: int, v: int, weight: int) -> None:
        """
        Add a weighted edge to the graph.
        
        Args:
            u: Source node
            v: Destination node
            weight: Weight of the edge
        """
        self.graph[u].append((v, weight))
        self.graph[v].append((u, weight))  # For undirected graph
    
    def dijkstra(self, start: int) -> Tuple[Dict[int, int], Dict[int, int]]:
        """
        Find the shortest path from start node to all other nodes.
        
        Args:
            start: Starting node
            
        Returns:
            A tuple containing:
            - distances: Dictionary with shortest distance to each node
            - previous: Dictionary with previous node in shortest path
        """
        distances = {node: float('inf') for node in self.graph}
        distances[start] = 0
        previous = {node: None for node in self.graph}
        
        # Min-heap: (distance, node)
        min_heap = [(0, start)]
        visited = set()
        
        while min_heap:
            current_distance, current_node = heapq.heappop(min_heap)
            
            # Skip if already visited
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # If current distance is greater than stored, skip
            if current_distance > distances[current_node]:
                continue
            
            # Check all neighbors
            for neighbor, weight in self.graph[current_node]:
                distance = current_distance + weight
                
                # If we found a shorter path, update it
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(min_heap, (distance, neighbor))
        
        return distances, previous
    
    def get_shortest_path(self, start: int, end: int) -> Tuple[List[int], int]:
        """
        Get the shortest path between two nodes.
        
        Args:
            start: Starting node
            end: Ending node
            
        Returns:
            A tuple containing:
            - path: List of nodes in the shortest path
            - distance: Total distance of the path
        """
        distances, previous = self.dijkstra(start)
        
        path = []
        current = end
        
        # Reconstruct path from end to start
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        
        # Verify path is valid
        if distances[end] == float('inf'):
            return [], float('inf')
        
        return path, distances[end]
    
    def print_all_shortest_paths(self, start: int) -> None:
        """
        Print shortest paths from start node to all other nodes.
        
        Args:
            start: Starting node
        """
        distances, previous = self.dijkstra(start)
        
        print(f"\nShortest paths from node {start}:")
        print("-" * 50)
        
        for node in sorted(distances.keys()):
            if distances[node] == float('inf'):
                print(f"Node {node}: UNREACHABLE")
            else:
                # Reconstruct path
                path = []
                current = node
                while current is not None:
                    path.append(current)
                    current = previous[current]
                path.reverse()
                
                print(f"Node {node}: Distance = {distances[node]}, Path = {' -> '.join(map(str, path))}")


# Example usage
if __name__ == "__main__":
    # Create a graph
    dijkstra = DijkstraAlgorithm()
    
    # Add edges (node1, node2, weight)
    edges = [
        (0, 1, 4),
        (0, 2, 2),
        (1, 2, 1),
        (1, 3, 5),
        (2, 3, 8),
        (2, 4, 10),
        (3, 4, 2),
        (3, 5, 6),
        (4, 5, 3),
    ]
    
    for u, v, w in edges:
        dijkstra.add_edge(u, v, w)
    
    # Find shortest paths from node 0
    dijkstra.print_all_shortest_paths(0)
    
    # Find shortest path between specific nodes
    start, end = 0, 5
    path, distance = dijkstra.get_shortest_path(start, end)
    
    print(f"\nShortest path from {start} to {end}:")
    print(f"Path: {' -> '.join(map(str, path))}")
    print(f"Distance: {distance}")
