# ⚽ FIFA 22 Analytics Dashboard

An interactive analytics dashboard built with **Streamlit** and **Plotly** for exploring FIFA 22 player statistics.

---

## 📦 Dataset

Download the dataset from Kaggle:

**[FIFA 22 Complete Player Dataset](https://www.kaggle.com/datasets/stefanoleone992/fifa-22-complete-player-dataset)**

1. Download and unzip the archive
2. Place `players_22.csv` inside the `data/` folder:

```
fifa-analytics/
└── data/
    └── players_22.csv   ← goes here
```

---

## 🚀 Setup & Run

### 1. Clone / download this project

```bash
cd fifa-analytics
```

### 2. (Optional) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`.

---

## 📊 What the Dashboard Shows

| Section | Insight |
|---|---|
| **KPI Row** | Total players, avg rating, avg age, avg market value, nations represented |
| **Top Rated Players** | Horizontal bar chart of highest-rated players |
| **Players by Nation** | Which countries produce the most top players |
| **Age vs. Rating Curve** | How average rating peaks across career ages |
| **Attribute by Position** | Pace / Shooting / Passing / Defending breakdown per role |
| **Most Valuable Squads** | Clubs with highest total squad market value |
| **Rising Stars** | Young players (≤23) with the biggest growth potential gap |
| **Data Table** | Searchable, sortable raw player table |

### Sidebar Filters

Use the sidebar to filter by:
- Overall rating range
- Age range
- Position group (GK / Defender / Midfielder / Forward)
- Preferred foot (Left / Right / Both)

All charts update instantly based on your selection.

---

## 🗂 Project Structure

```
fifa-analytics/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── data/
│   └── players_22.csv      # Dataset (download from Kaggle)
└── scripts/
    ├── __init__.py
    ├── data_loader.py      # Data loading & preprocessing
    └── analytics.py        # Analysis functions
```

---

## 🛠 Tech Stack

- **Streamlit** — web app framework
- **Pandas** — data manipulation
- **Plotly** — interactive charts
