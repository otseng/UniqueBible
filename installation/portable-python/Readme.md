# Portable Python

Allows running UBA from a memory stick by having a complete Python interpreter and UBA code on memory stick.

## How to generate for Mac

Python:
* Copy [Portable Python 3.10.8](https://drive.google.com/drive/folders/12nyYAvh33ImFnU0_E1Nmv7RhQsOgMFYl) to memory stick.
* Run `unquarantine.sh` on Python files.

UBA:
* Run `python3 minimize.py` to delete unused files (will delete over 84000 files)
* Run `find . -empty -type d -delete` to delete empty directories
* Zip UBA directory
* Copy UBA.zip to stick
* Unzip UBA.zip on stick
