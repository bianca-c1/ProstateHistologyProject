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
import os

class MaskUtils:

    @staticmethod
    def getVerticesList(df, row):

        vertices_list = []
        for i in range(6):
            col_name = 'Vertices' if i == 0 else f'Vertices{i + 1}'
            value = ast.literal_eval(df.loc[row, col_name])
            vertices_list = vertices_list + value

        return vertices_list

    @staticmethod
    def getContourpoints(d, points):
        x = int(round(float(d['X'])))
        y = int(round(float(d['Y'])))
        points.append([x, y])

    @staticmethod
    def