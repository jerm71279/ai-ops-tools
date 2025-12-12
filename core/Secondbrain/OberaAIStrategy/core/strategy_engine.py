"""
OberaConnect AI Strategy Engine
Implementation of the Five AI Shifts Framework

The Five Shifts:
1. Leverage Charts - 1 person + AI = 5-10x output
2. Director Mindset - 80% directing / 20% doing
3. Data Moats - Proprietary data as competitive advantage
4. Autonomous Back Office - 98% AI / 2% human exceptions
5. Distribution Advantage - Relationships over features

This engine coordinates AI transformation across all OberaConnect projects
and provides unified feedback loops for continuous improvement.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class AIShift(Enum):
    """The Five AI Shifts"""
    LEVERAGE = "leverage_charts"
    DIRECTOR = "director_mindset"
    DATA_MOAT = "data_moat"
    AUTONOMOUS = "autonomous_back_office"
    DISTRIBUTION = "distribution_advantage"


class MaturityLevel(Enum):
    """AI transformation maturity levels"""
    NOT_STARTED = "not_started"
    EXPLORING = "exploring"
    IMPLEMENTING = "implementing"
    OPTIMIZING = "optimizing"
    TRANSFORMING = "transforming"


@dataclass
class ShiftMetrics:
    """Metrics for a single AI shift"""
    shift: AIShift
    maturity: MaturityLevel
    score: float  # 0-100
    automations_count: int = 0
    time_saved_hours: float = 0
    leverage_multiplier: float = 1.0
    data_points_collected: int = 0
    exceptions_rate: float = 0.0  # For 98/2 tracking
    last_assessed: Optional[str] = None
    initiatives: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['shift'] = self.shift.value
        data['maturity'] = self.maturity.value
        return data


@dataclass
class ProjectIntegration:
    """Tracks AI strategy integration with a project"""
    project_name: str
    project_path: str
    shifts_implemented: List[AIShift]
    feedback_loops: List[str]
    data_moat_contributions: List[str]
    automation_count: int
    leverage_multiplier: float
    last_updated: str

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['shifts_implemented'] = [s.value for s in self.shifts_implemented]
        return data


class OberaAIStrategyEngine:
    """
    Master engine for AI transformation strategy

    Coordinates the Five Shifts across all projects and
    provides unified metrics and insights.
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.data_dir / "strategy_state.json"
        self.metrics_file = self.data_dir / "shift_metrics.json"
        self.integrations_file = self.data_dir / "project_integrations.json"

        self._ensure_files()

    def _ensure_files(self):
        """Initialize state files"""
        if not self.state_file.exists():
            initial_state = {
                'initialized_at': datetime.now().isoformat(),
                'current_phase': 'foundation',
                'target_phase': 'optimization',
                'shifts': {
                    shift.value: {
                        'maturity': MaturityLevel.NOT_STARTED.value,
                        'score': 0,
                        'initiatives': []
                    }
                    for shift in AIShift
                },
                'milestones': [],
                'blockers': []
            }
            with open(self.state_file, 'w') as f:
                json.dump(initial_state, f, indent=2)

        if not self.metrics_file.exists():
            with open(self.metrics_file, 'w') as f:
                json.dump({
                    'snapshots': [],
                    'trends': {},
                    'last_updated': None
                }, f)

        if not self.integrations_file.exists():
            with open(self.integrations_file, 'w') as f:
                json.dump({
                    'projects': {},
                    'total_automations': 0,
                    'total_leverage': 1.0,
                    'data_moat_size': 0
                }, f)

    def register_project(
        self,
        project_name: str,
        project_path: str,
        shifts: List[AIShift],
        feedback_loops: List[str],
        data_contributions: List[str]
    ) -> None:
        """Register a project's AI strategy integration"""

        with open(self.integrations_file, 'r') as f:
            data = json.load(f)

        integration = ProjectIntegration(
            project_name=project_name,
            project_path=project_path,
            shifts_implemented=shifts,
            feedback_loops=feedback_loops,
            data_moat_contributions=data_contributions,
            automation_count=0,
            leverage_multiplier=1.0,
            last_updated=datetime.now().isoformat()
        )

        data['projects'][project_name] = integration.to_dict()

        with open(self.integrations_file, 'w') as f:
            json.dump(data, f, indent=2)

    def update_shift_metrics(
        self,
        shift: AIShift,
        metrics_update: Dict[str, Any]
    ) -> None:
        """Update metrics for a specific shift"""

        with open(self.state_file, 'r') as f:
            state = json.load(f)

        if shift.value in state['shifts']:
            state['shifts'][shift.value].update(metrics_update)
            state['shifts'][shift.value]['last_assessed'] = datetime.now().isoformat()

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

        # Record metrics snapshot
        self._record_metrics_snapshot()

    def _record_metrics_snapshot(self) -> None:
        """Record a point-in-time metrics snapshot"""

        with open(self.state_file, 'r') as f:
            state = json.load(f)

        with open(self.metrics_file, 'r') as f:
            metrics = json.load(f)

        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'shifts': state['shifts'],
            'overall_score': self._calculate_overall_score(state['shifts'])
        }

        metrics['snapshots'].append(snapshot)

        # Keep last 100 snapshots
        if len(metrics['snapshots']) > 100:
            metrics['snapshots'] = metrics['snapshots'][-100:]

        metrics['last_updated'] = datetime.now().isoformat()

        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)

    def _calculate_overall_score(self, shifts: Dict) -> float:
        """Calculate overall AI transformation score"""
        scores = [s.get('score', 0) for s in shifts.values()]
        return sum(scores) / max(len(scores), 1)

    def record_leverage_gain(
        self,
        project: str,
        task_type: str,
        time_before_minutes: float,
        time_after_minutes: float,
        description: str = None
    ) -> Dict[str, Any]:
        """
        SHIFT 1: Record a leverage gain from AI automation

        Tracks time saved and calculates leverage multiplier
        """

        leverage = time_before_minutes / max(time_after_minutes, 0.1)
        time_saved = time_before_minutes - time_after_minutes

        with open(self.integrations_file, 'r') as f:
            data = json.load(f)

        if project in data['projects']:
            # Update project leverage
            proj = data['projects'][project]
            proj['leverage_multiplier'] = (
                (proj['leverage_multiplier'] + leverage) / 2
            )  # Rolling average

        # Update total
        data['total_leverage'] = sum(
            p.get('leverage_multiplier', 1) for p in data['projects'].values()
        ) / max(len(data['projects']), 1)

        with open(self.integrations_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Update shift metrics
        self.update_shift_metrics(AIShift.LEVERAGE, {
            'time_saved_hours': time_saved / 60,
            'leverage_multiplier': leverage
        })

        return {
            'leverage_multiplier': leverage,
            'time_saved_minutes': time_saved,
            'description': description
        }

    def record_director_action(
        self,
        action_type: str,  # 'directing' or 'doing'
        task: str,
        duration_minutes: float,
        ai_assisted: bool = False
    ) -> None:
        """
        SHIFT 2: Track Director vs Doer ratio

        Goal: 80% directing / 20% doing
        """

        with open(self.state_file, 'r') as f:
            state = json.load(f)

        director_state = state['shifts'].get(AIShift.DIRECTOR.value, {})

        if 'time_directing' not in director_state:
            director_state['time_directing'] = 0
            director_state['time_doing'] = 0

        if action_type == 'directing':
            director_state['time_directing'] += duration_minutes
        else:
            director_state['time_doing'] += duration_minutes

        # Calculate ratio
        total_time = director_state['time_directing'] + director_state['time_doing']
        if total_time > 0:
            director_ratio = director_state['time_directing'] / total_time
            director_state['score'] = director_ratio * 100

        state['shifts'][AIShift.DIRECTOR.value] = director_state

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def record_data_contribution(
        self,
        project: str,
        data_type: str,
        record_count: int,
        description: str = None
    ) -> None:
        """
        SHIFT 3: Record data contribution to the Data Moat

        Tracks proprietary data accumulation
        """

        with open(self.integrations_file, 'r') as f:
            data = json.load(f)

        data['data_moat_size'] += record_count

        if project in data['projects']:
            if 'data_contributions' not in data['projects'][project]:
                data['projects'][project]['data_contributions'] = {}

            if data_type not in data['projects'][project]['data_contributions']:
                data['projects'][project]['data_contributions'][data_type] = 0

            data['projects'][project]['data_contributions'][data_type] += record_count

        with open(self.integrations_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Update shift metrics
        self.update_shift_metrics(AIShift.DATA_MOAT, {
            'data_points_collected': data['data_moat_size']
        })

    def record_automation_result(
        self,
        project: str,
        automation_name: str,
        was_exception: bool,
        required_human: bool
    ) -> None:
        """
        SHIFT 4: Track 98/2 automation ratio

        Goal: 98% automated / 2% human exceptions
        """

        with open(self.state_file, 'r') as f:
            state = json.load(f)

        autonomous_state = state['shifts'].get(AIShift.AUTONOMOUS.value, {})

        if 'total_operations' not in autonomous_state:
            autonomous_state['total_operations'] = 0
            autonomous_state['exceptions'] = 0

        autonomous_state['total_operations'] += 1
        if was_exception or required_human:
            autonomous_state['exceptions'] += 1

        # Calculate rate
        exception_rate = autonomous_state['exceptions'] / max(autonomous_state['total_operations'], 1)
        autonomous_state['exceptions_rate'] = exception_rate
        autonomous_state['score'] = (1 - exception_rate) * 100  # Higher is better

        state['shifts'][AIShift.AUTONOMOUS.value] = autonomous_state

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def get_strategy_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive strategy dashboard"""

        with open(self.state_file, 'r') as f:
            state = json.load(f)

        with open(self.integrations_file, 'r') as f:
            integrations = json.load(f)

        dashboard = {
            'generated_at': datetime.now().isoformat(),
            'overall_score': self._calculate_overall_score(state['shifts']),
            'current_phase': state['current_phase'],
            'shifts': {},
            'projects': {
                'count': len(integrations['projects']),
                'total_automations': integrations['total_automations'],
                'average_leverage': integrations['total_leverage'],
                'data_moat_size': integrations['data_moat_size']
            },
            'recommendations': []
        }

        # Process each shift
        for shift_id, shift_data in state['shifts'].items():
            shift_name = shift_id.replace('_', ' ').title()
            maturity = shift_data.get('maturity', 'not_started')
            score = shift_data.get('score', 0)

            dashboard['shifts'][shift_id] = {
                'name': shift_name,
                'maturity': maturity,
                'score': score,
                'status': self._get_shift_status(score)
            }

            # Add recommendations based on status
            if score < 30:
                dashboard['recommendations'].append({
                    'shift': shift_name,
                    'priority': 'high',
                    'recommendation': f"Focus on implementing {shift_name} - currently at {score:.0f}%"
                })
            elif score < 70:
                dashboard['recommendations'].append({
                    'shift': shift_name,
                    'priority': 'medium',
                    'recommendation': f"Continue developing {shift_name} - {score:.0f}% complete"
                })

        return dashboard

    def _get_shift_status(self, score: float) -> str:
        """Get status label for a shift score"""
        if score >= 90:
            return 'transforming'
        elif score >= 70:
            return 'optimizing'
        elif score >= 40:
            return 'implementing'
        elif score >= 10:
            return 'exploring'
        else:
            return 'not_started'

    def get_30_60_90_status(self) -> Dict[str, Any]:
        """
        Get status against the 30-60-90 day implementation plan
        from the OberaAI Strategy
        """

        with open(self.state_file, 'r') as f:
            state = json.load(f)

        initialized = datetime.fromisoformat(state['initialized_at'])
        days_elapsed = (datetime.now() - initialized).days

        plan = {
            'days_elapsed': days_elapsed,
            'current_period': 'Day 1-30' if days_elapsed <= 30 else ('Day 31-60' if days_elapsed <= 60 else 'Day 61-90'),
            'phases': {}
        }

        # Day 1-30: Foundation
        phase1_tasks = [
            ('Audit leverage opportunities', state['shifts'].get('leverage_charts', {}).get('score', 0) > 10),
            ('Clean data sources', state['shifts'].get('data_moat', {}).get('data_points_collected', 0) > 0),
            ('Define AI Ops function', True),  # Manual check needed
            ('Pick first automation', state['shifts'].get('autonomous_back_office', {}).get('total_operations', 0) > 0),
            ('Set up AI lab', True)  # Manual check needed
        ]
        plan['phases']['day_1_30'] = {
            'name': 'Foundation',
            'due': 'Day 30',
            'tasks': [{'task': t[0], 'complete': t[1]} for t in phase1_tasks],
            'completion': sum(1 for t in phase1_tasks if t[1]) / len(phase1_tasks)
        }

        # Day 31-60: Build Leverage
        phase2_tasks = [
            ('Deploy ticket automation', False),
            ('Create director playbooks', False),
            ('Launch distribution channel', False),
            ('Run first data analysis', state['shifts'].get('data_moat', {}).get('score', 0) > 20)
        ]
        plan['phases']['day_31_60'] = {
            'name': 'Build Leverage',
            'due': 'Day 60',
            'tasks': [{'task': t[0], 'complete': t[1]} for t in phase2_tasks],
            'completion': sum(1 for t in phase2_tasks if t[1]) / len(phase2_tasks)
        }

        # Day 61-90: Scale & Differentiate
        phase3_tasks = [
            ('Expand autonomous back office', state['shifts'].get('autonomous_back_office', {}).get('score', 0) > 50),
            ('Measure leverage gains', state['shifts'].get('leverage_charts', {}).get('leverage_multiplier', 1) > 2),
            ('Pre-sell AI service', False),
            ('Establish partnership', False)
        ]
        plan['phases']['day_61_90'] = {
            'name': 'Scale & Differentiate',
            'due': 'Day 90',
            'tasks': [{'task': t[0], 'complete': t[1]} for t in phase3_tasks],
            'completion': sum(1 for t in phase3_tasks if t[1]) / len(phase3_tasks)
        }

        # Overall status
        all_tasks = phase1_tasks + phase2_tasks + phase3_tasks
        plan['overall_completion'] = sum(1 for t in all_tasks if t[1]) / len(all_tasks)

        # Status assessment
        if days_elapsed <= 30:
            expected = plan['phases']['day_1_30']['completion']
            plan['status'] = 'on_track' if expected >= 0.5 else 'behind'
        elif days_elapsed <= 60:
            expected = (plan['phases']['day_1_30']['completion'] + plan['phases']['day_31_60']['completion']) / 2
            plan['status'] = 'on_track' if expected >= 0.5 else 'behind'
        else:
            plan['status'] = 'on_track' if plan['overall_completion'] >= 0.5 else 'behind'

        return plan

    def generate_weekly_report(self) -> str:
        """Generate weekly AI transformation report"""

        dashboard = self.get_strategy_dashboard()
        plan_status = self.get_30_60_90_status()

        lines = [
            "=" * 60,
            "OBERACONNECT AI TRANSFORMATION - WEEKLY REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
            "=" * 60,
            "",
            f"OVERALL TRANSFORMATION SCORE: {dashboard['overall_score']:.0f}/100",
            f"Current Phase: {dashboard['current_phase'].upper()}",
            f"30-60-90 Status: {plan_status['status'].upper()} (Day {plan_status['days_elapsed']})",
            "",
            "-" * 60,
            "THE FIVE SHIFTS",
            "-" * 60,
        ]

        for shift_id, shift_data in dashboard['shifts'].items():
            status_icon = "✓" if shift_data['score'] >= 70 else ("◐" if shift_data['score'] >= 30 else "○")
            lines.append(f"  {status_icon} {shift_data['name']}: {shift_data['score']:.0f}% ({shift_data['status']})")

        lines.extend([
            "",
            "-" * 60,
            "PROJECT INTEGRATIONS",
            "-" * 60,
            f"  Projects with AI: {dashboard['projects']['count']}",
            f"  Average Leverage: {dashboard['projects']['average_leverage']:.1f}x",
            f"  Data Moat Size: {dashboard['projects']['data_moat_size']:,} records",
            "",
        ])

        if dashboard['recommendations']:
            lines.append("-" * 60)
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 60)
            for rec in dashboard['recommendations'][:5]:
                priority_icon = "❗" if rec['priority'] == 'high' else "→"
                lines.append(f"  {priority_icon} {rec['recommendation']}")

        lines.extend(["", "=" * 60])

        return "\n".join(lines)


# Convenience functions for common operations
def record_automation(
    project: str,
    task: str,
    time_before: float,
    time_after: float
) -> Dict:
    """Quick function to record an automation gain"""
    engine = OberaAIStrategyEngine()
    return engine.record_leverage_gain(
        project=project,
        task_type=task,
        time_before_minutes=time_before,
        time_after_minutes=time_after
    )


def get_dashboard() -> Dict:
    """Quick function to get the strategy dashboard"""
    engine = OberaAIStrategyEngine()
    return engine.get_strategy_dashboard()
