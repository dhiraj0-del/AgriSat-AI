import requests
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import geopandas as gpd
from satellite import (
    get_latest_sentinel_image_from_bbox,
    calculate_farm_ndvi,
    interpret_ndvi
)
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

Draw(
    export=True,
    draw_options={
        "polyline": False,
        "rectangle": True,
        "circle": False,
        "circlemarker": False,
        "marker": False,
        "polygon": True
    }
).add_to(m)

map_data = st_folium(
    m,
    width=None,
    height=600
)
if map_data and map_data.get("all_drawings"):
    st.success(
        "Farm boundary selected successfully."
    )

    drawing = map_data["all_drawings"][0]

    coords = drawing["geometry"]["coordinates"][0]
    # Save farm polygon

    st.session_state["farm_polygon"] = coords
    # =====================================
    # BOUNDING BOX EXTRACTION
    # =====================================

    lons = [
        point[0]
        for point in coords
    ]

    lats = [
        point[1]
        for point in coords
    ]

    min_lon = min(lons)
    max_lon = max(lons)

    min_lat = min(lats)
    max_lat = max(lats)

    bbox = [
        min_lon,
        min_lat,
        max_lon,
        max_lat
    ]

    st.session_state["farm_bbox"] = bbox
    
    

    polygon_points = [
        (point[0], point[1])
        for point in coords
    ]

    polygon = Polygon(
        polygon_points
    )

    gdf = gpd.GeoDataFrame(
        index=[0],
        geometry=[polygon],
        crs="EPSG:4326"
    )

    gdf_projected = gdf.to_crs(
    epsg=32644
)

    area_m2 = gdf_projected.area.iloc[0]

    area_hectares = (
        area_m2 / 10000
    )
    st.session_state["farm_area"] = area_hectares

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "🌾 Farm Area (ha)",
            f"{area_hectares:.2f}"
        )

    with col2:
        st.metric(
            "📏 Farm Area (m²)",
            f"{area_m2:.0f}"
        )

    st.write(
        "Boundary Coordinates:"
    )

    st.write(
        coords
    )   
st.info(
    f"Current Selected Location: {location_name}"
)

# =========================
# WEATHER INTELLIGENCE
# =========================

st.header("🌦 Weather Intelligence")

weather_url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={farm_lat}"
    f"&longitude={farm_lon}"
    f"&current=temperature_2m,"
    f"relative_humidity_2m,"
    f"wind_speed_10m"
    f"&daily=precipitation_sum"
    f"&forecast_days=2"
)

try:

    weather_response = requests.get(
        weather_url,
        timeout=10
    )

    weather_data = weather_response.json()

    current = weather_data["current"]

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    wind_speed = current["wind_speed_10m"]
    tomorrow_rain = weather_data["daily"][
    "precipitation_sum"
][1]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🌡 Temperature",
            f"{temperature} °C"
        )

    with col2:
        st.metric(
            "💧 Humidity",
            f"{humidity}%"
        )

    with col3:
        st.metric(
            "💨 Wind Speed",
            f"{wind_speed} km/h"
        )
    
    with col4:
        st.metric(
            "🌧 Rain Tomorrow",
            f"{tomorrow_rain} mm"
        )


    if tomorrow_rain > 5:

        st.success(
            "🌧 Rain expected tomorrow. Delay irrigation."
        )

    else:

        st.warning(
            "☀ No significant rainfall expected. Irrigation may be required."
        )
    st.header("🚜 Smart Irrigation Advisory")

    if tomorrow_rain > 5:

        irrigation_status = (
            "Delay irrigation for 24 hours."
        )

    elif temperature > 35:

        irrigation_status = (
            "High temperature detected. Irrigate today."
        )

    elif humidity < 40:

        irrigation_status = (
            "Low humidity detected. Monitor soil moisture closely."
        )

    else:

        irrigation_status = (
            "Normal conditions. Irrigate within 2-3 days if needed."
        )

    st.success(
        irrigation_status
    )
except Exception as e:

    st.error(
        f"Weather Error: {e}"
    )
    
# =========================
# SMART IRRIGATION ADVISORY
# =========================

farm_area = st.session_state.get(
    "farm_area",
    0
)
water_required_liters = (
    farm_area * 50000
)

st.metric(
    "💧 Estimated Water Requirement",
    f"{water_required_liters:,.0f} L"
)

