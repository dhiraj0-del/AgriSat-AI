import pandas as pd

# Load dataset
df = pd.read_csv("data/AgriSat_Features.csv")

# Keep useful columns
df = df[['NDVI', 'NDWI', 'EVI']]

# Remove bad EVI values
df = df[(df['EVI'] > -1) & (df['EVI'] < 1)]

# NDVI statistics
ndvi_min = df['NDVI'].min()
ndvi_max = df['NDVI'].max()

print("NDVI Min:", ndvi_min)
print("NDVI Max:", ndvi_max)

# Calculate VCI
df['VCI'] = 100 * (
    (df['NDVI'] - ndvi_min) /
    (ndvi_max - ndvi_min)
)

print(df.head())



def classify_stress(vci):
    if vci < 20:
        return "Severe Stress"
    elif vci < 40:
        return "Moderate Stress"
    elif vci < 60:
        return "Mild Stress"
    else:
        return "Healthy"

df['Stress_Level'] = df['VCI'].apply(classify_stress)

print(df[['NDVI', 'VCI', 'Stress_Level']].head(10))



print("\nStress Level Distribution:")
print(df['Stress_Level'].value_counts())


def irrigation_advice(stress):
    if stress == "Severe Stress":
        return "Irrigate immediately"
    elif stress == "Moderate Stress":
        return "Irrigate within 2 days"
    elif stress == "Mild Stress":
        return "Monitor soil moisture"
    else:
        return "No irrigation needed"

df['Irrigation_Advice'] = (
    df['Stress_Level']
    .apply(irrigation_advice)
)

print(
    df[
        ['VCI',
         'Stress_Level',
         'Irrigation_Advice']
    ].head(10)
)