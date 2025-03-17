from fastapi import FastAPI
from pydantic import BaseModel
import os 
import ee

# Initialize Google Earth Engine
service_account_json = os.getenv("GEE_CREDENTIALS")
print("="*50)
print(service_account_json)
print("="*50)

if service_account_json:
    with open("/tmp/service-account.json", "w") as f:
        f.write(service_account_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/service-account.json"

print("Initializing GEE")
ee.Initialize(project="ee-harshsmj1504")
print("Initizalzation completed")
print("="*50)
print("Authenticating: ")
ee.Authenticate()
print("READY")
app = FastAPI()

# Define request model
class PolygonRequest(BaseModel):
    coords: list[list[float]]

def calculate_ndvi(coords: list[list[float]]):
    if len(coords) < 3:
        raise ValueError("A polygon must have at least 3 points.")

    # Ensure the polygon is closed (first and last points should be the same)
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    polygon = ee.Geometry.Polygon([coords])  # Convert to Polygon

    # Get the MODIS image for the specified period
    collection = ee.ImageCollection("MODIS/006/MOD13A1") \
        .filterBounds(polygon) \
        .sort("system:time_start", False) \
        .first()   # Use mean to get composite NDVI values
    
    ndvi = collection.select("NDVI").reduceRegion(
        reducer=ee.Reducer.mean(), 
        geometry=polygon, 
        scale=250
    ).get("NDVI")
    ndvi = ee.Number(ndvi).divide(10000) 
    return ndvi.getInfo() if ndvi else None

def calculate_soil_moisture(coords: list[list[float]]):
    polygon = ee.Geometry.Polygon(coords)

    # Use SMAP Soil Moisture data (latest)
    smap = ee.ImageCollection("NASA_USDA/HSL/SMAP_soil_moisture") \
        .filterBounds(polygon) \
        .sort("system:time_start", False) \
        .first()
    
    moisture = smap.select("ssm").reduceRegion(
        reducer=ee.Reducer.mean(), geometry=polygon, scale=1000
    ).get("ssm")

    return moisture.getInfo() if moisture else None

@app.post("/get_ndvi_soil_moisture/")
def get_ndvi_soil_moisture(request: PolygonRequest):
    """
    coords: List of coordinates [[lon1, lat1], [lon2, lat2], [lon3, lat3], ...] to form a polygon.
    """
    coords = request.coords
    ndvi = calculate_ndvi(coords)
    moisture = calculate_soil_moisture(coords)
    
    return {"ndvi": ndvi, "soil_moisture": moisture}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
