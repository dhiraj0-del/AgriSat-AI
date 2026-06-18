import requests
import folium
from streamlit_folium import st_folium
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# PAGE CONFIG
# =========================


st.set_page_config(
    page_title="AgriSat AI",
    page_icon="🌾",
    layout="wide"
)



# =========================
# TITLE
# =========================

st.title("🌾 AgriSat AI")

st.subheader(
    "Farmer Decision Support Platform"
)


# =========================
# FARMER SUMMARY
# =========================

st.header("📋 Field Summary")

st.success(
    "Crop is healthy and irrigation is not required immediately."
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🌾 Crop",
        "Rice"
    )

with col2:
    st.metric(
        "🟢 Health",
        "Healthy"
    )

with col3:
    st.metric(
        "🌱 Stage",
        "Flowering"
    )

with col4:
    st.metric(
        "💧 Water Needed",
        "18 mm"
    )


# =========================
# FARM LOCATION
# =========================

st.header("📍 Select Farm Location")

location_name = st.text_input(
    "🔍 Enter Village / Town / City",
    value="Amaravati"
)

farm_lat = 16.5725
farm_lon = 80.3575

try:

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": location_name,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "AgriSatAI"
    }

    response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=10
)

    data = response.json()

    if len(data) > 0:

        farm_lat = float(data[0]["lat"])
        farm_lon = float(data[0]["lon"])

        st.success(
            f"Location Found: {location_name}"
        )

    else:

        st.warning(
            "Location not found. Showing Amaravati."
        )

except Exception as e:

    st.error(
        f"Error: {e}"
    )
    
    
st.header("🗺️ Farm Location")

m = folium.Map(
    location=[farm_lat, farm_lon],
    zoom_start=14
)

folium.Marker(
    [farm_lat, farm_lon],
    popup=location_name,
    tooltip="Selected Location"
).add_to(m)

st_folium(
    m,
    width=None,
    height=600
)
st.info(
    f"Current Selected Location: {location_name}"
)

# =========================
# PROJECT OVERVIEW
# =========================

st.markdown("""
### Project Overview

AgriSat AI combines:

- Sentinel-2 Optical Data
- Sentinel-1 SAR Data
- Machine Learning
- Moisture Stress Detection
- Water Deficit Estimation
- Irrigation Advisory

to support precision agriculture and smart farming.
""")

# =========================
# LOAD SATELLITE DATA
# =========================

df = pd.read_csv("data/AgriSat_Features.csv")

df = df[['NDVI', 'NDWI', 'EVI']]

df = df[(df['EVI'] > -1) & (df['EVI'] < 1)]

# =========================
# KPI METRICS
# =========================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Samples",
    len(df)
)

col2.metric(
    "Avg NDVI",
    round(df["NDVI"].mean(), 3)
)

col3.metric(
    "Avg NDWI",
    round(df["NDWI"].mean(), 3)
)

col4.metric(
    "Avg EVI",
    round(df["EVI"].mean(), 3)
)



# =========================
# FARMER ADVISORY
# =========================

st.header("🚜 Farmer Advisory")

st.info(
    """
    Current Crop Condition: Healthy

    Recommended Action:
    No irrigation is required immediately.

    Monitor crop condition over the next 3-5 days.
    """
)  

# =========================
# DATASET PREVIEW
# =========================

st.header("📊 Dataset Preview")

st.dataframe(df.head())

# =========================
# DATASET STATISTICS
# =========================

st.header("📈 Dataset Statistics")

st.dataframe(df.describe())

# =========================
# NDVI HISTOGRAM
# =========================

st.header("🌱 NDVI Distribution")

fig1, ax1 = plt.subplots()

ax1.hist(
    df['NDVI'],
    bins=20
)

ax1.set_title("NDVI Distribution")
ax1.set_xlabel("NDVI")
ax1.set_ylabel("Frequency")

st.pyplot(fig1)

# =========================
# VCI CALCULATION
# =========================

ndvi_min = df['NDVI'].min()
ndvi_max = df['NDVI'].max()

