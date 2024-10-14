# status_page.py

from flask import Flask, render_template
import sqlite3
from pathlib import Path
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# ===========================
# Configuration
# ===========================

USB_MOUNT_POINT = '/mnt/usb'
PROJECT_LOGS_DIR = os.path.expanduser('~/projects/network-monitoring/logs')
DB_PATH_USB = os.path.join(USB_MOUNT_POINT, 'downtime_logs.db')
DB_PATH_SD = os.path.join(PROJECT_LOGS_DIR, 'downtime_logs.db')

# ===========================
# Determine the Correct Database Path
# ===========================

if Path(USB_MOUNT_POINT).exists():
    DB_PATH = DB_PATH_USB
else:
    DB_PATH = DB_PATH_SD

# ===========================
# Define Functions
# ===========================

def get_uptime_stats(period='today'):
    """
    Retrieve uptime statistics from the database based on the specified period.

    Parameters:
    - period (str): 'today', 'last_day', 'last_week', or 'last_month'

    Returns:
    - dict: Statistics including total downtime and number of incidents
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        now = datetime.now()

        if period == 'today':
            # Today: From midnight to now
            start_time = datetime(now.year, now.month, now.day)
            end_time = now
        elif period == 'last_day':
            # Last Day: From midnight of yesterday to midnight today
            start_time = datetime(now.year, now.month, now.day) - timedelta(days=1)
            end_time = datetime(now.year, now.month, now.day)
        elif period == 'last_week':
            # Last Week: From midnight 7 days ago to midnight yesterday
            start_time = datetime(now.year, now.month, now.day) - timedelta(weeks=1)
            end_time = datetime(now.year, now.month, now.day) - timedelta(days=1)
        elif period == 'last_month':
            # Last Month: From midnight 30 days ago to midnight 7 days ago
            start_time = datetime(now.year, now.month, now.day) - timedelta(days=30)
            end_time = datetime(now.year, now.month, now.day) - timedelta(weeks=1)
        else:
            return {}

        # Format times to match the database's datetime format
        start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        # Execute the query for the specified period
        c.execute('''
            SELECT COUNT(*) as count, COALESCE(SUM(duration), 0) as total_duration
            FROM downtime
            WHERE down_time >= ? AND down_time < ?
        ''', (start_str, end_str))

        result = c.fetchone()
        count, total_duration = result

        # Ensure total_duration is an integer
        total_duration = int(total_duration) if total_duration else 0

        conn.close()

        return {
            'count': count,
            'total_duration': total_duration
        }
    except Exception as e:
        # Log the exception if necessary
        # For security reasons, avoid exposing internal errors to the user
        return {
            'count': 0,
            'total_duration': 0
        }

@app.route('/')
def home():
    stats_today = get_uptime_stats('today')
    stats_last_day = get_uptime_stats('last_day')
    stats_last_week = get_uptime_stats('last_week')
    stats_last_month = get_uptime_stats('last_month')

    return render_template('status.html',
                           stats_today=stats_today,
                           stats_last_day=stats_last_day,
                           stats_last_week=stats_last_week,
                           stats_last_month=stats_last_month)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
