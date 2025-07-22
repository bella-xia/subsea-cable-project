import argparse, json

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True)
    parser.add_argument('--prefix', type=str, required=True)
    parser.add_argument('--dst', type=str, default='')
    parser.add_argument('--front', type=str, default='True')
    args = parser.parse_args()

    dst_set = set([dst_item for dst_item in args.dst.split(',') if dst_item != ''])
    if len(dst_set) == 0:
        exit(0)
    front_flag = True if args.front == 'True' else False

    with open(args.input_dir, 'r') as f:
       data = json.load(f)
    
    airports = set([inst.split('(')[0] for inst in data.keys()])
    aggre_dict = {} 
    aggre_counter = {}
    for airport in airports:
        filtered_keys = [k for k in data.keys() if k.startswith(airport + '(')]
        airport_data = {}
        dates = set([k.split('(')[1][:-1] for k in filtered_keys])
        dates = sorted(list(dates))
        for date_str in dates:
            query_data = data.get(f'{airport}({date_str})', None)
            if not query_data:
                continue

            cns = sorted(list(query_data.keys()))
            unique_asns = set()
            all_counters = {}
            filtered_query_data = {}
            filtered_query_data['counter'] = {}
            for cn in cns:
                if cn.lower() not in dst_set:
                    continue
                all_counts = sum(list(query_data[cn].values()))
                all_counters[cn] = all_counts
                processed_query_data = {}
                for k, v in query_data[cn].items():
                    k = k if not front_flag else k.split('->')[0]
                    processed_query_data[k] = processed_query_data.get(k, 0) + v
                    aggre_counter[k] = aggre_counter.get(k, 0) + v
                    filtered_query_data['counter'][cn.lower()] = filtered_query_data['counter'].get(cn.lower(), 0) + v
                filtered_query_data.setdefault(cn.lower(), {})
                filtered_query_data[cn.lower()].update(processed_query_data)
            airport_data[date_str] = filtered_query_data

        aggre_dict[airport] = airport_data
    
    # create id2asn mapping
    sorted_asn = sorted(aggre_counter.keys(), key=lambda x : aggre_counter.get(x, 0), reverse=True)
    aggre_dict['sorted-asn'] = sorted_asn

    with open(f'data/crosscn/{args.prefix}.json', 'w') as f:
        json.dump(aggre_dict, f, indent=4)
