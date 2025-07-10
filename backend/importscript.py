import ee

# Initialize Earth Engine with default credentials
ee.Initialize(project='prototype-465419 ')

# Test pull
image = ee.Image("COPERNICUS/S2").select(['B4', 'B3', 'B2'])
print(image.getInfo())

