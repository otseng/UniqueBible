import glob
import os
import re

baseDir = ''

if os.path.exists('./htmlResources'):
    baseDir = './'
elif os.path.exists( '../../htmlResources'):
    baseDir = '../../'
else:
    print('Cannot find base dir')
    exit(1)

os.chdir(baseDir)

print('Base dir: ' + os.getcwd())

imagesUsed = []
with open(baseDir + 'patches.txt') as f:
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
        else:
            print("keeping " + filename)
            count = count + 1
            if count > 5:
                exit();
