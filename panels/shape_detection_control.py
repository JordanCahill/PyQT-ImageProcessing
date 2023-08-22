import time

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QCheckBox, QSpinBox, QLabel, QRadioButton, QButtonGroup


class ShapeDetectionPanel(QObject):

    start_detection_signal = pyqtSignal(int)
    def __init__(self):

        super().__init__()


        self.shape_detection_box = QGroupBox("Shape Detection")
        self.shape_detection_box.layout = QGridLayout()

        self.perform_detection_check = QCheckBox("Perform Shape Detection")

        self.shape_detection_settings = QGroupBox()
        self.shape_detection_settings.layout = QGridLayout()

        self.show_canny_edges_check = QRadioButton("Show Canny Edges")
        self.show_thresh_img_check = QRadioButton("Show Threshold Image")
        self.canny_or_thresh_group = QButtonGroup()
        self.canny_or_thresh_group.addButton(self.show_canny_edges_check)
        self.canny_or_thresh_group.addButton(self.show_thresh_img_check)
        self.show_rectangles_check = QCheckBox("Show Detected Rectangles")
        self.canny_thresh_spinbox = QSpinBox()
        self.canny_thresh_spinbox.setMaximum(255)
        self.canny_thresh_spinbox.setValue(100)
        self.canny_max_spinbox = QSpinBox()
        self.canny_max_spinbox.setMaximum(255)
        self.canny_max_spinbox.setValue(150)
        self.hough_thresh_spinbox = QSpinBox()
        self.hough_thresh_spinbox.setValue(80)
        self.block_size_spinbox = QSpinBox()
        self.block_size_spinbox.setValue(7)
        self.ap_size_spinbox = QSpinBox()
        self.ap_size_spinbox.setValue(7)
        self.invert_binary_image_check = QCheckBox("Invert Threshold Image")
        self.invert_binary_image_check.setEnabled(False)
        self.invert_binary_image_check.setStyleSheet("margin-left:25px")
        self.binary_thresh_spinbox = QSpinBox()
        self.binary_thresh_spinbox.setMaximum(255)
        self.binary_thresh_spinbox.setValue(150)

        self.canny_thresh_label = QLabel("Canny Threshold")
        self.canny_thresh_label.setStyleSheet("margin-left:20px")
        self.canny_max_label = QLabel("Canny Max Value")
        self.canny_max_label.setStyleSheet("margin-left:20px")
        self.block_size_label = QLabel("Block Size (Px)")
        self.block_size_label.setStyleSheet("margin-left:20px")
        self.binary_thresh_label = QLabel("Binary Threshold")
        self.binary_thresh_label.setStyleSheet("margin-left:20px")

        #self.shape_detection_settings.layout.addWidget(self.canny_or_thresh_group, 0, 0, 1, 2)
        self.shape_detection_settings.layout.addWidget(self.show_rectangles_check, 0, 0, 1, 2)
        self.shape_detection_settings.layout.addWidget(self.show_canny_edges_check, 1, 0, 1, 2)

        self.shape_detection_settings.layout.addWidget(self.canny_thresh_label, 3, 0)
        self.shape_detection_settings.layout.addWidget(self.canny_thresh_spinbox, 3, 1)
        self.shape_detection_settings.layout.addWidget(self.canny_max_label, 4, 0)
        self.shape_detection_settings.layout.addWidget(self.canny_max_spinbox, 4, 1)
        self.shape_detection_settings.layout.addWidget(self.block_size_label, 5, 0)
        self.shape_detection_settings.layout.addWidget(self.block_size_spinbox, 5, 1)
        self.shape_detection_settings.layout.addWidget(self.show_thresh_img_check, 6, 0, 1, 2)
        self.shape_detection_settings.layout.addWidget(self.invert_binary_image_check, 7, 0, 1, 2)
        self.shape_detection_settings.layout.addWidget(self.binary_thresh_label, 8, 0)
        self.shape_detection_settings.layout.addWidget(self.binary_thresh_spinbox, 8, 1)

        self.shape_detection_settings.layout
        # self.shape_detection_settings.layout.addWidget(QLabel("Aperture Size (Px)"), 7, 0)
        # self.shape_detection_settings.layout.addWidget(self.ap_size_spinbox, 7, 1)

        self.shape_detection_settings.setLayout(self.shape_detection_settings.layout)

        self.perform_detection_check.setChecked(True)
        self.show_canny_edges_check.setChecked(True)

        self.perform_detection_check.stateChanged.connect(self.perform_detection_check_changed)
        self.show_canny_edges_check.toggled.connect(self.perform_detection_check_changed)
        self.show_thresh_img_check.toggled.connect(self.perform_detection_check_changed)
        self.show_rectangles_check.stateChanged.connect(self.perform_detection_check_changed)
        self.canny_thresh_spinbox.textChanged.connect(self.perform_detection_check_changed)
        self.canny_max_spinbox.textChanged.connect(self.perform_detection_check_changed)
        self.hough_thresh_spinbox.textChanged.connect(self.perform_detection_check_changed)
        self.block_size_spinbox.textChanged.connect(self.perform_detection_check_changed)
        self.ap_size_spinbox.textChanged.connect(self.perform_detection_check_changed)
        self.invert_binary_image_check.stateChanged.connect(self.perform_detection_check_changed)
        self.binary_thresh_spinbox.textChanged.connect(self.perform_detection_check_changed)

        self.shape_detection_box.layout.addWidget(self.shape_detection_settings, 1, 0)
        self.shape_detection_box.layout.addWidget(self.perform_detection_check, 0, 0)
        self.shape_detection_box.setLayout(self.shape_detection_box.layout)


    def perform_detection_check_changed(self):

        if self.show_thresh_img_check.isChecked():

            self.invert_binary_image_check.setEnabled(True)
            self.binary_thresh_label.setEnabled(True)
            self.binary_thresh_spinbox.setEnabled(True)

            self.canny_max_spinbox.setEnabled(False)
            self.canny_thresh_spinbox.setEnabled(False)
            self.block_size_spinbox.setEnabled(False)
            self.canny_max_label.setEnabled(False)
            self.canny_thresh_label.setEnabled(False)
            self.block_size_label.setEnabled(False)
        else:

            self.invert_binary_image_check.setEnabled(False)
            self.binary_thresh_label.setEnabled(False)
            self.binary_thresh_spinbox.setEnabled(False)

            self.canny_max_spinbox.setEnabled(True)
            self.canny_thresh_spinbox.setEnabled(True)
            self.block_size_spinbox.setEnabled(True)
            self.canny_max_label.setEnabled(True)
            self.canny_thresh_label.setEnabled(True)
            self.block_size_label.setEnabled(True)
        if self.perform_detection_check.checkState():
            self.shape_detection_settings.setEnabled(True)
            self.start_detection_signal.emit(1)

        else:
            self.shape_detection_settings.setDisabled(True)
            self.start_detection_signal.emit(0)
