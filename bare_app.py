import numpy as np
import pandas as pd
import requests


def main():
    the_whole_db_in_json = get_fpl_database_in_json()

    element_types_df, teams_df, useful_player_attributes = keep_useful_data(the_whole_db_in_json)

    useful_player_attributes = map_position_and_team_columns(element_types_df, teams_df, useful_player_attributes)

    useful_player_attributes = correct_value_season_column(useful_player_attributes)

    most_vfm_players(useful_player_attributes, 5)

    most_valuable_position(useful_player_attributes)

    most_valuable_teams(useful_player_attributes, 5)

    save_to_csv_file(useful_player_attributes)


def save_to_csv_file(useful_player_attributes):
    # Save to csv file
    useful_player_attributes.to_csv('FplStatisticsSummary2020.csv')


def most_valuable_teams(useful_player_attributes, length):
    # Find which teams provide the most value when players with zero value are not considered
    useful_player_attributes_no_zeros = useful_player_attributes.loc[useful_player_attributes.value > 0]
    team_pivot = \
        useful_player_attributes_no_zeros.pivot_table(index='team_name', values='value', aggfunc=np.mean).reset_index()
    print('##############################################')
    print(team_pivot.sort_values('value', ascending=False).head(length))
    print('##############################################')


def most_valuable_position(useful_player_attributes):
    # Find which position provides the most value when players with zero value are not considered
    useful_player_attributes_no_zeros = useful_player_attributes.loc[useful_player_attributes.value > 0]
    pivot = \
        useful_player_attributes_no_zeros.pivot_table(index='position', values='value', aggfunc=np.mean).reset_index()
    print('##############################################')
    print(pivot.sort_values('value', ascending=False))
    print('##############################################')


def most_vfm_players(useful_player_attributes, length):
    # Find the most vfm players (most points per cost - value = points / cost)
    print('##############################################')
    print(useful_player_attributes.sort_values('value', ascending=False).head(length))
    print('##############################################')


def correct_value_season_column(useful_player_attributes):
    # Make a new column for value_season to guarantee float type of values in order to sort the df using it
    useful_player_attributes.insert(5, 'value', useful_player_attributes.value_season.astype(float))
    # Drop the value_season column as it is not needed anymore
    useful_player_attributes = useful_player_attributes.drop(['value_season'], axis=1)

    return useful_player_attributes


def map_position_and_team_columns(element_types_df, teams_df, useful_player_attributes):
    # Map the position of the player to a new column using the element types dataframe
    useful_player_attributes.insert(
        3, 'position', useful_player_attributes['element_type'].map(element_types_df.set_index('id').singular_name))
    # Drop the element type column as it is not needed anymore
    useful_player_attributes = useful_player_attributes.drop(['element_type'], axis=1)

    # Map the team of the player using the teams dataframe
    useful_player_attributes.insert(4, 'team_name', useful_player_attributes.team.map(teams_df.set_index('id').name))
    # Drop the team column as it is not needed anymore
    useful_player_attributes = useful_player_attributes.drop(['team'], axis=1)

    return useful_player_attributes


def keep_useful_data(the_whole_db_in_json):
    # Keep the data pieces that are needed for our application in pandas DataFrame format
    all_elements_df = pd.DataFrame(the_whole_db_in_json['elements'])
    element_types_df = pd.DataFrame(the_whole_db_in_json['element_types'])
    teams_df = pd.DataFrame(the_whole_db_in_json['teams'])

    # Keep the useful columns of the elements dataframe
    useful_player_attributes = all_elements_df[['first_name', 'second_name', 'team', 'selected_by_percent',
                                                'value_season', 'minutes', 'goals_scored', 'assists',
                                                'clean_sheets', 'own_goals', 'penalties_saved', 'penalties_missed',
                                                'saves', 'element_type', 'yellow_cards', 'red_cards', 'bonus',
                                                'transfers_in', 'total_points']]

    return element_types_df, teams_df, useful_player_attributes


def get_fpl_database_in_json():
    fpl_api_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    the_whole_db = requests.get(fpl_api_url)
    return the_whole_db.json()
