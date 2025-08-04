import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from .utils.generate_series import parse_hopdata, parse_iplink
from .utils.iplink_vis import render_topip

def L_fn(theta, s_n, n, sigma):
    return theta * s_n - (n * sigma ** 2 * theta ** 2) / 2 # log-likelihood difference, measures how much more likely the data is under the alternate hypothesis (mean = θ) compared to the null (mean = 0)

def two_sided_glr_cusum(data, win_size, theta_min=0.5, h=2.0):
    s_n, n = 0.0, 0
    points = []
    stat_history = []
    mle_thetas = []
    mu_0, sigma = np.mean(data[:win_size]), np.std(data[:win_size])
    sigma = sigma if sigma > 0.01 else 0.01
    for idx, x in enumerate(data):
        s_n += x - mu_0 # cusum
        n += 1 
        theta_hat = s_n / (n * sigma ** 2) # maximum likelihood estimate (MLE) of the unknown mean θ, assuming that sigma is constant and known
        mle_thetas.append(theta_hat)
        if abs(theta_hat) > theta_min:
            test_stat = L_fn(theta_hat, s_n, n, sigma)  
        else:
            test_stat = max(L_fn(theta_min, s_n, n, sigma), L_fn(-theta_min, s_n, n, sigma))
        stat_history.append(test_stat)
        if test_stat > h:
            points.append((idx, test_stat))
            s_n, n = 0.0, 0
            if len(data) > idx + win_size:
                mu_0, sigma = np.mean(data[idx:idx+win_size]), np.std(data[idx:idx+win_size])
                sigma = sigma if sigma > 0.1 else 0.1
        # print('[s_n, x, theta_hat, test_stat]=', s_n, x, theta_hat, test_stat)
    return {'points': points, 'stats': stat_history, 'thetas': mle_thetas}

def glr_cusum_processor(input_dir, start, end, aggre=True, spec='25th',
                        disp_iplink=False, iplink_input_dir=""):

    dates, dts, hop_data = parse_hopdata(input_dir, start, end, aggre, spec)
    data = two_sided_glr_cusum(hop_data, 5 if aggre else 50)
    points = data['points']

    if disp_iplink:
        fig, axes = plt.subplots(2, 1, sharex=True, figsize=(15, 10))
        ax1 = axes[0]
    else:
        fig, ax1 = plt.subplots(figsize=(15, 8))

    if aggre:
        ax1.plot(dts, hop_data, label='hop number', color='gray', marker='o', zorder=1)
    else:
        ax1.scatter(dts, hop_data, label='hop number', color='gray', marker='x', alpha=0.5, zorder=1)
    
    ax1.scatter([dts[i[0]] for i in points], [hop_data[i[0]]  for i in points], color='red', zorder=3)
    if aggre:
        ret_dates = [dts[i[0]] for i in points]
    else:
        ret_dates = list(set([dts[i[0]].date() for i in points]))
    ax1.set_ylabel('hop count')
    ax1.legend(loc='upper left')

    if not disp_iplink:
        ax1.set_xticks(dates)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.setp(ax1.get_xticklabels(), rotation=90, ha='right')
 
    ax2 = ax1.twinx()
    ax2.plot(dts, data['stats'], label='Log-likelyhood', linestyle=':')
    ax2.plot(dts, data['thetas'], label='estimated mle', linestyle=':')
    ax2.set_ylabel('GLR Stats / MLE')
    ax2.legend(loc='upper right')

    if disp_iplink:
        stats, aggre = parse_iplink(iplink_input_dir, start, end)
        render_topip(stats, aggre, axes[1])
        
        for i in points:
            axes[1].axvline(dts[i[0]], color='red', linestyle=':', alpha=0.5)
 

    fig.tight_layout()
    plt.close(fig)
    return ret_dates, fig

