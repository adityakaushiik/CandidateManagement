"""
This module sets up a logger for the application using Python's built-in logging library.
The logger is configured to output log messages to the console with a specific format and log level.
"""

import logging

# Create a logger instance with the name of the current module
logger = logging.getLogger(__name__)

# Set the logging level for the logger to DEBUG
logger.setLevel(logging.DEBUG)

# Create a StreamHandler to output log messages to the console
ch = logging.StreamHandler()

# Set the logging level for the StreamHandler to DEBUG
ch.setLevel(logging.DEBUG)

# Define a log message format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Apply the formatter to the StreamHandler
ch.setFormatter(formatter)

# Add the StreamHandler to the logger
logger.addHandler(ch)
