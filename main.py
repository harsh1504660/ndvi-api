from fastapi import FastAPI
from pydantic import BaseModel
import os 
import json
import ee

# Initialize Google Earth Engine

print("="*50)

service_account_info = json.loads(os.getenv("GEE_CREDENTIALS"))
credentials = ee.ServiceAccountCredentials(service_account_info["client_email"], key_data=json.dumps(service_account_info))

# Initialize Earth Engine
ee.Initialize(credentials)
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI
app = FastAPI()

# Enable CORS
origins = [
    "https://preview--soilwise-ui.lovable.app",  # Allow frontend origin
    "https://soilwise-ui.lovable.app",           # Allow the main domain (optional)
    "*"  # Allow all domains (use only for testing)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Set allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define request model
class PolygonRequest(BaseModel):
    coords: list[list[float]]

def calculate_ndvi(coords: list[list[float]]):
    if len(coords) < 3:
        raise ValueError("A polygon must have at least 3 points.")
    print(coords)
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
    print(ndvi)
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
    print(moisture)
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
    port = int(os.getenv("PORT", 10000))  # Render provides a PORT environment variable
    uvicorn.run(app, host="0.0.0.0", port=port)
