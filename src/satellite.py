from pystac_client import Client
import planetary_computer
import rasterio
import numpy as np
from rasterio.mask import mask
from shapely.geometry import Polygon
import json
from pyproj import Transformer


# =====================================
# GET LATEST SENTINEL IMAGE
# =====================================

def get_latest_sentinel_image_from_bbox(bbox):

    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1"
    )

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime="2024-01-01/2026-12-31",
        limit=1
    )

    items = list(search.items())

    if len(items) == 0:
        return None

    return planetary_computer.sign(
        items[0]
    )


# =====================================
# NDVI CALCULATION
# =====================================

def calculate_ndvi(item):

    red_url = item.assets["B04"].href
    nir_url = item.assets["B08"].href

    print("Loading Red Band...")

    with rasterio.open(red_url) as red_src:

        red = red_src.read(
            1,
            out_shape=(512, 512)
        ).astype("float32")

    print("Loading NIR Band...")

    with rasterio.open(nir_url) as nir_src:

        nir = nir_src.read(
            1,
            out_shape=(512, 512)
        ).astype("float32")

    print("Calculating NDVI...")

    ndvi = (
        (nir - red)
        /
        (nir + red + 1e-10)
    )

    mean_ndvi = np.nanmean(
        ndvi
    )

    return mean_ndvi


# =====================================
# NDVI INTERPRETATION
# =====================================

def interpret_ndvi(ndvi):

    if ndvi < 0.2:
        return "Bare Soil"

    elif ndvi < 0.5:
        return "Moderate Vegetation"

    else:
        return "Healthy Vegetation"



def calculate_farm_ndvi(
    item,
    farm_polygon
):

    red_url = item.assets["B04"].href
    nir_url = item.assets["B08"].href

    with rasterio.open(red_url) as red_src:

        raster_crs = red_src.crs

        transformer = Transformer.from_crs(
            "EPSG:4326",
            raster_crs,
            always_xy=True
        )

        transformed_coords = []

        for lon, lat in farm_polygon:

            x, y = transformer.transform(
                lon,
                lat
            )

            transformed_coords.append(
                (x, y)
            )

        polygon = Polygon(
            transformed_coords
        )

        geojson = [
            polygon.__geo_interface__
        ]

        red_clip, _ = mask(
            red_src,
            geojson,
            crop=True
        )

    with rasterio.open(nir_url) as nir_src:

        nir_clip, _ = mask(
            nir_src,
            geojson,
            crop=True
        )

    red = red_clip[0].astype(
        "float32"
    )

    nir = nir_clip[0].astype(
        "float32"
    )

    ndvi = (
        (nir - red)
        /
        (nir + red + 1e-10)
    )

    ndvi = np.where(
        np.isfinite(ndvi),
        ndvi,
        np.nan
    )
    
    return np.nanmean(
        ndvi
    )