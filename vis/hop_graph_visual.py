import networkx as nx 
from networkx.drawing.nx_agraph import to_agraph
from networkx.drawing.nx_pydot import to_pydot
import matplotlib.pyplot as plt

def process_node_graph(G, threshold, title):
    high_transit_nodes = [(node, G.nodes[node]['transit']) for node in G.nodes if G.nodes[node]['transit'] >= threshold]
    nodes_to_display = set([data[0] for data in high_transit_nodes])
    high_transit_nodes_copy = nodes_to_display.copy()
    for node, _ in high_transit_nodes:
        nodes_to_display.update(G.neighbors(node))
    nodes_to_display_arr = list(nodes_to_display)
    
    fig, ax = plt.subplots(figsize=(20, 15))
    sub_G = G.subgraph(nodes_to_display_arr)
    pos = nx.spring_layout(sub_G, k=0.3, iterations=50)
    node_colors = ['red' if node in high_transit_nodes_copy else 'lightgray' for node in sub_G.nodes()]
    node_transits = [G.nodes[node]['transit'] for node in sub_G.nodes()]
    max_transit = max(node_transits) if node_transits else 1
    node_sizes = [100 + 900 * (t / max_transit) for t in node_transits]
    nx.draw_networkx_nodes(sub_G, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_edges(sub_G, pos, edge_color='gray', alpha=0.6)
    nx.draw_networkx_labels(G, pos, labels={n:n for n in sub_G.nodes}, font_size=10)
    ax.set_title(title)
    plt.close(fig)
    return fig

def process_edge_graph(G, threshold, title):
    high_utilized_edges = [(edge, G.edges[edge]['weight']) for edge in G.edges() if G.edges[edge]['weight'] >= threshold]
    edges_to_display = set([data[0] for data in high_utilized_edges])
    nodes_to_display = set()
    for edge, _ in high_utilized_edges:
        nodes_to_display.add(edge[0])
        nodes_to_display.add(edge[1])
    
    nodes_to_display_arr = list(nodes_to_display)
    fig, ax = plt.subplots(figsize=(20, 15))
    sub_G = G.subgraph(nodes_to_display_arr)
    edge_weights = [G.edges[edge]['weight'] for edge in sub_G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    edge_widths = [1 + 4 * (w / max_weight) for w in edge_weights]
    pos = nx.spring_layout(sub_G, k=0.3, iterations=50)
    nx.draw_networkx_nodes(sub_G, pos, 
                           node_color='lightgray')
    nx.draw_networkx_edges(sub_G, pos, edge_color='lightgray', width=edge_widths, alpha=0.6)
    nx.draw_networkx_labels(G, pos, labels={n:n for n in sub_G.nodes}, font_size=10)
    ax.set_title(title)
    plt.close(fig)
    return fig

def graph_image_processor(input_dir, mode, threshold=40): 
    G = nx.read_graphml(input_dir)
    title = input_dir.split('/')[-1].split('.')[0]
    if mode == 'node':
        return process_node_graph(G, threshold, title)
    elif mode == 'edge':
        return process_edge_graph(G, threshold, title)
    return None
