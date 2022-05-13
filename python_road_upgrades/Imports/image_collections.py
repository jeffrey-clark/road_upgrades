import ee

# Google Earth Engine Sources
s2 = ee.ImageCollection("COPERNICUS/S2")
MODIS = ee.ImageCollection("MODIS/006/MOD13Q1")
rainfall = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY")

# Facebook Data
fb_pop = ee.Image("users/jc23500/FB_population_moz_2019-07-01")

# Ingested Maps from OpenStreetMap
buildings = ee.FeatureCollection("users/taminamatti/MOZ_centers_buildings_planet_osm_point_points")
commercial = ee.FeatureCollection("users/taminamatti/MOZ_centers_commercial_planet_osm_point_points")
education = ee.FeatureCollection("users/taminamatti/MOZ_centers_education_planet_osm_point_points")
emergency = ee.FeatureCollection("users/taminamatti/MOZ_centers_emergency_planet_osm_point_points")
financial = ee.FeatureCollection("users/taminamatti/MOZ_centers_financial_planet_osm_point_points")
government = ee.FeatureCollection("users/taminamatti/MOZ_centers_government_planet_osm_point_points")

cities = ee.FeatureCollection("users/jc23500/Mozambique_cities_planet_osm_point_points")