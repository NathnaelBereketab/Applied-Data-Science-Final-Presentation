"""
PHASE 3 - STEP 3.1: Prepare Data for Modeling
Goal: Prepare datasets for machine learning models (full features + limited features)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("PHASE 3 - STEP 3.1: Prepare Data for Modeling")
print("=" * 80)

# ============================================================================
# 1. LOAD DATASET WITH SUCCESS METRICS
# ============================================================================
print("\n1. LOADING DATASET WITH SUCCESS METRICS...")
try:
    df = pd.read_csv('movies_with_success_metrics.csv', low_memory=False)
    print(f"   [OK] Loaded {len(df):,} movies")
    print(f"   Shape: {df.shape}")
except FileNotFoundError:
    print("   [ERROR] movies_with_success_metrics.csv not found!")
    print("   [NOTE] Run phase2_step2_4_define_success_metric.py first")
    exit(1)

# ============================================================================
# 2. FILTER TO LABELED MOVIES ONLY (HITS VS FLOPS)
# ============================================================================
print("\n2. FILTERING TO LABELED MOVIES (HITS VS FLOPS)...")
df_labeled = df[df['is_hit'].notna()].copy()
print(f"   Labeled movies: {len(df_labeled):,}")
print(f"   Hits: {(df_labeled['is_hit'] == 1).sum():,}")
print(f"   Flops: {(df_labeled['is_hit'] == 0).sum():,}")

# ============================================================================
# 3. DEFINE FEATURE SETS
# ============================================================================
print("\n3. DEFINING FEATURE SETS...")

# Full feature set (all available information)
full_features = [
    # Financial
    'budget_final', 'revenue', 'roi',
    # Release date
    'release_year', 'release_month', 'release_season', 'release_day_of_week',
    # Content
    'runtime', 'num_genres', 'num_keywords', 'num_production_companies',
    # Cast/Crew
    'cast_size', 'crew_size', 'num_producers', 'num_writers',
    # Ratings
    'vote_average', 'vote_count', 'popularity',
    # Categorical (will be encoded)
    'director', 'lead_actor_1', 'lead_actor_2', 'lead_actor_3'
]

# Limited feature set (basic metadata only - proves formula works)
limited_features = [
    # Financial (basic)
    'budget_final',
    # Release date (basic)
    'release_month', 'release_season',
    # Content (basic)
    'runtime', 'num_genres',
    # Cast/Crew (basic)
    'cast_size', 'crew_size',
    # Ratings (basic)
    'vote_average', 'popularity'
]

print(f"\n   Full Feature Set ({len(full_features)} features):")
for i, feat in enumerate(full_features, 1):
    print(f"      {i:2d}. {feat}")

print(f"\n   Limited Feature Set ({len(limited_features)} features):")
for i, feat in enumerate(limited_features, 1):
    print(f"      {i:2d}. {feat}")

# ============================================================================
# 4. CHECK FEATURE AVAILABILITY
# ============================================================================
print("\n4. CHECKING FEATURE AVAILABILITY...")

def check_features(feature_list, df):
    """Check which features exist and have data"""
    available = []
    missing = []
    for feat in feature_list:
        if feat in df.columns:
            non_null = df[feat].notna().sum()
            pct = (non_null / len(df) * 100)
            if pct > 50:  # At least 50% coverage
                available.append((feat, non_null, pct))
            else:
                missing.append((feat, non_null, pct))
        else:
            missing.append((feat, 0, 0))
    return available, missing

full_available, full_missing = check_features(full_features, df_labeled)
limited_available, limited_missing = check_features(limited_features, df_labeled)

print(f"\n   Full Feature Set:")
print(f"      Available: {len(full_available)}/{len(full_features)}")
for feat, count, pct in full_available:
    print(f"         {feat}: {count:,} ({pct:.1f}%)")
if full_missing:
    print(f"      Missing/Low Coverage:")
    for feat, count, pct in full_missing:
        print(f"         {feat}: {count:,} ({pct:.1f}%)")

print(f"\n   Limited Feature Set:")
print(f"      Available: {len(limited_available)}/{len(limited_features)}")
for feat, count, pct in limited_available:
    print(f"         {feat}: {count:,} ({pct:.1f}%)")
if limited_missing:
    print(f"      Missing/Low Coverage:")
    for feat, count, pct in limited_missing:
        print(f"         {feat}: {count:,} ({pct:.1f}%)")

# ============================================================================
# 5. PREPARE FULL FEATURE DATASET
# ============================================================================
print("\n5. PREPARING FULL FEATURE DATASET...")

# Select features that exist and have good coverage
full_features_clean = [feat for feat, _, _ in full_available]

# Create feature matrix
X_full = df_labeled[full_features_clean].copy()
y = df_labeled['is_hit'].copy()

print(f"   Initial shape: {X_full.shape}")

# Handle missing values
print(f"\n   Handling missing values...")
missing_before = X_full.isnull().sum().sum()
print(f"      Missing values before: {missing_before:,}")

# For numeric features: fill with median
numeric_cols = X_full.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    if X_full[col].isnull().any():
        median_val = X_full[col].median()
        X_full[col].fillna(median_val, inplace=True)
        print(f"      Filled {col} with median: {median_val:.2f}")

# For categorical features: fill with 'Unknown'
categorical_cols = X_full.select_dtypes(include=['object']).columns
for col in categorical_cols:
    if X_full[col].isnull().any():
        X_full[col].fillna('Unknown', inplace=True)
        print(f"      Filled {col} with 'Unknown'")

missing_after = X_full.isnull().sum().sum()
print(f"      Missing values after: {missing_after:,}")

# Encode categorical variables
print(f"\n   Encoding categorical variables...")
label_encoders = {}
for col in categorical_cols:
    if col in X_full.columns:
        le = LabelEncoder()
        X_full[col] = le.fit_transform(X_full[col].astype(str))
        label_encoders[col] = le
        print(f"      Encoded {col}: {len(le.classes_)} unique values")

print(f"   Final shape: {X_full.shape}")

# ============================================================================
# 6. PREPARE LIMITED FEATURE DATASET
# ============================================================================
print("\n6. PREPARING LIMITED FEATURE DATASET...")

# Select features that exist and have good coverage
limited_features_clean = [feat for feat, _, _ in limited_available]

# Create feature matrix
X_limited = df_labeled[limited_features_clean].copy()

print(f"   Initial shape: {X_limited.shape}")

# Handle missing values (same approach)
print(f"\n   Handling missing values...")
missing_before = X_limited.isnull().sum().sum()
print(f"      Missing values before: {missing_before:,}")

# Fill numeric with median
numeric_cols_lim = X_limited.select_dtypes(include=[np.number]).columns
for col in numeric_cols_lim:
    if X_limited[col].isnull().any():
        median_val = X_limited[col].median()
        X_limited[col].fillna(median_val, inplace=True)
        print(f"      Filled {col} with median: {median_val:.2f}")

# Encode categorical variables (release_season)
categorical_cols_lim = X_limited.select_dtypes(include=['object']).columns
if len(categorical_cols_lim) > 0:
    print(f"\n   Encoding categorical variables...")
    for col in categorical_cols_lim:
        if col in X_limited.columns:
            le = LabelEncoder()
            X_limited[col] = le.fit_transform(X_limited[col].astype(str))
            print(f"      Encoded {col}: {len(le.classes_)} unique values")

missing_after = X_limited.isnull().sum().sum()
print(f"      Missing values after: {missing_after:,}")

print(f"   Final shape: {X_limited.shape}")

# ============================================================================
# 7. CREATE TRAIN/TEST SPLITS
# ============================================================================
print("\n7. CREATING TRAIN/TEST SPLITS...")

# Full feature split
X_full_train, X_full_test, y_full_train, y_full_test = train_test_split(
    X_full, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n   Full Feature Set:")
print(f"      Train: {len(X_full_train):,} movies ({len(X_full_train)/len(X_full)*100:.1f}%)")
print(f"      Test: {len(X_full_test):,} movies ({len(X_full_test)/len(X_full)*100:.1f}%)")
print(f"      Train - Hits: {(y_full_train == 1).sum():,}, Flops: {(y_full_train == 0).sum():,}")
print(f"      Test - Hits: {(y_full_test == 1).sum():,}, Flops: {(y_full_test == 0).sum():,}")

# Limited feature split
X_limited_train, X_limited_test, y_limited_train, y_limited_test = train_test_split(
    X_limited, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n   Limited Feature Set:")
print(f"      Train: {len(X_limited_train):,} movies ({len(X_limited_train)/len(X_limited)*100:.1f}%)")
print(f"      Test: {len(X_limited_test):,} movies ({len(X_limited_test)/len(X_limited)*100:.1f}%)")
print(f"      Train - Hits: {(y_limited_train == 1).sum():,}, Flops: {(y_limited_train == 0).sum():,}")
print(f"      Test - Hits: {(y_limited_test == 1).sum():,}, Flops: {(y_limited_test == 0).sum():,}")

# ============================================================================
# 8. SAVE PREPARED DATASETS
# ============================================================================
print("\n8. SAVING PREPARED DATASETS...")

# Save full feature datasets
X_full_train.to_csv('X_full_train.csv', index=False)
X_full_test.to_csv('X_full_test.csv', index=False)
y_full_train.to_csv('y_full_train.csv', index=False)
y_full_test.to_csv('y_full_test.csv', index=False)
print("   [OK] Saved full feature datasets")

# Save limited feature datasets
X_limited_train.to_csv('X_limited_train.csv', index=False)
X_limited_test.to_csv('X_limited_test.csv', index=False)
y_limited_train.to_csv('y_limited_train.csv', index=False)
y_limited_test.to_csv('y_limited_test.csv', index=False)
print("   [OK] Saved limited feature datasets")

# Save feature lists
with open('full_features_list.txt', 'w') as f:
    f.write('\n'.join(full_features_clean))
with open('limited_features_list.txt', 'w') as f:
    f.write('\n'.join(limited_features_clean))
print("   [OK] Saved feature lists")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("DATA PREPARATION SUMMARY:")
print("=" * 80)
print(f"Total labeled movies: {len(df_labeled):,}")
print(f"Full feature set: {len(full_features_clean)} features")
print(f"Limited feature set: {len(limited_features_clean)} features")
print(f"\nTrain/Test Split: 80/20")
print(f"   Train: {len(X_full_train):,} movies")
print(f"   Test: {len(X_full_test):,} movies")

print(f"\nFull Feature Set Features:")
for i, feat in enumerate(full_features_clean, 1):
    print(f"   {i:2d}. {feat}")

print(f"\nLimited Feature Set Features:")
for i, feat in enumerate(limited_features_clean, 1):
    print(f"   {i:2d}. {feat}")

print("\n[OK] Phase 3, Step 3.1 COMPLETE!")
print("=" * 80)

