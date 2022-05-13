import ee
import pandas as pd

ee.Initialize()

from Imports.road_collections import *

id_list = ee.List(list(range(0, 219)))

def getConcat(n):
    road = ee.Feature(wb_roads.toList(ee.Number(n).add(1)).get(ee.Number(n)))
    return road.toDictionary(road.propertyNames())

concat_list = id_list.map(getConcat).getInfo()


output_dics = []
for i in range(0, 219):
    concat_dic = concat_list[i]
    dic = {'road_id': i, 'concat': concat_dic['concat'],
           'district': concat_dic['DISTRICT_f'],
           'province': concat_dic['PROVINCE_f']}
    output_dics.append(dic)


df = pd.DataFrame(output_dics)

writer = pd.ExcelWriter(f"../Exports/id_concat_table.xlsx", engine='xlsxwriter', options={'strings_to_urls': False})
df.to_excel(writer, index=False)
writer.close()
