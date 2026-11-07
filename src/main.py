import signal
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from src.common.constants import APP_NAME
from src.gui.main_window import MainWindow


def main() -> None:
    # Allow terminal Ctrl+C (SIGINT) to cleanly exit the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # Timer allowing Python interpreter to run periodically to process OS signals
    sig_timer = QTimer()
    sig_timer.start(200)
    sig_timer.timeout.connect(lambda: None)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
