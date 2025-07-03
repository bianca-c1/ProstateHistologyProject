import os
import numpy as np
import matplotlib.pyplot as plt
import openslide
import tifffile as tiff

# documentation:
# https://openslide.org/api/python/

# don't forget to add the r at the beginning of the path
os.add_dll_directory(r'C:\Users\bchiang\miniconda3\Lib\site-packages\openslide-bin-4.0.0.8-windows-x64\bin')

#slide = openslide.open_slide(r'C:\Users\bchiang\Downloads\Lung H&E 3.svs')
#slide = openslide.open_slide(r'E:\Users\bchiang\IGPC Raw Histology\CMU-1.tiff')
slide = openslide.open_slide(r'E:\Users\bchiang\IGPC Raw Histology\IGPC 5002\IGPC-5_002 A14-1.tif')

img = tiff.imread(r'E:\Users\bchiang\IGPC Raw Histology\IGPC 5002\IGPC-5_002 A14-1.tif')

# some metadata stuff (more metadata in the documentation)
level_count = slide.level_count
properties = slide.properties.values()

# levels = levels on the histology slide
# 0 is highest resolution and then highest level is lowest resolution

wsiTile = slide.read_region((16324, 20008), 0, (5120, 5120))

# convert the image from BGR to RBG
wsiTileRGB = wsiTile.convert('RGB')
wsiTileNp = np.array(wsiTileRGB)

# make sure the figures are actually 512x512 because otherwise matplotlib might add padding
plt.figure(figsize = (512 / 100, 512 / 100), dpi = 100)

plt.imshow(wsiTileNp)
plt.axis('off')
plt.gca().set_frame_on(False)

# centers the image
plt.subplots_adjust(left = 0, right = 1, top = 1, bottom = 0)

# actually show the plot!!
plt.show()
