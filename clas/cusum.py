import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from .utils.generate_series import parse_hopdata, parse_iplink
from .utils.iplink_vis import render_topip

def estimate_params(window, d_factor=0.5, h_factor=2.0):
    mu_0, std = np.mean(window), np.std(window)
    std = std if std > 0.01 else 0.01
    drift_k, h_thres = d_factor * std, h_factor * std
    return mu_0, drift_k, h_thres

def two_sided_cusum(data_arr, win_size, mu_0=None, drift_k=None, h_thres=None,
                       dynamic=True):
    
    if not mu_0 or not drift_k or not h_thres:
        mu_0, drift_k, h_thres = estimate_params(data_arr[:win_size])

    pos_c, neg_c, pos_prev, neg_prev = 0, 0, 0, 0
    pos_alerts, neg_alerts = [], []
    pos_cs, neg_cs, mus = [], [], []
    
    for idx, inst in enumerate(data_arr):
        pos_prev, neg_prev = pos_c, neg_c
        pos_c = max(0, pos_c + (inst - mu_0 - drift_k))
        neg_c = min(0, neg_c + (inst - mu_0 + drift_k))
        
        pos_cs.append(pos_c)
        neg_cs.append(neg_c)
        mus.append(mu_0)
        
        if pos_c > h_thres or abs(neg_c) > h_thres:
    
            if pos_c > h_thres:
                pos_alerts.append((idx, inst, pos_c))
                pos_c = 0

            if abs(neg_c) > h_thres:
                neg_alerts.append((idx, inst, neg_c))
                neg_c = 0

            if dynamic:
                if idx + win_size <= len(data_arr):
                    mu_0, drift_k, h_thres = estimate_params(data_arr[idx:idx+win_size])
   

    return {
        'baseline': mus,
        'pos_alerts': pos_alerts,
        'neg_alerts': neg_alerts,
        'pos_series': pos_cs,
        'neg_series': neg_cs
    }

def cusum_processor(input_dir, start, end, aggre=True, spec='25th',
                    disp_iplink=False, iplink_input_dir=""):
   
    dates, dts, hop_data = parse_hopdata(input_dir, start, end, aggre, spec)
    
    if disp_iplink:
        fig, axes = plt.subplots(2, 1, sharex=True, figsize=(15, 10))
        ax1 = axes[0]
    else:
        fig, ax1 = plt.subplots(figsize=(15, 8))

    res = two_sided_cusum(hop_data, 5 if aggre else 50)
    
    if aggre:
        ax1.plot(dts, hop_data, label='hop number', color='gray', marker='o', zorder=1)
    else:
        ax1.scatter(dts, hop_data, label='hop number', color='gray', marker='x', alpha=0.5, zorder=1)

    ax1.plot(dts, res['baseline'], color='green', label='baseline', linestyle=':', zorder=2)
    ret_dates = set()
    if res['pos_alerts']:
        pos_ids, pos_vals, _ = zip(*res['pos_alerts'])
        ax1.scatter([dts[i] for i in pos_ids], pos_vals, color='red', label='Level Shift (pos)', zorder=3)
        if aggre:
            ret_dates.update([dts[i] for i in pos_ids])
        else:
            ret_dates.update([dts[i].date() for i in pos_ids])
    if res['neg_alerts']:
        neg_ids, neg_vals, _ = zip(*res['neg_alerts'])
        ax1.scatter([dts[i] for i in neg_ids], neg_vals, color='blue', label='Level Shift (neg)', zorder=4)
        if aggre:
            ret_dates.update([dts[i] for i in neg_ids])
        else:
            ret_dates.update([dts[i].date() for i in neg_ids])
    ax1.legend(loc='upper left')
    if not disp_iplink:
        ax1.set_xticks(dates)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.setp(ax1.get_xticklabels(), rotation=90, ha='right')
 
    ax2 = ax1.twinx()
    ax2.plot(dts, res['pos_series'], color='red', label='pos c', linestyle=':')
    ax2.plot(dts, res['neg_series'], color='blue', label='neg c', linestyle=':')
    ax2.legend(loc='upper right')

    if disp_iplink:
        stats, aggre = parse_iplink(iplink_input_dir, start, end)
        render_topip(stats, aggre, axes[1])
        if res['pos_alerts']:
            pos_ids, pos_vals, _ = zip(*res['pos_alerts'])
            for i in pos_ids:
                axes[1].axvline(dts[i], color='red', linestyle=':', alpha=0.5)

        if res['neg_alerts']:
            neg_ids, neg_vals, _ = zip(*res['neg_alerts'])
            for i in neg_ids:
                axes[1].axvline(dts[i], color='blue', linestyle=':', alpha=0.5)
    
    fig.tight_layout()        
    plt.close(fig)
    return list(ret_dates), fig
