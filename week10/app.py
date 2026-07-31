#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")

# ── Sidebar: 5 widgets ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)

    # Chained filter: Region narrows the Country list
    if selected_region == 'All':
        country_options = sorted(df['Country'].unique().tolist())
    else:
        country_options = sorted(df[df['Region'] == selected_region]['Country'].unique().tolist())
    selected_countries = st.multiselect("Countries", country_options, default=country_options[:3])

    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    date_range = st.date_input("Date range", value=(min_date, max_date),
                                min_value=min_date, max_value=max_date)

    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])

    highlight_top = st.checkbox("Show only top emitter highlighted")

if not selected_countries:
    st.warning("Select at least one country.")
    st.stop()

if not isinstance(date_range, tuple) or len(date_range) != 2:
    st.warning("Select a start and end date.")
    st.stop()

start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Date'] >= start_date) &
    (df['Date'] <= end_date)
]

y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'
y_label = 'CO2 Emissions (Mt)' if y_col == 'CO2_Mt' else 'CO2 per Capita'

# ── Filter summary caption ────────────────────────────────────────────────────
# BBD rule: always show users how many records match current filters
st.caption(f"{len(selected_countries)} countries | {selected_region} | "
           f"{start_date.date()}–{end_date.date()} | {metric}")

last_year = filtered['Year'].max()
first_year = filtered['Year'].min()
latest = filtered[filtered['Year'] == last_year].sort_values(y_col)
top_emitter = latest.iloc[-1]['Country'] if not latest.empty else None

# ── Extension: KPI row ────────────────────────────────────────────────────────
total_last = latest[y_col].sum()
total_first = filtered.loc[filtered['Year'] == first_year, y_col].sum()
pct_change = ((total_last - total_first) / total_first * 100) if total_first else 0

k1, k2, k3 = st.columns(3)
k1.metric(f"Total {metric} ({int(last_year)})", f"{total_last:,.2f}")
k2.metric(f"Change {int(first_year)}→{int(last_year)}", f"{pct_change:+.1f}%")
k3.metric("Top emitter", top_emitter or "—")

st.divider()

# ── Two charts reacting to all filters ────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    # BBD COLOUR TYPE: categorical (one hue per country); switches to
    # grey-and-highlight when the checkbox isolates the top emitter.
    fig1 = px.line(filtered, x='Year', y=y_col, color='Country',
                   labels={y_col: y_label},
                   title=f'{metric} over time')
    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(family='Arial', size=12),
                        margin=dict(l=10, r=10, t=40, b=10))

    if highlight_top and top_emitter:
        for trace in fig1.data:
            if trace.name == top_emitter:
                trace.line.color = '#E63946'
                trace.line.width = 3
            else:
                trace.line.color = '#CCCCCC'
                trace.line.width = 1
                trace.showlegend = False

        top_row = filtered[(filtered['Country'] == top_emitter) & (filtered['Year'] == last_year)]
        if not top_row.empty:
            fig1.add_annotation(x=last_year, y=top_row[y_col].values[0],
                                 text=top_emitter, showarrow=False,
                                 xanchor='left', xshift=8,
                                 font=dict(color='#E63946', size=12))

    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    # BBD COLOUR TYPE: highlight — single colour, focus on the ranking itself
    fig2 = px.bar(latest, x=y_col, y='Country', orientation='h',
                  color_discrete_sequence=['#2E75B6'],
                  labels={y_col: y_label, 'Country': ''},
                  title=f'Ranking – {int(last_year)}')
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(family='Arial', size=12),
                        xaxis=dict(range=[0, latest[y_col].max() * 1.15]),
                        margin=dict(l=10, r=10, t=40, b=10))
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.caption("Built with Streamlit + Plotly")
