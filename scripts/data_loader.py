"""
data_loader.py
--------------
Handles loading and preprocessing of the FIFA dataset.
Expected file: data/players_22.csv  (FIFA 22 dataset from Kaggle)
Kaggle link: https://www.kaggle.com/datasets/stefanoleone992/fifa-22-complete-player-dataset
"""

import pandas as pd


# Columns we actually need — keeps memory low
USECOLS = [
    "short_name", "long_name", "age", "nationality_name",
    "club_name", "league_name", "overall", "potential",
    "value_eur", "wage_eur", "height_cm", "weight_kg",
    "player_positions", "preferred_foot",
    "pace", "shooting", "passing", "dribbling", "defending", "physic",
    "attacking_heading_accuracy", "skill_ball_control",
    "movement_sprint_speed", "mentality_vision",
    "work_rate", "international_reputation",
]


def load_data(filepath: str = "data/players_22.csv") -> pd.DataFrame:
    """Load the FIFA CSV and return a raw DataFrame."""
    try:
        df = pd.read_csv(filepath, usecols=USECOLS, low_memory=False)
        return df
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Dataset not found at '{filepath}'.\n"
            "Download 'players_22.csv' from:\n"
            "https://www.kaggle.com/datasets/stefanoleone992/fifa-22-complete-player-dataset\n"
            "and place it inside the data/ folder."
        )


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich the raw DataFrame."""
    df = df.copy()

    # Drop rows missing key fields
    df.dropna(subset=["overall", "club_name", "nationality_name"], inplace=True)

    # Primary position (first listed)
    df["primary_position"] = df["player_positions"].str.split(",").str[0].str.strip()

    # Position group
    pos_map = {
        "GK": "Goalkeeper",
        "CB": "Defender", "LB": "Defender", "RB": "Defender",
        "LWB": "Defender", "RWB": "Defender",
        "CDM": "Midfielder", "CM": "Midfielder", "CAM": "Midfielder",
        "LM": "Midfielder", "RM": "Midfielder",
        "LW": "Forward", "RW": "Forward", "ST": "Forward",
        "CF": "Forward", "RF": "Forward", "LF": "Forward",
    }
    df["position_group"] = df["primary_position"].map(pos_map).fillna("Other")

    # Value in millions (readable)
    df["value_m"] = (df["value_eur"] / 1_000_000).round(2)
    df["wage_k"]  = (df["wage_eur"] / 1_000).round(2)

    # Growth potential
    df["growth"] = df["potential"] - df["overall"]

    # Numeric coercion for attribute cols
    attr_cols = ["pace", "shooting", "passing", "dribbling", "defending", "physic"]
    for col in attr_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.reset_index(drop=True, inplace=True)
    return df
