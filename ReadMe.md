## Overview
This solution involves setting up a Raspberry Pi to monitor internet connectivity by periodically pinging both the Fortigate F40 and an external reliable host (e.g., Google's DNS at 8.8.8.8). The system logs downtime events into a SQLite database, sends SMS notifications upon downtime and restoration, and provides a web-based status page to view uptime statistics.

## Hardware Setup
- **Raspberry Pi**: Ensure you have a Raspberry Pi (preferably Pi 3 or later) with Raspbian OS installed.
- **Network Connections**:
  - **Ethernet Cable**: Connect the Raspberry Pi to the Firewall using an Ethernet cable.
  - **Internet Connection**: Ensure the Firewall is connected to your internet modem.
  - **USB Drive**: Optionally, attach a USB drive for additional storage and logging.

## Software Requirements
- **Operating System**: Raspbian OS (now known as Raspberry Pi OS).
- **Python 3**: Ensure Python 3 is installed.
- **SQLite**: For the database.
- **Flask**: For the status webpage.
- **Twilio (or similar service)**: For sending SMS notifications.

## Setting Up the Raspberry Pi
### 1. Install the Operating System
If you haven't already, install the latest version of Raspberry Pi OS on your Raspberry Pi. You can download it from the official website.

### 2. Update and Upgrade
Open the terminal and run the following commands to update and upgrade your system:
```bash
sudo apt-get update
sudo apt-get upgrade -y
```
### 3. Install Required Packages
Install the necessary packages:

```bash
sudo apt-get install python3-pip sqlite3
pip3 install flask twilio
```
### 4. Update Environment Variables with Twilio Details
Now that you have your Twilio phone number, you'll need to update your environment variables accordingly.

**Using Systemd Service Environment Variables:**
If you're configuring environment variables directly in your monitor.service file, update it as follows:

**1- Edit the Service File:**

```bash
sudo nano /etc/systemd/system/monitor.service
````

**2- Add/Update Environment Variables:**

```ini
[Unit]
Description=Network Connectivity Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/projects/network-monitoring
ExecStart=/home/pi/projects/network-monitoring/venv/bin/python monitor.py
Restart=always
RestartSec=5
Environment=TWILIO_ACCOUNT_SID=your_account_sid
Environment=TWILIO_AUTH_TOKEN=your_auth_token
# Your Twilio number
Environment=TWILIO_PHONE_NUMBER='+1234567890'        
# Comma-separated recipient numbers
Environment=RECIPIENT_PHONE_NUMBERS='+0987654321,+11234567890'  

[Install]
WantedBy=multi-user.target
```
Replace:
your_account_sid with your actual Twilio Account SID.
your_auth_token with your actual Twilio Auth Token.
'+1234567890' with your Twilio phone number.
'+0987654321,+11234567890' with the recipient phone numbers (ensure they are comma-separated and include the country code).

**3- Reload and Restart Services:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable monitor.service
sudo systemctl start monitor.service
```

###  5- Create Systemd Service for status_page.py
**1- Create another service file:**

```bash
sudo nano /etc/systemd/system/status_page.service
```

**2- Add the following content:**

```ini
[Unit]
Description=Network Status Webpage
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/projects/network-monitoring/status_page.py
WorkingDirectory=/home/pi/projects/network-monitoring
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

**4- Save and exit.**

**5- Enable and start the service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable status_page.service
sudo systemctl start status_page.service
```

## Usage
### Accessing the Status Page
Once both services are running, you can access the network status webpage to view uptime statistics.

**1- Open a Web Browser:**

On any device connected to the same network as your Raspberry Pi, open a web browser.

**2- Navigate to the Status Page:**

Enter the following URL:

```url
http://<raspberry_pi_ip_address>:5000
```
**Example:**

```url
http://192.168.86.207:5000
```

**3- View Uptime Statistics:**

The webpage will display a table with the following columns:

**- Period:**  Timeframe (Today, Last Day, Last Week, Last Month)
**- Number of Downtimes:** Total number of downtime events within the period.
**- Total Downtime (seconds):** Cumulative downtime duration in seconds within the period.

## Monitoring Logs
Logs are crucial for monitoring the system's behavior and diagnosing issues.

**1- View Monitor Logs:**

```bash
sudo journalctl -u monitor.service -f
```
**-** The -f flag follows the log in real-time.

**2- View Status Page Logs:**

```bash
sudo journalctl -u status_page.service -f
```
**3- Access Log Files Directly:**

Depending on your configuration, logs may also be written to log files on the USB drive or microSD card.

**- USB Logs:**

```lua
/home/pi/projects/network-monitoring/logs/monitor_usb.log
/home/pi/projects/network-monitoring/logs/init_db_usb.log
```
**- microSD Logs:**

```lua
/home/pi/projects/network-monitoring/logs/monitor_sd.log
/home/pi/projects/network-monitoring/logs/init_db_sd.log
```