import sys, re, os
import math

#-------------- NESTED PATH CORRECTION --------------------------------#

# For all script files, we add the parent directory to the system path
import ee
import googleapiclient.errors

cwd = re.sub(r"[\\]", "/", os.getcwd())
cwd_list = cwd.split("/")
path = re.sub(r"[\\]", "/", sys.argv[0])
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

import Functions.general as f
from Imports.road_collections import *

##### PARAMETERS TO SET ########

road_set = Pemba_N
export_filename = "Pemba_N_Upgraded"
export_type = "asset"     # "asset" or "shp"

road_ids_to_subset = [
    629, 630, 4893, 6229, 6299, 6339, 7349, 7872, 8400, 8427, 10615, 13097, 14721, 14723, 14739, 14761, 21696, 21778,
    21779, 21779, 21780, 21781, 21857, 21866, 21866, 21939, 23542, 23711, 23800, 23800, 23861, 23879, 24081, 24084,
    24176, 25072, 25075, 25122, 25135, 25142, 25154, 25159, 25326, 25358, 25362, 25401, 25408
]



#################################

# subset 20 roads at a time
batch_n = 20
subsets = []
batches = math.ceil(len(road_ids_to_subset)/batch_n)
for b in range(0, batches):
    batch_ids = road_ids_to_subset[(b*batch_n): ((b+1)*batch_n)]
    print("lenght of batch is", len(batch_ids), batch_ids)
    batch_subset = f.subsetFeatureCollection(road_set, batch_ids)
    #print(batch_subset.getInfo())
    subsets.append(batch_subset.toList(batch_n, 0).getInfo())


# merge the lists
merged_list = [item for sublist in subsets for item in sublist]
# convert the feature collection
road_subset = ee.FeatureCollection(merged_list)

if export_type == "shp":
    # export the feature collection as a shape file
    task_config = {
         #'region': water_image,
         'folder':'Exports',
         'fileFormat': "SHP",
     }
    task = ee.batch.Export.table.toDrive(road_subset, export_filename, **task_config)
    task.start()
    task.status()

elif export_type == 'asset':
    task = ee.batch.Export.table.toAsset(road_subset, export_filename, assetId="users/jc23500/Pemba_N_Upgraded")
    task.start()
    task.status()
