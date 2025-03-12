from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
import ee
# from google.auth.transport.requests import Request
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
import os
# credentials_json = {
#   "type": "service_account",
#   "project_id": "marine-fusion-423921-r9",
#   "private_key_id": "3755fae305191e12b5780dba73954dbf0b8328f5",
#   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC0+QSu7bhL5L8v\nZI8WuU6gibYZfDQ0fHDZ+v1HMP4dRJSeX41/cgZbxmjz89pCqE/4ZD/QBjZn7wcE\n0iLGRzSrTxAEfojT101cxai+xKx84Yn8q2GCRnPikeR7CF1k+GHcF93YqOLCEEV3\nd5aGV9TKUMRRVsZ4LproqlRuTRpM9m1sIKe+qp71aVNSf84H9DFgvrONoyFxV+oI\n/NYXPY306Ro62yBcSU4dBRyP0xJeAam1lfjGG96/JNaxm+xM/S6tykScUvmzu9bW\nMbIBcZeJi87eEEoes6h4IABNpiuVbfAL3GPUEv7lfDfH9lYfscSZKI0bTe/Hu8qN\nVJwRWl3rAgMBAAECggEAAVtKsA5z8ek9derdrxLoecCW6sWICrf17TKvez0Sx/ay\nd0wmXmiytNDTORw27CXZeenCRjWXjIVp/U0p5U7wdEzBlvdMH4t2BqQj5CaIKbpg\nRkw4Gaj8wXfhhjFm+W79dK1f8ZthLt00CKHBUshbin2ymoXRgx8XXZj39rLK58+Y\n3JB0m2ZZWdQEYNb78SLQp166ECKxaNLPaBYqrvDglnxl8m6Od2kdgDCMK4sRl4tu\nHGF2q1HG01IdCbd1CT623KGHhH0wZct+ergx8lmGhCuSWQSNPMPOsvvR/Ter+DU1\nyq4vBOb/6lC6gX8gKKPZ5cs0frVAzSxd1xFtVD5eAQKBgQDz490VaABqcDU1GLEt\npnha3yVjwzIXf08GxpF+GWQ5Kzdp3zcJ/klOmdUBPat0ImOmbjrgOo0HXJlU7Jp+\nXy72tu3z5Bh+fQfgncs9xumyAry1zEt7daH1LqqeaUEr7hYIykDchCQyr+XuKh4p\nxkSx95VOfiC4CR0XrElLkmOQmwKBgQC99WY5eFHCKgsXmDVyMGFYpd5FcwRk2Y6l\nIf4PfK1K7+UGh1rn7jWdLN3yKtibXhvRSM7G++GCCbFRGQtfnyybtJKIoQArenMi\nrvoHIY3wBYQU5qxczdaO8fgwoBPxxnAuYu+Wyf6aLtPgt7cN7HQWfUsMEibGrTvh\nnEQ0h1t08QKBgBphjnuPSWQ6CPdaWWf3ttMViiTVa2ixQ6oW9ovuUTIB47eXBowV\nLnbLGwhMVGx2f9Lz33h7vN+L+6X9BeUfhKP5O5oDFUcxXRXF28Mt7f9sXl9H3u5W\n1hMAXkJOXldTJJ0Ey6lOvd+huTxe3+5i3PFnN4ZLDFz712LFJxR+nDh7AoGAeh3P\nSLTLwomqtdFY0n69pfKDsJvfQEIIDKqMnEInWVxdHFRZoW4ms1NLn0niFAds1J78\npzj34NQAVMVH5YH7eGGeLg1qgYjniW15OKpeh+XT4mfkeIivHRf62K+gArbyGS/r\nHEHg1heyh+0y1dWjT23el/T3TpPBQilmQ2qc5dECgYBVpRLHkEOWHpN5mlnthTdr\nDxG/SSBZWJq8oqM7YUxCmzAyaRiVoE7xzyohaqwP4B50zq+swbasRtAA1VsrO1Mk\nmuCObLFuVfQfiWDivEZ87kRlED6QI5bwv/e+0csOjquCjZIEW8EPlL6BWdMxA5Qz\nmFcNVRW0tiy+isBvBTCddQ==\n-----END PRIVATE KEY-----\n",
#   "client_email": "earth-engine-service-account@marine-fusion-423921-r9.iam.gserviceaccount.com",
#   "client_id": "106253643210164038943",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/earth-engine-service-account%40marine-fusion-423921-r9.iam.gserviceaccount.com",
#   "universe_domain": "googleapis.com"
# }

# credentials = service_account.Credentials.from_service_account_info(credentials_json)
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




