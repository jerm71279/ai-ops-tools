"""
OberaConnect AI Assessment Analyzer
Aligned with OberaAI Strategy - Director Mode + Leverage

This module implements the Director mindset:
- AI analyzes raw data and generates findings
- Human reviews and approves/modifies
- 80% directing (prompt design) / 20% doing (review)

Leverage: One engineer can assess dozens of customers by directing AI
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class AnalysisRequest:
    """Request for AI analysis"""
    customer_id: str
    customer_name: str
    assessment_type: str
    raw_data: Dict[str, Any]
    context: Optional[str] = None


@dataclass
class AnalysisResult:
    """AI-generated analysis result for human review"""
    request_id: str
    findings: List[Dict]
    summary: str
    risk_score: float
    confidence: float
    requires_human_review: List[str]
    auto_approved: List[str]


class AIAnalyzer:
    """
    AI-powered assessment analyzer

    Implements 98/2 Principle:
    - 98% of findings auto-generated from patterns
    - 2% flagged for human review (novel situations, high severity)
    """

    def __init__(self, patterns_dir: str = None):
        self.patterns_dir = Path(patterns_dir) if patterns_dir else Path(__file__).parent.parent / "data" / "patterns"
        self.patterns_dir.mkdir(parents=True, exist_ok=True)

        # Analysis templates for different assessment types
        self.analysis_templates = self._load_analysis_templates()

        # Known patterns from historical data (Data Moat)
        self.known_patterns = self._load_known_patterns()

    def _load_analysis_templates(self) -> Dict[str, Any]:
        """Load assessment analysis templates"""
        return {
            'security': {
                'categories': [
                    'Access Control',
                    'Network Security',
                    'Endpoint Protection',
                    'Data Protection',
                    'Monitoring & Logging',
                    'Backup & Recovery',
                    'Patch Management',
                    'User Awareness'
                ],
                'checks': {
                    'Access Control': [
                        {'check': 'mfa_enabled', 'title': 'Multi-Factor Authentication', 'severity': 'critical', 'impact': 15},
                        {'check': 'password_policy', 'title': 'Password Policy Compliance', 'severity': 'high', 'impact': 10},
                        {'check': 'privileged_accounts', 'title': 'Privileged Account Management', 'severity': 'high', 'impact': 10},
                        {'check': 'account_review', 'title': 'Regular Account Reviews', 'severity': 'medium', 'impact': 5},
                    ],
                    'Network Security': [
                        {'check': 'firewall_rules', 'title': 'Firewall Rule Review', 'severity': 'high', 'impact': 10},
                        {'check': 'network_segmentation', 'title': 'Network Segmentation', 'severity': 'high', 'impact': 10},
                        {'check': 'vpn_security', 'title': 'VPN Configuration Security', 'severity': 'medium', 'impact': 7},
                        {'check': 'wireless_security', 'title': 'Wireless Network Security', 'severity': 'medium', 'impact': 7},
                    ],
                    'Endpoint Protection': [
                        {'check': 'edr_deployed', 'title': 'EDR/Antivirus Deployment', 'severity': 'critical', 'impact': 15},
                        {'check': 'edr_current', 'title': 'EDR Definitions Current', 'severity': 'high', 'impact': 8},
                        {'check': 'host_firewall', 'title': 'Host-based Firewall Enabled', 'severity': 'medium', 'impact': 5},
                    ],
                    'Data Protection': [
                        {'check': 'encryption_at_rest', 'title': 'Data Encryption at Rest', 'severity': 'high', 'impact': 10},
                        {'check': 'encryption_in_transit', 'title': 'Data Encryption in Transit', 'severity': 'high', 'impact': 10},
                        {'check': 'dlp_controls', 'title': 'Data Loss Prevention Controls', 'severity': 'medium', 'impact': 7},
                    ],
                    'Monitoring & Logging': [
                        {'check': 'centralized_logging', 'title': 'Centralized Log Management', 'severity': 'high', 'impact': 10},
                        {'check': 'log_retention', 'title': 'Log Retention Policy', 'severity': 'medium', 'impact': 5},
                        {'check': 'alerting_configured', 'title': 'Security Alerting Configured', 'severity': 'high', 'impact': 8},
                    ],
                    'Backup & Recovery': [
                        {'check': 'backup_exists', 'title': 'Backup Solution Deployed', 'severity': 'critical', 'impact': 15},
                        {'check': 'backup_tested', 'title': 'Backup Recovery Tested', 'severity': 'high', 'impact': 10},
                        {'check': 'offsite_backup', 'title': 'Offsite/Cloud Backup', 'severity': 'high', 'impact': 10},
                    ],
                    'Patch Management': [
                        {'check': 'os_patching', 'title': 'OS Patch Compliance', 'severity': 'critical', 'impact': 12},
                        {'check': 'app_patching', 'title': 'Application Patch Compliance', 'severity': 'high', 'impact': 8},
                        {'check': 'firmware_current', 'title': 'Network Device Firmware Current', 'severity': 'medium', 'impact': 6},
                    ],
                    'User Awareness': [
                        {'check': 'security_training', 'title': 'Security Awareness Training', 'severity': 'medium', 'impact': 5},
                        {'check': 'phishing_testing', 'title': 'Phishing Simulation Testing', 'severity': 'medium', 'impact': 5},
                    ],
                }
            },
            'network': {
                'categories': [
                    'Infrastructure Health',
                    'Performance',
                    'Redundancy',
                    'Documentation',
                    'Standards Compliance'
                ],
                'checks': {
                    'Infrastructure Health': [
                        {'check': 'device_health', 'title': 'Network Device Health', 'severity': 'high', 'impact': 10},
                        {'check': 'uptime', 'title': 'Device Uptime Acceptable', 'severity': 'medium', 'impact': 5},
                        {'check': 'resource_utilization', 'title': 'Resource Utilization Within Limits', 'severity': 'medium', 'impact': 7},
                    ],
                    'Performance': [
                        {'check': 'bandwidth_adequate', 'title': 'Bandwidth Capacity Adequate', 'severity': 'high', 'impact': 10},
                        {'check': 'latency_acceptable', 'title': 'Network Latency Acceptable', 'severity': 'medium', 'impact': 7},
                        {'check': 'error_rates', 'title': 'Interface Error Rates Low', 'severity': 'medium', 'impact': 5},
                    ],
                    'Redundancy': [
                        {'check': 'isp_redundancy', 'title': 'ISP Redundancy', 'severity': 'high', 'impact': 10},
                        {'check': 'device_redundancy', 'title': 'Critical Device Redundancy', 'severity': 'medium', 'impact': 8},
                        {'check': 'power_redundancy', 'title': 'Power Redundancy (UPS)', 'severity': 'medium', 'impact': 5},
                    ],
                    'Documentation': [
                        {'check': 'network_diagram', 'title': 'Network Diagram Current', 'severity': 'low', 'impact': 3},
                        {'check': 'ip_documentation', 'title': 'IP Address Documentation', 'severity': 'low', 'impact': 3},
                        {'check': 'config_backup', 'title': 'Configuration Backups', 'severity': 'high', 'impact': 8},
                    ],
                    'Standards Compliance': [
                        {'check': 'naming_convention', 'title': 'Device Naming Standards', 'severity': 'low', 'impact': 2},
                        {'check': 'vlan_standards', 'title': 'VLAN Standards Compliance', 'severity': 'medium', 'impact': 5},
                    ],
                }
            },
            'cloud_readiness': {
                'categories': [
                    'Identity Readiness',
                    'Network Readiness',
                    'Application Readiness',
                    'Data Readiness',
                    'Security Readiness'
                ],
                'checks': {
                    'Identity Readiness': [
                        {'check': 'ad_health', 'title': 'Active Directory Health', 'severity': 'critical', 'impact': 15},
                        {'check': 'azure_ad_sync', 'title': 'Azure AD Sync Readiness', 'severity': 'high', 'impact': 10},
                        {'check': 'sso_readiness', 'title': 'SSO Implementation Readiness', 'severity': 'medium', 'impact': 7},
                    ],
                    'Network Readiness': [
                        {'check': 'bandwidth_cloud', 'title': 'Bandwidth for Cloud Workloads', 'severity': 'high', 'impact': 10},
                        {'check': 'vpn_capability', 'title': 'Site-to-Site VPN Capability', 'severity': 'high', 'impact': 10},
                        {'check': 'dns_readiness', 'title': 'DNS Configuration Readiness', 'severity': 'medium', 'impact': 5},
                    ],
                    'Application Readiness': [
                        {'check': 'app_inventory', 'title': 'Application Inventory Complete', 'severity': 'high', 'impact': 8},
                        {'check': 'app_dependencies', 'title': 'Application Dependencies Mapped', 'severity': 'medium', 'impact': 7},
                        {'check': 'saas_alternatives', 'title': 'SaaS Alternatives Identified', 'severity': 'low', 'impact': 3},
                    ],
                    'Data Readiness': [
                        {'check': 'data_classification', 'title': 'Data Classification Complete', 'severity': 'high', 'impact': 10},
                        {'check': 'data_volume', 'title': 'Data Volume Assessed', 'severity': 'medium', 'impact': 5},
                        {'check': 'compliance_requirements', 'title': 'Compliance Requirements Identified', 'severity': 'high', 'impact': 10},
                    ],
                    'Security Readiness': [
                        {'check': 'conditional_access', 'title': 'Conditional Access Planning', 'severity': 'high', 'impact': 10},
                        {'check': 'mfa_rollout', 'title': 'MFA Rollout Plan', 'severity': 'critical', 'impact': 12},
                    ],
                }
            }
        }

    def _load_known_patterns(self) -> Dict[str, Any]:
        """Load known patterns from historical assessments (Data Moat)"""
        pattern_file = self.patterns_dir / "finding_patterns.json"

        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                return json.load(f)

        return {}

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Director Mode Analysis

        Takes raw assessment data and generates structured findings.
        Flags items requiring human review vs auto-approved items.
        """
        request_id = f"analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        template = self.analysis_templates.get(request.assessment_type, {})
        findings = []
        requires_human_review = []
        auto_approved = []

        # Process each category
        for category, checks in template.get('checks', {}).items():
            for check in checks:
                check_key = check['check']
                check_result = self._evaluate_check(check_key, request.raw_data)

                if not check_result['passed']:
                    finding = {
                        'category': category,
                        'title': check['title'],
                        'description': check_result['description'],
                        'severity': check['severity'],
                        'score_impact': check['impact'],
                        'remediation_steps': check_result['remediation'],
                        'evidence': check_result.get('evidence'),
                        'confidence': check_result['confidence']
                    }
                    findings.append(finding)

                    # Determine if human review needed (98/2 principle)
                    if self._requires_human_review(finding, check_result):
                        requires_human_review.append(finding['title'])
                    else:
                        auto_approved.append(finding['title'])

        # Calculate overall risk score
        risk_score = self._calculate_risk_score(findings)

        # Generate summary
        summary = self._generate_summary(request, findings, risk_score)

        # Calculate overall confidence
        avg_confidence = sum(f.get('confidence', 0.8) for f in findings) / max(len(findings), 1)

        return AnalysisResult(
            request_id=request_id,
            findings=findings,
            summary=summary,
            risk_score=risk_score,
            confidence=avg_confidence,
            requires_human_review=requires_human_review,
            auto_approved=auto_approved
        )

    def _evaluate_check(self, check_key: str, raw_data: Dict) -> Dict:
        """Evaluate a specific check against raw data"""

        # Default result structure
        result = {
            'passed': True,
            'description': '',
            'remediation': [],
            'evidence': None,
            'confidence': 0.9
        }

        # Check evaluation logic - extensible for each check type
        check_data = raw_data.get(check_key, {})

        if isinstance(check_data, bool):
            result['passed'] = check_data
            result['confidence'] = 1.0
        elif isinstance(check_data, dict):
            result['passed'] = check_data.get('compliant', check_data.get('enabled', False))
            result['description'] = check_data.get('description', f'{check_key} check failed')
            result['evidence'] = check_data.get('evidence')
            result['confidence'] = check_data.get('confidence', 0.85)
        elif check_data is None:
            # No data provided - assume non-compliant with lower confidence
            result['passed'] = False
            result['description'] = f'No data available for {check_key} verification'
            result['confidence'] = 0.6

        # Add remediation steps based on check type
        result['remediation'] = self._get_remediation_steps(check_key, result['passed'])

        return result

    def _get_remediation_steps(self, check_key: str, passed: bool) -> List[str]:
        """Get remediation steps for a failed check"""

        if passed:
            return []

        # Remediation knowledge base (grows with Data Moat)
        remediation_db = {
            'mfa_enabled': [
                'Enable MFA for all user accounts in Azure AD/M365 Admin Center',
                'Configure Conditional Access policies requiring MFA',
                'Roll out Microsoft Authenticator app to all users',
                'Disable legacy authentication protocols'
            ],
            'password_policy': [
                'Configure minimum 14-character password requirement',
                'Enable password complexity requirements',
                'Set password expiration to 90 days or implement passwordless',
                'Enable Azure AD Password Protection'
            ],
            'firewall_rules': [
                'Review and document all firewall rules',
                'Remove any allow-all rules',
                'Implement least-privilege access rules',
                'Enable logging on all rules'
            ],
            'edr_deployed': [
                'Deploy Microsoft Defender for Endpoint or approved EDR',
                'Ensure all endpoints are enrolled',
                'Configure real-time protection',
                'Set up automated remediation actions'
            ],
            'backup_exists': [
                'Implement 3-2-1 backup strategy',
                'Deploy Axcient or approved backup solution',
                'Configure backup schedules for all critical systems',
                'Document backup and recovery procedures'
            ],
            'backup_tested': [
                'Schedule quarterly backup recovery tests',
                'Document test results and recovery times',
                'Update runbooks based on test findings',
                'Train staff on recovery procedures'
            ],
            'centralized_logging': [
                'Deploy SIEM solution (Graylog/Sentinel)',
                'Configure log forwarding from all critical systems',
                'Set up log retention policies',
                'Create alerting rules for security events'
            ],
            'os_patching': [
                'Configure Windows Update for Business or WSUS',
                'Set maintenance windows for automatic updates',
                'Monitor patch compliance via NinjaOne',
                'Create exception process for delayed patches'
            ],
            'network_segmentation': [
                'Implement VLAN segmentation for guest/IoT/corporate',
                'Configure inter-VLAN routing restrictions',
                'Deploy micro-segmentation for critical assets',
                'Document network segmentation design'
            ],
        }

        return remediation_db.get(check_key, [
            f'Review and remediate {check_key} finding',
            'Consult security best practices documentation',
            'Consider engaging security consultant for guidance'
        ])

    def _requires_human_review(self, finding: Dict, check_result: Dict) -> bool:
        """
        98/2 Principle: Determine if finding requires human review

        Human review required for:
        - Critical severity findings
        - Low confidence results
        - Novel findings not in historical patterns
        - High-impact findings (>10 points)
        """

        # Critical findings always need human review
        if finding['severity'] == 'critical':
            return True

        # Low confidence needs review
        if check_result['confidence'] < 0.7:
            return True

        # High impact needs review
        if finding['score_impact'] > 10:
            return True

        # Novel findings (not in historical patterns) need review
        if self.known_patterns:
            common_findings = self.known_patterns.get('common_findings', {})
            if finding['title'] not in common_findings:
                return True  # Novel finding

        return False

    def _calculate_risk_score(self, findings: List[Dict]) -> float:
        """Calculate overall risk score from findings"""

        if not findings:
            return 0.0

        severity_weights = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1,
            'info': 0.5
        }

        weighted_sum = sum(
            severity_weights.get(f['severity'], 1) * f['score_impact']
            for f in findings
        )

        # Normalize to 0-100 scale
        max_possible = 100 * 4  # Assuming max 100 points at critical severity
        risk_score = min(100, (weighted_sum / max_possible) * 100)

        return round(risk_score, 1)

    def _generate_summary(
        self,
        request: AnalysisRequest,
        findings: List[Dict],
        risk_score: float
    ) -> str:
        """Generate executive summary of analysis"""

        severity_counts = {}
        for f in findings:
            sev = f['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        total_impact = sum(f['score_impact'] for f in findings)

        summary = f"""Assessment Analysis for {request.customer_name}
Type: {request.assessment_type.upper()}
Risk Score: {risk_score}/100

Findings Summary:
- Critical: {severity_counts.get('critical', 0)}
- High: {severity_counts.get('high', 0)}
- Medium: {severity_counts.get('medium', 0)}
- Low: {severity_counts.get('low', 0)}

Total Score Impact: {total_impact} points
Estimated Final Score: {100 - total_impact}/100
"""

        if severity_counts.get('critical', 0) > 0:
            summary += "\n⚠️ CRITICAL FINDINGS REQUIRE IMMEDIATE ATTENTION"

        return summary

    def get_analysis_prompt(self, assessment_type: str, raw_data: Dict) -> str:
        """
        Director Mode: Generate prompt for external AI analysis

        Use this to direct Claude/GPT to analyze raw data
        """
        template = self.analysis_templates.get(assessment_type, {})

        prompt = f"""Analyze this {assessment_type} assessment data and identify security/compliance findings.

Assessment Template Categories:
{json.dumps(template.get('categories', []), indent=2)}

Raw Data to Analyze:
{json.dumps(raw_data, indent=2)}

For each finding, provide:
1. Category (from template)
2. Title (concise description)
3. Description (detailed explanation)
4. Severity (critical/high/medium/low)
5. Score Impact (1-15 points)
6. Remediation Steps (actionable items)
7. Evidence (what in the data indicates this finding)

Focus on actionable findings. Prioritize by risk.
Return findings as JSON array.
"""

        return prompt


class AssessmentDirector:
    """
    High-level director interface for assessments

    Implements Director Mode workflow:
    1. Collect raw data (automated via integrations)
    2. Direct AI to analyze
    3. Review flagged items
    4. Approve and generate report
    """

    def __init__(self):
        self.analyzer = AIAnalyzer()

    def quick_assess(
        self,
        customer_id: str,
        customer_name: str,
        assessment_type: str,
        raw_data: Dict
    ) -> Dict:
        """
        Quick assessment workflow for Director Mode

        Returns analysis with clear action items
        """
        request = AnalysisRequest(
            customer_id=customer_id,
            customer_name=customer_name,
            assessment_type=assessment_type,
            raw_data=raw_data
        )

        result = self.analyzer.analyze(request)

        return {
            'summary': result.summary,
            'risk_score': result.risk_score,
            'confidence': result.confidence,
            'total_findings': len(result.findings),
            'requires_review': result.requires_human_review,
            'auto_approved': result.auto_approved,
            'findings': result.findings,
            'action_required': len(result.requires_human_review) > 0,
            'next_steps': self._get_next_steps(result)
        }

    def _get_next_steps(self, result: AnalysisResult) -> List[str]:
        """Generate next steps based on analysis"""

        steps = []

        if result.requires_human_review:
            steps.append(f"Review {len(result.requires_human_review)} flagged findings requiring human judgment")

        if result.risk_score > 70:
            steps.append("Schedule urgent remediation planning session with customer")
        elif result.risk_score > 40:
            steps.append("Schedule remediation planning within 2 weeks")
        else:
            steps.append("Include findings in regular review cycle")

        steps.append("Generate customer-facing report")
        steps.append("Create remediation project in NinjaOne")

        return steps
