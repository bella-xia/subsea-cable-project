import streamlit as st
import os, sys
from utils.constants import STATS_ROOT_DIR, SRC2DST_RAW, SRC2DST_JSON, SRC2DST_GRAPH, SRC2DST_PRELIM
from .reusable_comp import savefig_button

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from clas.ewma import ewma_processor
from clas.cusum import cusum_processor
from clas.glr_cusum import glr_cusum_processor
from clas.bootstrap_cusum import bootstrap_cusum_processor

PROCESSOR_DICT = {
    'EWMA': ewma_processor,
    'CUSUM': cusum_processor,
    'GLR CUSUM': glr_cusum_processor,
    'bootstrap CUSUM': bootstrap_cusum_processor,
}
def render_clasout_realtime(select_src, select_dst, select_start, select_end):
    if not select_src or not select_dst or not select_start or not select_end:
        return
    vp = select_src.split('-')[1]
    dst = select_dst.split('-')[1]
    start_str = select_start.strftime('%m-%d')
    end_str = select_end.strftime('%m-%d')
    fig_prefix = f'{vp}2{dst}-{start_str}-to-{end_str}'

    hopnum_dir = f'{STATS_ROOT_DIR}/{SRC2DST_PRELIM}/{vp}2{dst}.json' 
    iplink_dir = f'{STATS_ROOT_DIR}/{SRC2DST_JSON}/{vp}2{dst}_crosscn_edge.json'

    select_method = st.pills('select classification method', list(PROCESSOR_DICT.keys()))
   
    if not select_method:
        return

    aggre = st.toggle('show aggregative statistics', value=True)
    disp_iplink = st.toggle('show ip link correspondence', value=False)

    select_spec = None
    if aggre:
        select_spec=st.segmented_control('select the statistics of interest', ('avg', 'med', 'max', 'min', 'q25', 'q75'), default='q25')
        if not select_spec:
            return

    ret_dates, fig = PROCESSOR_DICT[select_method](hopnum_dir, select_start, select_end, aggre=aggre, spec=select_spec, disp_iplink=disp_iplink, iplink_input_dir=iplink_dir)

    savefig_button(fig, fig_prefix, f'clas_hopnum_{"raw" if aggre else "stats"}_{select_method}_{select_spec if aggre else ""}.png')
    st.pyplot(fig)
    date_str = ', '.join([d.strftime("%m-%d") for d in sorted(ret_dates)])
    st.write(f'algorithm classifies {len(ret_dates)} instances of level shifts, happening respectively on:')
    st.write(date_str)
