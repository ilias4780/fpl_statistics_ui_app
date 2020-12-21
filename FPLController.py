"""
    FPLController.py
"""

import datetime
import logging
import os

import numpy as np
import pandas as pd
import requests

import best_15_optimisation as opt


class Controller(object):

    def __init__(self, main_window):
        self.logger = logging.getLogger(__name__)
        self.main_window = main_window

        self.fpl_database_in_json = None
        self.all_elements_df = None
        self.element_types_df = None
        self.teams_df = None
        self.events_df = None
        self.useful_player_attributes = None
        self.columns_for_sorting = None
        self.df_for_view = None
        self.model = None
        self.last_process = None
        self.columns_for_sorting = ['total_points', 'now_cost', 'value', 'position', 'team_name', 'form', 'minutes',
                                    'ict_index', 'ict_index_rank', 'goals_scored', 'assists', 'clean_sheets',
                                    'bonus', 'selected_by_percent', 'transfers_in', 'transfers_out']
        self.columns_for_optimisation = ['total_points', 'value', 'form', 'ict_index']

        # Populate the sort_value_button
        self.main_window.select_sort_value_button.addItems(self.columns_for_sorting)
        # Populate the find_best_15_button
        self.main_window.select_best_15_value_button.addItems(self.columns_for_optimisation)

        # Connections
        self.main_window.menu.addAction('&Exit', self.main_window.close)
        self.main_window.download_database_button.clicked.connect(self.get_fpl_database_in_json)
        self.main_window.process_data_button.clicked.connect(self.process_data)
        self.main_window.show_player_statistics_button.clicked.connect(self.show_player_statistics)
        self.main_window.select_sort_value_button.activated.connect(self.display_sorted_statistics)
        self.main_window.select_best_15_value_button.activated.connect(self.calculate_best_15_players)
        self.main_window.most_valuable_position_button.clicked.connect(self.display_most_valuable_position)
        self.main_window.most_valuable_teams_button.clicked.connect(self.display_most_valuable_teams)
        self.main_window.save_useful_player_attributes_df_to_csv.clicked.connect(
            self.save_useful_player_attributes_df_to_csv)
        self.main_window.save_df_for_view_to_csv.clicked.connect(self.save_df_for_view_to_csv)

    def get_fpl_database_in_json(self):
        fpl_api_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        try:
            the_whole_db = requests.get(fpl_api_url)
        except requests.RequestException as e:
            self.main_window.set_status_display_text("An error has occurred while trying to download the database. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to download the database.", exc_info=True)
        else:
            self.fpl_database_in_json = the_whole_db.json()
            self.main_window.set_status_display_text("Database has been downloaded successfully.")
            self.main_window.process_data_button.setDisabled(False)

    def process_data(self):
        try:
            # Keep the data pieces that are needed for our application in pandas DataFrame format
            self.all_elements_df = pd.DataFrame(self.fpl_database_in_json['elements'])
            self.element_types_df = pd.DataFrame(self.fpl_database_in_json['element_types'])
            self.teams_df = pd.DataFrame(self.fpl_database_in_json['teams'])

            # Use events df to add interesting stats like current gw, most points etc
            self.events_df = pd.DataFrame(self.fpl_database_in_json['events'])
            current_gameweek_index = self.events_df['is_current'].idxmax()
            current_gameweek = current_gameweek_index + 1
            highest_current_score = self.events_df['highest_score'][current_gameweek_index]
            next_deadline = self.events_df['deadline_time'][current_gameweek_index+1]
            next_deadline_date = datetime.datetime.strptime(next_deadline, '%Y-%m-%dT%H:%M:%SZ')\
                .strftime('%Y-%m-%d %H:%M:%S GMT')
            current_most_captained_index = self.events_df['most_captained'][current_gameweek_index]
            current_most_captained = self.all_elements_df['second_name'][current_most_captained_index]
            #??current_most_selected = self.events_df['most_selected'][current_gameweek_index]
            current_most_transferred_in_index = self.events_df['most_transferred_in'][current_gameweek_index]
            current_most_transferred_in = self.all_elements_df['second_name'][current_most_transferred_in_index]

            # Keep the useful columns of the elements dataframe
            self.useful_player_attributes = self.all_elements_df[['second_name', 'first_name', 'team',
                                                                  'selected_by_percent', 'value_season', 'form',
                                                                  'minutes', 'ict_index', 'ict_index_rank',
                                                                  'goals_scored', 'assists', 'clean_sheets',
                                                                  'own_goals', 'penalties_saved', 'penalties_missed',
                                                                  'saves', 'element_type', 'yellow_cards', 'red_cards',
                                                                  'bonus', 'transfers_in', 'transfers_out', 'now_cost',
                                                                  'total_points']].copy()

            # Adjust the 'now_cost' column to show millions (by default instead of 5.5 shows 55)
            self.useful_player_attributes.loc[:, 'now_cost'] *= 0.1

            # TODO: self.all_elements_df[['chance_of_playing_this_round', 'chance_of_playing_next_round']]
            # TODO: divide total_points with minutes to find points per minute of play
            # TODO: find about cost_change_event, cost_change_event_fall, cost_change_start, cost_change_start_fall

            # Map the position of the player to a new column using the element types dataframe
            self.useful_player_attributes.insert(
                2, 'position',
                self.useful_player_attributes['element_type'].map(self.element_types_df.set_index('id').singular_name))
            # Drop the element type column as it is not needed anymore
            self.useful_player_attributes = self.useful_player_attributes.drop(['element_type'], axis=1)

            # Map the team of the player using the teams dataframe
            self.useful_player_attributes.insert(
                3, 'team_name', self.useful_player_attributes.team.map(self.teams_df.set_index('id').name))
            # Drop the team column as it is not needed anymore
            self.useful_player_attributes = self.useful_player_attributes.drop(['team'], axis=1)

            # Make a new column for value_season to guarantee float type of values in order to sort the df using it
            self.useful_player_attributes.insert(5, 'value', self.useful_player_attributes.value_season.astype(float))
            # Drop the value_season column as it is not needed anymore
            self.useful_player_attributes = self.useful_player_attributes.drop(['value_season'], axis=1)
        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to process the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to process the data.", exc_info=True)
        else:
            self.main_window.set_status_display_text("Data has been processed successfully.")
            self.main_window.set_info_displays(current_gameweek, next_deadline_date)
            # Turn on buttons
            self.main_window.show_player_statistics_button.setDisabled(False)
            self.main_window.select_best_15_value_button.setDisabled(False)
            self.main_window.most_valuable_position_button.setDisabled(False)
            self.main_window.most_valuable_teams_button.setDisabled(False)
            self.main_window.save_useful_player_attributes_df_to_csv.setDisabled(False)

    def show_player_statistics(self):
        try:
            self.df_for_view = self.useful_player_attributes
        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to calculate the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to calculate the data.", exc_info=True)
        else:
            # Turn on the sort_value_button
            self.main_window.select_sort_value_button.setDisabled(False)
            # Set the table view
            self.main_window.set_table_view(self.df_for_view)
            # Set the response display
            self.main_window.set_status_display_text("Player statistics are shown below.")
            # Turn on buttons
            self.main_window.save_df_for_view_to_csv.setDisabled(False)
            # Save name of last process for save to csv function
            self.last_process = 'show_stats'

    def display_sorted_statistics(self):
        if self.last_process not in ['MV_position', 'MV_teams', 'Best_15']:
            try:
                column_to_sort = self.main_window.select_sort_value_button.currentText()
                self.df_for_view = self.useful_player_attributes.sort_values(column_to_sort, ascending=False)
            except Exception as e:
                self.main_window.set_status_display_text("An error has occurred while trying to calculate the data. "
                                                         "Please consult the log for details.")
                self.logger.error("An error has occurred while trying to sort the statistics.", exc_info=True)
            else:
                # Set the table view
                self.main_window.set_table_view(self.df_for_view)
                # Save name of last process for save to csv function
                self.last_process = column_to_sort

    def display_most_valuable_position(self):
        try:
            # Find which position provides the most value when players with zero value are not considered
            useful_player_attributes_no_zeros = \
                self.useful_player_attributes.loc[self.useful_player_attributes.value > 0]
            pivot = \
                useful_player_attributes_no_zeros.pivot_table(index='position', values='value',
                                                              aggfunc=np.mean).reset_index()
            pivot['value'] = pivot['value'].round(decimals=2)
            self.df_for_view = pivot.sort_values('value', ascending=False)
        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to calculate the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to calculate the data.", exc_info=True)
        else:
            self.main_window.set_table_view(self.df_for_view)
            self.main_window.set_status_display_text("Most Valuable Position shown below.")
            self.main_window.save_df_for_view_to_csv.setDisabled(False)
            self.last_process = 'MV_position'

    def display_most_valuable_teams(self):
        try:
            # Find which teams provide the most value when players with zero value are not considered
            useful_player_attributes_no_zeros = \
                self.useful_player_attributes.loc[self.useful_player_attributes.value > 0]
            team_pivot = \
                useful_player_attributes_no_zeros.pivot_table(index='team_name', values='value',
                                                              aggfunc=np.mean).reset_index()
            team_pivot['value'] = team_pivot['value'].round(decimals=2)
            self.df_for_view = team_pivot.sort_values('value', ascending=False)
        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to calculate the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to calculate the data.", exc_info=True)
        else:
            self.main_window.set_table_view(self.df_for_view)
            self.main_window.set_status_display_text("Most Valuable Teams shown below.")
            self.main_window.save_df_for_view_to_csv.setDisabled(False)
            self.last_process = 'MV_teams'

    def calculate_best_15_players(self):
        try:
            value_to_use_for_optimisation = self.main_window.select_best_15_value_button.currentText()
            names = self.useful_player_attributes["first_name"] + ' ' + self.useful_player_attributes["second_name"]
            names = names.tolist()
            positions = self.useful_player_attributes["position"].tolist()
            values = self.useful_player_attributes[value_to_use_for_optimisation].tolist()
            prices = self.useful_player_attributes["now_cost"].tolist()
            self.df_for_view = opt.find_best_15_players_by_value(names, positions, values, prices,
                                                                 value_to_use_for_optimisation)
        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to calculate the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to calculate the data.", exc_info=True)
        else:
            self.main_window.set_table_view(self.df_for_view)
            self.main_window.set_status_display_text("Best 15 successfully calculated.")
            self.main_window.save_df_for_view_to_csv.setDisabled(False)
            self.last_process = f'Best_15_{value_to_use_for_optimisation}'

    def save_useful_player_attributes_df_to_csv(self):
        try:
            selected_dir = str(self.main_window.dialog.getExistingDirectory(self.main_window, "Save Dataframe"))
            self.useful_player_attributes.to_csv(os.path.join(selected_dir, 'FplStatistics.csv'))
        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to save the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to save the data.", exc_info=True)
        else:
            self.main_window.set_status_display_text("Data has been saved to a spreadsheet.")

    def save_df_for_view_to_csv(self):
        try:
            selected_dir = str(self.main_window.dialog.getExistingDirectory(self.main_window, "Save Dataframe"))
            filename = 'FplStatistics_' + self.last_process + '.csv'
            self.df_for_view.to_csv(os.path.join(selected_dir, filename))
        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to save the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to save the data.", exc_info=True)
        else:
            self.main_window.set_status_display_text("Data has been saved to a spreadsheet.")
