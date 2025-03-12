from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
import ee
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import json

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware to allow requests from the frontend
origins = [
    "http://localhost",  # Allow frontend running from localhost
    "http://localhost:8000",  # Allow frontend running on the same server with a different port
    "http://127.0.0.1:8080",  # Allow frontend from 127.0.0.1 (common localhost address)
    "*",  # Allow all origins (be cautious when using '*' in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change it in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
# Initialize Google Earth Engine
ee.Authenticate() 
# Initialize Google Earth Engine
ee.Initialize(project="ee-harshsmj1504")

# Define the request body model
class AreaRequest(BaseModel):
    lat1: float
    lon1: float
    lat2: float
    lon2: float
    startDate: str
    endDate: str

# Function to calculate NDVI
def calculate_ndvi(lat1, lon1, lat2, lon2, start_date, end_date):
    # Define the area of interest
    geometry = ee.Geometry.Polygon(
        [[
            [lon1, lat1],
            [lon2, lat1],
            [lon2, lat2],
            [lon1, lat2]
        ]]
    )
    
    # Load Sentinel-2 imagery
    collection = ee.ImageCollection('COPERNICUS/S2') \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .sort('CLOUDY_PIXEL_PERCENTAGE')
    
    # Take the first image
    image = collection.first()
    
    # Calculate NDVI (NIR: B8, RED: B4)
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    
    # Reduce the NDVI to a mean value over the region of interest
    mean_ndvi = ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=30,
        maxPixels=1e8
    )
    
    # Extract NDVI value
    mean_ndvi_info = mean_ndvi.getInfo()
    return mean_ndvi_info

# Define the API endpoint to calculate NDVI
@app.post("/calculate_ndvi")
async def get_ndvi(area: AreaRequest):
    result = calculate_ndvi(
        area.lat1, area.lon1, area.lat2, area.lon2, area.startDate, area.endDate
    )
    return {"mean_ndvi": result['NDVI']}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




