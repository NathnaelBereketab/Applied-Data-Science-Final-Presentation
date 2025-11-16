"""
PHASE 1 - STEP 1.6: Load and Explore ratings datasets (ratings_small.csv and ratings.csv)
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("PHASE 1 - STEP 1.6: Exploring ratings datasets")
print("=" * 80)

# Try to load both ratings files
datasets = {}
for filename in ['ratings_small.csv', 'ratings.csv']:
    try:
        df = pd.read_csv(filename, low_memory=False, on_bad_lines='skip')
        datasets[filename] = df
        print(f"\n[OK] Loaded {filename} successfully!")
    except FileNotFoundError:
        print(f"\n[WARNING] {filename} not found, skipping...")
        continue
    except TypeError:
        try:
            df = pd.read_csv(filename, low_memory=False, error_bad_lines=False, warn_bad_lines=False)
            datasets[filename] = df
            print(f"\n[OK] Loaded {filename} successfully!")
        except Exception as e:
            print(f"\n[ERROR] Failed to load {filename}: {str(e)}")
            continue

if not datasets:
    print("\n[ERROR] No ratings datasets found!")
    exit(1)

# Analyze each dataset
for filename, df in datasets.items():
    print("\n" + "=" * 80)
    print(f"ANALYZING: {filename}")
    print("=" * 80)
    
    # Basic info
    print(f"\n1. DATASET SHAPE & STRUCTURE")
    print(f"   Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"   Columns: {len(df.columns)}")
    
    # Column names
    print(f"\n2. COLUMN NAMES:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")
    
    # Data types
    print(f"\n3. DATA TYPES:")
    print(df.dtypes)
    
    # Missing values
    print(f"\n4. MISSING VALUES:")
    missing = df.isnull().sum().sort_values(ascending=False)
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        'Missing Count': missing,
        'Missing %': missing_pct
    })
    print(missing_df)
    
    # Sample data
    print(f"\n5. SAMPLE DATA (First 5 rows):")
    print(df.head(5).to_string())
    
    # Analyze userId
    if 'userId' in df.columns:
        print(f"\n6. USER ID ANALYSIS:")
        print(f"   Total users: {df['userId'].nunique():,}")
        print(f"   Range: {df['userId'].min()} to {df['userId'].max()}")
        # Ratings per user
        ratings_per_user = df['userId'].value_counts()
        print(f"   Ratings per user:")
        print(f"      Mean: {ratings_per_user.mean():.1f}")
        print(f"      Median: {ratings_per_user.median():.1f}")
        print(f"      Min: {ratings_per_user.min()}")
        print(f"      Max: {ratings_per_user.max()}")
    
    # Analyze movieId
    if 'movieId' in df.columns:
        print(f"\n7. MOVIE ID ANALYSIS:")
        print(f"   Total unique movies: {df['movieId'].nunique():,}")
        print(f"   Range: {df['movieId'].min()} to {df['movieId'].max()}")
        # Ratings per movie
        ratings_per_movie = df['movieId'].value_counts()
        print(f"   Ratings per movie:")
        print(f"      Mean: {ratings_per_movie.mean():.1f}")
        print(f"      Median: {ratings_per_movie.median():.1f}")
        print(f"      Min: {ratings_per_movie.min()}")
        print(f"      Max: {ratings_per_movie.max()}")
    
    # Analyze rating
    if 'rating' in df.columns:
        print(f"\n8. RATING ANALYSIS:")
        print(f"   Non-null ratings: {df['rating'].notna().sum():,}")
        print(f"   Rating distribution:")
        print(f"      Mean: {df['rating'].mean():.2f}")
        print(f"      Median: {df['rating'].median():.2f}")
        print(f"      Range: {df['rating'].min():.1f} to {df['rating'].max():.1f}")
        print(f"      Std Dev: {df['rating'].std():.2f}")
        
        # Rating value counts
        print(f"\n   Rating value distribution:")
        rating_counts = df['rating'].value_counts().sort_index()
        for rating, count in rating_counts.items():
            pct = (count / len(df) * 100)
            print(f"      {rating:.1f}: {count:,} ({pct:.1f}%)")
    
    # Analyze timestamp if exists
    if 'timestamp' in df.columns:
        print(f"\n9. TIMESTAMP ANALYSIS:")
        print(f"   Non-null timestamps: {df['timestamp'].notna().sum():,}")
        if df['timestamp'].notna().any():
            # Convert timestamp to datetime
            try:
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
                valid_dates = df['datetime'].dropna()
                if len(valid_dates) > 0:
                    print(f"   Date range: {valid_dates.min()} to {valid_dates.max()}")
                    # Extract year
                    df['year'] = df['datetime'].dt.year
                    year_counts = df['year'].value_counts().sort_index()
                    print(f"   Ratings by year (sample):")
                    for year in sorted(year_counts.head(5).index):
                        print(f"      {int(year)}: {year_counts[year]:,} ratings")
                    print(f"      ...")
                    for year in sorted(year_counts.tail(3).index):
                        print(f"      {int(year)}: {year_counts[year]:,} ratings")
            except:
                print(f"   [NOTE] Could not parse timestamps")

# Summary comparison
print("\n" + "=" * 80)
print("SUMMARY COMPARISON:")
print("=" * 80)
for filename, df in datasets.items():
    print(f"\n{filename}:")
    print(f"   Total ratings: {len(df):,}")
    if 'userId' in df.columns:
        print(f"   Unique users: {df['userId'].nunique():,}")
    if 'movieId' in df.columns:
        print(f"   Unique movies: {df['movieId'].nunique():,}")
    if 'rating' in df.columns:
        print(f"   Average rating: {df['rating'].mean():.2f}")

print("\n[OK] Phase 1, Step 1.6 COMPLETE!")
print("=" * 80)
print("\n" + "=" * 80)
print("PHASE 1 COMPLETE - ALL DATASETS EXPLORED!")
print("=" * 80)

