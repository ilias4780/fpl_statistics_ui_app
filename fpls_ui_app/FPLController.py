"""
Source file that holds the controller of the application. All the logic of the application and the use
of the GUI elements lies here.

Classes in the source file:
    * :func:`Controller`: Class that holds all the logic of the application and the manipulation of the GUI elements
        that the :mod:`FPLViewer` source file holds.
"""

import json
import logging
import os

import requests

import best_15_optimisation as opt
import data_handling as dh


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
        self.useful_player_attributes = None
        self.columns_for_sorting = None
        self.df_for_view = None
        self.model = None
        self.last_process = None
        self.columns_for_sorting = ['total_points', 'now_cost', 'value', 'position', 'team_name', 'form', 'minutes',
                                    'ict_index', 'ict_index_rank', 'goals_scored', 'assists', 'clean_sheets',
                                    'bonus', 'selected_by_percent', 'transfer_diff', 'transfers_in', 'transfers_out']
        self.columns_for_optimisation = ['total_points', 'value', 'form',
                                         'ict_index', 'selected_by_percent']

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
        Get the FPL database.
        """
        try:
            self.fpl_database_in_json = dh.get_fpl_database_in_json()
        except requests.RequestException as e:
            self.main_window.set_status_display_text("An error has occurred while trying to download the database. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to download the database.", exc_info=True)
        else:
            self.main_window.set_status_display_text("Database has been downloaded successfully.")
            self.main_window.process_data_button.setDisabled(False)

    def process_data(self):
        """
        Extract the parts that we want to keep from the downloaded data and process them.
        """
        try:
            current_gameweek, next_deadline_date, self.useful_player_attributes = (
                dh.process_data(self.fpl_database_in_json)
            )
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
            self.df_for_view = self.useful_player_attributes.drop('uid', axis=1)
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
                self.df_for_view = dh.sort_statistics_table(
                    self.useful_player_attributes.drop('uid', axis=1),
                    column_to_sort
                )
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
        Display a table view with the most valuable positions.
        """
        try:
            self.df_for_view = dh.calculate_most_valuable_position(self.useful_player_attributes)
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
        Display a table view with the most valuable teams.
        """
        try:
            self.df_for_view = dh.calculate_most_valuable_teams(self.useful_player_attributes)
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
            result_df, total_stats = opt.find_best_15_players_by_value(
                self.useful_player_attributes['uid'].tolist(),
                self.useful_player_attributes['position'].tolist(),
                self.useful_player_attributes[value_to_use_for_optimisation].tolist(),
                self.useful_player_attributes['now_cost'].tolist(),
                self.useful_player_attributes['team_name'].tolist(),
                value_to_use_for_optimisation
            )

            self.df_for_view, gks, defs, mfs, fwds, stats = opt.post_process_data(
                self.useful_player_attributes[['uid', 'name']].copy(),
                result_df,
                total_stats
            )
        except opt.OptimisationValuesAllZeroError:
            self.main_window.set_status_display_text("The values chosen to be used for optimisation "
                                                     "are all zero.")
            self.logger.warning("The values chosen to be used for optimisation are all zero.")
        except Exception as e:
            self.main_window.set_status_display_text("An error has occurred while trying to calculate the data. "
                                                     "Please consult the log for details.")
            self.logger.error("An error has occurred while trying to calculate the data.", exc_info=True)
        else:
            self.main_window.set_table_view(self.df_for_view)
            self.main_window.set_status_display_text("Best 15 successfully calculated.")
            self.main_window.save_df_for_view_to_csv.setDisabled(False)
            self.last_process = f'Best_15_{value_to_use_for_optimisation}'
            self.main_window.set_best15_players_template(gks, defs, mfs, fwds, stats)

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
