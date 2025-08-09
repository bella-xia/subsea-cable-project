import streamlit as st
from utils.constants import DATA_ROOT_DIR, META_DIR
from utils.utils import reset_page
import os, datetime

def render_primary_realtime():
    cns = [f.split('.')[0].split('-')[-1] for f in os.listdir(f'{DATA_ROOT_DIR}/{META_DIR}')]
    names = [st.session_state.iso2cn.get(cn, 'unknown') + f'-{cn}' for cn in cns]
    select_cat = st.selectbox(
            'statistics category',
            ('Preliminary data', 'Cross-Country ASNs', 'IP Utilization Heatmap', 'IP Hop Connectivity Graph', 'IP Traceroute Changes Classification Method'),
            index=None,
            placeholder='select a category of interest',
            on_change=reset_page)

    select_src, select_dst = None, None
    select_start, select_end, select_contiguous = None, None, None
    if select_cat and len(names) > 0:
        select_src = st.selectbox(
                'vantage point', tuple(names), index=None,
                placeholder='select a vantage point', on_change=reset_page)
        select_dst = st.selectbox(
                'probe destination', tuple(names), index=None,
                placeholder='select a destination', on_change=reset_page)
    
        if select_cat not in ['Cross-Country ASNs', 'IP Hop Connectivity Graph']:
            select_start = st.date_input('statistics start time', datetime.date(2024, 11, 1))
            select_end = st.date_input('statistics end time', datetime.date(2024, 12, 31))
            if select_cat != 'IP Traceroute Changes Classification Method':
                select_contiguous = st.checkbox('contiguous dates')

    return select_cat, select_src, select_dst, select_start, select_end, select_contiguous
