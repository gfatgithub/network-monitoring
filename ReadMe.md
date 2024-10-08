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
