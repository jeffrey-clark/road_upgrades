import ee
import googleapiclient.errors

import Functions.general as f
import Functions.grid_cells as g
import Models.RoadExportModel as RM
import Models.CellExportModel as CM
import Imports.image_collections as IC


from Imports.geometries import *
from Imports.road_collections import *

import math
import time
import datetime
import pandas as pd


def roadAnalysis(road_geom, time1, time2, output="obj"):

    # If the road_geom is a feature because it came from a feature collection e.g. Nampula_N
    # then we first convert it to a geometry by extracting the geometry
    if isinstance(road_geom, ee.computedobject.ComputedObject):
        road_geom = ee.Feature(road_geom).geometry()

    print("length of road geom", road_geom.length().getInfo())

    # if the road_geom is greater than 5 km, split it (MOVE LOAD FROM SERVER TO CLIENT)
    strip_list = g.splitGeom(road_geom, 5, include_remainder=True)
    strip_list_length = strip_list.length().getInfo()

    analysis_list = []

    if strip_list_length == 1:
        # convert the road geometry to a feature
        road = f.processRoad(ee.Geometry(road_geom))

        # add band values as properties to the road feature
        road = f.analyzeBandsInDiff(road, ['B4', 'B8'], time1, time2)
    else:
        for i in range(0, strip_list_length):

            print(f"       strip {i}/{strip_list_length-1}")

            strip_geom = ee.Geometry(strip_list.get(i))


            try:   # CONTROL FOR INTERNAL ERRORS
                # convert the road geometry to a feature
                road_strip = f.processRoad(strip_geom)

                # add band values as properties to the road feature
                road_strip = f.analyzeBandsInDiff(road_strip, ['B4', 'B8'], time1, time2).getInfo()
                # print(road_strip)
                analysis_list.append(road_strip)

            except Exception as e:
                if str(e)[0:30] == "An internal error has occurred":  # HERE WE ADJUST FOR THE ERROR
                    print(f"There was an Internal Error, skipping road!")
                    return None

                if str(e)[0:15] == "Feature.toArray":
                    print(f"Error in array compilation, skipping road!")
                    return None
                else:
                    print(e)
                    raise ValueError(f"GEE ERROR: {e}")
        # merge the analysis list into one single road feature element
        road = None

        for a in analysis_list:

            if analysis_list.index(a) == len(analysis_list)-1:
                last_round = True
            else:
                last_round = False

            if road == None:
                road = a
                road_p = road['properties']
            else:
                a_p = a['properties']

                def copy_list_between_dics(dic1, dic2, key):
                    #print(f"road property: {key} = {len(dic1[key])}")
                    #print(f"a property: {key} = {len(dic2[key])}")
                    dic1[key] = dic1[key] + dic2[key]
                    #print(f"merged property: {key} = {len(dic1[key])}")
                    return dic1[key]


                for k in list(road_p.keys()):

                    if type(road_p[k]) == float:
                        road_p[k] = road_p[k] + a_p[k]

                    if type(road_p[k]) == list:
                        road_p[k] = copy_list_between_dics(road_p, a_p, k)

                        # clean in the end
                        if last_round and output in ["f", "feat"]:
                            road_p[k] = ee.List(road_p[k])

                    elif type(road_p[k]) == dict:
                        for k2 in list(road_p[k].keys()):
                            if type(road_p[k][k2]) == list:
                                road_p[k][k2] = copy_list_between_dics(road_p[k], a_p[k], k2)

                                # clean in the end
                                if last_round and output in ["f", "feat"]:
                                    road_p[k][k2] = ee.List(road_p[k][k2])

                        if last_round and output in ["f", "feat"]:
                            road_p[k] = ee.Dictionary(road_p[k])


        if output in ['o', 'obj', 'object']:
            road = {"geom": ee.Geometry(road_geom).getInfo(), 'properties': road_p}
        else:
            road = ee.Feature(ee.Geometry.LineString(road_geom.coordinates()), ee.Dictionary(road_p))


    # road = f.determineUpgrade(road)

    if output in ['o', 'obj', 'object']:
        road_obj = RM.Road(road)
        return road_obj

    elif output in ['f', 'feat', 'feature']:
        return road
    else:
        raise ValueError("ERROR! invalid argument 'output'. Revise pls")


