[![Documentation](https://img.shields.io/badge/GitHub%20Pages-222222?style=for-the-badge&logo=GitHub%20Pages&logoColor=white)](https://ilias4780.github.io/fpl_statistics_ui_app/index)\
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ilias4780-fpl-statistics-ui-app-fpls-ui-appdashboard-tdn5u0.streamlitapp.com/)

Readme
=======

This is a python application providing users with a GUI and a web interface, in order to download 
the FPL database by using the FPL API URL and make statistical calculations.

The Web interface of the app (the streamlit dashboard) is also hosted and available in the following link:
https://ilias4780-fpl-statistics-ui-app-fpls-ui-appdashboard-tdn5u0.streamlitapp.com/

You can use it or take a peak of the functionality there!

Changelog in Version 2.0.0
---------------------------
- Upgraded to python 3.9
- Added `points_per_game` stat column to stat table
- Changed documentation platform to GitHub Pages


Features
----------
- Graphical or Web Interface choice
- Info bar for interesting stats
- Download and save useful data from FPL database
- Save and load database to/from local JSON file for OFFLINE use
- Show sorted statistics based on your selection
- Calculate best 15 selection using mathematical engine solver optimization
- Calculate most valuable players
- Calculate most valuable position
- Calculate most valuable team
- Save data in CSVs


Code setup and execution
-------------------------
1. Create a python virtual environment.
2. Install the required dependencies by executing:  
    `pip install -r requirements.txt`    
3. Then, to execute the PYQT GUI, you execute the `main.py` file either from an IDE or from CMD running:  
    `python fpls_ui_app/main.py`
4. To execute the dashboard, you execute the `dashboard.py` file either from an IDE or from CMD running:  
    `streamlit run fpls_ui_app/dashboard.py`


Support
--------
If you have new ideas on features you would like feel free to either send an email to 
`ilias4780@gmail.com` or jump into the code yourself building it. You can also use the Issues
page of GitHub.
