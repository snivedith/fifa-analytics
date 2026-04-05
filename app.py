"""
app.py  —  FIFA 22 Analytics Dashboard
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

# ─── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FIFA 22 Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Theme colours ────────────────────────────────────────────────────────────
GREEN  = "#00d26a"
DARK   = "#0a0a0a"
CARD   = "#141414"
MUTED  = "#888888"

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500&display=swap');
  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background: {DARK}; color: #f0f0f0; }}
  h1,h2,h3 {{ font-family: 'Syne', sans-serif; }}
  .stApp {{ background: {DARK}; }}
  section[data-testid="stSidebar"] {{ background: #0f0f0f; border-right: 1px solid #1e1e1e; }}
  .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
  div[data-testid="metric-container"] {{
      background: {CARD}; border: 1px solid #1e1e1e;
      border-radius: 10px; padding: 1rem 1.2rem;
  }}
  div[data-testid="metric-container"] label {{ color: {MUTED}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: .08em; }}
  div[data-testid="metric-container"] [data-testid="metric-value"] {{ color: {GREEN}; font-family: 'Syne', sans-serif; font-size: 1.8rem; }}
  .stDataFrame {{ border-radius: 10px; overflow: hidden; }}
  footer, #MainMenu {{ visibility: hidden; }}
  .section-label {{
      font-family: 'Syne', sans-serif; font-size: 0.7rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: .15em;
      color: {GREEN}; margin-bottom: .5rem;
  }}
</style>
""", unsafe_allow_html=True)

# ─── Chart helper — consistent dark theme ─────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#cccccc", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#1e1e1e", zerolinecolor="#1e1e1e"),
    yaxis=dict(gridcolor="#1e1e1e", zerolinecolor="#1e1e1e"),
    colorway=[GREEN, "#00a854", "#007a3d", "#004d25", "#b3ffe0"],
)

def apply_theme(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ─── Load data ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading FIFA dataset…")
def get_data():
    df = load_data()          # downloads automatically — no CSV needed
    return preprocess_data(df)

try:
    df_full = get_data()
except ConnectionError as e:
    st.error(str(e))
    st.stop()


# ─── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ FIFA 22")
    st.markdown("---")

    st.markdown('<div class="section-label">Overall Rating</div>', unsafe_allow_html=True)
    rating_range = st.slider("", int(df_full.overall.min()), 99, (75, 99), label_visibility="collapsed")

    st.markdown('<div class="section-label">Age Range</div>', unsafe_allow_html=True)
    age_range = st.slider(" ", int(df_full.age.min()), int(df_full.age.max()), (16, 40), label_visibility="collapsed")

    st.markdown('<div class="section-label">Position Group</div>', unsafe_allow_html=True)
    all_positions = sorted(df_full["position_group"].dropna().unique().tolist())
    positions = st.multiselect("", all_positions, default=all_positions, label_visibility="collapsed")

    st.markdown('<div class="section-label">Preferred Foot</div>', unsafe_allow_html=True)
    foot_options = ["Both"] + sorted(df_full["preferred_foot"].dropna().unique().tolist())
    preferred_foot = st.selectbox("", foot_options, label_visibility="collapsed")

    st.markdown("---")
    st.caption(f"Dataset: {len(df_full):,} players total")

# ─── Apply filters ────────────────────────────────────────────────────────────
df = df_full.copy()
df = df[(df["overall"] >= rating_range[0]) & (df["overall"] <= rating_range[1])]
df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]
if positions:
    df = df[df["position_group"].isin(positions)]
if preferred_foot != "Both":
    df = df[df["preferred_foot"] == preferred_foot]


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("# FIFA 22 Player Analytics")
st.markdown(f"<span style='color:{MUTED}'>Exploring {len(df):,} players after filters</span>", unsafe_allow_html=True)
st.markdown("---")


# ─── KPI row ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Players", f"{len(df):,}")
k2.metric("Avg Overall", f"{df['overall'].mean():.1f}")
k3.metric("Avg Age", f"{df['age'].mean():.1f}")
k4.metric("Avg Value", f"€{df['value_m'].mean():.1f}M")
k5.metric("Nations", f"{df['nationality_name'].nunique()}")

