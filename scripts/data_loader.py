"""
data_loader.py
--------------
Loads FIFA player data automatically from a public URL.
No manual CSV download needed — works locally and on Streamlit Cloud.
"""

import pandas as pd
import streamlit as st

# Public URL — FIFA 21 player dataset hosted on GitHub
DATA_URL = "https://raw.githubusercontent.com/davidcarmo/fifa-players-dataset/main/fifa21_male2.csv"

# ── Column rename map ─────────────────────────────────────────────────────────
RENAME = {
    "Name":           "short_name",
    "Nationality":    "nationality_name",
    "Club":           "club_name",
    "Age":            "age",
    "OVA":            "overall",
    "POT":            "potential",
    "Value":          "value_eur_raw",
    "Wage":           "wage_eur_raw",
    "Positions":      "player_positions",
    "Preferred Foot": "preferred_foot",
    "PAC":            "pace",
    "SHO":            "shooting",
    "PAS":            "passing",
    "DRI":            "dribbling",
    "DEF":            "defending",
    "PHY":            "physic",
}

POS_MAP = {
    "GK":  "Goalkeeper",
    "CB":  "Defender",  "LB":  "Defender",  "RB":  "Defender",
    "LWB": "Defender",  "RWB": "Defender",
    "CDM": "Midfielder","CM":  "Midfielder","CAM": "Midfielder",
    "LM":  "Midfielder","RM":  "Midfielder",
    "LW":  "Forward",   "RW":  "Forward",   "ST":  "Forward",
    "CF":  "Forward",   "RF":  "Forward",   "LF":  "Forward",
}


def _parse_money(val) -> float:
    """Convert strings like '€100M' or '€500K' to float (in millions)."""
    if pd.isna(val):
        return 0.0
    val = str(val).replace("€", "").replace(",", "").strip()
    if "M" in val:
        return float(val.replace("M", ""))
    if "K" in val:
        return float(val.replace("K", "")) / 1000
    try:
        return float(val) / 1_000_000
    except ValueError:
        return 0.0


@st.cache_data(show_spinner="Downloading FIFA dataset…")
def load_data() -> pd.DataFrame:
    """Download dataset from public URL and return raw DataFrame."""
    try:
        df = pd.read_csv(DATA_URL)
        return df
    except Exception as e:
        raise ConnectionError(
            f"Could not download the dataset. Check your internet connection.\n{e}"
        )


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardise the raw DataFrame."""
    df = df.copy()

    # Keep only columns we have a rename for (ignore missing ones gracefully)
    cols_present = {k: v for k, v in RENAME.items() if k in df.columns}
    df = df[list(cols_present.keys())].rename(columns=cols_present)

    # Drop rows missing essentials
    df.dropna(subset=["overall", "club_name", "nationality_name"], inplace=True)

    # Market value & wage
    df["value_m"] = df["value_eur_raw"].apply(_parse_money)
    df["wage_k"]  = df["wage_eur_raw"].apply(_parse_money)

    # Primary position & group
    df["primary_position"] = (
        df["player_positions"].str.split(",").str[0].str.strip()
    )
    df["position_group"] = df["primary_position"].map(POS_MAP).fillna("Other")

    # Growth potential
    df["growth"] = pd.to_numeric(df["potential"], errors="coerce") - \
                   pd.to_numeric(df["overall"],   errors="coerce")

    # Numeric coercion
    for col in ["pace","shooting","passing","dribbling","defending","physic","overall","potential","age"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["overall", "age"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
