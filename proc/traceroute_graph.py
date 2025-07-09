import networkx as nx
import matplotlib.pyplot as plt
import argparse, gzip, json, re, os, ipaddress
from tqdm import tqdm
import maxminddb as mmdb

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
        label = None
        if record == 'None':
            continue
        if record:
            label = record
        else:
            with mmdb.open_database(args.maxmind_db) as reader:
                asn_data, prefix = reader.get_with_prefix_len(ip_addr)
                if not asn_data or not prefix:
                    continue
                
                network = ipaddress.ip_network(f'{ip_addr}/{prefix}', strict=False)
                network_addr = str(network.network_address)
                prefix = str(network)
                if mode == 'prefix':
                    if not network or not network_addr or not prefix:
                        continue

                    GLOBAL_PREFIX_DICT[convert_ip_str_to_number(network_addr)] = prefix
                    label = prefix
                elif mode == 'asn':
                    asn = asn_data.get('autonomous_system_number', None)
                    asn_org = asn_data.get('autonomous_system_organization', 'unknown')
                    if not asn:
                        continue
                    asn_desc = f'{asn}({asn_org})'
                    GLOBAL_ASN_DICT[convert_ip_str_to_number(network_addr)] = asn_desc
                    label = asn_desc

        if not label:
            continue
        if len(paths) == 0 or paths[-1] != label:
            paths.append(label)
    return paths

