import ee
import pandas as pd
import os, sys, re


class Spreadsheet:
    def __init__(self, filename, cell_width, cell_height):
        self.df = pd.DataFrame()
        self.filename = filename
        # compute the project_dir
        project_dir = re.search(r"^(.*road_upgrades)", os.getcwd()).group(1)
        export_dir = f"{project_dir}/Exports/Cells/{cell_width}x{cell_height}"
        if not os.path.isdir(export_dir):
            os.mkdir(export_dir)
        self.filepath = f"{export_dir}/{self.filename}"
        # if the file exists, load in existing df, and check how many rows are completed
        self.row_count = 0
        self.last_road = 0
        self.last_subroad = 0

        if os.path.isfile(self.filepath):
            self.df = pd.read_excel(self.filepath)
            self.row_count = len(self.df)
            self.last_road = self.df['road_id'].iloc[-1]
            self.last_subroad = self.df['subroad_id'].iloc[-1]

            print(self.df)
            print("last road is", self.last_road)
            print("last subroad is", self.last_subroad)

    def appendCell(self, region_name, road_id, subroad_id, road_feature):
        '''
        appends a road to the output df
        :param road_object: road object from Road Export Model
        :return: Appends a row to self (df)
        '''

        # if the road feature is in fact a python object
        if isinstance(road_feature, Cell):
            to_append = road_feature.convert_df(region_name, road_id, subroad_id)
        else:
            # Convert the road feature to Road Object row insertion
            to_append = Cell(road_feature).convert_df(region_name, road_id, subroad_id)

        if self.df.empty:
            self.df = to_append
        else:
            self.df = pd.concat([self.df, to_append])

    def save_progress(self):
        writer = pd.ExcelWriter(self.filepath, engine='xlsxwriter', options={'strings_to_urls': False})
        self.df.to_excel(writer, index=False)
        writer.close()


class Cell:
    def __init__(self, feature):

        if isinstance(feature, ee.feature.Feature):
            # control for objects/dictionaries being passed
            feature = feature.getInfo()
        else:
            pass # feature is already an object

        #self.geometry = feature['geometry']
        p = feature['properties']

        self.row_id = p['id_row']
        self.col_id = p['id_col']
        self.width = p['width']
        self.height = p['height']
        self.area = p['area']
        self.population = p['population']
        self.nearest_city = p['nearest_city']

        for var in ["NDVI", "rainfall"]:
            for year in list(range(2010, 2023)):

                att = f"{var}_{year}"
                if att in list(p.keys()):
                    setattr(self, att, p[att])
                else:
                    setattr(self, att, None)

        self.error = None



    def convert_df(self, region_name, road_id, subroad_id):

        df_dic = {
            "region": [region_name],
            "road_id": [road_id],
            "subroad_id": [subroad_id],
            "row_id": [self.row_id],
            "col_id": [self.col_id],
            "width": [self.width],
            "height": [self.height],
            "area": [self.area],
            "population": [self.population],
            "nearest_city": [self.nearest_city]
        }

        for var in ["NDVI", "rainfall"]:
            for year in list(range(2010, 2023)):
                att = f"{var}_{year}"
                df_dic[att] = getattr(self, att)

        df_dic['error'] = self.error

        df = pd.DataFrame(df_dic)

        return df



