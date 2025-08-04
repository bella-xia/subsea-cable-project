import os, random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from .utils.generate_series import parse_hopdata, parse_iplink
from .utils.iplink_vis import render_topip

def calculate_cusum(dist_arr, original_inst=False, top_k=5):
    x_avg = np.mean(dist_arr)
    cusum_arr = [0]
    for ts, count in enumerate(dist_arr):
        s_i = cusum_arr[-1] + (count - x_avg)
        cusum_arr.append(s_i)
    indices = [idx for idx in range(len(cusum_arr))]
    indices = sorted(indices, key = lambda x : abs(cusum_arr[x]), reverse=True)
    return (max(cusum_arr) -  min(cusum_arr), indices[:top_k])

def bootstrap_cusum(dist_arr, num_bootstrap = 500):
    original_cusum, shifts = calculate_cusum(dist_arr, original_inst=True)
    num_g = 0
    for _ in range(num_bootstrap):
        dist_arr_cp = dist_arr.copy()
        random.shuffle(dist_arr_cp)
        random_cusum, _ = calculate_cusum(dist_arr_cp)
        if random_cusum > original_cusum:
            num_g += 1
    return (num_g / num_bootstrap, shifts)

def bootstrap_cusum_processor(input_dir, start, end, aggre=False, spec='25th',
                              disp_iplink=False, iplink_input_dir=""):
    
    dates, dts, hop_data = parse_hopdata(input_dir, start, end, aggre, spec)
    
    if disp_iplink:
        fig, axes = plt.subplots(2, 1, sharex=True, figsize=(15, 10))
        ax = axes[0]
    else:
        fig, ax = plt.subplots(figsize=(15, 8))

    if aggre:
        ax.plot(dts, hop_data, marker='o', zorder=1)
    else:
        ax.scatter(dts, hop_data, marker='x', alpha=0.5, zorder=1)
    pval, shifts = bootstrap_cusum(hop_data)
    ret_dates = set()
    if pval < 0.05:
        ax.scatter([dts[i] for i in shifts], [hop_data[i] for i in shifts], color='red', zorder=3)
        if aggre:
            ret_dates.update([dts[i] for i in shifts])
        else:
            ret_dates.update([dts[i].date() for i in shifts])
    
    if not disp_iplink:
        ax.set_xticks(dates)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.setp(ax.get_xticklabels(), rotation=90, ha='right')
 
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    
    if disp_iplink:
        stats, aggre = parse_iplink(iplink_input_dir, start, end)
        render_topip(stats, aggre, axes[1])

        for i in shifts:
            axes[1].axvline(dts[i], color='red', linestyle=':', alpha=0.5)
        
    plt.tight_layout()
    plt.close(fig)
    return list(ret_dates), fig

