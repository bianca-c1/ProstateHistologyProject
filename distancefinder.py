import numpy as np
from scipy.spatial import distance
import pandas as pd

def dist(X, Y):
    return distance.cdist(X, Y, 'euclidean')

X = np.array([[1, 2], [3, 4], [5, 6]])
Y = np.array([[1,2], [3,4], [5,6]])
distances = dist(X, Y)
#print(distances, '\n')


df2 = pd.read_csv(r'E:\Users\bchiang\IGPC Raw Histology\Vertices\IGPC 1010\IGPC1010 A16.csv')
grouped = df2.groupby('Annotation Name')


for annotation_name, grouped_df in grouped:      # grouped_df is a tuple (for A16 it contains 2 things - G3 and Atrophy)
    print(len(grouped_df.iloc[0:1]))


# contour_name = df2.loc[row, 'Annotation Name']      # initial contour name to compare to in the while loop
#
# name_change = []        # array of indices that tell you when the region changes (e.g. 24 in IGPC1010 A16)
#
# for name_index in range(len(df2.values[:,1])):
#     last_name = df2.values[:,1][name_index-1]
#     if df2.values[:,1][name_index] != last_name and name_index != 0:
#         name_change.append(name_index)
#     name_index +=1

#while df2.loc[row,'Annotation Name'] == contour_name:
#for row in df2.loc[0:23]
