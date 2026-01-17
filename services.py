import numpy as np
from typing import List, Dict
from scipy.spatial.distance import pdist, squareform
from loguru import logger

from src.domain.entities import Track, Group, FrameData, BoundingBox
from src.domain.interfaces import ObjectDetector, ObjectTracker, VideoSource
from src.infrastructure.config import AppConfig

class AnalysisService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.frame_count = 0
        self.active_groups: List[Group] = []
        
    def analyze_groups(self, tracks: List[Track]) -> List[Group]:
        """
        Groups people based on distance.
        """
        if len(tracks) < 2:
            return []
            
        # Extract centroids
        centroids = np.array([t.bbox.center for t in tracks])
        track_ids = [t.track_id for t in tracks]
        
        # Calculate distance matrix (Euclidean)
        # Using pixels for now. In real world, homography projection is needed for meters.
        dist_matrix = squareform(pdist(centroids))
        
        # Simple Clustering: Connected Components
        # Threshold: e.g., 100 pixels (config value needed)
        # For now hardcoding or using heuristic: ~width of a person * 1.5
        threshold = 150.0 
        
        # Adjacency matrix
        adj_matrix = dist_matrix < threshold
        n = len(tracks)
        
        visited = [False] * n
        groups = []
        
        group_id_counter = 0
        
        for i in range(n):
            if not visited[i]:
                # Start a new component
                component = []
                stack = [i]
                visited[i] = True
                while stack:
                    curr = stack.pop()
                    component.append(curr)
                    for j in range(n):
                        if adj_matrix[curr][j] and not visited[j]:
                            visited[j] = True
                            stack.append(j)
                
                # If group size > 1, create a group
                if len(component) > 1:
                    members = [track_ids[idx] for idx in component]
                    # Calculate group centroid
                    member_centroids = centroids[component]
                    g_cen = np.mean(member_centroids, axis=0).astype(int)
                    
                    groups.append(Group(
                        group_id=group_id_counter,
                        members=members,
                        centroid=(g_cen[0], g_cen[1])
                    ))
                    group_id_counter += 1
                    
        return groups

    def analyze_behavior(self, tracks: List[Track], groups: List[Group]) -> List[str]:
        alerts = []
        
        for t in tracks:
            # Check Speed (Running)
            # Velocity is in pixels/frame. 
            # Heuristic: Normal walk ~ 2-5 pix/frame. Run > 10 pix/frame
            speed = np.sqrt(t.velocity[0]**2 + t.velocity[1]**2)
            if speed > 15.0:
                alerts.append(f"RUNNING: ID {t.track_id} (Speed: {speed:.1f})")
                
            # Loitering (Simple age check + low movement)
            # This is a naive implementation. Correct one needs ROI check.
            # We assume whole screen is monitored area.
            if t.age > (self.config.loitering_time_threshold * 30): # 30 FPS approx
                 # Check if they moved much
                 if len(t.history) > 100:
                     start_pos = t.history[0]
                     curr_pos = t.bbox.center
                     disp = np.sqrt((start_pos[0]-curr_pos[0])**2 + (start_pos[1]-curr_pos[1])**2)
                     if disp < 50: # Stayed within 50px radius for N seconds
                         alerts.append(f"LOITERING: ID {t.track_id}")

        # Group Alerts
        for g in groups:
            if len(g.members) > 4:
                alerts.append(f"CROWD: Group {g.group_id} has {len(g.members)} members")
                
        return list(set(alerts)) # Dedup


class VideoProcessingService:
    def __init__(self, 
                 source: VideoSource, 
                 detector: ObjectDetector, 
                 tracker: ObjectTracker,
                 analyzer: AnalysisService):
        self.source = source
        self.detector = detector
        self.tracker = tracker
        self.analyzer = analyzer
        self.frame_id = 0
        
    def process_next_frame(self) -> FrameData:
        try:
            ret, frame = next(self.source.read())
            if not ret:
                return None
                
            self.frame_id += 1
            
            # Detect
            detections = self.detector.detect(frame)
            
            # Track
            tracks = self.tracker.update(frame, detections)
            
            # Update Track History logic manually here if not in tracker
            for t in tracks:
                t.update_history()
            
            # Analyze
            groups = self.analyzer.analyze_groups(tracks)
            alerts = self.analyzer.analyze_behavior(tracks, groups)
            
            return FrameData(
                frame_id=self.frame_id,
                image=frame,
                tracks=tracks,
                groups=groups,
                alerts=alerts
            )
            
        except StopIteration:
            return None
