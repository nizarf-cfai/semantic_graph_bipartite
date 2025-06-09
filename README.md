<<<<<<< HEAD
# Drug Network Graph Visualization

This project visualizes drug relationships and their topics using an interactive network graph. The visualization is built using NetworkX and Pyvis.

## Features
- Interactive network visualization with physics-based layout
- Drug nodes with different sizes based on fit status
- Topic nodes colored by cluster
- Interactive legend showing node types and clusters
- Hover tooltips with detailed information
- Adjustable physics parameters for optimal layout

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Place your `clustered_card_all.json` file in the project directory
3. Run the application: `python app.py`

## Output
The script generates an interactive HTML file (`network_graph.html`) that can be opened in any web browser. The visualization includes:
- Drug nodes (pink) with different sizes and border styles based on fit status
- Topic nodes colored by their cluster
- Interactive physics controls for adjusting the layout
- A legend showing node types and cluster colors

## Docker Deployment
Build and run using Docker:
```bash
docker build -t drug-network-graph .
docker run -v $(pwd):/app drug-network-graph
```
Note: The volume mount is necessary to access the input JSON file and save the output HTML file. 
=======
# semantic_graph_bipartite
>>>>>>> b331a1e76785ce094c92a4e3a9d78ae659dd0591
