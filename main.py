import logging
import sys

from PyQt5.QtWidgets import QApplication

import FPLViewer
import FPLController


def main():
    # Logging setup
    logging.basicConfig(filename='fpl_app.log', level=logging.DEBUG, filemode='w',
                        format='%(asctime)s: %(filename)s: %(lineno)d: %(funcName)s: %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    # Application run
    try:
        app = QApplication(sys.argv)
        logger.debug('Application has started successfully.')

        stylesheet = """
            MainWindow{
                background-color: rgb(55,0,60)
            }
            QTableView{ 
                background-color: rgb(2,137,78);
                font-size: 18px
            }
            QPushButton{
                background-color: rgb(2,137,78);
                font-size: 16px;
                border-style: outset;
                border-width: 2px;
                border-radius: 15px;
                border-color: black;
                padding: 4px;
            }
            QLabel{
                font-size: 18px
            }
            QComboBox{
                background-color: rgb(2,137,78);
                font-size: 16px;
                border-style: outset;
                border-width: 2px;
                border-radius: 15px;
                border-color: black;
                padding: 4px;
            }
        """

        app.setStyleSheet(stylesheet)

        main_window = FPLViewer.MainWindow()
        controller = FPLController.Controller(main_window)

        main_window.show()

        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application has failed. Error is shown below:", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
