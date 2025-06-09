import json
import networkx as nx
from pyvis.network import Network
import random
import colorsys
from flask import Flask, send_file
import os

app = Flask(__name__)

def generate_graph():
    # Read the JSON data
    with open('clustered_card_all.json', 'r') as file:
        data = json.load(file)

    # Create a set of all drug names to ensure uniqueness
    drug_names = set(item['drug_generic_name'] for item in data)

    # Get unique clusters and create color mapping
    clusters = set()
    for item in data:
        for result in item['result']:
            clusters.add(result['cluster'])

    # Generate distinct colors for each cluster
    def generate_colors(n):
        colors = []
        for i in range(n):
            hue = i / n
            saturation = 0.3 + random.random() * 0.2  # Light colors
            value = 0.9 + random.random() * 0.1  # Bright colors
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            colors.append(hex_color)
        return colors

    cluster_colors = dict(zip(clusters, generate_colors(len(clusters))))

    # Create a network graph
    net = Network(height='750px', width='100%', bgcolor='#ffffff', font_color='#333')

    # Configure physics layout for more spacing
    net.barnes_hut(
        gravity=-15000,
        central_gravity=0.3,
        spring_length=200,
        spring_strength=0.04,
        damping=0.09,
        overlap=0.1
    )

    net.show_buttons(filter_=['physics'])

    # Add main drug nodes
    for item in data:
        drug_name = item['drug_generic_name']
        is_fit = item.get('fit', False)  # Get fit value, default to False if not present
        
        # Adjust size and border based on fit value
        node_size = 60 if is_fit else 40  # Bigger size for fit=True
        border_color = '#000000' if is_fit else '#FF69B4'  # Black border for fit=True
        border_width = 4 if is_fit else 3  # Thicker border for fit=True
        
        # Add main drug node with conditional styling
        net.add_node(drug_name, 
                     label=drug_name, 
                     size=node_size, 
                     color={
                         'background': '#FFB6C1',  # Light pink/red
                         'border': border_color,
                     },
                     borderWidth=border_width,
                     title=f"{drug_name}\nFit: {is_fit}",
                     font={'size': 16, 'bold': True})
        
        # Add topic nodes and connections
        for result in item['result']:
            topic = result['topic']
            # Skip if topic is actually a drug name
            if topic in drug_names:
                continue
                
            count = result['count']
            cluster = result['cluster']
            
            # Add topic node with cluster-specific color and size based on count
            node_size = count * 10  # Multiply count by 10 to make size differences more visible
            label_text = topic[:20] if len(topic) > 20 else topic
            net.add_node(topic, 
                        label=label_text, 
                        size=node_size, 
                        color=cluster_colors[cluster],
                        title=f"Topic: {topic}\nCount: {count}\nCluster: {cluster}")
            
            # Connect drug to topic with black edges of fixed width
            net.add_edge(drug_name, topic, 
                        color='black',
                        title=f"Count: {count}")

    # Add legend for clusters and fit status
    legend_html = """
    <div style="position: absolute; top: 10px; right: 10px; background: white; padding: 10px; border: 1px solid #ccc;">
        <h3>Legend</h3>
        <div style="margin-bottom: 10px;">
            <h4>Drug Node Types:</h4>
            <div><span style="display: inline-block; width: 20px; height: 20px; background: #FFB6C1; border: 4px solid #000; margin-right: 5px;"></span>Fit Drug (Larger)</div>
            <div><span style="display: inline-block; width: 20px; height: 20px; background: #FFB6C1; border: 3px solid #FF69B4; margin-right: 5px;"></span>Regular Drug</div>
        </div>
        <div>
            <h4>Clusters:</h4>
    """
    for cluster, color in cluster_colors.items():
        legend_html += f'<div><span style="display: inline-block; width: 20px; height: 20px; background: {color}; margin-right: 5px;"></span>{cluster}</div>'
    legend_html += "</div></div>"

    # Save with legend
    net.html = net.html.replace("</body>", f"{legend_html}</body>")
    net.save_graph('network_graph.html')

@app.route('/')
def serve_graph():
    # Generate the graph if it doesn't exist
    if not os.path.exists('network_graph.html'):
        generate_graph()
    return send_file('network_graph.html')

if __name__ == '__main__':
    # Generate the graph on startup
    generate_graph()
    # Run the Flask app
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port) 