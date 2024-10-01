import os
import sqlite3
import logging
from pathlib import Path

# ===========================
# Configuration and Setup
# ===========================

# Define the mount point for the USB memory stick
USB_MOUNT_POINT = '/media/pi/USB'

# Define the directory within your project to store log files
PROJECT_LOGS_DIR = os.path.expanduser('~/projects/network-monitoring/logs')

# Define the paths for the SQLite database on both USB and microSD card
DB_PATH_USB = os.path.join(USB_MOUNT_POINT, 'downtime_logs.db')  # Database path on USB
DB_PATH_SD = os.path.join(PROJECT_LOGS_DIR, 'downtime_logs.db')  # Database path on microSD

# Define the paths for the log files on both USB and microSD card
LOG_PATH_USB = os.path.join(PROJECT_LOGS_DIR, 'init_db_usb.log')  # Log file on USB
LOG_PATH_SD = os.path.join(PROJECT_LOGS_DIR, 'init_db_sd.log')  # Log file on microSD

# ===========================
# Ensure Logs Directory Exists
# ===========================

# Create the logs directory within the project if it doesn't already exist
# 'parents=True' allows creation of any necessary parent directories
# 'exist_ok=True' prevents an error if the directory already exists
Path(PROJECT_LOGS_DIR).mkdir(parents=True, exist_ok=True)

# ===========================
# Configure Logging
# ===========================

# Initialize a logger with the name 'init_db'
logger = logging.getLogger('init_db')

# Set the logging level to INFO to capture all INFO, WARNING, ERROR, and CRITICAL messages
logger.setLevel(logging.INFO)

# ===========================
# Create Logging Handlers Based on USB Availability
# ===========================

if Path(USB_MOUNT_POINT).exists():
    # USB is mounted and available

    # Define the log file path on the USB
    usb_log_file = LOG_PATH_USB

    # Create a FileHandler to write logs to the USB log file
    usb_log_handler = logging.FileHandler(usb_log_file)

    # Add the USB FileHandler to the logger
    logger.addHandler(usb_log_handler)

    # Log an informational message indicating that logging is directed to the USB
    logger.info("Logging to USB memory stick.")
else:
    # USB is not mounted; fallback to logging on the microSD card

    # Define the log file path on the microSD card
    sd_log_file = LOG_PATH_SD

    # Create a FileHandler to write logs to the microSD log file
    sd_log_handler = logging.FileHandler(sd_log_file)

    # Add the microSD FileHandler to the logger
    logger.addHandler(sd_log_handler)

    # Log a warning message indicating that USB is unavailable and logging is on microSD
    logger.warning(f"USB mount point {USB_MOUNT_POINT} does not exist. Logging to microSD card.")

# ===========================
# Set Formatter for All Handlers
# ===========================

# Define the format for log messages, including timestamp, log level, and message
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Apply the formatter to all handlers attached to the logger
for handler in logger.handlers:
    handler.setFormatter(formatter)


# ===========================
# Define the Database Initialization Function
# ===========================

def initialize_database(db_path):
    """
    Initialize the SQLite database and create the 'downtime' table if it doesn't exist.

    Parameters:
    - db_path (str): The file path to the SQLite database.
    """
    try:
        # Ensure the directory for the database exists
        db_dir = Path(db_path).parent  # Get the parent directory of the database file
        if not db_dir.exists():
            # If the directory doesn't exist, log an error and exit the function
            logger.error(f"The directory {db_dir} does not exist.")
            logger.error("Please ensure the USB memory stick is mounted correctly.")
            return

        # Connect to SQLite database at the specified path
        # If the database file doesn't exist, SQLite will create it
        conn = sqlite3.connect(db_path)
        c = conn.cursor()  # Create a cursor object to execute SQL commands

        # Create the 'downtime' table if it doesn't already exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS downtime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interface TEXT NOT NULL,
                down_time TEXT NOT NULL,
                up_time TEXT,
                duration INTEGER
            )
        ''')

        # Commit the transaction to save changes
        conn.commit()

        # Close the database connection
        conn.close()

        # Check if the database file was created
        if not Path(db_path).exists():
            # This block is unlikely to execute because SQLite creates the file if it doesn't exist
            logger.info(f"Database created successfully at {db_path}.")
        else:
            # Log that the database already exists and the table is ready
            logger.info(f"Database already exists at {db_path}. Table 'downtime' is ready.")

    except sqlite3.Error as e:
        # Log any SQLite-specific errors that occur during the operation
        logger.error(f"SQLite error occurred: {e}")
    except Exception as e:
        # Log any other unexpected errors
        logger.error(f"An unexpected error occurred: {e}")


# ===========================
# Entry Point of the Script
# ===========================

if __name__ == "__main__":
    # Determine which database path to use based on USB availability
    if Path(USB_MOUNT_POINT).exists():
        # USB is mounted; initialize the database on USB
        initialize_database(DB_PATH_USB)
    else:
        # USB is not mounted; initialize the database on microSD
        initialize_database(DB_PATH_SD)
