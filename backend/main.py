from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
def parse_pipeline(nodes: str = Form(...), edges: str = Form(...)):
    try:
        nodes_data = json.loads(nodes)
        edges_data = json.loads(edges)
        
        num_nodes = len(nodes_data)
        num_edges = len(edges_data)
        
        # Build adjacency list for DAG check
        adj = {node['id']: [] for node in nodes_data}
        in_degree = {node['id']: 0 for node in nodes_data}
        
        for edge in edges_data:
            source = edge['source']
            target = edge['target']
            
            # Ensure robustness if edge refers to non-existent node
            if source in adj and target in adj:
                adj[source].append(target)
                in_degree[target] += 1
                
        # Kahn's Algorithm for DAG check
        queue = [node_id for node_id in adj if in_degree[node_id] == 0]
        visited_count = 0
        
        while queue:
            u = queue.pop(0)
            visited_count += 1
            
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        is_dag = visited_count == num_nodes
        
        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'is_dag': is_dag
        }
    except Exception as e:
        return {'error': str(e)}