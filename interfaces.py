from abc import ABC, abstractmethod
from typing import List, Generator, Any
import numpy as np
from src.domain.entities import BoundingBox, Track, FrameData

class VideoSource(ABC):
    @abstractmethod
    def read(self) -> Generator[Tuple[bool, np.ndarray], None, None]:
        pass
        
    @abstractmethod
    def get_fps(self) -> float:
        pass
    
    @abstractmethod
    def release(self):
        pass

class ObjectDetector(ABC):
    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[BoundingBox]:
        pass

class ObjectTracker(ABC):
    @abstractmethod
    def update(self, frame: np.ndarray, detections: List[BoundingBox]) -> List[Track]:
        pass
