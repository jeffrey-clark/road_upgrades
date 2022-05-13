import sys, re, os
import ee
ee.Initialize()

from Imports.road_collections import *
import Functions.map_functions as mf

#-------------- NESTED PATH CORRECTION --------------------------------#

# For all script files, we add the parent directory to the system path
cwd = re.sub(r"[\\]", "/", os.getcwd())
cwd_list = cwd.split("/")
path = sys.argv[0]
path_list = path.split("/")
# either the entire filepath is entered as command i python
if cwd_list[0:3] == path_list[0:3]:
    full_path = path
# or a relative path is entered, in which case we append the path to the cwd_path
else:
    full_path = cwd + "/" + path
# remove the overlap
root_dir = re.search(r"(^.+python_road_upgrades)", full_path).group(1)
sys.path.append(root_dir)

#----------------------------------------------------------------------#


time1 = ["2019-07-01", "2019-09-30"]
time2 = ["2020-07-01", "2020-09-30"]

# TO LOOK AT A ROAD, ENTER INDEX AS n
road_set = wb_roads
road_set_name = "wb_roads"
specific_road_ids = [90]

#road_set = Nampula_S
#road_set_name = "nampula_s"
# specific_road_ids = [1790, 9550, 10256, 10490, 10573, 10721, 10723, 10917, 11716, 11878, 11927, 11932,
#                      11934, 11939, 11965, 11969]

# road_set = Pemba_N
# road_set_name = "pemba_N"
# specific_road_ids = [244]

# road_set = Pemba_S
# road_set_name = "pemba_S"
# specific_road_ids = [4780]  #[4789, 4846, 4851]

# road_set = Lichinga_N
# road_set_name   = "lichinga_N"
# specific_road_ids = [4266]

# road_set = Lichinga_S
# road_set_name = "lichinga_S"
# specific_road_ids = [2140]

# road_set = Nampula_N
# road_set_name = "nampula_N"
# specific_road_ids = [1, 14, 92]

#how many roads do we have in the road set
print(f"Road count in {road_set_name}: {road_set.size().getInfo()}")



for n in range(0, road_set.size().getInfo()):

    if len(specific_road_ids) > 0:
        if n not in specific_road_ids:
            continue

    print("Analyzing road:", n)

    # get the road from the imported roads FeatureCollection
    road = ee.Feature(road_set.toList(n+1).get(n))

    # extract the subroads
    subroads = road.geometry().geometries()
    subroad_count = subroads.length().getInfo()

    for i in range(0, subroad_count):

        # check if the files exist
        expdir = f"{root_dir}/Exports/Images/{road_set_name}_{time1[0]}_{time1[1]}_{time2[0]}_{time2[1]}"
        pngdir = f"{expdir}/png"
        skip = True
        suffixes = ["diff", "t1", "t2"]
        for s in suffixes:
            if not os.path.isfile(f"{pngdir}/{n}_{i}_{s}.png"):
                skip = False
                break
        if skip:
            print(f"skipping {n} {i}")
            continue

        road_geom = ee.Geometry(subroads.get(i))

        # continue if the road is less than 500 meters
        if road_geom.length().getInfo() < 500:
            continue

        mf.export_maps(expdir, road_geom, time1, time2, f"{n}_{i}")

