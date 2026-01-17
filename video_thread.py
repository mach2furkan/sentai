from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage
import cv2
import time
from src.application.services import VideoProcessingService
from src.presentation.draw_utils import DrawUtils

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    stats_signal = pyqtSignal(dict)
    
    def __init__(self, service: VideoProcessingService):
        super().__init__()
        self.service = service
        self._run_flag = True
        
    def run(self):
        while self._run_flag:
            start_time = time.time()
            data = self.service.process_next_frame()
            
            if data is None:
                # End of video or error
                time.sleep(0.1)
                continue
                
            # Draw Overlays
            processed_img = DrawUtils.draw_overlays(data)
            
            # Convert to Qt Image
            rgb_image = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            p = convert_to_Qt_format.scaled(1280, 720, Qt.AspectRatioMode.KeepAspectRatio)
            
            # Emit signals
            self.change_pixmap_signal.emit(p)
            
            # Emit stats
            stats = {
                "tracks": len(data.tracks),
                "groups": len(data.groups),
                "alerts": len(data.alerts),
                "fps": 1.0 / (time.time() - start_time + 0.0001)
            }
            self.stats_signal.emit(stats)
            
    def stop(self):
        self._run_flag = False
        self.wait()
