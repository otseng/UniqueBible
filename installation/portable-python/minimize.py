import glob
import os
import re

if os.path.exists('./htmlResources'):
    pass
elif os.path.exists('../../htmlResources'):
    os.chdir('../../')
else:
    print('Cannot find base dir')
    exit(1)

print('Minimizing ' + os.getcwd())

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
    if 'png' in filename and not os.path.isdir(filename):
        if filename not in imagesUsed:
            os.remove(filename)
            print('removing ' + filename)
            count = count + 1
            # if count > 50000:
            #     exit();
        else:
            pass
            # print('keeping ' + filename)

print('Done')