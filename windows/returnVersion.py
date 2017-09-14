from __future__ import print_function
# This script reads the setup.py and returns the current version number
# Used as part of building the WIndows setup file (DronekitWinBuild.bat)
# It assumes there is a line like this:
# version = "12344"

# glob supports Unix style pathname extensions
with open("../setup.py") as f:
    searchlines = f.readlines()
    for i, line in enumerate(searchlines):
        if "version = " in line: 
            print(line[11:len(line)-2])
            break