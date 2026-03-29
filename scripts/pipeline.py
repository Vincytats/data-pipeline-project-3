# pipeline.py

import pandas as pd

# =========================
# CONFIG
# =========================

GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1PIaSrEvGDyv1HEIsYLGmSbSyVwQ2h149yyp3ww3gHqo/export?format=csv"

OUTPUT_FILE = "processed_monthly_stats.csv"

# =========================
# LOAD DATA
# =========================

def load_data():
    print("Loading data from Google Sheets...")
    df = pd.read_csv(GOOGLE_SHEET_CSV)
    return df

# =========================
# CLEAN + STANDARDIZE
# =========================

def clean_data(df):
    print("Cleaning data...")

    # Remove whitespace in column names
    df.columns = df.columns.str.strip()

    # Standardize column names (adjust if needed)
    df = df.rename(columns={
        "Implementing Partner": "IP Name",
        "Indicator": "Indicators",
        "Achieved": "Achieved Outputs"
    })

    return df

# =========================
# SELECT RELEVANT COLUMNS
# =========================

def select_columns(df):
    print("Selecting relevant columns...")

    required_columns = [
        "Month",
        "Indicators",
        "IP Name",
        "Achieved Outputs",
        "Number training partnerships/collaborations to be established",
        "Number participants to complete vocational skills training",
        "Number certifications to be issued",
        "Number participants to complete work readiness or soft skills training"
    ]

    # Keep only columns that exist
    available_columns = [col for col in required_columns if col in df.columns]

    df = df[available_columns]

    return df

# =========================
# DATA CLEANING RULES
# =========================

def transform_data(df):
    print("Transforming data...")

    # Convert numeric columns properly
    numeric_cols = df.select_dtypes(include=['object']).columns

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    # Drop completely empty rows
    df = df.dropna(how='all')

    return df

def run_pipeline():
    df = load_data()
    df = clean_data(df)
    df = select_columns(df)
    df = transform_data(df)

    # Save final dataset
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"✅ Pipeline complete. File saved as {OUTPUT_FILE}")


if __name__ == "__main__":
    run_pipeline()
