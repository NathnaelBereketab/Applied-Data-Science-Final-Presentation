"""
PHASE 3 - STEP 3.2: Build Machine Learning Models
Goal: Build Random Forest models (full + limited features) to validate the formula
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("PHASE 3 - STEP 3.2: Build Machine Learning Models")
print("=" * 80)

# ============================================================================
# 1. LOAD PREPARED DATASETS
# ============================================================================
print("\n1. LOADING PREPARED DATASETS...")

try:
    X_full_train = pd.read_csv('X_full_train.csv')
    X_full_test = pd.read_csv('X_full_test.csv')
    y_full_train = pd.read_csv('y_full_train.csv').values.ravel()
    y_full_test = pd.read_csv('y_full_test.csv').values.ravel()
    
    X_limited_train = pd.read_csv('X_limited_train.csv')
    X_limited_test = pd.read_csv('X_limited_test.csv')
    y_limited_train = pd.read_csv('y_limited_train.csv').values.ravel()
    y_limited_test = pd.read_csv('y_limited_test.csv').values.ravel()
    
    print(f"   [OK] Loaded all datasets")
    print(f"   Full features - Train: {X_full_train.shape}, Test: {X_full_test.shape}")
    print(f"   Limited features - Train: {X_limited_train.shape}, Test: {X_limited_test.shape}")
except FileNotFoundError as e:
    print(f"   [ERROR] {e}")
    print("   [NOTE] Run phase3_step3_1_prepare_modeling_data.py first")
    exit(1)

# ============================================================================
# 2. BUILD FULL FEATURE MODEL (RANDOM FOREST)
# ============================================================================
print("\n2. BUILDING FULL FEATURE MODEL (Random Forest)...")

print("   Training Random Forest with full features...")
rf_full = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'  # Handle class imbalance
)

rf_full.fit(X_full_train, y_full_train)
print("   [OK] Model trained")

# Predictions
y_full_train_pred = rf_full.predict(X_full_train)
y_full_test_pred = rf_full.predict(X_full_test)

# Metrics
train_acc = accuracy_score(y_full_train, y_full_train_pred)
test_acc = accuracy_score(y_full_test, y_full_test_pred)
train_prec = precision_score(y_full_train, y_full_train_pred)
test_prec = precision_score(y_full_test, y_full_test_pred)
train_rec = recall_score(y_full_train, y_full_train_pred)
test_rec = recall_score(y_full_test, y_full_test_pred)
train_f1 = f1_score(y_full_train, y_full_train_pred)
test_f1 = f1_score(y_full_test, y_full_test_pred)

print(f"\n   Full Feature Model Performance:")
print(f"      Train Accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)")
print(f"      Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
print(f"      Train Precision: {train_prec:.4f}")
print(f"      Test Precision: {test_prec:.4f}")
print(f"      Train Recall: {train_rec:.4f}")
print(f"      Test Recall: {test_rec:.4f}")
print(f"      Train F1-Score: {train_f1:.4f}")
print(f"      Test F1-Score: {test_f1:.4f}")

# Feature importance
feature_importance_full = pd.DataFrame({
    'feature': X_full_train.columns,
    'importance': rf_full.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n   Top 10 Most Important Features (Full Model):")
for i, row in feature_importance_full.head(10).iterrows():
    print(f"      {row['feature']}: {row['importance']:.4f}")

# Confusion matrix
cm_full = confusion_matrix(y_full_test, y_full_test_pred)
print(f"\n   Confusion Matrix (Test Set):")
print(f"      True Negatives (Flops): {cm_full[0,0]}")
print(f"      False Positives: {cm_full[0,1]}")
print(f"      False Negatives: {cm_full[1,0]}")
print(f"      True Positives (Hits): {cm_full[1,1]}")

# ============================================================================
# 3. BUILD LIMITED FEATURE MODEL (RANDOM FOREST)
# ============================================================================
print("\n3. BUILDING LIMITED FEATURE MODEL (Random Forest)...")

print("   Training Random Forest with limited features...")
rf_limited = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

rf_limited.fit(X_limited_train, y_limited_train)
print("   [OK] Model trained")

# Predictions
y_limited_train_pred = rf_limited.predict(X_limited_train)
y_limited_test_pred = rf_limited.predict(X_limited_test)

# Metrics
train_acc_lim = accuracy_score(y_limited_train, y_limited_train_pred)
test_acc_lim = accuracy_score(y_limited_test, y_limited_test_pred)
train_prec_lim = precision_score(y_limited_train, y_limited_train_pred)
test_prec_lim = precision_score(y_limited_test, y_limited_test_pred)
train_rec_lim = recall_score(y_limited_train, y_limited_train_pred)
test_rec_lim = recall_score(y_limited_test, y_limited_test_pred)
train_f1_lim = f1_score(y_limited_train, y_limited_train_pred)
test_f1_lim = f1_score(y_limited_test, y_limited_test_pred)

print(f"\n   Limited Feature Model Performance:")
print(f"      Train Accuracy: {train_acc_lim:.4f} ({train_acc_lim*100:.2f}%)")
print(f"      Test Accuracy: {test_acc_lim:.4f} ({test_acc_lim*100:.2f}%)")
print(f"      Train Precision: {train_prec_lim:.4f}")
print(f"      Test Precision: {test_prec_lim:.4f}")
print(f"      Train Recall: {train_rec_lim:.4f}")
print(f"      Test Recall: {test_rec_lim:.4f}")
print(f"      Train F1-Score: {train_f1_lim:.4f}")
print(f"      Test F1-Score: {test_f1_lim:.4f}")

# Feature importance
feature_importance_limited = pd.DataFrame({
    'feature': X_limited_train.columns,
    'importance': rf_limited.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n   Feature Importance (Limited Model):")
for i, row in feature_importance_limited.iterrows():
    print(f"      {row['feature']}: {row['importance']:.4f}")

# Confusion matrix
cm_limited = confusion_matrix(y_limited_test, y_limited_test_pred)
print(f"\n   Confusion Matrix (Test Set):")
print(f"      True Negatives (Flops): {cm_limited[0,0]}")
print(f"      False Positives: {cm_limited[0,1]}")
print(f"      False Negatives: {cm_limited[1,0]}")
print(f"      True Positives (Hits): {cm_limited[1,1]}")

# ============================================================================
# 4. COMPARE MODELS
# ============================================================================
print("\n4. MODEL COMPARISON:")

comparison = pd.DataFrame({
    'Metric': ['Train Accuracy', 'Test Accuracy', 'Train Precision', 'Test Precision',
               'Train Recall', 'Test Recall', 'Train F1', 'Test F1'],
    'Full Features': [train_acc, test_acc, train_prec, test_prec,
                     train_rec, test_rec, train_f1, test_f1],
    'Limited Features': [train_acc_lim, test_acc_lim, train_prec_lim, test_prec_lim,
                        train_rec_lim, test_rec_lim, train_f1_lim, test_f1_lim],
    'Difference': [train_acc - train_acc_lim, test_acc - test_acc_lim,
                  train_prec - train_prec_lim, test_prec - test_prec_lim,
                  train_rec - train_rec_lim, test_rec - test_rec_lim,
                  train_f1 - train_f1_lim, test_f1 - test_f1_lim]
})

print(comparison.to_string(index=False))

# ============================================================================
# 5. SAVE RESULTS
# ============================================================================
print("\n5. SAVING RESULTS...")

# Save feature importance
feature_importance_full.to_csv('feature_importance_full_model.csv', index=False)
feature_importance_limited.to_csv('feature_importance_limited_model.csv', index=False)
print("   [OK] Saved feature importance rankings")

# Save model comparison
comparison.to_csv('model_comparison.csv', index=False)
print("   [OK] Saved model comparison")

# Save detailed classification reports
with open('classification_report_full.txt', 'w') as f:
    f.write("FULL FEATURE MODEL - CLASSIFICATION REPORT\n")
    f.write("=" * 80 + "\n\n")
    f.write(classification_report(y_full_test, y_full_test_pred, 
                                 target_names=['Flop', 'Hit']))
    f.write("\n\nCONFUSION MATRIX:\n")
    f.write(str(cm_full))

with open('classification_report_limited.txt', 'w') as f:
    f.write("LIMITED FEATURE MODEL - CLASSIFICATION REPORT\n")
    f.write("=" * 80 + "\n\n")
    f.write(classification_report(y_limited_test, y_limited_test_pred,
                                 target_names=['Flop', 'Hit']))
    f.write("\n\nCONFUSION MATRIX:\n")
    f.write(str(cm_limited))

print("   [OK] Saved classification reports")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("MODEL BUILDING SUMMARY:")
print("=" * 80)
print(f"Full Feature Model:")
print(f"   Test Accuracy: {test_acc:.2f}%")
print(f"   Test F1-Score: {test_f1:.4f}")
print(f"   Features: {X_full_train.shape[1]}")

print(f"\nLimited Feature Model:")
print(f"   Test Accuracy: {test_acc_lim:.2f}%")
print(f"   Test F1-Score: {test_f1_lim:.4f}")
print(f"   Features: {X_limited_train.shape[1]}")

print(f"\nAccuracy Difference: {test_acc - test_acc_lim:.2f}%")
if test_acc_lim > 0.70:
    print(f"   [SUCCESS] Limited model achieves >70% accuracy - Formula validated!")
elif test_acc_lim > 0.65:
    print(f"   [GOOD] Limited model achieves >65% accuracy - Formula works reasonably well")
else:
    print(f"   [NOTE] Limited model accuracy could be improved")

print("\n[OK] Phase 3, Step 3.2 COMPLETE!")
print("=" * 80)

