import streamlit as st
import os
from utils.constants import ROOT_DIR, CLASSIFICATION_SUBDIR
from utils.utils import reset_page, extract_stats_images
from .reusable_comp import render_button


def render_classification(select_src, select_dst):
    if not select_src or not select_dst:
        return

    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[0]
    img1_path = f'{ROOT_DIR}/{CLASSIFICATION_SUBDIR}/{vp}2{dst}_traceroutes_ip_dist_divergence.png'
    img2_path = f'{ROOT_DIR}/{CLASSIFICATION_SUBDIR}/{vp}2{dst}_frobenius_dist.png'
    binary_heatmap = st.toggle('with heatmap', on_change=reset_page)
    if not binary_heatmap:
        res = (st.image(img1_path, caption='Distribution Divergence') if os.path.exists(img1_path) else st.markdown(f'no data from {vp} to {dst}'))
        res = (st.image(img2_path, caption='Frobenius Distance on Graph') if os.path.exists(img2_path) else st.markdown(f'no data from {vp} to {dst}'))
    else:
        col1, col2 = st.columns(2)
        with col1:
            res = (st.image(img1_path, caption='Distribution Divergence') if os.path.exists(img1_path) else st.markdown(f'no data from {vp} to {dst}'))
            res = (st.image(img2_path, caption='Frobenius Distance on Graph') if os.path.exists(img2_path) else st.markdown(f'no data from {vp} to {dst}'))

        with col2:
            img_dict = extract_stats_images(f'images/{vp}2{dst}')
            img_used = []
            label_used = [] 
            for lab in ['IP Link Presence', 'IP Link Density', 'Cross-country IP Link Presence','Cross-country IP Link Density']:
                if img_dict.get(lab, None):
                    img_used.append(img_dict[lab])
                    label_used.append(lab)
            res = (st.image(img_used[st.session_state.img_idx], caption=label_used[st.session_state.img_idx]) if len(img_used) > 0 else st.markdown('no heatmap available'))
            render_button(len(img_used))
