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
    parser.add_argument('--input_dir', type=str, default='outputs/traceroute_le0_ip.json')
    parser.add_argument('--threshold', type=int, default=-1)
    parser.add_argument('--unit', type=str, default='ip_address')
    parser.add_argument('--target', type=str, default='node')

    args = parser.parse_args()

    with open(args.input_dir, 'r') as f:
        data = json.load(f)

    
    # format the data to processed via pandas
    dates = data.keys()
    formatted_data = []
    for day in dates:
        for inst in data[day]:
            formatted_data.append({'date': day, 'ip_address': inst['node'], 'count': inst['count']})

    df = pd.DataFrame(formatted_data)
    unique_ips_sorted = sorted(df['ip_address'].unique(), key=(format_ip if args.unit != 'asn' else lambda x : x))
    df['ip_address'] = pd.Categorical(df['ip_address'], categories=unique_ips_sorted, ordered=True)
    pivot_df = df.pivot_table(index='ip_address', columns='date', values='count', observed=False).fillna(0)

    if args.threshold == -1:
        presence_df = (pivot_df > 0).astype(int)
        
        plt.figure(figsize=(15 if args.target == 'node' else 20, 10 if args.target == 'node' else 15))
        sns.heatmap(presence_df, cmap='Blues', cbar=False, linewidth=0.5, linecolor='lightgray')    
        plt.yticks(rotation=0)
        plt.xticks(rotation=45, ha='right')
        plt.savefig(f'images/{args.unit}_presence_heatmap.png')

    else:
        filtered_df = df[df['count'] > args.threshold]    
        filtered_pivot_df = filtered_df.pivot_table(index='ip_address', columns='date', values='count', observed=False).fillna(0)

        plt.figure(figsize=(15 if args.target == 'node' else 20, 10 if args.target == 'node' else 15))
        ax = sns.heatmap(filtered_pivot_df, cmap='Blues', cbar=True, linewidth=0.5, linecolor='lightgray')    
        # plt.yticks(rotation=0, fontsize=3)
        ax.set_yticks(np.arange(len(filtered_pivot_df.index)) + 0.5) # Positions of ticks (center of cells)
        ax.set_yticklabels(filtered_pivot_df.index.tolist(), rotation=0, fontsize=10)
        plt.xticks(rotation=45, ha='right')
        plt.savefig(f'images/{args.unit}_threshold_{args.threshold}_{args.target}_heatmap.png')

