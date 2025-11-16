"""
PHASE 2 - STEP 2.2: Feature Engineering
Goal: Extract features from JSON columns, create new features, prepare data for analysis
"""

import pandas as pd
import numpy as np
import json
import ast
from datetime import datetime
from collections import Counter

print("=" * 80)
print("PHASE 2 - STEP 2.2: Feature Engineering")
print("=" * 80)

# ============================================================================
# 1. LOAD MERGED DATASET
# ============================================================================
print("\n1. LOADING MERGED DATASET...")
try:
    df = pd.read_csv('merged_movies_phase2.csv', low_memory=False)
    print(f"   [OK] Loaded {len(df):,} movies")
    print(f"   Shape: {df.shape}")
except FileNotFoundError:
    print("   [ERROR] merged_movies_phase2.csv not found!")
    print("   [NOTE] Run phase2_step2_1_merge_datasets.py first")
    exit(1)

# ============================================================================
# 2. HANDLE BUDGET CONVERSION
# ============================================================================
print("\n2. HANDLING BUDGET DATA...")
# Try to convert budget from movies_metadata (handle corrupted row)
print("   Converting budget column from movies_metadata...")
def safe_convert_budget(val):
    """Safely convert budget value to numeric"""
    if pd.isna(val):
        return None
    try:
        val_str = str(val)
        # Skip extremely long strings (corrupted data)
        if len(val_str) > 50:
            return None
        result = float(val_str)
        # Filter unreasonable values
        if result < 0 or result > 1e12:
            return None
        return result
    except:
        return None

# Apply safe conversion
df['budget_numeric'] = df['budget'].apply(safe_convert_budget)

# Use IMDb budget if available and movies_metadata budget is missing
print("   Combining budget sources...")
df['budget_final'] = df['budget_numeric']
# Fill missing with IMDb budget
missing_budget = df['budget_final'].isna()
df.loc[missing_budget, 'budget_final'] = df.loc[missing_budget, 'budget_x']

budget_count = df['budget_final'].notna().sum()
print(f"   [OK] Movies with budget data: {budget_count:,} ({budget_count/len(df)*100:.1f}%)")

# ============================================================================
# 3. CALCULATE ROI (Return on Investment)
# ============================================================================
print("\n3. CALCULATING ROI...")
df['roi'] = None
valid_financial = df[(df['budget_final'].notna()) & (df['budget_final'] > 0) & 
                     (df['revenue'].notna()) & (df['revenue'] > 0)]
df.loc[valid_financial.index, 'roi'] = (
    valid_financial['revenue'] / valid_financial['budget_final']
)
roi_count = df['roi'].notna().sum()
print(f"   [OK] Movies with ROI calculated: {roi_count:,} ({roi_count/len(df)*100:.1f}%)")
if roi_count > 0:
    roi_data = df[df['roi'].notna()]['roi']
    print(f"   ROI statistics:")
    print(f"      Mean: {roi_data.mean():.2f}x")
    print(f"      Median: {roi_data.median():.2f}x")
    print(f"      Max: {roi_data.max():.2f}x")

