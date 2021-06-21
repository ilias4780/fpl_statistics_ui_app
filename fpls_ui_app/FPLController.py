"""
Source file that holds the controller of the application. All the logic of the application and the use
of the GUI elements lies here.

Classes in the source file:
    * :func:`Controller`: Class that holds all the logic of the application and the manipulation of the GUI elements
        that the :mod:`FPLViewer` source file holds.
"""

import datetime
import json
import logging
import os

import numpy as np
import pandas as pd
import requests

import best_15_optimisation as opt
from FPLViewer import Best15PopUp


class Controller(object):
    """
    Class that holds all the logic of the application and the manipulation of the GUI elements
    that the :mod:`FPLViewer` source file holds.
    """

    def __init__(self, main_window):
        self.logger = logging.getLogger(__name__)
        self.main_window = main_window
        self.popup = None

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
                                    'bonus', 'selected_by_percent', 'transfer_diff', 'transfers_in', 'transfers_out']
        self.columns_for_optimisation = ['total_points', 'value', 'form', 'ict_index']

        # Populate the sort_value_button
        self.main_window.select_sort_value_button.addItems(self.columns_for_sorting)
        # Populate the find_best_15_button
        self.main_window.select_best_15_value_button.addItems(self.columns_for_optimisation)

        # Connections
        self.main_window.menu.addAction('&Save Database', self.save_database_to_file)
        self.main_window.menu.addAction('&Load Database from file', self.load_database_from_file)
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
        """
        Get the FPL database using the FPL's API.
        """
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
        """
        Extract the parts that we want to keep from the downloaded data and process them.
        """
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
            try:
                next_deadline = self.events_df['deadline_time'][current_gameweek_index+1]
                next_deadline_date = datetime.datetime.strptime(next_deadline, '%Y-%m-%dT%H:%M:%SZ')\
                    .strftime('%Y-%m-%d %H:%M:%S GMT')
            except KeyError:
                next_deadline_date = 'End of Season'
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

            # Cast ICT Index and Selected by Percent Columns to numeric, so that they can be sorted properly.
            self.useful_player_attributes[["ict_index", "selected_by_percent"]] = \
                self.useful_player_attributes[["ict_index", "selected_by_percent"]].apply(pd.to_numeric)

            # Make a new column for the transfer difference
            transfer_loc = self.useful_player_attributes.columns.get_loc("transfers_in")
            self.useful_player_attributes.insert(transfer_loc, "transfer_diff",
                                                 self.useful_player_attributes["transfers_in"] -
                                                 self.useful_player_attributes["transfers_out"])
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
        """
        Create a table view with the player statistics.
        """
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
        """
        Sort the table view with the player statistics.
        """
        if self.last_process not in ['MV_position', 'MV_teams', 'Best_15']:
            try:
                column_to_sort = self.main_window.select_sort_value_button.currentText()
                columns = self.useful_player_attributes.columns.tolist()
                column_to_sort_index = columns.index(column_to_sort)
                if column_to_sort == 'position':
                    columns.insert(2, columns.pop(column_to_sort_index))
                elif column_to_sort == 'team_name':
                    columns.insert(3, columns.pop(column_to_sort_index))
                else:
                    columns.insert(4, columns.pop(column_to_sort_index))
                self.df_for_view = self.useful_player_attributes.reindex(columns=columns).sort_values(
                    column_to_sort, ascending=False)
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
        """
        Create a table view with the most valuable positions.
        """
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
        """
        Create a table view with the most valuable teams.
        """
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
        """
        Calculate and display the best 15 players selection based on the criteria selected by the user.
        """
        try:
            value_to_use_for_optimisation = self.main_window.select_best_15_value_button.currentText()
            names = self.useful_player_attributes["first_name"] + ' ' + self.useful_player_attributes["second_name"]
            names = names.tolist()
            positions = self.useful_player_attributes["position"].tolist()
            values = self.useful_player_attributes[value_to_use_for_optimisation].tolist()
            prices = self.useful_player_attributes["now_cost"].tolist()
            teams = self.useful_player_attributes["team_name"].tolist()
            result_df, total_stats = opt.find_best_15_players_by_value(names, positions, values, prices, teams,
                                                                       value_to_use_for_optimisation)
            self.df_for_view = pd.concat([result_df, total_stats], ignore_index=True)
            gks, defs, mfs, fwds, stats = self.get_sep_data_from_results(result_df, total_stats)
        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to calculate the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to calculate the data.", exc_info=True)
        else:
            self.main_window.set_table_view(self.df_for_view)
            self.main_window.set_status_display_text("Best 15 successfully calculated.")
            self.main_window.save_df_for_view_to_csv.setDisabled(False)
            self.last_process = f'Best_15_{value_to_use_for_optimisation}'
            self.popup = Best15PopUp(gks, defs, mfs, fwds, stats)
            self.popup.exec()

    def save_useful_player_attributes_df_to_csv(self):
        """
        Save the useful player attributes dataframe to a CSV in a selected directory by the user.
        """
        try:
            selected_dir = str(self.main_window.dialog.getExistingDirectory(self.main_window, "Save Dataframe"))
            if selected_dir:
                self.useful_player_attributes.to_csv(os.path.join(selected_dir, 'FplStatistics.csv'))
                self.main_window.set_status_display_text("Data has been saved to a spreadsheet.")
            else:
                self.main_window.set_status_display_text("No directory has been selected.")

        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to save the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to save the data.", exc_info=True)

    def save_df_for_view_to_csv(self):
        """
        Save the table view dataframe to a CSV in a selected directory by the user.
        """
        try:
            selected_dir = str(self.main_window.dialog.getExistingDirectory(self.main_window, "Save Dataframe"))
            if selected_dir:
                filename = 'FplStatistics_' + self.last_process + '.csv'
                self.df_for_view.to_csv(os.path.join(selected_dir, filename))
                self.main_window.set_status_display_text("Data has been saved to a spreadsheet.")
            else:
                self.main_window.set_status_display_text("No directory has been selected.")

        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to save the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to save the data.", exc_info=True)

    def save_database_to_file(self):
        """
        Save the downloaded FPL data to a JSON in a selected directory by the user.
        """
        try:
            # Check if the data has been downloaded
            if self.fpl_database_in_json:
                selected_dir = str(self.main_window.dialog.getExistingDirectory(self.main_window, "Save Database"))
                if selected_dir:
                    with open(os.path.join(selected_dir, 'FplData.json'), 'w') as f:
                        json.dump(self.fpl_database_in_json, f, indent=4)
                    self.main_window.set_status_display_text("Database has been saved to a file.")
                else:
                    self.main_window.set_status_display_text("No directory has been selected.")
            else:
                self.main_window.set_status_display_text("Data has not yet been downloaded.")
        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to save the Database. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to save the data.", exc_info=True)

    def load_database_from_file(self):
        """
        Load Offline the FPL data from a JSON file selected by the user.
        """
        try:
            selected_file = self.main_window.dialog.getOpenFileName(self.main_window.dialog,
                                                                    "Load database",
                                                                    "C:\\",
                                                                    "JSON files (*.json)")[0]
            if selected_file:
                with open(selected_file, 'r') as f:
                    self.fpl_database_in_json = json.load(f)
                self.main_window.set_status_display_text("Database has been loaded from file successfully.")
                self.main_window.process_data_button.setDisabled(False)
            else:
                self.main_window.set_status_display_text("No file has been selected.")

        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to load the database "
                                                     "from file. Please consult the log for details.")
            self.logger.error("An error has occurred while trying to load the database.", exc_info=True)

    @staticmethod
    def get_sep_data_from_results(results, statistics):
        """
        Separate the results returned by the optimization and bring it in a format suitable for
        display.

        :param results: pandas dataframe containing the results of the optimization
        :param statistics: pandas dataframe containing the statistics of the optimization process

        :returns: lists containing the goalkeepers, defenders, midfielders and forwards returned by the
            optimization, plus a list containing the statistics of the optimization process

        """

        gks = results['player'].loc[results['position'] == "Goalkeeper"].tolist()
        defs = results['player'].loc[results['position'] == "Defender"].tolist()
        mfs = results['player'].loc[results['position'] == "Midfielder"].tolist()
        fwds = results['player'].loc[results['position'] == "Forward"].tolist()
        stats_names = statistics.loc[0].tolist()
        stats_values = statistics.loc[1].tolist()
        stats = dict()
        for count, item in enumerate(stats_names):
            stats[item] = stats_values[count]

        return gks, defs, mfs, fwds, stats
