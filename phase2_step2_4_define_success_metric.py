"""
PHASE 2 - STEP 2.4: Define Success Metric
Goal: Create a robust definition of "hit" vs "flop" for analysis
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("PHASE 2 - STEP 2.4: Defining Success Metric")
print("=" * 80)

# ============================================================================
# 1. LOAD CLEANED DATASET
# ============================================================================
print("\n1. LOADING CLEANED DATASET...")
try:
    df = pd.read_csv('movies_cleaned_phase2.csv', low_memory=False)
    print(f"   [OK] Loaded {len(df):,} movies")
except FileNotFoundError:
    print("   [ERROR] movies_cleaned_phase2.csv not found!")
    print("   [NOTE] Run phase2_step2_3_data_cleaning.py first")
    exit(1)

# ============================================================================
# 2. ANALYZE CURRENT SUCCESS METRICS
# ============================================================================
print("\n2. ANALYZING CURRENT SUCCESS METRICS...")

# Revenue distribution
if 'revenue' in df.columns:
    revenue_positive = df[df['revenue'] > 0]['revenue']
    if len(revenue_positive) > 0:
        print(f"\n   Revenue Statistics (positive revenue only):")
        print(f"      Count: {len(revenue_positive):,} movies")
        print(f"      Mean: ${revenue_positive.mean():,.0f}")
        print(f"      Median: ${revenue_positive.median():,.0f}")
        print(f"      25th percentile: ${revenue_positive.quantile(0.25):,.0f}")
        print(f"      75th percentile: ${revenue_positive.quantile(0.75):,.0f}")
        print(f"      90th percentile: ${revenue_positive.quantile(0.90):,.0f}")

# ROI distribution
if 'roi' in df.columns:
    roi_positive = df[df['roi'].notna() & (df['roi'] > 0)]['roi']
    if len(roi_positive) > 0:
        print(f"\n   ROI Statistics:")
        print(f"      Count: {len(roi_positive):,} movies")
        print(f"      Mean: {roi_positive.mean():.2f}x")
        print(f"      Median: {roi_positive.median():.2f}x")
        print(f"      25th percentile: {roi_positive.quantile(0.25):.2f}x")
        print(f"      75th percentile: {roi_positive.quantile(0.75):.2f}x")
        print(f"      90th percentile: {roi_positive.quantile(0.90):.2f}x")

# Vote average distribution
if 'vote_average' in df.columns:
    votes_with_data = df[df['vote_average'].notna() & (df['vote_count'] >= 10)]['vote_average']
    if len(votes_with_data) > 0:
        print(f"\n   Vote Average Statistics (movies with 10+ votes):")
        print(f"      Count: {len(votes_with_data):,} movies")
        print(f"      Mean: {votes_with_data.mean():.2f}")
        print(f"      Median: {votes_with_data.median():.2f}")
        print(f"      25th percentile: {votes_with_data.quantile(0.25):.2f}")
        print(f"      75th percentile: {votes_with_data.quantile(0.75):.2f}")
        print(f"      90th percentile: {votes_with_data.quantile(0.90):.2f}")

# Budget distribution
if 'budget_final' in df.columns:
    budget_positive = df[df['budget_final'] > 0]['budget_final']
    if len(budget_positive) > 0:
        print(f"\n   Budget Statistics (positive budget only):")
        print(f"      Count: {len(budget_positive):,} movies")
        print(f"      Mean: ${budget_positive.mean():,.0f}")
        print(f"      Median: ${budget_positive.median():,.0f}")

# ============================================================================
# 3. CREATE MULTIPLE SUCCESS DEFINITIONS
# ============================================================================
print("\n3. CREATING MULTIPLE SUCCESS DEFINITIONS...")

# Definition 1: Based on ROI (if budget and revenue available)
print("\n   Definition 1: ROI-Based")
df['is_hit_roi'] = None
if 'roi' in df.columns:
    # Hit: ROI >= 2.0 (made at least 2x the budget)
    # Flop: ROI < 1.0 (lost money)
    df.loc[df['roi'] >= 2.0, 'is_hit_roi'] = 1
    df.loc[(df['roi'].notna()) & (df['roi'] < 1.0), 'is_hit_roi'] = 0
    roi_hits = (df['is_hit_roi'] == 1).sum()
    roi_flops = (df['is_hit_roi'] == 0).sum()
    print(f"      Hits (ROI >= 2.0): {roi_hits:,}")
    print(f"      Flops (ROI < 1.0): {roi_flops:,}")
    print(f"      Undefined: {(df['is_hit_roi'].isna()).sum():,}")

# Definition 2: Based on Revenue Threshold (median)
print("\n   Definition 2: Revenue-Based (Median Threshold)")
df['is_hit_revenue'] = None
if 'revenue' in df.columns:
    revenue_median = df[df['revenue'] > 0]['revenue'].median()
    print(f"      Median revenue threshold: ${revenue_median:,.0f}")
    df.loc[df['revenue'] > revenue_median, 'is_hit_revenue'] = 1
    df.loc[(df['revenue'] > 0) & (df['revenue'] <= revenue_median), 'is_hit_revenue'] = 0
    rev_hits = (df['is_hit_revenue'] == 1).sum()
    rev_flops = (df['is_hit_revenue'] == 0).sum()
    print(f"      Hits (revenue > median): {rev_hits:,}")
    print(f"      Flops (revenue <= median): {rev_flops:,}")
    print(f"      Undefined (zero revenue): {(df['is_hit_revenue'].isna()).sum():,}")

# Definition 3: Based on Vote Average (quality metric)
print("\n   Definition 3: Vote-Based (Quality Metric)")
df['is_hit_votes'] = None
if 'vote_average' in df.columns:
    # Only use movies with sufficient votes (>= 50 votes for reliability)
    votes_reliable = df[df['vote_count'] >= 50]
    if len(votes_reliable) > 0:
        vote_median = votes_reliable['vote_average'].median()
        print(f"      Median vote average (50+ votes): {vote_median:.2f}")
        df.loc[(df['vote_count'] >= 50) & (df['vote_average'] > vote_median), 'is_hit_votes'] = 1
        df.loc[(df['vote_count'] >= 50) & (df['vote_average'] <= vote_median), 'is_hit_votes'] = 0
        vote_hits = (df['is_hit_votes'] == 1).sum()
        vote_flops = (df['is_hit_votes'] == 0).sum()
        print(f"      Hits (vote > median): {vote_hits:,}")
        print(f"      Flops (vote <= median): {vote_flops:,}")
        print(f"      Undefined (< 50 votes): {(df['is_hit_votes'].isna()).sum():,}")

# Definition 4: Combined (ROI if available, else revenue)
print("\n   Definition 4: Combined (ROI Preferred, Revenue Fallback)")
df['is_hit_combined'] = None
# Use ROI if available
if 'roi' in df.columns:
    df.loc[df['roi'] >= 2.0, 'is_hit_combined'] = 1
    df.loc[(df['roi'].notna()) & (df['roi'] < 1.0), 'is_hit_combined'] = 0

# Fill remaining with revenue-based
if 'revenue' in df.columns:
    revenue_median = df[df['revenue'] > 0]['revenue'].median()
    remaining = df['is_hit_combined'].isna()
    df.loc[remaining & (df['revenue'] > revenue_median), 'is_hit_combined'] = 1
    df.loc[remaining & (df['revenue'] > 0) & (df['revenue'] <= revenue_median), 'is_hit_combined'] = 0

combined_hits = (df['is_hit_combined'] == 1).sum()
combined_flops = (df['is_hit_combined'] == 0).sum()
print(f"      Hits: {combined_hits:,}")
print(f"      Flops: {combined_flops:,}")
print(f"      Undefined: {(df['is_hit_combined'].isna()).sum():,}")

# Definition 5: High Revenue Threshold (Top 25%)
print("\n   Definition 5: High Revenue Threshold (Top 25%)")
df['is_hit_top25'] = None
if 'revenue' in df.columns:
    revenue_75th = df[df['revenue'] > 0]['revenue'].quantile(0.75)
    print(f"      75th percentile threshold: ${revenue_75th:,.0f}")
    df.loc[df['revenue'] > revenue_75th, 'is_hit_top25'] = 1
    df.loc[(df['revenue'] > 0) & (df['revenue'] <= revenue_75th), 'is_hit_top25'] = 0
    top25_hits = (df['is_hit_top25'] == 1).sum()
    top25_flops = (df['is_hit_top25'] == 0).sum()
    print(f"      Hits (top 25%): {top25_hits:,}")
    print(f"      Flops (bottom 75%): {top25_flops:,}")

# ============================================================================
# 4. COMPARE DEFINITIONS
# ============================================================================
print("\n4. COMPARING SUCCESS DEFINITIONS...")

comparison_data = []
for col in ['is_hit_roi', 'is_hit_revenue', 'is_hit_votes', 'is_hit_combined', 'is_hit_top25']:
    if col in df.columns:
        hits = (df[col] == 1).sum()
        flops = (df[col] == 0).sum()
        total = hits + flops
        if total > 0:
            hit_pct = (hits / total * 100)
            comparison_data.append({
                'Definition': col.replace('is_hit_', ''),
                'Hits': hits,
                'Flops': flops,
                'Total Labeled': total,
                'Hit %': f"{hit_pct:.1f}%"
            })

comparison_df = pd.DataFrame(comparison_data)
print(comparison_df.to_string(index=False))

# ============================================================================
# 5. SELECT PRIMARY SUCCESS METRIC
# ============================================================================
print("\n5. SELECTING PRIMARY SUCCESS METRIC...")
print("   [DECISION] Using 'is_hit_combined' as primary metric")
print("   Reason: Combines ROI (most accurate) with revenue fallback (broader coverage)")

df['is_hit'] = df['is_hit_combined'].copy()

# Create a more detailed success score (0-1 scale)
print("\n   Creating success score (0.0 to 1.0)...")
df['success_score'] = None

# For movies with ROI
if 'roi' in df.columns:
    roi_movies = df['roi'].notna()
    # Normalize ROI to 0-1 scale (cap at 10x ROI = 1.0)
    df.loc[roi_movies, 'success_score'] = np.clip(df.loc[roi_movies, 'roi'] / 10.0, 0, 1)

# For movies with revenue only (normalize by 90th percentile)
if 'revenue' in df.columns:
    revenue_90th = df[df['revenue'] > 0]['revenue'].quantile(0.90)
    revenue_only = df['success_score'].isna() & (df['revenue'] > 0)
    df.loc[revenue_only, 'success_score'] = np.clip(df.loc[revenue_only, 'revenue'] / revenue_90th, 0, 1)

print(f"   Movies with success score: {df['success_score'].notna().sum():,}")

# ============================================================================
# 6. ANALYZE SUCCESS DISTRIBUTION
# ============================================================================
print("\n6. ANALYZING SUCCESS DISTRIBUTION...")

if 'is_hit' in df.columns:
    hits = df[df['is_hit'] == 1]
    flops = df[df['is_hit'] == 0]
    
    print(f"\n   HITS ({len(hits):,} movies):")
    if 'budget_final' in df.columns:
        hit_budget = hits[hits['budget_final'] > 0]['budget_final']
        if len(hit_budget) > 0:
            print(f"      Mean budget: ${hit_budget.mean():,.0f}")
            print(f"      Median budget: ${hit_budget.median():,.0f}")
    
    if 'revenue' in df.columns:
        hit_revenue = hits[hits['revenue'] > 0]['revenue']
        if len(hit_revenue) > 0:
            print(f"      Mean revenue: ${hit_revenue.mean():,.0f}")
            print(f"      Median revenue: ${hit_revenue.median():,.0f}")
    
    if 'roi' in df.columns:
        hit_roi = hits[hits['roi'].notna()]['roi']
        if len(hit_roi) > 0:
            print(f"      Mean ROI: {hit_roi.mean():.2f}x")
            print(f"      Median ROI: {hit_roi.median():.2f}x")
    
    print(f"\n   FLOPS ({len(flops):,} movies):")
    if 'budget_final' in df.columns:
        flop_budget = flops[flops['budget_final'] > 0]['budget_final']
        if len(flop_budget) > 0:
            print(f"      Mean budget: ${flop_budget.mean():,.0f}")
            print(f"      Median budget: ${flop_budget.median():,.0f}")
    
    if 'revenue' in df.columns:
        flop_revenue = flops[flops['revenue'] > 0]['revenue']
        if len(flop_revenue) > 0:
            print(f"      Mean revenue: ${flop_revenue.mean():,.0f}")
            print(f"      Median revenue: ${flop_revenue.median():,.0f}")
    
    if 'roi' in df.columns:
        flop_roi = flops[flops['roi'].notna()]['roi']
        if len(flop_roi) > 0:
            print(f"      Mean ROI: {flop_roi.mean():.2f}x")
            print(f"      Median ROI: {flop_roi.median():.2f}x")

# ============================================================================
# 7. SAVE DATASET WITH SUCCESS METRICS
# ============================================================================
print(f"\n7. SAVING DATASET WITH SUCCESS METRICS...")
output_file = 'movies_with_success_metrics.csv'
df.to_csv(output_file, index=False)
print(f"   [OK] Saved to {output_file}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUCCESS METRIC DEFINITION SUMMARY:")
print("=" * 80)
print(f"Primary Metric: 'is_hit' (combined ROI + revenue)")
if 'is_hit' in df.columns:
    hits = (df['is_hit'] == 1).sum()
    flops = (df['is_hit'] == 0).sum()
    total_labeled = hits + flops
    print(f"   Hits: {hits:,} ({hits/total_labeled*100:.1f}%)")
    print(f"   Flops: {flops:,} ({flops/total_labeled*100:.1f}%)")
    print(f"   Total labeled: {total_labeled:,} movies")

print(f"\nAdditional Metrics Created:")
print(f"   - is_hit_roi: ROI-based (ROI >= 2.0 = hit)")
print(f"   - is_hit_revenue: Revenue-based (above median = hit)")
print(f"   - is_hit_votes: Vote-based (above median = hit)")
print(f"   - is_hit_top25: Top 25% revenue = hit")
print(f"   - success_score: Continuous score (0.0 to 1.0)")

print("\n[OK] Phase 2, Step 2.4 COMPLETE!")
print("=" * 80)

