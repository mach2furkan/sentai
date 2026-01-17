# Sentinel AI

Sentinel AI is a defense-grade, real-time computer vision system designed for security, crowd analysis, and behavior modeling. It features a modern PyQt6 interface and clean architecture.

## Features
- **Real-time Detection**: Uses YOLOv8 for human detection.
- **Robust Tracking**: Implements SORT (Simple Online and Realtime Tracking) with Kalman Filters.
- **Group Analysis**: Dynamically clusters people based on spatial proximity.
- **Behavior Analysis**: Detects Loitering, Running, and Crowd formation.
- **Modern GUI**: Dark-themed, responsive interface with real-time analytics.

## Installation

1.  **Prerequisites**: Python 3.10+
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: For GPU support, ensure you install the CUDA version of PyTorch.*

## Usage

1.  **Run the Application**:
    ```bash
    python -m src.main
    ```

2.  **Configuration**:
    Edit `src/infrastructure/config.py` to change:
    -   `video_source`: Path to a video file or camera index ('0').
    -   `model_path`: Path to YOLOv8 model (default: `yolov8n.pt`).
    -   `loitering_time_threshold`: Seconds to trigger loitering alert.

## Architecture
The project follows **Clean Architecture** principles:
-   `src/domain`: Core business logic and entities (Person, Track, Group).
-   `src/application`: Use cases and orchestration (VideoService, AnalysisService).
-   `src/infrastructure`: External adapters (OpenCV, YOLO, SORT).
-   `src/presentation`: UI components (PyQt6 MainWindow).

## Advanced Features
-   **Kalman Filtering**: Smooths tracking trajectories.
-   **Graph-based Clustering**: Uses connected components for group detection.
-   **Multi-threaded**: Video processing runs on a separate thread to keep UI responsive.
