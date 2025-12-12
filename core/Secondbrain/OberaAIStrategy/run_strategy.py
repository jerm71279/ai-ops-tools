#!/usr/bin/env python3
"""
OberaAI Strategy Runner
Run aggregation and view dashboard from command line

Usage:
    python run_strategy.py              # Run aggregation + show dashboard
    python run_strategy.py --status     # Just show status
    python run_strategy.py --dashboard  # Just show dashboard
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from OberaAIStrategy import run_aggregation, get_aggregation_status, get_dashboard


def show_dashboard():
    """Display the strategy dashboard"""
    dashboard = get_dashboard()

    print("\n" + "="*60)
    print("OBERA AI STRATEGY DASHBOARD")
    print("="*60)
    print(f"Generated: {dashboard['generated_at']}")
    print(f"Overall Score: {dashboard['overall_score']:.0f}%")
    print(f"Current Phase: {dashboard['current_phase'].upper()}")

    print("\n--- Five AI Shifts ---")
    for shift_id, shift in dashboard['shifts'].items():
        bar = "█" * int(shift['score'] / 10) + "░" * (10 - int(shift['score'] / 10))
        print(f"  {shift['name']:<25} [{bar}] {shift['score']:>3}% ({shift['maturity']})")

    print("\n--- Projects ---")
    proj = dashboard['projects']
    print(f"  Registered: {proj['count']}")
    print(f"  Total Automations: {proj['total_automations']}")
    print(f"  Average Leverage: {proj['average_leverage']:.1f}x")
    print(f"  Data Moat Size: {proj['data_moat_size']} records")

    if dashboard.get('recommendations'):
        print("\n--- Top Recommendations ---")
        for rec in dashboard['recommendations'][:3]:
            print(f"  [{rec['priority'].upper()}] {rec['recommendation']}")

    print()


def show_status():
    """Display aggregation system status"""
    status = get_aggregation_status()

    print("\n" + "="*60)
    print("FEEDBACK AGGREGATION STATUS")
    print("="*60)
    print(f"Total Runs: {status['total_runs']}")
    print(f"Last Run: {status['last_run'] or 'Never'}")
    print(f"Total Data Points: {status['totals']['data_points']}")

    print("\n--- Source Status ---")
    for project, info in status['source_status'].items():
        icon = "✓" if info['path_exists'] else "✗"
        files = len(info['files_found'])
        print(f"  {icon} {project}: {files} feedback files")

    print()


def run_and_report():
    """Run aggregation and show results"""
    print("\nRunning feedback aggregation...")
    results = run_aggregation()

    print(f"\n--- Aggregation Results ---")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Projects: {', '.join(results['projects_processed'])}")

    total_points = 0
    for project, metrics in results['metrics_collected'].items():
        points = metrics.get('data_points', 0)
        total_points += points
        auto_rate = metrics.get('automation_rate', 0)
        print(f"  {project}: {points} data points, {auto_rate:.0%} automation")
        for insight in metrics.get('insights', []):
            print(f"    → {insight}")

    print(f"\nTotal data points collected: {total_points}")

    if results['errors']:
        print(f"\nErrors ({len(results['errors'])}):")
        for err in results['errors']:
            print(f"  ✗ {err['project']}: {err['error']}")


def main():
    parser = argparse.ArgumentParser(description="OberaAI Strategy Runner")
    parser.add_argument('--status', action='store_true', help='Show aggregation status only')
    parser.add_argument('--dashboard', action='store_true', help='Show dashboard only')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    if args.json:
        if args.status:
            print(json.dumps(get_aggregation_status(), indent=2, default=str))
        elif args.dashboard:
            print(json.dumps(get_dashboard(), indent=2, default=str))
        else:
            results = run_aggregation()
            print(json.dumps(results, indent=2, default=str))
        return

    if args.status:
        show_status()
    elif args.dashboard:
        show_dashboard()
    else:
        # Default: run aggregation and show dashboard
        run_and_report()
        show_dashboard()


if __name__ == "__main__":
    main()
