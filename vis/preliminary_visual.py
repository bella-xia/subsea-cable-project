import matplotlib.pyplot as plt
import gzip, argparse, json, statistics, re
from tqdm import tqdm
from utils.date_processing import generate_date_sequence

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--unit", type=str, default="date")
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--contiguous', type=str, default='False')
    parser.add_argument('--start_time', type=str, default='xx')
    parser.add_argument('--end_time', type=str, default='xx')

    args = parser.parse_args()

    contiguous_flag = True if args.contiguous == 'True' else False

    if contiguous_flag and (args.start_time == 'xx' or args.end_time == 'xx'):
        print(f'expected contiguous dates but do not specify range')
        exit(-1)
    if contiguous_flag and args.unit == 'cycle':
        print(f'error: unable to determine contiguous cycle names')
        exit(-2)

    date_pattern = re.compile(r'(c\d+)\.\d{2}(\d{2})(\d{2})(\d{2})\.warts.gz')
    output_prefix = f"({args.start_time})2({args.end_time})_per_{args.unit}{'_contiguous' if contiguous_flag else ''}"

    max_rtt_avg, max_rtt_std = [], []
    hop_num_avg, hop_num_std = [], []
    keys = []
    data_aggre, counter_aggre = {}, {}
    with gzip.open(args.input_dir, 'rt', encoding='utf-8') as f:
        for line in tqdm(f):
            partial_dict = json.loads(line)
            for key, value in partial_dict.items():
                break
            re_date = date_pattern.search(key)
            date_key = f"{re_date.group(2)}-{re_date.group(3)}-{re_date.group(4)}"
            if args.unit == 'cycle':
                date_key = f'{re_date.group(1)}({date_key})'
            counter_aggre.setdefault(date_key, {})
            for item in value:
                counter_aggre[date_key].setdefault(item['stop-reason'], 0)
                counter_aggre[date_key][item['stop-reason']] += 1
            if not data_aggre.get(date_key, None):
                data_aggre[date_key] = {
                    'max-rtts': [],
                    'hop-nums': []
                }
            # average over last three hop
            data_aggre[date_key]['max-rtts'].extend(
                [statistics.mean([i['rtt'] for i in item['hop-metas'][-3:]]) for item in value if item['stop-reason'] == 'completed'])
            data_aggre[date_key]['hop-nums'].extend([item['stop-hop'] for item in value if item['stop-reason'] == 'completed'])

    sorted_data_aggre = dict(sorted(data_aggre.items(), key=lambda item: item[0]))
    for key, value in sorted_data_aggre.items():
        if len(value['max-rtts']) == 0:
            continue
        keys.append(key)
        max_rtt_avg.append(statistics.mean(value['max-rtts']))
        max_rtt_std.append(statistics.stdev(value['max-rtts']) if len(value['max-rtts']) > 1 else 0)
        hop_num_avg.append(statistics.mean(value['hop-nums']))
        hop_num_std.append(statistics.stdev(value['hop-nums']) if len(value['hop-nums']) > 1 else 0)
    
    if contiguous_flag:
        expected_keys = generate_date_sequence(args.start_time, args.end_time) 
        expected_rtt_avg, expected_rtt_std = [], []
        expected_num_avg, expected_num_std = [], []
        counter = 0
        while keys[counter] < args.start_time:
            counter += 1
        for key in expected_keys:
            if keys[counter] == key:
                expected_rtt_avg.append(max_rtt_avg[counter])
                expected_rtt_std.append(max_rtt_std[counter])
                expected_num_avg.append(hop_num_avg[counter])
                expected_num_std.append(hop_num_std[counter])
                counter += 1
            else:
                expected_rtt_avg.append(0)
                expected_rtt_std.append(0)
                expected_num_avg.append(0)
                expected_num_std.append(0)
            counter_aggre.setdefault(key, {})
    elif args.start_time == 'xx' and args.end_time == 'xx':
        expected_keys = keys
        expected_rtt_avg, expected_rtt_std = max_rtt_avg, max_rtt_std
        expected_num_avg, expected_num_std = hop_num_avg, hop_num_std
    else:
        expected_keys = []
        expected_rtt_avg, expected_rtt_std = [], []
        expected_num_avg, expected_num_std = [], []
        for k, v1, v2, v3, v4 in zip(keys, max_rtt_avg, max_rtt_std, hop_num_avg, hop_num_std):
            if args.start_time != 'xx' and args.start_time > k:
                continue
            if args.end_time != 'xx' and args.end_time < k:
                break

            expected_keys.append(k)
            expected_rtt_avg.append(v1)
            expected_rtt_std.append(v2)
            expected_num_avg.append(v3)
            expected_num_std.append(v4)

    # graph 1: on stop reasons
    fig1, ax1 = plt.subplots(figsize=(15, 10))
    fig2, ax2 = plt.subplots(figsize=(15, 10))
    total_probes_per_day = {k : sum([c for _, c in v.items()]) for k, v in counter_aggre.items()}
    counter_cats = sorted({cat for counts in counter_aggre.values() for cat in counts}) 

    color_map = {
    'noreason': 'tab:gray',
    'completed': 'tab:green',
    'loop': 'tab:orange',
    'error': 'tab:red',
    'unreach': 'tab:blue',
    'gss': 'tab:yellow',
    'icmp': 'tab:pink',
    'hoplimit': 'tab:purple',
    'gaplimit': 'tab:olive',
    }
    bottom = [0] * len(expected_keys)
    for cat in counter_cats:
        values = [counter_aggre[key].get(cat, 0) for key in expected_keys]
        ratio_keys = [key for key in expected_keys if total_probes_per_day[key] != 0]
        ratios = [counter_aggre[key].get(cat, 0) / total_probes_per_day[key] for key in ratio_keys]
        if cat != 'gaplimit':
            ax1.bar(expected_keys, values, bottom=bottom, label=cat, color=color_map[cat])
            ax2.plot(ratio_keys, ratios, label=cat, color=color_map[cat])
            bottom = [b + v for b, v, in zip(bottom, values)]      
    
    ax1.set_ylabel('probe counts')
    ax1.set_xlabel('Time Duration')
    ax1.tick_params(axis='x', labelrotation=30, labelsize=8)
    ax1.legend(title='stop reason')
    fig1.savefig(f'{args.output_dir}/{output_prefix}_stophop_reason_counts_no_gaplimit_histogram.png')

    ax2.set_ylabel('probe ratio')
    ax2.set_xlabel('Time Duration')
    ax2.tick_params(axis='x', labelrotation=30, labelsize=8)
    ax2.legend(title='stop reason')
    fig2.savefig(f'{args.output_dir}/{output_prefix}_stophop_reason_ratios_no_gaplimit_histogram.png')
    
    values = [counter_aggre[key].get('gaplimit', 0) for key in expected_keys]
    ratios = [counter_aggre[key].get('gaplimit', 0) / total_probes_per_day[key] for key in ratio_keys]
    ax1.bar(expected_keys, values, bottom=bottom, label='gaplimit', color=color_map['gaplimit'])
    ax1.legend(title='stop reason')
    ax2.plot(ratio_keys, ratios,label='gaplimit', color=color_map['gaplimit'])
    ax2.legend(title='stop reason')
    fig1.savefig(f'{args.output_dir}/{output_prefix}_stophop_reason_counts_histogram.png')     
    fig2.savefig(f'{args.output_dir}/{output_prefix}_stophop_reason_ratios_histogram.png')
    plt.close()

    # graph 2: all completed trip time statistics
    fig, axes = plt.subplots(2, 1, figsize=(30, 10))
    x_pos = range(len(expected_keys))
    width = 10
    
    bars = axes[0].bar(x_pos, expected_rtt_avg, yerr=expected_rtt_std)
    for bar in bars:
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width() / 2, height + 50, f'{height:.2f}', ha='center', va='bottom', fontsize=8)
    axes[0].set_xlabel('Time Duration')
    axes[0].set_ylabel('Last-hop Round-trip time')
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels(expected_keys)
    axes[0].tick_params(axis='x', labelrotation=30, labelsize=8)
    bars = axes[1].bar([p for p in x_pos], expected_num_avg, yerr=expected_num_std)
    for bar in bars:
        height = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width() / 2, height + 3, f'{height:.2f}', ha='center', va='bottom', fontsize=8)
    axes[1].set_xlabel('Time Duration')
    axes[1].set_ylabel('Number of Hops')
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(expected_keys)
    axes[1].tick_params(axis='x', labelrotation=30, labelsize=8)

    plt.savefig(f"{args.output_dir}/{output_prefix}_traceroute_preliminary_stat.png")
