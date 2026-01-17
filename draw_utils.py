import cv2
import numpy as np
from src.domain.entities import FrameData

class DrawUtils:
    @staticmethod
    def draw_overlays(frame_data: FrameData):
        img = frame_data.image
        
        # 1. Draw Tracks
        for track in frame_data.tracks:
            x1, y1, x2, y2 = track.bbox.x1, track.bbox.y1, track.bbox.x2, track.bbox.y2
            
            # Color based on speed (behavior)
            color = (0, 255, 0) # Green normal
            speed = np.sqrt(track.velocity[0]**2 + track.velocity[1]**2)
            if speed > 15.0:
                 color = (0, 0, 255) # Red running
            
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            # Label: ID
            label = f"ID: {track.track_id}"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Draw trail
            if len(track.history) > 1:
                pts = np.array(track.history, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(img, [pts], False, (0, 255, 255), 1)

        # 2. Draw Groups
        for group in frame_data.groups:
            # Draw line between members map
            # This is expensive to find members' bboxes again from IDs easily, 
            # so we just draw centroid for now.
            # Ideally we pass tracks map or similar.
            cx, cy = group.centroid
            cv2.circle(img, (cx, cy), 10, (255, 0, 255), -1)
            cv2.putText(img, f"GRP {group.group_id}", (cx+15, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            
        # 3. Draw Alerts
        y_offset = 30
        if frame_data.alerts:
            cv2.putText(img, "WARNING / ALERTS:", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            y_offset += 30
            for alert in frame_data.alerts:
                 cv2.putText(img, alert, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                 y_offset += 25
                 
        return img
