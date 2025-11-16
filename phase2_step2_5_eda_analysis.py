"""
PHASE 2 - STEP 2.5: Exploratory Data Analysis (EDA)
Goal: Compare hits vs flops to discover patterns and the "formula" for success
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import ast
import json

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("=" * 80)
print("PHASE 2 - STEP 2.5: Exploratory Data Analysis (EDA)")
print("=" * 80)

# ============================================================================
# 1. LOAD DATASET WITH SUCCESS METRICS
# ============================================================================
print("\n1. LOADING DATASET WITH SUCCESS METRICS...")
try:
    df = pd.read_csv('movies_with_success_metrics.csv', low_memory=False)
    print(f"   [OK] Loaded {len(df):,} movies")
except FileNotFoundError:
    print("   [ERROR] movies_with_success_metrics.csv not found!")
    print("   [NOTE] Run phase2_step2_4_define_success_metric.py first")
    exit(1)

# Filter to labeled movies only (hits and flops)
df_labeled = df[df['is_hit'].notna()].copy()
hits = df_labeled[df_labeled['is_hit'] == 1].copy()
flops = df_labeled[df_labeled['is_hit'] == 0].copy()

print(f"   Hits: {len(hits):,} movies")
print(f"   Flops: {len(flops):,} movies")
print(f"   Total for analysis: {len(df_labeled):,} movies")

# ============================================================================
# 2. FINANCIAL ANALYSIS: BUDGET, REVENUE, ROI
# ============================================================================
print("\n2. FINANCIAL ANALYSIS: Budget, Revenue, ROI...")

financial_features = {
    'budget_final': 'Budget',
    'revenue': 'Revenue',
    'roi': 'ROI'
}

print("\n   Comparing Hits vs Flops:")
for col, name in financial_features.items():
    if col in df_labeled.columns:
        hit_data = hits[hits[col].notna() & (hits[col] > 0)][col]
        flop_data = flops[flops[col].notna() & (flops[col] > 0)][col]
        
        if len(hit_data) > 0 and len(flop_data) > 0:
            hit_mean = hit_data.mean()
            flop_mean = flop_data.mean()
            ratio = hit_mean / flop_mean if flop_mean > 0 else 0
            
            print(f"\n   {name}:")
            print(f"      Hits - Mean: ${hit_mean:,.0f}" if 'roi' not in col else f"      Hits - Mean: {hit_mean:.2f}x")
            print(f"      Flops - Mean: ${flop_mean:,.0f}" if 'roi' not in col else f"      Flops - Mean: {flop_mean:.2f}x")
            print(f"      Ratio: {ratio:.2f}x")

# Create financial comparison plot
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Budget comparison
if 'budget_final' in df_labeled.columns:
    budget_data = []
    labels = []
    for data, label in [(hits[hits['budget_final'] > 0]['budget_final'], 'Hits'),
                        (flops[flops['budget_final'] > 0]['budget_final'], 'Flops')]:
        if len(data) > 0:
            budget_data.append(data / 1e6)  # Convert to millions
            labels.append(label)
    
    if len(budget_data) == 2:
        axes[0].boxplot(budget_data, labels=labels)
        axes[0].set_title('Budget Distribution: Hits vs Flops', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Budget (Millions USD)', fontsize=12)
        axes[0].grid(True, alpha=0.3)

# Revenue comparison
if 'revenue' in df_labeled.columns:
    revenue_data = []
    labels = []
    for data, label in [(hits[hits['revenue'] > 0]['revenue'], 'Hits'),
                        (flops[flops['revenue'] > 0]['revenue'], 'Flops')]:
        if len(data) > 0:
            revenue_data.append(data / 1e6)  # Convert to millions
            labels.append(label)
    
    if len(revenue_data) == 2:
        axes[1].boxplot(revenue_data, labels=labels)
        axes[1].set_title('Revenue Distribution: Hits vs Flops', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Revenue (Millions USD)', fontsize=12)
        axes[1].grid(True, alpha=0.3)

# ROI comparison
if 'roi' in df_labeled.columns:
    roi_data = []
    labels = []
    for data, label in [(hits[hits['roi'].notna() & (hits['roi'] > 0)]['roi'], 'Hits'),
                        (flops[flops['roi'].notna() & (flops['roi'] > 0)]['roi'], 'Flops')]:
        if len(data) > 0:
            roi_data.append(data)
            labels.append(label)
    
    if len(roi_data) == 2:
        axes[2].boxplot(roi_data, labels=labels)
        axes[2].set_title('ROI Distribution: Hits vs Flops', fontsize=14, fontweight='bold')
        axes[2].set_ylabel('ROI (x)', fontsize=12)
        axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('eda_financial_comparison.png', dpi=300, bbox_inches='tight')
print("   [OK] Saved: eda_financial_comparison.png")
plt.close()

# ============================================================================
# 3. GENRE ANALYSIS
# ============================================================================
print("\n3. GENRE ANALYSIS...")

def parse_genres(genre_str):
    """Parse genres from JSON string"""
    if pd.isna(genre_str):
        return []
    try:
        genres = json.loads(genre_str)
        return [g.get('name', '') for g in genres if isinstance(g, dict)]
    except:
        try:
            genres = ast.literal_eval(genre_str)
            return [g.get('name', '') for g in genres if isinstance(g, dict)]
        except:
            return []

# Collect genres for hits and flops
hit_genres = []
flop_genres = []

for idx, row in hits.iterrows():
    genres = parse_genres(row.get('genres', ''))
    hit_genres.extend(genres)

for idx, row in flops.iterrows():
    genres = parse_genres(row.get('genres', ''))
    flop_genres.extend(genres)

# Count genre frequencies
hit_genre_counts = Counter(hit_genres)
flop_genre_counts = Counter(flop_genres)

# Get top genres
all_genres = set(hit_genre_counts.keys()) | set(flop_genre_counts.keys())
genre_comparison = []

for genre in all_genres:
    if genre:  # Skip empty strings
        hit_count = hit_genre_counts.get(genre, 0)
        flop_count = flop_genre_counts.get(genre, 0)
        total = hit_count + flop_count
        if total >= 50:  # Only genres with at least 50 movies
            hit_rate = (hit_count / total * 100) if total > 0 else 0
            genre_comparison.append({
                'Genre': genre,
                'Hits': hit_count,
                'Flops': flop_count,
                'Total': total,
                'Hit Rate %': hit_rate
            })

genre_df = pd.DataFrame(genre_comparison).sort_values('Hit Rate %', ascending=False)
print(f"\n   Top Genres by Hit Rate (min 50 movies):")
print(genre_df.head(10).to_string(index=False))

# Create genre comparison plot
if len(genre_df) > 0:
    top_genres = genre_df.head(10)
    fig, ax = plt.subplots(figsize=(12, 8))
    y_pos = np.arange(len(top_genres))
    ax.barh(y_pos, top_genres['Hit Rate %'], color='green', alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_genres['Genre'])
    ax.set_xlabel('Hit Rate (%)', fontsize=12)
    ax.set_title('Top 10 Genres by Hit Rate', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig('eda_genre_analysis.png', dpi=300, bbox_inches='tight')
    print("   [OK] Saved: eda_genre_analysis.png")
    plt.close()

# ============================================================================
# 4. RELEASE DATE ANALYSIS
# ============================================================================
print("\n4. RELEASE DATE ANALYSIS...")

# Convert release_date_parsed if needed
if 'release_date_parsed' in df_labeled.columns:
    df_labeled['release_date_parsed'] = pd.to_datetime(df_labeled['release_date_parsed'], errors='coerce')

# Release month analysis
if 'release_month' in df_labeled.columns:
    month_hit_rate = []
    for month in range(1, 13):
        month_movies = df_labeled[df_labeled['release_month'] == month]
        if len(month_movies) > 0:
            hit_rate = (month_movies['is_hit'] == 1).sum() / len(month_movies) * 100
            month_hit_rate.append({
                'Month': month,
                'Hit Rate %': hit_rate,
                'Count': len(month_movies)
            })
    
    month_df = pd.DataFrame(month_hit_rate)
    if len(month_df) > 0:
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_df['Month Name'] = month_df['Month'].apply(lambda x: month_names[x-1])
        print(f"\n   Hit Rate by Release Month:")
        print(month_df.sort_values('Hit Rate %', ascending=False).to_string(index=False))

# Release season analysis
if 'release_season' in df_labeled.columns:
    season_hit_rate = []
    for season in ['Winter', 'Spring', 'Summer', 'Fall']:
        season_movies = df_labeled[df_labeled['release_season'] == season]
        if len(season_movies) > 0:
            hit_rate = (season_movies['is_hit'] == 1).sum() / len(season_movies) * 100
            season_hit_rate.append({
                'Season': season,
                'Hit Rate %': hit_rate,
                'Count': len(season_movies)
            })
    
    season_df = pd.DataFrame(season_hit_rate)
    if len(season_df) > 0:
        print(f"\n   Hit Rate by Release Season:")
        print(season_df.sort_values('Hit Rate %', ascending=False).to_string(index=False))

# Create release date visualization
if 'release_season' in df_labeled.columns:
    fig, ax = plt.subplots(figsize=(10, 6))
    season_order = ['Winter', 'Spring', 'Summer', 'Fall']
    season_rates = []
    for season in season_order:
        season_movies = df_labeled[df_labeled['release_season'] == season]
        if len(season_movies) > 0:
            hit_rate = (season_movies['is_hit'] == 1).sum() / len(season_movies) * 100
            season_rates.append(hit_rate)
        else:
            season_rates.append(0)
    
    ax.bar(season_order, season_rates, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'], alpha=0.7)
    ax.set_ylabel('Hit Rate (%)', fontsize=12)
    ax.set_title('Hit Rate by Release Season', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('eda_release_season.png', dpi=300, bbox_inches='tight')
    print("   [OK] Saved: eda_release_season.png")
    plt.close()

# ============================================================================
# 5. CAST & CREW ANALYSIS
# ============================================================================
print("\n5. CAST & CREW ANALYSIS...")

# Cast size comparison
if 'cast_size' in df_labeled.columns:
    hit_cast = hits[hits['cast_size'].notna()]['cast_size']
    flop_cast = flops[flops['cast_size'].notna()]['cast_size']
    
    if len(hit_cast) > 0 and len(flop_cast) > 0:
        print(f"\n   Cast Size:")
        print(f"      Hits - Mean: {hit_cast.mean():.1f}, Median: {hit_cast.median():.1f}")
        print(f"      Flops - Mean: {flop_cast.mean():.1f}, Median: {flop_cast.median():.1f}")

# Crew size comparison
if 'crew_size' in df_labeled.columns:
    hit_crew = hits[hits['crew_size'].notna()]['crew_size']
    flop_crew = flops[flops['crew_size'].notna()]['crew_size']
    
    if len(hit_crew) > 0 and len(flop_crew) > 0:
        print(f"\n   Crew Size:")
        print(f"      Hits - Mean: {hit_crew.mean():.1f}, Median: {hit_crew.median():.1f}")
        print(f"      Flops - Mean: {flop_crew.mean():.1f}, Median: {flop_crew.median():.1f}")

# Director analysis
if 'director' in df_labeled.columns:
    hit_directors = hits[hits['director'].notna()]['director'].value_counts()
    flop_directors = flops[flops['director'].notna()]['director'].value_counts()
    
    # Find directors with multiple movies
    all_directors = set(hit_directors.index) | set(flop_directors.index)
    director_stats = []
    
    for director in all_directors:
        if director and director != 'None':
            hit_count = hit_directors.get(director, 0)
            flop_count = flop_directors.get(director, 0)
            total = hit_count + flop_count
            if total >= 5:  # Directors with at least 5 movies
                hit_rate = (hit_count / total * 100) if total > 0 else 0
                director_stats.append({
                    'Director': director,
                    'Hits': hit_count,
                    'Flops': flop_count,
                    'Total': total,
                    'Hit Rate %': hit_rate
                })
    
    director_df = pd.DataFrame(director_stats).sort_values('Hit Rate %', ascending=False)
    if len(director_df) > 0:
        print(f"\n   Top Directors by Hit Rate (min 5 movies):")
        print(director_df.head(10).to_string(index=False))

# ============================================================================
# 6. KEYWORDS ANALYSIS
# ============================================================================
print("\n6. KEYWORDS ANALYSIS...")

def parse_keywords(keyword_str):
    """Parse keywords from Python list string"""
    if pd.isna(keyword_str):
        return []
    try:
        keywords = ast.literal_eval(keyword_str)
        return [k.get('name', '') for k in keywords if isinstance(k, dict)]
    except:
        return []

# Collect keywords for hits and flops
hit_keywords = []
flop_keywords = []

for idx, row in hits.iterrows():
    keywords = parse_keywords(row.get('keywords', ''))
    hit_keywords.extend(keywords)

for idx, row in flops.iterrows():
    keywords = parse_keywords(row.get('keywords', ''))
    flop_keywords.extend(keywords)

# Count keyword frequencies
hit_keyword_counts = Counter(hit_keywords)
flop_keyword_counts = Counter(flop_keywords)

# Find keywords that appear more in hits vs flops
all_keywords = set(hit_keyword_counts.keys()) | set(flop_keyword_counts.keys())
keyword_comparison = []

for keyword in all_keywords:
    if keyword:  # Skip empty strings
        hit_count = hit_keyword_counts.get(keyword, 0)
        flop_count = flop_keyword_counts.get(keyword, 0)
        total = hit_count + flop_count
        if total >= 20:  # Only keywords with at least 20 movies
            hit_rate = (hit_count / total * 100) if total > 0 else 0
            keyword_comparison.append({
                'Keyword': keyword,
                'Hits': hit_count,
                'Flops': flop_count,
                'Total': total,
                'Hit Rate %': hit_rate
            })

keyword_df = pd.DataFrame(keyword_comparison).sort_values('Hit Rate %', ascending=False)
if len(keyword_df) > 0:
    print(f"\n   Top Keywords by Hit Rate (min 20 movies):")
    print(keyword_df.head(15).to_string(index=False))

# ============================================================================
# 7. NUMERIC FEATURES COMPARISON
# ============================================================================
print("\n7. NUMERIC FEATURES COMPARISON...")

numeric_features = ['runtime', 'vote_average', 'vote_count', 'popularity', 
                   'num_genres', 'num_keywords', 'num_production_companies']

comparison_stats = []
for feature in numeric_features:
    if feature in df_labeled.columns:
        hit_data = hits[hits[feature].notna()][feature]
        flop_data = flops[flops[feature].notna()][feature]
        
        if len(hit_data) > 0 and len(flop_data) > 0:
            hit_mean = hit_data.mean()
            flop_mean = flop_data.mean()
            ratio = hit_mean / flop_mean if flop_mean > 0 else 0
            
            comparison_stats.append({
                'Feature': feature,
                'Hits Mean': hit_mean,
                'Flops Mean': flop_mean,
                'Ratio': ratio
            })

if comparison_stats:
    stats_df = pd.DataFrame(comparison_stats)
    print(stats_df.to_string(index=False))

# ============================================================================
# 8. CORRELATION ANALYSIS
# ============================================================================
print("\n8. CORRELATION ANALYSIS...")

# Select numeric features for correlation
corr_features = ['is_hit', 'budget_final', 'revenue', 'roi', 'runtime', 
                 'vote_average', 'vote_count', 'popularity', 'num_genres', 
                 'cast_size', 'crew_size', 'num_keywords', 'num_production_companies']

corr_df = df_labeled[corr_features].select_dtypes(include=[np.number])
correlation = corr_df.corr()['is_hit'].sort_values(ascending=False)

print("\n   Correlation with Success (is_hit):")
for feature, corr in correlation.items():
    if feature != 'is_hit':
        print(f"      {feature}: {corr:.3f}")

# Create correlation heatmap
if len(corr_df.columns) > 1:
    fig, ax = plt.subplots(figsize=(12, 10))
    corr_matrix = corr_df.corr()
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('eda_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    print("   [OK] Saved: eda_correlation_heatmap.png")
    plt.close()

# ============================================================================
# 9. SAVE SUMMARY STATISTICS
# ============================================================================
print("\n9. SAVING SUMMARY STATISTICS...")

# Save genre analysis
if len(genre_df) > 0:
    genre_df.to_csv('eda_genre_analysis.csv', index=False)
    print("   [OK] Saved: eda_genre_analysis.csv")

# Save keyword analysis
if len(keyword_df) > 0:
    keyword_df.to_csv('eda_keyword_analysis.csv', index=False)
    print("   [OK] Saved: eda_keyword_analysis.csv")

# Save director analysis
if 'director' in df_labeled.columns and len(director_df) > 0:
    director_df.to_csv('eda_director_analysis.csv', index=False)
    print("   [OK] Saved: eda_director_analysis.csv")

# Save correlation analysis
correlation_df = pd.DataFrame({
    'Feature': correlation.index,
    'Correlation': correlation.values
}).sort_values('Correlation', ascending=False)
correlation_df.to_csv('eda_correlation_analysis.csv', index=False)
print("   [OK] Saved: eda_correlation_analysis.csv")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("EDA ANALYSIS SUMMARY:")
print("=" * 80)
print(f"Analyzed {len(df_labeled):,} movies ({len(hits):,} hits, {len(flops):,} flops)")
print(f"\nKey Findings:")
print(f"   - Financial: Hits have {hit_data.mean()/flop_data.mean():.1f}x higher budgets")
print(f"   - Genres: Top genre by hit rate identified")
print(f"   - Release: Seasonal patterns analyzed")
print(f"   - Cast/Crew: Size comparisons completed")
print(f"   - Keywords: Success-associated keywords identified")
print(f"   - Correlations: Feature importance ranked")

print("\nVisualizations Created:")
print("   - eda_financial_comparison.png")
print("   - eda_genre_analysis.png")
print("   - eda_release_season.png")
print("   - eda_correlation_heatmap.png")

print("\n[OK] Phase 2, Step 2.5 COMPLETE!")
print("=" * 80)

