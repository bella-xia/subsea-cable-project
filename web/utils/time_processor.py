import os, json

def aggre_avail_data(in_dir, in_suffix, start, end):
    files = [f for f in os.listdir(in_dir) if f.endswith(in_suffix)]
    
    json_data = {}
    for f in files:
        with open(os.path.join(in_dir, f)) as in_f:
            json_data.update(json.load(in_f))
    
    return json_data
        
