#!/usr/bin/env python3
"""
Call Flow Web Interface with Authentication - OberaConnect
Secure web-based interface for creating and managing call flow configurations
"""

from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from call_flow_generator import CallFlowGenerator
from contract_tracker import ContractTracker
from pathlib import Path
import json
import os
import re
import subprocess
import ipaddress
from datetime import datetime

# Add Nmap_Project to path for network config
import sys
sys.path.insert(0, '/home/mavrick/Projects/Nmap_Project')

# Nmap project directories
NMAP_PROJECT_DIR = Path('/home/mavrick/Projects/Nmap_Project')
SCANS_DIR = NMAP_PROJECT_DIR / 'scans'

app = Flask(__name__)
# Use persistent secret key for sessions
SECRET_KEY_FILE = Path('/home/mavrick/Projects/Secondbrain/.secret_key')
if SECRET_KEY_FILE.exists():
    app.secret_key = SECRET_KEY_FILE.read_bytes()
else:
    app.secret_key = os.urandom(24)
    SECRET_KEY_FILE.write_bytes(app.secret_key)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize tools
generator = CallFlowGenerator()
tracker = ContractTracker()

# Network config directory
NETWORK_CONFIG_DIR = Path('/home/mavrick/Projects/Nmap_Project/scans/configs')
NETWORK_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Static IP registry
STATIC_IP_FILE = Path('/home/mavrick/Projects/Secondbrain/static_ip_registry.json')

def load_static_ips():
    if STATIC_IP_FILE.exists():
        with open(STATIC_IP_FILE, 'r') as f:
            return json.load(f)
    return {"devices": []}

