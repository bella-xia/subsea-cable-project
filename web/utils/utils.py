import streamlit as st
import pandas as pd
import os, re
from .constants import STATS_SUBFIX

def next_page():
    st.session_state.img_idx += 1

def prev_page():
    st.session_state.img_idx -=  1

def reset_page():
    st.session_state.img_idx = 0

def toggle_zoom():
    st.session_state.page_config = (
        'centered' if st.session_state.page_config == 'wide' else 'wide'
    )

def extract_stats_images(img_dir):
    img_dict = {}
    img_dict.setdefault('Stop Hop Reasons', [])
    for img in (os.listdir(img_dir) if os.path.exists(img_dir) else []):
        for k, v in STATS_SUBFIX.items():
            if img.endswith(v):
                if k == 'Stop Hop Reasons':
                    img_dict[k].append(os.path.join(img_dir, img))
                else:
                    img_dict[k] = os.path.join(img_dir, img)
    return img_dict


def define_iso(iso_dir):
    if 'iso2cn' not in st.session_state:
        iso_data = pd.read_csv(iso_dir)
        iso_data = iso_data[~iso_data['alpha-2'].isna()]
        iso2cn = {iso_data.iloc[i]['alpha-2'].lower() : re.sub(r'\s', r'', iso_data.iloc[i]['name'].lower()) for i in range(len(iso_data)) }
        iso2cn['uk'] = 'unitedkingdom'
        cn2iso = {v : k for k, v in iso2cn.items()}
        st.session_state['iso2cn'] = iso2cn
        st.session_state['cn2iso'] = cn2iso
    

