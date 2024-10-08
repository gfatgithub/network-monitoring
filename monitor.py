# monitor.py

import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# ===========================
# Configuration and Setup
# ===========================

# Define the mount point for the USB memory stick
USB_MOUNT_POINT =  '/mnt/usb'

# Define the directory within your project to store log files
PROJECT_LOGS_DIR = os.path.expanduser('~/projects/network-monitoring/logs')

# Define the paths for the SQLite database on both USB and microSD card
DB_PATH_USB = os.path.join(USB_MOUNT_POINT, 'downtime_logs.db')  # Database path on USB
DB_PATH_SD = os.path.join(PROJECT_LOGS_DIR, 'downtime_logs.db')  # Database path on microSD

# Define the paths for the log files on both USB and microSD card
LOG_PATH_USB = os.path.join(PROJECT_LOGS_DIR, 'monitor_usb.log')  # Log file on USB
LOG_PATH_SD = os.path.join(PROJECT_LOGS_DIR, 'monitor_sd.log')  # Log file on microSD

# ===========================
# Ensure Logs Directory Exists
# ===========================

# Create the logs directory within the project if it doesn't already exist
Path(PROJECT_LOGS_DIR).mkdir(parents=True, exist_ok=True)

# ===========================
# Configure Logging
# ===========================

# Initialize a logger with the name 'monitor'
logger = logging.getLogger('monitor')
logger.setLevel(logging.INFO)  # Set the logging level to INFO

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
# Determine the Correct Database Path
# ===========================

if Path(USB_MOUNT_POINT).exists():
    # USB is mounted; use the database path on USB
    DB_PATH = DB_PATH_USB
else:
    # USB is not mounted; use the database path on microSD
    DB_PATH = DB_PATH_SD


# ===========================
# Define Functions
# ===========================

def log_downtime(interface, down_time, up_time=None, duration=None):
    """
    Log downtime events to the SQLite database.

    Parameters:
    - interface (str): The name of the network interface (e.g., 'Internet').
    - down_time (str): Timestamp when the interface went down.
    - up_time (str, optional): Timestamp when the interface came back up.
    - duration (int, optional): Duration of downtime in seconds.
    """
    try:
        # Connect to the SQLite database at the determined path
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Insert a new record into the 'downtime' table
        c.execute('''
            INSERT INTO downtime (interface, down_time, up_time, duration)
            VALUES (?, ?, ?, ?)
        ''', (interface, down_time, up_time, duration))

        # Commit the transaction to save changes
        conn.commit()

        # Close the database connection
        conn.close()

        # Log an informational message indicating successful logging
        logger.info(f"Logged downtime for {interface}.")
    except sqlite3.Error as e:
        # Log any SQLite-specific errors that occur during the operation
        logger.error(f"SQLite error occurred while logging downtime: {e}")
    except Exception as e:
        # Log any other unexpected errors
        logger.error(f"An unexpected error occurred while logging downtime: {e}")


def check_connectivity():
    """
    Check connectivity by pinging the Firewall f40 and a reliable external host.
    Returns True if both are online, False otherwise.
    """
    import subprocess
    interface = 'eth0'  # Replace with 'wlan0' if using Wi-Fi
    firewall_ip = '192.168.1.99'  # Firewall LAN IP
    external_ip = '8.8.8.8'  # External IP to confirm internet connectivity

    try:
        # Ping the Firewall directly
        subprocess.check_output(['ping', '-c', '1', '-I', interface, firewall_ip])

        # Ping the external IP to confirm internet connectivity
        subprocess.check_output(['ping', '-c', '1', '-I', interface, external_ip])

        return True
    except subprocess.CalledProcessError:
        return False


def monitor():
    """
    Continuously monitor network connectivity and log downtimes.
    """
    # Define the name of the network interface being monitored
    interface = 'Internet'

    # Initialize state variables
    is_down = False  # Indicates current network status (False = online, True = offline)
    down_time = None  # Stores the timestamp when the network went down

    while True:
        # Check current network connectivity status
        online = check_connectivity()

        if not online and not is_down:
            # Network has just gone down

            is_down = True  # Update state to indicate downtime
            down_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Record downtime start

            # Log a warning indicating the network is down
            logger.warning(f"{interface} is down at {down_time}.")

            # Log the downtime event in the SQLite database
            log_downtime(interface, down_time)

        elif online and is_down:
            # Network has just come back up

            is_down = False  # Update state to indicate network is back online
            up_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Record uptime
            # Calculate the duration of downtime in seconds
            duration = int((datetime.strptime(up_time, '%Y-%m-%d %H:%M:%S') -
                            datetime.strptime(down_time, '%Y-%m-%d %H:%M:%S')).total_seconds())

            # Log an informational message indicating the network is back up
            logger.info(f"{interface} is back up at {up_time}. Downtime duration: {duration} seconds.")

            # Attempt to update the existing downtime record with up_time and duration
            try:
                # Connect to the SQLite database
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()

                # Update the latest downtime record where up_time is NULL
                c.execute('''
                    UPDATE downtime
                    SET up_time = ?, duration = ?
                    WHERE interface = ? AND up_time IS NULL
                    ORDER BY id DESC
                    LIMIT 1
                ''', (up_time, duration, interface))

                # Commit the transaction to save changes
                conn.commit()

                # Close the database connection
                conn.close()
            except sqlite3.Error as e:
                # Log any SQLite-specific errors that occur during the update
                logger.error(f"SQLite error occurred while updating downtime: {e}")
            except Exception as e:
                # Log any other unexpected errors
                logger.error(f"An unexpected error occurred while updating downtime: {e}")

        # Wait for a specified interval before performing the next connectivity check
        import time
        time.sleep(60)  # Pause for 60 seconds


# ===========================
# Entry Point
# ===========================

if __name__ == "__main__":
    # Start the monitoring process when the script is executed directly
    monitor()
