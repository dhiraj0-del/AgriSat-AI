import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("data/crop_labels.csv")

print("Dataset Preview:")
print(df.head())

# Convert crop names into numerical labels
crop_mapping = {
    'Rice': 0,
    'Wheat': 1,
    'Cotton': 2
}

df['Label'] = df['Crop'].map(crop_mapping)

print("\nDataset with Labels:")
print(df.head())

# Features
X = df[['NDVI', 'NDWI', 'EVI']]

# Labels
y = df['Label']

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42
)

# Create model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train model
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# Accuracy
print("\nAccuracy:")
print(accuracy_score(y_test, predictions))

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, predictions))

# Feature Importance
print("\nFeature Importance:")

for feature, importance in zip(X.columns,
                               model.feature_importances_):
    print(f"{feature}: {importance:.4f}")

# Predict a new sample
new_sample = [[0.27, -0.03, 0.88]]

prediction = model.predict(new_sample)

reverse_mapping = {
    0: 'Rice',
    1: 'Wheat',
    2: 'Cotton'
}

print("\nPredicted Crop:")
print(reverse_mapping[prediction[0]])

# Save model
joblib.dump(model, "crop_model.pkl")

print("\nModel saved as crop_model.pkl")