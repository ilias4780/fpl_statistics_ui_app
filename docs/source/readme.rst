.. _Readme:

FPL Python Statistics UI App
==============================

This is a python application providing users with a GUI in order to download
the FPL database by using the FPL API URL and make statistical calculations.

Changelog in Version 1.6
--------------------------
- You can now save the downloaded FPL database locally in human readable JSON format (I propose Notepad++ for
  opening it after). That way you can create an archive of data of each Game Week for the whole season.
- You can now use the app OFFLINE! by loading from a JSON file the FPL database. The options for both saving and
  loading to/from local file are in the `Options` menu on the top of the window.
- Added docstrings and Sphinx generated HTML documentation.

Features:
-------------
- Graphical Interface
- Info bar for interesting stats
- Download and save useful data from FPL database
- Save and load database to/from local JSON file for OFFLINE use
- Show sorted statistics based on your selection
- Calculate best 15 selection using mathematical engine solver optimization
- Calculate most valuable players
- Calculate most valuable position
- Calculate most valuable team
- Save data in CSVs

EXECUTABLE AVAILABLE!!
-----------------------
You can now download the zip containing the application's executable
if you don't care about the code. Just download the `FPL_Statistics_UI` zip
and double click the `FPL_Python_Stats.exe` inside it. Enjoy!

Code setup:
-------------
1. Create a python virtual environment.
2. Install the required dependencies by executing:
`pip install -r requirements.txt`
3. Then you execute the `main.py` file either from an IDE or from CMD running:
`python main.py`


To build the application the following command was used:
`pyinstaller --onedir --windowed --add-data "C:/Users/.../Lib/site-packages/pulp;pulp/" -n FPL_Python_Stats main.py`
To generate docstrings using pyment:
`pyment -w -o reST .`


Support:
-------------
If you have new ideas on features you would like feel free to either send an email to
`ilias4780@gmail.com` or jump into the code yourself building it. You can also use the Issues
page of Github.
