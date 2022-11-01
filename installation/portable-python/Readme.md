# Portable Python

Allows running UBA on any computer by having a complete Python interpreter and UBA code on USB stick.

## Mac (M1 or x86)

Prepare USB stick:
* Verify USB has at least 16 GB free
* Rename USB stick to "UBA_USB"

Download:
* Download [Portable Python 3.10.8](https://drive.google.com/drive/folders/12nyYAvh33ImFnU0_E1Nmv7RhQsOgMFYl)
* Download [UBA.zip](https://github.com/eliranwong/UniqueBible/archive/refs/heads/main.zip)
* Unzip UBA.zip

Minimize:
* In unzipped UBA folder, run `python3 minimize.py` to delete unused files (will delete over 84000 files)
* Run `find . -empty -type d -delete` to delete empty directories

Configure:
* Copy installation/portable-python/run*.sh to UBA root
* On hard drive, execute `run_m1.sh` (M1 Mac) or `run_x86.sh` (x86 Mac) 
* Wait while the venv directory is being created
* After UBA starts, optionally download resources

Copy to stick:
* Copy Portable Python to stick and unzip
* Rename Portable Python directory to either `3.10.8_m1` or `3.10.8_x86`
* Run `unquarantine.sh` on Portable Python files on stick
* Copy UBA.zip to stick and unzip

Run UBA:
* Execute `run_m1.sh` or `run_x86.sh` on stick

Notes:
* On Mac, USB is under `/Volumes`
* On Ubuntu, USB is under `/media`
