import argparse, os, re, json
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm, trange
from scipy.special import rel_entr
from scipy.spatial.distance import jensenshannon

def get_divergence(d1, d2, epsilon=1e-10):
    support = set()
    support.update(d1.keys())
    support.update(d2.keys())
    support = list(support)

    p = np.array([d1.get(k, 0) for k in support], dtype=np.float64)
    q = np.array([d2.get(k, 0) for k in support], dtype=np.float64)
    p += epsilon
    q += epsilon
    p /= p.sum()
    q /= q.sum()

    kl_div = np.sum(rel_entr(p, q))
    js_div = jensenshannon(p, q, base=2) ** 2

    return kl_div, js_div

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_prefix', type=str, required=True)
    parser.add_argument('--top_k', type=int, default=50)
    parser.add_argument('--top_r', type=int, default=80) # top 20% of traffic
    parser.add_argument('--mode', type=str, default='top_r')
    args = parser.parse_args()

    node_path = args.input_prefix + '_for_node.json'
    edge_path = args.input_prefix + '_for_edge.json'
    
    assert(os.path.exists(node_path) and os.path.exists(edge_path))

    with open(node_path, 'r') as f:
        node_data = json.load(f)
    
    with open(edge_path, 'r') as f:
        edge_data = json.load(f)

    assert(sorted(node_data.keys()) == sorted(edge_data.keys()))
    dates = sorted(node_data.keys())

    keys, node_js, node_kl, edge_js, edge_kl = [], [], [], [], []

    prev_node, curr_node, prev_edge, curr_edge = None, None, None,None
    
    for date in dates:
        if prev_node and prev_edge:
            keys.append(date)
        
        # Node data
        stats_per_day = node_data[date]
        sorted_stats_per_day = sorted(stats_per_day, key=lambda x : x['count'], reverse=True)
        if args.mode == 'top_k':
            curr_node = {item['node']: item['count'] for item in sorted_stats_per_day[:args.top_k]}
        else:
            curr_node = {}
            total_traffic = sum(item['count'] for item in sorted_stats_per_day)
            accum_dist = 0
            for item in sorted_stats_per_day:
                curr_node[item['node']] = item['count']
                accum_dist += item['count']
                if accum_dist > total_traffic * args.top_r:
                    break
        if prev_node:
            kl_div, js_div = get_divergence(prev_node, curr_node)
            node_js.append(js_div)
            node_kl.append(kl_div)
        prev_node = curr_node

        # Edge data
        stats_per_day = edge_data[date]
        sorted_stats_per_day = sorted(stats_per_day, key=lambda x : x['count'], reverse=True)
        if args.mode == 'top_k':
            curr_edge = {item['node']: item['count'] for item in sorted_stats_per_day[:args.top_k]}
        else:
            curr_edge = {}
            total_traffic = sum(item['count'] for item in sorted_stats_per_day)
            accum_dist = 0
            for item in sorted_stats_per_day:
                curr_edge[item['node']] = item['count']
                accum_dist += item['count']
                if accum_dist > total_traffic * args.top_r:
                    break
        if prev_edge:
            kl_div, js_div = get_divergence(prev_edge, curr_edge)
            edge_js.append(js_div)
            edge_kl.append(kl_div)
        prev_edge = curr_edge

    
    filter_spec = f'(top {args.top_k})' if args.mode == 'top_k' else f'(top {args.top_r}%)'

    fig, (ax11, ax21) = plt.subplots(2, 1, sharex=True, figsize=(20, 10))
    color = 'tab:red'
    ax11.set_title(f'Top IP Hop Distribution Change over Time {filter_spec}')
    ax11.set_ylabel('KL Divergence', color=color)
    ax11.plot(keys, node_kl, color=color, marker='o')
    ax11.tick_params(axis='y', labelcolor=color)

    ax12 = ax11.twinx()
    color = 'tab:blue'
    ax12.set_ylabel('JS Divergence', color=color)
    ax12.plot(keys, node_js, color=color, marker='o')
    ax12.tick_params(axis='y', labelcolor=color)

    ax21.set_title(f'Top IP Link Distribution Change over Time {filter_spec}')
    color = 'tab:red'
    ax21.set_xlabel('date')
    ax21.plot(keys, edge_kl, color=color, marker='o')
    ax21.tick_params(axis='y', labelcolor=color)
    plt.setp(ax21.get_xticklabels(), rotation=45, ha='right')

    ax22 = ax21.twinx()
    color = 'tab:blue'
    ax22.plot(keys, edge_js, color=color, marker='o')
    ax22.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.savefig(f'images/classification/{args.input_prefix.split(")_")[-1]}_dist_divergence.png')

