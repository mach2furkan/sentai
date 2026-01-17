from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np

@dataclass
class BoundingBox:
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    class_id: int

    @property
    def center(self) -> Tuple[int, int]:
        return int((self.x1 + self.x2) / 2), int((self.y1 + self.y2) / 2)

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

@dataclass
class Track:
    track_id: int
    bbox: BoundingBox
    velocity: Tuple[float, float] = (0.0, 0.0) # dx, dy
    history: List[Tuple[int, int]] = field(default_factory=list) # Center points
    state: int = 1 # 1: Active, 0: Lost
    age: int = 0

    def update_history(self):
        self.history.append(self.bbox.center)
        if len(self.history) > 300: # Keep last 300 points
            self.history.pop(0)

@dataclass
class Group:
    group_id: int
    members: List[int] = field(default_factory=list) # Track IDs
    centroid: Tuple[int, int] = (0, 0)
    
@dataclass
class FrameData:
    frame_id: int
    image: np.ndarray
    tracks: List[Track] = field(default_factory=list)
    groups: List[Group] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
