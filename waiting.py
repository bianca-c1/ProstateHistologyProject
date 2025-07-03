import os
import os.path
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import openslide
from bs4 import BeautifulSoup
import re


os.add_dll_directory(r'C:\Users\bchiang\miniconda3\Lib\site-packages\openslide-bin-4.0.0.8-windows-x64\bin')

# !!! trying to grab the contours of the image and put them in an array

xml_file = open(r"E:\Users\bchiang\IGPC Raw Histology\IGPC 1010\IGPC-1010 A16.xml")

with open(r"E:\Users\bchiang\IGPC Raw Histology\IGPC 1010\IGPC-1010 A17.xml", 'r') as f:
    data = f.read()

bs_data = BeautifulSoup(data, "xml")
b = bs_data.find_all("Annotation") #, string=re.compile('G3'))
print(b)