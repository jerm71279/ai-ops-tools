"""
OberaConnect Assessment Engine
Aligned with OberaAI Strategy - Data Moats + Director Mode

This engine implements the 98/2 principle:
- AI handles 98% of assessment analysis and pattern detection
- Humans audit 2% exceptions requiring judgment

Feedback Loops:
1. Score Tracking Loop - Track scores over time, show improvement trends
2. Remediation Feedback Loop - Generate action items, track completion
3. Comparative Analysis Loop - Compare across customers/time periods
4. Pattern Detection Loop - Identify common gaps across customer base (Data Moat)
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class AssessmentType(Enum):
    SECURITY = "security"
    NETWORK = "network"
    CLOUD_READINESS = "cloud_readiness"
    COMPLIANCE = "compliance"
    INFRASTRUCTURE = "infrastructure"


class SeverityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RemediationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"
    ACCEPTED_RISK = "accepted_risk"


@dataclass
class Finding:
    """Individual assessment finding"""
    id: str
    category: str
    title: str
    description: str
    severity: SeverityLevel
    score_impact: float  # 0-10 points deducted
    remediation_steps: List[str]
    remediation_status: RemediationStatus = RemediationStatus.PENDING
    evidence: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    completion_date: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['severity'] = self.severity.value
        data['remediation_status'] = self.remediation_status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Finding':
        data['severity'] = SeverityLevel(data['severity'])
        data['remediation_status'] = RemediationStatus(data['remediation_status'])
        return cls(**data)


@dataclass
class AssessmentResult:
    """Complete assessment result with feedback loop data"""
    id: str
    customer_id: str
    customer_name: str
    assessment_type: AssessmentType
    timestamp: str
    version: str = "1.0"

    # Scores
    overall_score: float = 100.0
    category_scores: Dict[str, float] = field(default_factory=dict)

    # Findings
    findings: List[Finding] = field(default_factory=list)

    # Feedback Loop Data
    previous_assessment_id: Optional[str] = None
    score_delta: Optional[float] = None  # Change from previous
    trend: Optional[str] = None  # "improving", "declining", "stable"

    # Metadata for Data Moat
    environment_profile: Dict[str, Any] = field(default_factory=dict)
    technology_stack: List[str] = field(default_factory=list)
    industry: Optional[str] = None
    employee_count: Optional[int] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['assessment_type'] = self.assessment_type.value
        data['findings'] = [f.to_dict() if isinstance(f, Finding) else f for f in self.findings]
        return data


class AssessmentEngine:
    """
    Core assessment engine with built-in feedback loops

    Implements OberaAI Strategy:
    - Leverage: One engineer can assess many customers with AI assistance
    - Director Mode: AI analyzes, human reviews exceptions
    - Data Moat: Aggregates patterns across all assessments
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Sub-directories for data organization
        self.assessments_dir = self.data_dir / "assessments"
        self.patterns_dir = self.data_dir / "patterns"
        self.benchmarks_dir = self.data_dir / "benchmarks"

        for d in [self.assessments_dir, self.patterns_dir, self.benchmarks_dir]:
            d.mkdir(exist_ok=True)

        # In-memory caches
        self._pattern_cache: Dict[str, Any] = {}
        self._benchmark_cache: Dict[str, Any] = {}

    def generate_assessment_id(self, customer_id: str, assessment_type: str) -> str:
        """Generate unique assessment ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_input = f"{customer_id}_{assessment_type}_{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:12]

    def create_assessment(
        self,
        customer_id: str,
        customer_name: str,
        assessment_type: AssessmentType,
        environment_profile: Dict[str, Any] = None,
        technology_stack: List[str] = None,
        industry: str = None,
        employee_count: int = None
    ) -> AssessmentResult:
        """Create a new assessment with automatic linking to previous assessments"""

        assessment_id = self.generate_assessment_id(customer_id, assessment_type.value)

        # Find previous assessment for this customer/type (Feedback Loop: Trend Tracking)
        previous = self.get_latest_assessment(customer_id, assessment_type)

        result = AssessmentResult(
            id=assessment_id,
            customer_id=customer_id,
            customer_name=customer_name,
            assessment_type=assessment_type,
            timestamp=datetime.now().isoformat(),
            previous_assessment_id=previous.id if previous else None,
            environment_profile=environment_profile or {},
            technology_stack=technology_stack or [],
            industry=industry,
            employee_count=employee_count
        )

        return result

    def add_finding(
        self,
        assessment: AssessmentResult,
        category: str,
        title: str,
        description: str,
        severity: SeverityLevel,
        score_impact: float,
        remediation_steps: List[str],
        evidence: str = None
    ) -> Finding:
        """Add a finding to an assessment"""

        finding_id = f"{assessment.id}_{len(assessment.findings) + 1:03d}"

        finding = Finding(
            id=finding_id,
            category=category,
            title=title,
            description=description,
            severity=severity,
            score_impact=score_impact,
            remediation_steps=remediation_steps,
            evidence=evidence
        )

        assessment.findings.append(finding)
        assessment.overall_score = max(0, assessment.overall_score - score_impact)

        # Update category scores
        if category not in assessment.category_scores:
            assessment.category_scores[category] = 100.0
        assessment.category_scores[category] = max(0, assessment.category_scores[category] - score_impact)

        return finding

    def calculate_trend(self, assessment: AssessmentResult) -> None:
        """
        FEEDBACK LOOP: Score Tracking
        Calculate trend compared to previous assessment
        """
        if assessment.previous_assessment_id:
            previous = self.load_assessment(assessment.previous_assessment_id)
            if previous:
                assessment.score_delta = assessment.overall_score - previous.overall_score

                if assessment.score_delta > 5:
                    assessment.trend = "improving"
                elif assessment.score_delta < -5:
                    assessment.trend = "declining"
                else:
                    assessment.trend = "stable"

    def save_assessment(self, assessment: AssessmentResult) -> str:
        """Save assessment and update pattern database"""

        # Calculate trend before saving
        self.calculate_trend(assessment)

        # Save assessment
        filepath = self.assessments_dir / f"{assessment.id}.json"
        with open(filepath, 'w') as f:
            json.dump(assessment.to_dict(), f, indent=2)

        # Update pattern database (Data Moat)
        self._update_patterns(assessment)

        return str(filepath)

    def load_assessment(self, assessment_id: str) -> Optional[AssessmentResult]:
        """Load an assessment by ID"""
        filepath = self.assessments_dir / f"{assessment_id}.json"
        if not filepath.exists():
            return None

        with open(filepath, 'r') as f:
            data = json.load(f)

        data['assessment_type'] = AssessmentType(data['assessment_type'])
        data['findings'] = [Finding.from_dict(f) for f in data['findings']]
        return AssessmentResult(**data)

    def get_latest_assessment(
        self,
        customer_id: str,
        assessment_type: AssessmentType
    ) -> Optional[AssessmentResult]:
        """Get the most recent assessment for a customer/type combination"""

        assessments = []
        for filepath in self.assessments_dir.glob("*.json"):
            with open(filepath, 'r') as f:
                data = json.load(f)

            if (data['customer_id'] == customer_id and
                data['assessment_type'] == assessment_type.value):
                assessments.append((data['timestamp'], filepath))

        if not assessments:
            return None

        # Sort by timestamp, get most recent
        assessments.sort(key=lambda x: x[0], reverse=True)
        latest_path = assessments[0][1]

        with open(latest_path, 'r') as f:
            data = json.load(f)

        data['assessment_type'] = AssessmentType(data['assessment_type'])
        data['findings'] = [Finding.from_dict(f) for f in data['findings']]
        return AssessmentResult(**data)

    def get_customer_history(self, customer_id: str) -> List[Dict]:
        """
        FEEDBACK LOOP: Comparative Analysis
        Get assessment history for a customer showing score progression
        """
        history = []

        for filepath in self.assessments_dir.glob("*.json"):
            with open(filepath, 'r') as f:
                data = json.load(f)

            if data['customer_id'] == customer_id:
                history.append({
                    'id': data['id'],
                    'type': data['assessment_type'],
                    'timestamp': data['timestamp'],
                    'overall_score': data['overall_score'],
                    'finding_count': len(data['findings']),
                    'trend': data.get('trend'),
                    'score_delta': data.get('score_delta')
                })

        history.sort(key=lambda x: x['timestamp'])
        return history

    def _update_patterns(self, assessment: AssessmentResult) -> None:
        """
        FEEDBACK LOOP: Pattern Detection (Data Moat)
        Aggregate finding patterns across all assessments
        """
        pattern_file = self.patterns_dir / "finding_patterns.json"

        # Load existing patterns
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                patterns = json.load(f)
        else:
            patterns = {
                'by_category': {},
                'by_severity': {},
                'by_industry': {},
                'by_technology': {},
                'common_findings': {},
                'remediation_success_rate': {},
                'last_updated': None
            }

        # Update patterns from this assessment
        for finding in assessment.findings:
            # By category
            cat = finding.category
            if cat not in patterns['by_category']:
                patterns['by_category'][cat] = {'count': 0, 'titles': {}}
            patterns['by_category'][cat]['count'] += 1

            title = finding.title
            if title not in patterns['by_category'][cat]['titles']:
                patterns['by_category'][cat]['titles'][title] = 0
            patterns['by_category'][cat]['titles'][title] += 1

            # By severity
            sev = finding.severity.value
            if sev not in patterns['by_severity']:
                patterns['by_severity'][sev] = 0
            patterns['by_severity'][sev] += 1

            # Common findings across all assessments
            if title not in patterns['common_findings']:
                patterns['common_findings'][title] = {
                    'count': 0,
                    'severity': sev,
                    'category': cat,
                    'avg_score_impact': 0,
                    'total_score_impact': 0
                }
            patterns['common_findings'][title]['count'] += 1
            patterns['common_findings'][title]['total_score_impact'] += finding.score_impact
            patterns['common_findings'][title]['avg_score_impact'] = (
                patterns['common_findings'][title]['total_score_impact'] /
                patterns['common_findings'][title]['count']
            )

        # By industry
        if assessment.industry:
            ind = assessment.industry
            if ind not in patterns['by_industry']:
                patterns['by_industry'][ind] = {'assessments': 0, 'avg_score': 0, 'total_score': 0}
            patterns['by_industry'][ind]['assessments'] += 1
            patterns['by_industry'][ind]['total_score'] += assessment.overall_score
            patterns['by_industry'][ind]['avg_score'] = (
                patterns['by_industry'][ind]['total_score'] /
                patterns['by_industry'][ind]['assessments']
            )

        # By technology stack
        for tech in assessment.technology_stack:
            if tech not in patterns['by_technology']:
                patterns['by_technology'][tech] = {'assessments': 0, 'common_findings': []}
            patterns['by_technology'][tech]['assessments'] += 1

        patterns['last_updated'] = datetime.now().isoformat()

        # Save updated patterns
        with open(pattern_file, 'w') as f:
            json.dump(patterns, f, indent=2)

    def get_pattern_insights(self) -> Dict[str, Any]:
        """
        FEEDBACK LOOP: Data Moat Intelligence
        Get aggregated insights from pattern database
        """
        pattern_file = self.patterns_dir / "finding_patterns.json"

        if not pattern_file.exists():
            return {'message': 'No pattern data available yet'}

        with open(pattern_file, 'r') as f:
            patterns = json.load(f)

        # Generate insights
        insights = {
            'most_common_findings': [],
            'highest_risk_categories': [],
            'industry_benchmarks': {},
            'technology_risk_profiles': {},
            'recommendations': []
        }

        # Top 10 most common findings
        if patterns['common_findings']:
            sorted_findings = sorted(
                patterns['common_findings'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:10]
            insights['most_common_findings'] = [
                {'title': k, **v} for k, v in sorted_findings
            ]

        # Categories with most critical/high findings
        for cat, data in patterns['by_category'].items():
            insights['highest_risk_categories'].append({
                'category': cat,
                'total_findings': data['count']
            })
        insights['highest_risk_categories'].sort(
            key=lambda x: x['total_findings'], reverse=True
        )

        # Industry benchmarks
        insights['industry_benchmarks'] = patterns.get('by_industry', {})

        # Generate AI-ready recommendations
        if insights['most_common_findings']:
            top_finding = insights['most_common_findings'][0]
            insights['recommendations'].append({
                'priority': 'high',
                'recommendation': f"Focus remediation on '{top_finding['title']}' - found in {top_finding['count']} assessments",
                'potential_impact': f"Addresses {top_finding['avg_score_impact']:.1f} average score points per customer"
            })

        return insights

    def generate_remediation_plan(self, assessment: AssessmentResult) -> Dict[str, Any]:
        """
        FEEDBACK LOOP: Remediation Feedback
        Generate prioritized remediation plan with tracking
        """
        plan = {
            'assessment_id': assessment.id,
            'customer': assessment.customer_name,
            'generated_at': datetime.now().isoformat(),
            'current_score': assessment.overall_score,
            'target_score': min(100, assessment.overall_score + 20),  # Aim for 20-point improvement
            'phases': [],
            'quick_wins': [],
            'long_term': []
        }

        # Sort findings by severity and score impact
        critical_high = [f for f in assessment.findings
                        if f.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]]
        medium_low = [f for f in assessment.findings
                     if f.severity in [SeverityLevel.MEDIUM, SeverityLevel.LOW]]

        # Phase 1: Critical/High findings
        if critical_high:
            plan['phases'].append({
                'phase': 1,
                'name': 'Critical Remediation',
                'findings': [f.to_dict() for f in critical_high],
                'potential_score_gain': sum(f.score_impact for f in critical_high),
                'priority': 'immediate'
            })

        # Phase 2: Medium/Low findings
        if medium_low:
            plan['phases'].append({
                'phase': 2,
                'name': 'Security Hardening',
                'findings': [f.to_dict() for f in medium_low],
                'potential_score_gain': sum(f.score_impact for f in medium_low),
                'priority': 'scheduled'
            })

        # Identify quick wins (low effort, high impact)
        for finding in assessment.findings:
            if finding.score_impact >= 5 and len(finding.remediation_steps) <= 3:
                plan['quick_wins'].append({
                    'finding': finding.title,
                    'score_gain': finding.score_impact,
                    'steps': finding.remediation_steps
                })

        return plan

    def update_remediation_status(
        self,
        assessment_id: str,
        finding_id: str,
        status: RemediationStatus,
        notes: str = None
    ) -> bool:
        """
        FEEDBACK LOOP: Remediation Tracking
        Update finding status and track completion
        """
        assessment = self.load_assessment(assessment_id)
        if not assessment:
            return False

        for finding in assessment.findings:
            if finding.id == finding_id:
                finding.remediation_status = status
                if notes:
                    finding.notes.append(f"{datetime.now().isoformat()}: {notes}")
                if status == RemediationStatus.COMPLETED:
                    finding.completion_date = datetime.now().isoformat()

                # Re-save assessment
                self.save_assessment(assessment)

                # Update remediation success patterns
                self._update_remediation_patterns(finding, status)
                return True

        return False

    def _update_remediation_patterns(self, finding: Finding, status: RemediationStatus) -> None:
        """Track remediation success rates for pattern analysis"""
        pattern_file = self.patterns_dir / "finding_patterns.json"

        if not pattern_file.exists():
            return

        with open(pattern_file, 'r') as f:
            patterns = json.load(f)

        title = finding.title
        if 'remediation_success_rate' not in patterns:
            patterns['remediation_success_rate'] = {}

        if title not in patterns['remediation_success_rate']:
            patterns['remediation_success_rate'][title] = {
                'attempted': 0,
                'completed': 0,
                'deferred': 0,
                'accepted_risk': 0
            }

        patterns['remediation_success_rate'][title]['attempted'] += 1

        if status == RemediationStatus.COMPLETED:
            patterns['remediation_success_rate'][title]['completed'] += 1
        elif status == RemediationStatus.DEFERRED:
            patterns['remediation_success_rate'][title]['deferred'] += 1
        elif status == RemediationStatus.ACCEPTED_RISK:
            patterns['remediation_success_rate'][title]['accepted_risk'] += 1

        with open(pattern_file, 'w') as f:
            json.dump(patterns, f, indent=2)

    def get_benchmark_comparison(
        self,
        assessment: AssessmentResult,
        compare_by: str = 'industry'
    ) -> Dict[str, Any]:
        """
        FEEDBACK LOOP: Benchmark Comparison
        Compare assessment against aggregated benchmarks
        """
        insights = self.get_pattern_insights()

        comparison = {
            'assessment_score': assessment.overall_score,
            'comparison_type': compare_by,
            'percentile': None,
            'above_average': None,
            'recommendations': []
        }

        if compare_by == 'industry' and assessment.industry:
            benchmarks = insights.get('industry_benchmarks', {})
            if assessment.industry in benchmarks:
                avg = benchmarks[assessment.industry]['avg_score']
                comparison['benchmark_average'] = avg
                comparison['above_average'] = assessment.overall_score > avg
                comparison['delta'] = assessment.overall_score - avg

        return comparison


# Convenience function for quick assessments
def quick_security_assessment(
    customer_id: str,
    customer_name: str,
    findings_data: List[Dict]
) -> AssessmentResult:
    """
    Director Mode: Quick security assessment from structured input
    AI can generate findings_data, human reviews and approves
    """
    engine = AssessmentEngine()

    assessment = engine.create_assessment(
        customer_id=customer_id,
        customer_name=customer_name,
        assessment_type=AssessmentType.SECURITY
    )

    for finding in findings_data:
        engine.add_finding(
            assessment=assessment,
            category=finding.get('category', 'General'),
            title=finding['title'],
            description=finding['description'],
            severity=SeverityLevel(finding.get('severity', 'medium')),
            score_impact=finding.get('score_impact', 5),
            remediation_steps=finding.get('remediation_steps', []),
            evidence=finding.get('evidence')
        )

    engine.save_assessment(assessment)
    return assessment
