"""
PHASE 1 - STEP 1.5: Load and Explore links datasets (links.csv and links_small.csv)
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("PHASE 1 - STEP 1.5: Exploring links datasets")
print("=" * 80)

# Try to load both links files
datasets = {}
for filename in ['links.csv', 'links_small.csv']:
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
    print("\n[ERROR] No links datasets found!")
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
    
    # Analyze ID columns
    print(f"\n5. ID COLUMN ANALYSIS:")
    id_cols = [col for col in df.columns if any(x in col.lower() for x in ['id', 'movie', 'imdb', 'tmdb'])]
    for col in id_cols:
        print(f"   {col}:")
        print(f"      Non-null: {df[col].notna().sum():,}")
        print(f"      Unique values: {df[col].nunique():,}")
        if df[col].dtype in ['int64', 'float64']:
            print(f"      Range: {df[col].min()} to {df[col].max()}")
    
    # Sample data
    print(f"\n6. SAMPLE DATA (First 5 rows):")
    try:
        print(df.head(5).to_string())
    except UnicodeEncodeError:
        print("   [NOTE] Sample contains special characters")
        for col in df.columns:
            print(f"   {col}: {df[col].iloc[0] if len(df) > 0 else 'N/A'}")
    
    # Check for movieId column (common in links files)
    if 'movieId' in df.columns:
        print(f"\n7. MOVIE ID ANALYSIS:")
        print(f"   Total movieIds: {df['movieId'].nunique():,}")
        print(f"   Duplicate movieIds: {(df['movieId'].duplicated()).sum():,}")
    
    # Check for imdbId
    if 'imdbId' in df.columns:
        print(f"\n8. IMDB ID ANALYSIS:")
        print(f"   Total imdbIds: {df['imdbId'].nunique():,}")
        print(f"   Non-null imdbIds: {df['imdbId'].notna().sum():,}")
        print(f"   Format check:")
        imdb_ids = df[df['imdbId'].notna()]['imdbId']
        if len(imdb_ids) > 0:
            # Check if they're numeric (tt format)
            sample = str(imdb_ids.iloc[0])
            print(f"      Sample: {sample}")
            if sample.startswith('tt'):
                print(f"      Format: tt####### (IMDB format)")
            elif sample.isdigit():
                print(f"      Format: Numeric")
    
    # Check for tmdbId
    if 'tmdbId' in df.columns:
        print(f"\n9. TMDB ID ANALYSIS:")
        print(f"   Total tmdbIds: {df['tmdbId'].nunique():,}")
        print(f"   Non-null tmdbIds: {df['tmdbId'].notna().sum():,}")
        if df['tmdbId'].notna().any():
            tmdb_ids = df[df['tmdbId'].notna()]['tmdbId']
            if tmdb_ids.dtype in ['int64', 'float64']:
                print(f"      Range: {tmdb_ids.min():.0f} to {tmdb_ids.max():.0f}")

# Summary comparison
print("\n" + "=" * 80)
print("SUMMARY COMPARISON:")
print("=" * 80)
for filename, df in datasets.items():
    print(f"\n{filename}:")
    print(f"   Total rows: {len(df):,}")
    if 'movieId' in df.columns:
        print(f"   Unique movieIds: {df['movieId'].nunique():,}")
    if 'imdbId' in df.columns:
        print(f"   Unique imdbIds: {df['imdbId'].notna().sum():,}")
    if 'tmdbId' in df.columns:
        print(f"   Unique tmdbIds: {df['tmdbId'].notna().sum():,}")

print("\n[OK] Phase 1, Step 1.5 COMPLETE!")
print("=" * 80)

