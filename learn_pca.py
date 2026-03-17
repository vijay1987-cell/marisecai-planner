import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os

# create data set
data = {
            'Height': [150, 180, 145, 160, 166, 175, 195, 190, 180, 196],
            'Weight': [50, 62, 68, 80, 91, 52, 64, 72, 83, 94]
}
# creating a neat table of the above values 
df = pd.DataFrame(data)

# calculate stats for the data above, their mean and variance
means = df.mean()
variances = df.var()

print(f"Mean of Height: {means[0]:.2f}, Variance: {variances[0]:.2f}")
print(f"Mean of Weight: {means[1]:.2f}, Variance: {variances[1]:.2f}")      

# Standardizing the data    
scaler = StandardScaler()
df_Scaled = scaler.fit_transform(df) #(x-u/sigma)
# Finding Principlal components
pca = PCA(n_components=2)
pca_data = pca.fit_transform(df_Scaled) #Trnsform the standardized data to find the PCAs

