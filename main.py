from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
import ee
from datetime import datetime, timedelta

# Initialize Google Earth Engine
print("=" * 50)

service_account_info = json.loads(os.getenv("GEE_CREDENTIALS"))
credentials = ee.ServiceAccountCredentials(service_account_info["client_email"], key_data=json.dumps(service_account_info))

# Initialize Earth Engine
ee.Initialize(credentials)
app = FastAPI()

# Define request model
class PolygonRequest(BaseModel):
    coords: list[list[float]]

def calculate_ndvi(coords: list[list[float]], days: int = 7):
    if len(coords) < 3:
        raise ValueError("A polygon must have at least 3 points.")

    if coords[0] != coords[-1]:
        coords.append(coords[0])

    polygon = ee.Geometry.Polygon([coords])
    today = datetime.utcnow()
    results = []

    for i in range(days):
        date = today - timedelta(days=i)
        start_date = (date - timedelta(days=16)).strftime('%Y-%m-%d')  # Look back 16 days
        end_date = date.strftime('%Y-%m-%d')

        collection = ee.ImageCollection("MODIS/006/MOD13A1") \
            .filterBounds(polygon) \
            .filterDate(start_date, end_date) \
            .sort("system:time_start", False) \
            .limit(1)  # Get the most recent available image

        if collection.size().getInfo() == 0:
            results.append({"date": end_date, "ndvi": None})  # No data available
            continue

        image = collection.first()

        ndvi = image.select("NDVI").reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=polygon,
            scale=250
        ).get("NDVI")

        results.append({"date": end_date, "ndvi": ee.Number(ndvi).divide(10000).getInfo() if ndvi else None})

    return results

def calculate_soil_moisture(coords: list[list[float]], days: int = 7):
    polygon = ee.Geometry.Polygon(coords)
    today = datetime.utcnow()
    results = []

    for i in range(days):
        date = today - timedelta(days=i)
        start_date = date.strftime('%Y-%m-%d')
        end_date = (date + timedelta(days=1)).strftime('%Y-%m-%d')

        smap = ee.ImageCollection("NASA_USDA/HSL/SMAP_soil_moisture") \
            .filterBounds(polygon) \
            .filterDate(start_date, end_date) \
            .mean()

        moisture = smap.select("ssm").reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=polygon,
            scale=1000
        ).get("ssm")

        if moisture:
            results.append({"date": start_date, "soil_moisture": ee.Number(moisture).getInfo()})

    return results

@app.post("/get_ndvi_soil_moisture/")
def get_ndvi_soil_moisture(request: PolygonRequest):
    coords = request.coords
    ndvi_values = calculate_ndvi(coords, days=7)
    moisture_values = calculate_soil_moisture(coords, days=7)

    return {
        "ndvi_last_7_days": ndvi_values,
        "soil_moisture_last_7_days": moisture_values
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
