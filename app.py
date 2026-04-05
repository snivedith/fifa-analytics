"""
app.py  —  FIFA Analytics Dashboard
Dark professional theme — all text visible
Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from scripts.data_loader import load_data, preprocess_data
from scripts.analytics import (
    top_rated_players,
    nationality_distribution,
    overall_by_position,
    age_vs_overall,
    most_valuable_clubs,
    growth_potential_players,
)

st.set_page_config(
    page_title="FIFA Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Plotly chart defaults (dark background, white text) ──────────────────────
CHART = dict(
    paper_bgcolor="#1E293B",
    plot_bgcolor="#1E293B",
    font=dict(family="Arial", color="#FFFFFF", size=13),
    margin=dict(l=10, r=20, t=40, b=20),
    height=420,
)

def style(fig):
    fig.update_layout(**CHART)
    fig.update_xaxes(tickfont=dict(color="#FFFFFF", size=12), gridcolor="#334155")
    fig.update_yaxes(tickfont=dict(color="#FFFFFF", size=12), gridcolor="#334155")
    return fig

BLUE_SCALE = ["#1E3A8A","#1D4ED8","#3B82F6","#60A5FA","#BAE6FD"]

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading FIFA dataset…")
def get_data():
    return preprocess_data(load_data())

try:
    df_full = get_data()
except Exception as e:
    st.error(str(e))
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚽ FIFA Analytics")
    st.markdown("---")

    st.subheader("Overall Rating")
    rating_range = st.slider("Rating", int(df_full.overall.min()), 99, (60, 99), label_visibility="collapsed")

    st.subheader("Age Range")
    age_range = st.slider("Age", int(df_full.age.min()), int(df_full.age.max()), (16, 45), label_visibility="collapsed")

    st.subheader("Position Group")
    all_positions = sorted(df_full["position_group"].dropna().unique().tolist())
    positions = st.multiselect("Position", all_positions, default=all_positions, label_visibility="collapsed")

    st.subheader("Preferred Foot")
    foot_options = ["Both"] + sorted(df_full["preferred_foot"].dropna().unique().tolist())
    preferred_foot = st.selectbox("Foot", foot_options, label_visibility="collapsed")

    st.markdown("---")
    st.caption(f"Dataset: {len(df_full):,} players")

# ── Filters ───────────────────────────────────────────────────────────────────
df = df_full.copy()
df = df[(df["overall"] >= rating_range[0]) & (df["overall"] <= rating_range[1])]
df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]
if positions:
    df = df[df["position_group"].isin(positions)]
if preferred_foot != "Both":
    df = df[df["preferred_foot"] == preferred_foot]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# ⚽ FIFA Player Analytics")
st.markdown(f"**{len(df):,} players** found with current filters")
st.markdown("---")

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Players",  f"{len(df):,}")
k2.metric("Avg Overall",    f"{df['overall'].mean():.1f}")
k3.metric("Avg Age",        f"{df['age'].mean():.1f}")
k4.metric("Avg Value",      f"€{df['value_m'].mean():.1f}M")
k5.metric("Nations",        f"{df['nationality_name'].nunique()}")

st.markdown("---")

# ── Row 1 ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top Rated Players")
    top_n = st.slider("Number of players to show", 5, 30, 15, key="top_n")
    top_df = top_rated_players(df, n=top_n)
    fig1 = px.bar(
        top_df, x="overall", y="short_name", orientation="h",
        color="overall", color_continuous_scale=BLUE_SCALE,
        hover_data=["club_name", "nationality_name", "primary_position"],
        labels={"overall": "Rating", "short_name": "Player"},
        title="Players by Overall Rating"
    )
    fig1.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    style(fig1)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🌍 Players by Nation")
    nat_df = nationality_distribution(df, top_n=20)
    fig2 = px.bar(
        nat_df, x="player_count", y="nationality", orientation="h",
        color="player_count", color_continuous_scale=BLUE_SCALE,
        labels={"player_count": "Players", "nationality": "Country"},
        title="Top 20 Nations by Player Count"
    )
    fig2.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    style(fig2)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Row 2 ─────────────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("📈 Age vs. Average Rating")
    age_df = age_vs_overall(df)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=age_df["age"], y=age_df["avg_overall"],
        fill="tozeroy", fillcolor="rgba(59,130,246,0.15)",
        line=dict(color="#3B82F6", width=2.5),
        mode="lines+markers",
        marker=dict(color="#3B82F6", size=5),
        name="Avg Rating"
    ))
    fig3.update_layout(
        title="Player Rating by Age",
        xaxis_title="Age",
        yaxis_title="Avg Overall Rating"
    )
    style(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("⚡ Attributes by Position")
    pos_df = overall_by_position(df)
    blues = ["#1D4ED8","#3B82F6","#60A5FA","#93C5FD","#BFDBFE"]
    fig4 = go.Figure()
    for i, attr in enumerate(["pace","shooting","passing","defending","physic"]):
        if attr in pos_df.columns:
            fig4.add_trace(go.Bar(
                name=attr.capitalize(),
                x=pos_df["position_group"],
                y=pos_df[attr],
                marker_color=blues[i],
            ))
    fig4.update_layout(
        barmode="group",
        title="Key Attributes by Position",
        legend=dict(font=dict(color="#FFFFFF"))
    )
    style(fig4)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── Row 3 ─────────────────────────────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("💰 Most Valuable Squads")
    clubs_df = most_valuable_clubs(df, top_n=15)
    if clubs_df["total_value_m"].sum() > 0:
        fig5 = px.bar(
            clubs_df, x="total_value_m", y="club_name", orientation="h",
            color="total_value_m", color_continuous_scale=BLUE_SCALE,
            labels={"total_value_m": "Total Value (€M)", "club_name": "Club"},
            title="Top 15 Clubs by Squad Value"
        )
        fig5.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    else:
        club_ovr = (
            df.groupby("club_name")["overall"]
            .mean().round(1).sort_values(ascending=False)
            .head(15).reset_index()
            .rename(columns={"overall": "avg_overall"})
        )
        fig5 = px.bar(
            club_ovr, x="avg_overall", y="club_name", orientation="h",
            color="avg_overall", color_continuous_scale=BLUE_SCALE,
            labels={"avg_overall": "Avg Rating", "club_name": "Club"},
            title="Top 15 Clubs by Avg Overall Rating"
        )
        fig5.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    style(fig5)
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("🌱 Rising Stars (Age ≤ 23)")
    min_ovr = st.slider("Min current overall rating", 55, 80, 65, key="rising_min")
    rising_df = growth_potential_players(df, min_overall=min_ovr, n=20)
    if len(rising_df) > 0:
        fig6 = px.scatter(
            rising_df, x="overall", y="potential",
            size="growth", color="growth",
            color_continuous_scale=BLUE_SCALE,
            hover_data=["short_name", "age", "club_name", "primary_position"],
            labels={"overall": "Current Rating", "potential": "Potential Rating"},
            title="Young Players with Highest Growth Potential"
        )
        fig6.update_traces(marker_line_color="#1E293B", marker_line_width=1)
        style(fig6)
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("No rising stars found. Try lowering the minimum overall rating.")

st.markdown("---")

# ── Data Table ────────────────────────────────────────────────────────────────
st.subheader("📋 Player Data Table")
show_cols = [c for c in ["short_name","age","nationality_name","club_name",
             "primary_position","overall","potential","value_m","wage_k","preferred_foot"]
             if c in df.columns]

search = st.text_input("🔍 Search by player name", placeholder="e.g. Messi, Ronaldo…")
display_df = df[show_cols].copy()
if search:
    display_df = display_df[display_df["short_name"].str.contains(search, case=False, na=False)]

st.dataframe(
    display_df.sort_values("overall", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=400,
)
st.caption("Source: FIFA Player Dataset · Kaggle")
