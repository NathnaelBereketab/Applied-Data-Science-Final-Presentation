"""
PHASE 1 - STEP 1.4: Load and Explore imdb_movies.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("PHASE 1 - STEP 1.4: Exploring imdb_movies.csv")
print("=" * 80)

# Load the dataset
print("\n1. LOADING DATASET...")
try:
    df = pd.read_csv('imdb_movies.csv', low_memory=False, on_bad_lines='skip')
    print(f"   [OK] Dataset loaded successfully!")
except FileNotFoundError:
    print("   [ERROR] imdb_movies.csv not found!")
    exit(1)
except TypeError:
    try:
        df = pd.read_csv('imdb_movies.csv', low_memory=False, error_bad_lines=False, warn_bad_lines=False)
        print(f"   [OK] Dataset loaded successfully!")
    except Exception as e:
        print(f"   [ERROR] Failed to load: {str(e)}")
        exit(1)

# Basic info
print("\n2. DATASET SHAPE & STRUCTURE")
print(f"   Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"   Columns: {len(df.columns)}")

# Column names
print("\n3. COLUMN NAMES:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i:2d}. {col}")

# Data types
print("\n4. DATA TYPES:")
print(df.dtypes)

# Missing values
print("\n5. MISSING VALUES (Top 15):")
missing = df.isnull().sum().sort_values(ascending=False)
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Missing %': missing_pct
})
print(missing_df.head(15))

# Check merge keys
print("\n6. MERGE KEY ANALYSIS:")
merge_keys = []
for key in ['imdb_id', 'id', 'movie_id', 'tmdb_id', 'imdb_title_id']:
    if key in df.columns:
        merge_keys.append(key)
        print(f"   Merge key found: '{key}'")
        print(f"      Unique values: {df[key].nunique():,}")
        print(f"      Duplicates: {(df[key].duplicated()).sum():,}")
        if df[key].dtype in ['int64', 'float64']:
            print(f"      Range: {df[key].min()} to {df[key].max()}")

if not merge_keys:
    print("   [WARNING] No standard merge key found!")
    print("   Available columns:", list(df.columns))

# Sample of raw data
print("\n7. SAMPLE OF RAW DATA (First 2 rows):")
try:
    print(df.head(2).to_string())
except UnicodeEncodeError:
    print("   [NOTE] Sample data contains special characters - showing column info only")
    print(f"   Columns: {list(df.columns)}")
    for col in df.columns:
        if df[col].dtype == 'object':
            sample_val = str(df[col].iloc[0])[:100] if len(df) > 0 else "N/A"
            print(f"   {col}: {sample_val}")

# Analyze year column if exists
print("\n8. YEAR ANALYSIS:")
year_cols = [col for col in df.columns if 'year' in col.lower()]
if year_cols:
    for col in year_cols:
        print(f"   {col}:")
        print(f"      Non-null: {df[col].notna().sum():,}")
        if df[col].notna().any():
            year_data = df[df[col].notna()][col]
            if year_data.dtype in ['int64', 'float64']:
                print(f"      Range: {year_data.min():.0f} to {year_data.max():.0f}")
                print(f"      Mean: {year_data.mean():.0f}")
                # Filter to 2000-2025
                filtered = year_data[(year_data >= 2000) & (year_data <= 2025)]
                print(f"      Movies 2000-2025: {len(filtered):,}")
else:
    print("   No year column found")

# Analyze score/rating column if exists
print("\n9. RATING/SCORE ANALYSIS:")
rating_cols = [col for col in df.columns if any(x in col.lower() for x in ['score', 'rating', 'vote', 'imdb'])]
if rating_cols:
    for col in rating_cols:
        print(f"   {col}:")
        print(f"      Non-null: {df[col].notna().sum():,}")
        if df[col].notna().any():
            rating_data = df[df[col].notna()][col]
            if rating_data.dtype in ['int64', 'float64']:
                print(f"      Mean: {rating_data.mean():.2f}")
                print(f"      Median: {rating_data.median():.2f}")
                print(f"      Range: {rating_data.min():.2f} to {rating_data.max():.2f}")
else:
    print("   No rating/score column found")

# Analyze budget/revenue if exists
print("\n10. FINANCIAL DATA ANALYSIS:")
financial_cols = [col for col in df.columns if any(x in col.lower() for x in ['budget', 'revenue', 'gross', 'box'])]
if financial_cols:
    for col in financial_cols:
        print(f"   {col}:")
        print(f"      Non-null: {df[col].notna().sum():,}")
        if df[col].notna().any():
            # Convert to numeric if needed
            try:
                financial_data = pd.to_numeric(df[col], errors='coerce')
                financial_positive = financial_data[financial_data > 0]
                if len(financial_positive) > 0:
                    print(f"      Mean: ${financial_positive.mean():,.0f}")
                    print(f"      Median: ${financial_positive.median():,.0f}")
                    print(f"      Max: ${financial_positive.max():,.0f}")
            except:
                print(f"      [NOTE] Could not convert to numeric")
else:
    print("   No financial columns found")

# Analyze genre column if exists
print("\n11. GENRE ANALYSIS:")
genre_cols = [col for col in df.columns if 'genre' in col.lower()]
if genre_cols:
    for col in genre_cols:
        print(f"   {col}:")
        print(f"      Non-null: {df[col].notna().sum():,}")
        # Sample values
        sample_genres = df[col].dropna().head(5)
        print(f"      Sample values:")
        for idx, val in enumerate(sample_genres, 1):
            try:
                print(f"         {idx}. {str(val)[:100]}")
            except UnicodeEncodeError:
                print(f"         {idx}. [Contains special characters]")
else:
    print("   No genre column found")

# Analyze country/language if exists
print("\n12. COUNTRY/LANGUAGE ANALYSIS:")
location_cols = [col for col in df.columns if any(x in col.lower() for x in ['country', 'language', 'origin'])]
if location_cols:
    for col in location_cols:
        print(f"   {col}:")
        print(f"      Non-null: {df[col].notna().sum():,}")
        if df[col].notna().any():
            unique_vals = df[col].nunique()
            print(f"      Unique values: {unique_vals}")
            if unique_vals <= 20:
                print(f"      Values: {df[col].value_counts().head(10).to_dict()}")
else:
    print("   No country/language columns found")

# Compare with other datasets
print("\n13. DATASET COMPARISON:")
if merge_keys:
    print(f"   Movies in imdb_movies dataset: {len(df):,}")
    print(f"   [NOTE] Compare with:")
    print(f"      - movies_metadata.csv: 24,007 movies (2000-2025)")
    print(f"      - credits.csv: 4,803 movies")
    print(f"      - keywords.csv: 45,432 unique movies")

# Summary
print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"[OK] Total movies in imdb_movies dataset: {len(df):,}")
if merge_keys:
    print(f"[OK] Merge keys available: {', '.join(merge_keys)}")
if year_cols:
    year_data = df[df[year_cols[0]].notna()][year_cols[0]]
    if year_data.dtype in ['int64', 'float64']:
        filtered = year_data[(year_data >= 2000) & (year_data <= 2025)]
        print(f"[OK] Movies from 2000-2025: {len(filtered):,}")

print("\n[OK] Phase 1, Step 1.4 COMPLETE!")
print("=" * 80)

