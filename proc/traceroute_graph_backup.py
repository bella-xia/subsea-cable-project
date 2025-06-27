import networkx as nx
import matplotlib.pyplot as plt
import argparse, gzip, json, re, os
from tqdm import tqdm
from ipwhois.net import Net
from ipwhois.asn import IPASN

GLOBAL_ASN_DICT : dict[int, str] = {}
GLOBAL_PREFIX_DICT :  dict[int, str] = {}

def is_private(ip_addr : str) -> bool:
    # private ips include:
    # 10.0.0.0 to 10.255.255.255
    # 172.16.0.0 to 172.31.255.255
    # 192.168.0.0 to 192.168.255.255
    ip_addr_arr = ip_addr.split('.')
    sec1, sec2 = int(ip_addr_arr[0]), int(ip_addr_arr[1])
    if (sec1 == 10 or (sec1 == 172 and (sec2 >= 16 and sec2 <= 31)) or (sec1 == 192 and sec2 == 168)):
        return True
    return False

def convert_ip_str_to_number(ip_addr : str) -> int | None:
    ip_addr_arr = ip_addr.split('.')
    ip_num = 0
    for sec in ip_addr_arr:
        try:
            val = int(sec)  
            assert 0 <= val <= 255
        except Exception:
            return None  
     
        ip_num = (ip_num << 8) + val

    if not (0 <= ip_num < (1 << 32)):
        return None
    return ip_num

def longest_prefix_match(ip_addr : str, mode: str) -> str | None: 
    ip_num = convert_ip_str_to_number(ip_addr)

    # invalid ip
    if not ip_num:
        return 'None'
    prefix_len = 32
    while ip_num > 0:
        # get rid of the last digit
        mask = (1 << prefix_len) - 1 << (32 - prefix_len)
        ip_num = ip_num & mask
        query = GLOBAL_ASN_DICT.get(ip_num, None) if mode == 'asn' else GLOBAL_PREFIX_DICT.get(ip_num, None)
        if query:
            return query
        prefix_len -= 1
    
    return None

def extract_path(data : dict[any], mode : str) -> list[str]:
    ret = []
    ret.append(data['src-ip'])
    ret.extend([inst['src'] for inst in data['hop-metas']])
    ret.append(data['dst-ip'])

    ip_addrs = [ip_addr for ip_addr in ret if not is_private(ip_addr)]
    if mode == 'ip':
        return ip_addrs

    paths = []
    
    for _, ip_addr in enumerate(ip_addrs):
        record = longest_prefix_match(ip_addr, mode)
        if record == 'None':
            continue
        if record:
            label = record
        else:
            net = Net(ip_addr)
            obj = IPASN(net)
            results = obj.lookup()
            if not results or not results['asn_cidr'] or not results['asn'] or not results['asn_country_code'] or results['asn_cidr'] == 'NA' or results['asn'] == 'NA':
                continue
            prefix = results['asn_cidr'].split('/')[0]
            if mode == 'prefix':
                label = results['asn_cidr']
                GLOBAL_PREFIX_DICT[convert_ip_str_to_number(prefix)] = results['asn_cidr']
            elif mode == 'asn':
                if results['asn'] == 'NA':
                    GLOBAL_ASN_DICT[convert_ip_str_to_number(ip_addr)] = 'None'
                    continue
                else:
                    label = results['asn_description'] if (results['asn_description'] and len(results['asn_description']) > 0) else f"{results['asn']}, {results['asn_country_code']}"
                    GLOBAL_ASN_DICT[convert_ip_str_to_number(prefix)] = label

        if len(paths) == 0 or paths[-1] != label:
            paths.append(label)
    return paths