def process_node_graph(G, high_transit_nodes, file_prefix, label):
    nodes_to_display = set([data[0] for data in high_transit_nodes])
    high_transit_nodes_copy = nodes_to_display.copy()
    for node, _ in high_transit_nodes:
        nodes_to_display.update(G.neighbors(node))
    nodes_to_display_arr = list(nodes_to_display)
    
    plt.figure(figsize=(20, 15))
    sub_G = G.subgraph(nodes_to_display_arr)
    pos = nx.spring_layout(sub_G, k=0.3, iterations=50)
    node_colors = ['red' if node in high_transit_nodes_copy else 'lightgray' for node in sub_G.nodes()]
    node_sizes = [200 if node in high_transit_nodes else 50 for node in sub_G.nodes()]
    nx.draw_networkx_nodes(sub_G, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_edges(sub_G, pos, edge_color='gray', alpha=0.6)
    nx.draw_networkx_labels(G, pos, labels={n:n for n in sub_G.nodes}, font_size=10)

    plt.title(f"{label} Traceroute Transit Graph with Node >={args.threshold} Highlighted")
    plt.savefig(f'images/{file_prefix}/{label}_traceroute_high_transit_node_bound{args.threshold}.png')
    plt.close()

def process_edge_graph(G, high_utilized_edges, file_prefix, label):
    nodes_to_display = set()
    for edge, _ in high_utilized_edges:
        nodes_to_display.add(edge[0])
        nodes_to_display.add(edge[1])
    
    nodes_to_display_arr = list(nodes_to_display)
    plt.figure(figsize=(20, 15))
    sub_G = G.subgraph(nodes_to_display_arr)
    node_colors = ['lightgray' for node in sub_G.nodes()]
    node_sizes = [50 for node in sub_G.nodes()]
    pos = nx.spring_layout(sub_G, k=0.3, iterations=50)
    nx.draw_networkx_nodes(sub_G, pos, 
                           node_color=node_colors, node_size=node_sizes
                           )
    nx.draw_networkx_edges(sub_G, pos, edge_color='gray', alpha=0.6)
    nx.draw_networkx_labels(G, pos, labels={n:n for n in sub_G.nodes}, font_size=10)

    plt.title(f"{label} Traceroute Transit Graph with Edge >={args.threshold} Highlighted")
    plt.savefig(f'images/{file_prefix}/{label}_traceroute_high_utilized_edge_bound{args.threshold}.png')
    plt.close()   

def process_current_node_graph(G, file_prefix, label):
        node_transit_tuple = [(node, G.nodes[node]['transit']) for node in G.nodes]
        threshold = args.threshold if args.threshold else 0
        high_transit_nodes = [(node, count) for (node, count) in node_transit_tuple if count > threshold]
        if args.out_format == 'json':
            transit_node_with_degrees = [{'node': node, 'count': transit} for (node, transit) in high_transit_nodes]
            json_dict[label] = transit_node_with_degrees

        elif args.out_format == 'image':
            process_node_graph(G, high_transit_nodes, file_prefix, label)
        elif args.out_format == 'xml':
            output_prefix = args.output_prefix if not args.threshold else args.output_prefix + '-thres' + str(args.threshold)
            os.makedirs(f'data/graphs/{output_prefix}', exist_ok=True)
            nx.write_graphml(G, f'data/graphs/{output_prefix}/{label}_trace_node.graphml')

def process_current_edge_graph(G, file_prefix, label):
    edge_weight_tuple = [(edge, G.edges[edge]['weight']) for edge in G.edges()]
    threshold = args.threshold if args.threshold else 0
    high_utilized_edges = [(edge, count) for (edge, count) in edge_weight_tuple if count > threshold]
    if args.out_format == 'json':
        transit_edge_with_weights = [{'node': f'{edge[0]}->{edge[1]}', 'count': weight} for (edge, weight) in high_utilized_edges]
        json_dict[label] = transit_edge_with_weights

    elif args.out_format == 'image':
        process_edge_graph(G, high_utilized_edges, file_prefix, label)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--threshold", type=int, default=None)
    parser.add_argument("--mode", type=str, default="ip")
    parser.add_argument("--out_format", type=str, default="json") # choices: json, image, xml
    parser.add_argument("--target", type=str, default="node")
    parser.add_argument('--output_prefix', type=str, required=True)
    parser.add_argument('--maxmind_db', type=str, default='data/GeoLite2-ASN.mmdb')
    parser.add_argument('--start_time', type=str, default='xx')
    parser.add_argument('--end_time', type=str, default='xx')
    args = parser.parse_args()

    if args.out_format == 'xml':
        args.target = 'node' # ensure we onlt need to implement xml save logic in one processing helper function
    
    date_pattern = re.compile(r'(c\d+)\.\d{2}(\d{2})(\d{2})(\d{2})\.warts.gz')
    json_dict = {}
    output_prefix = f'({args.start_time})2({args.end_time})_{args.output_prefix}/{args.target}-{args.mode}'
    if args.threshold:
        output_prefix += '-thres' + str(args.threshold)

    prev_label = None
    if args.out_format == 'image':
        if os.path.exists(f'images/{output_prefix}'):
            exit(0)
        os.makedirs(f'images/{output_prefix}')
    
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
            if args.start_time != 'xx' and label < args.start_time:
                continue

            if not prev_label:
                # init new instnace
                G = nx.DiGraph()
                unique_probes = set()

            elif prev_label != label:
                if args.target == 'node':
                    process_current_node_graph(G, output_prefix, prev_label)
                elif args.target == 'edge':
                    process_current_edge_graph(G, output_prefix, prev_label)
                   
                G.clear()
                unique_probes.clear()
                if args.end_time != 'xx' and args.end_time < label:
                    break
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
                            G.nodes[prev_str]['transit'] += 1
                    prev_str = ip_addr
                G.nodes[prev_str]['transit'] += 1
        
        if args.end_time == 'xx' or args.end_time > label:
            if args.target == 'node':
                process_current_node_graph(G, output_prefix, label)
            elif args.target == 'edge':
                process_current_edge_graph(G, output_prefix, label)

        if args.out_format == 'json':
            output_name = f'data/outputs/({args.start_time})2({args.end_time})_{args.output_prefix}_traceroutes_{args.mode}_for_{args.target}.json'
            with open(output_name, 'w') as f:
                json.dump(json_dict, f, indent=4)
