"""
app.py  —  FIFA Analytics Dashboard
Design: Blue & Professional (Corporate)
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
    page_title="FIFA Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Theme ────────────────────────────────────────────────────────────────────
BLUE       = "#1D4ED8"
BLUE_LIGHT = "#3B82F6"
DARK       = "#0F172A"
SLATE      = "#1E293B"
MUTED      = "#64748B"
WHITE      = "#F8FAFC"
BLUE_SCALE = ["#DBEAFE", "#93C5FD", "#3B82F6", "#1D4ED8", "#1E3A8A"]

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: {WHITE};
      color: {DARK} !important;
  }}
  .stApp {{ background-color: {WHITE}; }}

  /* Fix all general text to be dark and visible */
  p, span, div, label {{ color: {DARK} !important; }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{ background-color: {DARK}; }}
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span,
  section[data-testid="stSidebar"] div,
  section[data-testid="stSidebar"] label {{ color: #CBD5E1 !important; }}
  section[data-testid="stSidebar"] h2 {{ color: white !important; }}

  /* Slider labels */
  .stSlider label, .stSlider p {{ color: {DARK} !important; font-weight: 600; }}
  .stSlider [data-testid="stTickBarMin"],
  .stSlider [data-testid="stTickBarMax"] {{ color: {MUTED} !important; }}

  /* Selectbox and multiselect labels */
  .stSelectbox label, .stMultiSelect label {{ color: {DARK} !important; font-weight: 600; }}

  /* Text input */
  .stTextInput label {{ color: {DARK} !important; font-weight: 600; }}
  .stTextInput input {{ color: {DARK} !important; background: white; border: 1px solid #E2E8F0; }}

  /* Metric cards */
  div[data-testid="metric-container"] {{
      background: white; border: 1px solid #E2E8F0;
      border-top: 3px solid {BLUE}; border-radius: 8px;
      padding: 1.2rem 1.4rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  div[data-testid="metric-container"] label {{
      color: {MUTED} !important; font-size: 0.72rem; font-weight: 600;
      text-transform: uppercase; letter-spacing: 0.08em;
  }}
  div[data-testid="metric-container"] [data-testid="metric-value"] {{
      color: {DARK} !important; font-family: 'IBM Plex Mono', monospace;
      font-size: 1.75rem; font-weight: 600;
  }}

  /* Section titles */
  .section-title {{
      font-size: 0.85rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.12em; color: {BLUE} !important; margin-bottom: 0.6rem;
  }}

  /* Page header banner */
  .page-header {{
      background: linear-gradient(135deg, {DARK} 0%, {SLATE} 100%);
      border-radius: 12px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
  }}
  .page-header h1 {{ color: white !important; margin: 0; font-size: 2rem !important; }}
  .page-header p {{ color: #94A3B8 !important; margin: 0.3rem 0 0 0; font-size: 0.95rem; }}

  /* Dataframe */
  .stDataFrame {{ border-radius: 8px; }}

  /* Caption */
  .stCaption {{ color: {MUTED} !important; }}

  footer, #MainMenu {{ visibility: hidden; }}
  .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}
</style>
""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#F8FAFC",
    plot_bgcolor="#F8FAFC",
    font=dict(family="Plus Jakarta Sans", color="#0F172A", size=13),
    margin=dict(l=10, r=20, t=40, b=20),
    height=420,
)

def apply_theme(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    # Force all axis text to dark on every chart
    fig.update_xaxes(
        tickfont=dict(color="#0F172A", size=13),
        titlefont=dict(color="#0F172A", size=13),
        title_standoff=10,
    )
    fig.update_yaxes(
        tickfont=dict(color="#0F172A", size=13),
        titlefont=dict(color="#0F172A", size=13),
        title_standoff=10,
    )
    return fig

# ─── Load data ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading FIFA dataset…")
def get_data():
    df = load_data()
    return preprocess_data(df)

try:
    df_full = get_data()
except (ConnectionError, ValueError) as e:
    st.error(str(e))
    st.stop()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ FIFA Analytics")
    st.markdown("<hr style='border-color:#1E293B'>", unsafe_allow_html=True)

    st.markdown("**Overall Rating**")
    rating_range = st.slider("", int(df_full.overall.min()), 99, (60, 99), label_visibility="collapsed")

    st.markdown("**Age Range**")
    age_range = st.slider(" ", int(df_full.age.min()), int(df_full.age.max()), (16, 45), label_visibility="collapsed")

    st.markdown("**Position Group**")
    all_positions = sorted(df_full["position_group"].dropna().unique().tolist())
    positions = st.multiselect("", all_positions, default=all_positions, label_visibility="collapsed")

    st.markdown("**Preferred Foot**")
    foot_options = ["Both"] + sorted(df_full["preferred_foot"].dropna().unique().tolist())
    preferred_foot = st.selectbox("", foot_options, label_visibility="collapsed")

    st.markdown("<hr style='border-color:#1E293B'>", unsafe_allow_html=True)
    st.caption(f"Total players in dataset: {len(df_full):,}")

# ─── Apply filters ────────────────────────────────────────────────────────────
df = df_full.copy()
df = df[(df["overall"] >= rating_range[0]) & (df["overall"] <= rating_range[1])]
df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]
if positions:
    df = df[df["position_group"].isin(positions)]
if preferred_foot != "Both":
    df = df[df["preferred_foot"] == preferred_foot]

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <h1>⚽ FIFA Player Analytics</h1>
    <p>Exploring <strong style="color:white">{len(df):,} players</strong> · Use the sidebar to filter</p>
</div>
""", unsafe_allow_html=True)

