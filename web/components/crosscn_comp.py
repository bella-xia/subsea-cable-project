import streamlit as st
import os, json
from utils.constants import ROOT_DIR, ASN_SUBDIR, DATA_ROOT_DIR, SRC2ALL_CROSSCN
from utils.utils import reset_page
from .reusable_comp import render_button


def render_crosscn_asn_img(select_src):
    if not select_src:
        return

    vp = select_src.split('-')[1]
    img_dir = f'{ROOT_DIR}/{ASN_SUBDIR}/{vp}-crosscn-asn'
    airport_set = set()
    for f in os.listdir(img_dir):
        airport_set.add(f.split('-')[0])

    select_airport = st.selectbox(
        'selected airport',
        tuple(airport_set),
        index=0,
        placeholder='select an airport',
        on_change=reset_page)
    img_dir += f'/{select_airport}-{vp}-maxmind-front-as'
    imgs =  sorted(os.listdir(img_dir))
    st.image(os.path.join(img_dir, imgs[st.session_state.img_idx]), use_container_width=True)
    render_button(len(imgs))

def render_crosscn_asn_realtime(select_src, processor):
    if not select_src or not processor:
        return

    vp = select_src.split('-')[1]
    img_dir = f'{DATA_ROOT_DIR}/{SRC2ALL_CROSSCN}'
    
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

        

