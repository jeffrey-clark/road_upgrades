import os
import sys
import re
import pandas as pd
import numpy as np

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

def dummy_row_distance(df, dummy, agg_list):
    if not isinstance(agg_list, list):
        raise ValueError("agg_list argument needs to be a list")
    output_index = df.reset_index().set_index([('road', ''), ('subroad', '')])
    filtered = df.loc[df[dummy] == 1,]
    dist = filtered.reset_index().loc[:, [('road', ''), ('subroad', ''), ('id', '')]].groupby(['road', 'subroad']).diff().fillna(0).values
    dist = pd.DataFrame(dist, index=filtered.index).reset_index().rename(columns={0: "dist"})
    dist = dist.reset_index()#.group_by(['road', 'subroad'])
    dist = dist.groupby(['road', 'subroad']).agg({'dist': agg_list})
    dist = dist.reindex(df.index.droplevel(2).unique())
    return dist

folder_name = "Pemba_N"        # directory should exist in Exports/Roads and Exports/Points
prefix = folder_name           # prefix in the road files e.g. roads_2018_2019_05_07.xlsx has prefix roads

dir_roads = f"{root_dir}/Exports/Roads/{folder_name}"
dir_points = f"{root_dir}/Exports/Points/{folder_name}"

files_roads = os.listdir(dir_roads)
files_points = os.listdir(dir_points)


# sort the point files in ascending order
point_file_id = [int(re.search(r"_(\d+).csv", x).group(1)) for x in files_points]
data = [{'fn': files_points[i], 'id': point_file_id[i]} for i in range(0, len(files_points))]
data = sorted(data, key = lambda x: x['id'])
files_points = [x['fn'] for x in data]


