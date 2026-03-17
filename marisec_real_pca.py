import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import os

# 1. Housekeeping
output_dir = "outputs"
if not os.path.exists(output_dir): os.makedirs(output_dir)

# 2. Download the Medical CSV (Breast Cancer Wisconsin Dataset)
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.data"
columns = ['ID', 'Diagnosis', 'Radius', 'Texture', 'Perimeter', 'Area', 'Smoothness', 
           'Compactness', 'Concavity', 'Points', 'Symmetry', 'Dimension']
# (Note: The actual dataset has 30 features, we use the first 10 for clarity)
df = pd.read_csv(url, names=columns, usecols=range(12))

print("--- Step 1: Data Downloaded ---")
print(df.head())

# 3. Clean & Impute Missing Data
# We replace any 0 or NaN values in medical features with the Median
imputer = SimpleImputer(strategy='median')
medical_features = columns[2:] # Skipping ID and Diagnosis
df[medical_features] = imputer.fit_transform(df[medical_features])

print("\n--- Step 2: Missing Data Imputed with Median ---")

# 4. Statistical Study (Mean, Median, Variance, SD)
stats_df = pd.DataFrame({
    'Mean': df[medical_features].mean(),
    'Median': df[medical_features].median(),
    'Variance': df[medical_features].var(),
    'SD': df[medical_features].std()
})
print("\n--- Step 3: Statistical Study ---")
print(stats_df)

# 5. PCA Calculation
# Standardize first (Essential for medical data with different units)
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df[medical_features])

pca = PCA(n_components=2)
pca_results = pca.fit_transform(scaled_data)

# 6. Visualization: Side-by-Side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Plot 1: Original Distribution (using two key medical metrics)
sns.scatterplot(data=df, x='Radius', y='Texture', hue='Diagnosis', ax=ax1, palette='Set1', alpha=0.6)
ax1.set_title(f"Original Medical Data\n(Radius vs Texture)")
ax1.grid(True, linestyle='--', alpha=0.5)

# Plot 2: PCA Results
# Coloring by Diagnosis (M = Malignant, B = Benign) to see if PCA separates them
ax2.scatter(pca_results[:, 0], pca_results[:, 1], c=df['Diagnosis'].map({'M': 'red', 'B': 'green'}), alpha=0.5)
ax2.set_title(f"PCA Analysis\nPC1 Var: {pca.explained_variance_ratio_[0]*100:.1f}%")
ax2.set_xlabel("Principal Component 1 (General Severity)")
ax2.set_ylabel("Principal Component 2 (Secondary Variance)")
ax2.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
save_path = os.path.join(output_dir, "medical_pca_results.png")
plt.savefig(save_path)
print(f"\nAnalysis complete! Results saved to: {save_path}")