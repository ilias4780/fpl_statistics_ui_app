"""
To run the dashboard, run from the command line the below:
`streamlit run fpls_ui_app/dashboard.py`

"""
import json

import streamlit as st

import best_15_optimisation as opt
import data_handling as dh


def set_best15_players_template(goalkeepers,
                                defenders,
                                midfielders,
                                forwards,
                                statistics,
                                st_tab):
    """
    Creates the template for the best 15 players selection and populates it.
    """
    # stats
    st_tab.write("OPTIMISATION STATS:")
    col1, col2, col3, col4 = st_tab.columns(4)
    col1.metric(label=list(statistics.keys())[0], value=list(statistics.values())[0])
    col2.metric(label=list(statistics.keys())[1], value=list(statistics.values())[1])
    col3.metric(label=list(statistics.keys())[2], value=list(statistics.values())[2])
    col4.metric(label=list(statistics.keys())[3], value=list(statistics.values())[3])
    if list(statistics.values())[0] == 'Optimal':
        st_tab.write("TEAM SELECTION:")
        st_tab.markdown(

            """
            <style>
            table {
                color: black;
                font-weight: bold;
                min-width: 800px;
                min-height: 600px;
                background: url("https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Football_field.svg/512px-Football_field.svg.png");
                background-size: 100% 100%;
            }
            table th:first-of-type {
                width: 20%;
            }
            table th:nth-of-type(2) {
                width: 20%;
            }
            table th:nth-of-type(3) {
                width: 20%;
            }
            table th:nth-of-type(4) {
                width: 20%;
            }
            table th:nth-of-type(5) {
                width: 20%;
            }
            </style>
            """
            f"""
            |                  |                  |                  |                  |                  |
            |:----------------:|:----------------:|:----------------:|:----------------:|:----------------:|
            |                  | {goalkeepers[0]} |                  | {goalkeepers[1]} |                  |
            |  {defenders[0]}  |  {defenders[1]}  |  {defenders[2]}  |  {defenders[3]}  |  {defenders[4]}  |
            | {midfielders[0]} | {midfielders[1]} | {midfielders[2]} | {midfielders[3]} | {midfielders[4]} |
            |                  |  {forwards[0]}   |  {forwards[1]}   |  {forwards[2]}   |                  |
            |                  |                  |                  |                  |                  |
            """,
            unsafe_allow_html=True
        )


