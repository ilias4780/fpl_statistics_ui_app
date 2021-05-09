"""
Source file that holds the table view model of the window.

Classes in the source file:
    * :func:`TableViewModel`: Class that holds all the logic of the application and the manipulation of the GUI elements
        that the :mod:`FPLViewer` source file holds.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QAbstractTableModel


class TableViewModel(QAbstractTableModel):
    """
    The table view model that is used by the application to display the various dataframes.
    """

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        """
        Return the row count of the dataframe to display.

        :param parent:  (Default value = None)

        """
        # Pandas .shape() returns a tuple representing the dimensionality of the DataFrame.
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        """
        Return the column count of the dataframe to display.

        :param parnet:  (Default value = None)

        """
        # Pandas .shape() returns a tuple representing the dimensionality of the DataFrame.
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
        Return the data according to index passed.

        :param index: 
        :param role:  (Default value = Qt.ItemDataRole.DisplayRole)

        """
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        """
        Return the header data.

        :param col: 
        :param orientation: 
        :param role: 

        """
        if orientation == Qt.Orientations.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]
        return None
