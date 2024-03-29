"""
Source file that holds the viewer of the application. All the GUI elements are structured here and ready to
be picked up and used by the controller.

Classes in the source file:
    * :func:`MainWindow`: Class that holds the main window used in the application's GUI.

"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QGridLayout, QTableView, QFileDialog, QComboBox, QLabel,
                             QVBoxLayout, QWidget, QLCDNumber, QPushButton, QDialog)

import FPLModel


class MainWindow(QMainWindow):
    """
    Class that holds the main window used in the application's GUI.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Create main window
        self.setWindowTitle('FPL Statistics Python APP')
        self.setMinimumSize(1366, 768)
        self.menu = self.menuBar().addMenu("&Options")

        # Specify the general layout and central widget
        self._general_layout = QVBoxLayout()
        self._central_widget = QWidget(self)
        self.setCentralWidget(self._central_widget)
        self._central_widget.setLayout(self._general_layout)

        # Add the button for db download and data processing
        self._buttons_layout1 = QGridLayout()
        self._create_download_database_button()
        self._create_process_data_button()

        # Instantiate the status display
        self._create_response_display()
        self._general_layout.addLayout(self._buttons_layout1)

        # Add the information bar
        self._create_info_bar()

        # Create the tab widget
        self._tab_widget = QTabWidget(self)
        self._general_layout.addWidget(self._tab_widget)

        # Set tab 1 structure
        self._tab_1_central_widget = QWidget()
        self._tab_1_general_layout = QVBoxLayout()
        self._tab_1_central_widget.setLayout(self._tab_1_general_layout)
        self._tab_widget.addTab(self._tab_1_central_widget, 'Statistics')

        # Set tab 2 structure
        self._tab_2_central_widget = QWidget()
        self._tab_2_general_layout = QVBoxLayout()
        self._tab_2_central_widget.setLayout(self._tab_2_general_layout)
        self._tab_widget.addTab(self._tab_2_central_widget, ' Best 15 Selection')

        # Set tab 1 content
        # Create the grid for calculations
        self._buttons_layout1_tab1 = QGridLayout()
        self._create_show_player_statistics_button()
        self._create_sort_by_label()
        self._create_select_sort_value_button()
        self._create_most_valuable_position_button()
        self._create_most_valuable_teams_button()
        self._tab_1_general_layout.addLayout(self._buttons_layout1_tab1)

        # Instantiate the table view
        self._create_table_view()

        # Add the buttons for saving the dataframes
        self._buttons_layout2_tab1 = QGridLayout()
        self._create_save_useful_player_attributes_df_to_csv_button()
        self._create_save_df_for_view_to_csv_button()
        self._tab_1_general_layout.addLayout(self._buttons_layout2_tab1)

        # Set tab 2 content
        # Create the grid for the content
        self._buttons_layout1_tab2 = QGridLayout()
        self._create_find_best_15_label()
        self._create_select_best_15_value_button()
        self._tab_2_general_layout.addLayout(self._buttons_layout1_tab2)

        # Create the players template
        self._best15_players_layout = QVBoxLayout()
        self._best15_players_stat_names_labels = list()
        self._best15_players_stat_values_labels = list()
        self._best15_players_player_labels = list()
        self._best15_players_grid = QGridLayout()
        self._instantiate_best15_players_template()

        # Set the dialog layout
        self._tab_2_general_layout.addLayout(self._best15_players_layout)

        # Add the file dialog for choosing the save directory
        self.dialog = QFileDialog()

    def _create_info_bar(self):
        """Creates the information bar of the main window."""
        self._info_layout = QGridLayout()
        self._gameweek_label = QLabel("We are currently in Gameweek:")
        self._gameweek_label.setAlignment(Qt.AlignCenter)
        self._gameweek_label.setStyleSheet("background-color: rgb(2,137,78)")
        self._gameweek_label.setFixedHeight(60)
        self._gameweek_lcd = QLCDNumber()
        self._gameweek_lcd.setFixedHeight(60)
        self._deadline_label = QLabel("Next Deadline Date:")
        self._deadline_label.setAlignment(Qt.AlignCenter)
        self._deadline_label.setStyleSheet("background-color: rgb(2,137,78)")
        self._deadline_label.setFixedHeight(60)
        self._deadline_display = QLabel()
        self._deadline_display.setStyleSheet("background-color: rgb(2,137,78)")
        self._deadline_display.setFixedHeight(60)
        self._info_layout.addWidget(self._gameweek_label, 0, 0)
        self._info_layout.addWidget(self._gameweek_lcd, 0, 1)
        self._info_layout.addWidget(self._deadline_label, 0, 2)
        self._info_layout.addWidget(self._deadline_display, 0, 3)
        self._general_layout.addLayout(self._info_layout)

    def set_info_displays(self, gw, deadline):
        """
        Creates the information display of the main window.
        :param gw: 
        :param deadline: 

        """
        self._gameweek_lcd.display(gw)
        self._deadline_display.setText(deadline)

    def _create_response_display(self):
        """Creates the response display of the main window. """
        self.status_bar_label = QLabel()
        self.status_bar_label.setFixedHeight(40)
        self.status_bar_label.setStyleSheet("background-color: rgb(2,137,78)")
        self.status_bar_label.setText("Ready...")
        self._buttons_layout1.addWidget(self.status_bar_label, 0, 2, 1, 3)

    def _create_download_database_button(self):
        """Creates the download database button of the main window. """
        self.download_database_button = QPushButton('Download Database')
        self.download_database_button.setFixedSize(180, 40)
        self._buttons_layout1.addWidget(self.download_database_button, 0, 0)

    def _create_process_data_button(self):
        """Creates the process data button of the main window. """
        self.process_data_button = QPushButton('Process Data')
        self.process_data_button.setFixedSize(120, 40)
        self._buttons_layout1.addWidget(self.process_data_button, 0, 1)
        self.process_data_button.setDisabled(True)

    def _create_show_player_statistics_button(self):
        """Creates the show player statistics button of the main window. """
        self.show_player_statistics_button = QPushButton("Show player \nstatistics")
        self.show_player_statistics_button.setFixedSize(140, 60)
        self._buttons_layout1_tab1.addWidget(self.show_player_statistics_button, 1, 0)
        self.show_player_statistics_button.setDisabled(True)

    def _create_sort_by_label(self):
        """Creates the sort by label of the main window. """
        self.sort_by_label = QLabel()
        self.sort_by_label.setText("<font color='black'>Sort by:</font>")
        self.sort_by_label.setAlignment(Qt.AlignBottom)
        self.sort_by_label.setFixedSize(140, 25)
        self._buttons_layout1_tab1.addWidget(self.sort_by_label, 0, 1)

    def _create_select_sort_value_button(self):
        """Creates the select sort value button of the main window. """
        self.select_sort_value_button = QComboBox()
        self.select_sort_value_button.setFixedSize(140, 60)
        self._buttons_layout1_tab1.addWidget(self.select_sort_value_button, 1, 1)
        self.select_sort_value_button.setDisabled(True)

    def _create_find_best_15_label(self):
        """Creates the find best 15 label of the main window. """
        self.find_best_15_label = QLabel()
        self.find_best_15_label.setText("<font color='black'>Obj.Target:</font>")
        self.find_best_15_label.setWordWrap(True)
        self.find_best_15_label.setAlignment(Qt.AlignBottom)
        self.find_best_15_label.setFixedSize(140, 25)
        self._buttons_layout1_tab2.addWidget(self.find_best_15_label)

    def _create_select_best_15_value_button(self):
        """Creates the select best 15 value button of the main window. """
        self.select_best_15_value_button = QComboBox()
        self.select_best_15_value_button.setFixedSize(140, 60)
        self._buttons_layout1_tab2.addWidget(self.select_best_15_value_button)
        self.select_best_15_value_button.setDisabled(True)

    def _create_most_valuable_position_button(self):
        """Creates the most valuable position button of the main window. """
        self.most_valuable_position_button = QPushButton('Calculate most \nValuable Position')
        self.most_valuable_position_button.setFixedSize(140, 60)
        self._buttons_layout1_tab1.addWidget(self.most_valuable_position_button, 1, 3)
        self.most_valuable_position_button.setDisabled(True)

    def _create_most_valuable_teams_button(self):
        """Creates the most valuable teams button of the main window. """
        self.most_valuable_teams_button = QPushButton('Calculate most \nValuable Teams')
        self.most_valuable_teams_button.setFixedSize(140, 60)
        self._buttons_layout1_tab1.addWidget(self.most_valuable_teams_button, 1, 4)
        self.most_valuable_teams_button.setDisabled(True)

    def _create_table_view(self):
        """Creates the table view of the main window. """
        self.table_view = QTableView()
        self.table_view.resize(800, 600)
        self._tab_1_general_layout.addWidget(self.table_view)

    def set_table_view(self, df):
        """
        Sets the dataframe model to the table view.

        :param df: Dataframe to be set to the table view

        """
        model = FPLModel.TableViewModel(df)
        self.table_view.setModel(model)

    def set_status_display_text(self, text):
        """
        Sets the display text to the status display.

        :param text: Text to be set to the status display.

        """
        self.status_bar_label.setText(text)
        self.status_bar_label.setFocus()

    def _create_save_useful_player_attributes_df_to_csv_button(self):
        """Creates the save useful player attributes df to csv button of the main window. """
        self.save_useful_player_attributes_df_to_csv = QPushButton('Save Original \nDataframe To CSV')
        self.save_useful_player_attributes_df_to_csv.setFixedSize(180, 60)
        self._buttons_layout2_tab1.addWidget(self.save_useful_player_attributes_df_to_csv, 0, 0)
        self.save_useful_player_attributes_df_to_csv.setDisabled(True)

    def _create_save_df_for_view_to_csv_button(self):
        """Creates the save df of table view to csv button of the main window. """
        self.save_df_for_view_to_csv = QPushButton('Save Current View \nDataframe To CSV')
        self.save_df_for_view_to_csv.setFixedSize(180, 60)
        self._buttons_layout2_tab1.addWidget(self.save_df_for_view_to_csv, 0, 1)
        self.save_df_for_view_to_csv.setDisabled(True)

    def _instantiate_best15_players_template(self):
        """Instantiates the players template of the best 15 selection with default data."""
        gks = [f"Player {i}" for i in range(1, 3)]
        defs = [f"Player {i}" for i in range(3, 8)]
        mfs = [f"Player {i}" for i in range(8, 13)]
        fwds = [f"Player {i}" for i in range(13, 16)]
        stats = {f"Stat {i}": f"Value {i}" for i in range(1, 5)}

        players = gks + defs + mfs + fwds

        # Create the stats labels
        stat_counter = 0
        for stat, value in stats.items():
            stat_label = QLabel(stat)
            stat_label.setAlignment(Qt.AlignCenter)
            stat_label.setFixedHeight(40)
            stat_label.setStyleSheet(
                """
                background-color: grey;
                font-size: 24px;
                """)
            value_label = QLabel(f"{value}")
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setFixedHeight(40)
            value_label.setStyleSheet(
                """
                background-color: grey;
                font-size: 24px;
                """)
            self._best15_players_stat_names_labels.append(stat_label)
            self._best15_players_stat_values_labels.append(value_label)
            self._best15_players_grid.addWidget(stat_label, 0, stat_counter)
            self._best15_players_grid.addWidget(value_label, 1, stat_counter)
            stat_counter += 1

        # Create the player labels
        player_labels = dict()
        for player in players:
            player_name = player.replace(" ", "\n")
            player_labels[player] = QLabel(player_name)
            player_labels[player].setAlignment(Qt.AlignCenter)
            player_labels[player].setStyleSheet(
                """
                background-color: rgb(2,137,78);
                font-size: 24px;
                border-style: outset;
                border-width: 2px;
                border-radius: 15px;
                border-color: black;
                padding: 4px;
                """)
            self._best15_players_player_labels.append(player_labels[player])

        gk_counter = 1
        def_counter = 0
        mf_counter = 0
        fwd_counter = 1
        for player, label in player_labels.items():
            if player in gks:
                self._best15_players_grid.addWidget(label, 2, gk_counter)
                gk_counter += 2
            elif player in defs:
                self._best15_players_grid.addWidget(label, 3, def_counter)
                def_counter += 1
            elif player in mfs:
                self._best15_players_grid.addWidget(label, 4, mf_counter)
                mf_counter += 1
            elif player in fwds:
                self._best15_players_grid.addWidget(label, 5, fwd_counter)
                fwd_counter += 1

        self._best15_players_layout.addLayout(self._best15_players_grid)

    def set_best15_players_template(self, gks, defs, mfs, fwds, stats):
        """
        Sets the players and stats of the best 15 players template.

        :param gks: list of the goalkeepers
        :param defs: list of the defenders
        :param mfs: list of the midfielders
        :param fwds: list of the forwards
        :param stats: statistics of the optimisation
        """
        players = gks + defs + mfs + fwds

        # Set the stats labels
        for count, stat_label in enumerate(self._best15_players_stat_names_labels):
            stat_label.setText(str(list(stats.keys())[count]))
            self._best15_players_stat_values_labels[count].setText(str(list(stats.values())[count]))

        # Set the player labels
        for count, player_label in enumerate(self._best15_players_player_labels):
            player_label.setText(str(players[count]))
