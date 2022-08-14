.. _Readme:

.. image:: https://readthedocs.org/projects/fpl-statistics-ui-app/badge/?version=latest
    :target: https://fpl-statistics-ui-app.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Readme
=======

This is a python application providing users with a GUI and a web interface, in order to download
the FPL database by using the FPL API URL and make statistical calculations.

The Web interface of the app (the streamlit dashboard) is also hosted and available in the following link:
https://ilias4780-fpl-statistics-ui-app-fpls-ui-appdashboard-tdn5u0.streamlitapp.com/

You can use it or take a peak of the functionality there!

Changelog in Version 1.9.0
---------------------------
- Separated all the calculations and data functionality from the controller.
- Created a Streamlit dashboard to show the calculations, instead of running the application as PYQT app.
- Added last year's database json (2021-2022) to `Archive` folder.
- Removed exe zip, an exe will no longer be available.

Changelog in Version 1.9.1
---------------------------
- Couple of fixes to the configuration of the streamlit dashboard
- Hosted the streamlit dashboard in the streamlit cloud (link shared above)


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
page of Github.