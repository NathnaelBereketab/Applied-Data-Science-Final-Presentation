"""
PHASE 1 - STEP 1.2: Load and Explore credits dataset (tmdb_5000_credits.csv or credits.csv)
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

print("=" * 80)
print("PHASE 1 - STEP 1.2: Exploring credits dataset")
print("=" * 80)

# Try to load tmdb_5000_credits.csv first, fallback to credits.csv
print("\n1. LOADING DATASET...")
df = None
for filename in ['tmdb_5000_credits.csv', 'credits.csv']:
    try:
        df = pd.read_csv(filename, low_memory=False, on_bad_lines='skip')
        print(f"   [OK] Loaded {filename} successfully!")
        break
    except FileNotFoundError:
        continue
    except TypeError:
        try:
            df = pd.read_csv(filename, low_memory=False, error_bad_lines=False, warn_bad_lines=False)
            print(f"   [OK] Loaded {filename} successfully!")
            break
        except:
            continue

if df is None:
    print("   [ERROR] Could not find credits dataset!")
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

# Check merge key (movie_id or id)
print("\n6. MERGE KEY ANALYSIS:")
merge_key = None
for key in ['movie_id', 'id', 'tmdb_id']:
    if key in df.columns:
        merge_key = key
        print(f"   Merge key found: '{key}'")
        print(f"   Unique movies: {df[key].nunique():,}")
        print(f"   Duplicate IDs: {(df[key].duplicated()).sum():,}")
        break

if merge_key is None:
    print("   [WARNING] No standard merge key found!")
    print("   Available columns:", list(df.columns))

# Sample of raw data
print("\n7. SAMPLE OF RAW DATA (First 2 rows):")
print(df.head(2).to_string())

# Analyze cast column (JSON format)
print("\n8. CAST COLUMN ANALYSIS:")
if 'cast' in df.columns:
    print(f"   Non-null cast entries: {df['cast'].notna().sum():,}")
    print(f"   Null cast entries: {df['cast'].isna().sum():,}")
    
    # Try to parse a sample cast entry
    sample_cast = df[df['cast'].notna()]['cast'].iloc[0] if df['cast'].notna().any() else None
    if sample_cast:
        try:
            cast_data = json.loads(sample_cast)
            print(f"   [OK] Cast is JSON format")
            print(f"   Sample cast entry structure:")
            if isinstance(cast_data, list) and len(cast_data) > 0:
                print(f"      Type: List with {len(cast_data)} actors")
                print(f"      First actor keys: {list(cast_data[0].keys())}")
                print(f"      Sample actor: {cast_data[0]}")
        except json.JSONDecodeError:
            print(f"   [WARNING] Cast column is not valid JSON")
            print(f"   Sample (first 200 chars): {str(sample_cast)[:200]}")
    
    # Count cast members per movie
    print("\n   Analyzing cast size per movie...")
    cast_sizes = []
    for idx, cast_str in enumerate(df['cast']):
        if pd.notna(cast_str):
            try:
                cast_data = json.loads(cast_str)
                if isinstance(cast_data, list):
                    cast_sizes.append(len(cast_data))
            except:
                pass
        if idx >= 100:  # Sample first 100 for speed
            break
    
    if cast_sizes:
        print(f"   Cast size (sample of first 100 movies):")
        print(f"      Mean: {np.mean(cast_sizes):.1f} actors")
        print(f"      Median: {np.median(cast_sizes):.1f} actors")
        print(f"      Min: {min(cast_sizes)} actors")
        print(f"      Max: {max(cast_sizes)} actors")
else:
    print("   [WARNING] 'cast' column not found!")

# Analyze crew column (JSON format)
print("\n9. CREW COLUMN ANALYSIS:")
if 'crew' in df.columns:
    print(f"   Non-null crew entries: {df['crew'].notna().sum():,}")
    print(f"   Null crew entries: {df['crew'].isna().sum():,}")
    
    # Try to parse a sample crew entry
    sample_crew = df[df['crew'].notna()]['crew'].iloc[0] if df['crew'].notna().any() else None
    if sample_crew:
        try:
            crew_data = json.loads(sample_crew)
            print(f"   [OK] Crew is JSON format")
            print(f"   Sample crew entry structure:")
            if isinstance(crew_data, list) and len(crew_data) > 0:
                print(f"      Type: List with {len(crew_data)} crew members")
                print(f"      First crew member keys: {list(crew_data[0].keys())}")
                print(f"      Sample crew member: {crew_data[0]}")
        except json.JSONDecodeError:
            print(f"   [WARNING] Crew column is not valid JSON")
            print(f"   Sample (first 200 chars): {str(sample_crew)[:200]}")
    
    # Analyze crew roles
    print("\n   Analyzing crew roles...")
    crew_roles = {}
    for idx, crew_str in enumerate(df['crew']):
        if pd.notna(crew_str):
            try:
                crew_data = json.loads(crew_str)
                if isinstance(crew_data, list):
                    for member in crew_data:
                        if isinstance(member, dict) and 'job' in member:
                            role = member['job']
                            crew_roles[role] = crew_roles.get(role, 0) + 1
            except:
                pass
        if idx >= 100:  # Sample first 100 for speed
            break
    
    if crew_roles:
        print(f"   Top crew roles (sample of first 100 movies):")
        sorted_roles = sorted(crew_roles.items(), key=lambda x: x[1], reverse=True)
        for role, count in sorted_roles[:10]:
            print(f"      {role}: {count}")
else:
    print("   [WARNING] 'crew' column not found!")

# Check for title column (for merging reference)
print("\n10. TITLE/IDENTIFIER COLUMNS:")
title_cols = [col for col in df.columns if 'title' in col.lower() or 'name' in col.lower()]
if title_cols:
    print(f"   Found title/name columns: {title_cols}")
    for col in title_cols:
        print(f"      {col}: {df[col].notna().sum():,} non-null values")
else:
    print("   No title/name columns found")

# Summary
print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"[OK] Total movies in credits dataset: {len(df):,}")
if merge_key:
    print(f"[OK] Unique movies (by {merge_key}): {df[merge_key].nunique():,}")
if 'cast' in df.columns:
    print(f"[OK] Movies with cast data: {df['cast'].notna().sum():,}")
if 'crew' in df.columns:
    print(f"[OK] Movies with crew data: {df['crew'].notna().sum():,}")

print("\n[OK] Phase 1, Step 1.2 COMPLETE!")
print("=" * 80)

