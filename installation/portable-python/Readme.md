# Portable Python

Allows running UBA on any computer by having a complete Python interpreter and UBA code on USB stick.

## Mac (M1 or x86)

Download:
* Download [Portable Python 3.10.8](https://drive.google.com/drive/folders/12nyYAvh33ImFnU0_E1Nmv7RhQsOgMFYl)
* Download UBA

Minimize:
* Run `python3 minimize.py` to delete unused files (will delete over 84000 files)
* Run `find . -empty -type d -delete` to delete empty directories

Configure:
* Copy installation/portable-python/run*.sh to UBA root
* On hard drive, execute `run_m1.sh` or `run_x86.sh`
* Download resources

Copy to stick:
* Name stick to `UBA_USB`
* Copy Portable Python to stick and unzip
* Rename to either `3.10.8_m1` or `3.10.8_x86`
* Run `unquarantine.sh` on Portable Python files on stick
* Zip UBA directory
* Copy UBA.zip to stick
* Unzip UBA.zip on stick

Test:
* Execute `run_m1.sh` or `run_x86.sh` on stick

Notes:
* On Mac, `/Volumes`
* On Ubuntu, `/media`
