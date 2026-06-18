import pandas as pd

data = {
    'Crop': [
        'Rice',
        'Wheat',
        'Cotton',
        'Rice',
        'Cotton'
    ],

    'Rainfall_mm': [
        20,
        30,
        15,
        45,
        25
    ]
}

df = pd.DataFrame(data)

print(df)


crop_water_requirement = {
    'Rice': 50,
    'Wheat': 35,
    'Cotton': 40
}


df['ETc'] = df['Crop'].map(
    crop_water_requirement
)


df['Water_Deficit'] = (
    df['ETc']
    - df['Rainfall_mm']
)

print(df)


def irrigation_advice(deficit):

    if deficit > 25:
        return "Irrigate Immediately"

    elif deficit > 10:
        return "Irrigate Within 2 Days"

    elif deficit > 0:
        return "Monitor Soil Moisture"

    else:
        return "No Irrigation Needed"

df['Advice'] = (
    df['Water_Deficit']
    .apply(irrigation_advice)
)

print(df)