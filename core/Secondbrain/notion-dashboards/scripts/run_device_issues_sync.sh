#!/bin/bash
# Device Issues Sync - runs every 2 hours
cd /home/mavrick/Projects/Secondbrain/notion-dashboards/scripts
source ../.env
python3 device_issues_sync.py --config ../config/config.json >> /var/log/notion_device_issues.log 2>&1
