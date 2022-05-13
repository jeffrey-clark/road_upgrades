import sys, re, os

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

from Functions.processes import *

##### PARAMETERS TO SET ########

spreadsheet_filename = "grid_cells_01_02"

years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
start_mm_dd = "1-01"
end_mm_dd = "02-28"
road_segment_length = 1     # how many km should we split the road
grid_cell_height = 10       # how high should the grid cell be (km)

road_set = wb_roads

specific_road_ids = None
#specific_road_ids = [8, 12, 15]

#################################
# server CLI overwrite
try:
    spreadsheet_filename = sys.argv[1]  # string name of the excel sheet (without .xslx ending) e.g. "my_sheet"
    roads_str = sys.argv[2]             # string name of road_set (needs to correspond with existing variable)
                                        # e.g."wb_roads"

    modname = globals()['__name__']
    modobj = sys.modules[modname]
    road_set = getattr(modobj, roads_str)

    road_segment_length = sys.argv[3]   # how many km should we split the road
    grid_cell_height = sys.argv[4]      # how high should the grid cell be (km)

    years = sys.argv[5].split(" ")      # string of space-separated years e.g. "2010 2011 2012"
    start_mm_dd = sys.argv[6]           # month and day for start of composite period e.g. "01_01"  (note underscore)
    end_mm_dd = sys.argv[7]             # month and day for end of composite period e.g. "02_28"    (note underscore)
except:
    pass


##################################

def subsetFeatureCollection(fc, id_list):

    if id_list == None:
        return ee.FeatureCollection(fc)

    def getFeatureByID(fc):
        def wrap(id):
            return ee.FeatureCollection(fc).toList(1, ee.Number(id)).get(0)
        return wrap

    fc_list = ee.List(id_list).map(getFeatureByID(fc))
    return ee.FeatureCollection(fc_list)


roads = ee.FeatureCollection(subsetFeatureCollection(road_set, specific_road_ids))



complete = False
while not complete:
    # Now let us load in multiple geometries

    complete = gridAnalysis_BATCH(spreadsheet_filename, roads, float(road_segment_length), float(grid_cell_height),
                                  years, start_mm_dd, end_mm_dd)

    try:
        complete = gridAnalysis_BATCH(spreadsheet_filename, roads, float(road_segment_length), float(grid_cell_height),
                                      years, start_mm_dd, end_mm_dd)
        print(datetime.datetime.now())
    except KeyboardInterrupt:
        exit()
    except:
        # wait 30 minutes
        print("Memory fail, restarting")

        print("sleeping")
        time.sleep(60)