import argparse, json, statistics, random, gzip, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from datetime import datetime
from scipy.signal import find_peaks

def calculate_cusum(dist_arr, original_inst=False, top_k=3):
    x_avg = statistics.mean(dist_arr)
    cusum_arr = [0]
    for ts, count in enumerate(dist_arr):
        s_i = cusum_arr[-1] + (count - x_avg)
        cusum_arr.append(s_i)
    indices = [idx for idx in range(len(cusum_arr))]
    indices = sorted(indices, key = lambda x : abs(cusum_arr[x]), reverse=True)
    return (max(cusum_arr) -  min(cusum_arr), indices[:top_k])

def bootstrap_CUSUM(dist_arr, num_bootstrap = 500):
    original_CUSUM, shifts = calculate_cusum(dist_arr, original_inst=True)
    num_g = 0
    for _ in range(num_bootstrap):
        dist_arr_cp = dist_arr.copy()
        random.shuffle(dist_arr_cp)
        random_CUSUM, _ = calculate_cusum(dist_arr_cp)
        if random_CUSUM > original_CUSUM:
            num_g += 1
    return (num_g / num_bootstrap, shifts)

def topip_cusum_processor(input_dir, start, end, mode='top_r', top_r=5, top_k=5):
    with open(input_dir, 'r') as f:
       data = json.load(f)
    
    stats, aggre = {}, set()
    all_dates = list(data.keys())

    for k, v in data.items():
        for item in v:
            stats.setdefault(item['node'], {})
            stats[item['node']][k] = item['count']

        sorted_node = sorted(v, key=lambda x : x['count'], reverse=True)
        if mode == 'top_k':
            sorted_node = sorted_node[:top_k]
        elif mode == 'top_r':
            num_extracted = int(len(sorted_node) * top_r / 100)
            sorted_node = sorted_node[:num_extracted]

        aggre.update([item['node'] for item in sorted_node])

    fig, ax = plt.subplots(figsize=(12,6))
    for node in list(aggre):
        ts_raw = sorted(stats[node].items(), key=lambda x : x[0])
        ts_raw = {k : v for (k, v) in ts_raw}
        ts_data = [ts_raw.get(k, 0) for k in all_dates]
        pval, ts = bootstrap_CUSUM(ts_data)
        if pval < 0.05:
            ax.plot(all_dates, ts_data, label=f'{node}', alpha=0.6)
            ax.axvline(all_dates[ts[0]], color='red', linestyle='--', alpha=0.2)
   
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.tick_params(axis='x', rotation=90)
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),
        title="Nodes", borderaxespad=0, fontsize='small') 
    plt.tight_layout()
    plt.close()
    return fig

def hopnum_cusum_processor(input_dir, start, end):
    start_dt = datetime.combine(start, datetime.min.time()).replace(tzinfo=None)
    end_dt = datetime.combine(end, datetime.min.time()).replace(tzinfo=None)
    data_aggre = []
    with open(input_dir, 'r') as f:
        data = json.load(f)
    dts, hop_data = [], []
    fig, ax = plt.subplots(figsize=(12,6))
    for item in data:
        dt = datetime.fromisoformat(item['datetime']).replace(tzinfo=None)
        if dt < start_dt:
            continue
        if dt > end_dt:
            break
        dts.append(dt)
        hop_data.append(item['hop-num'])
    pval, shifts = bootstrap_CUSUM(hop_data)
    ax.scatter(dts, hop_data, marker='x', alpha=0.5)
    if pval < 0.05:
        for ts in shifts:
            ax.axvline(dts[ts], linestyle='--', alpha=0.2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    plt.tight_layout()
    plt.close(fig)
    return fig

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_prefix', type=str, required=True)
    parser.add_argument('--top_k', type=int, default=5) # perform CUSUM on top 5 ip addresses per day
    parser.add_argument('--top_r', type=int, default=5) 
    parser.add_argument('--mode', type=str, default='top_r')
    parser.add_argument('--start', type=str, default='24-01-30')
    parser.add_argument('--end', type=str, default='24-03-03')
    args = parser.parse_args()

  
