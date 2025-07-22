import json, argparse, re, gzip, statistics

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True)
    parser.add_argument('--output_prefix', type=str, required=True)
    args = parser.parse_args()

    date_pattern = re.compile(r'(c\d+)\.\d{2}(\d{2})(\d{2})(\d{2})\.warts.gz')
    data_aggre = []
    with gzip.open(args.input_dir, 'rt', encoding='utf-8') as f:
        for line in f:
            partial_dict = json.loads(line)
            for key, value in partial_dict.items():
                break
            for item in value:
                if item['stop-reason'] != 'completed':
                    continue
 
                dt = item['start-ts']
                rtts = [i['rtt'] for i in item['hop-metas'][-3:]]
                hop_num = item['stop-hop']

                data_aggre.append({
                    'datetime': dt,
                    'last-rtts': rtts,
                    'hop-num' : hop_num
                })
            
    sorted(data_aggre, key = lambda x : x['datetime'])

    with open(f'data/prelim/{args.output_prefix}.json', 'w') as f:
        json.dump(data_aggre, f, indent=4)
