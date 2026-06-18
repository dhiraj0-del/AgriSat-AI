import pandas as pd

df = pd.read_csv("data/AgriSat_Features.csv")

print("Original Dataset:")
print(df.describe())

# Keep only required columns
df = df[['NDVI', 'NDWI', 'EVI']]

# Remove extreme EVI values
df = df[(df['EVI'] > -1) & (df['EVI'] < 1)]

print("\nCleaned Dataset:")
print(df.describe())