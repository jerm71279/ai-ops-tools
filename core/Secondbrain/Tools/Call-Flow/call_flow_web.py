import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Call Flow Web Interface - OberaConnect
Web-based interface for creating and managing call flow configurations
"""

from flask import Flask, render_template_string, request, jsonify, send_file
from call_flow_generator import CallFlowGenerator
from contract_tracker import ContractTracker
from pathlib import Path
import json

app = Flask(__name__)
generator = CallFlowGenerator()
tracker = ContractTracker()

# HTML Template with embedded CSS
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
        }
        header h1 {
            margin: 0;
            font-size: 24px;
        }
        header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
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
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>OberaConnect Tools</h1>
            <p>Call Flow Generator & Contract Tracker</p>
        </header>

        <div class="tabs">
            <div class="tab active" onclick="showTab('callflow')">Call Flow Generator</div>
            <div class="tab" onclick="showTab('contracts')">Contract Tracker</div>
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
                            <label for="portal_access">ConnectWare Portal Access (who needs it?)</label>
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
                            <textarea id="business_hours_routing" name="business_hours_routing" placeholder="Ring all phones, then voicemail"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="after_hours_routing">After Hours Routing</label>
                            <textarea id="after_hours_routing" name="after_hours_routing" placeholder="Straight to voicemail"></textarea>
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
            <div id="contract-alerts">
                Loading contracts...
            </div>

            <h3 style="margin-top: 30px;">All Active Contracts</h3>
            <div id="all-contracts">
                Loading...
            </div>

            <div style="margin-top: 20px;">
                <button class="btn btn-success" onclick="exportContracts()">Export to CSV</button>
                <button class="btn btn-secondary" onclick="loadContracts()">Refresh</button>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Update tabs
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');

            // Update panels
            document.querySelectorAll('.panel').forEach(panel => panel.classList.remove('active'));
            document.getElementById(tabName + '-panel').classList.add('active');

            // Load contracts when switching to that tab
            if (tabName === 'contracts') {
                loadContracts();
            }
        }

        function clearForm() {
            document.getElementById('callflow-form').reset();
            document.getElementById('result').innerHTML = '';
        }

        // Handle form submission
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
                        <div class="alert alert-error">
                            <strong>Error:</strong> ${result.error}
                        </div>
                    `;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = `
                    <div class="alert alert-error">
                        <strong>Error:</strong> ${error.message}
                    </div>
                `;
            }
        });

        async function loadContracts() {
            try {
                const response = await fetch('/api/contracts');
                const data = await response.json();

                // Display alerts
                let alertsHtml = '';

                if (data.alerts.critical.length > 0) {
                    alertsHtml += '<h4>Critical (30 days or less)</h4><ul class="contract-list">';
                    data.alerts.critical.forEach(c => {
                        alertsHtml += `
                            <li class="contract-item critical">
                                <div>
                                    <strong>${c.customer_name}</strong> - ${c.contract_type}<br>
                                    <small>Expires: ${c.end_date}</small>
                                </div>
                                <span class="badge badge-critical">${c.days_until_expiry} days</span>
                            </li>
                        `;
                    });
                    alertsHtml += '</ul>';
                }

                if (data.alerts.warning.length > 0) {
                    alertsHtml += '<h4>Warning (31-60 days)</h4><ul class="contract-list">';
                    data.alerts.warning.forEach(c => {
                        alertsHtml += `
                            <li class="contract-item warning">
                                <div>
                                    <strong>${c.customer_name}</strong> - ${c.contract_type}<br>
                                    <small>Expires: ${c.end_date}</small>
                                </div>
                                <span class="badge badge-warning">${c.days_until_expiry} days</span>
                            </li>
                        `;
                    });
                    alertsHtml += '</ul>';
                }

                if (data.alerts.upcoming.length > 0) {
                    alertsHtml += '<h4>Upcoming (61-90 days)</h4><ul class="contract-list">';
                    data.alerts.upcoming.forEach(c => {
                        alertsHtml += `
                            <li class="contract-item upcoming">
                                <div>
                                    <strong>${c.customer_name}</strong> - ${c.contract_type}<br>
                                    <small>Expires: ${c.end_date}</small>
                                </div>
                                <span class="badge badge-success">${c.days_until_expiry} days</span>
                            </li>
                        `;
                    });
                    alertsHtml += '</ul>';
                }

                if (!alertsHtml) {
                    alertsHtml = '<p>No contracts expiring in the next 90 days.</p>';
                }

                document.getElementById('contract-alerts').innerHTML = alertsHtml;

                // Display all contracts
                let allHtml = '<ul class="contract-list">';
                data.contracts.forEach(c => {
                    allHtml += `
                        <li class="contract-item">
                            <div>
                                <strong>${c.customer_name}</strong> - ${c.contract_type}<br>
                                <small>${c.start_date} to ${c.end_date}</small>
                            </div>
                            <span class="badge badge-success">${c.status}</span>
                        </li>
                    `;
                });
                allHtml += '</ul>';
                document.getElementById('all-contracts').innerHTML = allHtml;

            } catch (error) {
                document.getElementById('contract-alerts').innerHTML = `
                    <div class="alert alert-error">Error loading contracts: ${error.message}</div>
                `;
            }
        }

        async function exportContracts() {
            window.open('/api/contracts/export', '_blank');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/generate-callflow', methods=['POST'])
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
def download_file(filename):
    file_path = Path('call_flows_generated') / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return "File not found", 404


@app.route('/api/contracts')
def get_contracts():
    alerts = tracker.get_renewal_alerts()
    return jsonify({
        'alerts': alerts,
        'contracts': tracker.list_all()
    })


@app.route('/api/contracts/export')
def export_contracts():
    csv_path = tracker.export_to_csv()
    return send_file(csv_path, as_attachment=True)


def main():
    print("\n" + "=" * 50)
    print("OberaConnect Tools Web Interface")
    print("=" * 50)
    print("\nStarting server...")
    print("Open in browser: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")

    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
