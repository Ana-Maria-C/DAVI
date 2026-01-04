import pandas as pd
import os

KEYWORDS_FILE = 'movie_lens_data.csv'

def verify_data():
    if not os.path.exists(KEYWORDS_FILE):
        print(f"Error: {KEYWORDS_FILE} not found.")
        return

    print(f"Loading {KEYWORDS_FILE}...")
    try:
        df = pd.read_csv(KEYWORDS_FILE)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"Shape: {df.shape}")
    print("\nColumn Info:")
    print(df.info())

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Rows:")
    print(df.duplicated().sum())

    print("\nSample Data:")
    print(df.head())

    print("\nEmpty Strings Count (approx):")
    for col in df.columns:
        if df[col].dtype == object:
            empty_count = (df[col] == "").sum() + (df[col].astype(str).str.strip() == "").sum()
            if empty_count > 0:
                print(f"{col}: {empty_count}")

if __name__ == "__main__":
    verify_data()
