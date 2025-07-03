import os
import numpy as np
import matplotlib.pyplot as plt
import openslide
import tifffile as tiff
import time

#os.add_dll_directory(r'C:\Users\bchiang\miniconda3\Lib\site-packages\openslide-bin-4.0.0.8-windows-x64\bin')

t = time.time()

# this one takes a while
img = tiff.imread(r'E:\Users\bchiang\IGPC Raw Histology\IGPC 1010\IGPC-1010 A16.tif')

print('imread', time.time() - t)

tile = img[44300:44300+800, 17750:17750+800]        # order is y,x NOT x,y
#tile = img[12000:12000+2048, 18000:18000+2048]

# 800 by 800 tile
# all in G3 (top left pixel is 44300, 17750)

plt.figure(figsize = (512 / 100, 512 / 100), dpi = 100)
#plt.axis('off')
plt.gca().set_frame_on(False)

plt.imshow(tile)

#plt.plot(640,570, "og", markersize = 10)
plt.show()

print('final', time.time() - t)