import sys
import csv
import locale
#sys.path.append(r"D:\Users\rau\Code\ImageQuizzer\ImageQuizzer\Code\Utilities")
from UtilsIOXml import UtilsIOXml
from lxml import etree
import os
from MaskUtils import MaskUtils

locale.setlocale(locale.LC_ALL, '')
sDelimiter = ';' if locale.localeconv()['decimal_point'] == ',' else ','
lls = [['edytor poranka PN', '1/04/2016', '15:00'],
       ['edytor PN 2', '2/04/2016', '08:30'],
       ['edytor PN noc', '3/04/2016', '22:00']]

#
#vertices_path = r"E:\Users\bchiang\IGPC Raw Histology\IGPC 2012"
#paths = MaskUtils.getPaths(vertices_path, ".xml")

# CHANGE THIS TO THE DIRECTORY AND FILENAME YOU SAVED THE XML FILE
sXmlPath = r'E:\Users\bchiang\IGPC Raw Histology\IGPC 2012\Prostate\IGPC-2_012 A21-1.xml'

oXML = UtilsIOXml()

# xSession = oXML.OpenXml(sXmlPath, 'Session')[1]
oXML.OpenXml(sXmlPath, 'Annotations')   #Session
xSession = oXML.GetRootNode()

annotations = oXML.GetChildren(xSession, 'Annotation')
# ann_att = oXML.GetListOfNodeAttributes(annotations[0])
# print(ann_att)

lsHeaders = ['Annotation Id', 'Annotation Name', 'Region', 'Length', 'Area', 'Length (Microns)', 'Area (Microns)','Vertices', 'Vertices2', 'Vertices3', 'Vertices4', 'Vertices5', 'Vertices6']
#lsHeaders = ['PageID','PageGroup','QuestionSetID','QuestionDescriptor','QuestionType','Option','ResponseLoginTime','ResponseTime','Response']


# CHANGE THIS TO THE FILENAME YOU WANT TO SAVE THE OUTPUT CSV FILE
with open(r'E:\Users\bchiang\IGPC Raw Histology\Vertices\IGPC 2012\IGPC-2_012 A21-1 Prostate.csv', 'w', newline="") as fID:
    writer = csv.writer(fID, delimiter=sDelimiter)
    writer.writerow(lsHeaders)

    count = 0
    for i in annotations:       # loop through every annotation (1-13, each with their own regions)

        sId = oXML.GetValueOfNodeAttribute(i, 'Id')        # annotation id (1-13)
        sName = oXML.GetValueOfNodeAttribute(i, 'Name')    # annotation name (G3, G4, atrophy, etc.)

        children = oXML.GetChildren(i,"Regions")                               # get the children of the current annotation

        for j in children:                      # loop through all the children (will either be 'regions' or 'attributes')

            childrenlist2 = oXML.GetChildren(j, "Region")
            #print(oXML.GetElementNodeName(childrenlist2[0]))            # children list 2 is full of Region and RAHeaders

            for k in childrenlist2:
                if oXML.GetElementNodeName(k) == "Region":
                    sID = oXML.GetValueOfNodeAttribute(k, 'Id')
                    sLength = oXML.GetValueOfNodeAttribute(k, 'Length')
                    sArea = oXML.GetValueOfNodeAttribute(k, 'Area')
                    sLengthMic = oXML.GetValueOfNodeAttribute(k, 'LengthMicrons')
                    sAreaMic = oXML.GetValueOfNodeAttribute(k, 'AreaMicrons')

                    vertices = oXML.GetChildren(k, 'Vertices')          # vertices label

                    for l in vertices:
                        vertices2 = oXML.GetChildren(l, 'Vertex')       # list of actual vertices

                        vertexlist = []
                        vertexlist2 = []
                        vertexlist3 = []
                        vertexlist4 = []
                        vertexlist5 = []
                        vertexlist6 = []

                        count2 = 0
                        for m in vertices2:                                          # m = every vertex (attributes of each m are the coordinates of that vertex)
                            vertex = oXML.GetAttributes(m)

                            if count2 < 600:
                                vertexlist.append(vertex)
                            elif 600 <= count2 < 1200:
                                vertexlist2.append(vertex)
                            elif 1200 <= count2 < 1800:
                                vertexlist3.append(vertex)
                            elif 1800 <= count2 < 2400:
                                vertexlist4.append(vertex)
                            elif 2400 <= count2 < 3000:
                                vertexlist5.append(vertex)
                            elif 3000 <= count2 <= 3600:
                                vertexlist6.append(vertex)

                            count2+=1

                        lsNewLine = [sId, sName, sID, sLength, sArea, sLengthMic, sAreaMic, vertexlist, vertexlist2, vertexlist3, vertexlist4, vertexlist5, vertexlist6]
                        writer.writerow(lsNewLine)

        count+=1
            
fID.close()