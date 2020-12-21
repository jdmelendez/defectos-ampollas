
import math
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
import io
import glob
import os


PATH_ANNS = "./GUI/Archivos/dataset/Anotaciones/20124_132949_C4_12_D.xml"

annotation_xml = ET.parse(PATH_ANNS)
print(annotation_xml)
root = annotation_xml.getroot()

for indice_root, i in enumerate(root):
    for indice_child, child in enumerate(i):
        # print(child.tag, child.attrib)

        if indice_root == 1:
            indice_child = indice_child + len(root[0])

        print(child.tag)
        #     data_string = child.text
        # print(data_string)


#     data_string = i.text
#     print(data_string)

# print(root)
