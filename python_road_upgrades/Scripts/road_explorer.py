from Functions.processes import *

time1 = ["2017-05-01", "2017-07-31"]
time2 = ["2021-01-01", "2021-03-31"]

# TO LOOK AT A ROAD, ENTER INDEX AS n
road_set = wb_roads
road_set_name = "wb_roads"

#how many roads do we have in the road set
print(f"Road count in {road_set_name}: {road_set.size().getInfo()}")

# if we want to look at a specific road fill in below
n = 7
print("Analyzing road:", n)

# get the road from the imported roads FeatureCollection
road = ee.Feature(road_set.toList(n+1).get(n))

# extract the subroads
subroads = road.geometry().geometries()
subroad_count = subroads.length().getInfo()

for i in range(0, subroad_count):
    road_geom = ee.Geometry(subroads.get(i))

    # continue if the road is less than 500 meters
    if road_geom.length().getInfo() < 500:
        continue

    print("   Analyzing subroad", i)
    road = roadAnalysis(road_geom, time1, time2, output="f")

    analysis_bright = road.get("analysis_bright")
    analysis_dark = road.get("analysis_dark")

    print("ANALYSIS BRIGHT", analysis_bright.getInfo())
    print("ANALYSIS DARK", analysis_dark.getInfo())
    print("LENGTH IS", road.get("length_km").getInfo())
    print("UPGRADE TYPE IS", road.get("upgrade_type").getInfo())
