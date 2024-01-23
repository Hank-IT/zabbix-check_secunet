# Introduction
Script to monitor Secunet TI Konnektors. Monitors Konnektor status and cards.

# Dependencies
apt install python3-requests python3-dateutil

# Usage
check.py --url=<url> --username=<username> --password=<password> -k <status|cards|version|update-status|tsl>

The user performing the requests needs the role "Lokaler Admin".