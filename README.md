[![Documentation Status](https://readthedocs.org/projects/fpl-statistics-ui-app/badge/?version=latest)](https://fpl-statistics-ui-app.readthedocs.io/en/latest/?badge=latest)

README
=======

This is a python application providing users with a GUI in order to download 
the FPL database by using the FPL API URL and make statistical calculations.

Changelog in Version 1.7.0
---------------------------
- Upgraded from PyQt5 to PyQt6 library.
- Issue #3: Fixed sorting issue in for columns ICT Index and Selected by Percent.
- Ticket by geo-xar: When shorting rows by any criteria then the relevant column should be displayed first
- Ticket by geo-xar: Added a new column containing the transfer difference (transfers in - transfers out) which can
  be used for sorting as well. Colour may be used in the future but not in this release.
- Executable was not updated as I face an issue with PyQt6 and pyinstaller. Will update once I find the solution.


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
    `pyinstaller --onedir --windowed --add-data "C:/Users/.../Lib/site-packages/pulp;pulp/" -n FPL_Python_Stats main.py`


Support
-------------
If you have new ideas on features you would like feel free to either send an email to 
`ilias4780@gmail.com` or jump into the code yourself building it. You can also use the Issues
page of Github.