# =========================
# FARM INTELLIGENCE
# =========================

st.header("🧠 Farm Intelligence")

farm_area = st.session_state.get(
    "farm_area",
    0
)

water_required_liters = (
    farm_area * 50000
)

# =========================
# HEAT STRESS RISK
# =========================

if temperature > 35:
    heat_risk = "🔴 High"

elif temperature > 30:
    heat_risk = "🟡 Moderate"

else:
    heat_risk = "🟢 Low"

# =========================
# MOISTURE RISK
# =========================

if humidity < 40:
    moisture_risk = "🔴 High"

elif humidity < 60:
    moisture_risk = "🟡 Moderate"

else:
    moisture_risk = "🟢 Low"

# =========================
# WIND RISK
# =========================

if wind_speed > 20:
    wind_risk = "🔴 High"

elif wind_speed > 10:
    wind_risk = "🟡 Moderate"

else:
    wind_risk = "🟢 Low"

# =========================
# RAIN RISK
# =========================

if tomorrow_rain > 10:
    rain_risk = "🟢 Good Rainfall"

elif tomorrow_rain > 3:
    rain_risk = "🟡 Light Rain"

else:
    rain_risk = "🔴 No Rain"

# =========================
# DISPLAY METRICS
# =========================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🌡 Heat Risk",
        heat_risk
    )

with col2:
    st.metric(
        "💧 Moisture Risk",
        moisture_risk
    )

with col3:
    st.metric(
        "💨 Wind Risk",
        wind_risk
    )

with col4:
    st.metric(
        "🌧 Rain Status",
        rain_risk
    )

# =========================
# SATELLITE CONNECTION
# =========================

st.header("🛰 Satellite Intelligence")

if "farm_bbox" in st.session_state:

    bbox = st.session_state["farm_bbox"]

    try:

        item = (
            get_latest_sentinel_image_from_bbox(
                bbox
            )
        )

        if item:

            st.success(
                "Sentinel-2 image found."
            )

            st.write(
                f"Image ID: {item.id}"
            )

            with st.spinner(
                "Calculating NDVI..."
            ):

                farm_polygon = (
                    st.session_state[
                        "farm_polygon"
                    ]
                )

                ndvi = calculate_farm_ndvi(
                    item,
                    farm_polygon
                )

                health = interpret_ndvi(
                    ndvi
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "🌿 NDVI",
                        f"{ndvi:.3f}"
                    )

                with col2:
                    st.metric(
                        "🌾 Crop Health",
                        health
                    )

        else:

            st.warning(
                "No Sentinel image found."
            )

    except Exception as e:

        st.error(
            f"Satellite Error: {e}"
        )

# =========================
# FARM STATISTICS
# =========================

st.subheader("📊 Farm Statistics")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "🌾 Farm Area",
        f"{farm_area:.2f} ha"
    )

with col2:
    st.metric(
        "🚰 Water Requirement",
        f"{water_required_liters:,.0f} L"
    )

# =========================
# OVERALL RISK SCORE
# =========================

risk_score = 0

if temperature > 35:
    risk_score += 1

if humidity < 40:
    risk_score += 1

if wind_speed > 20:
    risk_score += 1

if tomorrow_rain < 3:
    risk_score += 1

if risk_score >= 3:
    overall_risk = "🔴 High"

elif risk_score >= 2:
    overall_risk = "🟡 Moderate"

else:
    overall_risk = "🟢 Low"

st.subheader("⚠ Overall Farm Risk")

st.metric(
    "Risk Level",
    overall_risk
)

# =========================
# SMART RECOMMENDATION
# =========================

st.subheader("🚜 Smart Recommendation")

if overall_risk == "🔴 High":

    st.error(
        """
        High environmental stress detected.

        Recommendation:
        • Irrigate within 24 hours
        • Monitor crop health daily
        • Avoid fertilizer application during heat stress
        """
    )

elif overall_risk == "🟡 Moderate":

    st.warning(
        """
        Moderate risk detected.

        Recommendation:
        • Monitor soil moisture
        • Irrigate within 2-3 days if rainfall does not occur
        """
    )

else:

    st.success(
        """
        Farm conditions are healthy.

        Recommendation:
        • No immediate irrigation required
        • Continue routine monitoring
        """
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