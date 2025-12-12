"""
OberaConnect AI Strategy - Project Registry
Maps all projects to their AI transformation implementations

This registry connects the feedback loops from each project
to the central OberaAI Strategy for unified tracking.
"""

from typing import Dict, List, Any
from pathlib import Path
from ..core.strategy_engine import OberaAIStrategyEngine, AIShift


# Project definitions with their AI integrations
PROJECT_REGISTRY = {
    'Assessment': {
        'path': '/home/mavrick/Projects/Assessment',
        'description': 'Security and compliance assessment framework',
        'shifts': [
            AIShift.DATA_MOAT,      # Pattern learning from assessments
            AIShift.DIRECTOR,        # AI analyzes, human reviews
            AIShift.AUTONOMOUS,      # 98% auto-analysis, 2% exceptions
            AIShift.LEVERAGE         # One engineer can assess many customers
        ],
        'feedback_loops': [
            'score_tracking',
            'remediation_tracking',
            'pattern_learning',
            'benchmark_comparison'
        ],
        'data_contributions': [
            'assessment_patterns',
            'finding_correlations',
            'industry_benchmarks',
            'remediation_success_rates'
        ],
        'key_metrics': [
            'assessments_completed',
            'patterns_identified',
            'remediation_completion_rate'
        ]
    },

    'Azure_Projects': {
        'path': '/home/mavrick/Projects/Azure_Projects',
        'description': 'Azure migration and operations monitoring',
        'shifts': [
            AIShift.AUTONOMOUS,      # 98% automated verification
            AIShift.LEVERAGE,        # Automated monitoring multiplies engineer capacity
            AIShift.DATA_MOAT        # Performance benchmarks from migrations
        ],
        'feedback_loops': [
            'robocopy_verification',
            'disk_clone_monitoring',
            'permission_validation',
            'performance_benchmarking'
        ],
        'data_contributions': [
            'migration_performance_data',
            'error_patterns',
            'duration_benchmarks'
        ],
        'key_metrics': [
            'migrations_completed',
            'success_rate',
            'avg_migration_time'
        ]
    },

    'NetworkScannerSuite': {
        'path': '/home/mavrick/Projects/NetworkScannerSuite',
        'description': 'Network discovery and scanning service',
        'shifts': [
            AIShift.DATA_MOAT,       # Network intelligence database
            AIShift.LEVERAGE,        # Automated scanning multiplies capacity
            AIShift.AUTONOMOUS       # Auto-retry failed scans
        ],
        'feedback_loops': [
            'scan_performance',
            'error_recovery',
            'network_intelligence',
            'resource_monitoring'
        ],
        'data_contributions': [
            'device_patterns',
            'service_patterns',
            'vendor_profiles',
            'security_indicators'
        ],
        'key_metrics': [
            'scans_completed',
            'hosts_analyzed',
            'intelligence_records'
        ]
    },

    'Template_Docs': {
        'path': '/home/mavrick/Projects/Template Docs',
        'description': 'Site survey workflow system',
        'shifts': [
            AIShift.DIRECTOR,        # AI generates recommendations, human reviews
            AIShift.DATA_MOAT,       # Customer intelligence database
            AIShift.DISTRIBUTION,    # Survey captures leads, drives sales
            AIShift.LEVERAGE         # Automated recommendations multiply sales capacity
        ],
        'feedback_loops': [
            'completion_tracking',
            'accuracy_validation',
            'recommendation_effectiveness',
            'customer_journey'
        ],
        'data_contributions': [
            'customer_profiles',
            'recommendation_outcomes',
            'service_adoption_patterns'
        ],
        'key_metrics': [
            'surveys_completed',
            'recommendations_generated',
            'conversion_rate'
        ]
    },

    'Secondbrain': {
        'path': '/home/mavrick/Projects/Secondbrain',
        'description': 'Knowledge management and AI orchestration',
        'shifts': [
            AIShift.DATA_MOAT,       # Central knowledge repository
            AIShift.DIRECTOR,        # Two-agent orchestration
            AIShift.LEVERAGE         # AI-powered knowledge synthesis
        ],
        'feedback_loops': [
            'agent_orchestration',
            'knowledge_consistency',
            'pattern_detection'
        ],
        'data_contributions': [
            'documentation_patterns',
            'knowledge_relationships',
            'improvement_history'
        ],
        'key_metrics': [
            'documents_processed',
            'patterns_identified',
            'consistency_score'
        ]
    },

    'skills_SIEM': {
        'path': '/home/mavrick/Projects/skills/SEIM-skills',
        'description': 'SIEM security automation and SOAR playbooks',
        'shifts': [
            AIShift.AUTONOMOUS,      # Automated alert response
            AIShift.LEVERAGE,        # SOC capacity multiplication
            AIShift.DATA_MOAT        # Threat intelligence
        ],
        'feedback_loops': [
            'alert_response',
            'playbook_effectiveness',
            'threat_patterns'
        ],
        'data_contributions': [
            'alert_patterns',
            'response_outcomes',
            'threat_indicators'
        ],
        'key_metrics': [
            'alerts_processed',
            'auto_remediation_rate',
            'response_time'
        ]
    },

    'network_troubleshooting_tool': {
        'path': '/home/mavrick/Projects/network-troubleshooting-tool',
        'description': 'Network assessment and troubleshooting',
        'shifts': [
            AIShift.LEVERAGE,        # Automated assessment
            AIShift.AUTONOMOUS       # Step-by-step automation
        ],
        'feedback_loops': [
            'assessment_feedback',
            'workflow_recording'
        ],
        'data_contributions': [
            'network_baselines',
            'troubleshooting_patterns'
        ],
        'key_metrics': [
            'assessments_run',
            'issues_identified'
        ]
    },

    'Nmap_Project': {
        'path': '/home/mavrick/Projects/Nmap_Project',
        'description': 'Network scanning and configuration',
        'shifts': [
            AIShift.LEVERAGE,        # Scan automation
            AIShift.DATA_MOAT        # Scan history
        ],
        'feedback_loops': [
            'scan_history',
            'discovery_to_config'
        ],
        'data_contributions': [
            'scan_results',
            'network_configurations'
        ],
        'key_metrics': [
            'scans_completed',
            'configs_generated'
        ]
    }
}


