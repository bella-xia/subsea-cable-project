import streamlit as st
import os, json
from utils.constants import STATS_ROOT_DIR, SRC2ALL_CROSSCN
from utils.utils import reset_page
from .reusable_comp import render_button

def render_crosscn_asn_realtime(select_src, processor):
    if not select_src or not processor:
        return

    vp = select_src.split('-')[1]
    img_dir = f'{STATS_ROOT_DIR}/{SRC2ALL_CROSSCN}'
    
    ref = None
    if os.path.exists(img_dir):
        for f in os.listdir(img_dir):
            if f.startswith(f'{vp}2'):
                ref = f
                break
    if not ref:
        st.write(f'no graph data available for {vp}2all at {img_dir}')
        return
    
    full_path = os.path.join(img_dir, ref)
    with open(full_path, 'r') as f:
        data = json.load(f)

    airports = [k for k in data.keys() if k != 'sorted-asn']
    select_airport = st.segmented_control("airport specs", airports, default=airports[0], selection_mode='single')
    sub_data = data[select_airport]
    avail_dates = sorted(sub_data.keys())
    fig = processor(full_path, avail_dates[st.session_state.img_idx], select_airport)
    st.pyplot(fig)
    render_button(len(avail_dates))

        

