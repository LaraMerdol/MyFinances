import subprocess
import networkx as nx
import os
import pydot
from itertools import combinations
# Step 1: Generate the DOT file using pydeps
def generate_dot_file(project_path, output_file):
    try:
        command = ["pydeps", "--show-dot ", project_path,output_file]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("pydeps output:", result.stdout)
        if result.returncode != 0:
            print("pydeps error:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running pydeps: {e}")
        print("Ensure pydeps is installed and the project path is correct.")
        raise

# Step 2: Load the DOT file into a networkx graph
# Step 2: Load the DOT file into a networkx graph
def load_dot_file(dot_file):
    if not os.path.exists(dot_file):
        raise FileNotFoundError(f"The file {dot_file} was not created. Check the pydeps command.")
    
    # Read the DOT file into a networkx graph
    graph = nx.drawing.nx_pydot.read_dot(dot_file)
    
    # Convert node and edge attributes to integers if necessary
    for node in graph.nodes():
        if "weight" in graph.nodes[node]:
            try:
                graph.nodes[node]["weight"] = int(graph.nodes[node]["weight"])
            except (ValueError, TypeError):
                # If conversion fails, remove the attribute
                del graph.nodes[node]["weight"]
    
    for u, v, data in graph.edges(data=True):
        if "weight" in data:
            try:
                data["weight"] = int(data["weight"])
            except (ValueError, TypeError):
                # If conversion fails, remove the attribute
                del data["weight"]
    print("Nodes:", len(graph.nodes(data=True)))
    print("Edges:", len(graph.edges(data=True)))
    
    return graph


# Step 3: Calculate Modularity Quality (MQ) as per the lecture formula
def calculate_mq(graph, communities):
    # Convert communities to sets for faster lookups
    communities = [set(c) for c in communities]
    k = len(communities)
    
    # Calculate intra-connectivity (A_i) for each cluster
    A = []
    for cluster in communities:
        N_i = len(cluster)
        mu_i = sum(1 for u, v in graph.edges() if u in cluster and v in cluster)
        A_i = mu_i / (N_i ** 2) if N_i > 0 else 0
        A.append(A_i)
    
    # Calculate interconnectivity (E_ij) between clusters
    E = []
    for (i, j) in combinations(range(k), 2):
        cluster_i = communities[i]
        cluster_j = communities[j]
        epsilon_ij = sum(1 for u, v in graph.edges() if (u in cluster_i and v in cluster_j) or (u in cluster_j and v in cluster_i))
        N_i = len(cluster_i)
        N_j = len(cluster_j)
        E_ij = epsilon_ij / (2 * N_i * N_j) if (N_i > 0 and N_j > 0) else 0
        E.append(E_ij)
    
    # Compute MQ
    if k == 1:
        mq = A[0]
    else:
        avg_A = sum(A) / k
        avg_E = sum(E) / (k * (k - 1) / 2)  # Number of unique pairs: k*(k-1)/2
        mq = avg_A - avg_E
    
    return mq

# Main function
def main():
    project_path = "/Users/lara/Desktop/MyFinances/backend"
    dot_file = "a.dot"
    
    try:
        #generate_dot_file(project_path, dot_file)
        graph = load_dot_file(dot_file)
        
        # Detect communities using Louvain method
        undirected_graph = graph.to_undirected()
        communities = nx.community.greedy_modularity_communities(undirected_graph)
        
        # Calculate MQ using the lecture formula
        mq = calculate_mq(graph, communities)
        print(f"Modularity Quality (MQ): {mq}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()