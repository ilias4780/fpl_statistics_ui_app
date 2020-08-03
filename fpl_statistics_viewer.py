"""
    fpl_statistics_viewer.py
"""
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QGridLayout
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

        self.general_layout = QVBoxLayout()
        self._central_widget = QWidget(self)
        self.setCentralWidget(self._central_widget)
        self._central_widget.setLayout(self.general_layout)

        self.buttons_layout = QGridLayout()
        self._create_download_database_button()
        self._create_process_data_button()
        self.general_layout.addLayout(self.buttons_layout)

        self._create_status_display()

    def _create_status_display(self):
        self.response_display = QTextEdit()
        self.response_display.setAcceptRichText(True)
        self.response_display.setFixedHeight(40)
        self.response_display.setFixedWidth(400)
        self.response_display.setReadOnly(True)
        self.general_layout.addWidget(self.response_display, alignment=Qt.AlignLeft)

    def _create_download_database_button(self):
        self.download_database_button = QPushButton('Download Database')
        self.download_database_button.setFixedSize(120, 40)
        self.buttons_layout.addWidget(self.download_database_button, 0, 0)

    def _create_process_data_button(self):
        self.process_data_button = QPushButton('Process Data')
        self.process_data_button.setFixedSize(120, 40)
        self.buttons_layout.addWidget(self.process_data_button, 0, 1)
        self.process_data_button.setDisabled(True)

    def set_response_display_text(self, text):
        self.response_display.setText(text)
        self.response_display.setAlignment(Qt.AlignCenter)
        self.response_display.setFocus()
