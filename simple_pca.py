import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import os

# 1. CREATE DATA: We make a dictionary with 10 people's height and weight
data = {
    'Height': [150, 160, 170, 180, 190, 155, 165, 175, 185, 195],
    'Weight': [50, 62, 68, 80, 91, 52, 64, 72, 83, 94]
}
df = pd.DataFrame(data)  # Turn the dictionary into a neat Table (DataFrame)

# 2. CALCULATE STATS: Find the average (Mean) and the spread (Variance)
means = df.mean()       # Calculates the middle point for Height and Weight
variances = df.var()    # Calculates how much the numbers vary from the mean

print(f"Mean Height: {means[0]:.2f}, Variance: {variances[0]:.2f}")
print(f"Mean Weight: {means[1]:.2f}, Variance: {variances[1]:.2f}")

# 3. STANDARDIZE: PCA requires data to be centered at 0 with a standard scale
scaler = StandardScaler()           # Initialize the scaler tool
df_scaled = scaler.fit_transform(df) # Subtract mean and divide by standard deviation

# 4. RUN PCA: Ask the AI to find the "Principal Components" (the main trends)
pca = PCA(n_components=2)           # We want to find the top 2 trends
pca_data = pca.fit_transform(df_scaled) # Transform our data into the new PCA space

# 5. VISUALIZATION: Create two plots side-by-side to compare
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# --- PLOT 1: ORIGINAL DATA ---
ax1.scatter(df['Height'], df['Weight'], color='blue', alpha=0.6, label='Patients')
ax1.plot(means[0], means[1], 'r*', markersize=15, label='Mean Center') # Plot the Mean as a star

# Draw 'Error Bars' to show the Variance (Spread) visually
ax1.errorbar(means[0], means[1], xerr=np.sqrt(variances[0]), yerr=np.sqrt(variances[1]), 
             fmt='none', ecolor='black', capsize=5, label='Variance (Spread)')

ax1.set_title("Original Space: Seeing Mean & Variance")
ax1.set_xlabel("Height (cm)")
ax1.set_ylabel("Weight (kg)")
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.5)

# --- PLOT 2: PCA SPACE ---
# Here, the 'X' axis is our Principal Component 1 (the strongest trend)
ax2.scatter(pca_data[:, 0], pca_data[:, 1], color='purple', alpha=0.6)

# Label the axes with the "Explained Variance" (How much info did we capture?)
ax2.set_title(f"PCA Space: PC1 captures {pca.explained_variance_ratio_[0]*100:.1f}% Info")
ax2.set_xlabel("Principal Component 1 (Size Trend)")
ax2.set_ylabel("Principal Component 2 (Noise/Variation)")

# Draw lines at 0 to show the new center of the world
ax2.axhline(0, color='black', linewidth=1)
ax2.axvline(0, color='black', linewidth=1)
ax2.grid(True, linestyle='--', alpha=0.5)

# 6. SAVE & FINISH
plt.tight_layout() # Adjust layout so titles don't overlap
plt.savefig('outputs/pca_step_by_step.png') # Save result to your NVMe folder
print("Success! Open 'pca_step_by_step.png' to see the transformation.")