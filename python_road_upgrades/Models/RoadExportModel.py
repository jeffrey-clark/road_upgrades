import ee
import pandas as pd
import os, sys, re
import numpy as np
import math


class Spreadsheet:
    def __init__(self, filename):
        self.df = pd.DataFrame()
        self.df_points = pd.DataFrame()
        self.filename = filename
        if self.filename[-5:] == ".xlsx":
            self.filename = self.filename[:-5]
        # compute the project_dir
        self.project_dir = re.search(r"^(.*road_upgrades)", os.getcwd()).group(1)
        self.filepath = f"{self.project_dir}/Exports/Roads/{self.filename}.xlsx"
        self.filepath_points = f"{self.project_dir}/Exports/Points/{self.filename}_points_0.csv"
        self.row_count = 0
        self.last_road = 0
        self.last_subroad = 0

        # if the file exists, load in existing df, and check how many rows are completed
        if os.path.isfile(self.filepath):
            self.df = pd.read_excel(self.filepath, engine='openpyxl')
            self.row_count = len(self.df)
            self.last_road = self.df['road_id'].iloc[-1]
            self.last_subroad = self.df['subroad_id'].iloc[-1]

            self.update_point_fp()

            # make sure that there is a corresponding point file and that there are points for all roads
            if os.path.isfile(self.filepath_points):
                #self.df_points = pd.read_excel(self.filepath_points, engine='openpyxl')
                pass

            else:
                raise ValueError(f"Missing point file: {self.filepath_points}")

            print(self.df)
            print("last road is", self.last_road)
            print("last subroad is", self.last_subroad)


    def update_point_fp(self):
        # compute the filepath points, considering the file splitting
        fp_suffix = math.floor(self.df.shape[0] / 50)
        #fp_suffix = math.floor((road_id) / 50) * 50
        self.filepath_points = f"{self.project_dir}/Exports/Points/{self.filename}_points_{fp_suffix}.csv"

    def appendRoad(self, region_name, road_id, subroad_id, road_feature):
        '''
        appends a road to the output df
        :param road_object: road object from Road Export Model
        :return: Appends a row to self (df)
        '''

        self.update_point_fp()

        if isinstance(road_feature, Road):
            road = road_feature

        elif isinstance(road_feature, ee.feature.Feature):
            # Convert the road feature to Road Object row insertion
            road = Road(road_feature)
        else:
            raise ValueError("ERROR IN FORMAT OF ROAD IN APPENDING PROCESS")

        road_to_append = road.convert_df(region_name, road_id, subroad_id)
        points_to_append = road.export_points_df(region_name, road_id, subroad_id)

        if self.df.empty:
            self.df = road_to_append
        else:
            self.df = pd.concat([self.df, road_to_append])

        if self.df_points.empty:
            self.df_points = points_to_append
        else:
            self.df_points = pd.concat([self.df_points, points_to_append])


    def save_progress(self):

        # export the point data to excel
        #writer = pd.ExcelWriter(self.filepath_points, engine='xlsxwriter', options={'strings_to_urls': False})
        #self.df_points.to_excel(writer, index=False)
        #writer.close()
        if os.path.isfile(self.filepath_points):
            self.df_points.to_csv(self.filepath_points, mode="a", index=False, header=False)
        else:
            self.df_points.to_csv(self.filepath_points, index=False, header=True)

        # export the road data to excel
        writer = pd.ExcelWriter(self.filepath, engine='xlsxwriter', options={'strings_to_urls': False})
        self.df.to_excel(writer, index=False)
        writer.close()



