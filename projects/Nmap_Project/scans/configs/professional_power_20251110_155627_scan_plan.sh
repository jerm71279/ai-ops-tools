#!/bin/bash
# Scan Plan for Professional Power
# Generated: 2025-11-10T15:56:27.682173

echo '======================================'
echo 'Scan Plan: Professional Power'
echo '======================================'
echo ''

# Primary Network: 192.168.1.0/24
echo 'Scanning primary network: 192.168.1.0/24...'
nmap -T4 -v 192.168.1.0/24 -oA /scans/professional_power_primary_20251110_155627

echo ''
echo '======================================'
echo 'All scans complete!'
echo '======================================'
