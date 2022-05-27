"""
To run the dashboard, run from the command line the below:
`streamlit run fpls_ui_app/dashboard.py`

"""

import streamlit as st

import data_handling as dh


class Dashboard:

    def __init__(self):
        self.useful_stats = None

        st.button("Download and process FPL database", key="db_down",
                  help="Download the official FPL database using FPL's API and process the data.",
                  on_click=self.download_fpl_database_and_process())

        if st.button("Display useful stats", key="stats", help="Display useful statistics from the FPL database."):
            st.write(self.useful_stats)

    def download_fpl_database_and_process(self):
        _, _, self.useful_stats = dh.process_data(dh.get_fpl_database_in_json())


if __name__ == '__main__':
    obj = Dashboard()
