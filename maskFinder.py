import sys, os
import re

registered = os.listdir(r"Z:\IGPC Registered")      # if in this list and doesn't have "Prostate" folder then append to no_mask
empty = []
print(registered)

no_mask = []
paths = ["Y:/", r"Z:\IGPC"]

for path in paths:
    for (dirpath, dirnames, filenames) in os.walk(path):
        empty = dirnames
        #print(empty)
        # print("files:", filenames)

        for f in empty:
            if path == "Y:/":
                if re.sub(r'\W+', '', f).replace("_","") in registered:
                    if not os.path.isdir(fr"Y:\{f}\Pathology\DIGITIZED_H&E\Prostate"):
                        no_mask.append(f)

            if path == r"Z:\IGPC":
                if re.sub(r'\W+', '', f).replace("_", "") in registered:
                    if not os.path.isdir(fr"Z:\IGPC\{f}\Pathology\DIGITIZED_H&E\Prostate"):
                        no_mask.append(f)


# print(os.listdir("Y:/"))
# print(re.sub(r'\W+', '', empty[0]).replace("_",""))
# print(empty[0])
print(no_mask)

# ['IGPC-2_012', 'IGPC-2_017', 'IGPC1025', 'IGPC1032', 'IGPC-2_042', 'IGPC-2_043', 'IGPC-2_045', 'IGPC-2_046', 'IGPC-2_048', 'IGPC-2_049', 'IGPC-2_050', 'IGPC-2_051', 'IGPC-2_052', 'IGPC2_041']
# ignore the ones that are formatted weird bc those are wrong!