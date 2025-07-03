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
import Utils
from PIL import Image
import sys

t = time.time()

df = pd.read_csv(r'E:\Users\bchiang\IGPC Raw Histology\Vertices\IGPC 1010\IGPC1010 A16 Prostate.csv')
df2 = pd.read_csv(r'E:\Users\bchiang\IGPC Raw Histology\Vertices\IGPC 1010\IGPC1010 A16.csv')

starter_coords = ast.literal_eval(df.loc[0,'Vertices'])[0]

max_xvalue = int(float(starter_coords['X']))
max_yvalue = int(float(starter_coords['Y']))

# get the prostate contour + make the mask border
prostate_points = []

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

        if x > max_xvalue:
            max_xvalue = x
        if y > max_yvalue:
            max_yvalue = y

# add to the max x and y values to create the proper border
padding = 4000

# x and y have to be flipped !!! idk why
mask = np.zeros((max_yvalue+padding,max_xvalue+padding), dtype = np.uint8)

# PROSTATE MASK + DIMENSIONS TIME
print("mask dimensions", time.time() - t)



######################################################
##### contour time don't touch anything above this!!!!
######################################################

# maybe use something like this later if you need to distinguish the cancer by grade
# annotation_dict = {
#     "G3": 'brown', "G4": 'grey', "G5": 'black', "Atrophy": 'blue', "Margin": 'yellow', "EPE": 'light blue', "PIN": 'light green',
#     "G3+4": 'green', "G4+3": 'purple', "G4+5": 'red', "G5+4": 'cyan', "G3+5": 'light grey', "G5+3": 'teal' }


# groupby separates the df by annotation name (ex. G3 and Atrophy for A16)
grouped = df2.groupby('Annotation Name')

## MAIN LOOP
# loops as many times as there are types of annotations (2 for A16, 6 for A17)
for annotation_name, grouped_df in grouped:

    # skip anything that isn't actually cancer
    if annotation_name == "Atrophy" or annotation_name == "PIN" or annotation_name == "EPE" or annotation_name == "Margin" or annotation_name == "Inflammation":
        continue

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

print("all contours! (grabbing + merging)", time.time()-t)

#########################
##### cancer detection!!
#########################

#point = [6900,33000]
    #[19072,43678]   # this is a point inside G3 contour 2
    #[17750.0,44300.0] this is a point inside G3 contour 1

new_mask = skimage.measure.block_reduce(mask,(512,512), np.mean)
uint8_mask = (new_mask - new_mask.min()) / (new_mask.max() - new_mask.min())
uint8_mask = (100*uint8_mask).astype(np.uint8)

# for row in uint8_mask:
#     count3 = 0
#     for point in row:
#         for o in merged_contours:
#             val = cv2.pointPolygonTest(np.array(o, dtype='float32'), point, measureDist = False)
#             if val == 1.0:
#                 check.append(count3)
#         count3 += 1

coord_list = np.argwhere(uint8_mask == 100)

clean_coords = []
for i in range(len(coord_list)):
    x = tuple(coord_list)[i][0]
    y = tuple(coord_list)[i][1]
    coords = [x, y]
    clean_coords.append(coords)

#print(tuple(coord_list)[0][0])

#########################
##### showing the image!
#########################

# img = Image.fromarray(uint8_mask)
# img.save(r'E:\Users\bchiang\IGPC Raw Histology\Masks\IGPC 1010\IGPC1010 A16 test.png')

del mask
del new_mask
del uint8_mask

img = tiff.imread(r'E:\Users\bchiang\IGPC Raw Histology\IGPC 1010\IGPC-1010 A16.tif')
print(len(clean_coords))

try:
    tiff_x = clean_coords[4][0]*512
    tiff_y = clean_coords[4][1]*512
    print(tiff_x, tiff_y)
except IndexError:
    print("whoops")

tile = img[tiff_y:tiff_y+512, tiff_x:tiff_x+512]

plt.figure(figsize = (512 / 100, 512 / 100), dpi = 100)
plt.gca().set_frame_on(False)

plt.imshow(tile)
plt.show()

print("final", time.time()-t)


# plt.imshow(mask, cmap='gray')
#
# print("imshow", time.time()-t)
#
# plt.title('A19 Test')
# plt.axis('off')
# #plt.gca().set_frame_on(False)
# plt.show()
#
# print("final", time.time()-t)
