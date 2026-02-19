import numpy as np
import matplotlib.pyplot as plt
import skimage.measure
import tifffile as tiff
import pandas as pd
import cv2
import ast
import sys, os
from PIL import Image
from MaskUtils import MaskUtils
import time

t = time.time()

########################
##### FOLDER PATHS #####
########################

# folder paths
vertices_path = r"E:\Users\bchiang\IGPC Raw Histology\Vertices"
tif_path = r"E:\Users\bchiang\IGPC Raw Histology"

# list of raw paths for the .csv and .tif files (v = regular vertices, p = prostate vertices)
v_paths = MaskUtils.getPaths("vertices", vertices_path)[0]
p_paths = MaskUtils.getPaths("vertices", vertices_path)[1]
tif_files = MaskUtils.getPaths("tif", tif_path)[2]

print(v_paths, "\n", p_paths, "\n", tif_files)
# print(len(v_paths), len(p_paths), len(tif_files))

print("folder paths", time.time()-t)

#####################
##### MAIN LOOP #####
#####################

# loop through every img file
for f in range(len(tif_files)):

    prostate_df = pd.read_csv(p_paths[f])
    contour_df = pd.read_csv(v_paths[f])

    starter_coords = ast.literal_eval(prostate_df.loc[0, 'Vertices'])[0]

    # CREATING INITIAL VALUES
    max_xvalue = int(float(starter_coords['X']))
    max_yvalue = int(float(starter_coords['Y']))

    # USE THE PROSTATE CONTOUR TO MAKE THE MASK DIMENSIONS
    prostate_coords = []

    #
    for row in range(len(prostate_df)):
        vertices_list = MaskUtils.getVerticesList(prostate_df, row)

        for d in vertices_list:
            x = float(d['X'])
            y = float(d['Y'])
            prostate_coords.append([x, y])

            if x > max_xvalue:
                max_xvalue = int(round(x))
            if y > max_yvalue:
                max_yvalue = int(round(y))

    # add to the max x and y values to give the pixel dimensions for each mask
    padding = 4000

    # x and y have to be flipped !!! (columns (y) then rows (x))
    mask = np.zeros((max_yvalue+padding,max_xvalue+padding), dtype = np.uint8)      # og mask
    mask2 = np.ones((max_yvalue+padding,max_xvalue+padding), dtype = np.uint8)   # inverted mask
    p_mask = np.zeros((max_yvalue+padding,max_xvalue+padding), dtype = np.uint8)    # prostate mask

########################
##### contour time #####
########################

    # groupby separates the df by annotation name (ex. G3 and Atrophy for A16)
    grouped = contour_df.groupby('Annotation Name')

    # array of annotation names that aren't cancer (therefore should not show up on the mask)
    not_cancer = ["Atrophy", "PIN", "EPE", "Margin", "Inflammation", "Perinural Invasion", "SV Invasion"]

    # loops as many times as there are types of annotations (2 for A16, 6 for A17)
    for annotation_name, grouped_df in grouped:

        annotation_contours = []

        # loop the number of rows of the df of that annotation name (ex. every row in G3)
        for k in range(len(grouped_df)):

            # add all the vertices from each column in the csv together into one array
            vertices_list = []
            for i in range(6):
                value = ast.literal_eval(grouped_df.iloc[k, i+7])
                vertices_list = vertices_list + value

            # extract the points and turn them into floats
            region_points = []
            for p in vertices_list:
                x = float(p['X'])
                y = float(p['Y'])
                region_points.append([x, y])    # all vertices from one region

            annotation_contours.append(region_points)   # array of this structure: [[points],[points2],[points3], etc.]

        merged_contours = MaskUtils.mergeContours(annotation_contours)

        # draw a polygon for each new merged region
        for r in merged_contours:
            contour = np.array(r, dtype=np.int32).reshape((-1, 1, 2))

            if annotation_name in not_cancer:
                colour_value = 0.0
                cv2.fillPoly(mask2,[contour], colour_value)
            else:
                colour_value = 255.0
                cv2.fillPoly(mask, [contour], colour_value)

    # making the prostate mask (p_mask)
    # prostate_coords = MaskUtils.mergeContours(prostate_coords)
    contour = np.array(prostate_coords, dtype=np.int32).reshape((-1, 1, 2))
    cv2.fillPoly(p_mask, [contour], 255.0)

    print("mask1, mask2, and prostate mask", time.time() - t)

##############################
##### cancer detection!! #####
##############################

    # mask = cancer, mask2 = inverted mask
    mask3 = mask * mask2
    del mask, mask2

    # downsample the image (each pixel value of the new image is the mean of a 512x512 tile of the og image)
    reduced = skimage.measure.block_reduce(mask3,(512,512), np.mean)
    p_reduced = skimage.measure.block_reduce(p_mask,(512,512), np.mean)

    del mask3, p_mask

    # only include tiles that are 100% cancer and tiles that contain 230/255 % prostate
    uint8_mask = (reduced == 255).astype(np.uint8) * 255
    reduced_pmask = (p_reduced > 230).astype(np.uint8) * 255

    cancer_coords = np.argwhere(uint8_mask == 255)
    non_cancer_coords = np.argwhere(uint8_mask < 255)
    p_mask_coords = np.argwhere(reduced_pmask == 255)

    # FORMAT IS [Y,X], [Y,X], ETC.
    clean_cancer_coords = MaskUtils.cleanCoords(cancer_coords)
    clean_noncancer_coords = MaskUtils.cleanCoords(non_cancer_coords)
    clean_pmask_coords = MaskUtils.cleanCoords(p_mask_coords)

    print("Cancer length:", len(clean_cancer_coords), "NON-cancer length", len(clean_noncancer_coords))
    print("new mask + cancer and non cancer coords", time.time() - t)

############################
##### saving the mask! #####
############################

    # img = Image.fromarray(mask)
    # img2 = Image.fromarray(mask2)
    # img3 =  Image.fromarray(mask3)

    # path = v_paths[f]
    # patient = path.split("\\")[5]                       # gives: IGPC####
    # file_name = path.split("\\")[-1].split(".")[0]      # gives: IGPC-2_051 A15-1 Prostate

    # try:
    #     #img.save(fr'E:\Users\bchiang\IGPC Raw Histology\Masks\{patient}\{file_name} test.png')
    #     #img2.save(fr'E:\Users\bchiang\IGPC Raw Histology\Masks\{patient}\{file_name} test2.png')
    #     img3.save(fr'E:\Users\bchiang\IGPC Raw Histology\Masks\{patient}\{file_name} test3.png')
    #     print("saved")
    # except OSError:
    #     "the image is prob still open"

############################
##### showing the tile #####
############################

    # print(tif_files[f])
    # img = tiff.imread(tif_files[f])
    #
    # patient_no = tif_files[f].split("\\")[4]  # gives: IGPC 1010
    # file_name = tif_files[f].split("\\")[5].split(".")[0]  # gives: IGPC-1010 A16, IGPC-2_014 A16-1
    #
    # print("cancer tiles")
    # MaskUtils.saveImageTiles(clean_cancer_coords, clean_pmask_coords, img, patient_no, file_name, 1)
    #
    # print("non-cancer tiles")
    # MaskUtils.saveImageTiles(clean_noncancer_coords, clean_pmask_coords, img, patient_no, file_name, 0)

print("final", time.time() - t)