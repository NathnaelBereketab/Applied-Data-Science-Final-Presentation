"""
PHASE 2 - STEP 2.3: Data Cleaning & Filtering
Goal: Clean the dataset, handle missing values, remove duplicates, prepare for analysis
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("PHASE 2 - STEP 2.3: Data Cleaning & Filtering")
print("=" * 80)

# ============================================================================
# 1. LOAD ENGINEERED DATASET
# ============================================================================
print("\n1. LOADING ENGINEERED DATASET...")
try:
    df = pd.read_csv('movies_engineered_phase2.csv', low_memory=False)
    print(f"   [OK] Loaded {len(df):,} movies")
    print(f"   Shape: {df.shape}")
except FileNotFoundError:
    print("   [ERROR] movies_engineered_phase2.csv not found!")
    print("   [NOTE] Run phase2_step2_2_feature_engineering.py first")
    exit(1)

initial_count = len(df)

# ============================================================================
# 2. VERIFY YEAR FILTER (2000-2025)
# ============================================================================
print("\n2. VERIFYING YEAR FILTER (2000-2025)...")
if 'release_year' in df.columns:
    year_range = (df['release_year'].min(), df['release_year'].max())
    print(f"   Current year range: {year_range[0]:.0f} to {year_range[1]:.0f}")
    
    # Filter to 2000-2025
    df = df[(df['release_year'] >= 2000) & (df['release_year'] <= 2025)].copy()
    print(f"   [OK] Filtered to 2000-2025: {len(df):,} movies")
    print(f"   Removed: {initial_count - len(df):,} movies outside range")
else:
    print("   [WARNING] release_year column not found")

# ============================================================================
# 3. REMOVE DUPLICATES
# ============================================================================
print("\n3. REMOVING DUPLICATES...")
initial_count = len(df)
duplicates = df.duplicated(subset=['id'], keep='first')
duplicate_count = duplicates.sum()
if duplicate_count > 0:
    df = df[~duplicates].copy()
    print(f"   [OK] Removed {duplicate_count:,} duplicate movies")
    print(f"   Remaining: {len(df):,} movies")
else:
    print(f"   [OK] No duplicates found")

# ============================================================================
# 4. HANDLE MISSING VALUES IN KEY COLUMNS
# ============================================================================
print("\n4. HANDLING MISSING VALUES...")

# Check missing values in key columns
key_columns = ['title', 'release_year', 'revenue', 'budget_final', 'director', 
               'lead_actor_1', 'num_genres', 'cast_size', 'crew_size']
print(f"   Missing values in key columns:")
for col in key_columns:
    if col in df.columns:
        missing = df[col].isna().sum()
        pct = (missing / len(df) * 100)
        if missing > 0:
            print(f"      {col}: {missing:,} ({pct:.1f}%)")

# Handle missing titles (remove if no title)
if 'title' in df.columns:
    missing_titles = df['title'].isna().sum()
    if missing_titles > 0:
        df = df[df['title'].notna()].copy()
        print(f"   [OK] Removed {missing_titles:,} movies without titles")

# Handle missing release_year (remove if no year)
if 'release_year' in df.columns:
    missing_year = df['release_year'].isna().sum()
    if missing_year > 0:
        df = df[df['release_year'].notna()].copy()
        print(f"   [OK] Removed {missing_year:,} movies without release year")

# ============================================================================
# 5. CLEAN FINANCIAL DATA
# ============================================================================
print("\n5. CLEANING FINANCIAL DATA...")

# Revenue: Set zeros to NaN (likely missing data, not actual zero revenue)
if 'revenue' in df.columns:
    zero_revenue = (df['revenue'] == 0).sum()
    print(f"   Movies with zero revenue: {zero_revenue:,}")
    # Keep zeros for now, but note them
    print(f"   [NOTE] Zero revenue kept (may be missing data)")

# Budget: Handle zeros and outliers
if 'budget_final' in df.columns:
    zero_budget = (df['budget_final'] == 0).sum()
    print(f"   Movies with zero budget: {zero_budget:,}")
    
    # Check for extreme outliers
    budget_positive = df[df['budget_final'] > 0]['budget_final']
    if len(budget_positive) > 0:
        q99 = budget_positive.quantile(0.99)
        outliers = (df['budget_final'] > q99).sum()
        print(f"   Budget outliers (>99th percentile): {outliers:,}")
        print(f"   99th percentile: ${q99:,.0f}")

# ROI: Handle extreme outliers
if 'roi' in df.columns:
    roi_positive = df[df['roi'].notna() & (df['roi'] > 0)]['roi']
    if len(roi_positive) > 0:
        q99 = roi_positive.quantile(0.99)
        extreme_roi = (df['roi'] > q99).sum()
        print(f"   ROI outliers (>99th percentile): {extreme_roi:,}")
        print(f"   99th percentile ROI: {q99:.2f}x")
        # Cap ROI at 99th percentile for analysis
        df.loc[df['roi'] > q99, 'roi'] = q99
        print(f"   [OK] Capped extreme ROI values at 99th percentile")

# ============================================================================
# 6. CLEAN TEXT DATA
# ============================================================================
print("\n6. CLEANING TEXT DATA...")

# Clean director names (remove extra whitespace)
if 'director' in df.columns:
    df['director'] = df['director'].astype(str).str.strip()
    df.loc[df['director'] == 'None', 'director'] = None
    df.loc[df['director'] == 'nan', 'director'] = None
    print(f"   [OK] Cleaned director names")

# Clean actor names
for col in ['lead_actor_1', 'lead_actor_2', 'lead_actor_3']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        df.loc[df[col] == 'None', col] = None
        df.loc[df[col] == 'nan', col] = None

# ============================================================================
# 7. HANDLE NUMERIC OUTLIERS
# ============================================================================
print("\n7. HANDLING NUMERIC OUTLIERS...")

# Runtime outliers
if 'runtime' in df.columns:
    runtime_positive = df[df['runtime'] > 0]['runtime']
    if len(runtime_positive) > 0:
        # Remove movies with runtime < 30 min (likely errors) or > 300 min (very rare)
        outliers = ((df['runtime'] < 30) | (df['runtime'] > 300)).sum()
        if outliers > 0:
            df = df[~((df['runtime'] < 30) | (df['runtime'] > 300))].copy()
            print(f"   [OK] Removed {outliers:,} movies with unrealistic runtime")

# Vote count outliers (very low vote counts may be unreliable)
if 'vote_count' in df.columns:
    low_votes = (df['vote_count'] < 10).sum()
    print(f"   Movies with < 10 votes: {low_votes:,} (may be less reliable)")

# ============================================================================
# 8. CREATE ANALYSIS-READY SUBSET
# ============================================================================
print("\n8. CREATING ANALYSIS-READY SUBSETS...")

# Subset 1: Movies with both budget and revenue (for ROI analysis)
df_with_roi = df[(df['budget_final'].notna()) & (df['budget_final'] > 0) &
                 (df['revenue'].notna()) & (df['revenue'] > 0)].copy()
print(f"   Movies with budget AND revenue: {len(df_with_roi):,}")

# Subset 2: Movies with success label (hits vs flops)
df_labeled = df[df['is_hit'].notna()].copy()
print(f"   Movies with success label (hits/flops): {len(df_labeled):,}")

# Subset 3: Movies with director
df_with_director = df[df['director'].notna()].copy()
print(f"   Movies with director: {len(df_with_director):,}")

# Subset 4: Movies with lead actors
df_with_actors = df[df['lead_actor_1'].notna()].copy()
print(f"   Movies with lead actors: {len(df_with_actors):,}")

# ============================================================================
# 9. FINAL DATA QUALITY CHECK
# ============================================================================
print("\n9. FINAL DATA QUALITY CHECK...")

print(f"   Final dataset size: {len(df):,} movies")
print(f"   Final columns: {df.shape[1]}")

# Check completeness of key features
print(f"\n   Feature Completeness:")
key_features = {
    'revenue': 'Revenue',
    'budget_final': 'Budget',
    'roi': 'ROI',
    'director': 'Director',
    'lead_actor_1': 'Lead Actor',
    'num_genres': 'Genres',
    'cast_size': 'Cast',
    'num_keywords': 'Keywords'
}

for col, name in key_features.items():
    if col in df.columns:
        non_null = df[col].notna().sum()
        pct = (non_null / len(df) * 100)
        print(f"      {name}: {non_null:,} ({pct:.1f}%)")

# ============================================================================
# 10. SAVE CLEANED DATASET
# ============================================================================
print(f"\n10. SAVING CLEANED DATASET...")
output_file = 'movies_cleaned_phase2.csv'
df.to_csv(output_file, index=False)
print(f"   [OK] Saved to {output_file}")

# Save analysis-ready subsets
print(f"\n   Saving analysis-ready subsets...")
df_with_roi.to_csv('movies_with_roi.csv', index=False)
df_labeled.to_csv('movies_labeled_hits_flops.csv', index=False)
print(f"   [OK] Saved subsets for analysis")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("CLEANING SUMMARY:")
print("=" * 80)
print(f"Initial movies: {initial_count:,}")
print(f"Final movies: {len(df):,}")
print(f"Removed: {initial_count - len(df):,} movies")

print(f"\nAnalysis-Ready Datasets:")
print(f"   Full cleaned dataset: {len(df):,} movies")
print(f"   With ROI: {len(df_with_roi):,} movies")
print(f"   With success labels: {len(df_labeled):,} movies")
print(f"   With director: {len(df_with_director):,} movies")
print(f"   With lead actors: {len(df_with_actors):,} movies")

print("\n[OK] Phase 2, Step 2.3 COMPLETE!")
print("=" * 80)

