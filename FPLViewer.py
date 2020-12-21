"""
    FPLViewer.py
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QTableView, QFileDialog, QComboBox, QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLCDNumber
from PyQt5.QtWidgets import QPushButton

import FPLModel


class MainWindow(QMainWindow):

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

        # Create the grid for calculations
        self._buttons_layout2 = QGridLayout()
        self._create_show_player_statistics_button()
        self._create_sort_by_label()
        self._create_select_sort_value_button()
        self._create_find_best_15_label()
        self._create_select_best_15_button_value()
        self._create_most_valuable_position_button()
        self._create_most_valuable_teams_button()
        self._general_layout.addLayout(self._buttons_layout2)

        # Instantiate the table view
        self._create_table_view()

        # Add the buttons for saving the dataframes
        self._buttons_layout3 = QGridLayout()
        self._create_save_useful_player_attributes_df_to_csv()
        self._create_save_df_for_view_to_csv()
        self._general_layout.addLayout(self._buttons_layout3)

        # Add the file dialog for choosing the save directory
        self.dialog = QFileDialog()

    def _create_info_bar(self):
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
        self._gameweek_lcd.display(gw)
        self._deadline_display.setText(deadline)

    def _create_response_display(self):
        self.status_bar_label = QLabel()
        self.status_bar_label.setFixedHeight(40)
        self.status_bar_label.setStyleSheet("background-color: rgb(2,137,78)")
        self.status_bar_label.setText("Ready...")
        self._buttons_layout1.addWidget(self.status_bar_label, 0, 2, 1, 3)

    def _create_download_database_button(self):
        self.download_database_button = QPushButton('Download Database')
        self.download_database_button.setFixedSize(180, 40)
        self._buttons_layout1.addWidget(self.download_database_button, 0, 0)

    def _create_process_data_button(self):
        self.process_data_button = QPushButton('Process Data')
        self.process_data_button.setFixedSize(120, 40)
        self._buttons_layout1.addWidget(self.process_data_button, 0, 1)
        self.process_data_button.setDisabled(True)

    def _create_show_player_statistics_button(self):
        self.show_player_statistics_button = QPushButton("Show player \nstatistics")
        self.show_player_statistics_button.setFixedSize(140, 60)
        self._buttons_layout2.addWidget(self.show_player_statistics_button, 1, 0)
        self.show_player_statistics_button.setDisabled(True)

    def _create_sort_by_label(self):
        self.sort_by_label = QLabel()
        self.sort_by_label.setText("<font color='white'>Sort by:</font>")
        self.sort_by_label.setAlignment(Qt.AlignBottom)
        self.sort_by_label.setFixedSize(140, 60)
        self._buttons_layout2.addWidget(self.sort_by_label, 0, 1)

    def _create_select_sort_value_button(self):
        self.select_sort_value_button = QComboBox()
        self.select_sort_value_button.setFixedSize(140, 60)
        self._buttons_layout2.addWidget(self.select_sort_value_button, 1, 1)
        self.select_sort_value_button.setDisabled(True)

    def _create_find_best_15_label(self):
        self.find_best_15_label = QLabel()
        self.find_best_15_label.setText("<font color='white'>Find best 15 based on:</font>")
        self.find_best_15_label.setWordWrap(True)
        self.find_best_15_label.setAlignment(Qt.AlignBottom)
        self.find_best_15_label.setFixedSize(140, 60)
        self._buttons_layout2.addWidget(self.find_best_15_label, 0, 2)

    def _create_select_best_15_button_value(self):
        self.select_best_15_value_button = QComboBox()
        self.select_best_15_value_button.setFixedSize(140, 60)
        self._buttons_layout2.addWidget(self.select_best_15_value_button, 1, 2)
        self.select_best_15_value_button.setDisabled(True)

    def _create_most_valuable_position_button(self):
        self.most_valuable_position_button = QPushButton('Calculate most \nValuable Position')
        self.most_valuable_position_button.setFixedSize(140, 60)
        self._buttons_layout2.addWidget(self.most_valuable_position_button, 1, 3)
        self.most_valuable_position_button.setDisabled(True)

    def _create_most_valuable_teams_button(self):
        self.most_valuable_teams_button = QPushButton('Calculate most \nValuable Teams')
        self.most_valuable_teams_button.setFixedSize(140, 60)
        self._buttons_layout2.addWidget(self.most_valuable_teams_button, 1, 4)
        self.most_valuable_teams_button.setDisabled(True)

    def _create_table_view(self):
        self.table_view = QTableView()
        self.table_view.resize(800, 600)
        self._general_layout.addWidget(self.table_view)

    def set_table_view(self, df):
        model = FPLModel.TableViewModel(df)
        self.table_view.setModel(model)

    def set_status_display_text(self, text):
        self.status_bar_label.setText(text)
        self.status_bar_label.setFocus()

    def _create_save_useful_player_attributes_df_to_csv(self):
        self.save_useful_player_attributes_df_to_csv = QPushButton('Save Original \nDataframe To CSV')
        self.save_useful_player_attributes_df_to_csv.setFixedSize(180, 80)
        self._buttons_layout3.addWidget(self.save_useful_player_attributes_df_to_csv, 0, 0)
        self.save_useful_player_attributes_df_to_csv.setDisabled(True)

    def _create_save_df_for_view_to_csv(self):
        self.save_df_for_view_to_csv = QPushButton('Save Current View \nDataframe To CSV')
        self.save_df_for_view_to_csv.setFixedSize(180, 80)
        self._buttons_layout3.addWidget(self.save_df_for_view_to_csv, 0, 1)
        self.save_df_for_view_to_csv.setDisabled(True)
