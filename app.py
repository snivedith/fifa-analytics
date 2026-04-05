"""
app.py  —  FIFA 22 Analytics Dashboard
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

# ─── Theme colours ────────────────────────────────────────────────────────────
BLUE       = "#1D4ED8"
BLUE_LIGHT = "#3B82F6"
BLUE_PALE  = "#EFF6FF"
DARK       = "#0F172A"
SLATE      = "#1E293B"
MUTED      = "#64748B"
WHITE      = "#F8FAFC"

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: {WHITE};
      color: {DARK};
  }}
  .stApp {{ background-color: {WHITE}; }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
      background-color: {DARK};
      border-right: none;
  }}
  section[data-testid="stSidebar"] * {{ color: #CBD5E1 !important; }}
  section[data-testid="stSidebar"] h1,
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {{
      color: white !important;
  }}
  section[data-testid="stSidebar"] .stSlider label,
  section[data-testid="stSidebar"] .stMultiSelect label,
  section[data-testid="stSidebar"] .stSelectbox label {{
      color: #94A3B8 !important;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
  }}

  /* Metrics */
  div[data-testid="metric-container"] {{
      background: white;
      border: 1px solid #E2E8F0;
      border-top: 3px solid {BLUE};
      border-radius: 8px;
      padding: 1.2rem 1.4rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  div[data-testid="metric-container"] label {{
      color: {MUTED};
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
  }}
  div[data-testid="metric-container"] [data-testid="metric-value"] {{
      color: {DARK};
      font-family: 'IBM Plex Mono', monospace;
      font-size: 1.75rem;
      font-weight: 600;
  }}

  /* Headers */
  h1 {{ color: {DARK}; font-weight: 700; font-size: 1.8rem !important; }}
  h2, h3 {{ color: {DARK}; font-weight: 600; }}

  /* Section cards */
  .chart-card {{
      background: white;
      border: 1px solid #E2E8F0;
      border-radius: 10px;
      padding: 1.2rem 1.4rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      margin-bottom: 1rem;
  }}
  .section-title {{
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: {BLUE};
      margin-bottom: 0.3rem;
  }}
  .page-header {{
      background: linear-gradient(135deg, {DARK} 0%, {SLATE} 100%);
      border-radius: 12px;
      padding: 2rem 2.5rem;
      margin-bottom: 1.5rem;
      color: white;
  }}
  .page-header h1 {{ color: white !important; margin: 0; font-size: 2rem !important; }}
  .page-header p {{ color: #94A3B8; margin: 0.3rem 0 0 0; font-size: 0.95rem; }}

  .badge {{
      display: inline-block;
      background: {BLUE_PALE};
      color: {BLUE};
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.2rem 0.6rem;
      border-radius: 999px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
  }}

  footer, #MainMenu {{ visibility: hidden; }}
  .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}
  div[data-testid="stDataFrame"] {{ border-radius: 8px; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)

# ─── Plotly theme ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#334155", size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0", linecolor="#E2E8F0"),
    yaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0", linecolor="#E2E8F0"),
    colorway=[BLUE, BLUE_LIGHT, "#60A5FA", "#93C5FD", "#BFDBFE"],
)

BLUE_SCALE = ["#DBEAFE", "#93C5FD", "#3B82F6", "#1D4ED8", "#1E3A8A"]

def apply_theme(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
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
    rating_range = st.slider("", int(df_full.overall.min()), 99, (70, 99), label_visibility="collapsed")

    st.markdown("**Age Range**")
    age_range = st.slider(" ", int(df_full.age.min()), int(df_full.age.max()), (16, 40), label_visibility="collapsed")

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

# ─── Page header ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <h1>⚽ FIFA Player Analytics</h1>
    <p>Exploring <strong style="color:white">{len(df):,} players</strong> · Use the sidebar to filter by rating, age, position, and foot</p>
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

# ─── Row 1 ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown('<div class="section-title">🏆 Top Rated Players</div>', unsafe_allow_html=True)
    top_n = st.slider("Show top N", 5, 30, 15, key="top_n")
    top_df = top_rated_players(df, n=top_n)
    fig1 = px.bar(
        top_df, x="overall", y="short_name", orientation="h",
        color="overall", color_continuous_scale=BLUE_SCALE,
        hover_data=["club_name", "nationality_name", "primary_position", "value_m"],
        labels={"overall": "Rating", "short_name": ""},
    )
    fig1.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    apply_theme(fig1)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">🌍 Players by Nation</div>', unsafe_allow_html=True)
    nat_df = nationality_distribution(df, top_n=20)
    fig2 = px.bar(
        nat_df, x="player_count", y="nationality", orientation="h",
        color="player_count", color_continuous_scale=BLUE_SCALE,
        labels={"player_count": "Players", "nationality": ""},
    )
    fig2.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    apply_theme(fig2)
    st.plotly_chart(fig2, use_container_width=True)

# ─── Row 2 ────────────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-title">📈 Age vs. Average Rating</div>', unsafe_allow_html=True)
    age_df = age_vs_overall(df)
    fig3 = px.line(
        age_df, x="age", y="avg_overall", markers=True,
        labels={"age": "Age", "avg_overall": "Avg Overall Rating"},
    )
    fig3.update_traces(line_color=BLUE, marker_color=BLUE, line_width=2.5, marker_size=5)
    # Add subtle fill under line
    fig3.add_traces(go.Scatter(
        x=age_df["age"], y=age_df["avg_overall"],
        fill="tozeroy", fillcolor="rgba(29,78,216,0.07)",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"
    ))
    apply_theme(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown('<div class="section-title">⚡ Attributes by Position</div>', unsafe_allow_html=True)
    pos_df = overall_by_position(df)
    attr_cols = ["pace", "shooting", "passing", "defending", "physic"]
    blues = ["#1D4ED8", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"]
    fig4 = go.Figure()
    for i, attr in enumerate(attr_cols):
        if attr in pos_df.columns:
            fig4.add_trace(go.Bar(
                name=attr.capitalize(),
                x=pos_df["position_group"],
                y=pos_df[attr],
                marker_color=blues[i],
            ))
    fig4.update_layout(barmode="group", legend=dict(orientation="h", y=1.12, font=dict(size=11)))
    apply_theme(fig4)
    st.plotly_chart(fig4, use_container_width=True)

# ─── Row 3 ────────────────────────────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="section-title">💰 Most Valuable Squads</div>', unsafe_allow_html=True)
    clubs_df = most_valuable_clubs(df)
    fig5 = px.bar(
        clubs_df, x="total_value_m", y="club_name", orientation="h",
        color="total_value_m", color_continuous_scale=BLUE_SCALE,
        labels={"total_value_m": "Total Value (€M)", "club_name": ""},
    )
    fig5.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    apply_theme(fig5)
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.markdown('<div class="section-title">🌱 Rising Stars (≤23)</div>', unsafe_allow_html=True)
    min_ovr = st.slider("Min current overall", 60, 85, 70, key="rising_min")
    rising_df = growth_potential_players(df, min_overall=min_ovr, n=20)
    fig6 = px.scatter(
        rising_df, x="overall", y="potential",
        size="growth", color="growth",
        color_continuous_scale=BLUE_SCALE,
        hover_data=["short_name", "age", "club_name", "primary_position"],
        labels={"overall": "Current Rating", "potential": "Potential Rating"},
    )
    fig6.update_traces(marker_line_color="white", marker_line_width=1)
    apply_theme(fig6)
    st.plotly_chart(fig6, use_container_width=True)

# ─── Data table ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-title">📋 Player Data Table</div>', unsafe_allow_html=True)

show_cols = [c for c in ["short_name", "age", "nationality_name", "club_name",
             "primary_position", "overall", "potential", "value_m", "wage_k",
             "preferred_foot"] if c in df.columns]

search = st.text_input("🔍 Search player", placeholder="e.g. Messi, Ronaldo…")
display_df = df[show_cols].copy()
if search:
    display_df = display_df[display_df["short_name"].str.contains(search, case=False, na=False)]

st.dataframe(
    display_df.sort_values("overall", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=380,
)
st.caption("Source: FIFA Player Dataset · Kaggle")