df['VCI'] = (
    100 *
    (
        (df['NDVI'] - ndvi_min)
        /
        (ndvi_max - ndvi_min)
    )
)

# =========================
# STRESS CLASSIFICATION
# =========================

def classify_stress(vci):

    if vci < 20:
        return "Severe Stress"

    elif vci < 40:
        return "Moderate Stress"

    elif vci < 60:
        return "Mild Stress"

    else:
        return "Healthy"

df['Stress_Level'] = df['VCI'].apply(
    classify_stress
)

# =========================
# STRESS BAR CHART
# =========================

st.header("🚨 Stress Distribution")

stress_counts = (
    df['Stress_Level']
    .value_counts()
)

fig2, ax2 = plt.subplots()

ax2.bar(
    stress_counts.index,
    stress_counts.values
)

ax2.set_title(
    "Stress Distribution"
)

st.pyplot(fig2)

# =========================
# STRESS PIE CHART
# =========================

st.header("🥧 Stress Percentage")

fig3, ax3 = plt.subplots()

ax3.pie(
    stress_counts.values,
    labels=stress_counts.index,
    autopct='%1.1f%%'
)

ax3.set_title(
    "Stress Distribution"
)

st.pyplot(fig3)

# =========================
# IRRIGATION ADVICE
# =========================

def irrigation_advice(stress):

    if stress == "Severe Stress":
        return "Irrigate Immediately"

    elif stress == "Moderate Stress":
        return "Irrigate Within 2 Days"

    elif stress == "Mild Stress":
        return "Monitor Soil Moisture"

    else:
        return "No Irrigation Needed"

df['Advice'] = (
    df['Stress_Level']
    .apply(irrigation_advice)
)

st.header("💧 Irrigation Advisory")

st.dataframe(
    df[
        [
            'VCI',
            'Stress_Level',
            'Advice'
        ]
    ].head(10)
)

# =========================
# WATER DEFICIT ESTIMATION
# =========================

water_df = pd.DataFrame({

    'Crop': [
        'Rice',
        'Wheat',
        'Cotton'
    ],

    'Rainfall_mm': [
        20,
        30,
        15
    ]
})

crop_water_requirement = {

    'Rice': 50,
    'Wheat': 35,
    'Cotton': 40
}

water_df['ETc'] = (
    water_df['Crop']
    .map(crop_water_requirement)
)

water_df['Water_Deficit'] = (
    water_df['ETc']
    -
    water_df['Rainfall_mm']
)

def irrigation_advice_water(deficit):

    if deficit > 25:
        return "Irrigate Immediately"

    elif deficit > 10:
        return "Irrigate Within 2 Days"

    elif deficit > 0:
        return "Monitor Soil Moisture"

    else:
        return "No Irrigation Needed"

water_df['Advice'] = (
    water_df['Water_Deficit']
    .apply(irrigation_advice_water)
)

st.header("🚰 Water Deficit Estimation")

st.dataframe(water_df)

# =========================
# SAR DATA
# =========================

st.header("📡 Sentinel-1 SAR Statistics")

sar_df = pd.read_csv("data/SAR_Features.csv")

st.dataframe(
    sar_df[['VV', 'VH']]
    .describe()
)

col1, col2 = st.columns(2)

col1.metric(
    "Average VV",
    round(
        sar_df['VV'].mean(),
        2
    )
)

col2.metric(
    "Average VH",
    round(
        sar_df['VH'].mean(),
        2
    )
)

# =========================
# PROJECT WORKFLOW
# =========================

st.header("🏗 Project Workflow")

st.code("""
Satellite Data
      ↓
NDVI / NDWI / EVI
      ↓
SAR Features (VV, VH)
      ↓
Crop Classification
      ↓
Phenology Analysis
      ↓
VCI Stress Detection
      ↓
Water Deficit Estimation
      ↓
Irrigation Advisory
      ↓
Dashboard
""")

# =========================
# DEVELOPER INFO
# =========================

st.header("👨‍💻 Developer")

st.write(
    "AgriSat AI developed by A V D DHIRAJ "
)