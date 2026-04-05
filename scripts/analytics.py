"""
analytics.py
------------
Five focused analyses on the FIFA dataset.
Each function returns a DataFrame or dict ready to plot.
"""

import pandas as pd


def top_rated_players(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Return the top-N players by overall rating."""
    cols = ["short_name", "club_name", "nationality_name",
            "primary_position", "overall", "potential", "value_m", "age"]
    return (
        df[cols]
        .sort_values("overall", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def nationality_distribution(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Count of players per nationality (top N)."""
    return (
        df["nationality_name"]
        .value_counts()
        .head(top_n)
        .rename_axis("nationality")
        .reset_index(name="player_count")
    )


def overall_by_position(df: pd.DataFrame) -> pd.DataFrame:
    """Average overall, pace, shooting, passing, defending by position group."""
    cols = ["position_group", "overall", "pace", "shooting", "passing", "defending", "physic"]
    return (
        df[cols]
        .groupby("position_group")
        .mean(numeric_only=True)
        .round(1)
        .reset_index()
    )


def age_vs_overall(df: pd.DataFrame) -> pd.DataFrame:
    """Average overall rating bucketed by age — shows player peak age curve."""
    return (
        df.groupby("age")["overall"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"overall": "avg_overall"})
        .sort_values("age")
    )


def most_valuable_clubs(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Total squad market value per club (top N)."""
    return (
        df.groupby("club_name")["value_m"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
        .rename(columns={"value_m": "total_value_m"})
    )


def growth_potential_players(df: pd.DataFrame, min_overall: int = 70, n: int = 20) -> pd.DataFrame:
    """Young players (≤23) with biggest gap between potential and current overall."""
    return (
        df[(df["age"] <= 23) & (df["overall"] >= min_overall)]
        [["short_name", "age", "club_name", "nationality_name",
          "primary_position", "overall", "potential", "growth", "value_m"]]
        .sort_values("growth", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
