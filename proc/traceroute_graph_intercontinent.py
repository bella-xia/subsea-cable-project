import networkx as nx
import matplotlib.pyplot as plt
import argparse, gzip, json, re, os, copy
from tqdm import tqdm
import maxminddb as mmdb 

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

def extract_iclinks(data : dict[any]) -> list[str]:
    ret = []
    ret.append(data['src-ip'])
    ret.extend([inst['src'] for inst in data['hop-metas']])
    ret.append(data['dst-ip'])
    ip_addrs = [ip_addr for ip_addr in ret if not is_private(ip_addr)]
    links = []

    # looking for neighboring paths
    prev_ip, prev_country = None, None
    for idx, ip_addr in enumerate(ip_addrs):
        with mmdb.open_database(args.ipinfo_db) as reader:
            data = reader.get(ip_addr)
        
        if not data or not data['country']:
            continue

        ip_geoloc = data['country']
        if not prev_country:
           prev_country = ip_geoloc
        elif prev_country != ip_geoloc:
            links.append([prev_ip, ip_addr])

        prev_ip, prev_country = ip_addr, ip_geoloc
    
    return links
 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument('--output_prefix', type=str, required=True)
    parser.add_argument('--ipinfo_db', type=str, default='data/ipinfo_lite.mmdb')
    args = parser.parse_args()
    
    date_pattern = re.compile(r'(c\d+)\.\d{2}(\d{2})(\d{2})(\d{2})\.warts.gz')
    json_dict, per_date_dict = {}, {}

    prev_label = None
    
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

            if prev_label and prev_label != label:
                json_dict[prev_label] = [{'node': key, 'count': value} for key, value in per_date_dict.items()] 
                per_date_dict = {}

            prev_label = label

            for inst in value:
                data = extract_iclinks(inst)

                for link in data:
                    desc = f'{link[0]}->{link[1]}'
                    per_date_dict[desc] = per_date_dict.get(desc, 0) + 1

    output_name = f'data/{args.output_prefix}-traceroute-intercontinental-links.json'
    with open(output_name, 'w') as f:
        json.dump(json_dict, f, indent=4)
