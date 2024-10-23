import sys
from Rufus.logger import rufus_logger

def error_message_detail(error, error_detail: sys):
    """
    Generate detailed error message including file name, line number, and error description.
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = (
        f"Error occurred in Rufus script: {file_name} "
        f"at line number: {exc_tb.tb_lineno} "
        f"error message: {str(error)}"
    )
    return error_message

class RufusException(Exception):
    """
    Custom exception class for Rufus-specific errors
    """
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail)
        rufus_logger.error(self.error_message)
    
    def __str__(self):
        return self.error_message

# Specific Exception Classes
class CrawlerException(RufusException):
    """Exception raised for errors in the web crawler"""
    pass

class ExtractorException(RufusException):
    """Exception raised for errors in content extraction"""
    pass

class SynthesizerException(RufusException):
    """Exception raised for errors in document synthesis"""
    pass

if __name__ == "__main__":
    rufus_logger.info("Rufus exception handling system initialized")
    try:
        # Test exception handling
        raise ValueError("Test error")
    except Exception as e:
        rufus_logger.error("An error occurred", exc_info=True)
        raise RufusException(e, sys)