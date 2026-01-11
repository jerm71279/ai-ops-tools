"""
OberaConnect Assessment Feedback Loops
Aligned with OberaAI Strategy - Data Moats + Autonomous Operations

Four Core Feedback Loops:
1. Score Tracking Loop - Monitor improvement over time
2. Remediation Loop - Track and verify fixes
3. Pattern Learning Loop - Build proprietary insights (Data Moat)
4. Benchmark Loop - Compare against industry/peer groups
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class FeedbackEvent:
    """Single feedback event for tracking"""
    event_id: str
    event_type: str  # score_change, remediation, pattern, benchmark
    timestamp: str
    customer_id: str
    assessment_id: str
    data: Dict[str, Any]
    processed: bool = False


class ScoreTrackingLoop:
    """
    FEEDBACK LOOP 1: Score Tracking

    Monitors assessment scores over time to:
    - Identify improvement trends
    - Detect declining security posture
    - Trigger alerts for significant changes
    - Build customer health dashboards
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.tracking_file = data_dir / "score_tracking.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.tracking_file.exists():
            with open(self.tracking_file, 'w') as f:
                json.dump({'customers': {}, 'alerts': [], 'trends': {}}, f)

    def record_score(
        self,
        customer_id: str,
        assessment_type: str,
        score: float,
        assessment_id: str
    ) -> Dict[str, Any]:
        """Record a new score and return trend analysis"""

        with open(self.tracking_file, 'r') as f:
            data = json.load(f)

        # Initialize customer tracking if new
        if customer_id not in data['customers']:
            data['customers'][customer_id] = {}

        if assessment_type not in data['customers'][customer_id]:
            data['customers'][customer_id][assessment_type] = []

        # Add new score
        entry = {
            'score': score,
            'assessment_id': assessment_id,
            'timestamp': datetime.now().isoformat()
        }
        data['customers'][customer_id][assessment_type].append(entry)

        # Calculate trend
        scores = data['customers'][customer_id][assessment_type]
        trend_analysis = self._analyze_trend(scores)

        # Check for alerts
        alerts = self._check_alerts(customer_id, assessment_type, scores, trend_analysis)
        data['alerts'].extend(alerts)

        # Update trends
        data['trends'][f"{customer_id}_{assessment_type}"] = trend_analysis

        with open(self.tracking_file, 'w') as f:
            json.dump(data, f, indent=2)

        return {
            'current_score': score,
            'trend': trend_analysis,
            'alerts': alerts
        }

    def _analyze_trend(self, scores: List[Dict]) -> Dict[str, Any]:
        """Analyze score trend over time"""

        if len(scores) < 2:
            return {
                'direction': 'insufficient_data',
                'change': 0,
                'assessment_count': len(scores)
            }

        recent = scores[-1]['score']
        previous = scores[-2]['score']
        change = recent - previous

        # Calculate moving average if enough data
        if len(scores) >= 3:
            recent_avg = sum(s['score'] for s in scores[-3:]) / 3
            older_avg = sum(s['score'] for s in scores[:-3][-3:]) / min(3, len(scores) - 3) if len(scores) > 3 else scores[0]['score']
            trend_strength = recent_avg - older_avg
        else:
            trend_strength = change

        if change > 10:
            direction = 'significantly_improving'
        elif change > 0:
            direction = 'improving'
        elif change < -10:
            direction = 'significantly_declining'
        elif change < 0:
            direction = 'declining'
        else:
            direction = 'stable'

        return {
            'direction': direction,
            'change': change,
            'trend_strength': trend_strength,
            'assessment_count': len(scores),
            'all_time_high': max(s['score'] for s in scores),
            'all_time_low': min(s['score'] for s in scores),
            'average': sum(s['score'] for s in scores) / len(scores)
        }

    def _check_alerts(
        self,
        customer_id: str,
        assessment_type: str,
        scores: List[Dict],
        trend: Dict
    ) -> List[Dict]:
        """Generate alerts based on score changes"""

        alerts = []

        if len(scores) < 2:
            return alerts

        current = scores[-1]['score']
        previous = scores[-2]['score']

        # Alert: Significant decline
        if current < previous - 15:
            alerts.append({
                'type': 'significant_decline',
                'severity': 'high',
                'customer_id': customer_id,
                'assessment_type': assessment_type,
                'message': f"Security score dropped {previous - current:.1f} points",
                'timestamp': datetime.now().isoformat(),
                'action_required': True
            })

        # Alert: Score below threshold
        if current < 50:
            alerts.append({
                'type': 'below_threshold',
                'severity': 'critical',
                'customer_id': customer_id,
                'assessment_type': assessment_type,
                'message': f"Security score ({current:.1f}) below minimum threshold (50)",
                'timestamp': datetime.now().isoformat(),
                'action_required': True
            })

        # Alert: Consistent decline
        if trend['direction'] == 'significantly_declining':
            alerts.append({
                'type': 'trend_alert',
                'severity': 'medium',
                'customer_id': customer_id,
                'assessment_type': assessment_type,
                'message': "Consistent declining trend detected",
                'timestamp': datetime.now().isoformat(),
                'action_required': True
            })

        return alerts

    def get_customer_dashboard(self, customer_id: str) -> Dict[str, Any]:
        """Get dashboard data for a customer"""

        with open(self.tracking_file, 'r') as f:
            data = json.load(f)

        customer_data = data['customers'].get(customer_id, {})

        dashboard = {
            'customer_id': customer_id,
            'assessments': {},
            'overall_health': 'unknown',
            'active_alerts': []
        }

        total_score = 0
        count = 0

        for assessment_type, scores in customer_data.items():
            if scores:
                latest = scores[-1]
                trend = data['trends'].get(f"{customer_id}_{assessment_type}", {})

                dashboard['assessments'][assessment_type] = {
                    'current_score': latest['score'],
                    'last_assessed': latest['timestamp'],
                    'trend': trend.get('direction', 'unknown'),
                    'history_count': len(scores)
                }

                total_score += latest['score']
                count += 1

        if count > 0:
            avg_score = total_score / count
            if avg_score >= 80:
                dashboard['overall_health'] = 'healthy'
            elif avg_score >= 60:
                dashboard['overall_health'] = 'needs_attention'
            else:
                dashboard['overall_health'] = 'at_risk'

        # Get active alerts
        dashboard['active_alerts'] = [
            a for a in data['alerts']
            if a['customer_id'] == customer_id and a.get('action_required', False)
        ]

        return dashboard


class RemediationLoop:
    """
    FEEDBACK LOOP 2: Remediation Tracking

    Tracks remediation progress to:
    - Monitor fix completion rates
    - Calculate time-to-remediation
    - Identify blockers and delays
    - Verify fixes in subsequent assessments
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.remediation_file = data_dir / "remediation_tracking.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.remediation_file.exists():
            with open(self.remediation_file, 'w') as f:
                json.dump({
                    'active_remediations': {},
                    'completed': [],
                    'metrics': {
                        'avg_time_to_fix': {},
                        'completion_rate': {},
                        'by_severity': {}
                    }
                }, f)

    def create_remediation(
        self,
        customer_id: str,
        finding_id: str,
        finding_title: str,
        severity: str,
        target_date: str = None
    ) -> str:
        """Create a new remediation tracking entry"""

        remediation_id = f"rem_{finding_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        with open(self.remediation_file, 'r') as f:
            data = json.load(f)

        if customer_id not in data['active_remediations']:
            data['active_remediations'][customer_id] = {}

        data['active_remediations'][customer_id][remediation_id] = {
            'finding_id': finding_id,
            'finding_title': finding_title,
            'severity': severity,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'target_date': target_date,
            'updates': [],
            'verification_status': 'unverified'
        }

        with open(self.remediation_file, 'w') as f:
            json.dump(data, f, indent=2)

        return remediation_id

    def update_status(
        self,
        customer_id: str,
        remediation_id: str,
        status: str,
        notes: str = None
    ) -> Dict[str, Any]:
        """Update remediation status"""

        with open(self.remediation_file, 'r') as f:
            data = json.load(f)

        if customer_id not in data['active_remediations']:
            return {'error': 'Customer not found'}

        if remediation_id not in data['active_remediations'][customer_id]:
            return {'error': 'Remediation not found'}

        rem = data['active_remediations'][customer_id][remediation_id]
        old_status = rem['status']
        rem['status'] = status

        update = {
            'timestamp': datetime.now().isoformat(),
            'from_status': old_status,
            'to_status': status,
            'notes': notes
        }
        rem['updates'].append(update)

        # If completed, calculate metrics and move to completed list
        if status == 'completed':
            rem['completed_at'] = datetime.now().isoformat()
            created = datetime.fromisoformat(rem['created_at'])
            completed = datetime.fromisoformat(rem['completed_at'])
            rem['time_to_fix_days'] = (completed - created).days

            # Update metrics
            self._update_metrics(data, rem)

            # Move to completed
            data['completed'].append({
                'customer_id': customer_id,
                'remediation_id': remediation_id,
                **rem
            })
            del data['active_remediations'][customer_id][remediation_id]

        with open(self.remediation_file, 'w') as f:
            json.dump(data, f, indent=2)

        return {'status': 'updated', 'remediation': rem}

    def _update_metrics(self, data: Dict, remediation: Dict) -> None:
        """Update aggregate metrics"""

        severity = remediation['severity']

        # Time to fix by severity
        if severity not in data['metrics']['avg_time_to_fix']:
            data['metrics']['avg_time_to_fix'][severity] = {'total_days': 0, 'count': 0}

        data['metrics']['avg_time_to_fix'][severity]['total_days'] += remediation.get('time_to_fix_days', 0)
        data['metrics']['avg_time_to_fix'][severity]['count'] += 1

        # Completion rate by severity
        if severity not in data['metrics']['completion_rate']:
            data['metrics']['completion_rate'][severity] = {'completed': 0, 'total': 0}

        data['metrics']['completion_rate'][severity]['completed'] += 1

    def verify_remediation(
        self,
        customer_id: str,
        remediation_id: str,
        verified: bool,
        verification_notes: str = None
    ) -> Dict[str, Any]:
        """
        FEEDBACK LOOP: Verify fix in subsequent assessment

        This closes the loop by confirming fixes actually worked
        """

        with open(self.remediation_file, 'r') as f:
            data = json.load(f)

        # Check in completed remediations
        for completed in data['completed']:
            if (completed['customer_id'] == customer_id and
                completed['remediation_id'] == remediation_id):

                completed['verification_status'] = 'verified' if verified else 'failed'
                completed['verification_date'] = datetime.now().isoformat()
                completed['verification_notes'] = verification_notes

                if not verified:
                    # Reopen remediation if verification failed
                    return self._reopen_remediation(data, completed)

                with open(self.remediation_file, 'w') as f:
                    json.dump(data, f, indent=2)

                return {'status': 'verified', 'remediation': completed}

        return {'error': 'Remediation not found in completed list'}

    def _reopen_remediation(self, data: Dict, completed: Dict) -> Dict:
        """Reopen a failed remediation"""

        customer_id = completed['customer_id']

        if customer_id not in data['active_remediations']:
            data['active_remediations'][customer_id] = {}

        new_id = f"{completed['remediation_id']}_reopened"
        data['active_remediations'][customer_id][new_id] = {
            'finding_id': completed['finding_id'],
            'finding_title': completed['finding_title'],
            'severity': completed['severity'],
            'status': 'reopened',
            'created_at': datetime.now().isoformat(),
            'original_remediation': completed['remediation_id'],
            'updates': [{
                'timestamp': datetime.now().isoformat(),
                'notes': 'Reopened due to failed verification'
            }],
            'verification_status': 'pending_reverification'
        }

        with open(self.remediation_file, 'w') as f:
            json.dump(data, f, indent=2)

        return {
            'status': 'reopened',
            'new_remediation_id': new_id,
            'reason': 'verification_failed'
        }

    def get_remediation_report(self, customer_id: str = None) -> Dict[str, Any]:
        """Get remediation metrics report"""

        with open(self.remediation_file, 'r') as f:
            data = json.load(f)

        report = {
            'generated_at': datetime.now().isoformat(),
            'metrics': data['metrics'],
            'active_count': 0,
            'completed_count': len(data['completed']),
            'overdue': []
        }

        # Calculate averages
        for severity, metrics in data['metrics']['avg_time_to_fix'].items():
            if metrics['count'] > 0:
                metrics['average'] = metrics['total_days'] / metrics['count']

        # Count active and find overdue
        for cust_id, remediations in data['active_remediations'].items():
            if customer_id and cust_id != customer_id:
                continue

            for rem_id, rem in remediations.items():
                report['active_count'] += 1

                if rem.get('target_date'):
                    target = datetime.fromisoformat(rem['target_date'])
                    if target < datetime.now():
                        report['overdue'].append({
                            'customer_id': cust_id,
                            'remediation_id': rem_id,
                            'finding': rem['finding_title'],
                            'severity': rem['severity'],
                            'days_overdue': (datetime.now() - target).days
                        })

        return report


class PatternLearningLoop:
    """
    FEEDBACK LOOP 3: Pattern Learning (DATA MOAT)

    Builds proprietary insights from assessment data:
    - Common vulnerabilities by industry
    - Technology-specific risk patterns
    - Effective remediation strategies
    - Predictive risk indicators
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.patterns_file = data_dir / "learned_patterns.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.patterns_file.exists():
            with open(self.patterns_file, 'w') as f:
                json.dump({
                    'industry_patterns': {},
                    'technology_patterns': {},
                    'size_patterns': {},
                    'finding_correlations': {},
                    'remediation_effectiveness': {},
                    'predictive_indicators': {},
                    'last_analysis': None
                }, f)

    def learn_from_assessment(
        self,
        assessment_data: Dict,
        findings: List[Dict],
        industry: str = None,
        technology_stack: List[str] = None,
        employee_count: int = None
    ) -> Dict[str, Any]:
        """
        Learn patterns from a completed assessment

        This is where the DATA MOAT grows - every assessment
        makes the pattern database more valuable
        """

        with open(self.patterns_file, 'r') as f:
            patterns = json.load(f)

        insights_generated = []

        # Learn industry patterns
        if industry:
            if industry not in patterns['industry_patterns']:
                patterns['industry_patterns'][industry] = {
                    'assessment_count': 0,
                    'avg_score': 0,
                    'total_score': 0,
                    'common_findings': {},
                    'risk_profile': {}
                }

            ind_data = patterns['industry_patterns'][industry]
            ind_data['assessment_count'] += 1
            ind_data['total_score'] += assessment_data.get('overall_score', 0)
            ind_data['avg_score'] = ind_data['total_score'] / ind_data['assessment_count']

            for finding in findings:
                title = finding.get('title', 'Unknown')
                if title not in ind_data['common_findings']:
                    ind_data['common_findings'][title] = 0
                ind_data['common_findings'][title] += 1

            insights_generated.append(f"Updated {industry} industry pattern database")

        # Learn technology patterns
        if technology_stack:
            for tech in technology_stack:
                if tech not in patterns['technology_patterns']:
                    patterns['technology_patterns'][tech] = {
                        'assessment_count': 0,
                        'associated_findings': {},
                        'avg_score': 0,
                        'total_score': 0
                    }

                tech_data = patterns['technology_patterns'][tech]
                tech_data['assessment_count'] += 1
                tech_data['total_score'] += assessment_data.get('overall_score', 0)
                tech_data['avg_score'] = tech_data['total_score'] / tech_data['assessment_count']

                for finding in findings:
                    title = finding.get('title', 'Unknown')
                    if title not in tech_data['associated_findings']:
                        tech_data['associated_findings'][title] = 0
                    tech_data['associated_findings'][title] += 1

            insights_generated.append(f"Updated patterns for {len(technology_stack)} technologies")

        # Learn size patterns
        if employee_count:
            size_bucket = self._get_size_bucket(employee_count)
            if size_bucket not in patterns['size_patterns']:
                patterns['size_patterns'][size_bucket] = {
                    'assessment_count': 0,
                    'avg_score': 0,
                    'total_score': 0,
                    'common_gaps': {}
                }

            size_data = patterns['size_patterns'][size_bucket]
            size_data['assessment_count'] += 1
            size_data['total_score'] += assessment_data.get('overall_score', 0)
            size_data['avg_score'] = size_data['total_score'] / size_data['assessment_count']

        # Learn finding correlations
        finding_titles = [f.get('title') for f in findings]
        for i, f1 in enumerate(finding_titles):
            if f1 not in patterns['finding_correlations']:
                patterns['finding_correlations'][f1] = {}

            for f2 in finding_titles[i+1:]:
                if f2 not in patterns['finding_correlations'][f1]:
                    patterns['finding_correlations'][f1][f2] = 0
                patterns['finding_correlations'][f1][f2] += 1

        patterns['last_analysis'] = datetime.now().isoformat()

        with open(self.patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2)

        return {
            'patterns_updated': True,
            'insights': insights_generated
        }

    def _get_size_bucket(self, employee_count: int) -> str:
        """Categorize by company size"""
        if employee_count < 10:
            return 'micro'
        elif employee_count < 50:
            return 'small'
        elif employee_count < 200:
            return 'medium'
        elif employee_count < 1000:
            return 'large'
        else:
            return 'enterprise'

    def get_predictive_insights(
        self,
        industry: str = None,
        technology_stack: List[str] = None,
        employee_count: int = None
    ) -> Dict[str, Any]:
        """
        DATA MOAT VALUE: Predictive insights based on patterns

        This is the competitive advantage - predicting likely
        findings BEFORE the assessment based on customer profile
        """

        with open(self.patterns_file, 'r') as f:
            patterns = json.load(f)

        predictions = {
            'likely_findings': [],
            'expected_score_range': {'min': 0, 'max': 100},
            'high_risk_areas': [],
            'recommendations': []
        }

        # Industry-based predictions
        if industry and industry in patterns['industry_patterns']:
            ind_data = patterns['industry_patterns'][industry]

            # Predict score based on industry average
            predictions['expected_score_range'] = {
                'min': max(0, ind_data['avg_score'] - 15),
                'max': min(100, ind_data['avg_score'] + 15)
            }

            # Top findings in this industry
            if ind_data['common_findings']:
                sorted_findings = sorted(
                    ind_data['common_findings'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]

                for title, count in sorted_findings:
                    likelihood = count / ind_data['assessment_count']
                    predictions['likely_findings'].append({
                        'finding': title,
                        'likelihood': f"{likelihood:.0%}",
                        'basis': f"Found in {count}/{ind_data['assessment_count']} {industry} assessments"
                    })

        # Technology-based predictions
        if technology_stack:
            for tech in technology_stack:
                if tech in patterns['technology_patterns']:
                    tech_data = patterns['technology_patterns'][tech]

                    if tech_data['associated_findings']:
                        top_finding = max(
                            tech_data['associated_findings'].items(),
                            key=lambda x: x[1]
                        )
                        predictions['high_risk_areas'].append({
                            'technology': tech,
                            'common_finding': top_finding[0],
                            'frequency': top_finding[1]
                        })

        # Size-based predictions
        if employee_count:
            size_bucket = self._get_size_bucket(employee_count)
            if size_bucket in patterns['size_patterns']:
                size_data = patterns['size_patterns'][size_bucket]
                predictions['recommendations'].append({
                    'type': 'size_based',
                    'recommendation': f"Companies of this size ({size_bucket}) typically score {size_data['avg_score']:.0f}",
                    'action': 'Focus pre-assessment on common gaps for this company size'
                })

        return predictions

    def get_correlation_insights(self, finding_title: str) -> List[Dict]:
        """Get correlated findings - if you find X, you often find Y"""

        with open(self.patterns_file, 'r') as f:
            patterns = json.load(f)

        correlations = patterns.get('finding_correlations', {}).get(finding_title, {})

        insights = []
        for correlated, count in sorted(correlations.items(), key=lambda x: x[1], reverse=True)[:5]:
            insights.append({
                'correlated_finding': correlated,
                'co_occurrence_count': count,
                'recommendation': f"When '{finding_title}' is found, also check for '{correlated}'"
            })

        return insights


class BenchmarkLoop:
    """
    FEEDBACK LOOP 4: Benchmark Comparison

    Provides context by comparing against:
    - Industry peers
    - Similar-sized companies
    - Overall customer base
    - Best-in-class performers
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.benchmark_file = data_dir / "benchmarks.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.benchmark_file.exists():
            with open(self.benchmark_file, 'w') as f:
                json.dump({
                    'global': {'scores': [], 'percentiles': {}},
                    'by_industry': {},
                    'by_size': {},
                    'by_assessment_type': {},
                    'best_in_class': {},
                    'last_updated': None
                }, f)

    def update_benchmarks(
        self,
        score: float,
        assessment_type: str,
        industry: str = None,
        employee_count: int = None
    ) -> None:
        """Update benchmark data with new assessment"""

        with open(self.benchmark_file, 'r') as f:
            benchmarks = json.load(f)

        # Update global benchmarks
        benchmarks['global']['scores'].append(score)
        self._recalculate_percentiles(benchmarks['global'])

        # Update by assessment type
        if assessment_type not in benchmarks['by_assessment_type']:
            benchmarks['by_assessment_type'][assessment_type] = {'scores': [], 'percentiles': {}}
        benchmarks['by_assessment_type'][assessment_type]['scores'].append(score)
        self._recalculate_percentiles(benchmarks['by_assessment_type'][assessment_type])

        # Update by industry
        if industry:
            if industry not in benchmarks['by_industry']:
                benchmarks['by_industry'][industry] = {'scores': [], 'percentiles': {}}
            benchmarks['by_industry'][industry]['scores'].append(score)
            self._recalculate_percentiles(benchmarks['by_industry'][industry])

        # Update by size
        if employee_count:
            size_bucket = self._get_size_bucket(employee_count)
            if size_bucket not in benchmarks['by_size']:
                benchmarks['by_size'][size_bucket] = {'scores': [], 'percentiles': {}}
            benchmarks['by_size'][size_bucket]['scores'].append(score)
            self._recalculate_percentiles(benchmarks['by_size'][size_bucket])

        # Track best in class
        if score >= 90:
            key = f"{assessment_type}_{industry or 'general'}"
            if key not in benchmarks['best_in_class']:
                benchmarks['best_in_class'][key] = []
            benchmarks['best_in_class'][key].append({
                'score': score,
                'timestamp': datetime.now().isoformat()
            })

        benchmarks['last_updated'] = datetime.now().isoformat()

        with open(self.benchmark_file, 'w') as f:
            json.dump(benchmarks, f, indent=2)

    def _get_size_bucket(self, employee_count: int) -> str:
        if employee_count < 10:
            return 'micro'
        elif employee_count < 50:
            return 'small'
        elif employee_count < 200:
            return 'medium'
        elif employee_count < 1000:
            return 'large'
        else:
            return 'enterprise'

    def _recalculate_percentiles(self, data: Dict) -> None:
        """Recalculate percentile thresholds"""
        scores = sorted(data['scores'])
        n = len(scores)

        if n == 0:
            return

        data['percentiles'] = {
            '25th': scores[int(n * 0.25)] if n >= 4 else scores[0],
            '50th': scores[int(n * 0.5)] if n >= 2 else scores[0],
            '75th': scores[int(n * 0.75)] if n >= 4 else scores[-1],
            '90th': scores[int(n * 0.9)] if n >= 10 else scores[-1],
            'mean': sum(scores) / n,
            'count': n
        }

    def get_benchmark_comparison(
        self,
        score: float,
        assessment_type: str,
        industry: str = None,
        employee_count: int = None
    ) -> Dict[str, Any]:
        """Get benchmark comparison for a score"""

        with open(self.benchmark_file, 'r') as f:
            benchmarks = json.load(f)

        comparison = {
            'score': score,
            'comparisons': {}
        }

        # Global comparison
        global_data = benchmarks['global']
        if global_data['scores']:
            comparison['comparisons']['global'] = {
                'percentile': self._calculate_percentile(score, global_data['scores']),
                'vs_mean': score - global_data['percentiles'].get('mean', 0),
                'sample_size': len(global_data['scores'])
            }

        # Assessment type comparison
        if assessment_type in benchmarks['by_assessment_type']:
            type_data = benchmarks['by_assessment_type'][assessment_type]
            if type_data['scores']:
                comparison['comparisons']['assessment_type'] = {
                    'percentile': self._calculate_percentile(score, type_data['scores']),
                    'vs_mean': score - type_data['percentiles'].get('mean', 0),
                    'sample_size': len(type_data['scores'])
                }

        # Industry comparison
        if industry and industry in benchmarks['by_industry']:
            ind_data = benchmarks['by_industry'][industry]
            if ind_data['scores']:
                comparison['comparisons']['industry'] = {
                    'industry': industry,
                    'percentile': self._calculate_percentile(score, ind_data['scores']),
                    'vs_mean': score - ind_data['percentiles'].get('mean', 0),
                    'sample_size': len(ind_data['scores'])
                }

        # Size comparison
        if employee_count:
            size_bucket = self._get_size_bucket(employee_count)
            if size_bucket in benchmarks['by_size']:
                size_data = benchmarks['by_size'][size_bucket]
                if size_data['scores']:
                    comparison['comparisons']['company_size'] = {
                        'size_category': size_bucket,
                        'percentile': self._calculate_percentile(score, size_data['scores']),
                        'vs_mean': score - size_data['percentiles'].get('mean', 0),
                        'sample_size': len(size_data['scores'])
                    }

        # Generate insights
        comparison['insights'] = self._generate_benchmark_insights(comparison)

        return comparison

    def _calculate_percentile(self, score: float, scores: List[float]) -> int:
        """Calculate percentile ranking"""
        if not scores:
            return 50

        below = sum(1 for s in scores if s < score)
        return int((below / len(scores)) * 100)

    def _generate_benchmark_insights(self, comparison: Dict) -> List[str]:
        """Generate human-readable insights from comparison"""

        insights = []

        for comp_type, data in comparison['comparisons'].items():
            percentile = data.get('percentile', 50)

            if percentile >= 90:
                insights.append(f"Top 10% performer in {comp_type.replace('_', ' ')}")
            elif percentile >= 75:
                insights.append(f"Above average in {comp_type.replace('_', ' ')} (top 25%)")
            elif percentile <= 25:
                insights.append(f"Below average in {comp_type.replace('_', ' ')} - improvement needed")

            vs_mean = data.get('vs_mean', 0)
            if vs_mean > 15:
                insights.append(f"Significantly above {comp_type.replace('_', ' ')} average (+{vs_mean:.0f} points)")
            elif vs_mean < -15:
                insights.append(f"Significantly below {comp_type.replace('_', ' ')} average ({vs_mean:.0f} points)")

        return insights


class FeedbackLoopOrchestrator:
    """
    Master orchestrator for all feedback loops

    Coordinates the four loops to provide unified insights
    and ensure data flows between loops appropriately
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.score_loop = ScoreTrackingLoop(self.data_dir)
        self.remediation_loop = RemediationLoop(self.data_dir)
        self.pattern_loop = PatternLearningLoop(self.data_dir)
        self.benchmark_loop = BenchmarkLoop(self.data_dir)

    def process_assessment(
        self,
        assessment_data: Dict,
        findings: List[Dict],
        customer_id: str,
        industry: str = None,
        technology_stack: List[str] = None,
        employee_count: int = None
    ) -> Dict[str, Any]:
        """
        Process a completed assessment through all feedback loops

        This is the main entry point that triggers all learning and tracking
        """

        results = {
            'loops_processed': [],
            'insights': [],
            'actions_created': []
        }

        assessment_type = assessment_data.get('assessment_type', 'general')
        score = assessment_data.get('overall_score', 0)
        assessment_id = assessment_data.get('id', 'unknown')

        # 1. Score Tracking Loop
        score_result = self.score_loop.record_score(
            customer_id=customer_id,
            assessment_type=assessment_type,
            score=score,
            assessment_id=assessment_id
        )
        results['loops_processed'].append('score_tracking')
        results['trend'] = score_result['trend']

        if score_result.get('alerts'):
            results['actions_created'].extend(score_result['alerts'])

        # 2. Remediation Loop - Create tracking for findings
        for finding in findings:
            if finding.get('severity') in ['critical', 'high']:
                rem_id = self.remediation_loop.create_remediation(
                    customer_id=customer_id,
                    finding_id=finding.get('id', 'unknown'),
                    finding_title=finding.get('title', 'Unknown Finding'),
                    severity=finding.get('severity', 'medium')
                )
                results['actions_created'].append({
                    'type': 'remediation_created',
                    'remediation_id': rem_id,
                    'finding': finding.get('title')
                })
        results['loops_processed'].append('remediation')

        # 3. Pattern Learning Loop
        pattern_result = self.pattern_loop.learn_from_assessment(
            assessment_data=assessment_data,
            findings=findings,
            industry=industry,
            technology_stack=technology_stack,
            employee_count=employee_count
        )
        results['loops_processed'].append('pattern_learning')
        results['insights'].extend(pattern_result.get('insights', []))

        # 4. Benchmark Loop
        self.benchmark_loop.update_benchmarks(
            score=score,
            assessment_type=assessment_type,
            industry=industry,
            employee_count=employee_count
        )
        benchmark_comparison = self.benchmark_loop.get_benchmark_comparison(
            score=score,
            assessment_type=assessment_type,
            industry=industry,
            employee_count=employee_count
        )
        results['loops_processed'].append('benchmark')
        results['benchmark'] = benchmark_comparison
        results['insights'].extend(benchmark_comparison.get('insights', []))

        return results

    def get_unified_insights(self, customer_id: str) -> Dict[str, Any]:
        """Get unified insights from all loops for a customer"""

        return {
            'dashboard': self.score_loop.get_customer_dashboard(customer_id),
            'remediation_status': self.remediation_loop.get_remediation_report(customer_id),
            'generated_at': datetime.now().isoformat()
        }
