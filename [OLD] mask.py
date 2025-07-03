import numpy as np
import matplotlib.pyplot as plt
import openslide
import tifffile as tiff
import pandas as pd
import cv2
import ast
import time

df = pd.read_csv(r'E:\Users\bchiang\IGPC Raw Histology\Vertices\IGPC 1010\IGPC1010 A17 Prostate.csv')
df2 = pd.read_csv(r'E:\Users\bchiang\IGPC Raw Histology\Vertices\IGPC 1010\IGPC1010 A17.csv')

t = time.time()
#mask = np.zeros((60000,82600), dtype = np.uint8)       <- for IGPC 1010 A16

starter_coords = ast.literal_eval(df.loc[0, 'Vertices'])[0]

min_xvalue = int(float(starter_coords['X']))
max_xvalue = int(float(starter_coords['X']))
min_yvalue = int(float(starter_coords['Y']))
max_yvalue = int(float(starter_coords['Y']))

prostate_points = []

# get all prostate contours + make the mask border
for row in range(len(df)):

    vertices_list = []
    for i in range(6):
        col_name = 'Vertices' if i == 0 else f'Vertices{i+1}'
        value = ast.literal_eval(df.loc[row, col_name])
        vertices_list = vertices_list + value

    for d in vertices_list:
        x = int(round(float(d['X'])))
        y = int(round(float(d['Y'])))
        prostate_points.append([x, y])

        if x < min_xvalue:      # might be able to remove the min values
            min_xvalue = x
        if x > max_xvalue:
            max_xvalue = x

        if y < min_yvalue:
            min_yvalue = y
        if y > max_yvalue:
            max_yvalue = y

padding = 4000
mask = np.zeros((max_yvalue+padding,max_xvalue+padding), dtype = np.uint8)

#contour_name = df2.loc[0,'Annotation Name']

# actual histology contours
for row in range(len(df2)):

    vertices_list = []
    for i in range(6):
        col_name = 'Vertices' if i == 0 else f'Vertices{i + 1}'
        value = ast.literal_eval(df2.loc[row, col_name])
        vertices_list = vertices_list + value

    points = []
    for d in vertices_list:
        x = int(round(float(d['X'])))
        y = int(round(float(d['Y'])))
        points.append([x, y])

    contour = np.array(points, dtype=np.int32).reshape((-1, 1, 2))  # (number of points, ?, two coords (X,Y))
    print(contour)
    cv2.fillPoly(mask, [contour], color=(255, 0, 0))

# row = 0
# points = []
#
# # one annotation name (ex. G3 -> G4)
# while df2.loc[row,'Annotation Name'] == contour_name:
#
#     vertices_list = []
#     for i in range(6):
#         col_name = 'Vertices' if i == 0 else f'Vertices{i+1}'
#         value = ast.literal_eval(df2.loc[row, col_name])
#         vertices_list = vertices_list + value
#
#     for d in vertices_list:
#         x = int(float(d['X']))
#         y = int(float(d['Y']))
#         points.append([x, y])
#
#     row += 1
    #contour_name = df2.loc[row, 'Annotation Name']


# print("all contours:", time.time()-t)#, "and min and max:", min_xvalue, ",", max_xvalue, min_yvalue, ",", max_yvalue)
#
# #kernel = np.ones((5, 5), np.uint8)
# # img_dilation = cv2.dilate(mask, kernel, iterations=1)
# # img_erosion = cv2.erode(img_dilation, kernel, iterations=1)
#
# plt.imshow(mask, cmap='gray')
#
# print("imshow", time.time()-t)
# plt.title('Dilate + Constrict Test!')
# plt.axis('off')
# #plt.gca().set_frame_on(False)
# plt.show()

print("final", time.time()-t)
