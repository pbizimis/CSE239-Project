import logging
import sys
from typing import Optional

# Create a custom logger
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name or __name__)
    
    # Only configure if no handlers exist (avoid duplicate handlers)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create console handler with formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger
