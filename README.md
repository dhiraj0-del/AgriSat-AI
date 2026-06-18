AgriSat AI 🌾🛰️

AI-Driven Crop Classification, Moisture Stress Detection, and Irrigation Advisory System

AgriSat AI is a satellite-based precision agriculture platform

The project integrates:

Sentinel-2 Optical Satellite Data
Sentinel-1 SAR Data
Machine Learning
Moisture Stress Detection
Water Deficit Estimation
Irrigation Advisory Generation

to support precision agriculture and smart farming.

Features

Satellite Feature Extraction
NDVI
NDWI
EVI

from Sentinel-2 imagery using Google Earth Engine.

SAR Analysis
VV Polarization
VH Polarization

from Sentinel-1 imagery.

Crop Classification

Random Forest-based crop classification pipeline.

Moisture Stress Detection

Vegetation Condition Index (VCI) based stress monitoring:

Healthy
Mild Stress
Moderate Stress
Severe Stress
Irrigation Advisory

Automated irrigation recommendations based on stress and water deficit analysis.

Dashboard

Interactive Streamlit dashboard for visualization and analysis.

project structure
AGRISAT_AI/
│
├── data/
│   ├── AgriSat_Features.csv
│   ├── SAR_Features.csv
│   └── crop_labels.csv
│
├── models/
│   └── crop_model.pkl
│
├── src/
│   ├── dashboard.py
│   ├── data_analysis.py
│   ├── moisture_stress.py
│   ├── phenology.py
│   ├── train_crop_model.py
│   └── water_deficit.py
│
├── screenshots/
├── requirements.txt
├── README.md
└── LICENSE


Installation

git clone <repository-url>
cd AGRISAT_AI

pip install -r requirements.txt

Run Dashboard

streamlit run src/dashboard.py


Technologies Used

Python
Google Earth Engine
Streamlit
Pandas
NumPy
Scikit-Learn
Matplotlib
Sentinel-1
Sentinel-2
Future Scope
Interactive Farmer Dashboard
Real-Time Weather Integration
AI Agronomist Chatbot
Yield Prediction
Mobile Application


Developer

Dhiraj
