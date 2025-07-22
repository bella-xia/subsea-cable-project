import os, argparse, json
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from .utils.date_processing import generate_date_sequence

def crosscn_asn_processor(input_dir, time_spec, key_spec,
                          pri_cspec='tab20', sup_cspec='viridis', num_sup=20):
    pri_cmap = plt.get_cmap(pri_cspec)
    sup_cmap = plt.get_cmap(sup_cspec).resampled(num_sup)
 
    with open(input_dir, 'r') as f:
        j = json.load(f)
        data = j.get(key_spec, {})
        asn_list = j.get('sorted-asn', [])

    if len(data) == 0 or len(asn_list) == 0:
        return None

    bar_data = data.get(time_spec, {})
    count_data = bar_data.get('counter', {})
    if len(bar_data) == 0 or len(count_data) == 0:
        return None

    asn2color = {asn : pri_cmap(idx) if idx < 20 else sup_cmap(idx - 20) for idx, asn in enumerate(asn_list[:20 + num_sup - 1])}
    asn2color['other'] = sup_cmap(19)
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))

    # bar chart on the number of packets probed to each destination cn
    sorted_count_data = dict(sorted(count_data.items(), key=lambda x : x[0]))
    bars = axes[0].bar(sorted_count_data.keys(), sorted_count_data.values())
    for bar in bars:
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width() / 2, height + 50, f'{int(height)}', ha='center', va='bottom')
    axes[0].set_xlabel('country probed')
    axes[0].set_ylabel('probes completed')
    axes[0].set_title(time_spec)

    # bar chart on the ratio distribution of asns
    cns = sorted_count_data.keys()
    bottom = [0.0] * len(cns)
    for asn in asn2color.keys():
        ratios = [float(bar_data[cn].get(asn, 0)) / sorted_count_data[cn] for cn in cns]
        if sum(ratios) > 0:
            axes[1].bar(cns, ratios, bottom=bottom, label='\n->'.join(asn.split('->')), color=asn2color[asn])
            bottom = [b + v for b, v in zip(bottom, ratios)]
    axes[1].bar(cns, [1.0 - b for b in bottom], bottom=bottom, label='other', color=asn2color['other']) 
    axes[1].legend(title='asn', loc='center left', bbox_to_anchor=(1.01, 0.5), borderaxespad=0, frameon=False) 
    axes[1].set_xlabel('country probed')
    axes[1].set_ylabel('ASN proportion in inter-country path')
    axes[1].set_title(f'Inter-Country Link ASN distribution')
    plt.tight_layout()
    plt.close(fig)
    return fig

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True)
    parser.add_argument('--vp', type=str, default=None)
    parser.add_argument('--start_date', type=str, default='2024-01-30')
    parser.add_argument('--end_date', type=str, default='2024-03-25')
    parser.add_argument('--gap', type=int, default=1)
    parser.add_argument('--airport', type=str, default=None)
    parser.add_argument('--threshold', type=int, default=15)
    parser.add_argument('--supple_color', type=int, default=10)
    parser.add_argument('--primary_cmap', type=str, default='tab20')
    parser.add_argument('--supple_cmap', type=str, default='viridis')
    parser.add_argument('--label', type=str, default='maxmind')
    parser.add_argument('--front_as', action='store_true')

    args = parser.parse_args()
    pri_cmap = plt.get_cmap(args.primary_cmap)
    sup_cmap = plt.get_cmap(args.supple_cmap).resampled(args.supple_color)
    cmap_idx = 0
    asn2color = {}
    global_unique_asns = set()
    dates = generate_date_sequence(args.start_date, args.end_date, args.gap) 
    for date_str in dates:
        query_data = data[args.vp].get(f'{args.airport}({date_str})', None)
        if not query_data:
            print(f'unable to find {args.airport}({date_str}), skipping...')
            continue
        print(f'querying {args.airport}({date_str})...')
        cns = sorted(list(query_data.keys()))
        unique_asns = set()
        all_counters = {}
        filtered_query_data = {}
        for cn in cns:
            all_counts = sum(list(query_data[cn].values()))
            all_counters[cn] = float(all_counts)
            if args.front_as:
                processed_query_data = {}
                for k, v in query_data[cn].items():
                    mod_k = k.split('->')[0]
                    processed_query_data[mod_k] = processed_query_data.get(mod_k, 0) + query_data[cn][k]
            else:
                processed_query_data = query_data[cn]

            filtered_data = dict([(k, v) for k, v in processed_query_data.items() if v > (all_counts // args.threshold)])
            filtered_query_data[cn] = {}
            filtered_query_data[cn]['other'] = all_counts - sum(list(filtered_data.values()))
            filtered_query_data[cn].update(filtered_data)
            unique_asns = unique_asns.union(list(filtered_data.keys()))
        unique_asns = sorted(list(unique_asns))
        unique_asns.append('other')
        figs, axes = plt.subplots(2, 1, figsize=(15, 10))
        bars = axes[0].bar(all_counters.keys(), all_counters.values())
        for bar in bars:
            height = bar.get_height()
            axes[0].text(bar.get_x() + bar.get_width() / 2, height + 50, f'{int(height)}', ha='center', va='bottom')
        axes[0].set_xlabel('country probed')
        axes[0].set_ylabel('probes completed')
        axes[0].set_title(f'{args.airport}({args.vp}) on {date_str}: total probes to each country')
        bottom = [0.0] * len(cns)
        for idx, asn in enumerate(unique_asns):
            if asn not in asn2color:
                global_unique_asns.add(asn)
                if cmap_idx >= 20 + args.supple_color:
                    continue 
                c = pri_cmap(cmap_idx) if cmap_idx < 20 else sup_cmap(cmap_idx - 20)
                asn2color[asn] = c
                cmap_idx += 1
            else:
                c = asn2color[asn]
            values = [filtered_query_data[cn].get(asn, 0.0) for cn in cns]
            ratios = [float(filtered_query_data[cn].get(asn, 0.0)) / all_counters[cn] for cn in cns]
            axes[1].bar(cns, ratios, bottom=bottom, label='\n->'.join(asn.split('->')), color=c)
            bottom = [b + v for b, v in zip(bottom, ratios)]

        axes[1].legend(title='asn', loc='center left', bbox_to_anchor=(1.01, 0.5), borderaxespad=0, frameon=False) 
        axes[1].set_xlabel('country probed')
        axes[1].set_ylabel('ASN proportion in inter-country path')
        axes[1].set_title(f'Inter-Country Link ASN distribution')
        plt.tight_layout()
        plt.savefig(f'images/{vp_lab}-intercountry-asn/{args.airport}-{args.label}-{"" if not args.front_as else "front-as"}/{args.vp}-{args.airport}-{date_str}.png')
        plt.close()
   
    print(f'with a threshold of {args.threshold}, used {len(global_unique_asns)} colors')
   
 