# ─── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Players",  f"{len(df):,}")
k2.metric("Avg Overall",    f"{df['overall'].mean():.1f}")
k3.metric("Avg Age",        f"{df['age'].mean():.1f}")
k4.metric("Avg Value",      f"€{df['value_m'].mean():.1f}M")
k5.metric("Nations",        f"{df['nationality_name'].nunique()}")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Row 1: Top Players + Nations ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">🏆 Top Rated Players</div>', unsafe_allow_html=True)
    top_n = st.slider("Number of players", 5, 30, 15, key="top_n")
    top_df = top_rated_players(df, n=top_n)
    fig1 = px.bar(
        top_df, x="overall", y="short_name", orientation="h",
        color="overall", color_continuous_scale=BLUE_SCALE,
        hover_data=["club_name", "nationality_name", "primary_position"],
        labels={"overall": "Rating", "short_name": ""},
        title="Players ranked by Overall Rating"
    )
    fig1.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    apply_theme(fig1)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">🌍 Players by Nation (Top 20)</div>', unsafe_allow_html=True)
    nat_df = nationality_distribution(df, top_n=20)
    fig2 = px.bar(
        nat_df, x="player_count", y="nationality", orientation="h",
        color="player_count", color_continuous_scale=BLUE_SCALE,
        labels={"player_count": "Number of Players", "nationality": ""},
        title="Top 20 Nations by Player Count"
    )
    fig2.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    apply_theme(fig2)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ─── Row 2: Age curve + Position ──────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-title">📈 Age vs. Average Rating</div>', unsafe_allow_html=True)
    age_df = age_vs_overall(df)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=age_df["age"], y=age_df["avg_overall"],
        fill="tozeroy", fillcolor="rgba(29,78,216,0.08)",
        line=dict(color=BLUE, width=2.5),
        mode="lines+markers",
        marker=dict(color=BLUE, size=5),
        name="Avg Rating"
    ))
    fig3.update_layout(
        title="How player ratings change with age",
        xaxis_title="Age", yaxis_title="Avg Overall Rating"
    )
    apply_theme(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown('<div class="section-title">⚡ Attributes by Position</div>', unsafe_allow_html=True)
    pos_df = overall_by_position(df)
    blues = ["#1D4ED8", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"]
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
        title="Key attributes by player position",
        legend=dict(orientation="h", y=1.15, font=dict(size=11))
    )
    apply_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ─── Row 3: Clubs + Rising Stars ──────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="section-title">💰 Most Valuable Squads</div>', unsafe_allow_html=True)
    clubs_df = most_valuable_clubs(df, top_n=15)
    if clubs_df["total_value_m"].sum() > 0:
        fig5 = px.bar(
            clubs_df, x="total_value_m", y="club_name", orientation="h",
            color="total_value_m", color_continuous_scale=BLUE_SCALE,
            labels={"total_value_m": "Total Squad Value (€M)", "club_name": ""},
            title="Top 15 clubs by total squad market value"
        )
        fig5.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        apply_theme(fig5)
        st.plotly_chart(fig5, use_container_width=True)
    else:
        # Fallback: show clubs by average overall instead
        st.info("Market value data not available — showing clubs by average overall rating instead.")
        club_ovr = (
            df.groupby("club_name")["overall"]
            .mean().round(1).sort_values(ascending=False)
            .head(15).reset_index()
            .rename(columns={"overall": "avg_overall"})
        )
        fig5b = px.bar(
            club_ovr, x="avg_overall", y="club_name", orientation="h",
            color="avg_overall", color_continuous_scale=BLUE_SCALE,
            labels={"avg_overall": "Avg Overall Rating", "club_name": ""},
            title="Top 15 clubs by average player overall rating"
        )
        fig5b.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        apply_theme(fig5b)
        st.plotly_chart(fig5b, use_container_width=True)

with col6:
    st.markdown('<div class="section-title">🌱 Rising Stars (Age ≤ 23)</div>', unsafe_allow_html=True)
    min_ovr = st.slider("Min current overall rating", 55, 80, 65, key="rising_min")
    rising_df = growth_potential_players(df, min_overall=min_ovr, n=20)
    if len(rising_df) > 0:
        fig6 = px.scatter(
            rising_df, x="overall", y="potential",
            size="growth", color="growth",
            color_continuous_scale=BLUE_SCALE,
            hover_data=["short_name", "age", "club_name", "primary_position"],
            labels={"overall": "Current Rating", "potential": "Potential Rating"},
            title="Young players with biggest growth potential"
        )
        fig6.update_traces(marker_line_color="white", marker_line_width=1)
        apply_theme(fig6)
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("No rising stars found with current filters. Try lowering the minimum overall rating.")

st.markdown("---")

# ─── Data Table ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Full Player Table</div>', unsafe_allow_html=True)
show_cols = [c for c in ["short_name","age","nationality_name","club_name",
             "primary_position","overall","potential","value_m","wage_k","preferred_foot"]
             if c in df.columns]

search = st.text_input("🔍 Search by player name", placeholder="e.g. Messi, Ronaldo, Neymar…")
display_df = df[show_cols].copy()
if search:
    display_df = display_df[display_df["short_name"].str.contains(search, case=False, na=False)]

st.dataframe(
    display_df.sort_values("overall", ascending=False).reset_index(drop=True),
    use_container_width=True, height=400,
)
st.caption("Source: FIFA Player Dataset · Kaggle")
