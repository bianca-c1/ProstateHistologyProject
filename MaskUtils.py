import numpy as np
import skimage.measure
import tifffile as tiff
import pandas as pd
import cv2
import ast
from scipy.spatial import distance
import math
from PIL import Image
import sys
import os


class MaskUtils:

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def getPaths(type, path):

        """
        get the file paths for the .csv or .tif files given the parent path and vertices/tif
        """

        v_paths = []
        p_paths = []
        tif_paths = []

        if type == "xml":
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:
                    if file.endswith(".xml") in file:
                        file_path = os.path.join(dirpath, file)


        if type == "vertices":
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:
                    if file.endswith(".csv") in file:
                        file_path = os.path.join(dirpath, file)

                        if "Prostate" in file_path:
                            p_paths.append(file_path)
                        else:
                            v_paths.append(file_path)

        if type == "tif":
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:
                    file_path = os.path.join(dirpath, file)
                    if file_path.endswith(".tif") in file_path:
                        tif_paths.append(file_path)

        return v_paths, p_paths, tif_paths      #should maybe catch empty list being returned

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def getVerticesList(df, row):

        """
        extracts the vertices from the Excel file given [x] and returns them as a full list
        """

        vertices_list = []
        for i in range(6):
            col_name = 'Vertices' if i == 0 else f'Vertices{i + 1}'
            value = ast.literal_eval(df.loc[row, col_name])
            vertices_list = vertices_list + value

        return vertices_list

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def getContourpoints(vertices):

        """
        cleans the coordinates
        """

        points = []
        for coord in vertices:
            x = float(coord['X'])
            y = float(coord['Y'])
            points.append([x, y])

        return points


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def mergeContours(all_contours):

        """
        merge contours that are close together given a list of all contours
        """

        first_last = []
        for region in all_contours:
            first_last.append(region[0])
            first_last.append(region[-1])
            # even is first and odd is last (0 based indexing instead of 1 in MATLAB)

        first_last = np.array(first_last)
        dist_matrix = distance.cdist(first_last, first_last, 'euclidean')
        dist_matrix[dist_matrix <= 0] = math.inf

        closest = np.argmin(dist_matrix, axis=1)  # closest[i] = index of closest endpoint
        used = np.zeros(len(closest), dtype=bool)

        merged_contours = []
        for i in range(0, len(closest), 2):

            if used[i]:
                continue
            merged = []
            next = i

            while not used[next]:
                contour_idx = next // 2  # floor divide (divide then round down)
                contour = all_contours[contour_idx]

                if next % 2 == 1:
                    contour = contour[::-1]
                merged.extend(contour)
                used[next] = True
                used[next ^ 1] = True
                next = closest[next ^ 1]

            if merged:
                merged_contours.append(merged)
        return merged_contours


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def cleanCoords(coord_list):

        """
        clean a list of coordinates given the coordinate list (hardcoded I think)
        """

        clean_coords = []
        for i in range(len(coord_list)):
            x = tuple(coord_list)[i][0]
            y = tuple(coord_list)[i][1]
            coords = [x, y]
            clean_coords.append(coords)
        return clean_coords


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def saveImageTiles(coords, prostate_coords, img, patient_no, file_name, tile_type):
        """
        saves all tiles from the current img
        """

        for coord in range(len(coords)):
            tiff_x = coords[coord][1] * 512
            tiff_y = coords[coord][0] * 512

            if [tiff_y / 512, tiff_x / 512] in prostate_coords:
                tile = img[tiff_y:tiff_y + 512, tiff_x:tiff_x + 512]
                # print("tile:", "X", tiff_x, "Y", tiff_y)

                saved_tile = Image.fromarray(tile)

                if tile_type == 1:
                    saved_tile.save(fr'E:\Users\bchiang\IGPC Raw Histology\IGPC Tiles\{patient_no}\Cancer\{file_name}_X{tiff_x}_Y{tiff_y}_1.png')
                if tile_type == 0:
                    saved_tile.save(fr'E:\Users\bchiang\IGPC Raw Histology\IGPC Tiles\{patient_no}\Non-cancer\{file_name}_X{tiff_x}_Y{tiff_y}_0.png')

        # non cancer loop
        # for coord in range(len(clean_noncancer_coords)):
        #     tiff_x = clean_noncancer_coords[coord][1]*512
        #     tiff_y = clean_noncancer_coords[coord][0]*512
        #
        #     if [tiff_y/512,tiff_x/512] in clean_pmask_coords:
        #
        #         tile = img[tiff_y:tiff_y + 512, tiff_x:tiff_x + 512]
        #         #print("tile:", "X", tiff_x, "Y", tiff_y)
        #
        #         saved_tile = Image.fromarray(tile)          # CHANGE THIS FROM TEST TO {patient} WHEN UR DONE TESTING
        #         saved_tile.save(fr'E:\Users\bchiang\IGPC Raw Histology\IGPC Tiles\{patient_no} test\Non-cancer\{file_name}_X{tiff_x}_Y{tiff_y}_0.png')