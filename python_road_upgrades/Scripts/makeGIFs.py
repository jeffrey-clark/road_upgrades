# import Image module
import re

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os, sys

# import_dir = '../Exports/Images/wb_roads_2020-05-01_2020-07-31_2021-05-01_2021-07-31/png'
# export_dir = '../Exports/Images/wb_roads_2020-05-01_2020-07-31_2021-05-01_2021-07-31/png_web'

import_dir = 'D:/road_upgrades/Exports/Images/wb_roads_timeline_2016-05-01_2021-07-31/png'
export_dir = 'D:/road_upgrades/Exports/Images/wb_roads_timeline_2016-05-01_2021-07-31/gifs'
specific_road_subroad_ids = []
overwrite = True
#specific_road_subroad_ids = [(30, 0)]


if not os.path.isdir(export_dir):
    os.mkdir(export_dir)

images_alphabetic_order = os.listdir(import_dir)

image_dics = []
for f in images_alphabetic_order:
    m = re.search(r"^(\d+)_(\d+)_(\d+)_(\d+)", f)
    road_id = int(m.group(1))
    subroad_id = int(m.group(2))
    year = int(m.group(3))
    month = int(m.group(4))
    insert = {'road_id': road_id, 'subroad_id': subroad_id, 'year': year, 'month': month, 'filename': f}
    image_dics.append(insert)

image_dics = sorted(image_dics, key=lambda k: (k['road_id'], k['subroad_id'], k['year'], k['month']))
images = [x['filename'] for x in image_dics]


image_collections = {}

for file in images:
    m = re.search(r"^(\d+)_(\d+)_", file)
    road_id = int(m.group(1))
    subroad_id = int(m.group(2))
    tup = (road_id, subroad_id)
    if tup not in list(image_collections.keys()):
        image_collections[tup] = [file]
    else:
        image_collections[tup].append(file)


for tup in list(image_collections.keys()):
    if isinstance(specific_road_subroad_ids, list):
        if len(specific_road_subroad_ids) > 0 and (tup not in specific_road_subroad_ids):
            continue

    gif_filename = f"{tup[0]}_{tup[1]}"
    if os.path.isfile(f'{export_dir}/{gif_filename}.gif') and overwrite == False:
        continue

    # Now import the images
    img_list = []
    for i in image_collections[tup]:
        m = re.search(r"^(\d+)_(\d+)_(\d+)_(\d+)", i)
        road_id = int(m.group(1))
        subroad_id = int(m.group(2))
        year = int(m.group(3))
        month = int(m.group(4))

        fp = f'{import_dir}/{i}'[:-4]
        img = Image.open(f"{fp}.png")
        img_cropped = img.crop((52, 25, 1852, 845))


        # add some text
        I1 = ImageDraw.Draw(img_cropped)

        # Custom font style and font size

        font_large = ImageFont.truetype('D:/road_upgrades/Fonts/BebasNeue-Regular.ttf', 70)
        font_small = ImageFont.truetype('D:/road_upgrades/Fonts/BebasNeue-Regular.ttf', 40)

        # Add Text to an image
        I1.text((20, 20), f"{year}", font=font_large, fill=(255, 255, 255))
        I1.text((20, 760), f"Road: {road_id}  Subroad: {subroad_id}", font=font_small, fill=(255, 255, 255))

        # Display edited image
        #img_cropped.show()
        # Save the edited image
        #img.save("car2.png")

        # I downsize the image with an ANTIALIAS filter (gives the highest quality)
        #img_web = img_cropped.resize((160, 73), Image.ANTIALIAS)  # 220, 100

        img_list.append(img_cropped)


    gif_filename = f"{tup[0]}_{tup[1]}"
    img_list[0].save(f'{export_dir}/{gif_filename}.gif',
                   save_all=True,
                   append_images=img_list[1:],
                   duration=1000,
                   loop=0)

    print(f"Published: {gif_filename}")