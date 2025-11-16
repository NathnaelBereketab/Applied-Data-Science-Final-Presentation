"""
PHASE 2 - STEP 2.1: Merge All Useful CSVs
Goal: Combine movies_metadata + credits + keywords + imdb_movies using links.csv for ID mapping
"""

import pandas as pd
import numpy as np
import json
import ast
from datetime import datetime

print("=" * 80)
print("PHASE 2 - STEP 2.1: Merging All Datasets")
print("=" * 80)

# ============================================================================
# 1. LOAD MOVIES_METADATA (PRIMARY DATASET)
# ============================================================================
print("\n1. LOADING movies_metadata.csv...")
try:
    df_movies = pd.read_csv('movies_metadata.csv', low_memory=False, on_bad_lines='skip')
    print(f"   [OK] Loaded {len(df_movies):,} movies")
except TypeError:
    try:
        df_movies = pd.read_csv('movies_metadata.csv', low_memory=False, error_bad_lines=False, warn_bad_lines=False)
        print(f"   [OK] Loaded {len(df_movies):,} movies")
    except:
        df_movies = pd.read_csv('movies_metadata.csv', engine='python', on_bad_lines='skip', error_bad_lines=False)
        print(f"   [OK] Loaded {len(df_movies):,} movies")
except Exception as e:
    print(f"   [ERROR] Failed to load: {str(e)}")
    exit(1)

# Extract year and filter to 2000-2025
print("\n   Extracting year and filtering to 2000-2025...")
df_movies['release_date_parsed'] = pd.to_datetime(df_movies['release_date'], errors='coerce')
df_movies['release_year'] = df_movies['release_date_parsed'].dt.year
df_movies = df_movies[(df_movies['release_year'] >= 2000) & (df_movies['release_year'] <= 2025)].copy()
print(f"   [OK] Filtered to {len(df_movies):,} movies (2000-2025)")

# Convert id to numeric for merging (handle string IDs)
print("\n   Converting id column for merging...")
df_movies['id'] = pd.to_numeric(df_movies['id'], errors='coerce')
df_movies = df_movies[df_movies['id'].notna()].copy()
print(f"   [OK] {len(df_movies):,} movies with valid numeric IDs")

# Convert revenue to numeric (already should be, but ensure)
df_movies['revenue'] = pd.to_numeric(df_movies['revenue'], errors='coerce')

# Convert popularity to numeric
df_movies['popularity'] = pd.to_numeric(df_movies['popularity'], errors='coerce')

print(f"\n   movies_metadata shape: {df_movies.shape}")
print(f"   Key columns: id, title, release_year, revenue, budget, popularity, vote_average")

# ============================================================================
# 2. LOAD LINKS (FOR ID MAPPING)
# ============================================================================
print("\n2. LOADING links.csv for ID mapping...")
try:
    df_links = pd.read_csv('links.csv', low_memory=False, on_bad_lines='skip')
    print(f"   [OK] Loaded {len(df_links):,} ID mappings")
    print(f"   Columns: {list(df_links.columns)}")
except Exception as e:
    print(f"   [WARNING] Could not load links.csv: {str(e)}")
    df_links = None

# ============================================================================
# 3. MERGE WITH CREDITS
# ============================================================================
print("\n3. MERGING WITH credits.csv...")
try:
    # Try credits.csv first, then tmdb_5000_credits.csv
    try:
        df_credits = pd.read_csv('credits.csv', low_memory=False, on_bad_lines='skip')
        print(f"   [OK] Loaded credits.csv: {len(df_credits):,} movies")
    except:
        df_credits = pd.read_csv('tmdb_5000_credits.csv', low_memory=False, on_bad_lines='skip')
        print(f"   [OK] Loaded tmdb_5000_credits.csv: {len(df_credits):,} movies")
    
    print(f"   Credits columns: {list(df_credits.columns)}")
    
    # Check which ID column exists
    merge_key_credits = None
    for key in ['movie_id', 'id']:
        if key in df_credits.columns:
            merge_key_credits = key
            break
    
    if merge_key_credits:
        # Convert to numeric
        df_credits[merge_key_credits] = pd.to_numeric(df_credits[merge_key_credits], errors='coerce')
        df_credits = df_credits[df_credits[merge_key_credits].notna()].copy()
        
        # Merge on id (movies_metadata) = merge_key_credits (credits)
        print(f"   Merging on id = {merge_key_credits}...")
        df_merged = df_movies.merge(df_credits, left_on='id', right_on=merge_key_credits, how='left', suffixes=('', '_credits'))
        print(f"   [OK] Merged! New shape: {df_merged.shape}")
        
        # Check if cast column exists (might be named differently)
        cast_col = None
        for col in ['cast', 'Cast', 'CAST']:
            if col in df_merged.columns:
                cast_col = col
                break
        
        if cast_col:
            print(f"   Movies with credits: {df_merged[cast_col].notna().sum():,}")
            print(f"   Movies without credits: {df_merged[cast_col].isna().sum():,}")
        else:
            print(f"   [NOTE] Cast column not found, but merge completed")
    else:
        print(f"   [WARNING] No merge key found in credits, skipping")
        df_merged = df_movies.copy()
except Exception as e:
    print(f"   [WARNING] Could not merge credits: {str(e)}")
    import traceback
    traceback.print_exc()
    df_merged = df_movies.copy()

