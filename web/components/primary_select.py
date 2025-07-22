import streamlit as st
from utils.constants import ROOT_DIR
from utils.utils import reset_page
import os, datetime

def render_primary():
    lev1_files = os.listdir(ROOT_DIR)
    select_cat = st.selectbox(
            'statistics category',
            ('Preliminary data', 'Cross-Country ASNs', 'IP Utilization Heatmap', 'IP Hop Connectivity Graph', 'IP Traceroute Changes Classification Method'),
            index=None,
            placeholder='select a category of interest',
            on_change=reset_page)

    select_src, select_dst = None, None
    select_start, select_end, select_contiguous = None, None, None
    if select_cat:
        lev2_files = [f for f in lev1_files if (f != 'crosscn-asns' and f != 'classification')]
        src_set, dst_set = set(), set()
        for f in lev2_files:
            f_arr = f.split('2')
            if st.session_state.iso2cn.get(f_arr[0], None):
                src_set.add(f"{st.session_state.iso2cn[f_arr[0]]}-{f_arr[0]}")
            if st.session_state.cn2iso.get(f_arr[1], None):
                dst_set.add(f"{f_arr[1]}-{st.session_state.cn2iso[f_arr[1]]}")

        select_src = st.selectbox(
                'vantage point', tuple(src_set), index=None,
                placeholder='select a vantage point', on_change=reset_page) if src_set else None
        select_dst = st.selectbox(
                'probe destination', tuple(dst_set), index=None,
                placeholder='select a destination', on_change=reset_page) if dst_set else None
    
        if select_cat not in ['Cross-Country ASNs', 'IP Hop Connectivity Graph']:
            select_start = st.date_input('statistics start time', datetime.date(2024, 1, 30))
            select_end = st.date_input('statistics end time', datetime.date(2024, 3, 30))
            select_contiguous = st.checkbox('contiguous dates')

    return select_cat, select_src, select_dst, select_start, select_end, select_contiguous





