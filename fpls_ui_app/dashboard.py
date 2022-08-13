"""
To run the dashboard, run from the command line the below:
`streamlit run fpls_ui_app/dashboard.py`

"""
import json

import streamlit as st

import best_15_optimisation as opt
import data_handling as dh


def set_best15_players_template(goalkeepers, defenders, midfielders, forwards, statistics):
    """
    Creates the template for the best 15 players selection and populates it.
    """
    # stats
    st.write("OPTIMISATION STATS:")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label=list(statistics.keys())[0], value=list(statistics.values())[0])
    col2.metric(label=list(statistics.keys())[1], value=list(statistics.values())[1])
    col3.metric(label=list(statistics.keys())[2], value=list(statistics.values())[2])
    col4.metric(label=list(statistics.keys())[3], value=list(statistics.values())[3])
    st.write("TEAM SELECTION:")
    # goalkeepers
    col1, col2, col3, col4 = st.columns(4)
    col2.markdown(goalkeepers[0])
    col3.markdown(goalkeepers[1])
    # defenders
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown(defenders[0])
    col2.markdown(defenders[1])
    col3.markdown(defenders[2])
    col4.markdown(defenders[3])
    col5.markdown(defenders[4])
    # midfielders
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown(midfielders[0])
    col2.markdown(midfielders[1])
    col3.markdown(midfielders[2])
    col4.markdown(midfielders[3])
    col5.markdown(midfielders[4])
    # forwards
    col1, col2, col3, col4, col5 = st.columns(5)
    col2.markdown(forwards[0])
    col3.markdown(forwards[1])
    col4.markdown(forwards[2])


def run_dashboard():
    """
    Runs the streamlit dashboard.
    """
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

    # Create the best 15 selection button
    options_mapping = {
        'Total Points': 'total_points',
        'Value': 'value',
        'Form': 'form',
        'ICT Index': 'ict_index'
    }
    if option := st.sidebar.selectbox("Calculate best 15 players - select criteria:",
                                      options=[None, *options_mapping.keys()], key="best_15",
                                      help="Calculate the best 15 player selection based on the criteria selected below."):
        names, positions, values, prices, teams = opt.pre_process_data(st.session_state.useful_player_attributes,
                                                                       options_mapping[option])
        result_df, total_stats = opt.find_best_15_players_by_value(names, positions, values, prices, teams,
                                                                   options_mapping[option])
        df_for_view, gks, defs, mfs, fwds, stats = opt.post_process_data(result_df, total_stats)
        set_best15_players_template(gks, defs, mfs, fwds, stats)

    # Create the save downloaded db into json
    st.sidebar.download_button("Download FPL database to file",
                               data=json.dumps(st.session_state.full_database, indent=4),
                               file_name="FplData.json", mime="application/json", key="down_data",
                               help="Download the full FPL downloaded database into a JSON file.")


if __name__ == '__main__':
    run_dashboard()
