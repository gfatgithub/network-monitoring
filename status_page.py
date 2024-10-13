# status_page.py

from flask import Flask, render_template
import sqlite3
from pathlib import Path
import os

app = Flask(__name__)

# Configuration
USB_MOUNT_POINT = '/mnt/usb'
PROJECT_LOGS_DIR = os.path.expanduser('~/projects/network-monitoring/logs')
DB_PATH_USB = os.path.join(USB_MOUNT_POINT, 'downtime_logs.db')
DB_PATH_SD = os.path.join(PROJECT_LOGS_DIR, 'downtime_logs.db')

# Determine the correct database path
if Path(USB_MOUNT_POINT).exists():
    DB_PATH = DB_PATH_USB
else:
    DB_PATH = DB_PATH_SD

def get_uptime_stats(period='day'):
    """
    Retrieve uptime statistics from the database.

    Parameters:
    - period (str): 'day', 'week', or 'month'

    Returns:
    - dict: Statistics including total downtime and number of incidents
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        if period == 'day':
            time_threshold = datetime.now() - timedelta(days=1)
        elif period == 'week':
            time_threshold = datetime.now() - timedelta(weeks=1)
        elif period == 'month':
            time_threshold = datetime.now() - timedelta(days=30)
        else:
            return {}

        c.execute('''
            SELECT COUNT(*), SUM(duration)
            FROM downtime
            WHERE down_time >= ?
        ''', (time_threshold.strftime('%Y-%m-%d %H:%M:%S'),))

        count, total_duration = c.fetchone()
        total_duration = total_duration if total_duration else 0

        conn.close()

        return {
            'count': count,
            'total_duration': total_duration
        }
    except Exception as e:
        return {
            'count': 0,
            'total_duration': 0
        }

@app.route('/')
def home():
    from datetime import datetime, timedelta

    stats_day = get_uptime_stats('day')
    stats_week = get_uptime_stats('week')
    stats_month = get_uptime_stats('month')

    return render_template('status.html',
                           stats_day=stats_day,
                           stats_week=stats_week,
                           stats_month=stats_month)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
