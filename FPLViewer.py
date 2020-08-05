"""
    FPLViewer.py
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QTableView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QPushButton


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('FPL Statistics Python APP')
        self.setFixedSize(1024, 768)
        self.menu = self.menuBar().addMenu("&Options")

        self._general_layout = QVBoxLayout()
        self._central_widget = QWidget(self)
        self.setCentralWidget(self._central_widget)
        self._central_widget.setLayout(self._general_layout)

        self._buttons_layout1 = QGridLayout()
        self._create_download_database_button()
        self._create_process_data_button()
        self._general_layout.addLayout(self._buttons_layout1)

        self._buttons_layout2 = QGridLayout()
        self._create_most_vfm_players_button()
        self._general_layout.addLayout(self._buttons_layout2)

        self._create_status_display()
        self._create_table_view()

    def _create_status_display(self):
        self._response_display = QTextEdit()
        self._response_display.setAcceptRichText(True)
        self._response_display.setFixedHeight(40)
        self._response_display.setFixedWidth(400)
        self._response_display.setReadOnly(True)
        self._general_layout.addWidget(self._response_display, alignment=Qt.AlignLeft)

    def _create_download_database_button(self):
        self.download_database_button = QPushButton('Download Database')
        self.download_database_button.setFixedSize(120, 40)
        self._buttons_layout1.addWidget(self.download_database_button, 0, 0)

    def _create_process_data_button(self):
        self.process_data_button = QPushButton('Process Data')
        self.process_data_button.setFixedSize(120, 40)
        self._buttons_layout1.addWidget(self.process_data_button, 0, 1)
        self.process_data_button.setDisabled(True)

    def _create_most_vfm_players_button(self):
        self.most_vfm_players_button = QPushButton('Calculate most \nVFM players.')
        self.most_vfm_players_button.setFixedSize(120, 40)
        self._buttons_layout2.addWidget(self.most_vfm_players_button, 0, 0)
        self.most_vfm_players_button.setDisabled(True)

    def _create_table_view(self):
        self.table_view = QTableView()
        self.table_view.resize(800, 600)
        self._general_layout.addWidget(self.table_view)

    def set_table_view(self, data):
        self.table_view.setModel(data)

    def set_response_display_text(self, text):
        self._response_display.setText(text)
        self._response_display.setAlignment(Qt.AlignCenter)
        self._response_display.setFocus()
