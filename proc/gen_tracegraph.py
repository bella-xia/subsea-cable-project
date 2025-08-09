import networkx as nx
import argparse, gzip, json, re, os, ipaddress
from tqdm import tqdm

def is_private(ip_addr : str) -> bool:
    ip_addr_arr = ip_addr.split('.')
    sec1, sec2 = int(ip_addr_arr[0]), int(ip_addr_arr[1])
    if (sec1 == 10 or (sec1 == 172 and (sec2 >= 16 and sec2 <= 31)) or (sec1 == 192 and sec2 == 168)):
        return True
    return False

def extract_path(data : dict[any]) -> list[str]:
    ret = []
    ret.append(data['src-ip'])
    ret.extend([inst['src'] for inst in data['hop-metas']])
    ret.append(data['dst-ip'])

    ip_addrs = [ip_addr for ip_addr in ret if not is_private(ip_addr)]
    return ip_addrs

def process_current_node_graph(G, file_prefix, label):
    node_transit_tuple = [(node, G.nodes[node]['transit'], list(G.nodes[node]['asns'])) for node in G.nodes]
    if args.out_format == 'json':
        transit_node_with_degrees = [{'node': node, 'count': transit, 'asns': asns} for (node, transit, asns) in node_transit_tuple]
        json_dict[label] = transit_node_with_degrees
    
    elif args.out_format == 'xml':
        for node in G.nodes:
            G.nodes[node]['asns'] = ';; '.join(list(G.nodes[node]['asns']))
        for edge in G.edges:
            G.edges[edge]['asns'] = ';; '.join(list(G.edges[edge]['asns']))
        nx.write_graphml(G, f'{args.out_dir}/{label}.graphml')

def process_current_edge_graph(G, file_prefix, label):
    edge_weight_tuple = [(edge, G.edges[edge]['weight'], list(G.edges[edge]['asns'])) for edge in G.edges()]
    if args.out_format == 'json':
        transit_edge_with_weights = [{'node': f'{edge[0]}->{edge[1]}', 'count': weight, 'asns': asns} for (edge, weight, asns) in edge_weight_tuple]
        json_dict[label] = transit_edge_with_weights

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_path", type=str, required=True)
    parser.add_argument("--out_format", type=str, default="json") # choices: json, xml
    parser.add_argument("--target", type=str, default="node")
    parser.add_argument('--out_dir', type=str, required=True)
    args = parser.parse_args()

    if args.out_format == 'xml':
        args.target = 'node'     

    date_pattern = re.compile(r'(c\d+)\.\d{2}(\d{2})(\d{2})(\d{2})\.warts.gz')
    json_dict = {}
    if args.out_format == 'xml':
        os.makedirs(args.out_dir, exist_ok=True)

    prev_label = None
    with gzip.open(args.in_path, 'rt', encoding='utf-8') as f:
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
                G = nx.DiGraph()
                unique_probes = set()

            elif prev_label != label:
                if args.target == 'node':
                    process_current_node_graph(G, args.out_dir, prev_label)
                elif args.target == 'edge':
                    process_current_edge_graph(G, args.out_dir, prev_label)
                   
                G.clear()
                unique_probes.clear()
            prev_label = label

            for inst in value:
                data = extract_path(inst)

                probe_str = '->'.join(data)
                if probe_str in unique_probes:
                    continue

                unique_probes.add(probe_str)
                prev_str = None
                
                for idx, ip_addr in enumerate(data):
                    if not G.has_node(ip_addr):
                        G.add_node(ip_addr, transit=0,
                                    asns = set())
                    if prev_str:
                        if not G.has_edge(prev_str, ip_addr):
                            G.add_edge(prev_str, ip_addr, weight=1,
                                       asns = set())
                        else:
                            G[prev_str][ip_addr]['weight'] += 1
                            G.nodes[prev_str]['transit'] += 1
                            G[prev_str][ip_addr]['asns'].update(inst['crosscn-asn'])
                            G.nodes[prev_str]['asns'].update(inst['crosscn-asn'])
                    prev_str = ip_addr
                G.nodes[prev_str]['transit'] += 1
                G.nodes[prev_str]['asns'].update(inst['crosscn-asn'])
        
        if args.target == 'node':
            process_current_node_graph(G, args.out_dir, label)
        elif args.target == 'edge':
            process_current_edge_graph(G, args.out_dir, label)

        if args.out_format == 'json':
            with open(args.out_dir, 'w') as f:
                json.dump(json_dict, f, indent=4)
