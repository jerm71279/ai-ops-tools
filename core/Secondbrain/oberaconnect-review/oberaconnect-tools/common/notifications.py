"""
Email and Notification Service for OberaConnect

Sends alert notifications via email, with support for:
- SMTP (Gmail, O365, custom)
- Alert severity filtering
- Rate limiting to prevent spam
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email configuration from environment variables."""
    smtp_host: str = field(default_factory=lambda: os.getenv('SMTP_HOST', 'smtp.gmail.com'))
    smtp_port: int = field(default_factory=lambda: int(os.getenv('SMTP_PORT', '587')))
    smtp_user: str = field(default_factory=lambda: os.getenv('SMTP_USER', ''))
    smtp_password: str = field(default_factory=lambda: os.getenv('SMTP_PASSWORD', ''))
    from_address: str = field(default_factory=lambda: os.getenv('ALERT_FROM_EMAIL', 'alerts@oberaconnect.com'))
    to_address: str = field(default_factory=lambda: os.getenv('ALERT_TO_EMAIL', 'support@oberaconnect.com'))
    use_tls: bool = field(default_factory=lambda: os.getenv('SMTP_USE_TLS', 'true').lower() == 'true')

    def is_configured(self) -> bool:
        """Check if SMTP is properly configured."""
        return bool(self.smtp_user and self.smtp_password)


