# import Image module
from PIL import Image
import os, sys

# import_dir = '../Exports/Images/wb_roads_2020-05-01_2020-07-31_2021-05-01_2021-07-31/png'
# export_dir = '../Exports/Images/wb_roads_2020-05-01_2020-07-31_2021-05-01_2021-07-31/png_web'

import_dir = 'D:/road_upgrades/Exports/Images/wb_roads_timeline_2016-05-01_2021-07-31/png'
export_dir = 'D:/road_upgrades/Exports/Images/wb_roads_timeline_2016-05-01_2021-07-31/png_web'

if not os.path.isdir(export_dir):
    os.mkdir(export_dir)

images = os.listdir(import_dir)
img_count = len(images)
count = 1
for i in images:
    fp = f'{import_dir}/{i}'[:-4]
    img = Image.open(f"{fp}.png")

    #print(f"Size before crop is: {img.size}")

    # crop the image
    #img_cropped = img.crop((52, 20, 100, 845))
    img_cropped = img.crop((52, 25, 1852, 845))

    #print(f"Size after  crop is: {img_cropped.size}")

    # I downsize the image with an ANTIALIAS filter (gives the highest quality)
    img_web = img_cropped.resize((160, 73), Image.ANTIALIAS)  #220, 100

    export_fp = fp = f'{export_dir}/{i}'[:-4]
    img_web.save(f"{export_fp}.png", optimize=True, quality=95)

    print(f"exported img {count} / {img_count}")
    count = count + 1
