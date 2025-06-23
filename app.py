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
    with open('card_cluster_all3.json', 'r') as file:
        data = json.load(file)

    # data = data[:10]
    # Create a set of all drug names to ensure uniqueness
    drug_names = set(item['drug_generic_name'] for item in data)

    # Get unique clusters and create color mapping
    clusters = set()
    sponsor_classes = set()
    for item in data:
        for result in item['result']:
            clusters.add(result['cluster'])
        # Collect sponsor classes
        for sponsor in item.get('sponsor') or []:
            sponsor_classes.add(sponsor['class'])

    # Generate distinct colors for each cluster and sponsor class
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
    # Assign most noticeable colors to INDUSTRY and ACADEMY, generate colors for others
    sponsor_class_colors = {}
    fixed_colors = {
        'INDUSTRY': '#FF0000',  # Bright red
        'ACADEMY': '#1E90FF',   # Blue
    }
    # Assign fixed colors first
    for key, color in fixed_colors.items():
        for sponsor_class in sponsor_classes:
            if sponsor_class.upper() == key:
                sponsor_class_colors[sponsor_class] = color
    # Generate colors for the rest
    other_classes = [c for c in sponsor_classes if c.upper() not in fixed_colors]
    other_colors = generate_colors(len(other_classes))
    for sponsor_class, color in zip(other_classes, other_colors):
        sponsor_class_colors[sponsor_class] = color

    # Create a network graph
    net = Network(height='750px', width='100%', bgcolor='#ffffff', font_color='#000000')

    # Advanced vis.js options for better node separation
    options = {
        "physics": {
            "repulsion": {
                "nodeDistance": 1200,
                "centralGravity": 0.2,
                "springLength": 350,
                "springStrength": 0.05,
                "damping": 0.09
            },
            "minVelocity": 0.1
        },
        "nodes": {
            "scaling": {
                "label": {
                    'enabled': True,
                    'min': 40,
                    'max': 100,
                    'maxVisible': 100000,
                    'drawThreshold': 0
                }
            },
            "font": {
                "size": 70,
                "vadjust": 0,
                "bold": True
            }
        }
    }
    net.set_options(json.dumps(options))

    # net.show_buttons(filter_=['physics'])

    # Add main drug nodes
    sponsor_nodes_added = set()
    for item in data:
        drug_name = item['drug_generic_name']
        is_fit = item.get('fit', False)  # Get fit value, default to False if not present
        
        # Adjust size and border based on fit value
        node_size = 100   # Bigger size for fit=True
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
                    font={
                        'face': 'arial',
                        'size': 70,  # Even larger font size for drug nodes
                        'vadjust': 0,
                        'background': 'rgba(255,255,255,0.8)',  # Background for visibility
                        'bold': True
                    })
        
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
                        label=' ', 
                        size=node_size, 
                        color=cluster_colors[cluster],
                        title=f"Topic: {topic}\nCount: {count}\nCluster: {cluster}",
                        )
            
            # Connect drug to topic with black edges of fixed width
            net.add_edge(drug_name, topic, 
                        color='black',
                        title=f"Count: {count}",
                        length=400)

        # Add sponsor nodes and edges
        for sponsor in (item.get('sponsor') or [])[:5]:
            sponsor_name = sponsor['name']
            sponsor_class = sponsor['class']
            if sponsor_name not in sponsor_nodes_added:
                net.add_node(
                    sponsor_name,
                    label=' ',  # Hide label
                    size=25,  # Smaller size
                    color=sponsor_class_colors[sponsor_class],
                    borderWidth=2,  # Default border
                    shape='triangle',  # Triangle shape
                    title=f"Sponsor: {sponsor_name}\nClass: {sponsor_class}",
                    font={
                        'face': 'arial',
                        'size': 30,
                        'vadjust': 0,
                        'background': 'rgba(255,255,255,0.8)',
                        'bold': True
                    }
                )
                sponsor_nodes_added.add(sponsor_name)
            # Connect sponsor to drug
            net.add_edge(sponsor_name, drug_name, color='gray', title=f"Sponsor: {sponsor_name}", length=400)

    # Add legend for clusters, fit status, and sponsor classes
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
    legend_html += """
        </div>
        <div>
            <h4>Sponsor Classes:</h4>
    """
    for sponsor_class, color in sponsor_class_colors.items():
        legend_html += f'<div><span style="display: inline-block; width: 20px; height: 20px; background: {color}; margin-right: 5px;"></span>{sponsor_class}</div>'
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