# ============================================================================
# 4. MERGE WITH KEYWORDS
# ============================================================================
print("\n4. MERGING WITH keywords.csv...")
try:
    df_keywords = pd.read_csv('keywords.csv', low_memory=False, on_bad_lines='skip')
    print(f"   [OK] Loaded {len(df_keywords):,} movies with keywords")
    
    # Convert id to numeric
    df_keywords['id'] = pd.to_numeric(df_keywords['id'], errors='coerce')
    df_keywords = df_keywords[df_keywords['id'].notna()].copy()
    
    # Remove duplicates (keep first)
    df_keywords = df_keywords.drop_duplicates(subset=['id'], keep='first')
    print(f"   [OK] {len(df_keywords):,} unique movies after removing duplicates")
    
    # Merge on id
    print(f"   Merging on id...")
    df_merged = df_merged.merge(df_keywords, on='id', how='left', suffixes=('', '_keywords'))
    print(f"   [OK] Merged! New shape: {df_merged.shape}")
    print(f"   Movies with keywords: {df_merged['keywords'].notna().sum():,}")
    print(f"   Movies without keywords: {df_merged['keywords'].isna().sum():,}")
except Exception as e:
    print(f"   [WARNING] Could not merge keywords: {str(e)}")

# ============================================================================
# 5. MERGE WITH IMDB_MOVIES (using links or title matching)
# ============================================================================
print("\n5. MERGING WITH imdb_movies.csv...")
try:
    df_imdb = pd.read_csv('imdb_movies.csv', low_memory=False, on_bad_lines='skip')
    print(f"   [OK] Loaded {len(df_imdb):,} movies from IMDb")
    
    # Try to merge using links.csv if available
    if df_links is not None:
        print(f"   Using links.csv for ID mapping...")
        # Convert imdbId in links to match imdb_movies (might need title matching)
        # For now, try title + date matching
        print(f"   Attempting title + date matching...")
        
        # Parse date_x in imdb_movies (try multiple formats)
        df_imdb['date_parsed'] = pd.to_datetime(df_imdb['date_x'], errors='coerce')
        df_imdb['imdb_year'] = df_imdb['date_parsed'].dt.year
        
        # Filter imdb_movies to 2000-2025
        df_imdb_filtered = df_imdb[(df_imdb['imdb_year'] >= 2000) & (df_imdb['imdb_year'] <= 2025)].copy()
        print(f"   [OK] {len(df_imdb_filtered):,} IMDb movies from 2000-2025")
        
        # Merge on title and year (fuzzy matching)
        print(f"   Merging on title + year...")
        df_merged = df_merged.merge(
            df_imdb_filtered[['names', 'imdb_year', 'score', 'budget_x', 'revenue', 'genre', 'country']],
            left_on=['title', 'release_year'],
            right_on=['names', 'imdb_year'],
            how='left',
            suffixes=('', '_imdb')
        )
        print(f"   [OK] Merged! New shape: {df_merged.shape}")
        print(f"   Movies with IMDb data: {df_merged['score'].notna().sum():,}")
        print(f"   Movies with IMDb budget: {df_merged['budget_x'].notna().sum():,}")
    else:
        print(f"   [NOTE] No links.csv available, skipping IMDb merge")
except Exception as e:
    print(f"   [WARNING] Could not merge IMDb movies: {str(e)}")

# ============================================================================
# 6. SUMMARY OF MERGED DATASET
# ============================================================================
print("\n" + "=" * 80)
print("MERGE SUMMARY:")
print("=" * 80)
print(f"Final dataset shape: {df_merged.shape}")
print(f"Total movies: {len(df_merged):,}")

print(f"\nData Completeness:")
# Check for cast column (might have different name)
cast_col = None
for col in ['cast', 'Cast', 'CAST']:
    if col in df_merged.columns:
        cast_col = col
        break
if cast_col:
    print(f"   Movies with credits (cast/crew): {df_merged[cast_col].notna().sum():,} ({df_merged[cast_col].notna().sum()/len(df_merged)*100:.1f}%)")
else:
    print(f"   Movies with credits: [Column not found]")

if 'keywords' in df_merged.columns:
    print(f"   Movies with keywords: {df_merged['keywords'].notna().sum():,} ({df_merged['keywords'].notna().sum()/len(df_merged)*100:.1f}%)")
if 'revenue' in df_merged.columns:
    print(f"   Movies with revenue: {df_merged['revenue'].notna().sum():,} ({df_merged['revenue'].notna().sum()/len(df_merged)*100:.1f}%)")
if 'budget_x' in df_merged.columns:
    print(f"   Movies with IMDb budget: {df_merged['budget_x'].notna().sum():,} ({df_merged['budget_x'].notna().sum()/len(df_merged)*100:.1f}%)")
if 'score' in df_merged.columns:
    print(f"   Movies with IMDb score: {df_merged['score'].notna().sum():,} ({df_merged['score'].notna().sum()/len(df_merged)*100:.1f}%)")

print(f"\nKey Columns Available:")
key_cols = ['id', 'title', 'release_year', 'revenue', 'budget', 'popularity', 'vote_average', 'vote_count', 
            'cast', 'crew', 'keywords', 'genres']
if 'budget_x' in df_merged.columns:
    key_cols.append('budget_x')
if 'score' in df_merged.columns:
    key_cols.append('score')
available_cols = [col for col in key_cols if col in df_merged.columns]
print(f"   {', '.join(available_cols)}")

# Save merged dataset
print(f"\n6. SAVING MERGED DATASET...")
output_file = 'merged_movies_phase2.csv'
df_merged.to_csv(output_file, index=False)
print(f"   [OK] Saved to {output_file}")

print("\n[OK] Phase 2, Step 2.1 COMPLETE!")
print("=" * 80)

