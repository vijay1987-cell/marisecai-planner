import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import os

# 1. Housekeeping: Output folder
output_dir = "outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. Generate Correlated Maritime Data (e.g., Engine RPM vs Speed)
np.random.seed(42)
mean = [50, 50]
cov = [[10, 8], [8, 10]]  # The '8' creates a strong correlation
data = np.random.multivariate_normal(mean, cov, 200)

# 3. Perform PCA (Extracting 2 components)
pca = PCA(n_components=2)
pca.fit(data)
data_pca = pca.transform(data)

# Extract stats for the labels
var_ratio = pca.explained_variance_ratio_
components = pca.components_
variances = pca.explained_variance_

# 4. Create Side-by-Side Visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# --- PLOT 1: Original Data Space ---
ax1.scatter(data[:, 0], data[:, 1], alpha=0.5, color='blue', label='Sensor Data')
# Draw the Principal Component Vectors (Arrows)
for i, (vector, var) in enumerate(zip(components, variances)):
    # Scale vector for visibility
    v = vector * 3 * np.sqrt(var) 
    ax1.annotate('', xy=pca.mean_ + v, xytext=pca.mean_,
                 arrowprops=dict(arrowstyle='->', linewidth=3, 
                                 color='red' if i==0 else 'green'))
ax1.set_title("Original Data Space\n(Showing Directions of Max Variance)")
ax1.set_xlabel("Sensor A (e.g., Engine RPM)")
ax1.set_ylabel("Sensor B (e.g., Ship Speed)")
ax1.axis('equal') # Important: keep 1:1 scale to see vectors correctly

# --- PLOT 2: PCA Transformed Space ---
ax2.scatter(data_pca[:, 0], data_pca[:, 1], alpha=0.5, color='purple')
ax2.set_title("PCA Space\n(Data Rotated to Most Important Axes)")
ax2.set_xlabel(f"PC1 (Variance: {var_ratio[0]*100:.1f}%)")
ax2.set_ylabel(f"PC2 (Variance: {var_ratio[1]*100:.1f}%)")
ax2.axhline(0, color='black', linewidth=1, alpha=0.5)
ax2.axvline(0, color='black', linewidth=1, alpha=0.5)
ax2.axis('equal')

plt.tight_layout()
save_path = os.path.join(output_dir, "pca_comparison.png")
plt.savefig(save_path)
print(f"Comparison saved to: {save_path}")