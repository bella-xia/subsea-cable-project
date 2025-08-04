import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from .utils.generate_series import parse_hopdata, parse_iplink
from .utils.iplink_vis import render_topip

def ewma(data_arr, win_size, lam_factor=0.2, control_limit=3, mu_0=None, dynamic=True):
    
    if not mu_0:
        mu_0, std = np.mean(data_arr[:win_size]), np.std(data_arr[:win_size])
        std = std if std > 0.1 else 0.1
   
    z = mu_0
    n = 0
    pos_alerts, neg_alerts = [], []
    ucls, lcls, mus = [], [], []

    for idx, inst in enumerate(data_arr):
        z = lam_factor * inst + (1 - lam_factor) * z
        multiplier = np.sqrt(lam_factor / (2 - lam_factor) * (1 - (1 - lam_factor) ** (2 * (n + 1))))
        ucl = mu_0 + control_limit * std * multiplier
        lcl = mu_0 - control_limit * std * multiplier
        ucls.append(ucl)
        lcls.append(lcl)
        mus.append(mu_0)

        if z > ucl or z < lcl:
            if z > ucl:
                pos_alerts.append((idx, inst, ucl))
            if z < lcl:
                neg_alerts.append((idx, inst, lcl))

            if idx + win_size <= len(data_arr):
                mu_0, std = np.mean(data_arr[idx:idx+win_size]), np.std(data_arr[idx:idx+win_size])
                std = std if std > 0.01 else 0.01
                z = mu_0
                n = -1
        n += 1

    return {
        'baseline': mus,
        'pos_alerts': pos_alerts,
        'neg_alerts': neg_alerts,
        'ucl_series': ucls,
        'lcl_series': lcls,
    }

def ewma_processor(input_dir, start, end, aggre=True, spec='25th',
                   disp_iplink=False, iplink_input_dir=""):
    
    dates, dts, hop_data = parse_hopdata(input_dir, start, end, aggre, spec)
    
    if disp_iplink:
        fig, axes = plt.subplots(2, 1, sharex=True, figsize=(15, 10))
        ax = axes[0]
    else:
        fig, ax = plt.subplots(figsize=(15, 8))
    res = ewma(hop_data, 5 if aggre else 50)
    
    if aggre:
        ax.plot(dts, hop_data, label='hop number', color='gray', marker='o', zorder=1)
    else:
        ax.scatter(dts, hop_data, label='hop number', color='gray', marker='x', alpha=0.5, zorder=1)

    ax.plot(dts, res['baseline'], color='green', label='baseline', linestyle=':', zorder=2)
    ax.plot(dts, res['ucl_series'], color='red', label='upper bound', linestyle=':', zorder=3)
    ax.plot(dts, res['lcl_series'], color='blue', label='lower bound', linestyle=':', zorder=4)
    ret_dates = set()
    if res['pos_alerts']:
        pos_ids, pos_vals, _ = zip(*res['pos_alerts'])
        ax.scatter([dts[i] for i in pos_ids], pos_vals, color='red', label='Level Shift (pos)', zorder=5)
        if aggre:
            ret_dates.update([dts[i] for i in pos_ids])
        else:
            ret_dates.update([dts[i].date() for i in pos_ids])
    if res['neg_alerts']:
        neg_ids, neg_vals, _ = zip(*res['neg_alerts'])
        ax.scatter([dts[i] for i in neg_ids], neg_vals, color='blue', label='Level Shift (neg)', zorder=6)
        if aggre:
            ret_dates.update([dts[i] for i in neg_ids])
        else:
            ret_dates.update([dts[i].date() for i in neg_ids])
    if not disp_iplink:
        ax.set_xticks(dates)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.setp(ax.get_xticklabels(), rotation=90, ha='right')
 
    ax.legend()

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
