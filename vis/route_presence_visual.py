import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse, json
from utils.date_processing import generate_date_sequence

def format_ip(ip_addr : str) -> tuple[int]:
    ip_addr = '.'.join(ip_addr.split('->'))
    return tuple(map(int, ip_addr.split('.')))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True)
    parser.add_argument('--threshold', type=int, default=40)
    parser.add_argument('--mode', type=str, default='density')
    parser.add_argument('--unit', type=str, default='ip')
    parser.add_argument('--target', type=str, default='node')
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--start_time', type=str, default='xx')
    parser.add_argument('--end_time', type=str, default='xx')
    parser.add_argument('--contiguous', type=str, default='False')

    args = parser.parse_args()
    contiguous_flag = True if args.contiguous == 'True' else False
    if contiguous_flag and (args.start_time == 'xx' or args.end_time == 'xx'):
        print('expected contiguous dates but do not specify range')
    output_prefix = f'({args.start_time})2({args.end_time})_{args.unit}'
    if contiguous_flag:
        output_prefix += '_contiguous'

    with open(args.input_dir, 'r') as f:
        data = json.load(f)
    
    dates = data.keys()
    dates = list(sorted(dates))
    if args.start_time != 'xx':
        while dates[0] < args.start_time:
            dates = dates[1:]
    if args.end_time != 'xx':
        while dates[-1] > args.end_time:
            dates = dates[:-1]
    formatted_data = []
    for day in dates:
        for inst in data[day]:
            formatted_data.append({'date': day, 'node': inst['node'], 'count': inst['count']})

    df = pd.DataFrame(formatted_data)
    # unique_ips_sorted = sorted(df['node'].unique(), key=(format_ip if args.unit == 'ip' else lambda x : x))
    # df['node'] = pd.Categorical(df['node'], categories=unique_ips_sorted, ordered=True)
    # pivot_df = df.pivot_table(index='node', columns='date', values='count', observed=False).fillna(0)
    sorted_df = df.sort_values(by='count', ascending=False)
    top_ip_rows = sorted_df.drop_duplicates(subset='node').head(args.threshold)
    filtered_ips = top_ip_rows['node'].unique()
    filtered_ips_set = set(filtered_ips)
    filtered_df = df[df['node'].isin(filtered_ips_set)]    
    filtered_pivot_df = filtered_df.pivot_table(index='node', columns='date', values='count', observed=False).fillna(0)
    if contiguous_flag:
        contiguous_dates = generate_date_sequence(args.start_time, args.end_time)
        filtered_pivot_df = filtered_pivot_df.reindex(columns=contiguous_dates, fill_value=0)

    if args.mode == 'presence' or args.mode == 'both':
        presence_df = (filtered_pivot_df > 0).astype(int)
        plt.figure(figsize=(15 if args.target == 'node' else 20, 10 if args.target == 'node' else 15))
        ax = sns.heatmap(presence_df, cmap='Blues', cbar=False, linewidth=0.5, linecolor='lightgray')    
        ax.set_yticks(np.arange(len(presence_df.index)) + 0.5) 
        ax.set_yticklabels(presence_df.index.tolist(), rotation=0, fontsize=10)
        plt.xticks(rotation=45, ha='right')
        plt.savefig(f'{args.output_dir}/{output_prefix}_presence_heatmap_{args.target}.png')

    if args.mode == 'density' or args.mode == 'both':
        plt.figure(figsize=(15 if args.target == 'node' else 20, 10 if args.target == 'node' else 15))
        ax = sns.heatmap(filtered_pivot_df, cmap='Blues', cbar=True, linewidth=0.5, linecolor='lightgray')    
        ax.set_yticks(np.arange(len(filtered_pivot_df.index)) + 0.5) # Positions of ticks (center of cells)
        ax.set_yticklabels(filtered_pivot_df.index.tolist(), rotation=0, fontsize=10)
        plt.xticks(rotation=45, ha='right')
        plt.savefig(f'{args.output_dir}/{output_prefix}_threshold_{args.threshold}_{args.target}_heatmap.png')