def roadAnalysis_BATCH(region_name, geom_feature_col, specific_ids, time1, time2, output="obj", batch_size=10,
                       from_index=0, to_index="max"):

    # Initialize the output dataframe
    output_df = RM.Spreadsheet(f"{region_name}.xlsx")


    if specific_ids != None:
        geom_feature_col = ee.FeatureCollection(f.subsetFeatureCollection(geom_feature_col, specific_ids))

    # compute the size of the geom feature collection
    size = geom_feature_col.size().getInfo()

    if specific_ids == None:
        specific_ids = list(range(0, size))

    # compute the number of rounds
    rounds = math.ceil(size / batch_size)

    # loop through the rounds
    for i in range(0, rounds):
        offset = batch_size * i

        # skip already completed roads
        if (offset + 10) <= (output_df.last_road + 1):
            continue

        print("offset is", offset)

        feat_list = ee.List(geom_feature_col.toList(batch_size, offset))
        geom_list = feat_list.map(lambda f: ee.Feature(f).geometry())

        for i in range(0, geom_list.length().getInfo()):

            road_id = offset + i

            if road_id < (output_df.last_road):
                continue

            print(f"processing road {road_id}/{size-1}  ({specific_ids[i]})")

            # confirm that the geom is a LineString and not MultiLineString or some other Polygon
            # if ee.String(ee.Geometry(geom_list.get(i)).type()).getInfo() != "LineString":
            #     output_df.appendRoad(region_name, road_id, ['Error', 'Road not single Line'])
            #     continue

            # extract the subroads
            subroads = ee.List(ee.Geometry(geom_list.get(i)).geometries())
            subroad_count = subroads.length().getInfo()

            # loop through the subroads

            # clear the point_df
            output_df.df_points = pd.DataFrame()

            for subroad_id in range(0, subroad_count):

                # skip already processed subroads
                if (subroad_id <= output_df.last_subroad) and (road_id == output_df.last_road) and (len(output_df.df) != 0):
                    continue

                # get the subroad geometry
                road_geom = ee.Geometry(subroads.get(subroad_id))
                # compute the subroad length and skip if less than 500 meters
                road_feature = f.processRoad(road_geom)
                length_km = road_feature.get('length_km').getInfo()
                if length_km < 0.5:
                    continue

                print(f"    analyzing subroad {subroad_id}/{subroad_count-1}")
                road = roadAnalysis(road_geom, time1, time2, output="o")
                if road != None:
                    output_df.appendRoad(region_name, specific_ids[road_id], subroad_id, road)

            # if the length of the road was greater than 10km, save right away
            # if road_length > 10:
            #     output_df.save_progress()
            #     print("saved because road was longer than 10km")
            output_df.save_progress()

        output_df.save_progress()

    return True


def gridAnalysis(road_geom, road_segment_length, grid_cell_height, years=None,
                 start_mm_dd="01-01", end_mm_dd="03-31", output="obj"):

    # If the road_geom is a feature because it came from a feature collection e.g. Nampula_N
    # then we first convert it to a geometry by extracting the geometry
    if isinstance(road_geom, ee.computedobject.ComputedObject):
        road_geom = ee.Feature(road_geom).geometry()

    # create the strip grid usign the segments direction
    #strip_grid = g.createStripGrid(road_geom, 1, 10, "segment")
    # create the strip grid using the roads direction
    strip_grid = g.createStripGrid(road_geom, road_segment_length, grid_cell_height, "road")

    # HOW LONG IS THE STRIP_GRID ?

    grid_length = strip_grid.length().getInfo()

    if not isinstance(years, list):
        years = [2016, 2017, 2018, 2019, 2020, 2021, 2022]


    if output in ['o', 'obj', 'object']:

        # Process the strip grid one at a time
        output = []
        for i in range(0, grid_length):
            print(f"      processing grid {i+1} out of {grid_length}")
            grid_list = ee.List([strip_grid.get(i)])


            grid_list = g.analyzeGrid(grid_list, years, start_mm_dd, end_mm_dd)

            grid_list = g.computeNearestDistances(grid_list, "nearest_city", IC.cities)

            cell_fe = ee.Feature(grid_list.get(0))
            cell_fe = cell_fe.set("id_row", i)

            output.append(CM.Cell(cell_fe))
        return output

    elif output in ['f', 'feat', 'feature']:
        grid_list = g.analyzeGrid(strip_grid, years, start_mm_dd, end_mm_dd)
        grid_list = g.computeNearestDistances(grid_list, "nearest_city", IC.cities)
        return grid_list
    else:
        raise ValueError("ERROR! invalid argument 'output'. Revise pls")


