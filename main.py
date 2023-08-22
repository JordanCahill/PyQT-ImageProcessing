"""This script is the main script of the application and designed to be called as __main__. In the interest of
readibility and modularity, each panel on the GUI is separated into its own module in the panels folder.

The majority of dependencies can be installed using pip, however the Spinnaker libraries need to be installed from a
wheel downloaded from their website"""

import sys
from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QGridLayout, QDesktopWidget

from panels.camera_viewer import CameraViewPanel
from panels.shape_detection_control import ShapeDetectionPanel


class App(QMainWindow):
    """ Main application class. Creates a AppContainer object which contains all the GUI widgets """

    def __init__(self):
        super().__init__()

        self.title = 'Shape Detector'
        self.setWindowIcon(QIcon("assets/logo.ico"))
        self.left = 0
        self.top = 0
        self.width = 400
        self.height = 500
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # If second monitor connected, open GUI on it
        monitor = QDesktopWidget().screenGeometry(1)
        if not monitor.isEmpty():
            self.move(monitor.left(), monitor.top())
            self.showFullScreen()

        self.application_container = AppContainer(self)
        self.setCentralWidget(self.application_container)

        self.show()


class AppContainer(QWidget):
    """
    A class containing all the application tabs, and underlying logic. On init, instantiates all widgets and connections
    """

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.layout = QGridLayout()

        # Instantiate the interface widgets
        self.shape_detection_settings = ShapeDetectionPanel()
        self.camera_view = CameraViewPanel()

        self.layout.addWidget(self.camera_view.camera_view_box, 0, 0, 2, 2)

        self.layout.addWidget(self.shape_detection_settings.shape_detection_box, 0, 2, 1, 1)

        self.setLayout(self.layout)

        # Listen for a pyqtSignal to start the shape detection algorithm
        self.shape_detection_settings.start_detection_signal.connect(self.update_shape_detection_signal_received)

        self.update_shape_detection_signal_received(1)  # Start detection on application open

    def update_shape_detection_signal_received(self, code):
        """ When a parameter in the shape detection panel is changed, it emits a signal to the main code to update
        the shape detection algorithm, taking the parameters from the panel. The parameters are then passed to the
        thread in the camera view object where shape detection is being implemented

        :param code: Should be 1 or 0; Indicates whether to start or stop detecting shapes
        """
        if code is 1:
            self.camera_view.thread.detecting_shapes = True
            parameters = [
                self.shape_detection_settings.show_rectangles_check.isChecked(),
                self.shape_detection_settings.show_canny_edges_check.isChecked(),
                self.shape_detection_settings.canny_thresh_spinbox.value(),
                self.shape_detection_settings.canny_max_spinbox.value(),
                self.shape_detection_settings.block_size_spinbox.value(),
                self.shape_detection_settings.show_thresh_img_check.isChecked(),
                self.shape_detection_settings.invert_binary_image_check.isChecked(),
                self.shape_detection_settings.binary_thresh_spinbox.value()]

            self.camera_view.thread.parameters = parameters

        else:
            self.camera_view.thread.detecting_shapes = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('styles/style.qss').read_text())
    ex = App()
    sys.exit(app.exec_())
