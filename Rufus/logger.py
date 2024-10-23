import logging
import os
from datetime import datetime

class RufusLogger:
    def __init__(self):
        # Create logs directory
        self.LOG_FILE = f"rufus_{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.logs_path = os.path.join(os.getcwd(), "logs")
        os.makedirs(self.logs_path, exist_ok=True)
        
        # Create log file path
        self.LOG_FILE_PATH = os.path.join(self.logs_path, self.LOG_FILE)
        
        # Configure logging
        logging.basicConfig(
            filename=self.LOG_FILE_PATH,
            format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO
        )
        
        # Add console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logging.getLogger('').addHandler(console_handler)
        
        self.logger = logging.getLogger("Rufus")
        
    def get_logger(self):
        return self.logger

# Global logger instance
rufus_logger = RufusLogger().get_logger()

# Function to access the logger
def get_logger(self, name=None):
        return logging.getLogger(name or "Rufus")

if __name__ == "__main__":
    rufus_logger.info("Rufus logging system initialized")