st.markdown("---")


# ─── Row 1: Top Players + Nationality Map ─────────────────────────────────────
col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown("### 🏆 Top Rated Players")
    top_n = st.slider("Show top N players", 5, 30, 15, key="top_n")
    top_df = top_rated_players(df, n=top_n)

    fig = px.bar(
        top_df, x="overall", y="short_name", orientation="h",
        color="overall", color_continuous_scale=["#004d25", GREEN],
        hover_data=["club_name", "nationality_name", "primary_position", "value_m"],
        labels={"overall": "Rating", "short_name": ""},
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False, title="")
    apply_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 🌍 Players by Nation")
    nat_df = nationality_distribution(df, top_n=20)
    fig2 = px.bar(
        nat_df, x="player_count", y="nationality", orientation="h",
        color="player_count", color_continuous_scale=["#004d25", GREEN],
        labels={"player_count": "Players", "nationality": ""},
    )
    fig2.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    apply_theme(fig2)
    st.plotly_chart(fig2, use_container_width=True)


# ─── Row 2: Age curve + Position breakdown ────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown("### 📈 Age vs. Average Rating")
    age_df = age_vs_overall(df)
    fig3 = px.line(
        age_df, x="age", y="avg_overall",
        labels={"age": "Age", "avg_overall": "Avg Overall Rating"},
        markers=True,
    )
    fig3.update_traces(line_color=GREEN, marker_color=GREEN, line_width=2.5)
    apply_theme(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("### ⚡ Attribute Breakdown by Position")
    pos_df = overall_by_position(df)
    attr_cols = ["pace", "shooting", "passing", "defending", "physic"]

    fig4 = go.Figure()
    colors = [GREEN, "#00a854", "#007a3d", "#b3ffe0", "#004d25"]
    for i, attr in enumerate(attr_cols):
        fig4.add_trace(go.Bar(
            name=attr.capitalize(),
            x=pos_df["position_group"],
            y=pos_df[attr],
            marker_color=colors[i % len(colors)],
        ))
    fig4.update_layout(barmode="group", legend=dict(orientation="h", y=1.1))
    apply_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)


# ─── Row 3: Richest clubs + Rising stars ─────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.markdown("### 💰 Most Valuable Squads")
    clubs_df = most_valuable_clubs(df)
    fig5 = px.bar(
        clubs_df, x="total_value_m", y="club_name", orientation="h",
        color="total_value_m", color_continuous_scale=["#004d25", GREEN],
        labels={"total_value_m": "Total Value (€M)", "club_name": ""},
    )
    fig5.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    apply_theme(fig5)
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.markdown("### 🌱 Rising Stars (≤23, High Potential)")
    min_ovr = st.slider("Min current overall", 60, 85, 70, key="rising_min")
    rising_df = growth_potential_players(df, min_overall=min_ovr, n=15)

    fig6 = px.scatter(
        rising_df, x="overall", y="potential",
        size="growth", color="growth",
        color_continuous_scale=["#004d25", GREEN],
        hover_data=["short_name", "age", "club_name", "primary_position"],
        labels={"overall": "Current Rating", "potential": "Potential Rating"},
    )
    fig6.update_traces(marker_line_color=DARK, marker_line_width=1)
    apply_theme(fig6)
    st.plotly_chart(fig6, use_container_width=True)


# ─── Data Table ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Player Data Table")

show_cols = ["short_name", "age", "nationality_name", "club_name",
             "primary_position", "overall", "potential", "value_m", "wage_k", "preferred_foot"]
search = st.text_input("🔍 Search by player name", placeholder="e.g. Messi, Ronaldo…")

display_df = df[show_cols].copy()
if search:
    display_df = display_df[display_df["short_name"].str.contains(search, case=False, na=False)]

st.dataframe(
    display_df.sort_values("overall", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=380,
)

st.caption("Source: FIFA 22 Complete Player Dataset — Kaggle (stefanoleone992)")