# ============================================================================
# 4. EXTRACT RELEASE DATE FEATURES
# ============================================================================
print("\n4. EXTRACTING RELEASE DATE FEATURES...")
# Recreate release_date_parsed if needed
if 'release_date' in df.columns:
    if 'release_date_parsed' not in df.columns or df['release_date_parsed'].dtype != 'datetime64[ns]':
        df['release_date_parsed'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    df['release_month'] = df['release_date_parsed'].dt.month
    df['release_day'] = df['release_date_parsed'].dt.day
    df['release_day_of_week'] = df['release_date_parsed'].dt.dayofweek  # 0=Monday, 6=Sunday
    
    # Create season feature
    def get_season(month):
        if pd.isna(month):
            return None
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    df['release_season'] = df['release_month'].apply(get_season)
    print(f"   [OK] Extracted: release_month, release_day, release_day_of_week, release_season")
else:
    print("   [WARNING] release_date column not found")

# ============================================================================
# 5. PARSE GENRES
# ============================================================================
print("\n5. PARSING GENRES...")
if 'genres' in df.columns:
    all_genres = []
    genre_counts = []
    
    genre_parse_errors = 0
    for idx, genres_str in enumerate(df['genres']):
        if pd.notna(genres_str) and str(genres_str).strip() != '':
            try:
                # Try JSON first, then ast.literal_eval (for Python list format)
                try:
                    genres_data = json.loads(genres_str)
                except json.JSONDecodeError:
                    genres_data = ast.literal_eval(genres_str)
                
                if isinstance(genres_data, list) and len(genres_data) > 0:
                    genre_list = [g.get('name', '') for g in genres_data if isinstance(g, dict)]
                    all_genres.extend(genre_list)
                    genre_counts.append(len(genre_list))
                else:
                    genre_counts.append(0)
            except json.JSONDecodeError:
                genre_parse_errors += 1
                genre_counts.append(0)
            except:
                genre_parse_errors += 1
                genre_counts.append(0)
        else:
            genre_counts.append(0)
    
    if genre_parse_errors > 0:
        print(f"   [WARNING] {genre_parse_errors} genre entries had parsing errors")
    
    df['num_genres'] = genre_counts
    print(f"   [OK] Extracted genre count per movie")
    print(f"   Mean genres per movie: {np.mean(genre_counts):.1f}")
    
    # Get top genres
    if all_genres:
        top_genres = Counter(all_genres).most_common(10)
        print(f"   Top 10 genres:")
        for genre, count in top_genres:
            print(f"      {genre}: {count:,} movies")

# ============================================================================
# 6. EXTRACT CAST FEATURES
# ============================================================================
print("\n6. EXTRACTING CAST FEATURES...")
if 'cast' in df.columns:
    lead_actors = []
    cast_sizes = []
    actor_ids = []
    
    parse_errors = 0
    for idx, cast_str in enumerate(df['cast']):
        if pd.notna(cast_str) and str(cast_str).strip() != '':
            try:
                # Try JSON first, then ast.literal_eval (for Python list format)
                try:
                    cast_data = json.loads(cast_str)
                except json.JSONDecodeError:
                    cast_data = ast.literal_eval(cast_str)
                
                if isinstance(cast_data, list) and len(cast_data) > 0:
                    cast_sizes.append(len(cast_data))
                    # Get lead actors (order 0, 1, 2)
                    leads = [actor for actor in cast_data if isinstance(actor, dict) and actor.get('order', 999) < 3]
                    lead_names = [actor.get('name', '') for actor in leads[:3]]
                    lead_actors.append(lead_names)
                    # Collect all actor IDs for popularity calculation
                    actor_ids.extend([actor.get('id') for actor in cast_data if isinstance(actor, dict) and actor.get('id')])
                else:
                    cast_sizes.append(0)
                    lead_actors.append([])
            except json.JSONDecodeError as e:
                parse_errors += 1
                cast_sizes.append(0)
                lead_actors.append([])
            except Exception as e:
                parse_errors += 1
                cast_sizes.append(0)
                lead_actors.append([])
        else:
            cast_sizes.append(0)
            lead_actors.append([])
    
    if parse_errors > 0:
        print(f"   [WARNING] {parse_errors} cast entries had parsing errors")
    
    df['cast_size'] = cast_sizes
    df['lead_actor_1'] = [leads[0] if len(leads) > 0 else None for leads in lead_actors]
    df['lead_actor_2'] = [leads[1] if len(leads) > 1 else None for leads in lead_actors]
    df['lead_actor_3'] = [leads[2] if len(leads) > 2 else None for leads in lead_actors]
    
    print(f"   [OK] Extracted cast features")
    print(f"   Mean cast size: {np.mean(cast_sizes):.1f} actors")
    print(f"   Movies with lead actors: {df['lead_actor_1'].notna().sum():,}")

# ============================================================================
# 7. EXTRACT CREW FEATURES (DIRECTOR, PRODUCERS)
# ============================================================================
print("\n7. EXTRACTING CREW FEATURES...")
if 'crew' in df.columns:
    directors = []
    producers = []
    writers = []
    crew_sizes = []
    
    crew_parse_errors = 0
    for idx, crew_str in enumerate(df['crew']):
        if pd.notna(crew_str) and str(crew_str).strip() != '':
            try:
                # Try JSON first, then ast.literal_eval (for Python list format)
                try:
                    crew_data = json.loads(crew_str)
                except json.JSONDecodeError:
                    crew_data = ast.literal_eval(crew_str)
                
                if isinstance(crew_data, list) and len(crew_data) > 0:
                    crew_sizes.append(len(crew_data))
                    # Extract director
                    director = None
                    for member in crew_data:
                        if isinstance(member, dict) and member.get('job') == 'Director':
                            director = member.get('name', '')
                            break
                    directors.append(director)
                    
                    # Extract producers
                    producer_list = [member.get('name', '') for member in crew_data 
                                   if isinstance(member, dict) and 'Producer' in member.get('job', '')]
                    producers.append(producer_list)
                    
                    # Extract writers
                    writer_list = [member.get('name', '') for member in crew_data 
                                 if isinstance(member, dict) and 'Writer' in member.get('job', '')]
                    writers.append(writer_list)
                else:
                    crew_sizes.append(0)
                    directors.append(None)
                    producers.append([])
                    writers.append([])
            except json.JSONDecodeError as e:
                crew_parse_errors += 1
                crew_sizes.append(0)
                directors.append(None)
                producers.append([])
                writers.append([])
            except Exception as e:
                crew_parse_errors += 1
                crew_sizes.append(0)
                directors.append(None)
                producers.append([])
                writers.append([])
        else:
            crew_sizes.append(0)
            directors.append(None)
            producers.append([])
            writers.append([])
    
    if crew_parse_errors > 0:
        print(f"   [WARNING] {crew_parse_errors} crew entries had parsing errors")
    
    df['director'] = directors
    df['num_producers'] = [len(p) for p in producers]
    df['num_writers'] = [len(w) for w in writers]
    df['crew_size'] = crew_sizes
    
    print(f"   [OK] Extracted crew features")
    print(f"   Movies with director: {df['director'].notna().sum():,}")
    print(f"   Mean crew size: {np.mean(crew_sizes):.1f}")

# ============================================================================
# 8. PARSE KEYWORDS
# ============================================================================
print("\n8. PARSING KEYWORDS...")
if 'keywords' in df.columns:
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
                    keyword_names = [kw.get('name', '') if isinstance(kw, dict) else str(kw) for kw in keywords_data]
                    all_keyword_names.extend(keyword_names)
                else:
                    keyword_counts.append(0)
            except:
                keyword_counts.append(0)
        else:
            keyword_counts.append(0)
    
    df['num_keywords'] = keyword_counts
    print(f"   [OK] Extracted keyword count")
    print(f"   Mean keywords per movie: {np.mean(keyword_counts):.1f}")

# ============================================================================
# 9. PARSE PRODUCTION COMPANIES
# ============================================================================
print("\n9. PARSING PRODUCTION COMPANIES...")
if 'production_companies' in df.columns:
    company_counts = []
    
    for idx, companies_str in enumerate(df['production_companies']):
        if pd.notna(companies_str) and str(companies_str).strip() != '':
            try:
                # Try JSON first, then ast.literal_eval (for Python list format)
                try:
                    companies_data = json.loads(companies_str)
                except json.JSONDecodeError:
                    companies_data = ast.literal_eval(companies_str)
                
                if isinstance(companies_data, list):
                    company_counts.append(len(companies_data))
                else:
                    company_counts.append(0)
            except:
                company_counts.append(0)
        else:
            company_counts.append(0)
    
    df['num_production_companies'] = company_counts
    print(f"   [OK] Extracted production company count")
    print(f"   Mean companies per movie: {np.mean(company_counts):.1f}")

# ============================================================================
# 10. CREATE SUCCESS TARGET VARIABLE
# ============================================================================
print("\n10. CREATING SUCCESS TARGET VARIABLE...")
# Define success based on ROI (if available) or revenue threshold
df['is_hit'] = None

# Method 1: Based on ROI (if budget and revenue available)
roi_hits = df[(df['roi'].notna()) & (df['roi'] >= 2.0)]  # ROI >= 2x
df.loc[roi_hits.index, 'is_hit'] = 1

# Method 2: Based on revenue threshold (for movies without budget)
# Use median revenue as threshold
revenue_median = df[df['revenue'] > 0]['revenue'].median()
revenue_hits = df[(df['is_hit'].isna()) & (df['revenue'].notna()) & (df['revenue'] > revenue_median)]
df.loc[revenue_hits.index, 'is_hit'] = 1

# Method 3: Mark flops (ROI < 1.0 or revenue below threshold)
roi_flops = df[(df['roi'].notna()) & (df['roi'] < 1.0)]
df.loc[roi_flops.index, 'is_hit'] = 0

revenue_flops = df[(df['is_hit'].isna()) & (df['revenue'].notna()) & (df['revenue'] <= revenue_median) & (df['revenue'] > 0)]
df.loc[revenue_flops.index, 'is_hit'] = 0

hit_count = (df['is_hit'] == 1).sum()
flop_count = (df['is_hit'] == 0).sum()
print(f"   [OK] Created success target variable")
print(f"   Hits: {hit_count:,} ({hit_count/len(df)*100:.1f}%)")
print(f"   Flops: {flop_count:,} ({flop_count/len(df)*100:.1f}%)")
print(f"   Undefined: {(df['is_hit'].isna()).sum():,}")

# ============================================================================
# 11. SUMMARY OF ENGINEERED FEATURES
# ============================================================================
print("\n" + "=" * 80)
print("FEATURE ENGINEERING SUMMARY:")
print("=" * 80)

new_features = [
    'budget_final', 'roi', 'release_month', 'release_season', 'release_day_of_week',
    'num_genres', 'cast_size', 'lead_actor_1', 'lead_actor_2', 'lead_actor_3',
    'director', 'num_producers', 'num_writers', 'crew_size',
    'num_keywords', 'num_production_companies', 'is_hit'
]

print(f"\nNew Features Created ({len(new_features)}):")
for i, feat in enumerate(new_features, 1):
    if feat in df.columns:
        non_null = df[feat].notna().sum()
        print(f"   {i:2d}. {feat}: {non_null:,} non-null ({non_null/len(df)*100:.1f}%)")
    else:
        print(f"   {i:2d}. {feat}: [NOT CREATED]")

print(f"\nTotal columns in dataset: {df.shape[1]}")
print(f"Total movies: {len(df):,}")

# Save engineered dataset
print(f"\n11. SAVING ENGINEERED DATASET...")
output_file = 'movies_engineered_phase2.csv'
df.to_csv(output_file, index=False)
print(f"   [OK] Saved to {output_file}")

print("\n[OK] Phase 2, Step 2.2 COMPLETE!")
print("=" * 80)

