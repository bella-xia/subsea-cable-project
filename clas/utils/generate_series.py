import json
import numpy as np
from datetime import datetime

def parse_hopdata(input_dir, start, end, aggre, spec):
    start_dt = datetime.combine(start, datetime.min.time()).replace(tzinfo=None)
    end_dt = datetime.combine(end, datetime.min.time()).replace(tzinfo=None)
    dates = set()
 
    with open(input_dir, 'r') as f:
        data = json.load(f)
    data = sorted(data, key=lambda x : datetime.fromisoformat(x['datetime']))
    dts, hop_data = [], []

    if not aggre:
        for item in data:
            dt = datetime.fromisoformat(item['datetime']).replace(tzinfo=None)
            if dt < start_dt:
                continue
            if dt > end_dt:
                break
            dts.append(dt)
            dates.add(dt.date())
            hop_data.append(item['hop-num'])

        return list(dates), dts, hop_data
    
    buf = []
    for item in data:
        dt = datetime.fromisoformat(item['datetime']).replace(tzinfo=None)
        if dt < start_dt:
            continue
        if dt > end_dt:
            break
        dt = dt.date()
        dates.add(dt)
        if len(dts) == 0:
            dts.append(dt)
            buf.append(item['hop-num'])
        elif dt == dts[-1]:
            buf.append(item['hop-num'])
        else:
            if len(buf) == 0:
                dts[-1] = dt
                continue

            dts.append(dt)
            buf_arr = np.array(buf)
            
            if spec == 'min':
                hop_data.append(min(buf))
            elif spec == 'max':
                hop_data.append(max(buf))
            elif spec == 'avg':
                hop_data.append(int(np.mean(buf_arr)))
            else:
                q25, q50, q75 = np.percentile(buf_arr, [25, 50, 75])

                if spec == 'q25':
                    hop_data.append(int(q25))
                elif spec == 'q75':
                    hop_data.append(int(q75))
                elif spec == 'med':
                    hop_data.append(int(q50))
                else:
                    raise Exception('unimplemented statistics')
            buf = []

    if len(buf) > 0:
        buf_arr = np.array(buf)
        
        if spec == 'min':
            hop_data.append(min(buf))
        elif spec == 'max':
            hop_data.append(max(buf))
        elif spec == 'avg':
            hop_data.append(int(np.mean(buf_arr)))
        else:
            q25, q50, q75 = np.percentile(buf_arr, [25, 50, 75])

            if spec == 'q25':
                hop_data.append(int(q25))
            elif spec == 'q75':
                hop_data.append(int(q75))
            elif spec == 'med':
                hop_data.append(int(q50))
            else:
                raise Exception('unimplemented statistics')

    return sorted(list(dates)), dts, hop_data


def parse_iplink(input_dir, start, end, 
                mode='top_k', top_r=5, top_k=5):
    start_dt = datetime.combine(start, datetime.min.time()).replace(tzinfo=None)
    end_dt = datetime.combine(end, datetime.min.time()).replace(tzinfo=None)

    with open(input_dir, 'r') as f:
       data = json.load(f)
    
    stats, aggre = {}, set()
    counter = {}

    for k, v in data.items():
        dt = datetime.strptime(k, '%y-%m-%d').replace(tzinfo=None)
        if dt < start_dt:
            continue
        if dt > end_dt:
            break
        for item in v:
            stats.setdefault(item['node'], {})
            stats[item['node']][dt] = item['count']

        sorted_node = sorted(v, key=lambda x : x['count'], reverse=True)
        if mode == 'top_k':
            sorted_node = sorted_node[:top_k]
        elif mode == 'top_r':
            num_extracted = int(len(sorted_node) * top_r / 100)
            sorted_node = sorted_node[:num_extracted]
        
        for item in sorted_node:
            aggre.add(item['node'])
            counter[item['node']] = counter.get(item['node'], 0) + item['count']

    aggre = sorted(list(aggre), key=lambda x : counter.get(x, 0), reverse=True)

    return stats, aggre