def save_static_ips(data):
    with open(STATIC_IP_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# User database file
USERS_FILE = Path("users.json")

def load_users():
    """Load users from file"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    # Default users - change these passwords!
    default_users = {
        "admin": {
            "password": generate_password_hash("oberaconnect2025"),
            "name": "Administrator",
            "role": "admin"
        },
        "user": {
            "password": generate_password_hash("oberatools"),
            "name": "OberaConnect User",
            "role": "user"
        }
    }
    save_users(default_users)
    return default_users

def save_users(users):
    """Save users to file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

USERS = load_users()

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.name = USERS.get(username, {}).get('name', username)
        self.role = USERS.get(username, {}).get('role', 'user')

@login_manager.user_loader
def load_user(username):
    if username in USERS:
        return User(username)
    return None

# Login page template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - OberaConnect Tools</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header h1 {
            color: #2563eb;
            margin: 0 0 10px 0;
        }
        .login-header p {
            color: #666;
            margin: 0;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #2563eb;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
        }
        .btn:hover {
            background: #1d4ed8;
        }
        .alert {
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .alert-error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #ef4444;
        }
        .alert-info {
            background: #dbeafe;
            color: #1e40af;
            border: 1px solid #3b82f6;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>OberaConnect Tools</h1>
            <p>Please log in to continue</p>
        </div>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST" action="{{ url_for('login') }}">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Log In</button>
        </form>
    </div>
</body>
</html>
'''

# Main app template with logout button
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OberaConnect - Call Flow Generator</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background: #2563eb;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header-left h1 {
            margin: 0;
            font-size: 24px;
        }
        .header-left p {
            margin: 5px 0 0 0;
            opacity: 0.9;
        }
        .header-right {
            text-align: right;
        }
        .header-right .user-info {
            margin-bottom: 8px;
            font-size: 14px;
        }
        .header-right .logout-btn {
            padding: 8px 16px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
        }
        .header-right .logout-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: white;
            border: 2px solid #ddd;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
        }
        .tab.active {
            background: #2563eb;
            color: white;
            border-color: #2563eb;
        }
        .panel {
            display: none;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .panel.active {
            display: block;
        }
        .form-section {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }
        .form-section h3 {
            margin: 0 0 15px 0;
            color: #2563eb;
        }
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        .form-group {
            display: flex;
            flex-direction: column;
        }
        .form-group label {
            font-weight: 500;
            margin-bottom: 5px;
            font-size: 14px;
        }
        .form-group input,
        .form-group select,
        .form-group textarea {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .form-group textarea {
            min-height: 80px;
            resize: vertical;
        }
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #2563eb;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            margin-right: 10px;
        }
        .btn-primary {
            background: #2563eb;
            color: white;
        }
        .btn-secondary {
            background: #6b7280;
            color: white;
        }
        .btn-success {
            background: #10b981;
            color: white;
        }
        .btn:hover {
            opacity: 0.9;
        }
        .alert {
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .alert-success {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #10b981;
        }
        .alert-error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #ef4444;
        }
        .contract-list {
            list-style: none;
            padding: 0;
        }
        .contract-item {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .contract-item.critical {
            border-left: 4px solid #ef4444;
        }
        .contract-item.warning {
            border-left: 4px solid #f59e0b;
        }
        .contract-item.upcoming {
            border-left: 4px solid #10b981;
        }
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-critical {
            background: #fee2e2;
            color: #991b1b;
        }
        .badge-warning {
            background: #fef3c7;
            color: #92400e;
        }
        .badge-success {
            background: #d1fae5;
            color: #065f46;
        }
        #result {
            margin-top: 20px;
        }
        .secure-badge {
            display: inline-block;
            padding: 2px 8px;
            background: #10b981;
            color: white;
            border-radius: 4px;
            font-size: 10px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-left">
                <h1>OberaConnect Tools <span class="secure-badge">SECURE</span></h1>
                <p>Call Flow Generator, Contract Tracker & Network Config</p>
            </div>
            <div class="header-right">
                <div class="user-info">Logged in as: <strong>{{ current_user.name }}</strong></div>
                <a href="{{ url_for('logout') }}" class="logout-btn">Log Out</a>
            </div>
        </header>

        <div class="tabs">
            <div class="tab active" onclick="showTab('callflow')">Call Flow Generator</div>
            <div class="tab" onclick="showTab('contracts')">Contract Tracker</div>
            <div class="tab" onclick="showTab('network')">Network Config</div>
        </div>

        <!-- Call Flow Generator Panel -->
        <div id="callflow-panel" class="panel active">
            <form id="callflow-form">
                <div class="form-section">
                    <h3>Business Information</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="business_name">Business Name *</label>
                            <input type="text" id="business_name" name="business_name" required>
                        </div>
                        <div class="form-group">
                            <label for="address">Address</label>
                            <input type="text" id="address" name="address">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="contact_name">Contact Name *</label>
                            <input type="text" id="contact_name" name="contact_name" required>
                        </div>
                        <div class="form-group">
                            <label for="contact_number">Contact Number</label>
                            <input type="tel" id="contact_number" name="contact_number">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="business_hours">Business Hours</label>
                            <input type="text" id="business_hours" name="business_hours" placeholder="Mon-Fri 8am-5pm">
                        </div>
                        <div class="form-group">
                            <label for="main_phone_number">Main Phone Number *</label>
                            <input type="tel" id="main_phone_number" name="main_phone_number" required>
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>Current Providers</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="internet_provider">Internet Provider</label>
                            <input type="text" id="internet_provider" name="internet_provider">
                        </div>
                        <div class="form-group">
                            <label for="it_vendor">Current IT Vendor</label>
                            <input type="text" id="it_vendor" name="it_vendor">
                        </div>
                        <div class="form-group">
                            <label for="phone_vendor">Current Phone Vendor</label>
                            <input type="text" id="phone_vendor" name="phone_vendor">
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>Phone Number Setup</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="creating_or_porting">Creating or Porting?</label>
                            <select id="creating_or_porting" name="creating_or_porting">
                                <option value="porting">Porting Existing Numbers</option>
                                <option value="creating">Creating New Numbers</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="requested_port_date">Requested Port Date</label>
                            <input type="date" id="requested_port_date" name="requested_port_date">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="numbers_to_port">Numbers to Port (comma-separated)</label>
                            <textarea id="numbers_to_port" name="numbers_to_port" placeholder="8505551234, 8505551235"></textarea>
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>Configuration</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="extension_list">Extension List</label>
                            <textarea id="extension_list" name="extension_list" placeholder="Reception: ext 100, Sales: ext 101"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="portal_access">ConnectWare Portal Access</label>
                            <input type="text" id="portal_access" name="portal_access">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="mobile_app_users">ConnectMobile App Users</label>
                            <input type="text" id="mobile_app_users" name="mobile_app_users">
                        </div>
                        <div class="form-group">
                            <label for="texting_type">Texting Type</label>
                            <select id="texting_type" name="texting_type">
                                <option value="">None</option>
                                <option value="internal">Internal Only</option>
                                <option value="external">External (requires 10DLC)</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>Call Routing</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="business_hours_routing">Business Hours Routing</label>
                            <textarea id="business_hours_routing" name="business_hours_routing"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="after_hours_routing">After Hours Routing</label>
                            <textarea id="after_hours_routing" name="after_hours_routing"></textarea>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="voicemail_type">Voicemail Type</label>
                            <select id="voicemail_type" name="voicemail_type">
                                <option value="vm-to-email">Voicemail to Email</option>
                                <option value="standard">Standard Voicemail</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>Equipment</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="phone_count">Phone Count</label>
                            <input type="number" id="phone_count" name="phone_count" min="0">
                        </div>
                        <div class="form-group">
                            <label for="cordless_count">Cordless Phone Count</label>
                            <input type="number" id="cordless_count" name="cordless_count" min="0">
                        </div>
                        <div class="form-group">
                            <label for="conference_phone_count">Conference Phone Count</label>
                            <input type="number" id="conference_phone_count" name="conference_phone_count" min="0">
                        </div>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary">Generate Call Flow Document</button>
                <button type="button" class="btn btn-secondary" onclick="clearForm()">Clear Form</button>
            </form>

            <div id="result"></div>
        </div>

        <!-- Contract Tracker Panel -->
        <div id="contracts-panel" class="panel">
            <h3>Contract Renewal Alerts</h3>
            <div id="contract-alerts">Loading contracts...</div>

            <h3 style="margin-top: 30px;">All Active Contracts</h3>
            <div id="all-contracts">Loading...</div>

            <div style="margin-top: 20px;">
                <button class="btn btn-success" onclick="exportContracts()">Export to CSV</button>
                <button class="btn btn-secondary" onclick="loadContracts()">Refresh</button>
            </div>
        </div>

        <!-- Network Config Panel -->
        <div id="network-panel" class="panel">
            <form id="network-form">
                <div class="form-section">
                    <h3>Customer Information</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="net_customer_name">Customer Name *</label>
                            <input type="text" id="net_customer_name" name="customer_name" required>
                        </div>
                        <div class="form-group">
                            <label for="net_customer_id">Customer ID/Code</label>
                            <input type="text" id="net_customer_id" name="customer_id">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="net_contact_name">Primary Contact *</label>
                            <input type="text" id="net_contact_name" name="contact_name" required>
                        </div>
                        <div class="form-group">
                            <label for="net_contact_email">Contact Email *</label>
                            <input type="email" id="net_contact_email" name="contact_email" required>
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>Scan Authorization</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="net_auth_received" name="auth_received" value="true">
                                Written authorization received to scan
                            </label>
                        </div>
                        <div class="form-group">
                            <label for="net_auth_reference">Authorization Reference/Ticket #</label>
                            <input type="text" id="net_auth_reference" name="auth_reference">
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>Network Configuration</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="net_primary_network">Primary Network (CIDR) *</label>
                            <input type="text" id="net_primary_network" name="primary_network" placeholder="192.168.1.0/24" required>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Additional Networks</label>
                            <div id="additional-networks">
                                <input type="text" name="additional_network[]" placeholder="10.0.0.0/24" style="margin-bottom: 5px;">
                            </div>
                            <button type="button" class="btn btn-secondary" onclick="addNetwork()" style="padding: 6px 12px; font-size: 12px;">+ Add Network</button>
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>VLAN Configuration</h3>
                    <div id="vlan-list">
                        <div class="vlan-entry" style="display: grid; grid-template-columns: 80px 1fr 1fr 1fr auto; gap: 10px; margin-bottom: 10px; align-items: end;">
                            <div class="form-group" style="margin: 0;">
                                <label>VLAN ID</label>
                                <input type="number" name="vlan_id[]" placeholder="10" min="1" max="4094">
                            </div>
                            <div class="form-group" style="margin: 0;">
                                <label>Name</label>
                                <input type="text" name="vlan_name[]" placeholder="Management">
                            </div>
                            <div class="form-group" style="margin: 0;">
                                <label>Network (CIDR)</label>
                                <input type="text" name="vlan_network[]" placeholder="192.168.10.0/24">
                            </div>
                            <div class="form-group" style="margin: 0;">
                                <label>Gateway</label>
                                <input type="text" name="vlan_gateway[]" placeholder="192.168.10.1">
                            </div>
                            <button type="button" onclick="removeVlan(this)" style="padding: 8px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;">X</button>
                        </div>
                    </div>
                    <button type="button" class="btn btn-secondary" onclick="addVlan()" style="padding: 6px 12px; font-size: 12px;">+ Add VLAN</button>
                </div>

                <div class="form-section">
                    <h3>Exclusions (Do Not Scan)</h3>
                    <div id="exclusion-list">
                        <div class="exclusion-entry" style="display: grid; grid-template-columns: 1fr 2fr auto; gap: 10px; margin-bottom: 10px; align-items: end;">
                            <div class="form-group" style="margin: 0;">
                                <label>IP/Network</label>
                                <input type="text" name="exclusion_target[]" placeholder="192.168.1.1">
                            </div>
                            <div class="form-group" style="margin: 0;">
                                <label>Reason</label>
                                <input type="text" name="exclusion_reason[]" placeholder="Production server">
                            </div>
                            <button type="button" onclick="removeExclusion(this)" style="padding: 8px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;">X</button>
                        </div>
                    </div>
                    <button type="button" class="btn btn-secondary" onclick="addExclusion()" style="padding: 6px 12px; font-size: 12px;">+ Add Exclusion</button>
                </div>

                <div class="form-section">
                    <h3>Scan Settings</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="net_scan_type">Scan Type</label>
                            <select id="net_scan_type" name="scan_type">
                                <option value="quick">Quick Discovery (ping sweep only)</option>
                                <option value="standard" selected>Standard (discovery + port scan)</option>
                                <option value="intense">Intense (OS/service detection)</option>
                                <option value="custom">Custom (specify later)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="net_timing">Timing</label>
                            <select id="net_timing" name="timing">
                                <option value="T2">Polite (T2 - slower, less intrusive)</option>
                                <option value="T3" selected>Normal (T3 - default)</option>
                                <option value="T4">Aggressive (T4 - faster)</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="net_scheduled_time">Scheduled Scan Time</label>
                            <input type="datetime-local" id="net_scheduled_time" name="scheduled_time">
                        </div>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary">Save Network Configuration</button>
                <button type="button" class="btn btn-secondary" onclick="clearNetworkForm()">Clear Form</button>
                <button type="button" class="btn btn-success" onclick="loadNetworkConfigs()">View Saved Configs</button>
            </form>

            <div id="network-result"></div>
            <div id="saved-configs" style="margin-top: 20px;"></div>

            <hr style="margin: 30px 0; border: none; border-top: 2px solid #ddd;">

            <h2 style="color: #2563eb;">Network Scanning</h2>

            <div class="form-section">
                <h3>Quick Network Scan</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="scan_target">Target Network (CIDR)</label>
                        <input type="text" id="scan_target" placeholder="192.168.1.0/24">
                    </div>
                    <div class="form-group">
                        <label for="quick_scan_type">Scan Type</label>
                        <select id="quick_scan_type">
                            <option value="ping">Ping Sweep (fastest)</option>
                            <option value="fast">Fast Port Scan (top 100)</option>
                            <option value="standard">Standard (top 1000)</option>
                            <option value="service">Service Detection</option>
                        </select>
                    </div>
                </div>
                <button type="button" class="btn btn-primary" onclick="runQuickScan()">Run Scan</button>
                <button type="button" class="btn btn-secondary" onclick="detectNetwork()">Auto-Detect Network</button>
            </div>

            <div id="scan-status" style="margin-top: 15px;"></div>

            <div class="form-section">
                <h3>Saved Scan Plans</h3>
                <div id="scan-plans">Click "Load Scan Plans" to view</div>
                <button type="button" class="btn btn-secondary" onclick="loadScanPlans()" style="margin-top: 10px;">Load Scan Plans</button>
            </div>

            <div class="form-section">
                <h3>Scan Results</h3>
                <div id="scan-results">Click "Load Results" to view</div>
                <button type="button" class="btn btn-secondary" onclick="loadScanResults()" style="margin-top: 10px;">Load Results</button>
            </div>

            <hr style="margin: 30px 0; border: none; border-top: 2px solid #ddd;">

            <h2 style="color: #2563eb;">Static IP Management</h2>

            <div class="form-section">
                <h3>Add Static IP Device</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="static_ip">IP Address *</label>
                        <input type="text" id="static_ip" placeholder="192.168.1.100">
                    </div>
                    <div class="form-group">
                        <label for="static_mac">MAC Address</label>
                        <input type="text" id="static_mac" placeholder="AA:BB:CC:DD:EE:FF">
                    </div>
                    <div class="form-group">
                        <label for="static_hostname">Hostname *</label>
                        <input type="text" id="static_hostname" placeholder="server01">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="static_type">Device Type</label>
                        <select id="static_type">
                            <option value="server">Server</option>
                            <option value="workstation">Workstation</option>
                            <option value="printer">Printer</option>
                            <option value="router">Router</option>
                            <option value="switch">Switch</option>
                            <option value="firewall">Firewall</option>
                            <option value="access_point">Access Point</option>
                            <option value="camera">Camera</option>
                            <option value="voip">VoIP Phone</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="static_customer">Customer</label>
                        <input type="text" id="static_customer" placeholder="Customer name">
                    </div>
                    <div class="form-group">
                        <label for="static_location">Location</label>
                        <input type="text" id="static_location" placeholder="Server room, Floor 2">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group" style="flex: 2;">
                        <label for="static_notes">Notes</label>
                        <input type="text" id="static_notes" placeholder="Additional notes">
                    </div>
                </div>
                <button type="button" class="btn btn-primary" onclick="addStaticIP()">Add Device</button>
                <button type="button" class="btn btn-secondary" onclick="clearStaticForm()">Clear</button>
            </div>

            <div id="static-ip-result" style="margin-top: 15px;"></div>

            <div class="form-section">
                <h3>Registered Static IP Devices</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="filter_customer">Filter by Customer</label>
                        <input type="text" id="filter_customer" placeholder="All customers" onkeyup="loadStaticIPs()">
                    </div>
                    <div class="form-group">
                        <label for="filter_type">Filter by Type</label>
                        <select id="filter_type" onchange="loadStaticIPs()">
                            <option value="">All Types</option>
                            <option value="server">Server</option>
                            <option value="workstation">Workstation</option>
                            <option value="printer">Printer</option>
                            <option value="router">Router</option>
                            <option value="switch">Switch</option>
                            <option value="firewall">Firewall</option>
                            <option value="access_point">Access Point</option>
                            <option value="camera">Camera</option>
                            <option value="voip">VoIP Phone</option>
                        </select>
                    </div>
                </div>
                <div id="static-ip-list">Click "Load Devices" to view</div>
                <div style="margin-top: 10px;">
                    <button type="button" class="btn btn-secondary" onclick="loadStaticIPs()">Load Devices</button>
                    <button type="button" class="btn btn-success" onclick="exportStaticIPs()">Export CSV</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            document.querySelectorAll('.panel').forEach(panel => panel.classList.remove('active'));
            document.getElementById(tabName + '-panel').classList.add('active');
            if (tabName === 'contracts') loadContracts();
        }

        function clearForm() {
            document.getElementById('callflow-form').reset();
            document.getElementById('result').innerHTML = '';
        }

        document.getElementById('callflow-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = {};
            formData.forEach((value, key) => {
                if (key === 'numbers_to_port' && value) {
                    data[key] = value.split(',').map(n => n.trim());
                } else {
                    data[key] = value;
                }
            });

            try {
                const response = await fetch('/api/generate-callflow', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (result.success) {
                    document.getElementById('result').innerHTML = `
                        <div class="alert alert-success">
                            <strong>Success!</strong> Call flow document generated.<br>
                            <a href="/download/${result.filename}" target="_blank">Download DOCX</a>
                        </div>
                    `;
                } else {
                    document.getElementById('result').innerHTML = `
                        <div class="alert alert-error"><strong>Error:</strong> ${result.error}</div>
                    `;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = `
                    <div class="alert alert-error"><strong>Error:</strong> ${error.message}</div>
                `;
            }
        });

        async function loadContracts() {
            try {
                const response = await fetch('/api/contracts');
                const data = await response.json();
                let alertsHtml = '';

                if (data.alerts.critical.length > 0) {
                    alertsHtml += '<h4>Critical (30 days or less)</h4><ul class="contract-list">';
                    data.alerts.critical.forEach(c => {
                        alertsHtml += `<li class="contract-item critical"><div><strong>${c.customer_name}</strong> - ${c.contract_type}<br><small>Expires: ${c.end_date}</small></div><span class="badge badge-critical">${c.days_until_expiry} days</span></li>`;
                    });
                    alertsHtml += '</ul>';
                }
                if (data.alerts.warning.length > 0) {
                    alertsHtml += '<h4>Warning (31-60 days)</h4><ul class="contract-list">';
                    data.alerts.warning.forEach(c => {
                        alertsHtml += `<li class="contract-item warning"><div><strong>${c.customer_name}</strong> - ${c.contract_type}<br><small>Expires: ${c.end_date}</small></div><span class="badge badge-warning">${c.days_until_expiry} days</span></li>`;
                    });
                    alertsHtml += '</ul>';
                }
                if (data.alerts.upcoming.length > 0) {
                    alertsHtml += '<h4>Upcoming (61-90 days)</h4><ul class="contract-list">';
                    data.alerts.upcoming.forEach(c => {
                        alertsHtml += `<li class="contract-item upcoming"><div><strong>${c.customer_name}</strong> - ${c.contract_type}<br><small>Expires: ${c.end_date}</small></div><span class="badge badge-success">${c.days_until_expiry} days</span></li>`;
                    });
                    alertsHtml += '</ul>';
                }
                if (!alertsHtml) alertsHtml = '<p>No contracts expiring in the next 90 days.</p>';
                document.getElementById('contract-alerts').innerHTML = alertsHtml;

                let allHtml = '<ul class="contract-list">';
                data.contracts.forEach(c => {
                    allHtml += `<li class="contract-item"><div><strong>${c.customer_name}</strong> - ${c.contract_type}<br><small>${c.start_date} to ${c.end_date}</small></div><span class="badge badge-success">${c.status}</span></li>`;
                });
                allHtml += '</ul>';
                document.getElementById('all-contracts').innerHTML = allHtml;
            } catch (error) {
                document.getElementById('contract-alerts').innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
            }
        }

        async function exportContracts() {
            window.open('/api/contracts/export', '_blank');
        }

        // Network Config Functions
        function addNetwork() {
            const container = document.getElementById('additional-networks');
            const input = document.createElement('input');
            input.type = 'text';
            input.name = 'additional_network[]';
            input.placeholder = '10.0.0.0/24';
            input.style.marginBottom = '5px';
            container.appendChild(input);
        }

        function addVlan() {
            const container = document.getElementById('vlan-list');
            const entry = document.createElement('div');
            entry.className = 'vlan-entry';
            entry.style.cssText = 'display: grid; grid-template-columns: 80px 1fr 1fr 1fr auto; gap: 10px; margin-bottom: 10px; align-items: end;';
            entry.innerHTML = `
                <div class="form-group" style="margin: 0;">
                    <input type="number" name="vlan_id[]" placeholder="10" min="1" max="4094">
                </div>
                <div class="form-group" style="margin: 0;">
                    <input type="text" name="vlan_name[]" placeholder="Management">
                </div>
                <div class="form-group" style="margin: 0;">
                    <input type="text" name="vlan_network[]" placeholder="192.168.10.0/24">
                </div>
                <div class="form-group" style="margin: 0;">
                    <input type="text" name="vlan_gateway[]" placeholder="192.168.10.1">
                </div>
                <button type="button" onclick="removeVlan(this)" style="padding: 8px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;">X</button>
            `;
            container.appendChild(entry);
        }

        function removeVlan(btn) {
            btn.parentElement.remove();
        }

        function addExclusion() {
            const container = document.getElementById('exclusion-list');
            const entry = document.createElement('div');
            entry.className = 'exclusion-entry';
            entry.style.cssText = 'display: grid; grid-template-columns: 1fr 2fr auto; gap: 10px; margin-bottom: 10px; align-items: end;';
            entry.innerHTML = `
                <div class="form-group" style="margin: 0;">
                    <input type="text" name="exclusion_target[]" placeholder="192.168.1.1">
                </div>
                <div class="form-group" style="margin: 0;">
                    <input type="text" name="exclusion_reason[]" placeholder="Production server">
                </div>
                <button type="button" onclick="removeExclusion(this)" style="padding: 8px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;">X</button>
            `;
            container.appendChild(entry);
        }

        function removeExclusion(btn) {
            btn.parentElement.remove();
        }

        function clearNetworkForm() {
            document.getElementById('network-form').reset();
            document.getElementById('network-result').innerHTML = '';
        }

        document.getElementById('network-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);

            // Build structured data
            const data = {
                customer_name: formData.get('customer_name'),
                customer_id: formData.get('customer_id'),
                contact_name: formData.get('contact_name'),
                contact_email: formData.get('contact_email'),
                auth_received: formData.get('auth_received') === 'true',
                auth_reference: formData.get('auth_reference'),
                primary_network: formData.get('primary_network'),
                additional_networks: formData.getAll('additional_network[]').filter(n => n.trim()),
                vlans: [],
                exclusions: [],
                scan_type: formData.get('scan_type'),
                timing: formData.get('timing'),
                scheduled_time: formData.get('scheduled_time')
            };

            // Collect VLANs
            const vlanIds = formData.getAll('vlan_id[]');
            const vlanNames = formData.getAll('vlan_name[]');
            const vlanNetworks = formData.getAll('vlan_network[]');
            const vlanGateways = formData.getAll('vlan_gateway[]');
            for (let i = 0; i < vlanIds.length; i++) {
                if (vlanIds[i] && vlanNetworks[i]) {
                    data.vlans.push({
                        id: parseInt(vlanIds[i]),
                        name: vlanNames[i] || '',
                        network: vlanNetworks[i],
                        gateway: vlanGateways[i] || null
                    });
                }
            }

            // Collect exclusions
            const exclTargets = formData.getAll('exclusion_target[]');
            const exclReasons = formData.getAll('exclusion_reason[]');
            for (let i = 0; i < exclTargets.length; i++) {
                if (exclTargets[i]) {
                    data.exclusions.push({
                        target: exclTargets[i],
                        reason: exclReasons[i] || ''
                    });
                }
            }

            try {
                const response = await fetch('/api/network-config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (result.success) {
                    document.getElementById('network-result').innerHTML = `
                        <div class="alert alert-success">
                            <strong>Success!</strong> Network configuration saved.<br>
                            Config file: ${result.config_file}<br>
                            ${result.scan_plan ? 'Scan plan: ' + result.scan_plan : ''}
                        </div>
                    `;
                } else {
                    document.getElementById('network-result').innerHTML = `
                        <div class="alert alert-error"><strong>Error:</strong> ${result.error}</div>
                    `;
                }
            } catch (error) {
                document.getElementById('network-result').innerHTML = `
                    <div class="alert alert-error"><strong>Error:</strong> ${error.message}</div>
                `;
            }
        });

        async function loadNetworkConfigs() {
            try {
                const response = await fetch('/api/network-configs');
                const data = await response.json();

                if (data.configs.length === 0) {
                    document.getElementById('saved-configs').innerHTML = '<p>No saved configurations found.</p>';
                    return;
                }

                let html = '<h4>Saved Configurations</h4><ul class="contract-list">';
                data.configs.forEach(c => {
                    html += `
                        <li class="contract-item">
                            <div>
                                <strong>${c.customer_name}</strong><br>
                                <small>Network: ${c.primary_network} | VLANs: ${c.vlan_count} | Created: ${c.created_date}</small>
                            </div>
                            <span class="badge badge-success">${c.scan_type}</span>
                        </li>
                    `;
                });
                html += '</ul>';
                document.getElementById('saved-configs').innerHTML = html;
            } catch (error) {
                document.getElementById('saved-configs').innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
            }
        }

        // Network Scanning Functions
        async function runQuickScan() {
            const target = document.getElementById('scan_target').value;
            const scanType = document.getElementById('quick_scan_type').value;

            if (!target) {
                document.getElementById('scan-status').innerHTML = '<div class="alert alert-error">Please enter a target network (e.g., 192.168.1.0/24)</div>';
                return;
            }

            document.getElementById('scan-status').innerHTML = '<div class="alert alert-info">Scan started... This may take a few minutes.</div>';

            try {
                const response = await fetch('/api/run-scan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ target, scan_type: scanType })
                });
                const result = await response.json();

                if (result.success) {
                    document.getElementById('scan-status').innerHTML = `
                        <div class="alert alert-success">
                            <strong>Scan Complete!</strong><br>
                            Target: ${result.target}<br>
                            Output: ${result.output_dir}<br>
                            <pre style="margin-top: 10px; max-height: 300px; overflow-y: auto; background: #f5f5f5; padding: 10px; border-radius: 4px;">${result.output}</pre>
                        </div>
                    `;
                } else {
                    document.getElementById('scan-status').innerHTML = `<div class="alert alert-error"><strong>Error:</strong> ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('scan-status').innerHTML = `<div class="alert alert-error"><strong>Error:</strong> ${error.message}</div>`;
            }
        }

        async function detectNetwork() {
            document.getElementById('scan-status').innerHTML = '<div class="alert alert-info">Detecting network...</div>';

            try {
                const response = await fetch('/api/detect-network');
                const result = await response.json();

                if (result.success) {
                    document.getElementById('scan_target').value = result.network;
                    document.getElementById('scan-status').innerHTML = `
                        <div class="alert alert-success">
                            <strong>Network Detected!</strong><br>
                            Interface: ${result.interface}<br>
                            Your IP: ${result.ip}<br>
                            Network: ${result.network}<br>
                            Gateway: ${result.gateway || 'N/A'}
                        </div>
                    `;
                } else {
                    document.getElementById('scan-status').innerHTML = `<div class="alert alert-error"><strong>Error:</strong> ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('scan-status').innerHTML = `<div class="alert alert-error"><strong>Error:</strong> ${error.message}</div>`;
            }
        }

        async function loadScanPlans() {
            try {
                const response = await fetch('/api/scan-plans');
                const data = await response.json();

                if (data.plans.length === 0) {
                    document.getElementById('scan-plans').innerHTML = '<p>No scan plans found.</p>';
                    return;
                }

                let html = '<ul class="contract-list">';
                data.plans.forEach(p => {
                    html += `
                        <li class="contract-item">
                            <div>
                                <strong>${p.name}</strong><br>
                                <small>Created: ${p.created}</small>
                            </div>
                            <button class="btn btn-primary" onclick="runScanPlan('${p.filename}')" style="padding: 6px 12px; font-size: 12px;">Run</button>
                        </li>
                    `;
                });
                html += '</ul>';
                document.getElementById('scan-plans').innerHTML = html;
            } catch (error) {
                document.getElementById('scan-plans').innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
            }
        }

        async function runScanPlan(filename) {
            document.getElementById('scan-status').innerHTML = '<div class="alert alert-info">Running scan plan... This may take several minutes.</div>';

            try {
                const response = await fetch('/api/run-scan-plan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ filename })
                });
                const result = await response.json();

                if (result.success) {
                    document.getElementById('scan-status').innerHTML = `
                        <div class="alert alert-success">
                            <strong>Scan Plan Executed!</strong><br>
                            <pre style="margin-top: 10px; max-height: 300px; overflow-y: auto; background: #f5f5f5; padding: 10px; border-radius: 4px;">${result.output}</pre>
                        </div>
                    `;
                } else {
                    document.getElementById('scan-status').innerHTML = `<div class="alert alert-error"><strong>Error:</strong> ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('scan-status').innerHTML = `<div class="alert alert-error"><strong>Error:</strong> ${error.message}</div>`;
            }
        }

        async function loadScanResults() {
            try {
                const response = await fetch('/api/scan-results');
                const data = await response.json();

                if (data.results.length === 0) {
                    document.getElementById('scan-results').innerHTML = '<p>No scan results found.</p>';
                    return;
                }

                let html = '<ul class="contract-list">';
                data.results.forEach(r => {
                    html += `
                        <li class="contract-item">
                            <div>
                                <strong>${r.name}</strong><br>
                                <small>${r.files} files | ${r.date}</small>
                            </div>
                            <button class="btn btn-secondary" onclick="viewScanResult('${r.path}')" style="padding: 6px 12px; font-size: 12px;">View</button>
                        </li>
                    `;
                });
                html += '</ul>';
                document.getElementById('scan-results').innerHTML = html;
            } catch (error) {
                document.getElementById('scan-results').innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
            }
        }

        async function viewScanResult(path) {
            try {
                const response = await fetch('/api/view-scan-result?path=' + encodeURIComponent(path));
                const data = await response.json();

                if (data.success) {
                    document.getElementById('scan-status').innerHTML = `
                        <div class="alert alert-success">
                            <strong>Scan Result: ${data.name}</strong><br>
                            <pre style="margin-top: 10px; max-height: 400px; overflow-y: auto; background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">${data.content}</pre>
                        </div>
                    `;
                } else {
                    document.getElementById('scan-status').innerHTML = `<div class="alert alert-error"><strong>Error:</strong> ${data.error}</div>`;
                }
            } catch (error) {
                document.getElementById('scan-status').innerHTML = `<div class="alert alert-error"><strong>Error:</strong> ${error.message}</div>`;
            }
        }

        // Static IP Management Functions
        function clearStaticForm() {
            document.getElementById('static_ip').value = '';
            document.getElementById('static_mac').value = '';
            document.getElementById('static_hostname').value = '';
            document.getElementById('static_type').value = 'server';
            document.getElementById('static_customer').value = '';
            document.getElementById('static_location').value = '';
            document.getElementById('static_notes').value = '';
        }

        async function addStaticIP() {
            const ip = document.getElementById('static_ip').value;
            const hostname = document.getElementById('static_hostname').value;

            if (!ip || !hostname) {
                document.getElementById('static-ip-result').innerHTML = '<div class="alert alert-error">IP Address and Hostname are required</div>';
                return;
            }

            const data = {
                ip_address: ip,
                mac_address: document.getElementById('static_mac').value,
                hostname: hostname,
                device_type: document.getElementById('static_type').value,
                customer: document.getElementById('static_customer').value,
                location: document.getElementById('static_location').value,
                notes: document.getElementById('static_notes').value
            };

            try {
                const response = await fetch('/api/static-ip', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();

                if (result.success) {
                    document.getElementById('static-ip-result').innerHTML = `<div class="alert alert-success">Device added: ${hostname} (${ip})</div>`;
                    clearStaticForm();
                    loadStaticIPs();
                } else {
                    document.getElementById('static-ip-result').innerHTML = `<div class="alert alert-error">${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('static-ip-result').innerHTML = `<div class="alert alert-error">${error.message}</div>`;
            }
        }

        async function loadStaticIPs() {
            const customerFilter = document.getElementById('filter_customer').value;
            const typeFilter = document.getElementById('filter_type').value;

            try {
                let url = '/api/static-ips';
                const params = new URLSearchParams();
                if (customerFilter) params.append('customer', customerFilter);
                if (typeFilter) params.append('type', typeFilter);
                if (params.toString()) url += '?' + params.toString();

                const response = await fetch(url);
                const data = await response.json();

                if (data.devices.length === 0) {
                    document.getElementById('static-ip-list').innerHTML = '<p>No devices found.</p>';
                    return;
                }

                let html = '<table style="width: 100%; border-collapse: collapse; font-size: 13px;">';
                html += '<tr style="background: #f5f5f5;"><th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">IP</th><th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Hostname</th><th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Type</th><th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Customer</th><th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Location</th><th style="padding: 8px; border-bottom: 2px solid #ddd;">Actions</th></tr>';

                data.devices.forEach(d => {
                    html += `<tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>${d.ip_address}</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">${d.hostname}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><span class="badge badge-success">${d.device_type}</span></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">${d.customer || '-'}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">${d.location || '-'}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><button onclick="deleteStaticIP('${d.id}')" style="padding: 4px 8px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;">Delete</button></td>
                    </tr>`;
                });
                html += '</table>';
                document.getElementById('static-ip-list').innerHTML = html;
            } catch (error) {
                document.getElementById('static-ip-list').innerHTML = `<div class="alert alert-error">${error.message}</div>`;
            }
        }

        async function deleteStaticIP(id) {
            if (!confirm('Delete this device?')) return;

            try {
                const response = await fetch('/api/static-ip/' + id, { method: 'DELETE' });
                const result = await response.json();

                if (result.success) {
                    loadStaticIPs();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        async function exportStaticIPs() {
            window.open('/api/static-ips/export', '_blank');
        }
    </script>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in USERS and check_password_hash(USERS[username]['password'], password):
            user = User(username)
            login_user(user)
            flash('Logged in successfully.', 'info')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template_string(HTML_TEMPLATE, current_user=current_user)

@app.route('/api/generate-callflow', methods=['POST'])
@login_required
def generate_callflow():
    try:
        data = request.json
        output_path = generator.create_call_flow(data)
        return jsonify({
            'success': True,
            'filename': output_path.name,
            'path': str(output_path)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    file_path = Path('call_flows_generated') / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route('/api/contracts')
@login_required
def get_contracts():
    alerts = tracker.get_renewal_alerts()
    return jsonify({
        'alerts': alerts,
        'contracts': tracker.list_all()
    })

@app.route('/api/contracts/export')
@login_required
def export_contracts():
    csv_path = tracker.export_to_csv()
    return send_file(csv_path, as_attachment=True)

@app.route('/api/network-config', methods=['POST'])
@login_required
def save_network_config():
    try:
        data = request.json

        # Build configuration structure
        config = {
            "customer": {
                "name": data['customer_name'],
                "id": data.get('customer_id'),
                "contact": {
                    "name": data['contact_name'],
                    "email": data['contact_email']
                },
                "authorization": {
                    "received": data.get('auth_received', False),
                    "reference": data.get('auth_reference'),
                    "date": datetime.now().isoformat()
                }
            },
            "network": {
                "primary": data['primary_network'],
                "additional": data.get('additional_networks', []),
                "vlans": data.get('vlans', [])
            },
            "exclusions": data.get('exclusions', []),
            "scan_config": {
                "type": data.get('scan_type', 'standard'),
                "timing": data.get('timing', 'T3'),
                "scheduled_time": data.get('scheduled_time')
            },
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "created_by": current_user.id,
                "version": "1.0"
            }
        }

        # Create safe filename
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', data['customer_name'].lower())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.json"
        filepath = NETWORK_CONFIG_DIR / filename

        # Save config file
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)

        # Create exclusion file if needed
        if config['exclusions']:
            excl_filename = f"{safe_name}_{timestamp}_exclude.txt"
            excl_filepath = NETWORK_CONFIG_DIR / excl_filename
            with open(excl_filepath, 'w') as f:
                f.write(f"# Exclusion list for {config['customer']['name']}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                for excl in config['exclusions']:
                    f.write(f"{excl['target']}    # {excl['reason']}\n")

        # Create scan plan script
        scan_plan_file = create_scan_plan(config, safe_name, timestamp)

        return jsonify({
            'success': True,
            'config_file': filename,
            'scan_plan': scan_plan_file
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def create_scan_plan(config, safe_name, timestamp):
    """Create executable scan plan script"""
    plan_filename = f"{safe_name}_{timestamp}_scan_plan.sh"
    plan_filepath = NETWORK_CONFIG_DIR / plan_filename

    with open(plan_filepath, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write(f"# Scan Plan for {config['customer']['name']}\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n\n")

        f.write("echo '======================================'\n")
        f.write(f"echo 'Scan Plan: {config['customer']['name']}'\n")
        f.write("echo '======================================'\n")
        f.write("echo ''\n\n")

        # Build scan command based on type
        scan_type = config['scan_config']['type']
        timing = config['scan_config']['timing']

        scan_flags = f"-{timing} -v"
        if scan_type == "quick":
            scan_flags += " -sn"
        elif scan_type == "standard":
            scan_flags += " -sV"
        elif scan_type == "intense":
            scan_flags += " -A"

        # Primary network
        output_base = f"{NETWORK_CONFIG_DIR}/{safe_name}_{timestamp}_primary"
        f.write(f"# Primary Network: {config['network']['primary']}\n")
        f.write(f"echo 'Scanning primary network: {config['network']['primary']}...'\n")
        f.write(f"nmap {scan_flags} {config['network']['primary']} -oA {output_base}\n\n")

        # Additional networks
        for idx, network in enumerate(config['network']['additional'], 1):
            output_base = f"{NETWORK_CONFIG_DIR}/{safe_name}_{timestamp}_additional_{idx}"
            f.write(f"# Additional Network {idx}: {network}\n")
            f.write(f"echo 'Scanning additional network: {network}...'\n")
            f.write(f"nmap {scan_flags} {network} -oA {output_base}\n\n")

        # VLANs
        for vlan in config['network']['vlans']:
            output_base = f"{NETWORK_CONFIG_DIR}/{safe_name}_{timestamp}_vlan_{vlan['id']}"
            f.write(f"# VLAN {vlan['id']}: {vlan['name']} - {vlan['network']}\n")
            f.write(f"echo 'Scanning VLAN {vlan['id']} ({vlan['name']}): {vlan['network']}...'\n")
            f.write(f"nmap {scan_flags} {vlan['network']} -oA {output_base}\n\n")

        f.write("echo ''\n")
        f.write("echo '======================================'\n")
        f.write("echo 'All scans complete!'\n")
        f.write("echo '======================================'\n")

    os.chmod(plan_filepath, 0o755)
    return plan_filename

@app.route('/api/network-configs')
@login_required
def list_network_configs():
    try:
        configs = []
        for config_file in sorted(NETWORK_CONFIG_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
            with open(config_file, 'r') as f:
                config = json.load(f)

            configs.append({
                'filename': config_file.name,
                'customer_name': config['customer']['name'],
                'primary_network': config['network']['primary'],
                'vlan_count': len(config['network'].get('vlans', [])),
                'scan_type': config['scan_config']['type'],
                'created_date': config['metadata']['created_date'][:19]
            })

        return jsonify({'configs': configs})
    except Exception as e:
        return jsonify({'configs': [], 'error': str(e)})

@app.route('/api/detect-network')
@login_required
def detect_network():
    try:
        # Get default route interface
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        default_line = [l for l in result.stdout.split('\n') if 'default' in l]

        if not default_line:
            return jsonify({'success': False, 'error': 'No default route found'})

        parts = default_line[0].split()
        gateway = parts[2] if len(parts) > 2 else None
        interface = parts[4] if len(parts) > 4 else None

        # Get IP for interface
        result = subprocess.run(['ip', 'addr', 'show', interface], capture_output=True, text=True)
        ip_line = [l for l in result.stdout.split('\n') if 'inet ' in l and '127.0.0.1' not in l]

        if not ip_line:
            return jsonify({'success': False, 'error': 'No IP address found'})

        ip_cidr = ip_line[0].strip().split()[1]
        ip = ip_cidr.split('/')[0]

        # Calculate network
        network = str(ipaddress.ip_interface(ip_cidr).network)

        return jsonify({
            'success': True,
            'interface': interface,
            'ip': ip,
            'network': network,
            'gateway': gateway
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/run-scan', methods=['POST'])
@login_required
def run_scan():
    try:
        data = request.json
        target = data['target']
        scan_type = data.get('scan_type', 'ping')

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = SCANS_DIR / f"web_scan_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build nmap command based on scan type
        if scan_type == 'ping':
            cmd = ['nmap', '-sn', '-n', target, '-oA', str(output_dir / 'scan')]
        elif scan_type == 'fast':
            cmd = ['nmap', '-F', '-T4', target, '-oA', str(output_dir / 'scan')]
        elif scan_type == 'standard':
            cmd = ['nmap', '-T3', target, '-oA', str(output_dir / 'scan')]
        elif scan_type == 'service':
            cmd = ['nmap', '-sV', '-T3', target, '-oA', str(output_dir / 'scan')]
        else:
            cmd = ['nmap', '-sn', target, '-oA', str(output_dir / 'scan')]

        # Run scan with timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        return jsonify({
            'success': True,
            'target': target,
            'output_dir': str(output_dir),
            'output': result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Scan timed out (5 minute limit)'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/scan-plans')
@login_required
def list_scan_plans():
    try:
        plans = []
        for plan_file in sorted(NETWORK_CONFIG_DIR.glob("*_scan_plan.sh"), key=os.path.getmtime, reverse=True):
            stat = plan_file.stat()
            plans.append({
                'filename': plan_file.name,
                'name': plan_file.stem.replace('_scan_plan', '').replace('_', ' ').title(),
                'created': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            })
        return jsonify({'plans': plans})
    except Exception as e:
        return jsonify({'plans': [], 'error': str(e)})

@app.route('/api/run-scan-plan', methods=['POST'])
@login_required
def run_scan_plan():
    try:
        data = request.json
        filename = data['filename']
        plan_path = NETWORK_CONFIG_DIR / filename

        if not plan_path.exists():
            return jsonify({'success': False, 'error': 'Scan plan not found'})

        # Run scan plan with timeout
        result = subprocess.run(['bash', str(plan_path)], capture_output=True, text=True, timeout=600)

        return jsonify({
            'success': True,
            'output': result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Scan plan timed out (10 minute limit)'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/scan-results')
@login_required
def list_scan_results():
    try:
        results = []

        # Check scans directory for subdirectories
        if SCANS_DIR.exists():
            for scan_dir in sorted(SCANS_DIR.iterdir(), key=os.path.getmtime, reverse=True):
                if scan_dir.is_dir() and not scan_dir.name.startswith('.'):
                    files = list(scan_dir.glob('*.nmap'))
                    if files:
                        stat = scan_dir.stat()
                        results.append({
                            'name': scan_dir.name,
                            'path': str(scan_dir),
                            'files': len(files),
                            'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                        })

        return jsonify({'results': results[:20]})  # Limit to 20 most recent
    except Exception as e:
        return jsonify({'results': [], 'error': str(e)})

@app.route('/api/view-scan-result')
@login_required
def view_scan_result():
    try:
        path = request.args.get('path')
        scan_dir = Path(path)

        if not scan_dir.exists() or not scan_dir.is_dir():
            return jsonify({'success': False, 'error': 'Scan result not found'})

        # Find .nmap files and read the first one
        nmap_files = list(scan_dir.glob('*.nmap'))
        if not nmap_files:
            return jsonify({'success': False, 'error': 'No scan output files found'})

        # Read the first nmap file (or concatenate all)
        content = ""
        for nmap_file in sorted(nmap_files)[:3]:  # Limit to first 3 files
            content += f"\n=== {nmap_file.name} ===\n"
            with open(nmap_file, 'r') as f:
                file_content = f.read()
                content += file_content[-5000:] if len(file_content) > 5000 else file_content

        return jsonify({
            'success': True,
            'name': scan_dir.name,
            'content': content
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/static-ip', methods=['POST'])
@login_required
def add_static_ip():
    try:
        data = request.json
        registry = load_static_ips()

        # Generate unique ID
        import uuid
        device_id = str(uuid.uuid4())[:8]

        device = {
            'id': device_id,
            'ip_address': data['ip_address'],
            'mac_address': data.get('mac_address', ''),
            'hostname': data['hostname'],
            'device_type': data.get('device_type', 'other'),
            'customer': data.get('customer', ''),
            'location': data.get('location', ''),
            'notes': data.get('notes', ''),
            'created_date': datetime.now().isoformat(),
            'created_by': current_user.id
        }

        registry['devices'].append(device)
        save_static_ips(registry)

        return jsonify({'success': True, 'id': device_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/static-ips')
@login_required
def list_static_ips():
    try:
        registry = load_static_ips()
        devices = registry['devices']

        # Apply filters
        customer_filter = request.args.get('customer', '').lower()
        type_filter = request.args.get('type', '')

        if customer_filter:
            devices = [d for d in devices if customer_filter in d.get('customer', '').lower()]
        if type_filter:
            devices = [d for d in devices if d.get('device_type') == type_filter]

        # Sort by IP address
        devices.sort(key=lambda x: [int(p) for p in x['ip_address'].split('.')] if '.' in x['ip_address'] else [0])

        return jsonify({'devices': devices})
    except Exception as e:
        return jsonify({'devices': [], 'error': str(e)})

@app.route('/api/static-ip/<device_id>', methods=['DELETE'])
@login_required
def delete_static_ip(device_id):
    try:
        registry = load_static_ips()
        registry['devices'] = [d for d in registry['devices'] if d['id'] != device_id]
        save_static_ips(registry)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/static-ips/export')
@login_required
def export_static_ips():
    try:
        registry = load_static_ips()
        devices = registry['devices']

        # Create CSV
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['IP Address', 'MAC Address', 'Hostname', 'Device Type', 'Customer', 'Location', 'Notes', 'Created Date'])

        for d in devices:
            writer.writerow([
                d['ip_address'],
                d.get('mac_address', ''),
                d['hostname'],
                d.get('device_type', ''),
                d.get('customer', ''),
                d.get('location', ''),
                d.get('notes', ''),
                d.get('created_date', '')[:19]
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'static_ip_registry_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    print("\n" + "=" * 50)
    print("OberaConnect Tools Web Interface (Authenticated)")
    print("=" * 50)
    print("\nDefault credentials:")
    print("  Admin: admin / oberaconnect2025")
    print("  User:  user / oberatools")
    print("\nChange these passwords in users.json!")
    print("\nStarting server...")
    print("Open in browser: https://localhost:443")
    print("\nPress Ctrl+C to stop\n")

    app.run(host='0.0.0.0', port=443, ssl_context=(
        '/home/mavrick/Projects/Secondbrain/ssl/server.crt',
        '/home/mavrick/Projects/Secondbrain/ssl/server.key'
    ))

if __name__ == '__main__':
    main()
