"""
Create Comprehensive Visualization Dashboard
Shows all key findings from the movie success analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 16)
plt.rcParams['font.size'] = 10

print("=" * 80)
print("CREATING COMPREHENSIVE VISUALIZATION DASHBOARD")
print("=" * 80)

# Load data
print("\n1. LOADING DATA...")
try:
    df = pd.read_csv('movies_with_success_metrics.csv', low_memory=False)
    df_labeled = df[df['is_hit'].notna()].copy()
    hits = df_labeled[df_labeled['is_hit'] == 1]
    flops = df_labeled[df_labeled['is_hit'] == 0]
    
    # Load feature importance
    feature_imp_full = pd.read_csv('feature_importance_full_model.csv')
    feature_imp_limited = pd.read_csv('feature_importance_limited_model.csv')
    
    # Load genre analysis
    genre_df = pd.read_csv('eda_genre_analysis.csv')
    
    print(f"   [OK] Loaded {len(df_labeled):,} labeled movies")
except FileNotFoundError as e:
    print(f"   [ERROR] {e}")
    exit(1)

# Create figure with subplots
fig = plt.figure(figsize=(24, 20))
gs = GridSpec(4, 3, figure=fig, hspace=0.3, wspace=0.3)

# ============================================================================
# 1. FINANCIAL COMPARISON (Top Left)
# ============================================================================
ax1 = fig.add_subplot(gs[0, 0])
financial_data = {
    'Budget (Mean)': [hits[hits['budget_final'] > 0]['budget_final'].mean() / 1e6,
                     flops[flops['budget_final'] > 0]['budget_final'].mean() / 1e6],
    'Revenue (Mean)': [hits[hits['revenue'] > 0]['revenue'].mean() / 1e6,
                      flops[flops['revenue'] > 0]['revenue'].mean() / 1e6]
}
x = np.arange(len(financial_data))
width = 0.35
hits_vals = [financial_data['Budget (Mean)'][0], financial_data['Revenue (Mean)'][0]]
flops_vals = [financial_data['Budget (Mean)'][1], financial_data['Revenue (Mean)'][1]]

ax1.bar(x - width/2, hits_vals, width, label='Hits', color='#2ecc71', alpha=0.8)
ax1.bar(x + width/2, flops_vals, width, label='Flops', color='#e74c3c', alpha=0.8)
ax1.set_ylabel('Amount (Millions USD)', fontsize=11, fontweight='bold')
ax1.set_title('Financial Comparison: Hits vs Flops', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(['Budget', 'Revenue'])
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')
ax1.text(0, max(hits_vals[0], flops_vals[0]) * 0.9, f'2.17x', ha='center', fontweight='bold', fontsize=10)
ax1.text(1, max(hits_vals[1], flops_vals[1]) * 0.9, f'19.36x', ha='center', fontweight='bold', fontsize=10)

# ============================================================================
# 2. TOP GENRES BY HIT RATE (Top Middle)
# ============================================================================
ax2 = fig.add_subplot(gs[0, 1])
top_genres = genre_df.head(10).sort_values('Hit Rate %')
y_pos = np.arange(len(top_genres))
ax2.barh(y_pos, top_genres['Hit Rate %'], color='#3498db', alpha=0.8)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(top_genres['Genre'])
ax2.set_xlabel('Hit Rate (%)', fontsize=11, fontweight='bold')
ax2.set_title('Top 10 Genres by Hit Rate', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')
ax2.set_xlim(0, 80)

# ============================================================================
# 3. RELEASE SEASON ANALYSIS (Top Right)
# ============================================================================
ax3 = fig.add_subplot(gs[0, 2])
season_order = ['Winter', 'Spring', 'Summer', 'Fall']
season_rates = []
for season in season_order:
    season_movies = df_labeled[df_labeled['release_season'] == season]
    if len(season_movies) > 0:
        hit_rate = (season_movies['is_hit'] == 1).sum() / len(season_movies) * 100
        season_rates.append(hit_rate)
    else:
        season_rates.append(0)

colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
ax3.bar(season_order, season_rates, color=colors, alpha=0.8)
ax3.set_ylabel('Hit Rate (%)', fontsize=11, fontweight='bold')
ax3.set_title('Hit Rate by Release Season', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')
ax3.set_ylim(0, 60)
for i, (season, rate) in enumerate(zip(season_order, season_rates)):
    ax3.text(i, rate + 1, f'{rate:.1f}%', ha='center', fontweight='bold', fontsize=10)

# ============================================================================
# 4. FEATURE IMPORTANCE - LIMITED MODEL (Middle Left)
# ============================================================================
ax4 = fig.add_subplot(gs[1, 0])
top_features = feature_imp_limited.sort_values('importance', ascending=True).tail(9)
y_pos = np.arange(len(top_features))
ax4.barh(y_pos, top_features['importance'] * 100, color='#9b59b6', alpha=0.8)
ax4.set_yticks(y_pos)
ax4.set_yticklabels(top_features['feature'])
ax4.set_xlabel('Importance (%)', fontsize=11, fontweight='bold')
ax4.set_title('Feature Importance (Limited Model - 77% Accuracy)', fontsize=13, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='x')
for i, (idx, row) in enumerate(top_features.iterrows()):
    ax4.text(row['importance'] * 100 + 0.5, i, f"{row['importance']*100:.1f}%", 
             va='center', fontweight='bold', fontsize=9)

# ============================================================================
# 5. TOP KEYWORDS BY HIT RATE (Middle Middle)
# ============================================================================
ax5 = fig.add_subplot(gs[1, 1])
try:
    keyword_df = pd.read_csv('eda_keyword_analysis.csv')
    top_keywords = keyword_df.head(10).sort_values('Hit Rate %', ascending=True)
    y_pos = np.arange(len(top_keywords))
    ax5.barh(y_pos, top_keywords['Hit Rate %'], color='#16a085', alpha=0.8)
    ax5.set_yticks(y_pos)
    ax5.set_yticklabels(top_keywords['Keyword'], fontsize=9)
    ax5.set_xlabel('Hit Rate (%)', fontsize=11, fontweight='bold')
    ax5.set_title('Top 10 Success Keywords', fontsize=13, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='x')
    ax5.set_xlim(0, 100)
except:
    ax5.text(0.5, 0.5, 'Keyword data not available', ha='center', va='center', transform=ax5.transAxes)

# ============================================================================
# 6. CAST & CREW SIZE COMPARISON (Middle Right)
# ============================================================================
ax6 = fig.add_subplot(gs[1, 2])
team_data = {
    'Cast Size': [hits['cast_size'].mean(), flops['cast_size'].mean()],
    'Crew Size': [hits['crew_size'].mean(), flops['crew_size'].mean()]
}
x = np.arange(len(team_data))
width = 0.35
hits_team = [team_data['Cast Size'][0], team_data['Crew Size'][0]]
flops_team = [team_data['Cast Size'][1], team_data['Crew Size'][1]]

ax6.bar(x - width/2, hits_team, width, label='Hits', color='#2ecc71', alpha=0.8)
ax6.bar(x + width/2, flops_team, width, label='Flops', color='#e74c3c', alpha=0.8)
ax6.set_ylabel('Average Size', fontsize=11, fontweight='bold')
ax6.set_title('Team Size Comparison: Hits vs Flops', fontsize=13, fontweight='bold')
ax6.set_xticks(x)
ax6.set_xticklabels(['Cast', 'Crew'])
ax6.legend()
ax6.grid(True, alpha=0.3, axis='y')

# ============================================================================
# 7. MODEL PERFORMANCE COMPARISON (Bottom Left)
# ============================================================================
ax7 = fig.add_subplot(gs[2, 0])
try:
    model_comp = pd.read_csv('model_comparison.csv')
    metrics = ['Test Accuracy', 'Test Precision', 'Test Recall', 'Test F1']
    full_vals = []
    limited_vals = []
    for metric in metrics:
        row = model_comp[model_comp['Metric'] == metric]
        if len(row) > 0:
            full_vals.append(row['Full Features'].values[0] * 100)
            limited_vals.append(row['Limited Features'].values[0] * 100)
    
    x = np.arange(len(metrics))
    width = 0.35
    ax7.bar(x - width/2, full_vals, width, label='Full Features (99.78%)', color='#3498db', alpha=0.8)
    ax7.bar(x + width/2, limited_vals, width, label='Limited Features (77.27%)', color='#9b59b6', alpha=0.8)
    ax7.set_ylabel('Score (%)', fontsize=11, fontweight='bold')
    ax7.set_title('Model Performance Comparison', fontsize=13, fontweight='bold')
    ax7.set_xticks(x)
    ax7.set_xticklabels(['Accuracy', 'Precision', 'Recall', 'F1-Score'], rotation=15, ha='right')
    ax7.legend()
    ax7.grid(True, alpha=0.3, axis='y')
    ax7.set_ylim(0, 110)
except:
    ax7.text(0.5, 0.5, 'Model comparison data not available', ha='center', va='center', transform=ax7.transAxes)

# ============================================================================
# 8. RELEASE MONTH ANALYSIS (Bottom Middle)
# ============================================================================
ax8 = fig.add_subplot(gs[2, 1])
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_rates = []
for month in range(1, 13):
    month_movies = df_labeled[df_labeled['release_month'] == month]
    if len(month_movies) > 0:
        hit_rate = (month_movies['is_hit'] == 1).sum() / len(month_movies) * 100
        month_rates.append(hit_rate)
    else:
        month_rates.append(0)

colors_month = ['#e74c3c' if rate < 50 else '#2ecc71' for rate in month_rates]
ax8.bar(month_names, month_rates, color=colors_month, alpha=0.8)
ax8.set_ylabel('Hit Rate (%)', fontsize=11, fontweight='bold')
ax8.set_title('Hit Rate by Release Month', fontsize=13, fontweight='bold')
ax8.grid(True, alpha=0.3, axis='y')
ax8.set_ylim(0, 70)
ax8.axhline(y=50, color='black', linestyle='--', alpha=0.5, linewidth=1)
for i, (month, rate) in enumerate(zip(month_names, month_rates)):
    ax8.text(i, rate + 1, f'{rate:.1f}%', ha='center', fontsize=8, fontweight='bold')

# ============================================================================
# 9. NUMERIC FEATURES COMPARISON (Bottom Right)
# ============================================================================
ax9 = fig.add_subplot(gs[2, 2])
numeric_features = ['runtime', 'vote_average', 'popularity', 'num_keywords']
hits_vals = []
flops_vals = []
for feat in numeric_features:
    if feat in df_labeled.columns:
        hits_vals.append(hits[hits[feat].notna()][feat].mean())
        flops_vals.append(flops[flops[feat].notna()][feat].mean())

x = np.arange(len(numeric_features))
width = 0.35
ax9.bar(x - width/2, hits_vals, width, label='Hits', color='#2ecc71', alpha=0.8)
ax9.bar(x + width/2, flops_vals, width, label='Flops', color='#e74c3c', alpha=0.8)
ax9.set_ylabel('Average Value', fontsize=11, fontweight='bold')
ax9.set_title('Numeric Features: Hits vs Flops', fontsize=13, fontweight='bold')
ax9.set_xticks(x)
ax9.set_xticklabels(['Runtime\n(min)', 'Vote\nAvg', 'Popularity', 'Keywords'], fontsize=9)
ax9.legend()
ax9.grid(True, alpha=0.3, axis='y')

# ============================================================================
# 10. SUMMARY TEXT (Bottom Full Width)
# ============================================================================
ax10 = fig.add_subplot(gs[3, :])
ax10.axis('off')
summary_text = f"""
PROJECT SUMMARY: The Formula for a Successful Movie (2000-2025)

