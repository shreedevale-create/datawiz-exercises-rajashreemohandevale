#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ── STEP 6 (Class Exercise): Add a third chart using a DIVERGING colour scale ──
# something where values go above and below a meaningful midpoint
# Label the midpoint in an annotation.

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="World Happiness", page_icon="🌍", layout="wide")

df = pd.read_csv('data/world_happiness_2023.csv')
df.columns = ['Country','Region','Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

with st.sidebar:
    st.header("Filters")
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)

filtered = df if selected_region == 'All' else df[df['Region'] == selected_region]

st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# KPI row
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric("Avg Score", f"{filtered['Score'].mean():.2f}",
            f"{filtered['Score'].mean()-df['Score'].mean():+.2f} vs global")
col3.metric("Happiest", filtered.nlargest(1,'Score')['Country'].values[0])

st.divider()

# Two-column layout: Rankings (sequential) + Score vs GDP (highlight)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Rankings")
    top = filtered.nlargest(top_n, 'Score').sort_values('Score')

    fig1 = px.bar(top, x='Score', y='Country', orientation='h',
                  color_discrete_sequence=['#2E75B6'],
                  labels={'Score':'Score (0–10)','Country':''})

    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                        xaxis=dict(range=[0,8.5]), font=dict(family='Arial',size=12),
                        margin=dict(l=10,r=10,t=5,b=10))
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, width='stretch')

with col_right:
    st.subheader("Score vs GDP")
    fig2 = px.scatter(filtered, x='GDP', y='Score', hover_name='Country',
                       color_discrete_sequence=['#E63946'])
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(family='Arial',size=12),
                        margin=dict(l=10,r=10,t=5,b=10))
    st.plotly_chart(fig2, width='stretch')

st.divider()

# ── Third chart: DIVERGING colour scale ────────────────────────────────────
st.subheader("Happiness Score: Above vs Below Global Average")

# The meaningful midpoint here is the GLOBAL average score — every country
# either pulls the world average up or down, which is exactly what a
# diverging scale is for (two directions from a midpoint).
global_avg = df['Score'].mean()

diverge = filtered.nlargest(top_n, 'Score').copy()
diverge['Deviation'] = diverge['Score'] - global_avg
diverge = diverge.sort_values('Deviation')

# BBD COLOUR TYPE: diverging — red below the global average, blue above it,
# white at zero (i.e. exactly average).
fig3 = px.bar(diverge, x='Deviation', y='Country', orientation='h',
              color='Deviation',
              color_continuous_scale='RdBu',
              color_continuous_midpoint=0,
              labels={'Deviation': 'Happiness Score vs Global Average', 'Country': ''})

fig3.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                    font=dict(family='Arial', size=12),
                    xaxis=dict(gridcolor='#EEEEEE', zeroline=True,
                               zerolinecolor='black', zerolinewidth=1.5),
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=10, t=40, b=10))
fig3.update_traces(marker_line_width=0)

# Label the midpoint (x = 0 == the global average score) directly on the chart
fig3.add_annotation(x=0, y=1.06, yref='paper', showarrow=False,
                     text=f"Global average = {global_avg:.2f}",
                     font=dict(size=12, color='black'))

st.plotly_chart(fig3, width='stretch')

st.divider()
st.caption("Built with Streamlit + Plotly")
