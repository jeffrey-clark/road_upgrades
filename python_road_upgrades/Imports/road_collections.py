import ee
# Import all of the road regions
Lichinga_N = ee.FeatureCollection("users/jc23500/Roads_MOZ_Lichinga_N_planet_osm_line_lines")
Lichinga_S = ee.FeatureCollection("users/jc23500/Roads_MOZ_Lichinga_S_planet_osm_line_lines")
Nampula_N = ee.FeatureCollection("users/jc23500/Roads_MOZ_Nampula_N_planet_osm_line_lines")
Nampula_S = ee.FeatureCollection("users/jc23500/Roads_MOZ_Nampula_S_planet_osm_line_lines")
Pemba_N = ee.FeatureCollection("users/jc23500/Roads_MOZ_Pemba_N_planet_osm_line_lines")
Pemba_S = ee.FeatureCollection("users/jc23500/Roads_MOZ_Pemba_S_planet_osm_line_lines")
wb_roads = ee.FeatureCollection("users/jc23500/master_roads")

Sierra_Leone_N = ee.FeatureCollection("users/jc23500/Sierra_Leone_N")
Sierra_Leone_S = ee.FeatureCollection("users/jc23500/Sierra_Leone_S")

Uganda_N = ee.FeatureCollection("users/jc23500/Uganda_N")
Uganda_C = ee.FeatureCollection("users/jc23500/Uganda_C")
