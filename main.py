import logging
import sys

from PyQt5.QtWidgets import QApplication

import FPLViewer as v
import FPLController as c


def main():
    # Logging setup
    logging.basicConfig(filename='fpl_app.log', level=logging.DEBUG, filemode='w',
                        format='%(asctime)s: %(filename)s: %(lineno)d: %(funcName)s: %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    # Application run
    try:
        app = QApplication(sys.argv)

        stylesheet = """
            MainWindow{
                background-image: url('media/background.jpg');
                background-repeat: no-repeat;
                background-position: center;
                }
        """

        app.setStyleSheet(stylesheet)

        my_main_window = v.MainWindow()
        my_controller = c.Controller(my_main_window)

        my_main_window.show()

        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application has failed. Error is shown below:", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
