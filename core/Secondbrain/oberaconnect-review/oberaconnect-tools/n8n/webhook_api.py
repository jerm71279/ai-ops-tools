"""
n8n Webhook API

Flask REST API for n8n workflow integration.

Provides endpoints for:
- UniFi fleet queries
- NinjaOne alert access
- Cross-platform correlation
- Health checks (Kubernetes-compatible /health and /ready)
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime, timezone

from flask import Flask, request, jsonify


logger = logging.getLogger(__name__)

# Track server start time for uptime calculation
_start_time = time.time()
_version = "1.0.0"


def _format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or not parts:
        parts.append(f"{minutes}m")

    return " ".join(parts)


def create_app(
    unifi_client=None,
    ninjaone_client=None,
    correlator=None
) -> Flask:
    """
    Create Flask application with all endpoints.
    
    Args:
        unifi_client: UniFi API client instance
        ninjaone_client: NinjaOne API client instance
        correlator: Cross-platform correlator instance
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-me')
    
    # Store clients on app context
    app.unifi_client = unifi_client
    app.ninjaone_client = ninjaone_client
    app.correlator = correlator
    
    # Lazy imports to avoid circular dependencies
    _unifi_analyzer = None
    
    def get_unifi_analyzer():
        nonlocal _unifi_analyzer
        if _unifi_analyzer is None and app.unifi_client:
            from unifi import UniFiAnalyzer
            sites = app.unifi_client.get_sites()
            _unifi_analyzer = UniFiAnalyzer(sites)
        return _unifi_analyzer
    
    # ========== Health Endpoints ==========

    @app.route('/health', methods=['GET'])
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Liveness probe - is the server running?

        Returns 200 if the server is alive.
        Used by Kubernetes liveness probes and load balancers.
        """
        uptime_seconds = time.time() - _start_time
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': _version,
            'uptime_seconds': round(uptime_seconds, 2),
            'uptime_human': _format_uptime(uptime_seconds)
        })

    @app.route('/ready', methods=['GET'])
    @app.route('/api/ready', methods=['GET'])
    def readiness_check():
        """
        Readiness probe - can the server handle requests?

        Checks connectivity to all backend services.
        Returns 200 if ready, 503 if not.
        Used by Kubernetes readiness probes.
        """
        checks = {}
        all_ready = True

        # Check UniFi client
        if app.unifi_client:
            try:
                # Test by checking if we can get sites
                if hasattr(app.unifi_client, 'test_connection'):
                    checks['unifi'] = app.unifi_client.test_connection()
                else:
                    checks['unifi'] = True
            except Exception as e:
                checks['unifi'] = False
                checks['unifi_error'] = str(e)
                all_ready = False
        else:
            checks['unifi'] = None  # Not configured

        # Check NinjaOne client
        if app.ninjaone_client:
            try:
                if hasattr(app.ninjaone_client, 'test_connection'):
                    checks['ninjaone'] = app.ninjaone_client.test_connection()
                else:
                    checks['ninjaone'] = True
            except Exception as e:
                checks['ninjaone'] = False
                checks['ninjaone_error'] = str(e)
                all_ready = False
        else:
            checks['ninjaone'] = None  # Not configured

        # Check correlator
        checks['correlator'] = app.correlator is not None

        # Build response
        response = {
            'ready': all_ready,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'checks': checks
        }

        status_code = 200 if all_ready else 503
        return jsonify(response), status_code

    @app.route('/metrics', methods=['GET'])
    @app.route('/api/metrics', methods=['GET'])
    def metrics():
        """
        Basic metrics endpoint for monitoring.

        Returns key operational metrics in JSON format.
        For Prometheus, consider using prometheus_flask_exporter.
        """
        uptime_seconds = time.time() - _start_time

        metrics_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': _version,
            'uptime_seconds': round(uptime_seconds, 2),
            'services': {
                'unifi_configured': app.unifi_client is not None,
                'ninjaone_configured': app.ninjaone_client is not None,
                'correlator_configured': app.correlator is not None
            }
        }

        # Add site/device counts if available
        if app.unifi_client:
            try:
                sites = app.unifi_client.get_sites()
                metrics_data['unifi'] = {
                    'site_count': len(sites),
                    'total_devices': sum(s.device_count for s in sites),
                    'offline_devices': sum(s.offline_device_count for s in sites)
                }
            except Exception:
                metrics_data['unifi'] = {'error': 'Failed to fetch metrics'}

        if app.ninjaone_client:
            try:
                if hasattr(app.ninjaone_client, 'get_alerts'):
                    alerts = app.ninjaone_client.get_alerts()
                    critical = [a for a in alerts if a.severity == 'CRITICAL']
                    metrics_data['ninjaone'] = {
                        'total_alerts': len(alerts),
                        'critical_alerts': len(critical)
                    }
            except Exception:
                metrics_data['ninjaone'] = {'error': 'Failed to fetch metrics'}

        return jsonify(metrics_data)

    # ========== UniFi Endpoints ==========
    
    @app.route('/api/unifi/query', methods=['POST'])
    def unifi_query():
        """
        Execute natural language query against UniFi fleet.
        
        Request body:
            {"query": "show sites with offline devices"}
        
        Returns:
            Query result with matching sites
        """
        analyzer = get_unifi_analyzer()
        if not analyzer:
            return jsonify({'error': 'UniFi client not configured'}), 503
        
        data = request.get_json() or {}
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        try:
            result = analyzer.analyze(query)
            return jsonify(result.to_dict())
        except Exception as e:
            logger.error(f"Query error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/unifi/sites', methods=['GET'])
    def unifi_sites():
        """Get all UniFi sites."""
        if not app.unifi_client:
            return jsonify({'error': 'UniFi client not configured'}), 503
        
        try:
            sites = app.unifi_client.get_sites()
            return jsonify({
                'count': len(sites),
                'sites': [s.to_dict() for s in sites]
            })
        except Exception as e:
            logger.error(f"Sites error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/unifi/sites/<site_id>', methods=['GET'])
    def unifi_site(site_id: str):
        """Get specific UniFi site."""
        if not app.unifi_client:
            return jsonify({'error': 'UniFi client not configured'}), 503
        
        try:
            site = app.unifi_client.get_site(site_id)
            if not site:
                return jsonify({'error': 'Site not found'}), 404
            return jsonify(site.to_dict())
        except Exception as e:
            logger.error(f"Site error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/unifi/summary', methods=['GET'])
    def unifi_summary():
        """Get fleet summary."""
        if not app.unifi_client:
            return jsonify({'error': 'UniFi client not configured'}), 503
        
        try:
            summary = app.unifi_client.get_fleet_summary()
            return jsonify(summary.to_dict())
        except Exception as e:
            logger.error(f"Summary error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/unifi/offline', methods=['GET'])
    def unifi_offline():
        """Get sites with offline devices."""
        analyzer = get_unifi_analyzer()
        if not analyzer:
            return jsonify({'error': 'UniFi client not configured'}), 503
        
        try:
            result = analyzer.analyze("sites with offline devices")
            return jsonify(result.to_dict())
        except Exception as e:
            logger.error(f"Offline error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/unifi/validate', methods=['POST'])
    def unifi_validate():
        """
        Validate a proposed UniFi operation.
        
        Request body:
            {
                "action": "ssid_create",
                "sites": ["site-001", "site-002"],
                "plan": {"ssid": "Guest", "security": "wpa2"}
            }
        
        Returns:
            Validation result with any issues/suggestions
        """
        from common import validate_operation
        from unifi.checkers import get_unifi_checkers
        
        data = request.get_json() or {}
        
        action = data.get('action', '')
        sites = data.get('sites', [])
        plan = data.get('plan', {})
        
        if not action:
            return jsonify({'error': 'Missing action parameter'}), 400
        
        try:
            result = validate_operation(
                action=action,
                sites=sites,
                plan=plan,
                extra_checkers=get_unifi_checkers()
            )
            
            return jsonify({
                'canProceed': result.can_proceed,
                'needsApproval': result.needs_approval,
                'blocked': result.blocked,
                'result': result.overall_result.name,
                'riskLevel': result.risk_level.name,
                'issues': result.all_issues,
                'suggestions': result.all_suggestions,
                'riskFlags': result.all_risk_flags
            })
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ========== NinjaOne Endpoints ==========
    
    @app.route('/api/ninjaone/alerts', methods=['GET'])
    def ninjaone_alerts():
        """Get NinjaOne alerts."""
        if not app.ninjaone_client:
            return jsonify({'error': 'NinjaOne client not configured'}), 503
        
        severity = request.args.get('severity')
        org_id = request.args.get('org_id')
        
        try:
            alerts = app.ninjaone_client.get_alerts(severity=severity, org_id=org_id)
            return jsonify({
                'count': len(alerts),
                'alerts': [a.to_dict() for a in alerts]
            })
        except Exception as e:
            logger.error(f"Alerts error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ninjaone/alerts/critical', methods=['GET'])
    def ninjaone_critical():
        """Get critical NinjaOne alerts."""
        if not app.ninjaone_client:
            return jsonify({'error': 'NinjaOne client not configured'}), 503
        
        try:
            alerts = app.ninjaone_client.get_critical_alerts()
            return jsonify({
                'count': len(alerts),
                'alerts': [a.to_dict() for a in alerts]
            })
        except Exception as e:
            logger.error(f"Critical alerts error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ninjaone/devices', methods=['GET'])
    def ninjaone_devices():
        """Get NinjaOne devices."""
        if not app.ninjaone_client:
            return jsonify({'error': 'NinjaOne client not configured'}), 503
        
        org_id = request.args.get('org_id')
        
        try:
            devices = app.ninjaone_client.get_devices(org_id=org_id)
            return jsonify({
                'count': len(devices),
                'devices': [d.to_dict() for d in devices]
            })
        except Exception as e:
            logger.error(f"Devices error: {e}")
            return jsonify({'error': str(e)}), 500

    # ========== Alert Management Endpoints ==========

    @app.route('/api/ninjaone/alerts/<alert_id>/acknowledge', methods=['POST'])
    def acknowledge_alert(alert_id):
        """Acknowledge an alert by ID."""
        if not app.ninjaone_client:
            return jsonify({'error': 'NinjaOne client not configured'}), 503

        try:
            success = app.ninjaone_client.acknowledge_alert(alert_id)
            if success:
                return jsonify({'success': True, 'message': f'Alert {alert_id} acknowledged'})
            return jsonify({'success': False, 'error': 'Failed to acknowledge alert'}), 500
        except Exception as e:
            logger.error(f"Acknowledge error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ninjaone/alerts/<alert_id>/reset', methods=['POST'])
    def reset_alert(alert_id):
        """Reset/clear an alert by ID."""
        if not app.ninjaone_client:
            return jsonify({'error': 'NinjaOne client not configured'}), 503

        try:
            success = app.ninjaone_client.reset_alert(alert_id)
            if success:
                return jsonify({'success': True, 'message': f'Alert {alert_id} reset'})
            return jsonify({'success': False, 'error': 'Failed to reset alert'}), 500
        except Exception as e:
            logger.error(f"Reset error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ninjaone/devices/<device_id>/alerts/reset', methods=['POST'])
    def reset_device_alerts(device_id):
        """Reset all alerts for a device."""
        if not app.ninjaone_client:
            return jsonify({'error': 'NinjaOne client not configured'}), 503

        try:
            success = app.ninjaone_client.reset_device_alerts(device_id)
            if success:
                return jsonify({'success': True, 'message': f'All alerts reset for device {device_id}'})
            return jsonify({'success': False, 'error': 'Failed to reset device alerts'}), 500
        except Exception as e:
            logger.error(f"Reset device alerts error: {e}")
            return jsonify({'error': str(e)}), 500

    # ========== Webhook Endpoints (for NinjaOne to call) ==========

    @app.route('/api/webhooks/ninjaone/alert', methods=['POST'])
    def ninjaone_alert_webhook():
        """
        Webhook endpoint for NinjaOne alert notifications.

        Configure in NinjaOne: Administration > Notifications > Webhooks
        URL: https://your-server/api/webhooks/ninjaone/alert

        Expected payload:
        {
            "alertId": "123",
            "severity": "CRITICAL",
            "message": "Disk space critical",
            "deviceName": "SETCO-DC01",
            "organizationName": "Setco Industries"
        }
        """
        from common.notifications import notify_alert

        data = request.get_json() or {}

        alert_id = data.get('alertId', data.get('id', 'unknown'))
        severity = data.get('severity', 'UNKNOWN')
        message = data.get('message', 'No message')
        device_name = data.get('deviceName', data.get('device_name', ''))
        org_name = data.get('organizationName', data.get('org_name', ''))

        logger.info(f"Received NinjaOne webhook: {severity} alert for {device_name}")

        # Send email notification
        email_sent = notify_alert(
            alert_id=str(alert_id),
            severity=severity,
            message=message,
            device_name=device_name,
            org_name=org_name
        )

        return jsonify({
            'received': True,
            'alert_id': alert_id,
            'email_sent': email_sent
        })

    @app.route('/api/notifications/test', methods=['POST'])
    def test_notification():
        """
        Test email notification configuration.

        Request body (optional):
        {"email": "test@example.com"}
        """
        from common.notifications import get_notifier

        notifier = get_notifier()

        if not notifier.config.is_configured():
            return jsonify({
                'configured': False,
                'error': 'SMTP not configured. Set SMTP_USER and SMTP_PASSWORD environment variables.',
                'required_vars': ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD', 'ALERT_TO_EMAIL']
            }), 400

        # Send test email
        success = notifier.send_alert_email(
            alert_id='test-001',
            severity='MINOR',
            message='This is a test alert from OberaConnect. If you received this, email notifications are working!',
            device_name='TEST-DEVICE',
            org_name='OberaConnect Test'
        )

        return jsonify({
            'configured': True,
            'test_sent': success,
            'to_address': notifier.config.to_address
        })

    @app.route('/api/notifications/config', methods=['GET'])
    def notification_config():
        """Get current notification configuration (without secrets)."""
        from common.notifications import get_notifier

        notifier = get_notifier()
        config = notifier.config

        return jsonify({
            'configured': config.is_configured(),
            'smtp_host': config.smtp_host,
            'smtp_port': config.smtp_port,
            'from_address': config.from_address,
            'to_address': config.to_address,
            'use_tls': config.use_tls,
            'smtp_user_set': bool(config.smtp_user),
            'smtp_password_set': bool(config.smtp_password)
        })

    # ========== Correlation Endpoints ==========
    
    @app.route('/api/correlate/incident', methods=['POST'])
    def correlate_incident():
        """
        Get correlated incident context for a customer.
        
        Request body:
            {"customer": "Setco Industries"}
        """
        if not app.correlator:
            return jsonify({'error': 'Correlator not configured'}), 503
        
        data = request.get_json() or {}
        customer = data.get('customer', '')
        
        if not customer:
            return jsonify({'error': 'Missing customer parameter'}), 400
        
        try:
            incident = app.correlator.get_incident_context(customer)
            return jsonify(incident.to_dict())
        except Exception as e:
            logger.error(f"Correlation error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/correlate/issues', methods=['GET'])
    def correlate_issues():
        """Get all correlated issues."""
        if not app.correlator:
            return jsonify({'error': 'Correlator not configured'}), 503
        
        try:
            incidents = app.correlator.find_correlated_issues()
            return jsonify({
                'count': len(incidents),
                'incidents': [i.to_dict() for i in incidents]
            })
        except Exception as e:
            logger.error(f"Issues error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/correlate/morning-check', methods=['GET'])
    def morning_check():
        """Get morning check report."""
        if not app.correlator:
            return jsonify({'error': 'Correlator not configured'}), 503
        
        try:
            report = app.correlator.get_morning_check_report()
            return jsonify(report)
        except Exception as e:
            logger.error(f"Morning check error: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app


def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Run the webhook API server.
    
    Args:
        host: Bind address
        port: Port number
        debug: Enable debug mode
    """
    # Import clients
    from unifi import get_client as get_unifi_client, DemoUniFiClient
    from ninjaone import get_client as get_ninjaone_client, DemoNinjaOneClient
    from ninjaone import Correlator
    
    # Check for demo mode
    demo_mode = os.getenv('OBERACONNECT_DEMO', 'false').lower() == 'true'
    
    # Initialize clients
    unifi = get_unifi_client(demo=demo_mode)
    ninjaone = get_ninjaone_client(demo=demo_mode)

    # Initialize data (with graceful fallback on errors)
    try:
        unifi_sites = unifi.get_sites()
        logger.info(f"Loaded {len(unifi_sites)} UniFi sites")
    except Exception as e:
        logger.warning(f"Failed to load UniFi sites: {e}")
        unifi_sites = []

    try:
        ninjaone_alerts = ninjaone.get_alerts() if hasattr(ninjaone, 'get_alerts') else []
        ninjaone_devices = ninjaone.get_devices() if hasattr(ninjaone, 'get_devices') else []
        logger.info(f"Loaded {len(ninjaone_alerts)} NinjaOne alerts, {len(ninjaone_devices)} devices")
    except Exception as e:
        logger.warning(f"Failed to load NinjaOne data: {e}")
        ninjaone_alerts = []
        ninjaone_devices = []
    
    correlator = Correlator(
        unifi_sites=unifi_sites,
        ninjaone_alerts=ninjaone_alerts,
        ninjaone_devices=ninjaone_devices
    )
    
    # Create and run app
    app = create_app(
        unifi_client=unifi,
        ninjaone_client=ninjaone,
        correlator=correlator
    )
    
    logger.info(f"Starting webhook API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


__all__ = [
    'create_app',
    'run_server'
]
