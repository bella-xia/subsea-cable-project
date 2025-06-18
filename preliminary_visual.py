import matplotlib.pyplot as plt
import gzip, argparse, json, statistics, re
from tqdm import tqdm



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, default="data/egypt-probe-from-kenya.jsonl.gz")
    parser.add_argument("--unit", type=str, default="cycle")

    args = parser.parse_args()

    date_pattern = re.compile(r'(c\d+)\.\d{2}(\d{2})(\d{2})(\d{2})\.warts.gz')

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
            # average over last five hop
            data_aggre[date_key]['max-rtts'].extend(
                [statistics.mean([i['rtt'] for i in item['hop-metas'][-5:]]) for item in value if item['stop-reason'] == 'completed'])
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
    

    # graph 1: on stop reasons
    fig, ax = plt.subplots(figsize=(15, 10))
    keys = list(counter_aggre.keys())
    categories = list({cat for counts in counter_aggre.values() for cat in counts if cat != 'gaplimit'}) # TODO: ignoring gap limit for now because it takes up too much samples
    bottom = [0] * len(keys)
    for cat in categories:
        values = [counter_aggre[key].get(cat, 0) for key in keys]
        ax.bar(keys, values, bottom=bottom, label=cat)
        bottom = [b + v for b, v, in zip(bottom, values)]      
    
    ax.set_ylabel('probe counts')
    ax.set_xlabel('Time Duration')
    ax.tick_params(axis='x', labelrotation=30, labelsize=8)
    ax.legend(title='stop reason')
    fig.savefig(f'images/per-{args.unit}-stop-hop-reason-histogram.png')


    # graph 2: all completed trip time statistics
    fig, axes = plt.subplots(2, 1, figsize=(30, 10))
    x_pos = range(len(keys))  # Positions for the bar
    width = 10
    
    bars = axes[0].bar(x_pos, max_rtt_avg, yerr=max_rtt_std)
    for bar in bars:
        height = bar.get_height()
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,  # x position (center of bar)
            height + 50,                             # y position (top of bar)
            f'{height:.2f}',                    # text (rounded value)
            ha='center', va='bottom', fontsize=8  # alignment and styling
        )
    axes[0].set_xlabel('Time Duration')
    axes[0].set_ylabel('Last-hop Round-trip time')
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels(keys)
    axes[0].tick_params(axis='x', labelrotation=30, labelsize=8)
    bars = axes[1].bar([p for p in x_pos], hop_num_avg, yerr=hop_num_std)
    for bar in bars:
        height = bar.get_height()
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,  # x position (center of bar)
            height + 3,                             # y position (top of bar)
            f'{height:.2f}',                    # text (rounded value)
            ha='center', va='bottom', fontsize=8  # alignment and styling
        )
    axes[1].set_xlabel('Time Duration')
    axes[1].set_ylabel('Number of Hops')
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(keys)
    axes[1].tick_params(axis='x', labelrotation=30, labelsize=8)

    plt.savefig(f"images/per-{args.unit}-traceroute-preliminary-stat.png")
