"""
PHASE 1 - STEP 1.3: Load and Explore keywords dataset (keywords.csv)
"""

import pandas as pd
import numpy as np
import json
import ast
from datetime import datetime

print("=" * 80)
print("PHASE 1 - STEP 1.3: Exploring keywords dataset")
print("=" * 80)

# Load the dataset
print("\n1. LOADING DATASET...")
try:
    df = pd.read_csv('keywords.csv', low_memory=False, on_bad_lines='skip')
    print(f"   [OK] Dataset loaded successfully!")
except FileNotFoundError:
    print("   [ERROR] keywords.csv not found!")
    exit(1)
except TypeError:
    try:
        df = pd.read_csv('keywords.csv', low_memory=False, error_bad_lines=False, warn_bad_lines=False)
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
print("\n5. MISSING VALUES:")
missing = df.isnull().sum().sort_values(ascending=False)
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Missing %': missing_pct
})
print(missing_df)

# Check merge key (id or movie_id)
print("\n6. MERGE KEY ANALYSIS:")
merge_key = None
for key in ['id', 'movie_id', 'tmdb_id']:
    if key in df.columns:
        merge_key = key
        print(f"   Merge key found: '{key}'")
        print(f"   Unique movies: {df[key].nunique():,}")
        print(f"   Duplicate IDs: {(df[key].duplicated()).sum():,}")
        print(f"   ID range: {df[key].min()} to {df[key].max()}")
        break

if merge_key is None:
    print("   [WARNING] No standard merge key found!")
    print("   Available columns:", list(df.columns))

# Sample of raw data
print("\n7. SAMPLE OF RAW DATA (First 2 rows):")
print(df.head(2).to_string())

# Analyze keywords column (JSON format)
print("\n8. KEYWORDS COLUMN ANALYSIS:")
if 'keywords' in df.columns:
    print(f"   Non-null keyword entries: {df['keywords'].notna().sum():,}")
    print(f"   Null keyword entries: {df['keywords'].isna().sum():,}")
    
    # Try to parse a sample keywords entry
    sample_keywords = df[df['keywords'].notna()]['keywords'].iloc[0] if df['keywords'].notna().any() else None
    if sample_keywords:
        try:
            # Try JSON first
            keywords_data = json.loads(sample_keywords)
            print(f"   [OK] Keywords is JSON format")
        except json.JSONDecodeError:
            try:
                # Try Python literal eval (for string representation of Python list)
                keywords_data = ast.literal_eval(sample_keywords)
                print(f"   [OK] Keywords is Python list format (using ast.literal_eval)")
            except:
                print(f"   [WARNING] Keywords column format unknown")
                print(f"   Sample (first 200 chars): {str(sample_keywords)[:200]}")
                keywords_data = None
        
        if keywords_data:
            print(f"   Sample keywords entry structure:")
            if isinstance(keywords_data, list) and len(keywords_data) > 0:
                print(f"      Type: List with {len(keywords_data)} keywords")
                print(f"      First keyword keys: {list(keywords_data[0].keys())}")
                print(f"      Sample keyword: {keywords_data[0]}")
                print(f"      Sample keywords (first 5):")
                for i, kw in enumerate(keywords_data[:5]):
                    print(f"         {i+1}. {kw}")
    
    # Count keywords per movie
    print("\n   Analyzing keywords per movie...")
    keyword_counts = []
    all_keyword_names = []
    for idx, keywords_str in enumerate(df['keywords']):
        if pd.notna(keywords_str):
            try:
                # Try JSON first, then ast.literal_eval
                try:
                    keywords_data = json.loads(keywords_str)
                except json.JSONDecodeError:
                    keywords_data = ast.literal_eval(keywords_str)
                
                if isinstance(keywords_data, list):
                    keyword_counts.append(len(keywords_data))
                    for kw in keywords_data:
                        if isinstance(kw, dict) and 'name' in kw:
                            all_keyword_names.append(kw['name'])
            except:
                pass
        if idx >= 500:  # Sample first 500 for speed
            break
    
    if keyword_counts:
        print(f"   Keywords per movie (sample of first 500 movies):")
        print(f"      Mean: {np.mean(keyword_counts):.1f} keywords")
        print(f"      Median: {np.median(keyword_counts):.1f} keywords")
        print(f"      Min: {min(keyword_counts)} keywords")
        print(f"      Max: {max(keyword_counts)} keywords")
    
    # Most common keywords
    if all_keyword_names:
        print(f"\n   Most common keywords (sample of first 500 movies):")
        from collections import Counter
        keyword_freq = Counter(all_keyword_names)
        top_keywords = keyword_freq.most_common(20)
        for keyword, count in top_keywords:
            print(f"      {keyword}: {count} movies")
else:
    print("   [WARNING] 'keywords' column not found!")

# Check for title column (for merging reference)
print("\n9. TITLE/IDENTIFIER COLUMNS:")
title_cols = [col for col in df.columns if 'title' in col.lower() or 'name' in col.lower()]
if title_cols:
    print(f"   Found title/name columns: {title_cols}")
    for col in title_cols:
        print(f"      {col}: {df[col].notna().sum():,} non-null values")
else:
    print("   No title/name columns found")

# Compare with other datasets
print("\n10. DATASET COMPARISON:")
if merge_key:
    print(f"   Movies in keywords dataset: {df[merge_key].nunique():,}")
    print(f"   [NOTE] Compare with:")
    print(f"      - movies_metadata.csv: 24,007 movies (2000-2025)")
    print(f"      - credits.csv: 4,803 movies")

# Summary
print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"[OK] Total movies in keywords dataset: {len(df):,}")
if merge_key:
    print(f"[OK] Unique movies (by {merge_key}): {df[merge_key].nunique():,}")
if 'keywords' in df.columns:
    print(f"[OK] Movies with keywords data: {df['keywords'].notna().sum():,}")
    print(f"[OK] Movies without keywords: {df['keywords'].isna().sum():,}")

print("\n[OK] Phase 1, Step 1.3 COMPLETE!")
print("=" * 80)

