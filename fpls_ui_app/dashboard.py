"""
To run the dashboard, run from the command line the below:
`streamlit run fpls_ui_app/dashboard.py`

"""
import json

import streamlit as st

import data_handling as dh


if "full_database" not in st.session_state:
    # Download and process the data
    st.session_state.full_database = dh.get_fpl_database_in_json()
    st.session_state.current_gameweek, \
        st.session_state.next_deadline_date, \
        st.session_state.useful_player_attributes = dh.process_data(st.session_state.full_database)
    # Get most valuable teams and positions
    st.session_state.most_valuable_teams = dh.calculate_most_valuable_teams(
        st.session_state.useful_player_attributes
    )
    st.session_state.most_valuable_positions = dh.calculate_most_valuable_position(
        st.session_state.useful_player_attributes
    )

# Create the text elements
st.title("Welcome to the FPL Statistics Python APP! Good luck with your season!")
col1, col2 = st.columns(2)
col1.header(f"Current Gameweek: {st.session_state.current_gameweek}")
col2.header(f"Next Deadline Date: {st.session_state.next_deadline_date}")

# Create the upload data button
uploaded_file = st.sidebar.file_uploader("Load Database from file", type=['json'], key="upload",
                                         help="Load the FPL database from a local JSON file. (Please delete any "
                                              "uploaded file in order for the downloaded data to take precedence.")
if uploaded_file:
    uploaded_fpl_db = json.load(uploaded_file)
    st.session_state.current_gameweek, \
        st.session_state.next_deadline_date, \
        st.session_state.useful_player_attributes = dh.process_data(uploaded_fpl_db)
    st.session_state.most_valuable_teams = dh.calculate_most_valuable_teams(
        st.session_state.useful_player_attributes
    )
    st.session_state.most_valuable_positions = dh.calculate_most_valuable_position(
        st.session_state.useful_player_attributes
    )

# Create the re-download db button
if st.sidebar.button("Re-Download Database from FPL", key="upload",
                     help="Download the FPL database again from FPL server."):
    st.session_state.full_database = dh.get_fpl_database_in_json()
    st.session_state.current_gameweek, \
        st.session_state.next_deadline_date, \
        st.session_state.useful_player_attributes = dh.process_data(st.session_state.full_database)
    st.session_state.most_valuable_teams = dh.calculate_most_valuable_teams(
        st.session_state.useful_player_attributes
    )
    st.session_state.most_valuable_positions = dh.calculate_most_valuable_position(
        st.session_state.useful_player_attributes
    )

# Create the display stats button
if st.sidebar.button("Display useful stats", key="stats", help="Display useful statistics from the FPL database."):
    st.write(st.session_state.useful_player_attributes)
    st.download_button("Download useful stats", data=st.session_state.useful_player_attributes.to_csv(),
                       file_name="FplUsefulStats.csv", mime="text/csv", key="down_stats",
                       help="Download the useful stats in CSV format.")

# Create the display most valuable teams button
if st.sidebar.button("Display most valuable teams", key="mvp_teams",
                     help="Display the most valuable teams of the PL according to aggregated value of players."):
    st.write(st.session_state.most_valuable_teams)
    st.download_button("Download most valuable teams", data=st.session_state.most_valuable_teams.to_csv(),
                       file_name="FplMVPTeams.csv", mime="text/csv", key="down_teams",
                       help="Download the most valuable teams stats in CSV format.")

# Create the display most valuable positions button
if st.sidebar.button("Display most valuable positions", key="mvp_positions",
                     help="Display the most valuable positions of the PL according to "
                     "aggregated value of players in that position."):
    st.write(st.session_state.most_valuable_positions)
    st.download_button("Download most valuable positions", data=st.session_state.most_valuable_positions.to_csv(),
                       file_name="FplMVPPositions.csv", mime="text/csv", key="down_positions",
                       help="Download the most valuable positions stats in CSV format.")

# Create the save downloaded db into json
st.sidebar.download_button("Download FPL database to file", data=json.dumps(st.session_state.full_database, indent=4),
                           file_name="FplData.json", mime="application/json", key="down_data",
                           help="Download the full FPL downloaded database into a JSON file.")