class Road:
    def __init__(self, feature):
        if isinstance(feature, ee.feature.Feature):
            feature = feature.getInfo()
            
            self.geometry = feature['geometry']
            p = feature['properties']

        elif isinstance(feature, dict):
            self.geometry = feature['geom']
            p = feature['properties']

        else:
            print("Inserted type into Road class is", type(feature))
            raise ValueError("Review class type to Road Class")

        # # ANALYSIS BRIGHT
        # b = p['analysis_bright']
        # self.analysis_bright = b
        # self.b_share_B4 = b['share_B4']
        # self.b_share_B4_left = b['share_B4_left']
        # self.b_share_B4_right = b['share_B4_right']
        # self.b_share_B8 = b['share_B8']
        # self.b_share_B8_left = b['share_B8_left']
        # self.b_share_B8_right = b['share_B8_right']
        # # ANALYSIS DARK
        # d = p['analysis_dark']
        # self.analysis_dark = d
        # self.d_share_B4 = d['share_B4']
        # self.d_share_B4_left = d['share_B4_left']
        # self.d_share_B4_right = d['share_B4_right']
        # self.d_share_B8 = d['share_B8']
        # self.d_share_B8_left = d['share_B8_left']
        # self.d_share_B8_right = d['share_B8_right']

        self.length_km = p['length_km']
        self.points = p['points']
        self.points_control = p['points_control']
        self.segment_directions = p['segment_directions']
        self.segment_lengths = p['segment_lengths']
        self.segment_orth_directions = p['segment_orth_directions']


    def export_points_df(self, region_name, road_id, subroad_id):

        all_points = []

        point_lists = {
            "road": self.points,
            "left_25": self.points_control['left_25'],
            "left_50": self.points_control['left_50'],
            "left_75": self.points_control['left_75'],
            "right_25": self.points_control['right_25'],
            "right_50": self.points_control['right_50'],
            "right_75": self.points_control['right_75']
        }

        for list_name in list(point_lists.keys()):
            for id in range(0, len(point_lists[list_name])):
                p = point_lists[list_name][id]
                point = {
                    "road": road_id,
                    "subroad": subroad_id,
                    "type": list_name,
                    "id": id,
                    "coords": p['geometry']['coordinates']
                }

                # correct the diff factor array
                p['properties']['B4_diff_factor'] = p['properties']['diff_factors']["B4"]
                p['properties']['B8_diff_factor'] = p['properties']['diff_factors']["B8"]

                p['properties'].pop('diff_factors', None)

                point.update(p['properties'])

                all_points.append(point)

        return pd.DataFrame(all_points)


    def convert_df(self, region_name, road_id, subroad_id):

        data = {}

        # set the df column order
        atts = ["region", "road_id", "subroad_id", "length_km", "upgraded", "upgrade_type",
                #"b_share_B4", "b_share_B4_left", "b_share_B4_right", "b_share_B8", "b_share_B8_left",
                # "b_share_B8_right", "d_share_B4", "d_share_B4_left", "d_share_B4_right", "d_share_B8",
                # "d_share_B8_left", "d_share_B8_right",
                "start_coords", "end_coords", "segment_lengths", "segment_directions", "error"]

        for a in atts:
            data[a] = [None]

        # set the values that we have for sure
        data["region"] = [region_name]
        data["road_id"] = [road_id]
        data["subroad_id"] = [subroad_id]
        data["length_km"] = [self.length_km]
        data["start_coords"] = [self.geometry['coordinates'][0]]
        data["end_coords"] = [self.geometry['coordinates'][-1]]
        data['segment_lengths'] = [self.segment_lengths]
        data['segment_directions'] = [self.segment_directions]

        # try:
        #     data["b_share_B4"] = self.analysis_bright['share_B4']
        #     data["b_share_B4_left"] = self.analysis_bright['share_B4_left']
        #     data["b_share_B4_right"] = self.analysis_bright['share_B4_right']
        #     data["b_share_B8"] = self.analysis_bright['share_B8']
        #     data["b_share_B8_left"] = self.analysis_bright['share_B8_left']
        #     data["b_share_B8_right"] = self.analysis_bright['share_B8_right']
        #
        #     data["d_share_B4"] = self.analysis_dark['share_B4']
        #     data["d_share_B4_left"] = self.analysis_dark['share_B4_left']
        #     data["d_share_B4_right"] = self.analysis_dark['share_B4_right']
        #     data["d_share_B8"] = self.analysis_dark['share_B8']
        #     data["d_share_B8_left"] = self.analysis_dark['share_B8_left']
        #     data["d_share_B8_right"] = self.analysis_dark['share_B8_right']
        #
        # except:
        #     pass

        # print(data)

        df = pd.DataFrame(data)
        df.columns = atts

        return df
