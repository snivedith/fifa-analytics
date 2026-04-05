"""
data_loader.py
--------------
Loads FIFA player data automatically from a public GitHub URL.
No manual CSV download needed — works locally and on Streamlit Cloud.

Dataset: https://raw.githubusercontent.com/rashida048/Datasets/master/fifa.csv
Columns include: Name, Age, Nationality, Club, Overall, Potential,
                 Value, Wage, Position, Preferred Foot,
                 PAC, SHO, PAS, DRI, DEF, PHY
"""

import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/rashida048/Datasets/master/fifa.csv"


def _parse_money(val) -> float:
    """Convert strings like '€100M', '€500K' to float in millions."""
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

    # Normalise column names — strip whitespace
    df.columns = df.columns.str.strip()

    # Build rename map dynamically based on what columns exist
    rename_candidates = {
        "Name":           "short_name",
        "name":           "short_name",
        "Nationality":    "nationality_name",
        "nationality":    "nationality_name",
        "Club":           "club_name",
        "club":           "club_name",
        "Age":            "age",
        "age":            "age",
        "Overall":        "overall",
        "OVA":            "overall",
        "Potential":      "potential",
        "POT":            "potential",
        "Value":          "value_eur_raw",
        "Wage":           "wage_eur_raw",
        "Position":       "player_positions",
        "Positions":      "player_positions",
        "Preferred Foot": "preferred_foot",
        "PAC":            "pace",
        "SHO":            "shooting",
        "PAS":            "passing",
        "DRI":            "dribbling",
        "DEF":            "defending",
        "PHY":            "physic",
    }
    rename_map = {k: v for k, v in rename_candidates.items() if k in df.columns}
    df.rename(columns=rename_map, inplace=True)

    # Ensure required columns exist with fallback defaults
    for col in ["short_name", "nationality_name", "club_name", "overall", "age"]:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in dataset.")

    # Drop rows missing key fields
    df.dropna(subset=["overall", "club_name", "nationality_name"], inplace=True)

    # Market value & wage
    if "value_eur_raw" in df.columns:
        df["value_m"] = df["value_eur_raw"].apply(_parse_money)
    else:
        df["value_m"] = 0.0

    if "wage_eur_raw" in df.columns:
        df["wage_k"] = df["wage_eur_raw"].apply(_parse_money)
    else:
        df["wage_k"] = 0.0

    # Primary position & group
    if "player_positions" in df.columns:
        df["primary_position"] = df["player_positions"].str.split(",").str[0].str.strip()
    else:
        df["primary_position"] = "Unknown"

    pos_map = {
        "GK":  "Goalkeeper",
        "CB":  "Defender",  "LB":  "Defender",  "RB":  "Defender",
        "LWB": "Defender",  "RWB": "Defender",
        "CDM": "Midfielder","CM":  "Midfielder","CAM": "Midfielder",
        "LM":  "Midfielder","RM":  "Midfielder",
        "LW":  "Forward",   "RW":  "Forward",   "ST":  "Forward",
        "CF":  "Forward",   "RF":  "Forward",   "LF":  "Forward",
    }
    df["position_group"] = df["primary_position"].map(pos_map).fillna("Other")

    # Numeric coercion
    for col in ["pace","shooting","passing","dribbling","defending","physic","overall","potential","age"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Growth potential
    if "potential" in df.columns:
        df["growth"] = df["potential"] - df["overall"]
    else:
        df["growth"] = 0

    df.dropna(subset=["overall", "age"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