def register_all_projects(engine: OberaAIStrategyEngine = None) -> Dict[str, bool]:
    """Register all projects with the strategy engine"""

    if engine is None:
        engine = OberaAIStrategyEngine()

    results = {}

    for project_name, config in PROJECT_REGISTRY.items():
        try:
            engine.register_project(
                project_name=project_name,
                project_path=config['path'],
                shifts=config['shifts'],
                feedback_loops=config['feedback_loops'],
                data_contributions=config['data_contributions']
            )
            results[project_name] = True
        except Exception as e:
            results[project_name] = False

    return results


def get_project_config(project_name: str) -> Dict:
    """Get configuration for a specific project"""
    return PROJECT_REGISTRY.get(project_name)


def get_projects_by_shift(shift: AIShift) -> List[str]:
    """Get all projects implementing a specific shift"""
    return [
        name for name, config in PROJECT_REGISTRY.items()
        if shift in config['shifts']
    ]


def get_all_feedback_loops() -> Dict[str, List[str]]:
    """Get all feedback loops across all projects"""
    loops = {}
    for project_name, config in PROJECT_REGISTRY.items():
        loops[project_name] = config['feedback_loops']
    return loops


def get_data_moat_summary() -> Dict[str, Any]:
    """Get summary of data moat contributions"""
    summary = {
        'total_data_types': 0,
        'by_project': {}
    }

    for project_name, config in PROJECT_REGISTRY.items():
        contributions = config['data_contributions']
        summary['by_project'][project_name] = {
            'contributions': contributions,
            'count': len(contributions)
        }
        summary['total_data_types'] += len(contributions)

    return summary


def get_shift_coverage() -> Dict[str, Dict]:
    """Get coverage of each shift across projects"""
    coverage = {
        shift.value: {
            'projects': [],
            'coverage_percentage': 0
        }
        for shift in AIShift
    }

    total_projects = len(PROJECT_REGISTRY)

    for project_name, config in PROJECT_REGISTRY.items():
        for shift in config['shifts']:
            coverage[shift.value]['projects'].append(project_name)

    for shift_value, data in coverage.items():
        data['coverage_percentage'] = len(data['projects']) / total_projects * 100

    return coverage