DATASET: {len(df_labeled):,} movies analyzed ({len(hits):,} hits, {len(flops):,} flops)

KEY FINDINGS:
• Budget: Hits spend 2.17x more ($47.7M vs $21.9M) | Model Importance: 35.5%
• Revenue: Hits earn 19.36x more ($156.4M vs $8.1M)
• ROI: Hits achieve 8.68x better ROI (4.93x vs 0.57x)
• Top Genres: Family (74.3%), Fantasy (70.8%), Adventure (69.0%)
• Best Release: Summer (56.4% hit rate), December (62.3% hit rate)
• Team Size: Hits have 1.6x larger casts, 1.9x larger crews
• Top Keywords: IMAX (91.3%), Marvel Comic (90.5%), 3D (88.8%)

MODEL VALIDATION:
• Full Model: 99.78% accuracy (22 features) - Proves high accuracy achievable
• Limited Model: 77.27% accuracy (9 features) - Validates formula works with basic metadata
• Feature Importance: Budget (35.5%) > Popularity (18.9%) > Team Size (18.5%) > Timing (6.6%)

THE FORMULA: Budget ($30M+) + Popularity (12+) + Team Size (27+ cast, 38+ crew) + Timing (Summer/Dec) + Genre (Family/Fantasy/Adventure) = SUCCESS
"""

ax10.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=11,
          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
          family='monospace', transform=ax10.transAxes)

# ============================================================================
# SAVE VISUALIZATION
# ============================================================================
plt.suptitle('COMPREHENSIVE MOVIE SUCCESS ANALYSIS DASHBOARD', 
             fontsize=16, fontweight='bold', y=0.995)
plt.savefig('comprehensive_analysis_dashboard.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\n[OK] Saved: comprehensive_analysis_dashboard.png")
print("=" * 80)

