import sys
from loguru import logger
from PyQt6.QtWidgets import QApplication
from src.presentation.main_window import MainWindow
from src.infrastructure.config import load_config

def main():
    logger.add("sentinel_ai.log", rotation="500 MB")
    logger.info("Initializing Sentinel AI...")
    
    # Load configuration
    config = load_config()
    
    app = QApplication(sys.argv)
    
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