def gridAnalysis_BATCH(region_name, geom_feature_col, road_segment_length, grid_cell_height, year_list=None,
                       start_mm_dd="01-01", end_mm_dd="02-28",
                       output="obj", batch_size=10, from_index=0, to_index="max"):

    if not isinstance(year_list, list):
        year_list = [2016, 2017, 2018, 2019, 2020, 2021, 2022]

    # Initialize the output dataframe
    output_df = CM.Spreadsheet(f"{region_name}.xlsx", road_segment_length, grid_cell_height)

    # compute the size of the geom feature collection
    size = geom_feature_col.size().getInfo()
    #print("SIZE IS", size)
    # compute the number of rounds
    rounds = math.ceil(size / batch_size)

    # loop through the rounds
    for i in range(0, rounds):
        offset = batch_size * i

        # skip already completed roads
        if (offset + 10) <= (output_df.last_road + 1):
            continue

        print("offset is", offset)

        feat_list = ee.List(geom_feature_col.toList(batch_size, offset))
        geom_list = feat_list.map(lambda f: ee.Feature(f).geometry())

        for i in range(0, geom_list.length().getInfo()):

            road_id = offset + i

            if road_id < (output_df.last_road):
                continue

            print(f"processing road {road_id}/{size-1}")

            # confirm that the geom is a LineString and not MultiLineString or some other Polygon
            # if ee.String(ee.Geometry(geom_list.get(i)).type()).getInfo() != "LineString":
            #     output_df.appendRoad(region_name, road_id, ['Error', 'Road not single Line'])
            #     continue

            # extract the subroads
            subroads = ee.List(ee.Geometry(geom_list.get(i)).geometries())
            subroad_count = subroads.length().getInfo()

            # loop through the subroads
            for subroad_id in range(0, subroad_count):

                # skip already processed subroads
                if (subroad_id <= output_df.last_subroad) and (road_id == output_df.last_road) and (len(output_df.df) != 0):
                    continue

                # get the subroad geometry
                road_geom = ee.Geometry(subroads.get(subroad_id))
                # compute the subroad length and skip if less than 500 meters
                road_feature = f.processRoad(road_geom)
                length_km = road_feature.get('length_km').getInfo()
                if length_km < 0.5:
                    continue

                print(f"    analyzing subroad {subroad_id}/{subroad_count-1}")


                # here we can subset the years
                #
                #
                year_list_subsets = []
                chunk_size = 8
                if len(year_list) > chunk_size:
                    subset_count = math.ceil(len(year_list)/chunk_size)
                    for subset_id in range(0, subset_count):
                        start_index = chunk_size * subset_id
                        end_index = chunk_size * (subset_id + 1)
                        if end_index > len(year_list):
                            end_index = len(year_list)
                        year_list_subsets.append(year_list[start_index:end_index])
                else:
                    year_list_subsets = [year_list]

                merged_cell_list = None
                for year_subset in year_list_subsets:
                    cell_list = gridAnalysis(road_geom, road_segment_length, grid_cell_height, year_subset,
                                             start_mm_dd, end_mm_dd, output="o")
                    if merged_cell_list is None:
                        merged_cell_list = cell_list
                    else:
                        for o in range(0, len(cell_list)):
                            for att in list(merged_cell_list[0].__dict__.keys()):
                                existing_att_val = getattr(merged_cell_list[o], att)
                                if existing_att_val is None:
                                    new_att_val = getattr(cell_list[o], att)
                                    setattr(merged_cell_list[o], att, new_att_val)


                for i in range(0, len(merged_cell_list)):
                    print("ROW ID IS", merged_cell_list[i].row_id)
                    cell_to_append = merged_cell_list[i]
                    output_df.appendCell(region_name, road_id, subroad_id, cell_to_append)

                # shorter_geoms = g.splitGeom(road_geom, 1)
                # cell_count_buffer = 0
                # shorter_geoms_length = shorter_geoms.length().getInfo()
                # for z in range(0, shorter_geoms_length):
                #     geom = shorter_geoms.get(z)
                #     if shorter_geoms_length > 1:
                #         print(f"      batch {z+1} / {shorter_geoms_length}")
                #
                #     output_type = "o"
                #     cell_list = gridAnalysis(geom, year_list, start_mm_dd, end_mm_dd, output=output_type, skip_split=True)
                #
                #     if output_type == "f":
                #         cell_list_len = ee.Number(cell_list.length()).getInfo()
                #     else:
                #         cell_list_len = len(cell_list)
                #
                #     for i in range(0, cell_list_len):
                #         if output_type == "f":
                #             cell_to_append = ee.Feature(cell_list.get(i))
                #             cell_to_append = cell_to_append.set('id_row', (i + cell_count_buffer))
                #         else:
                #             cell_to_append = cell_list[i]
                #             cell_to_append.row_id = i + cell_count_buffer
                #         # update the row_id
                #
                #         output_df.appendCell(region_name, road_id, subroad_id, cell_to_append)
                #
                #     cell_count_buffer = cell_count_buffer + cell_list_len


            # if the length of the road was greater than 10km, save right away
            # if road_length > 10:
            #     output_df.save_progress()
            #     print("saved because road was longer than 10km")
            output_df.save_progress()

        output_df.save_progress()

    return True




if __name__ == "__main__":
    # specify dates of interest
    date1 = ["2017-05-01", "2017-07-31"]
    date2 = ["2021-01-01", "2021-03-31"]


    complete = False
    while not complete:
        # Now let us load in multiple geometries

        #complete = roadAnalysis_BATCH("WORLDBANK", wb_roads, date1, date2)

        try:
            # Tamina spreadsheet namn i citat nedan
            complete = roadAnalysis_BATCH("WORLDBANK_t", wb_roads, date1, date2)
            print(datetime.datetime.now())
        except:
            # wait 30 minutes
            print("Memory fail, restarting")

            print("sleeping")
            #time.sleep(60)

