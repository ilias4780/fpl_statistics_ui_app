"""
    FPLModel.py
"""

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QAbstractTableModel


class TableViewModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        # Pandas .shape() returns a tuple representing the dimensionality of the DataFrame.
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        # Pandas .shape() returns a tuple representing the dimensionality of the DataFrame.
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None
