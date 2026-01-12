"""
Business Analytics (BA) Agent
Autonomous business intelligence agent for OberaConnect Engineering Command Center

Integrates with:
- SharePoint Lists (Projects, Tasks, Tickets, TimeEntries)
- Gemini for natural language analysis
- MoE Router for intelligent task delegation
"""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

# Gemini integration
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Gemini features disabled.")


class AnalysisType(Enum):
    """Types of business analysis the BA Agent can perform"""
    PROJECT_HEALTH = "project_health"
    RESOURCE_UTILIZATION = "resource_utilization"
    TIME_ANALYSIS = "time_analysis"
    BUDGET_TRACKING = "budget_tracking"
    SLA_COMPLIANCE = "sla_compliance"
    CAPACITY_PLANNING = "capacity_planning"
    TREND_ANALYSIS = "trend_analysis"
    QUOTE_GENERATION = "quote_generation"


@dataclass
class AnalysisResult:
    """Result of a business analysis"""
    analysis_type: str
    timestamp: str
    data: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    confidence: float
    generated_by: str = "BA_Agent"


class BAAgent:
    """
    Business Analytics Agent

    Responsibilities:
    - Analyze project performance metrics
    - Generate executive summaries
    - Identify trends and anomalies
    - Forecast project completion dates
    - Budget vs actual analysis
    - Resource utilization optimization
    - Capacity planning recommendations
    - SLA compliance monitoring
    - Time-based quoting for work
    """

    def __init__(self, gemini_api_key: str = None):
        self.agent_id = "agent_ba"
        self.status = "ready"
        self.last_active = None
        self.analysis_history = []

        # Employee billable rates (will be loaded from SharePoint)
        self.billable_rates = {
            'Mavrick Faison': 150,
            'Patrick McFarland': 135,
            'Robbie McFarland': 200,
            'Default': 125
        }

        # Initialize Gemini
        self.gemini_model = None
        if GEMINI_AVAILABLE:
            api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                print("Gemini integration enabled for BA Agent")

        # Data cache
        self._projects_cache = []
        self._tasks_cache = []
        self._tickets_cache = []
        self._time_entries_cache = []
        self._cache_timestamp = None

        # Output directory for reports
        self.reports_dir = Path("./ba_reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Auto-load data from file if exists
        self.load_data_from_file()

    def load_data_from_file(self, filepath: str = None):
        """Load data from JSON file"""
        if filepath is None:
            filepath = Path("./data/ba_agent_data.json")
        else:
            filepath = Path(filepath)

        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                self.set_data(
                    projects=data.get('projects', []),
                    tasks=data.get('tasks', []),
                    tickets=data.get('tickets', []),
                    time_entries=data.get('time_entries', [])
                )
                print(f"Loaded data from {filepath}")
                print(f"  Projects: {len(self._projects_cache)}")
                print(f"  Tasks: {len(self._tasks_cache)}")
                print(f"  Tickets: {len(self._tickets_cache)}")
                print(f"  Time Entries: {len(self._time_entries_cache)}")
            except Exception as e:
                print(f"Error loading data file: {e}")

    def set_data(
        self,
        projects: List[Dict] = None,
        tasks: List[Dict] = None,
        tickets: List[Dict] = None,
        time_entries: List[Dict] = None
    ):
        """Set data from SharePoint for analysis"""
        if projects is not None:
            self._projects_cache = projects
        if tasks is not None:
            self._tasks_cache = tasks
        if tickets is not None:
            self._tickets_cache = tickets
        if time_entries is not None:
            self._time_entries_cache = time_entries
        self._cache_timestamp = datetime.now().isoformat()

    # ========================================================================
    # CORE ANALYSIS METHODS
    # ========================================================================

    def analyze_project_health(self, project_id: str = None) -> AnalysisResult:
        """
        Analyze health of projects

        Metrics:
        - Schedule variance (planned vs actual)
        - Budget variance (budget hours vs spent)
        - Task completion rate
        - Overdue items
        - Risk indicators
        """
        self.last_active = datetime.now().isoformat()

        projects = self._projects_cache
        if project_id:
            projects = [p for p in projects if str(p.get('id')) == str(project_id)]

        health_data = []
        insights = []
        recommendations = []

        for project in projects:
            fields = project.get('fields', project)
            project_name = fields.get('ProjectName', fields.get('Title', 'Unknown'))

            # Get related tasks
            project_tasks = [
                t for t in self._tasks_cache
                if str(t.get('fields', t).get('ProjectId')) == str(project.get('id'))
            ]

            # Calculate metrics
            total_tasks = len(project_tasks)
            completed_tasks = len([t for t in project_tasks if t.get('fields', t).get('Status') == 'Completed'])
            overdue_tasks = len([
                t for t in project_tasks
                if t.get('fields', t).get('DueDate') and
                   datetime.fromisoformat(t.get('fields', t).get('DueDate').split('T')[0]) < datetime.now() and
                   t.get('fields', t).get('Status') != 'Completed'
            ])

            budget_hours = float(fields.get('BudgetHours', 0) or 0)
            hours_spent = float(fields.get('HoursSpent', 0) or 0)
            percent_complete = float(fields.get('PercentComplete', 0) or 0)

            # Calculate health score (0-100)
            health_score = 100
            risk_factors = []

            # Budget variance check
            if budget_hours > 0:
                budget_used_pct = (hours_spent / budget_hours) * 100
                if budget_used_pct > percent_complete + 20:
                    health_score -= 20
                    risk_factors.append(f"Budget overrun risk: {budget_used_pct:.0f}% budget used at {percent_complete:.0f}% complete")

            # Overdue tasks check
            if total_tasks > 0:
                overdue_pct = (overdue_tasks / total_tasks) * 100
                if overdue_pct > 30:
                    health_score -= 25
                    risk_factors.append(f"{overdue_pct:.0f}% of tasks overdue")
                elif overdue_pct > 10:
                    health_score -= 10
                    risk_factors.append(f"{overdue_pct:.0f}% of tasks overdue")

            # Progress check
            if fields.get('DueDate'):
                due_date = datetime.fromisoformat(fields.get('DueDate').split('T')[0])
                days_remaining = (due_date - datetime.now()).days
                if days_remaining < 0:
                    health_score -= 30
                    risk_factors.append(f"Project overdue by {abs(days_remaining)} days")
                elif days_remaining < 7 and percent_complete < 80:
                    health_score -= 15
                    risk_factors.append(f"Only {days_remaining} days remaining, {percent_complete:.0f}% complete")

            # Status categorization
            if health_score >= 80:
                status = "Healthy"
            elif health_score >= 60:
                status = "At Risk"
            else:
                status = "Critical"

            health_data.append({
                'project_id': project.get('id'),
                'project_name': project_name,
                'health_score': max(0, health_score),
                'status': status,
                'percent_complete': percent_complete,
                'budget_hours': budget_hours,
                'hours_spent': hours_spent,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'overdue_tasks': overdue_tasks,
                'risk_factors': risk_factors
            })

            # Generate insights
            if status == "Critical":
                insights.append(f"CRITICAL: {project_name} requires immediate attention")
            elif status == "At Risk":
                insights.append(f"WARNING: {project_name} has risk factors to address")

        # Generate recommendations
        critical_projects = [p for p in health_data if p['status'] == 'Critical']
        if critical_projects:
            recommendations.append(f"Prioritize review of {len(critical_projects)} critical projects")
            for p in critical_projects[:3]:
                if p['overdue_tasks'] > 0:
                    recommendations.append(f"{p['project_name']}: Address {p['overdue_tasks']} overdue tasks")

        return AnalysisResult(
            analysis_type=AnalysisType.PROJECT_HEALTH.value,
            timestamp=datetime.now().isoformat(),
            data={'projects': health_data},
            insights=insights,
            recommendations=recommendations,
            confidence=0.85
        )

    def analyze_resource_utilization(self, date_range_days: int = 30) -> AnalysisResult:
        """
        Analyze team resource utilization

        Metrics:
        - Hours worked per employee
        - Billable vs non-billable ratio
        - Capacity utilization %
        - Workload distribution
        """
        self.last_active = datetime.now().isoformat()

        cutoff_date = datetime.now() - timedelta(days=date_range_days)

        # Filter time entries by date range
        recent_entries = []
        for entry in self._time_entries_cache:
            entry_date_str = entry.get('date', entry.get('fields', {}).get('EntryDate', ''))
            if entry_date_str:
                try:
                    entry_date = datetime.fromisoformat(entry_date_str.split('T')[0])
                    if entry_date >= cutoff_date:
                        recent_entries.append(entry)
                except ValueError:
                    continue

        # Aggregate by employee
        employee_stats = {}
        for entry in recent_entries:
            employee = entry.get('employee', entry.get('fields', {}).get('Employee', 'Unknown'))
            hours = float(entry.get('hours', entry.get('fields', {}).get('Hours', 0)) or 0)
            billable = entry.get('billable', entry.get('fields', {}).get('Billable', False))

            if employee not in employee_stats:
                employee_stats[employee] = {
                    'total_hours': 0,
                    'billable_hours': 0,
                    'non_billable_hours': 0,
                    'entries': 0,
                    'projects': set()
                }

            employee_stats[employee]['total_hours'] += hours
            if billable:
                employee_stats[employee]['billable_hours'] += hours
            else:
                employee_stats[employee]['non_billable_hours'] += hours
            employee_stats[employee]['entries'] += 1

            project_name = entry.get('projectName', entry.get('fields', {}).get('ProjectName', ''))
            if project_name:
                employee_stats[employee]['projects'].add(project_name)

        # Calculate utilization metrics
        utilization_data = []
        expected_hours = date_range_days * 8 * (5/7)  # 8 hours/day, 5 days/week

        insights = []
        recommendations = []

        for employee, stats in employee_stats.items():
            utilization_pct = (stats['total_hours'] / expected_hours) * 100 if expected_hours > 0 else 0
            billable_pct = (stats['billable_hours'] / stats['total_hours']) * 100 if stats['total_hours'] > 0 else 0

            rate = self.billable_rates.get(employee, self.billable_rates['Default'])
            billable_value = stats['billable_hours'] * rate

            utilization_data.append({
                'employee': employee,
                'total_hours': round(stats['total_hours'], 1),
                'billable_hours': round(stats['billable_hours'], 1),
                'non_billable_hours': round(stats['non_billable_hours'], 1),
                'utilization_pct': round(utilization_pct, 1),
                'billable_pct': round(billable_pct, 1),
                'billable_value': round(billable_value, 2),
                'hourly_rate': rate,
                'project_count': len(stats['projects']),
                'time_entries': stats['entries']
            })

            # Generate insights
            if utilization_pct > 100:
                insights.append(f"{employee} is over capacity at {utilization_pct:.0f}% utilization")
            elif utilization_pct < 60:
                insights.append(f"{employee} has available capacity ({100-utilization_pct:.0f}% available)")

            if billable_pct < 70 and stats['total_hours'] > 20:
                recommendations.append(f"Review {employee}'s non-billable work ({100-billable_pct:.0f}% of time)")

        # Team summary
        total_billable = sum(e['billable_value'] for e in utilization_data)
        total_hours = sum(e['total_hours'] for e in utilization_data)
        avg_utilization = sum(e['utilization_pct'] for e in utilization_data) / len(utilization_data) if utilization_data else 0

        return AnalysisResult(
            analysis_type=AnalysisType.RESOURCE_UTILIZATION.value,
            timestamp=datetime.now().isoformat(),
            data={
                'employees': utilization_data,
                'summary': {
                    'total_billable_value': round(total_billable, 2),
                    'total_hours_logged': round(total_hours, 1),
                    'average_utilization': round(avg_utilization, 1),
                    'date_range_days': date_range_days
                }
            },
            insights=insights,
            recommendations=recommendations,
            confidence=0.90
        )

    def generate_quote(
        self,
        task_description: str,
        complexity: str = "medium",  # low, medium, high, complex
        include_buffer: bool = True
    ) -> AnalysisResult:
        """
        Generate a time/cost quote for work

        Uses historical data and complexity factors to estimate
        """
        self.last_active = datetime.now().isoformat()

        # Complexity multipliers
        complexity_hours = {
            'low': {'min': 1, 'typical': 2, 'max': 4},
            'medium': {'min': 4, 'typical': 8, 'max': 16},
            'high': {'min': 8, 'typical': 24, 'max': 40},
            'complex': {'min': 24, 'typical': 40, 'max': 80}
        }

        base_hours = complexity_hours.get(complexity, complexity_hours['medium'])

        # Add buffer if requested (15%)
        buffer_multiplier = 1.15 if include_buffer else 1.0

        estimated_hours = {
            'min': round(base_hours['min'] * buffer_multiplier, 1),
            'typical': round(base_hours['typical'] * buffer_multiplier, 1),
            'max': round(base_hours['max'] * buffer_multiplier, 1)
        }

        # Calculate costs at different rates
        avg_rate = sum(self.billable_rates.values()) / len(self.billable_rates)

        cost_estimates = {
            'min': round(estimated_hours['min'] * avg_rate, 2),
            'typical': round(estimated_hours['typical'] * avg_rate, 2),
            'max': round(estimated_hours['max'] * avg_rate, 2)
        }

        # Use Gemini for more detailed analysis if available
        ai_analysis = None
        if self.gemini_model and task_description:
            try:
                prompt = f"""
                Analyze this task for time estimation:
                Task: {task_description}
                Complexity: {complexity}

                Provide:
                1. Key work items involved
                2. Potential risks or unknowns
                3. Suggested approach

                Keep response concise (3-5 bullet points max).
                """
                response = self.gemini_model.generate_content(prompt)
                ai_analysis = response.text
            except Exception as e:
                ai_analysis = f"AI analysis unavailable: {str(e)}"

        quote_data = {
            'task_description': task_description,
            'complexity': complexity,
            'estimated_hours': estimated_hours,
            'cost_estimates': cost_estimates,
            'average_hourly_rate': round(avg_rate, 2),
            'buffer_included': include_buffer,
            'ai_analysis': ai_analysis
        }

        return AnalysisResult(
            analysis_type=AnalysisType.QUOTE_GENERATION.value,
            timestamp=datetime.now().isoformat(),
            data=quote_data,
            insights=[
                f"Estimated {estimated_hours['typical']} hours for typical scenario",
                f"Cost range: ${cost_estimates['min']:,.2f} - ${cost_estimates['max']:,.2f}"
            ],
            recommendations=[
                "Review estimate with technical lead before quoting",
                "Document assumptions and exclusions"
            ],
            confidence=0.75
        )

    def analyze_time_reports(
        self,
        group_by: str = "project",  # project, employee, date, task
        date_range_days: int = 30
    ) -> AnalysisResult:
        """
        Analyze time entries for reporting

        Generates summaries for quoting and billing
        """
        self.last_active = datetime.now().isoformat()

        cutoff_date = datetime.now() - timedelta(days=date_range_days)

        # Filter recent entries
        recent_entries = []
        for entry in self._time_entries_cache:
            entry_date_str = entry.get('date', entry.get('fields', {}).get('EntryDate', ''))
            if entry_date_str:
                try:
                    entry_date = datetime.fromisoformat(entry_date_str.split('T')[0])
                    if entry_date >= cutoff_date:
                        recent_entries.append(entry)
                except ValueError:
                    continue

        # Group data
        grouped_data = {}

        for entry in recent_entries:
            fields = entry.get('fields', entry)

            # Determine group key
            if group_by == "project":
                key = fields.get('ProjectName', 'Unassigned')
            elif group_by == "employee":
                key = fields.get('Employee', entry.get('employee', 'Unknown'))
            elif group_by == "date":
                key = (entry.get('date', fields.get('EntryDate', ''))[:10])
            else:
                key = fields.get('TaskName', entry.get('taskName', 'General'))

            hours = float(entry.get('hours', fields.get('Hours', 0)) or 0)
            billable = entry.get('billable', fields.get('Billable', False))
            employee = fields.get('Employee', entry.get('employee', 'Unknown'))
            rate = self.billable_rates.get(employee, self.billable_rates['Default'])

            if key not in grouped_data:
                grouped_data[key] = {
                    'total_hours': 0,
                    'billable_hours': 0,
                    'billable_amount': 0,
                    'entries': 0,
                    'employees': set()
                }

            grouped_data[key]['total_hours'] += hours
            if billable:
                grouped_data[key]['billable_hours'] += hours
                grouped_data[key]['billable_amount'] += hours * rate
            grouped_data[key]['entries'] += 1
            grouped_data[key]['employees'].add(employee)

        # Format for output
        report_data = []
        for key, stats in grouped_data.items():
            report_data.append({
                'group': key,
                'total_hours': round(stats['total_hours'], 1),
                'billable_hours': round(stats['billable_hours'], 1),
                'billable_amount': round(stats['billable_amount'], 2),
                'entry_count': stats['entries'],
                'team_members': len(stats['employees'])
            })

        # Sort by total hours descending
        report_data.sort(key=lambda x: x['total_hours'], reverse=True)

        # Summary
        total_hours = sum(r['total_hours'] for r in report_data)
        total_billable = sum(r['billable_amount'] for r in report_data)

        insights = [
            f"Total {total_hours:.1f} hours logged in last {date_range_days} days",
            f"Total billable value: ${total_billable:,.2f}"
        ]

        if report_data:
            top_item = report_data[0]
            insights.append(f"Highest time consumer: {top_item['group']} ({top_item['total_hours']:.1f}h)")

        return AnalysisResult(
            analysis_type=AnalysisType.TIME_ANALYSIS.value,
            timestamp=datetime.now().isoformat(),
            data={
                'grouped_by': group_by,
                'date_range_days': date_range_days,
                'items': report_data,
                'summary': {
                    'total_hours': round(total_hours, 1),
                    'total_billable_amount': round(total_billable, 2),
                    'item_count': len(report_data)
                }
            },
            insights=insights,
            recommendations=[
                "Export to Excel for detailed client invoicing",
                "Review non-billable time for optimization opportunities"
            ],
            confidence=0.95
        )

    def generate_executive_summary(self) -> AnalysisResult:
        """
        Generate executive summary combining all analyses

        Perfect for weekly/monthly reporting
        """
        self.last_active = datetime.now().isoformat()

        # Run sub-analyses
        project_health = self.analyze_project_health()
        utilization = self.analyze_resource_utilization(date_range_days=7)
        time_report = self.analyze_time_reports(group_by="project", date_range_days=7)

        # Aggregate data
        projects_summary = project_health.data.get('projects', [])
        healthy_count = len([p for p in projects_summary if p['status'] == 'Healthy'])
        at_risk_count = len([p for p in projects_summary if p['status'] == 'At Risk'])
        critical_count = len([p for p in projects_summary if p['status'] == 'Critical'])

        utilization_summary = utilization.data.get('summary', {})
        time_summary = time_report.data.get('summary', {})

        executive_data = {
            'period': f"{datetime.now().strftime('%Y-%m-%d')} (Last 7 days)",
            'projects': {
                'total': len(projects_summary),
                'healthy': healthy_count,
                'at_risk': at_risk_count,
                'critical': critical_count
            },
            'team': {
                'total_hours': utilization_summary.get('total_hours_logged', 0),
                'avg_utilization': utilization_summary.get('average_utilization', 0),
                'total_billable_value': time_summary.get('total_billable_amount', 0)
            },
            'top_projects_by_time': time_report.data.get('items', [])[:5],
            'team_utilization': utilization.data.get('employees', [])
        }

        # Combine insights
        all_insights = (
            project_health.insights[:3] +
            utilization.insights[:2] +
            time_report.insights[:2]
        )

        all_recommendations = (
            project_health.recommendations[:2] +
            utilization.recommendations[:2]
        )

        # Use Gemini for narrative summary if available
        narrative = None
        if self.gemini_model:
            try:
                prompt = f"""
                Generate a brief executive summary (2-3 paragraphs) based on:
                - {len(projects_summary)} total projects: {healthy_count} healthy, {at_risk_count} at risk, {critical_count} critical
                - Team logged {utilization_summary.get('total_hours_logged', 0):.0f} hours
                - Average utilization: {utilization_summary.get('average_utilization', 0):.0f}%
                - Total billable value: ${time_summary.get('total_billable_amount', 0):,.0f}

                Focus on key takeaways for leadership.
                """
                response = self.gemini_model.generate_content(prompt)
                narrative = response.text
            except Exception as e:
                narrative = None

        executive_data['narrative_summary'] = narrative

        return AnalysisResult(
            analysis_type="executive_summary",
            timestamp=datetime.now().isoformat(),
            data=executive_data,
            insights=all_insights,
            recommendations=all_recommendations,
            confidence=0.85
        )

    # ========================================================================
    # NATURAL LANGUAGE QUERY (GEMINI)
    # ========================================================================

    async def query(self, question: str, context: Dict = None) -> Dict[str, Any]:
        """
        Answer natural language questions about the data
        Uses Gemini for intelligent responses
        """
        self.last_active = datetime.now().isoformat()

        if not self.gemini_model:
            return {
                "success": False,
                "error": "Gemini not available. Set GEMINI_API_KEY environment variable.",
                "answer": None
            }

        # Build context from cached data
        data_context = f"""
        Current Data Summary:
        - Projects: {len(self._projects_cache)} total
        - Tasks: {len(self._tasks_cache)} total
        - Tickets: {len(self._tickets_cache)} total
        - Time Entries: {len(self._time_entries_cache)} total

        Sample Project Names: {[p.get('fields', p).get('ProjectName', p.get('Title', ''))[:30] for p in self._projects_cache[:5]]}

        Employee Billable Rates: {json.dumps(self.billable_rates)}
        """

        if context:
            data_context += f"\nAdditional Context: {json.dumps(context)}"

        prompt = f"""
        You are a Business Analytics Agent for an Engineering Command Center.

        {data_context}

        User Question: {question}

        Provide a helpful, data-driven answer. If you need specific data that isn't available,
        explain what additional information would be needed.
        """

        try:
            response = self.gemini_model.generate_content(prompt)
            return {
                "success": True,
                "question": question,
                "answer": response.text,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": None
            }

    # ========================================================================
    # EXPORT & REPORTING
    # ========================================================================

    def export_report(self, analysis_result: AnalysisResult, format: str = "json") -> str:
        """Export analysis result to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{analysis_result.analysis_type}_{timestamp}.{format}"
        filepath = self.reports_dir / filename

        if format == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(analysis_result), f, indent=2, default=str)
        else:
            # Could add CSV, Excel support here
            raise ValueError(f"Unsupported format: {format}")

        return str(filepath)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "last_active": self.last_active,
            "gemini_available": self.gemini_model is not None,
            "data_cached": {
                "projects": len(self._projects_cache),
                "tasks": len(self._tasks_cache),
                "tickets": len(self._tickets_cache),
                "time_entries": len(self._time_entries_cache)
            },
            "cache_timestamp": self._cache_timestamp
        }


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """CLI entry point for BA Agent"""
    import argparse

    parser = argparse.ArgumentParser(description="Business Analytics Agent")
    parser.add_argument("--task", type=str, help="Task to perform")
    parser.add_argument("--project-id", type=str, help="Project ID for analysis")
    parser.add_argument("--days", type=int, default=30, help="Date range in days")
    parser.add_argument("--output", type=str, default="json", help="Output format")

    args = parser.parse_args()

    agent = BAAgent()

    print("=" * 60)
    print("Business Analytics Agent")
    print("=" * 60)
    print(f"\nStatus: {json.dumps(agent.get_status(), indent=2)}")

    if args.task == "project_health":
        result = agent.analyze_project_health(args.project_id)
        print(f"\nProject Health Analysis:")
        print(json.dumps(asdict(result), indent=2, default=str))

    elif args.task == "utilization":
        result = agent.analyze_resource_utilization(args.days)
        print(f"\nResource Utilization Analysis:")
        print(json.dumps(asdict(result), indent=2, default=str))

    elif args.task == "time_report":
        result = agent.analyze_time_reports(date_range_days=args.days)
        print(f"\nTime Report Analysis:")
        print(json.dumps(asdict(result), indent=2, default=str))

    elif args.task == "executive":
        result = agent.generate_executive_summary()
        print(f"\nExecutive Summary:")
        print(json.dumps(asdict(result), indent=2, default=str))

    elif args.task == "quote":
        # Example quote generation
        result = agent.generate_quote(
            task_description="Implement user authentication with Azure AD",
            complexity="high"
        )
        print(f"\nQuote Generation:")
        print(json.dumps(asdict(result), indent=2, default=str))

    else:
        print("\nAvailable tasks:")
        print("  --task project_health   Analyze project health")
        print("  --task utilization      Analyze resource utilization")
        print("  --task time_report      Generate time reports")
        print("  --task executive        Generate executive summary")
        print("  --task quote            Generate work quote")


if __name__ == "__main__":
    main()
