"""
OberaConnect AI Strategy - Feedback Aggregator
Connects all project feedback loops to the central strategy engine

This is the critical bridge that transforms isolated feedback loops
into a unified learning system.

Flow:
Project Feedback Loops → Aggregator → Strategy Engine → Dashboard/Actions
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from ..core.strategy_engine import OberaAIStrategyEngine, AIShift


class FeedbackAggregator:
    """
    Aggregates feedback from all project feedback loops
    and pushes metrics to the central strategy engine
    """

    def __init__(self, strategy_engine: OberaAIStrategyEngine = None):
        self.engine = strategy_engine or OberaAIStrategyEngine()
        self.aggregation_log = self.engine.data_dir / "aggregation_log.json"
        self._ensure_log()

        # Project feedback paths
        self.feedback_sources = {
            'Assessment': {
                'path': Path('/home/mavrick/Projects/Assessment/data'),
                'loops': ['score_tracking.json', 'remediation_tracking.json',
                         'learned_patterns.json', 'benchmarks.json']
            },
            'Azure_Projects': {
                'path': Path('/home/mavrick/Projects/Azure_Projects/feedback'),
                'loops': ['robocopy_operations.json', 'disk_clone_operations.json',
                         'permission_validations.json']
            },
            'NetworkScannerSuite': {
                'path': Path('/home/mavrick/Projects/NetworkScannerSuite/service/analytics_data'),
                'loops': ['scan_metrics.json', 'scan_errors.json',
                         'network_intelligence.json', 'resource_metrics.json']
            },
            'Template_Docs': {
                'path': Path('/home/mavrick/Projects/Template Docs/survey_system/data'),
                'loops': ['completion_tracking.json', 'accuracy_validation.json',
                         'recommendation_effectiveness.json', 'customer_journey.json',
                         'workflow_executions.json', 'workflow_feedback.json']
            }
        }

    def _ensure_log(self):
        if not self.aggregation_log.exists():
            with open(self.aggregation_log, 'w') as f:
                json.dump({
                    'runs': [],
                    'last_run': None,
                    'totals': {
                        'data_points': 0,
                        'leverage_records': 0,
                        'automation_events': 0
                    }
                }, f)

    def aggregate_all(self) -> Dict[str, Any]:
        """
        Run full aggregation from all project feedback loops

        This should be run daily or after significant activity
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'projects_processed': [],
            'metrics_collected': {},
            'errors': []
        }

        # Process each project
        for project_name, config in self.feedback_sources.items():
            try:
                project_metrics = self._process_project(project_name, config)
                results['metrics_collected'][project_name] = project_metrics
                results['projects_processed'].append(project_name)
            except Exception as e:
                results['errors'].append({
                    'project': project_name,
                    'error': str(e)
                })

        # Push aggregated metrics to strategy engine
        self._update_strategy_engine(results['metrics_collected'])

        # Log the run
        self._log_run(results)

        return results

    def _process_project(self, project_name: str, config: Dict) -> Dict[str, Any]:
        """Process feedback from a single project"""

        metrics = {
            'data_points': 0,
            'leverage_multiplier': 1.0,
            'automation_rate': 0.0,
            'exceptions_count': 0,
            'insights': []
        }

        feedback_path = config['path']

        if not feedback_path.exists():
            return metrics

        for loop_file in config['loops']:
            file_path = feedback_path / loop_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)

                    loop_metrics = self._extract_loop_metrics(
                        project_name, loop_file, data
                    )

                    # Merge metrics
                    metrics['data_points'] += loop_metrics.get('data_points', 0)
                    if loop_metrics.get('leverage_multiplier'):
                        metrics['leverage_multiplier'] = max(
                            metrics['leverage_multiplier'],
                            loop_metrics['leverage_multiplier']
                        )
                    if loop_metrics.get('automation_rate'):
                        metrics['automation_rate'] = loop_metrics['automation_rate']
                    metrics['exceptions_count'] += loop_metrics.get('exceptions', 0)

                    if loop_metrics.get('insights'):
                        metrics['insights'].extend(loop_metrics['insights'])

                except Exception as e:
                    pass  # Skip unreadable files

        return metrics

    def _extract_loop_metrics(
        self,
        project: str,
        loop_file: str,
        data: Dict
    ) -> Dict[str, Any]:
        """Extract relevant metrics from a feedback loop file"""

        metrics = {'data_points': 0, 'insights': []}

        # Assessment project
        if project == 'Assessment':
            if loop_file == 'learned_patterns.json':
                # Data Moat metrics
                metrics['data_points'] = len(data.get('finding_correlations', {}))

                industry_count = len(data.get('industry_patterns', {}))
                tech_count = len(data.get('technology_patterns', {}))
                metrics['insights'].append(f"Patterns from {industry_count} industries, {tech_count} technologies")

            elif loop_file == 'score_tracking.json':
                customers = data.get('customers', {})
                metrics['data_points'] = len(customers)

            elif loop_file == 'remediation_tracking.json':
                # Automation metrics from remediation
                completed = len(data.get('completed', []))
                active = sum(len(r) for r in data.get('active_remediations', {}).values())
                if completed + active > 0:
                    metrics['automation_rate'] = completed / (completed + active)

        # Azure Projects
        elif project == 'Azure_Projects':
            if loop_file == 'robocopy_operations.json':
                ops = data.get('operations', {})
                metrics['data_points'] = len(ops)

                benchmarks = data.get('benchmarks', {})
                if benchmarks.get('avg_speed_bytes_sec'):
                    metrics['insights'].append(
                        f"Avg robocopy speed: {benchmarks['avg_speed_bytes_sec']/1e6:.1f} MB/s"
                    )

            elif loop_file == 'disk_clone_operations.json':
                benchmarks = data.get('benchmarks', {})
                if benchmarks.get('avg_duration_minutes'):
                    metrics['insights'].append(
                        f"Avg disk clone: {benchmarks['avg_duration_minutes']:.0f} min"
                    )

        # NetworkScannerSuite
        elif project == 'NetworkScannerSuite':
            if loop_file == 'network_intelligence.json':
                # Data Moat metrics
                metrics['data_points'] = data.get('total_hosts_analyzed', 0)
                services = len(data.get('service_patterns', {}))
                vendors = len(data.get('vendor_profiles', {}))
                metrics['insights'].append(f"Network intel: {services} services, {vendors} vendors")

            elif loop_file == 'scan_metrics.json':
                scans = data.get('scans', [])
                metrics['data_points'] = len(scans)

                if scans:
                    # Calculate leverage from scan efficiency
                    successful = sum(1 for s in scans if s.get('outcome') == 'success')
                    if len(scans) > 0:
                        metrics['automation_rate'] = successful / len(scans)

            elif loop_file == 'scan_errors.json':
                errors = data.get('errors', [])
                recovery_success = data.get('recovery_success', {})
                metrics['exceptions'] = len(errors)

                # Calculate auto-recovery rate
                total_recovery = sum(r.get('attempted', 0) for r in recovery_success.values())
                successful_recovery = sum(r.get('successful', 0) for r in recovery_success.values())
                if total_recovery > 0:
                    metrics['insights'].append(
                        f"Auto-recovery rate: {successful_recovery/total_recovery:.0%}"
                    )

        # Template Docs / Survey System
        elif project == 'Template_Docs':
            if loop_file == 'workflow_executions.json':
                executions = data.get('executions', [])
                metrics['data_points'] = len(executions)

                if executions:
                    successful = sum(1 for e in executions if e.get('outcome') == 'success')
                    metrics['automation_rate'] = successful / len(executions)

            elif loop_file == 'recommendation_effectiveness.json':
                recs = data.get('recommendations', {})
                total_generated = sum(r.get('generated_count', 0) for r in recs.values())
                total_implemented = sum(r.get('implemented_count', 0) for r in recs.values())
                total_revenue = sum(r.get('total_revenue', 0) for r in recs.values())

                metrics['data_points'] = total_generated
                if total_generated > 0:
                    conversion = total_implemented / total_generated
                    metrics['insights'].append(
                        f"Recommendation conversion: {conversion:.0%}, Revenue: ${total_revenue:,.0f}"
                    )

            elif loop_file == 'customer_journey.json':
                customers = data.get('customers', {})
                metrics['data_points'] = len(customers)

                total_value = sum(c.get('total_value', 0) for c in customers.values())
                if customers:
                    metrics['insights'].append(
                        f"Customer LTV tracked: ${total_value:,.0f} across {len(customers)} customers"
                    )

        return metrics

    def _update_strategy_engine(self, metrics: Dict[str, Dict]) -> None:
        """Push aggregated metrics to the strategy engine"""

        total_data_points = 0
        total_leverage = 0
        leverage_count = 0
        total_automation_rate = 0
        automation_count = 0
        total_exceptions = 0

        for project_name, project_metrics in metrics.items():
            # Record data contribution
            data_points = project_metrics.get('data_points', 0)
            total_data_points += data_points

            if data_points > 0:
                self.engine.record_data_contribution(
                    project=project_name,
                    data_type='feedback_loop',
                    record_count=data_points
                )

            # Track leverage
            leverage = project_metrics.get('leverage_multiplier', 1.0)
            if leverage > 1.0:
                total_leverage += leverage
                leverage_count += 1

            # Track automation rate
            auto_rate = project_metrics.get('automation_rate', 0)
            if auto_rate > 0:
                total_automation_rate += auto_rate
                automation_count += 1

            # Track exceptions
            total_exceptions += project_metrics.get('exceptions_count', 0)

        # Update shift metrics

        # DATA MOAT shift
        self.engine.update_shift_metrics(AIShift.DATA_MOAT, {
            'data_points_collected': total_data_points,
            'score': min(100, total_data_points / 10)  # Scale to 100
        })

        # LEVERAGE shift
        if leverage_count > 0:
            avg_leverage = total_leverage / leverage_count
            self.engine.update_shift_metrics(AIShift.LEVERAGE, {
                'leverage_multiplier': avg_leverage,
                'score': min(100, avg_leverage * 20)  # 5x = 100%
            })

        # AUTONOMOUS shift (98/2)
        if automation_count > 0:
            avg_automation = total_automation_rate / automation_count
            exception_rate = total_exceptions / max(total_data_points, 1)
            self.engine.update_shift_metrics(AIShift.AUTONOMOUS, {
                'automations_count': automation_count,
                'exceptions_rate': exception_rate,
                'score': avg_automation * 100
            })

    def _log_run(self, results: Dict) -> None:
        """Log the aggregation run"""

        with open(self.aggregation_log, 'r') as f:
            log = json.load(f)

        run_record = {
            'timestamp': results['timestamp'],
            'projects': results['projects_processed'],
            'errors': len(results['errors']),
            'data_points_collected': sum(
                m.get('data_points', 0)
                for m in results['metrics_collected'].values()
            )
        }

        log['runs'].append(run_record)
        log['last_run'] = results['timestamp']

        # Keep last 100 runs
        if len(log['runs']) > 100:
            log['runs'] = log['runs'][-100:]

        # Update totals
        log['totals']['data_points'] += run_record['data_points_collected']

        with open(self.aggregation_log, 'w') as f:
            json.dump(log, f, indent=2)

    def get_aggregation_status(self) -> Dict[str, Any]:
        """Get status of the aggregation system"""

        with open(self.aggregation_log, 'r') as f:
            log = json.load(f)

        status = {
            'total_runs': len(log['runs']),
            'last_run': log['last_run'],
            'totals': log['totals'],
            'source_status': {}
        }

        # Check each feedback source
        for project_name, config in self.feedback_sources.items():
            path = config['path']
            status['source_status'][project_name] = {
                'path_exists': path.exists(),
                'files_found': []
            }

            if path.exists():
                for loop_file in config['loops']:
                    if (path / loop_file).exists():
                        status['source_status'][project_name]['files_found'].append(loop_file)

        return status


def run_aggregation() -> Dict[str, Any]:
    """Convenience function to run aggregation"""
    aggregator = FeedbackAggregator()
    return aggregator.aggregate_all()


def get_status() -> Dict[str, Any]:
    """Convenience function to check aggregation status"""
    aggregator = FeedbackAggregator()
    return aggregator.get_aggregation_status()


if __name__ == "__main__":
    # Run aggregation when executed directly
    print("Running feedback aggregation...")
    results = run_aggregation()

    print(f"\nProcessed {len(results['projects_processed'])} projects:")
    for project in results['projects_processed']:
        metrics = results['metrics_collected'].get(project, {})
        print(f"  - {project}: {metrics.get('data_points', 0)} data points")
        for insight in metrics.get('insights', []):
            print(f"      {insight}")

    if results['errors']:
        print(f"\nErrors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error['project']}: {error['error']}")
