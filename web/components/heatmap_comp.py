import streamlit as st
from utils.utils import extract_stats_images

def render_heatmap(select_src, select_dst):
    if not select_src or not select_dst:
        return
    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[0]
    img_dir = f'images/{vp}2{dst}'
    img_dict = extract_stats_images(img_dir)
    select_type = st.segmented_control("IP spec", ('IP Address', 'IP Link', 'Cross-country IP Link'), selection_mode='single')
    select_spec = st.segmented_control("heatmap type", ("Presence", "Density"), selection_mode='single')
    if select_type and select_spec:
        key = f'{select_type} {select_spec}'
        img = img_dict.get(key, None)
        res = (st.image(img) if img else st.markdown('no data available'))                   
 
