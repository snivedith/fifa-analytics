"""
data_loader.py
--------------
Loads FIFA player data automatically from a public GitHub URL.
Dataset: https://raw.githubusercontent.com/rashida048/Datasets/master/fifa.csv
"""

import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/rashida048/Datasets/master/fifa.csv"

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
    """Convert strings like '€100M', '€500K' to float in millions."""
    if pd.isna(val):
        return 0.0
    val = str(val).replace("€", "").replace(",", "").strip()
    if "M" in val:
        try: return float(val.replace("M", ""))
        except: return 0.0
    if "K" in val:
        try: return float(val.replace("K", "")) / 1000
        except: return 0.0
    try:
        return float(val) / 1_000_000
    except:
        return 0.0


@st.cache_data(show_spinner="Downloading FIFA dataset…")
def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(DATA_URL)
        return df
    except Exception as e:
        raise ConnectionError(f"Could not download the dataset.\n{e}")


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Print columns to help debug (visible in Streamlit logs)
    rename_candidates = {
        "Name": "short_name", "name": "short_name",
        "Nationality": "nationality_name", "nationality": "nationality_name",
        "Club": "club_name", "club": "club_name",
        "Age": "age", "age": "age",
        "Overall": "overall", "OVA": "overall",
        "Potential": "potential", "POT": "potential",
        "Value": "value_eur_raw", "Wage": "wage_eur_raw",
        "Position": "player_positions", "Positions": "player_positions",
        "Preferred Foot": "preferred_foot",
        "PAC": "pace", "SHO": "shooting", "PAS": "passing",
        "DRI": "dribbling", "DEF": "defending", "PHY": "physic",
    }
    rename_map = {k: v for k, v in rename_candidates.items() if k in df.columns}
    df.rename(columns=rename_map, inplace=True)

    df.dropna(subset=["overall", "club_name", "nationality_name"], inplace=True)

    # Parse money — use raw numeric if string parsing gives 0
    if "value_eur_raw" in df.columns:
        df["value_m"] = df["value_eur_raw"].apply(_parse_money)
        # If all zeros, try treating column as numeric directly
        if df["value_m"].sum() == 0:
            df["value_m"] = pd.to_numeric(df["value_eur_raw"], errors="coerce").fillna(0) / 1_000_000
    else:
        df["value_m"] = 0.0

    if "wage_eur_raw" in df.columns:
        df["wage_k"] = df["wage_eur_raw"].apply(_parse_money)
        if df["wage_k"].sum() == 0:
            df["wage_k"] = pd.to_numeric(df["wage_eur_raw"], errors="coerce").fillna(0) / 1_000
    else:
        df["wage_k"] = 0.0

    # Primary position & group
    if "player_positions" in df.columns:
        df["primary_position"] = df["player_positions"].str.split(",").str[0].str.strip()
    else:
        df["primary_position"] = "Unknown"

    df["position_group"] = df["primary_position"].map(POS_MAP).fillna("Other")

    # Numeric coercion
    for col in ["pace","shooting","passing","dribbling","defending","physic","overall","potential","age"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["growth"] = df.get("potential", 0) - df["overall"]
    df.dropna(subset=["overall", "age"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
