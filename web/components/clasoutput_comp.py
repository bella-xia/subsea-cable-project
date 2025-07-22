import streamlit as st
import os
from utils.constants import ROOT_DIR, CLASSIFICATION_SUBDIR, DATA_ROOT_DIR, SRC2DST_RAW, SRC2DST_JSON, SRC2DST_GRAPH, SRC2DST_PRELIM
from utils.utils import reset_page, extract_stats_images
from .reusable_comp import render_button

def render_clasout_img(select_src, select_dst):
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

def render_clasout_realtime(select_src, select_dst, select_start, select_end, select_method, processor):
    if not select_src or not select_dst or not select_start or not select_end or not select_method or not processor:
        return
    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[1]
    if select_method == 'hop number level shift':
        img_dir = f'{DATA_ROOT_DIR}/{SRC2DST_PRELIM}/{vp}2{dst}.json'
        if not os.path.exists(img_dir):
            st.write(f'cannot find hop statistics data from {vp} to {dst} in {DATA_ROOT_DIR}/{SRC2DST_PRELIM}')
        else:
            fig = processor(img_dir, select_start, select_end)
            st.pyplot(fig)
    elif select_method == 'ip link level shift':
        img_dir = f'{DATA_ROOT_DIR}/{SRC2DST_JSON}'
        ref = None
        for data in os.listdir(img_dir):
            if data.startswith(f'{vp}2{dst}_crosscn_edge'):
                ref = data
                break
        if not ref:
            st.write(f'cannot find cross-country IP Link data from {vp} to {dst} in {img_dir}')
        else:
            fig = processor(os.path.join(img_dir, ref), select_start, select_end)
            st.pyplot(fig)
    elif select_method == 'fordeian matrix distance':
        img_dir = f'{DATA_ROOT_DIR}/{SRC2DST_GRAPH}/{vp}2{dst}'
        fig = processor(img_dir)
        st.pyplot(fig)
    elif select_method == 'kl and js divergence':
        img_prefix = f'{DATA_ROOT_DIR}/{SRC2DST_JSON}/{vp}2{dst}'
        fig = processor(img_prefix)
        st.pyplot(fig)
