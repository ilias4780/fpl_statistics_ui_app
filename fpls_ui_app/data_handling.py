"""
Source file that holds the functions to download and process the FPL data.

Functions in the source file:
    * :func:`get_fpl_database_in_json`: Get the FPL database using the FPL's API.
    * :func:`process_data`: Extract the parts that we want to keep from the downloaded data and process them.
    * :func:`sort_statistics_table`: Sort the table view with the player statistics.
    * :func:`calculate_most_valuable_position`: Create a table view with the most valuable positions.
    * :func:`calculate_most_valuable_teams`: Create a table view with the most valuable teams.
"""

import datetime
import numpy as np
import pandas as pd
import requests


def get_fpl_database_in_json():
    """
    Get the FPL database using the FPL's API.
    """
    fpl_api_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    the_whole_db = requests.get(fpl_api_url)
    return the_whole_db.json()


def process_data(fpl_database_in_json):
    """
    Extract the parts that we want to keep from the downloaded data and process them.

    :param fpl_database_in_json: FPL database in JSON format
    :type fpl_database_in_json: dict
    """
    # Keep the data pieces that are needed for our application in pandas DataFrame format
    all_elements_df = pd.DataFrame(fpl_database_in_json['elements'])
    element_types_df = pd.DataFrame(fpl_database_in_json['element_types'])
    teams_df = pd.DataFrame(fpl_database_in_json['teams'])

    # Use events df to add interesting stats like current gw, most points etc
    events_df = pd.DataFrame(fpl_database_in_json['events'])
    current_gameweek_index = events_df['is_current'].idxmax()
    current_gameweek = current_gameweek_index + 1
    try:
        next_deadline = events_df['deadline_time'][current_gameweek_index+1]
        next_deadline_date = datetime.datetime.strptime(next_deadline, '%Y-%m-%dT%H:%M:%SZ')\
            .strftime('%Y-%m-%d %H:%M:%S GMT')
    except KeyError:
        next_deadline_date = 'End of Season'
    # Data for future stats labels
    # highest_current_score = events_df['highest_score'][current_gameweek_index]
    # current_most_captained_index = events_df['most_captained'][current_gameweek_index]
    # current_most_captained = all_elements_df['second_name'][current_most_captained_index]
    # current_most_selected = events_df['most_selected'][current_gameweek_index]
    # current_most_transferred_in_index = events_df['most_transferred_in'][current_gameweek_index]
    # current_most_transferred_in = all_elements_df['second_name'][current_most_transferred_in_index]

    # Keep the useful columns of the elements dataframe
    useful_player_attributes = all_elements_df[['second_name', 'first_name', 'team', 'selected_by_percent',
                                                'value_season', 'form', 'minutes', 'ict_index', 'ict_index_rank',
                                                'goals_scored', 'assists', 'clean_sheets', 'own_goals',
                                                'penalties_saved', 'penalties_missed', 'saves', 'element_type',
                                                'yellow_cards', 'red_cards', 'bonus', 'transfers_in', 'transfers_out',
                                                'now_cost', 'total_points']].copy()

    # Adjust the 'now_cost' column to show millions (by default instead of 5.5 shows 55)
    useful_player_attributes.loc[:, 'now_cost'] *= 0.1

    # TODO: all_elements_df[['chance_of_playing_this_round', 'chance_of_playing_next_round']]
    # TODO: divide total_points with minutes to find points per minute of play
    # TODO: find about cost_change_event, cost_change_event_fall, cost_change_start, cost_change_start_fall

    # Map the position of the player to a new column using the element types dataframe
    useful_player_attributes.insert(
        2, 'position',
        useful_player_attributes['element_type'].map(element_types_df.set_index('id').singular_name))
    # Drop the element type column as it is not needed anymore
    useful_player_attributes = useful_player_attributes.drop(['element_type'], axis=1)

    # Map the team of the player using the teams dataframe
    useful_player_attributes.insert(
        3, 'team_name', useful_player_attributes.team.map(teams_df.set_index('id').name))
    # Drop the team column as it is not needed anymore
    useful_player_attributes = useful_player_attributes.drop(['team'], axis=1)

    # Make a new column for value_season to guarantee float type of values in order to sort the df using it
    useful_player_attributes.insert(5, 'value', useful_player_attributes.value_season.astype(float))
    # Drop the value_season column as it is not needed anymore
    useful_player_attributes = useful_player_attributes.drop(['value_season'], axis=1)

    # Cast ICT Index and Selected by Percent Columns to numeric, so that they can be sorted properly.
    useful_player_attributes[["ict_index", "selected_by_percent"]] = \
        useful_player_attributes[["ict_index", "selected_by_percent"]].apply(pd.to_numeric)

    # Make a new column for the transfer difference
    transfer_loc = useful_player_attributes.columns.get_loc("transfers_in")
    useful_player_attributes.insert(
        transfer_loc, "transfer_diff",
        useful_player_attributes["transfers_in"] - useful_player_attributes["transfers_out"]
    )

    return current_gameweek, next_deadline_date, useful_player_attributes


def sort_statistics_table(useful_player_attributes, column_to_sort):
    """
    Sort the table view with the player statistics.

    :param useful_player_attributes: FPL statistics table
    :type useful_player_attributes: pandas.dataframe
    :param column_to_sort: Column to use for sorting
    :type column_to_sort: str
    """

    columns = useful_player_attributes.columns.tolist()
    column_to_sort_index = columns.index(column_to_sort)
    if column_to_sort == 'position':
        columns.insert(2, columns.pop(column_to_sort_index))
    elif column_to_sort == 'team_name':
        columns.insert(3, columns.pop(column_to_sort_index))
    else:
        columns.insert(4, columns.pop(column_to_sort_index))
    return useful_player_attributes.reindex(columns=columns).sort_values(column_to_sort, ascending=False)


def calculate_most_valuable_position(useful_player_attributes):
    """
    Create a table view with the most valuable positions.

    :param useful_player_attributes: FPL statistics table
    :type useful_player_attributes: pandas.dataframe
    """

    # Find which position provides the most value when players with zero value are not considered
    useful_player_attributes_no_zeros = useful_player_attributes.loc[useful_player_attributes.value > 0]
    pivot = useful_player_attributes_no_zeros.pivot_table(index='position', values='value',
                                                          aggfunc=np.mean).reset_index()
    pivot['value'] = pivot['value'].round(decimals=2)
    return pivot.sort_values('value', ascending=False)


def calculate_most_valuable_teams(useful_player_attributes):
    """
    Create a table view with the most valuable teams.

    :param useful_player_attributes: FPL statistics table
    :type useful_player_attributes: pandas.dataframe
    """

    # Find which teams provide the most value when players with zero value are not considered
    useful_player_attributes_no_zeros = useful_player_attributes.loc[useful_player_attributes.value > 0]
    team_pivot = useful_player_attributes_no_zeros.pivot_table(index='team_name', values='value',
                                                               aggfunc=np.mean).reset_index()
    team_pivot['value'] = team_pivot['value'].round(decimals=2)
    return team_pivot.sort_values('value', ascending=False)
