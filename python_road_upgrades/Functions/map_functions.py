import geemap
import ee
import os
from html2image import Html2Image
import Functions.general as f


def export_maps(dir_path, road_geom, time1, time2, name_base, zoom=16, overwrite=False,
                timeline_times=None):

    # create the directory for images
    # if timeline_times is None:
    #     dir_name = f"{road_set_name}_{time1[0]}_{time1[1]}_{time2[0]}_{time2[1]}"
    # else:
    #     times = timeline_times
    #     dir_name = f"{road_set_name}_{times[0][0]}_{times[-1][-1]}"

    #dir_path = f"Exports/Images/{dir_name}"

    paths = [dir_path, f"{dir_path}/html", f"{dir_path}/html/multi_layered",
             f"{dir_path}/html/single_layered", f"{dir_path}/png"]
    for p in paths:
        if not os.path.isdir(p):
            os.mkdir(p)

    # GENERAL CHECK FOR SKIPPING (IF ALL FILES ARE IN PLACE)
    # if not overwrite:
    #     skip = True
    #     #for suffix in ["_t1", "_t2", "_diff", "_diff_norm"]:
    #     for suffix in ["_t1", "_t2", "_diff"]:
    #         if not os.path.isfile(f"{dir_path}/png/f'{name_base}_{suffix}"):
    #             skip = False
    #     if skip:
    #         print("SKIPPING ROAD")
    #         return True

    # compute the midpoint
    midpoint = road_geom.centroid().coordinates().getInfo()
    #print(f"midpoint for road {n} subroad {i} is {midpoint}")

    # make potential adjustments for zoom
    #
    #

    # CREATE MAP OBJECTS
    Map_base = geemap.Map(center=(midpoint[1], midpoint[0]), zoom=16)
    Map_all = geemap.Map(center=(midpoint[1], midpoint[0]), zoom=16)
    Map_t1 = geemap.Map(center=(midpoint[1], midpoint[0]), zoom=16)
    Map_t2 = geemap.Map(center=(midpoint[1], midpoint[0]), zoom=16)
    Map_diff = geemap.Map(center=(midpoint[1], midpoint[0]), zoom=16)
    Map_diff_norm =geemap.Map(center=(midpoint[1], midpoint[0]), zoom=16)


    # FETCH IMAGE COMPOSITES AND DIFF
    t1 = f.fetchS2Composite(time1[0], time1[1], road_geom)
    t2 = f.fetchS2Composite(time2[0], time2[1], road_geom)
    diff = t2.subtract(t1)

    # SPECIFY VISUALIZATIONS
    rgbband_1500 = {"opacity": 1, "bands": ["B4", "B3", "B2"], "min": 200, "max": 1500, "gamma": 1}
    diff_B4 = {"opacity": 1, "bands": ["B4"], "min": 0, "max": 900, "gamma": 1}

    # for normalized diff adjustment
    #buffer_geom = road_geom.buffer(2000)
    #median_t1 = ee.Number(t1.select("B4").reduceRegion(ee.Reducer.median(), buffer_geom, 10).get(ee.String("B4")))
    #median_t2 = ee.Number(t2.select("B4").reduceRegion(ee.Reducer.median(), buffer_geom, 10).get(ee.String("B4")))
    #diff_factor = median_t2.subtract(median_t1).getInfo()
    #diff_factor_med = ee.Number(diff.select("B4").reduceRegion(ee.Reducer.median(), buffer_geom, 10).get(ee.String("B4"))).getInfo()
    #print("DIFF FACTOR MED IS", diff_factor_med)
    #print("REAL DIFF FACTOR IS", diff_factor)

    #diff_B4_norm = {"opacity": 1, "bands": ["B4"], "min": int(diff_factor), "max": 900, "gamma": 1}


    # ADD RELEVANT LAYERS TO EACH MAP
    Map_all.addLayer(t1, rgbband_1500, "t1")
    Map_t1.addLayer(t1, rgbband_1500, "t1")

    Map_all.addLayer(t2, rgbband_1500, "t2")
    Map_t2.addLayer(t2, rgbband_1500, "t2")

    Map_all.addLayer(diff, diff_B4, "diff")
    Map_diff.addLayer(diff, diff_B4, "diff")

    #Map_all.addLayer(diff, diff_B4_norm, "diff_norm")
    #Map_diff.addLayer(diff, diff_B4_norm, "diff_norm")


    # CREATE AN OBJECT-SUFFIX LIST
    maps = [
        {'map': Map_t1, 'suffix': "t1"},
        {'map': Map_t2, 'suffix': "t2"},
        {'map': Map_diff, 'suffix': "diff"}#,
        #{'map': Map_diff_norm, 'suffix': "diff_norm"}
    ]

    if timeline_times is not None:
        maps = [
            {'map': Map_t1, 'suffix': f"{time1[1][0:4]}_{time1[1][5:7]}"},
            {'map': Map_t2, 'suffix': f"{time2[1][0:4]}_{time2[1][5:7]}"},
        ]


    # GENERATE THE HTML FILE FOR MAP_ALL
    download_dir = f"{dir_path}/html/multi_layered"
    html_file = os.path.join(download_dir, f'{name_base}_multi.html')
    if os.path.isfile(html_file) and not overwrite:
        print("skipping html")
    else:
        Map_all.to_html(outfile=html_file, title=f'Road {name_base}', width='100%', height='880px')

    # GENERATE THE HTML FILE FOR SINGLE-LAYERED MAPS
    download_dir = f"{dir_path}/html/single_layered"
    for m in maps:
        html_file = os.path.join(download_dir, f'{name_base}_{m["suffix"]}.html')
        if os.path.isfile(html_file) and not overwrite:
            print("skipping single layer")
            continue
        else:
            m['map'].to_html(outfile=html_file, title=f'Road {name_base}', width='100%', height='880px')


    # EXPORT THE SINGLE-LAYERED HTML FILES AS IMAGES
    be = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    hti = Html2Image(browser_executable=be)

    hti.output_path = f"{dir_path}/png"
    hti.browser.flags = ['--virtual-time-budget=10000']

    for m in maps:
        html_file = os.path.join(download_dir, f'{name_base}_{m["suffix"]}.html')
        png_file = f"{hti.output_path}/{name_base}_{m['suffix']}.png"
        if os.path.isfile(png_file) and not overwrite:
            print("skipping multilayer")
            continue
        else:
            hti.screenshot(html_file=html_file, save_as=f'{name_base}_{m["suffix"]}.png')
