import argparse, os, re
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm, trange

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default='data/graphs')
    parser.add_argument('--norm', type=str, default='sum') # choices include sum, minmax, all
    parser.add_argument('--start_time', type=str, default='xx')
    parser.add_argument('--end_time', type=str, default='xx')
    parser.add_argument('--output_prefix', type=str, default=None)
    args = parser.parse_args()

    if not args.output_prefix:
        input_dir_arr = args.input_dir.split('/')
        args.output_prefix = input_dir_arr[-1]
        if len(args.output_prefix) == 0:
            args.output_prefix = input_dir_arr[-2]
    
    ident_pat = re.compile(r'\d{2}\-\d{2}\-\d{2}')
    graph_data = sorted(os.listdir(args.input_dir))

    start_idx = 0
    if args.start_time != 'xx':
        while graph_data[start_idx] < args.start_time:
            start_idx += 1
    end_idx = -1
    if args.end_time != 'xx':
        while graph_data[end_idx] > args.end_time:
            end_idx -= 1

    graph_data = graph_data[start_idx:end_idx + 1] if end_idx != -1 else graph_data[start_idx:]
    node_set = set()
    
    aggre_k = []
    daggre_raw, daggre_norm = [], []
    paggre_raw, paggre_norm = [], []

    for idx in trange(len(graph_data) - 1):
        graph_inst_d1, graph_inst_d2 = graph_data[idx], graph_data[idx + 1]
        k1, k2 = re.search(ident_pat, graph_inst_d1).group(), re.search(ident_pat, graph_inst_d2).group()
        aggre_k.append(k2)

        G_d1 = nx.read_graphml(os.path.join(args.input_dir, graph_inst_d1))
        G_d2 = nx.read_graphml(os.path.join(args.input_dir, graph_inst_d2))

        node_set.clear()
        node_set.update(list(G_d1.nodes()))
        node_set.update(list(G_d2.nodes()))

        # create nodes
        id2node = {i: n for i, n in enumerate(list(node_set))}
        node2id = {v : k for k, v in id2node.items()}
        n_node = len(node2id)

        # create a n*n matrix for both day
        A1_d, A2_d = np.zeros((n_node, n_node)), np.zeros((n_node, n_node)) # density
        A1_p, A2_p = np.zeros((n_node, n_node)), np.zeros((n_node, n_node)) # presence

        for i in range(n_node):
            for j in range(n_node):
                if (i != j):
                    ni, nj = id2node[i], id2node[j]
                    d1, d2 = G_d1.edges.get((ni, nj), None), G_d2.edges.get((ni, nj), None)
                    A1_d[i][j], A1_p[i][j] = (d1['weight'], 1) if d1 else (0, 0)
                    A2_d[i][j], A2_p[i][j] = (d2['weight'], 1) if d2 else (0, 0)
        
        daggre_raw.append(np.linalg.norm(A1_d - A2_d, ord='fro'))
        paggre_raw.append(np.linalg.norm(A1_p - A2_p, ord='fro'))
        
        if args.norm == 'sum':
            A1_d, A1_p = (A1_d / A1_d.sum(), A1_p / A1_p.sum())
            A2_d, A2_p = (A2_d / A2_d.sum(), A2_p / A2_p.sum())
            daggre_norm.append(np.linalg.norm(A1_d - A2_d, ord='fro'))
            paggre_norm.append(np.linalg.norm(A1_p - A2_p, ord='fro'))
        elif args.norm == 'minmax':
            A1_d = (A1_d - A1_d.min()) / (A1_d.max() - A1_d.min())
            A2_d = (A2_d - A2_d.min()) / (A2_d.max() - A2_d.min())
            # don't need to do it for presence because it only has 0 and 1
            daggre_norm.append(np.linalg.norm(A1_d - A2_d, ord='fro'))
            paggre_norm.append(np.linalg.norm(A1_p - A2_p, ord='fro'))
 
    fig, (ax11, ax21) = plt.subplots(2, 1, sharex=True, figsize=(20, 10))
    color = 'tab:red'
    ax11.set_title('IP Link Density Graph Difference over Time')
    ax11.set_ylabel('Frobenius Distance (raw)', color=color)
    ax11.plot(aggre_k, daggre_raw, color=color, marker='o')
    ax11.tick_params(axis='y', labelcolor=color)

    if len(daggre_norm) == len(aggre_k):
        ax12 = ax11.twinx()
        color = 'tab:blue'
        ax12.set_ylabel('Frobenius Distance (Normalized)', color=color)
        ax12.plot(aggre_k, daggre_norm, color=color, marker='o')
        ax12.tick_params(axis='y', labelcolor=color)

    ax21.set_title('IP Link Presence Graph Difference over Time')
    color = 'tab:red'
    ax21.set_xlabel('date')
    ax21.plot(aggre_k, paggre_raw, color=color, marker='o')
    ax21.tick_params(axis='y', labelcolor=color)
    plt.setp(ax21.get_xticklabels(), rotation=45, ha='right')

    if len(paggre_norm) == len(aggre_k):
        ax22 = ax21.twinx()
        color = 'tab:blue'
        ax22.plot(aggre_k, paggre_norm, color=color, marker='o')
        ax22.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.savefig(f'images/classification/{args.output_prefix}_frobenius_dist.png')
