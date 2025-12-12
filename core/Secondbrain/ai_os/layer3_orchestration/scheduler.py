"""
Layer 3: Workflow Scheduler
Schedules and triggers workflow execution
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

from ..core.logging import get_logger


@dataclass
class ScheduledTask:
    """A scheduled workflow task"""
    name: str
    workflow: str
    schedule: str  # cron-like expression or interval
    context: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0


class WorkflowScheduler:
    """
    Workflow scheduler for time-based and event-driven execution

    Supports:
    - Interval scheduling (every X minutes/hours)
    - Daily scheduling (at specific time)
    - Cron-like expressions
    - Event triggers
    """

    def __init__(self, execute_callback: Callable = None):
        self.logger = get_logger("ai_os.scheduler")
        self._execute_callback = execute_callback

        # Scheduled tasks
        self._tasks: Dict[str, ScheduledTask] = {}

        # Event triggers
        self._event_triggers: Dict[str, List[str]] = {}

        # Running state
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None

    def set_executor(self, callback: Callable):
        """Set the callback for executing workflows"""
        self._execute_callback = callback

    def schedule(
        self,
        name: str,
        workflow: str,
        schedule: str,
        context: Dict = None,
        enabled: bool = True
    ):
        """
        Schedule a workflow

        Args:
            name: Unique task name
            workflow: Workflow name to execute
            schedule: Schedule expression
                - "interval:5m" - every 5 minutes
                - "interval:1h" - every 1 hour
                - "daily:09:00" - daily at 9 AM
                - "weekly:mon:09:00" - weekly on Monday at 9 AM
            context: Context to pass to workflow
            enabled: Whether schedule is active
        """
        task = ScheduledTask(
            name=name,
            workflow=workflow,
            schedule=schedule,
            context=context or {},
            enabled=enabled,
            next_run=self._calculate_next_run(schedule)
        )
        self._tasks[name] = task
        self.logger.info(f"Scheduled task '{name}': {schedule}")

    def unschedule(self, name: str):
        """Remove a scheduled task"""
        if name in self._tasks:
            del self._tasks[name]
            self.logger.info(f"Unscheduled task: {name}")

    def on_event(self, event: str, workflow: str):
        """
        Register a workflow to run on event

        Args:
            event: Event name (e.g., "document_uploaded", "ticket_created")
            workflow: Workflow to execute
        """
        if event not in self._event_triggers:
            self._event_triggers[event] = []
        self._event_triggers[event].append(workflow)
        self.logger.info(f"Registered trigger: {event} -> {workflow}")

    async def trigger_event(self, event: str, context: Dict = None):
        """Trigger an event, executing associated workflows"""
        workflows = self._event_triggers.get(event, [])

        if not workflows:
            return

        self.logger.info(f"Event triggered: {event} ({len(workflows)} workflows)")

        for workflow in workflows:
            await self._execute_workflow(workflow, context or {})

    async def start(self):
        """Start the scheduler loop"""
        if self._running:
            return

        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("Scheduler started")

    async def stop(self):
        """Stop the scheduler"""
        self._running = False

        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Scheduler stopped")

    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self._running:
            try:
                now = datetime.now()

                for task in self._tasks.values():
                    if not task.enabled:
                        continue

                    if task.next_run and now >= task.next_run:
                        await self._run_task(task)

                # Check every 30 seconds
                await asyncio.sleep(30)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)

    async def _run_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        self.logger.info(f"Running scheduled task: {task.name}")

        task.last_run = datetime.now()
        task.run_count += 1
        task.next_run = self._calculate_next_run(task.schedule)

        await self._execute_workflow(task.workflow, task.context)

    async def _execute_workflow(self, workflow: str, context: Dict):
        """Execute a workflow"""
        if self._execute_callback:
            try:
                await self._execute_callback(workflow, context)
            except Exception as e:
                self.logger.error(f"Workflow execution failed: {e}")

    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time from schedule expression"""
        now = datetime.now()

        if schedule.startswith("interval:"):
            # Parse interval (e.g., "interval:5m", "interval:1h")
            interval_str = schedule.split(":")[1]

            if interval_str.endswith("m"):
                minutes = int(interval_str[:-1])
                return now + timedelta(minutes=minutes)
            elif interval_str.endswith("h"):
                hours = int(interval_str[:-1])
                return now + timedelta(hours=hours)
            elif interval_str.endswith("d"):
                days = int(interval_str[:-1])
                return now + timedelta(days=days)

        elif schedule.startswith("daily:"):
            # Parse daily time (e.g., "daily:09:00")
            time_str = schedule.split(":")[1:]
            hour = int(time_str[0])
            minute = int(time_str[1]) if len(time_str) > 1 else 0

            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        elif schedule.startswith("weekly:"):
            # Parse weekly (e.g., "weekly:mon:09:00")
            parts = schedule.split(":")
            day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
            target_day = day_map.get(parts[1].lower(), 0)
            hour = int(parts[2])
            minute = int(parts[3]) if len(parts) > 3 else 0

            days_ahead = target_day - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7

            next_run = now + timedelta(days=days_ahead)
            return next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Default: 1 hour from now
        return now + timedelta(hours=1)

    def get_schedule(self) -> List[Dict]:
        """Get all scheduled tasks"""
        return [
            {
                "name": task.name,
                "workflow": task.workflow,
                "schedule": task.schedule,
                "enabled": task.enabled,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "run_count": task.run_count
            }
            for task in self._tasks.values()
        ]

    def get_event_triggers(self) -> Dict[str, List[str]]:
        """Get all event triggers"""
        return self._event_triggers.copy()
