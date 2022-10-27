import glob
import os
import re

imagesUsed = []
with open('patches.txt') as f:
    lines = f.readlines()
for line in lines:
    if "htmlResources/material/" in line and ".png" in line:
        match = re.search(r'"file", "(.*)"', line).groups()
        if match:
            image = match[0]
            imagesUsed.append(image)

count = 0
for filename in glob.iglob('htmlResources/material/**/**', recursive=True):
    if "png" in filename and not os.path.isdir(filename):
        if filename not in imagesUsed:
            os.remove(filename)
            count = count + 1
            if count > 5:
                break;
        else:
            print("keeping " + filename)
            print(count)
