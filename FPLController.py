"""
    FPLController.py
"""

import logging

import pandas as pd
import requests

import FPLModel as m


class Controller(object):

    def __init__(self, main_window):
        self.logger = logging.getLogger(__name__)
        self.main_window = main_window

        self.fpl_database_in_json = None
        self.all_elements_df = None
        self.element_types_df = None
        self.teams_df = None
        self.useful_player_attributes = None
        self.most_vfm_players = None
        self.model = None

        # Connections
        self.main_window.menu.addAction('&Exit', self.main_window.close)
        self.main_window.download_database_button.clicked.connect(self.get_fpl_database_in_json)
        self.main_window.process_data_button.clicked.connect(self.process_data)
        self.main_window.most_vfm_players_button.clicked.connect(self.display_most_vfm_players)

    def get_fpl_database_in_json(self):
        fpl_api_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        try:
            the_whole_db = requests.get(fpl_api_url)
        except requests.RequestException as e:
            self.main_window.set_response_display_text("An error has occurred while trying to download the database. "
                                                       "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to download the database.", exc_info=True)
        else:
            self.fpl_database_in_json = the_whole_db.json()
            self.main_window.set_response_display_text("Database has been downloaded successfully.")
            self.logger.debug("Database has been downloaded successfully.")
            self.main_window.process_data_button.setDisabled(False)

    def process_data(self):
        try:
            # Keep the data pieces that are needed for our application in pandas DataFrame format
            self.all_elements_df = pd.DataFrame(self.fpl_database_in_json['elements'])
            self.element_types_df = pd.DataFrame(self.fpl_database_in_json['element_types'])
            self.teams_df = pd.DataFrame(self.fpl_database_in_json['teams'])

            # Keep the useful columns of the elements dataframe
            self.useful_player_attributes = self.all_elements_df[['first_name', 'second_name', 'team',
                                                                  'selected_by_percent', 'value_season', 'minutes',
                                                                  'goals_scored', 'assists', 'clean_sheets',
                                                                  'own_goals', 'penalties_saved', 'penalties_missed',
                                                                  'saves', 'element_type', 'yellow_cards', 'red_cards',
                                                                  'bonus', 'transfers_in', 'total_points']]

            # Map the position of the player to a new column using the element types dataframe
            self.useful_player_attributes.insert(
                3, 'position',
                self.useful_player_attributes['element_type'].map(self.element_types_df.set_index('id').singular_name))
            # Drop the element type column as it is not needed anymore
            self.useful_player_attributes = self.useful_player_attributes.drop(['element_type'], axis=1)

            # Map the team of the player using the teams dataframe
            self.useful_player_attributes.insert(
                4, 'team_name', self.useful_player_attributes.team.map(self.teams_df.set_index('id').name))
            # Drop the team column as it is not needed anymore
            self.useful_player_attributes = self.useful_player_attributes.drop(['team'], axis=1)

            # Make a new column for value_season to guarantee float type of values in order to sort the df using it
            self.useful_player_attributes.insert(5, 'value', self.useful_player_attributes.value_season.astype(float))
            # Drop the value_season column as it is not needed anymore
            self.useful_player_attributes = self.useful_player_attributes.drop(['value_season'], axis=1)
        except Exception as e:
            self.main_window.set_response_display_text("An error has occurred while trying to process the data. "
                                                       "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to process the data.", exc_info=True)
        else:
            self.main_window.set_response_display_text("Data has been processed successfully.")
            self.main_window.most_vfm_players_button.setDisabled(False)

    def display_most_vfm_players(self):
        try:
            # Find the most vfm players (most points per cost - value = points / cost)
            self.most_vfm_players = self.useful_player_attributes.sort_values('value', ascending=False)
            self.model = m.PandasModel(self.most_vfm_players)
        except Exception as e:
            self.main_window.set_response_display_text("An error has occurred while trying to calculate the data. "
                                                       "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to calculate the data.", exc_info=True)
        else:
            self.main_window.set_table_view(self.model)
            self.main_window.set_response_display_text("Most Valuable For Money Players shown below.")
