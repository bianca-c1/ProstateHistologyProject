import numpy as np
import matplotlib.pyplot as plt
import skimage.measure
import tifffile as tiff
import pandas as pd
import cv2
import ast
import time
from scipy.spatial import distance
import math
from PIL import Image
import sys
import MaskUtils

######################
##### Setting Up! #####
######################

prostate_df = pd.read_csv(r'E:\Users\bchiang\IGPC Raw Histology\Vertices\IGPC 2014\IGPC-2_014 A19-2 DEEPER Prostate.csv')
contour_df = pd.read_csv(r'E:\Users\bchiang\IGPC Raw Histology\Vertices\IGPC 2014\IGPC-2_014 A19-2 DEEPER.csv')

starter_coords = ast.literal_eval(prostate_df.loc[0, 'Vertices'])[0]

max_xvalue = int(float(starter_coords['X']))
max_yvalue = int(float(starter_coords['Y']))

# get the prostate contour + make the mask border
prostate_points = []

for row in range(len(prostate_df)):

    vertices_list = []
    for i in range(6):
        col_name = 'Vertices' if i == 0 else f'Vertices{i+1}'
        value = ast.literal_eval(prostate_df.loc[row, col_name])
        vertices_list = vertices_list + value

    for d in vertices_list:
        x = int(round(float(d['X'])))
        y = int(round(float(d['Y'])))
        prostate_points.append([x, y])

        if x > max_xvalue:
            max_xvalue = x
        if y > max_yvalue:
            max_yvalue = y

# add to the max x and y values to create the proper border
padding = 4000

# x and y have to be flipped !!! idk why
mask = np.zeros((max_yvalue+padding,max_xvalue+padding), dtype = np.uint8)



######################################################
##### contour time don't touch anything above this!!!!
######################################################

# groupby separates the df by annotation name (ex. G3 and Atrophy for A16)
grouped = contour_df.groupby('Annotation Name')

## MAIN LOOP
# loops as many times as there are types of annotations (2 for A16, 6 for A17)
for annotation_name, grouped_df in grouped:

    # skip anything that isn't actually cancer
    if annotation_name == "Atrophy" or annotation_name == "PIN" or annotation_name == "EPE" or annotation_name == "Margin" or annotation_name == "Inflammation":
        continue        # need to comment this out later when you fix the code

    else:
        # clears for every type of annotation
        all_contours = []

        # loop the number of rows of the df of that annotation name (ex. every row in G3, G4, Atrophy, etc.)
        for k in range(len(grouped_df)):

            # add all the vertices from each column in the csv together into one array
            vertices_list = []
            for i in range(6):
                value = ast.literal_eval(grouped_df.iloc[k, i+7])
                vertices_list = vertices_list + value

            # extract the points and turn them into floats
            points = []
            for p in vertices_list:
                x = float(p['X'])
                y = float(p['Y'])
                points.append([x, y])   # points = vertices from one region

            all_contours.append(points)  # array of this structure: [[points],[points2],[points3], etc.]

        ## merging contours
        first_last = []
        for region in all_contours:
            first_last.append(region[0])
            first_last.append(region[-1])
            # even is first and odd is last (0 based indexing instead of 1 in MATLAB)

        first_last = np.array(first_last)
        dist_matrix = distance.cdist(first_last,first_last, 'euclidean')
        dist_matrix[dist_matrix<=0] = math.inf

        closest = np.argmin(dist_matrix, axis=1)  # closest[i] = index of closest endpoint
        used = np.zeros(len(closest), dtype=bool)

        merged_contours = []
        for i in range(0, len(closest), 2):

            if used[i]:
                continue
            merged = []
            next = i

            while not used[next]:
                contour_idx = next // 2     # floor divide (divide then round down)
                contour = all_contours[contour_idx]

                if next % 2 == 1:
                    contour = contour[::-1]
                merged.extend(contour)
                used[next] = True
                used[next ^ 1] = True
                next = closest[next ^ 1]

            if merged:
                merged_contours.append(merged)

        # draw a polygon for each new merged region
        for r in merged_contours:
            contour = np.array(r, dtype=np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(mask, [contour], color=(255, 255, 255))


#########################
##### cancer detection!! DON'T TOUCH ANYTHING ABOVE THIS !
#########################

# downsample the image (each pixel value of the new image is the mean of a 512x512 tile of the og image)
# reduced = skimage.measure.block_reduce(mask,(512,512), np.mean)
# uint8_mask = (reduced == 255).astype(np.uint8) * 255
#
#
# coord_list = np.argwhere(uint8_mask == 255)
#
# clean_coords = []
# for i in range(len(coord_list)):
#     x = tuple(coord_list)[i][0]
#     y = tuple(coord_list)[i][1]
#     coords = [x, y]
#     clean_coords.append(coords)

#########################
##### showing the image!
#########################

img = Image.fromarray(mask)
img.save(r'E:\Users\bchiang\IGPC Raw Histology\Masks\IGPC 2014\IGPC-2_014 A19-2 DEEPER.png')

# to save memory
del mask
#del uint8_mask

# img = tiff.imread(r'E:\Users\bchiang\IGPC Raw Histology\IGPC 1010\IGPC-1010 A17.tif')
#
# try:
#     tiff_y = clean_coords[0][0]*512
#     tiff_x = clean_coords[0][1]*512
#     print(tiff_x, tiff_y)
# except IndexError:
#     print("whoops")
#
# tile = img[tiff_y:tiff_y+512, tiff_x:tiff_x+512]

# use the below stuff for showing the tile you open
#
# plt.figure(figsize = (512 / 100, 512 / 100), dpi = 100)
# plt.gca().set_frame_on(False)
#
# plt.imshow(tile)
# plt.show()