import time
import cv2
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGridLayout, QGroupBox, QSpinBox, QLineEdit, QCheckBox, \
    QHBoxLayout


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()

        self.thread_active = True
        self.detecting_shapes = False
        self.parameters = []

    def run(self):
        cap = cv2.VideoCapture(0)
        while self.thread_active:
            ret, cv_img = cap.read()
            if ret:
                if self.detecting_shapes:
                    cv_img = self.perform_shape_detection(cv_img, self.parameters)
                self.change_pixmap_signal.emit(cv_img)

    def perform_shape_detection(self, image, parameters):

        cv_img = image
        largest_contour = []

        if len(cv_img.shape) == 3:
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv_img
        ret, thresh = cv2.threshold(gray, parameters[7], 255, 0)

        if parameters[6]:
            thresh = np.invert(thresh)

        contours, hierarchy = cv2.findContours(thresh, 1, 2)

        for cnt in contours:
            if len(largest_contour) == 0:
                largest_contour = cnt
            if cv2.arcLength(cnt, False) > cv2.arcLength(largest_contour, False):
                largest_contour = cnt

        if parameters[1]:
            cv_img = cv2.Canny(cv_img, parameters[3], parameters[4], parameters[5])

        if parameters[5]:
            cv_img = thresh

        if parameters[0]:
            if len(cv_img.shape) == 2:
                cv_img = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
            cv_img = cv2.drawContours(cv_img, [largest_contour], -1, (0, 0, 255), 3)

        return cv_img

    def stop(self):
        self.thread_active = False


class CameraViewPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.thread = VideoThread()

        self.camera_view_box = QGroupBox("Camera View")
        self.camera_view_box.layout = QGridLayout()

        self.display_width = 1280 * 0.8
        self.display_height = 960 * 0.8
        # create the label that holds the image
        self.image_label = QLabel("No Camera Connected")
        self.image_label.resize(self.display_width, self.display_height)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.image = []

        self.camera_settings_box = QGroupBox("Imaging Controls")
        self.camera_settings_box.setFixedHeight(80)
        self.camera_settings_box.layout = QHBoxLayout()

        self.show_crosshairs_check = QCheckBox("Show Crosshairs  ")
        self.flip_h_check = QCheckBox("Flip Horizontal  ")
        self.flip_v_check = QCheckBox("Flip Vertical  ")

        self.capture_button = QPushButton("Capture Frame")
        self.capture_button.clicked.connect(self.capture_frame_pressed)

        self.camera_settings_box.layout.setSpacing(40)
        self.camera_settings_box.layout.addWidget(self.show_crosshairs_check)
        self.camera_settings_box.layout.addWidget(self.flip_h_check)
        self.camera_settings_box.layout.addWidget(self.flip_v_check)
        self.camera_settings_box.layout.addStretch()
        self.camera_settings_box.layout.addWidget(self.capture_button)

        self.camera_settings_box.setLayout(self.camera_settings_box.layout)

        self.camera_view_box.layout.addWidget(self.image_label)
        self.camera_view_box.layout.addWidget(self.camera_settings_box)

        self.start_thread()

        self.camera_view_box.setLayout(self.camera_view_box.layout)

    def start_thread(self):

        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        self.image = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def draw_crosshairs(self, img, binary_img=False):
        """
        Responsible for drawing a crosshair on the current image when called. Depending on whether shape detection is
        currently being performed or not, image may be binary, as indicated by the parameter 'binary_img'. If so draw
        the crosshairs in white, else red

        :param img: Image in the form of np array on which the crosshairs will be drawn
        :type img: np.ndarray
        :param binary_img: Flag for whether shape detection is currently being performed, and thus image is binary.
                           If so draw the crosshairs in white, else red
        :returns: The same image as the img parameter, with the crosshairs overlaid in either white or red
        """

        # Co-ords for the end-points of the crosshairs
        pt1_vertical = (int(img.shape[1] / 2), 0)
        pt2_vertical = (int(img.shape[1] / 2), img.shape[0])
        pt1_horizontal = (0, int(img.shape[0] / 2))
        pt2_horizontal = (img.shape[1], int(img.shape[0] / 2))

        # If performing shape detection, and thus image is binary, draw the crosshairs in white, else red
        if binary_img:
            color = (255, 255, 255)
        else:
            color = (0, 0, 255)

        cv2.line(img, pt1_vertical, pt2_vertical, color, 1)
        cv2.line(img, pt1_horizontal, pt2_horizontal, color, 1)

        return img

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""

        # Check to see if the image is binary, or not. If binary, signal draw_crosshairs so the crosshairs can be
        # drawn in white, else red
        binary_img_check = False
        if len(cv_img.shape) is 2:
            binary_img_check = True

        if self.show_crosshairs_check.checkState():
            cv_img = self.draw_crosshairs(cv_img, binary_img=binary_img_check)

        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        # If flagged, flip the image across the vertical and/or horizontal axes, 1 or 0 in flip() indicates which axis
        if self.flip_h_check.checkState():
            rgb_image = cv2.flip(rgb_image, 1)
        if self.flip_v_check.checkState():
            rgb_image = cv2.flip(rgb_image, 0)

        # Convert to format for QPixmap
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)

        pixmap_img = QPixmap.fromImage(p)
        return pixmap_img

    def capture_frame_pressed(self):
        """
        When the capture frame button is pressed, write the current image in the camera view to disc, in the 'output'
        folder. Uses current timestring as filename to ensure no overwrite
        """
        if len(self.image) > 0:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            filename = "output/" + timestr + ".png"
            cv2.imwrite(filename, self.image)