def process_node_graph(G, high_transit_nodes, file_prefix):
    nodes_to_display = set([data[0] for data in high_transit_nodes])
    high_transit_nodes_copy = nodes_to_display.copy()
    for node, _ in high_transit_nodes:
        nodes_to_display.update(G.neighbors(node))
    
    nodes_to_display_arr = list(nodes_to_display)
    
    plt.figure(figsize=(20, 15))
    sub_G = G.subgraph(nodes_to_display_arr)
    pos = nx.spring_layout(sub_G, k=0.3, iterations=50)
    node_colors = ['red' if node in high_transit_nodes else 'lightgray' for node in sub_G.nodes()]
    node_sizes = [200 if node in high_transit_nodes else 50 for node in sub_G.nodes()]
    nx.draw_networkx_nodes(sub_G, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_edges(sub_G, pos, edge_color='gray', alpha=0.6)
    nx.draw_networkx_labels(G, pos, labels={n:n for n in sub_G.nodes}, font_size=10)

    plt.title(f"{label} Traceroute Transit Graph with Node >={args.threshold} Highlighted")
    plt.savefig(f'images/{file_prefix}/{label}-traceroute-high-transit-node-bound{args.threshold}.png')
    plt.close()


def process_edge_graph(G, high_utilized_edges, file_prefix):
    nodes_to_display = set()
    for edge, _ in high_utilized_edges:
        nodes_to_display.add(edge[0])
        nodes_to_display.add(edge[1])
    
    nodes_to_display_arr = list(nodes_to_display)
    plt.figure(figsize=(20, 15))
    sub_G = G.subgraph(nodes_to_display_arr)
    pos = nx.spring_layout(sub_G, k=0.3, iterations=50)
    # node_colors = ['red' if node in high_transit_nodes else 'lightgray' for node in sub_G.nodes()]
    # node_sizes = [200 if node in high_transit_nodes else 50 for node in sub_G.nodes()]
    nx.draw_networkx_nodes(sub_G, pos, 
                           #node_color=node_colors, node_size=node_sizes
                           )
    nx.draw_networkx_edges(sub_G, pos, edge_color='gray', alpha=0.6)
    nx.draw_networkx_labels(G, pos, labels={n:n for n in sub_G.nodes}, font_size=10)

    plt.title(f"{label} Traceroute Transit Graph with Edge >={args.threshold} Highlighted")
    plt.savefig(f'images/{file_prefix}/{label}-traceroute-high-utilized-edge-bound{args.threshold}.png')
    plt.close()   

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--threshold", type=int, default=None)
    parser.add_argument("--mode", type=str, default="ip") # node frequency or edge frequency
    parser.add_argument("--out_format", type=str, default="json") # choose whether use json to parse data or output images directly
    parser.add_argument("--target", type=str, default="node") # check whether we are looking at node (ip / asn) or connection (tuple[ip, ip])
    parser.add_argument('--output_prefix', type=str, required=True)
    args = parser.parse_args()
    
    date_pattern = re.compile(r'(c\d+)\.\d{2}(\d{2})(\d{2})(\d{2})\.warts.gz')
    json_dict = {}

    prev_label = None
    if args.out_format == 'image':
        if os.path.exists(f'images/{args.output_prefix}/{args.target}+{args.mode}+bound+{args.threshold}'):
            exit(0)
        os.makedirs(f'images/{args.output_prefix}/{args.target}+{args.mode}+bound+{args.threshold}')
    
    with gzip.open(args.input_dir, 'rt', encoding='utf-8') as f:
        for line in tqdm(f):
            partial_dict = json.loads(line)
            for key, value in partial_dict.items():
                    break 

            value = [inst for inst in value if inst['stop-reason'] == 'completed']
            if len(value) == 0:
                continue
            re_date = date_pattern.search(key)
            label = f"{re_date.group(2)}-{re_date.group(3)}-{re_date.group(4)}"
            if not prev_label:
                # init new instnace
                G = nx.DiGraph()
                unique_probes = set()

            elif prev_label != label:
                
                if args.target == 'node':
                    node_transit_tuple = [(node, G.nodes[node]['transit']) for node in G.nodes]
                    threshold = args.threshold if args.threshold else 0
                    high_transit_nodes = [(node, count) for (node, count) in node_transit_tuple if count > threshold]
                    if args.out_format == 'json':
                        transit_node_with_degrees = [{'node': node, 'count': transit} for (node, transit) in high_transit_nodes]
                        json_dict[label] = transit_node_with_degrees

                    elif args.out_format == 'image':
                        process_node_graph(G, high_transit_nodes, f'{args.output_prefix}/{args.target}+{args.mode}+bound+{args.threshold}')
                elif args.target == 'edge':
                    edge_weight_tuple = [(edge, G.edges[edge]['weight']) for edge in G.edges()]
                    threshold = args.threshold if args.threshold else 0
                    high_utilized_edges = [(edge, count) for (edge, count) in edge_weight_tuple if count > threshold]
                    if args.out_format == 'json':
                        transit_edge_with_weights = [{'node': f'{edge[0]}->{edge[1]}', 'count': weight} for (edge, weight) in high_utilized_edges]
                        json_dict[label] = transit_edge_with_weights

                    elif args.out_format == 'image':
                        process_edge_graph(G, high_utilized_edges, f'{args.output_prefix}/{args.target}+{args.mode}+bound+{args.threshold}')

                G.clear()
                unique_probes.clear()

            prev_label = label

            for inst in value:
                data = extract_path(inst, args.mode)

                # ensure no completely redundant path
                probe_str = '->'.join(data)
                if probe_str in unique_probes:
                    continue

                unique_probes.add(probe_str)
                prev_str = None
                
                for idx, ip_addr in enumerate(data):
                    if not G.has_node(ip_addr):
                        G.add_node(ip_addr, transit=0)
                    if prev_str:
                        if not G.has_edge(prev_str, ip_addr):
                            G.add_edge(prev_str, ip_addr, weight=1)
                        else:
                            G[prev_str][ip_addr]['weight'] += 1
                            if idx > 0:
                                # transit level in the middle
                                G.nodes[prev_str]['transit'] += 1
                    prev_str = ip_addr

        if args.out_format == 'json':
            output_name = f'data/{args.output_prefix}-traceroute-le{args.threshold}-{args.mode}-for-{args.target}.json' if args.threshold else f'data/{args.output_prefix}-traceroutes-{args.mode}-for-{args.target}.json' 
            with open(output_name, 'w') as f:
                json.dump(json_dict, f, indent=4)
