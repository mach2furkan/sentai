from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PyQt6.QtGui import QPixmap, QFont, QImage
from PyQt6.QtCore import pyqtSlot, Qt
import sys

from src.infrastructure.config import AppConfig
from src.infrastructure.video_source import OpenCVVideoSource
from src.infrastructure.detector import YoloDetector
from src.infrastructure.tracker import SortTracker
from src.application.services import VideoProcessingService, AnalysisService
from src.presentation.video_thread import VideoThread

class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self.setWindowTitle(config.window_title)
        self.setGeometry(100, 100, config.window_size[0], config.window_size[1])
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
        
        # Setup Backend
        self.video_source = OpenCVVideoSource(config.video_source)
        # Using medium model for better balance if available, else nano
        self.detector = YoloDetector(config.yolo_model_path) 
        self.tracker = SortTracker()
        self.analyzer = AnalysisService(config)
        self.service = VideoProcessingService(self.video_source, self.detector, self.tracker, self.analyzer)
        
        self.init_ui()
        
        # Thread
        self.thread = VideoThread(self.service)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.stats_signal.connect(self.update_stats)
        self.thread.start()

    def init_ui(self):
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left Side: Video
        self.image_label = QLabel(self)
        self.image_label.resize(1000, 720)
        self.image_label.setStyleSheet("border: 2px solid #444;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_label, stretch=3)
        
        # Right Side: Stats
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)
        
        # Title
        title = QLabel("SENTINEL AI")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ff00;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(title)
        
        # Stats Box
        stats_group = QGroupBox("Live Statistics")
        stats_group.setStyleSheet("QGroupBox { border: 1px solid gray; margin-top: 10px; font-weight: bold; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        stats_layout = QVBoxLayout()
        
        self.lbl_active_tracks = QLabel("Active People: 0")
        self.lbl_active_groups = QLabel("Active Groups: 0")
        self.lbl_fps = QLabel("FPS: 0.0")
        
        font = QFont("Arial", 14)
        self.lbl_active_tracks.setFont(font)
        self.lbl_active_groups.setFont(font)
        self.lbl_fps.setFont(font)
        
        stats_layout.addWidget(self.lbl_active_tracks)
        stats_layout.addWidget(self.lbl_active_groups)
        stats_layout.addWidget(self.lbl_fps)
        stats_group.setLayout(stats_layout)
        right_panel.addWidget(stats_group)
        
        # Logs / Alerts
        logs_group = QGroupBox("System Logs")
        self.lbl_logs = QLabel("System Ready...")
        self.lbl_logs.setWordWrap(True)
        self.lbl_logs.setStyleSheet("color: #aaa;")
        logs_layout = QVBoxLayout()
        logs_layout.addWidget(self.lbl_logs)
        logs_group.setLayout(logs_layout)
        right_panel.addWidget(logs_group)
        
        right_panel.addStretch()
        main_layout.addLayout(right_panel, stretch=1)

    @pyqtSlot(QImage)
    def update_image(self, cv_img):
        self.image_label.setPixmap(QPixmap.fromImage(cv_img))

    @pyqtSlot(dict)
    def update_stats(self, stats):
        self.lbl_active_tracks.setText(f"Active People: {stats['tracks']}")
        self.lbl_active_groups.setText(f"Active Groups: {stats['groups']}")
        self.lbl_fps.setText(f"FPS: {stats['fps']:.1f}")
        
        if stats['alerts'] > 0:
            self.lbl_logs.setText(f"WARNING: {stats['alerts']} Active Alerts!")
            self.lbl_logs.setStyleSheet("color: red; font-weight: bold;")
        else:
             self.lbl_logs.setText("System Normal")
             self.lbl_logs.setStyleSheet("color: #00ff00;")

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()
