# Code changes for pyinstaller

* Add main.spec
* Add database wrapper (dbw.py) to use sqlite3 for binary run mode and apsw for Python run mode
* Add config.enableBinaryRunMode that is enabled when file "enable_binary_run_mode" exists in root
* Use Starter.py for layout
* Disable code self-updating
* Disable modules 'chinese-english-lookup','word-forms','lemmagen3'

## Code snippet

if config.enableBinaryRunMode:
