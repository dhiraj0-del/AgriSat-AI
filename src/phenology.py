monthly_ndvi = {
    "January": 0.2825,
    "February": 0.2300,
    "March": 0.1921,
    "April": 0.1760
}

for month, ndvi in monthly_ndvi.items():

    if ndvi < 0.2:
        stage = "Harvest/Post-Harvest"

    elif ndvi < 0.3:
        stage = "Vegetative Growth"

    elif ndvi < 0.5:
        stage = "Flowering"

    else:
        stage = "Dense Vegetation"

    print(f"{month}: NDVI={ndvi:.3f} → {stage}")