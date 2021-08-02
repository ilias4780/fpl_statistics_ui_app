[![Documentation Status](https://readthedocs.org/projects/fpl-statistics-ui-app/badge/?version=latest)](https://fpl-statistics-ui-app.readthedocs.io/en/latest/?badge=latest)

Readme
=======

This is a python application providing users with a GUI in order to download 
the FPL database by using the FPL API URL and make statistical calculations.

Changelog in Version 1.8.0
---------------------------
- Reverted to PyQt5 due to PyQt6 failing auto docs and pyinstaller build.
- Added `Archive` folder that stores the databases of previous years.
- Restructured GUI to use Tabs for different app features (enabling more space for future features).


Features
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
------------------------
You can download the zip containing the application's executable
if you don't care about the code. Just download the `FPL_Statistics_UI` zip
and double click the `FPL_Python_Stats.exe` inside it. Enjoy! 

Code setup
-------------
1. Create a python virtual environment.
2. Install the required dependencies by executing:  
    `pip install -r requirements.txt`    
3. Then you execute the `main.py` file either from an IDE or from CMD running:  
    `python fpls_ui_app/main.py`

To build the application into an executable the following command was used: 
    `pyinstaller --onedir --windowed --add-data "C:/Users/.../Lib/site-packages/pulp;pulp/" -n FPL_Python_Stats fpls_ui_app/main.py`


Support
-------------
If you have new ideas on features you would like feel free to either send an email to 
`ilias4780@gmail.com` or jump into the code yourself building it. You can also use the Issues
page of Github.
