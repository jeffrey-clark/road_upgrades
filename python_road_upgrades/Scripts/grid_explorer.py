from Functions.processes import *
import Functions.grid_cells as g
from Imports.image_collections import *

#ee.Initialize()

time1 = ["2017-05-01", "2017-07-31"]
time2 = ["2021-01-01", "2021-03-31"]

# TO LOOK AT A ROAD, ENTER INDEX AS n
road_set = wb_roads
road_set_name = "wb_roads"

#how many roads do we have in the road set
print(f"Road count in {road_set_name}: {road_set.size().getInfo()}")

# if we want to look at a specific road fill in below
n = 139
print("Analyzing road:", n)

# get the road from the imported roads FeatureCollection
road = ee.Feature(road_set.toList(n+1).get(n))

# extract the subroads
subroads = road.geometry().geometries()
subroad_count = subroads.length().getInfo()

for i in range(0, subroad_count):
    road_geom = ee.Geometry(subroads.get(i))
    print("   Analyzing subroad", i)

    # strip_grid = createStripGrid(road_geom, 1, 10, "segment")
    strip_grid = g.createStripGrid(road_geom, 1, 10, "road")

    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022]
    grid_list = g.analyzeGrid(strip_grid, years)

    grid_list = g.computeNearestDistances(grid_list, "nearest_commercial", commercial)

    info = grid_list.getInfo()
    for i in range(0, len(info)):
        print(f"  GRID {i}:")
        g = info[i]['properties']
        for k in list(g.keys()):
            print(f"    {k}: {g[k]}")
        print("")


