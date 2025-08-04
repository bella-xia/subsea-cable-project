import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.dates as mdates
import numpy as np
from datetime import timedelta

def render_topip(stats, aggre, ax, mode='top_k', top_r=5, top_k=5):
    
    n = len(aggre)
    colors = {}

    # First 20 colors from tab20
    tab20 = cm.get_cmap('tab20', 20)
    for i, node in enumerate(aggre[:20]):
        colors[node] = tab20(i)

    if n > 20:
        terrain = cm.get_cmap('terrain')
        gradient_indices = np.linspace(0, 1, n - 20)
        for i, node in enumerate(aggre[20:], start=0):
            colors[node] = terrain(gradient_indices[i])
    
    dates = set()
    for node in aggre:
        ts_raw = sorted(stats[node].items(), key=lambda x : x[0])
        ts_raw = {k : v for (k, v) in ts_raw}
        dates.update([k.date() for k in ts_raw.keys()])
        k, v = list(ts_raw.keys()), list(ts_raw.values())
        i, starter = 0, 0
        for i in range(len(ts_raw)):
           if i > 0 and k[i] - k[i-1] > timedelta(days=1):
               ax.plot(k[starter:i], v[starter:i], color=colors[node])
               starter = i
        ax.plot(k[starter:], v[starter:], color=colors[node], label=f'{node}')
    
    ax.set_xticks(list(dates))
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.setp(ax.get_xticklabels(), rotation=90, ha='right')
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),
        title="Nodes", borderaxespad=0, fontsize='small') 
