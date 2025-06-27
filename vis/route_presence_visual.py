import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse, json

def format_ip(ip_addr : str) -> tuple[int]:
    ip_addr = '.'.join(ip_addr.split('->'))
    return tuple(map(int, ip_addr.split('.')))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True)
    parser.add_argument('--threshold', type=int, default=-1)
    parser.add_argument('--unit', type=str, default='ip')
    parser.add_argument('--target', type=str, default='node')
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--filter', type=str, default='all')
    parser.add_argument('--start_time', type=str, default='xx')
    parser.add_argument('--end_time', type=str, default='xx')

    args = parser.parse_args()

    with open(args.input_dir, 'r') as f:
        data = json.load(f)

    
    # format the data to processed via pandas
    dates = data.keys()
    formatted_data = []
    for day in dates:
        for inst in data[day]:
            formatted_data.append({'date': day, 'node': inst['node'], 'count': inst['count']})

    df = pd.DataFrame(formatted_data)
    unique_ips_sorted = sorted(df['node'].unique(), key=(format_ip if args.unit == 'ip' else lambda x : x))
    df['node'] = pd.Categorical(df['node'], categories=unique_ips_sorted, ordered=True)
    pivot_df = df.pivot_table(index='node', columns='date', values='count', observed=False).fillna(0)

    if args.threshold == -1:
        presence_df = (pivot_df > 0).astype(int)
        
        plt.figure(figsize=(15 if args.target == 'node' else 20, 10 if args.target == 'node' else 15))
        ax = sns.heatmap(presence_df, cmap='Blues', cbar=False, linewidth=0.5, linecolor='lightgray')    
        ax.set_yticks(np.arange(len(presence_df.index)) + 0.5) # Positions of ticks (center of cells)
        ax.set_yticklabels(presence_df.index.tolist(), rotation=0, fontsize=10)
        plt.xticks(rotation=45, ha='right')
        plt.savefig(f'{args.output_dir}/{args.start_time}2{args.end_time}-{args.unit}-presence-heatmap-{args.target}.png')

    else:
        sorted_df = df.sort_values(by='count', ascending=False)
        top_ip_rows = sorted_df.drop_duplicates(subset='node').head(args.threshold)
        filtered_ips = top_ip_rows['node'].unique()
        filtered_ips_set = set(filtered_ips)
        filtered_df = df[df['node'].isin(filtered_ips_set)]    
        filtered_pivot_df = filtered_df.pivot_table(index='node', columns='date', values='count', observed=False).fillna(0)

        plt.figure(figsize=(15 if args.target == 'node' else 20, 10 if args.target == 'node' else 15))
        ax = sns.heatmap(filtered_pivot_df, cmap='Blues', cbar=True, linewidth=0.5, linecolor='lightgray')    
        ax.set_yticks(np.arange(len(filtered_pivot_df.index)) + 0.5) # Positions of ticks (center of cells)
        ax.set_yticklabels(filtered_pivot_df.index.tolist(), rotation=0, fontsize=10)
        plt.xticks(rotation=45, ha='right')
        plt.savefig(f'{args.output_dir}/{args.start_time}2{args.end_time}-{args.unit}-threshold-{args.threshold}-{args.target}-heatmap.png')