#for r in files_roads:
for r in files_roads:
    # r = "roads_2020_2021_05_07.xlsx"

    if not re.match(r"^" + re.escape(prefix) + r"_\d+_\d+.+", r):
        continue
    m = re.search(re.escape(prefix) + r"_(\d+)_(\d+)_(\d+)_(\d+).xlsx", r)
    year1, year2, month1, month2 = m.group(1), m.group(2), m.group(3), m.group(4)

    # load in the roads excel file
    fp_r = f"{dir_roads}/{r}"
    #df_r = pd.read_excel(fp_r, engine='openpyxl')

    # load in the csv points files and merge
    df_p = pd.DataFrame()
    for p in files_points:
        if r[:-5] in p:
            fp_p = f"{dir_points}/{p}"
            imported = pd.read_csv(fp_p)
            print(f"imported {fp_p}")
            if df_p.empty:
                df_p = imported
            else:
                df_p = pd.concat([df_p, imported])
    df_p = df_p.sort_values(by=["road", "subroad", "type", "id"])


    # reshape
    wide = pd.pivot_table(df_p, values=["B4_max", "B4_mean", "B4_min", "B8_max", "B8_mean", "B8_min", "B4_diff_factor",
                                        "B8_diff_factor" ], index=['road', 'subroad', 'id'], columns=['type'], aggfunc=np.sum)

    # adjust for the diff factor
    level1 = ['B4_max', 'B4_min', 'B4_mean', 'B8_max', 'B8_min', 'B8_mean']
    level2 = ['road', 'left_25', 'left_50', 'left_75', 'right_25', 'right_50', 'right_75']
    for l1 in level1:
        if l1[0:2] == "B4":
            diff_factor_array = wide.loc[:, ('B4_diff_factor', 'road')]
        elif l1[0:2] == "B8":
            diff_factor_array = wide.loc[:, ('B8_diff_factor', 'road')]
        else:
            raise ValueError("problem with diff factor adjustment")
        for l2 in level2:
            wide[(l1, l2)] = wide[(l1, l2)] - diff_factor_array
            #pass

    # rewrite the sides as a difference from the road and
    # create the averages
    level1 = ['B4_max', 'B4_min', 'B4_mean', 'B8_max', 'B8_min', 'B8_mean']
    for l1 in level1:
        # make sides relative
        # wide[[(l1, 'left_25'), (l1, 'left_50'), (l1, 'left_75')]] = wide[[(l1, 'left_25'), (l1, 'left_50'), (l1, 'left_75')]] - wide[[(l1, 'road')]].values
        # create the averages
        wide[(l1, 'left_avg')] =  wide[[(l1, 'left_25'), (l1, 'left_50'), (l1, 'left_75')]].mean(axis=1)
        wide[(l1, 'right_avg')] =  wide[[(l1, 'right_25'), (l1, 'right_50'), (l1, 'right_75')]].mean(axis=1)


    # thresholds, why not?
    # compute upgraded points
    thresholds = [50]

    for thresh in thresholds:
        level1 = ['B4_max', 'B8_max']
        upg = f"upg_{thresh}"
        for l1 in level1:
            wide[(l1, upg)] = ( (wide[(l1, 'road')] > thresh) &
                                (wide[(l1, 'left_avg')] <= 0.90 * wide[(l1, 'road')]) &
                                (wide[(l1, 'right_avg')] <= 0.90 * wide[(l1, 'road')]) ).astype(int)
        level1 = ['B4_min', 'B8_min']
        for l1 in level1:
            wide[(l1, upg)] = ( (wide[(l1, 'road')] < -thresh) &
                                (wide[(l1, 'left_avg')] >= 0.90 * wide[(l1, 'road')]) &
                                (wide[(l1, 'right_avg')] >= 0.90 * wide[(l1, 'road')]) ).astype(int)

    upg_list = [f"upg_{x}" for x in thresholds]

    # reorder columns
    col_index_list = []
    level1 = ['B4_max', 'B4_min', 'B4_mean', 'B8_max', 'B8_min', 'B8_mean', 'B4_diff_factor', 'B8_diff_factor']
    level2 = upg_list+['road', 'left_avg', 'right_avg', 'left_25', 'left_50', 'left_75', 'right_25', 'right_50', 'right_75']
    for l1 in level1:
        for l2 in level2:
            if l1 in ['B4_diff_factor', 'B8_diff_factor'] and l2 != "road":
                continue
            col_index_list.append((l1, l2))
    wide = wide.reindex(columns=col_index_list)

    # clean up by dropping NaN columns
    wide = wide.dropna(axis=1, how='all')



    # compute the total count in each subroad
    point_count = wide.reset_index().groupby(['road', 'subroad']).agg({('id', ''): 'count'}).values


    # generate the tuples for aggregation
    tup_dic = {}
    for l1 in ['B4_max', 'B4_min', 'B4_mean', 'B8_max', 'B8_min', 'B8_mean']:
        for l2 in ['road', 'left_avg', 'right_avg', f'upg_{thresholds[0]}']:
            if (l1, l2) in list(wide.columns):
                tup_dic[(l1, l2)] = 'mean'
            else:
                print(f"skipping {(l1, l2)}")

    tup_dic[('B4_diff_factor', 'road')] = 'mean'
    tup_dic[('B8_diff_factor', 'road')] = 'mean'

    brightness = wide.reset_index().groupby(['road', 'subroad']).agg(tup_dic)

    # rename the upg_0 to share
    brightness = brightness.rename(columns={f'upg_{thresholds[0]}': "share"})


    for l1 in ['B4_max', 'B4_min', 'B8_max', 'B8_min']:

        # aggregate the road, left and right avg of upgraded roads only
        upgraded_subset = wide.loc[wide[(l1, f'upg_{thresholds[0]}')] == 1, :]
        tup_dic = {}
        for l2 in ['road', 'left_avg', 'right_avg']:
            tup_dic[(l1, l2)] = 'mean'
        subset_aggs = upgraded_subset.reset_index().groupby(['road', 'subroad']).agg(tup_dic)
        # apply the complete index
        subset_aggs = subset_aggs.reindex(brightness.index)
        # insert the new aggregations into the brightness df
        col_id = list(brightness.columns).index((l1, 'right_avg'))
        for c in list(reversed(list(subset_aggs.columns))):
            brightness.insert((col_id + 1),(l1, f'{c[1]}_upg'), subset_aggs[c])

        # get the id of the share
        cols = list(brightness.columns)
        col_id = cols.index((l1, 'share'))
        dummy_aggs = ['median', 'mean']
        dummy_vars = dummy_row_distance(wide, (l1, f'upg_{thresholds[0]}'), dummy_aggs)
        for a in dummy_aggs:
            buffer = dummy_aggs.index(a)
            brightness.insert((col_id + buffer),(l1, f'dist_{a}'), dummy_vars[('dist', a)])

    brightness = brightness.sort_values(by=('B4_min', 'road'), ascending=True)  # shows the percentage of points that meet condition
    brightness = brightness.sort_index()


    cols_before_dummies = list(brightness.columns)

    # determine if the road is upgraded


    brightness[('upgrade', "bright_B4_diff")] = ( (brightness[('B4_min', 'road')] < 0 ) &
                                                  (brightness[('B4_min', 'left_avg')] > 0.75 * brightness[('B4_min', 'road')]) &
                                                  (brightness[('B4_min', 'right_avg')] > 0.75 * brightness[('B4_min', 'road')]) #&
                                                  #(brightness[('B4_min', 'left_avg')] > brightness[('B4_min', 'road')] + 50) &
                                                  #(brightness[('B4_min', 'right_avg')] > brightness[('B4_min', 'road')] + 50)
                                                  ).astype(int)


    b4_diff_array = brightness[('B4_diff_factor', 'road')].values
    brightness[('upgrade', "bright_B4")] = ( (brightness[('B4_min', 'road')] + b4_diff_array < 0 ) &
                                             (brightness[('B4_min', 'left_avg')] + b4_diff_array > 0.75 * (brightness[('B4_min', 'road')]+ b4_diff_array)) &
                                             (brightness[('B4_min', 'right_avg')] + b4_diff_array > 0.75 * (brightness[('B4_min', 'road')]+ b4_diff_array)) #&
                                             #(brightness[('B4_min', 'left_avg')] - b4_diff_array > brightness[('B4_min', 'road')] - b4_diff_array + 40) &
                                             #(brightness[('B4_min', 'right_avg')] - b4_diff_array > brightness[('B4_min', 'road')] - b4_diff_array + 40)
                                             ).astype(int)


    cols = [('upgrade', "bright_B4"), ('upgrade', "bright_B4_diff")] + cols_before_dummies
    brightness = brightness.loc[:, cols]

    # add the values to the export sheet

    brightness_results = brightness.reset_index().rename(columns={"road": "road_id", "subroad": "subroad_id"}).set_index(['road_id', 'subroad_id'])
    #brightness_results

    # x = df_r.set_index(['road_id', 'subroad_id'])
    #
    # x['upgraded'] = brightness_results[('upgrade', 'bright_B4_diff')]
    # x['b_share_B4'] = brightness_results[('B4_min', 'road_id')]
    # x['b_share_B4_left'] = brightness_results[('B4_min', 'left_avg')]
    # x['b_share_B4_right'] = brightness_results[('B4_min', 'right_avg')]
    #
    # x = x.reset_index()


    # export the brightness results (the analysis)
    analysis_filename = r.replace(prefix, 'analysis')
    writer = pd.ExcelWriter(f"{dir_roads}/{analysis_filename}", engine='xlsxwriter', options={'strings_to_urls': False})
    brightness_results.reset_index().to_excel(writer)
    writer.close()

    print(f"HURRA! We finished spreadsheet {r}")


    #writer = pd.ExcelWriter("detailed_point_medians.xlsx", engine='xlsxwriter', options={'strings_to_urls': False})
    #brightness_results.reset_index().to_excel(writer)
    #riter.close()




