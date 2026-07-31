# pages/03_demand.py — demand drill-down page (BBD squiggle level 3)
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters

# ─────────────────────────────────────────────────────────────────────────────
# Load data + shared sidebar — same filters, same filtered dataframe as
# pages 1 and 2, carried over via session_state.
# ─────────────────────────────────────────────────────────────────────────────
df, p95 = load_data()
filtered = sidebar_filters(df, p95)

st.title('Where Is Guest Demand Strongest?')
st.caption('Reviews per month as a proxy for demand | '
           f'{len(filtered):,} listings shown of {len(df):,} total')

# ─────────────────────────────────────────────────────────────────────────────
# A persisted widget of our own: focus on one room type.
# init once, keep alive across page switches, guard against a room type
# that's been filtered out by the sidebar since we last visited.
# ─────────────────────────────────────────────────────────────────────────────
room_options = sorted(df['room_type'].unique())
if 'sel_room' not in st.session_state:
    st.session_state.sel_room = room_options[0]
st.session_state.sel_room = st.session_state.sel_room  # keep alive across pages

rooms_avail = sorted(filtered['room_type'].unique())
if st.session_state.sel_room not in rooms_avail:       # guard: sidebar may have
    st.session_state.sel_room = rooms_avail[0]         # removed the saved choice

st.selectbox('Focus on a room type', rooms_avail, key='sel_room')
room = st.session_state.sel_room
room_df = filtered[filtered['room_type'] == room]

# ─────────────────────────────────────────────────────────────────────────────
# KPI row — 5-second test: the metrics alone answer "how strong is demand
# for this room type, relative to the filtered market?"
# ─────────────────────────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
k1.metric('Listings', f'{len(room_df):,}')
k2.metric('Median Reviews/Month', f"{room_df['reviews_per_month'].median():.2f}",
          f"{room_df['reviews_per_month'].median() - filtered['reviews_per_month'].median():+.2f} "
          'vs filtered market')
k3.metric('Median Price', f"£{room_df['price'].median():.0f}/night")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# One chart — demand story: price vs reviews/month, focused room type
# highlighted against the rest of the filtered market.
# BBD COLOUR TYPE: highlight — blue for the focused room type, grey recedes
# BBD CVD: blue vs grey — no red-green combination
# ─────────────────────────────────────────────────────────────────────────────
plot_df = filtered.copy()
plot_df['highlight'] = plot_df['room_type'].apply(
    lambda r: room if r == room else 'Other room types')

fig = px.scatter(plot_df, x='reviews_per_month', y='price', color='highlight',
                 color_discrete_map={room: '#2E75B6', 'Other room types': '#AAAAAA'},
                 category_orders={'highlight': ['Other room types', room]},
                 labels={'reviews_per_month': 'Reviews per Month (demand proxy)',
                         'price': 'Nightly Price (£)', 'highlight': ''},
                 title=f'{room} listings — where demand meets price')
fig.update_traces(marker=dict(size=8, opacity=0.75, line=dict(width=0)))
fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                  font=dict(family='Arial', size=12),
                  xaxis=dict(gridcolor='#EEEEEE'), yaxis=dict(gridcolor='#EEEEEE'),
                  legend=dict(orientation='h', y=1.08))
st.plotly_chart(fig, use_container_width=True)

# TEST: focus a room type, switch to page 1, change a filter, come back —
# both the sidebar filters AND this selection must be where you left them.