class AlertNotifier:
    """
    Sends email notifications for alerts with rate limiting.

    Features:
    - Deduplication: Won't send same alert twice within cooldown period
    - Rate limiting: Max emails per hour
    - Severity filtering: Only notify on configured severity levels
    """

    def __init__(
        self,
        config: Optional[EmailConfig] = None,
        cooldown_minutes: int = 15,
        max_per_hour: int = 20,
        min_severity: str = 'MAJOR'
    ):
        self.config = config or EmailConfig()
        self.cooldown = timedelta(minutes=cooldown_minutes)
        self.max_per_hour = max_per_hour
        self.min_severity = min_severity

        # Track sent alerts for deduplication
        self._sent_alerts: Dict[str, datetime] = {}
        self._hourly_count: int = 0
        self._hour_start: datetime = datetime.now()
        self._lock = Lock()

        # Severity hierarchy
        self._severity_levels = {
            'NONE': 0,
            'MINOR': 1,
            'MODERATE': 2,
            'MAJOR': 3,
            'CRITICAL': 4
        }

    def _should_notify(self, alert_id: str, severity: str) -> bool:
        """Check if alert should trigger notification."""
        with self._lock:
            # Check severity threshold
            alert_level = self._severity_levels.get(severity.upper(), 0)
            min_level = self._severity_levels.get(self.min_severity, 3)
            if alert_level < min_level:
                logger.debug(f"Alert {alert_id} below severity threshold ({severity} < {self.min_severity})")
                return False

            # Check hourly rate limit
            now = datetime.now()
            if now - self._hour_start > timedelta(hours=1):
                self._hourly_count = 0
                self._hour_start = now

            if self._hourly_count >= self.max_per_hour:
                logger.warning(f"Hourly rate limit reached ({self.max_per_hour}/hour)")
                return False

            # Check cooldown (deduplication)
            if alert_id in self._sent_alerts:
                last_sent = self._sent_alerts[alert_id]
                if now - last_sent < self.cooldown:
                    logger.debug(f"Alert {alert_id} in cooldown period")
                    return False

            return True

    def _mark_sent(self, alert_id: str):
        """Mark alert as sent for deduplication."""
        with self._lock:
            self._sent_alerts[alert_id] = datetime.now()
            self._hourly_count += 1

            # Cleanup old entries
            cutoff = datetime.now() - timedelta(hours=2)
            self._sent_alerts = {
                k: v for k, v in self._sent_alerts.items()
                if v > cutoff
            }

    def send_alert_email(
        self,
        alert_id: str,
        severity: str,
        message: str,
        device_name: str = '',
        org_name: str = '',
        extra_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send email notification for an alert.

        Returns True if email was sent, False if skipped or failed.
        """
        if not self.config.is_configured():
            logger.warning("SMTP not configured - skipping email notification")
            return False

        if not self._should_notify(alert_id, severity):
            return False

        try:
            # Build email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{severity}] {device_name or 'Alert'}: {message[:50]}"
            msg['From'] = self.config.from_address
            msg['To'] = self.config.to_address

            # Plain text body
            text_body = f"""
OberaConnect Alert Notification
================================

Severity: {severity}
Device: {device_name or 'Unknown'}
Organization: {org_name or 'Unknown'}
Alert ID: {alert_id}

Message:
{message}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            if extra_context:
                text_body += "\nAdditional Context:\n"
                for k, v in extra_context.items():
                    text_body += f"  {k}: {v}\n"

            text_body += """
---
This is an automated alert from OberaConnect.
To manage alerts, visit NinjaOne or reply to this email.
"""

            # HTML body
            severity_color = {
                'CRITICAL': '#dc3545',
                'MAJOR': '#fd7e14',
                'MODERATE': '#ffc107',
                'MINOR': '#17a2b8'
            }.get(severity.upper(), '#6c757d')

            html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: {severity_color}; color: white; padding: 15px; border-radius: 5px 5px 0 0;">
        <h2 style="margin: 0;">{severity} Alert</h2>
    </div>
    <div style="border: 1px solid #ddd; border-top: none; padding: 20px;">
        <p><strong>Device:</strong> {device_name or 'Unknown'}</p>
        <p><strong>Organization:</strong> {org_name or 'Unknown'}</p>
        <p><strong>Message:</strong></p>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            {message}
        </div>
        <p style="color: #666; font-size: 12px; margin-top: 20px;">
            Alert ID: {alert_id}<br>
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
    <div style="background: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; color: #666;">
        OberaConnect Alert System
    </div>
</body>
</html>
"""

            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)

            self._mark_sent(alert_id)
            logger.info(f"Alert email sent for {alert_id} to {self.config.to_address}")
            return True

        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")
            return False

    def send_digest(self, alerts: List[Dict[str, Any]]) -> bool:
        """Send a digest email with multiple alerts."""
        if not alerts:
            return False

        if not self.config.is_configured():
            logger.warning("SMTP not configured - skipping digest email")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[OberaConnect] Alert Digest: {len(alerts)} alerts"
            msg['From'] = self.config.from_address
            msg['To'] = self.config.to_address

            # Build alert list
            alert_rows = ""
            for a in alerts[:20]:  # Limit to 20 alerts
                alert_rows += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{a.get('severity', 'UNKNOWN')}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{a.get('device_name', 'Unknown')}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{a.get('message', '')[:60]}</td>
                </tr>
                """

            html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
    <div style="background: #0066cc; color: white; padding: 15px; border-radius: 5px 5px 0 0;">
        <h2 style="margin: 0;">OberaConnect Alert Digest</h2>
        <p style="margin: 5px 0 0 0;">{len(alerts)} active alerts</p>
    </div>
    <div style="border: 1px solid #ddd; border-top: none; padding: 20px;">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f8f9fa;">
                    <th style="padding: 10px; text-align: left;">Severity</th>
                    <th style="padding: 10px; text-align: left;">Device</th>
                    <th style="padding: 10px; text-align: left;">Message</th>
                </tr>
            </thead>
            <tbody>
                {alert_rows}
            </tbody>
        </table>
    </div>
    <div style="background: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; color: #666;">
        Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</body>
</html>
"""

            msg.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)

            logger.info(f"Alert digest sent with {len(alerts)} alerts")
            return True

        except Exception as e:
            logger.error(f"Failed to send alert digest: {e}")
            return False


# Global notifier instance
_notifier: Optional[AlertNotifier] = None


def get_notifier() -> AlertNotifier:
    """Get or create the global notifier instance."""
    global _notifier
    if _notifier is None:
        _notifier = AlertNotifier()
    return _notifier


def notify_alert(
    alert_id: str,
    severity: str,
    message: str,
    device_name: str = '',
    org_name: str = ''
) -> bool:
    """Convenience function to send alert notification."""
    return get_notifier().send_alert_email(
        alert_id=alert_id,
        severity=severity,
        message=message,
        device_name=device_name,
        org_name=org_name
    )
