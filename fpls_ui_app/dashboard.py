"""
To run the dashboard, run from the command line the below:
`streamlit run fpls_ui_app/dashboard.py`

"""

import streamlit as st

import data_handling as dh

if "current_gameweek" not in st.session_state:
    # Download and process the data
    st.session_state.current_gameweek, \
        st.session_state.next_deadline_date, \
        st.session_state.useful_player_attributes = dh.process_data(dh.get_fpl_database_in_json())

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