def run_dashboard():
    """
    Runs the streamlit dashboard.
    """
    st.set_page_config(layout="wide")

    if "full_database" not in st.session_state:
        # Download and process the data
        st.session_state.full_database = dh.get_fpl_database_in_json()
        (st.session_state.current_gameweek,
         st.session_state.next_deadline_date,
         st.session_state.useful_player_attributes) = dh.process_data(st.session_state.full_database)
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

    # Create the two tabs
    stat_tab, opt_tab = st.tabs(['Statistics', 'Best Selection'])

    # Create the upload data button in the sidebar
    uploaded_file = st.sidebar.file_uploader(
        "Load Database from file",
        type=['json'],
        key="upload",
        help="Load the FPL database from a local JSON file. (Please delete any uploaded "
             "file in order for the downloaded data to take precedence."
    )
    if uploaded_file:
        uploaded_fpl_db = json.load(uploaded_file)
        (st.session_state.current_gameweek,
         st.session_state.next_deadline_date,
         st.session_state.useful_player_attributes) = dh.process_data(uploaded_fpl_db)
        st.session_state.most_valuable_teams = dh.calculate_most_valuable_teams(
            st.session_state.useful_player_attributes
        )
        st.session_state.most_valuable_positions = dh.calculate_most_valuable_position(
            st.session_state.useful_player_attributes
        )

    # Create the re-download db button in the sidebar
    if st.sidebar.button(
            "Re-Download Database from FPL",
            key="download",
            help="Download the FPL database again from FPL server."
    ):
        st.session_state.full_database = dh.get_fpl_database_in_json()
        (st.session_state.current_gameweek,
         st.session_state.next_deadline_date,
         st.session_state.useful_player_attributes) = dh.process_data(st.session_state.full_database)
        st.session_state.most_valuable_teams = dh.calculate_most_valuable_teams(
            st.session_state.useful_player_attributes
        )
        st.session_state.most_valuable_positions = dh.calculate_most_valuable_position(
            st.session_state.useful_player_attributes
        )

    # Create the save downloaded db into json in the sidebar
    st.sidebar.download_button(
        "Save FPL database to file",
        data=json.dumps(st.session_state.full_database, indent=4),
        file_name="FplData.json",
        mime="application/json",
        key="down_data",
        help="Save the full FPL downloaded database into a JSON file."
    )

    # Create the display stats button
    if stat_tab.button(
            "Display useful stats",
            key="stats",
            help="Display useful statistics from the FPL database."
    ):
        stat_tab.write(st.session_state.useful_player_attributes.drop('uid', axis=1))
        stat_tab.download_button(
            "Download useful stats",
            data=st.session_state.useful_player_attributes.to_csv(),
            mime="text/csv",
            key="down_stats",
            help="Download the useful stats in CSV format."
        )

    # Create the display most valuable teams button
    if stat_tab.button(
            "Display most valuable teams",
            key="mvp_teams",
            help="Display the most valuable teams of the PL according to aggregated value of players."
    ):
        stat_tab.write(st.session_state.most_valuable_teams)
        stat_tab.download_button(
            "Download most valuable teams",
            data=st.session_state.most_valuable_teams.to_csv(),
            file_name="FplMVPTeams.csv",
            mime="text/csv",
            key="down_teams",
            help="Download the most valuable teams stats in CSV format."
        )

    # Create the display most valuable positions button
    if stat_tab.button(
            "Display most valuable positions",
            key="mvp_positions",
            help="Display the most valuable positions of the PL according to "
                 "aggregated value of players in that position."
    ):
        stat_tab.write(st.session_state.most_valuable_positions)
        stat_tab.download_button(
            "Download most valuable positions",
            data=st.session_state.most_valuable_positions.to_csv(),
            file_name="FplMVPPositions.csv",
            mime="text/csv",
            key="down_positions",
            help="Download the most valuable positions stats in CSV format."
        )

    # Best 15 selection optimisation
    # Pre-selected players multi selects
    pre_selected_gks = opt_tab.multiselect(
        "Pre-selected Goalkeepers:",
        options=st.session_state.useful_player_attributes.loc[
            st.session_state.useful_player_attributes['position'] == 'Goalkeeper', 'name'],
        max_selections=2,
        help="Enforce the selection of specific goal keeper(s)."
    )
    pre_selected_defs = opt_tab.multiselect(
        "Pre-selected Defenders:",
        options=st.session_state.useful_player_attributes.loc[
            st.session_state.useful_player_attributes['position'] == 'Defender', 'name'],
        max_selections=5,
        help="Enforce the selection of specific defender(s)."
    )
    pre_selected_mfs = opt_tab.multiselect(
        "Pre-selected Midfielders:",
        options=st.session_state.useful_player_attributes.loc[
            st.session_state.useful_player_attributes['position'] == 'Midfielder', 'name'],
        max_selections=5,
        help="Enforce the selection of specific midfielder(s)."
    )
    pre_selected_fwds = opt_tab.multiselect(
        "Pre-selected Forwards:",
        options=st.session_state.useful_player_attributes.loc[
            st.session_state.useful_player_attributes['position'] == 'Forward', 'name'],
        max_selections=3,
        help="Enforce the selection of specific forward(s)."
    )
    pre_selected_players = (pre_selected_gks + pre_selected_defs +
                            pre_selected_mfs + pre_selected_fwds)
    pre_selected_uids = st.session_state.useful_player_attributes.query(
        'name in (@pre_selected_players)'
    )['uid'].tolist()

    # Best 15 selection calculation
    options_mapping = {
        'Total Points': 'total_points',
        'Value': 'value',
        'Form': 'form',
        'ICT Index': 'ict_index'
    }
    if option := opt_tab.selectbox(
            "Calculate best 15 players - select criteria:",
            options=[None, *options_mapping.keys()],
            key="best_15",
            help="Calculate the best 15 player selection based on the criteria selected below."
    ):
        result_df, total_stats = opt.find_best_15_players_by_value(
            st.session_state.useful_player_attributes['uid'].tolist(),
            st.session_state.useful_player_attributes['position'].tolist(),
            st.session_state.useful_player_attributes[options_mapping[option]].tolist(),
            st.session_state.useful_player_attributes['now_cost'].tolist(),
            st.session_state.useful_player_attributes['team_name'].tolist(),
            options_mapping[option],
            pre_selected_uids
        )
        df_for_view, gks, defs, mfs, fwds, stats = opt.post_process_data(
            st.session_state.useful_player_attributes[['uid', 'name']].copy(),
            result_df,
            total_stats
        )
        set_best15_players_template(
            gks,
            defs,
            mfs,
            fwds,
            stats,
            opt_tab
        )


if __name__ == '__main__':
    run_dashboard()
