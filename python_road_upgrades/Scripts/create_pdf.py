import os
import re

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer)
from reportlab.lib.styles import ParagraphStyle
import pandas as pd


print(f"A4 Dimensions {A4}")
w, h = A4

img_dir = f"../Exports/Images/wb_roads_2020-05-01_2020-07-31_2021-05-01_2021-07-31/png_web"
images = os.listdir(img_dir)

# sort the filenames in ascending order
road_ids = [int(re.search(r"^(\d+)_", x).group(1)) for x in images]
subroad_ids = [int(re.search(r"^\d+_(\d+)", x).group(1)) for x in images]
data = [{'fn': images[i], 'road_id': road_ids[i], 'subroad_id': subroad_ids[i]} for i in range(0, len(images))]
data = sorted(data, key = lambda x: (x['road_id'], x['subroad_id']))
images = [x['fn'] for x in data]


img_count = int(len(images)/3)
print(f"image count is", img_count)


c = canvas.Canvas("../Exports/Roads/appendix_road_composites.pdf", pagesize=A4)

status_df = pd.read_excel("../Imports/visual_classification_2020_2021_05_07.xlsx").fillna(0)

h_pagebreaks = 0
page_number = 1
row_count = 0

for i in range(0, img_count):
    row_count = row_count + 1

    img1 = f"{img_dir}/{images[3*i+0]}"     # diff image
    img2 = f"{img_dir}/{images[3*i+1]}"     # t1 image
    img3 = f"{img_dir}/{images[3*i+2]}"     # t2 image

    m = re.search(r"^(\d+)_(\d+)", images[3*i+0])
    road_id = m.group(1)
    subroad_id = m.group(2)

    if page_number == 1:
        # TITLE
        text = c.beginText(100, h - 50)
        text.setFont("Courier-Bold", 18)
        text.textLine(f"Visual Classification of Training Data ")
        c.drawText(text)
        # Names
        text = c.beginText(100, h - 75)
        text.setFont("Courier", 10)
        text.textLine(f"By: Jeffrey Clark and Tamina Matti")
        c.drawText(text)
        # Explaining text
        text = c.beginText(40, h - 100)
        text.setFont("Courier", 8)
        text.textLine(f"The following documents presents snapshots of each subroad in our training dataset. The images to the left")
        text.textLine(f"are composites from 2020-05-01 to 2020-07-31, the middle images are composites from 2021-05-01 to 2021-07-31.")
        text.textLine(f"The right-most images are differenced composites, where bright elements indicate elements present in the ")
        text.textLine(f"latter (middle) composites, but not in the former. The subroad of interest always runs through the center ")
        text.textLine(f"of each image.")
        c.drawText(text)

        buffer = (row_count)*100 + 40
    else:
        buffer = (row_count)*100 - 65

    #c.drawString(40, h-70-buffer, f"Road {road_id}, subroad {subroad_id}")
    text = c.beginText(40, h-20-buffer)
    text.setFont("Courier-Bold", 10)
    upg_status = status_df.loc[(status_df['road_id'] == int(road_id)) & (status_df['subroad_id'] == int(subroad_id)), 'upgrade'].values
    if upg_status == 0:
        text.textLine(f"Road {road_id}, Subroad {subroad_id}    NOT UPGRADED")
    else:
        text.textLine(f"Road {road_id}, Subroad {subroad_id}    UPGRADED")
    c.drawText(text)

    c.drawImage(img2, 40, h - 100 - buffer)
    c.drawImage(img3, 220, h - 100 - buffer)
    c.drawImage(img1, 400, h - 100 - buffer)

    if buffer >= h - 300:
        # add page number
        text = c.beginText(w/2-10, 30)
        text.setFont("Courier", 8)
        text.textLine(f"{page_number}")
        c.drawText(text)
        # new page
        c.showPage()
        page_number = page_number + 1
        row_count = 0

c.save()