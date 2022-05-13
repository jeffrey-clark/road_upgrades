import sys, re, os

#-------------- NESTED PATH CORRECTION --------------------------------#

# For all script files, we add the parent directory to the system path
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

from Functions.processes import *

##### PARAMETERS TO SET ########

spreadsheet_filename = "client_side"

# specify dates of interest
# Tamina ran the code on 21/2 and changed the dates in date2.
# Tamina ran the code on 28/2 and changed the dates in date2.
date1 = ["2017-05-01", "2017-07-31"]
date2 = ["2018-05-01", "2018-07-31"]

road_set = wb_roads

specific_road_ids = None
#specific_road_ids = []
#specific_road_ids = [7, 14, 82]

#################################


# for server CLI execution
try:

    modname = globals()['__name__']
    modobj = sys.modules[modname]

    spreadsheet_filename = sys.argv[1]

    roads_str = sys.argv[2]    # string name of road_set
    road_set = getattr(modobj, roads_str)

    date1_1 = sys.argv[3]
    date1_2 = sys.argv[4]
    date2_1 = sys.argv[5]
    date2_2 = sys.argv[6]

    date1 = [date1_1, date1_2]
    date2 = [date2_1, date2_2]

except:
    pass



complete = False
while not complete:
    # Now let us load in multiple geometries

    #complete = roadAnalysis_BATCH(spreadsheet_filename, road_set, specific_road_ids, date1, date2)

    try:

        complete = roadAnalysis_BATCH(spreadsheet_filename, road_set, specific_road_ids, date1, date2)
        print(datetime.datetime.now())
    except KeyboardInterrupt:
        exit()
    except:
        # wait 30 minutes
        print("Memory fail, restarting")

        print("sleeping")
        time.sleep(15)