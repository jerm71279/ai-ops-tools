# Power Automate Flow Templates

## Overview

This document provides templates and instructions for creating Power Automate flows to integrate with the Engineering Command Center (ECC).

---

## Flow 1: Task Overdue Alert

**Purpose:** Send notifications when tasks are past due

### Trigger
- **Type:** Recurrence
- **Frequency:** Daily at 8:00 AM

### Flow Steps

```yaml
Trigger: Recurrence
  Frequency: Day
  Interval: 1
  Start time: 08:00

Action 1: Get items (SharePoint)
  Site Address: https://oberaconnect.sharepoint.com/sites/Engineering
  List Name: Tasks
  Filter Query: Status ne 'Done' and Status ne 'Completed' and DueDate lt '@{utcNow()}'

Condition: Check if items exist
  If length(body('Get_items')?['value']) > 0:

    Action 2: Apply to each (loop through overdue tasks)
      For each: @{body('Get_items')?['value']}

      Action 3: Get user profile (V2)
        User (UPN): @{items('Apply_to_each')?['AssignedTo']?['Email']}

      Action 4: Send an email (V2)
        To: @{outputs('Get_user_profile_(V2)')?['body/mail']}
        Subject: "Overdue Task: @{items('Apply_to_each')?['Title']}"
        Body: |
          <h2>Task Overdue Alert</h2>
          <p><strong>Task:</strong> @{items('Apply_to_each')?['Title']}</p>
          <p><strong>Due Date:</strong> @{items('Apply_to_each')?['DueDate']}</p>
          <p><strong>Project:</strong> @{items('Apply_to_each')?['ProjectName']}</p>
          <p><strong>Priority:</strong> @{items('Apply_to_each')?['Priority']}</p>
          <p>Please update the task status or contact your manager if you need assistance.</p>
          <p><a href="https://jolly-island-06ade710f.3.azurestaticapps.net">Open Engineering Command Center</a></p>

      Action 5: Post adaptive card in a chat or channel (Teams)
        Team: Engineering
        Channel: General
        Adaptive Card: |
          {
            "type": "AdaptiveCard",
            "body": [
              {
                "type": "TextBlock",
                "size": "Medium",
                "weight": "Bolder",
                "text": "Task Overdue Alert",
                "color": "Attention"
              },
              {
                "type": "FactSet",
                "facts": [
                  {"title": "Task", "value": "@{items('Apply_to_each')?['Title']}"},
                  {"title": "Assigned To", "value": "@{items('Apply_to_each')?['AssignedTo']?['LookupValue']}"},
                  {"title": "Due Date", "value": "@{items('Apply_to_each')?['DueDate']}"},
                  {"title": "Days Overdue", "value": "@{div(sub(ticks(utcNow()),ticks(items('Apply_to_each')?['DueDate'])),864000000000)}"}
                ]
              }
            ],
            "actions": [
              {
                "type": "Action.OpenUrl",
                "title": "Open ECC",
                "url": "https://jolly-island-06ade710f.3.azurestaticapps.net"
              }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4"
          }
```

### Setup Instructions

1. Go to https://make.powerautomate.com
2. Click "Create" > "Scheduled cloud flow"
3. Name: "ECC - Task Overdue Alert"
4. Set recurrence to daily at 8:00 AM
5. Add SharePoint "Get items" action
6. Configure filter for overdue incomplete tasks
7. Add email and Teams notification actions
8. Save and test

---

## Flow 2: Task Assignment Notification

**Purpose:** Notify users when assigned to a task

### Trigger
- **Type:** When an item is created or modified (SharePoint)
- **List:** Tasks

### Flow Steps

```yaml
Trigger: When an item is created or modified
  Site Address: https://oberaconnect.sharepoint.com/sites/Engineering
  List Name: Tasks

Condition: Check if AssignedTo changed
  If: @{triggerBody()?['AssignedTo']?['Email']} is not empty

  Action 1: Get user profile
    User: @{triggerBody()?['AssignedTo']?['Email']}

  Action 2: Send email notification
    To: @{outputs('Get_user_profile')?['body/mail']}
    Subject: "New Task Assigned: @{triggerBody()?['Title']}"
    Body: |
      <h2>You've been assigned a new task</h2>
      <table>
        <tr><td><strong>Task:</strong></td><td>@{triggerBody()?['Title']}</td></tr>
        <tr><td><strong>Project:</strong></td><td>@{triggerBody()?['ProjectName']}</td></tr>
        <tr><td><strong>Priority:</strong></td><td>@{triggerBody()?['Priority']}</td></tr>
        <tr><td><strong>Due Date:</strong></td><td>@{triggerBody()?['DueDate']}</td></tr>
        <tr><td><strong>Description:</strong></td><td>@{triggerBody()?['Description']}</td></tr>
      </table>
      <p><a href="https://jolly-island-06ade710f.3.azurestaticapps.net">View in Engineering Command Center</a></p>

  Action 3: Post to Teams (optional)
    Post a message: @{triggerBody()?['AssignedTo']?['LookupValue']} was assigned task "@{triggerBody()?['Title']}"
```

---

## Flow 3: Time Entry Approval

**Purpose:** Route time entries over 8 hours for manager approval

### Trigger
- **Type:** When an item is created (SharePoint)
- **List:** TimeEntries

### Flow Steps

```yaml
Trigger: When an item is created
  Site Address: https://oberaconnect.sharepoint.com/sites/Engineering
  List Name: TimeEntries

Condition: Hours > 8
  If: @{triggerBody()?['Hours']} greater than 8

  Action 1: Start and wait for an approval
    Approval type: Approve/Reject - First to respond
    Title: "Time Entry Approval Required"
    Assigned to: manager@oberaconnect.com
    Details: |
      Employee: @{triggerBody()?['Employee']}
      Hours: @{triggerBody()?['Hours']}
      Date: @{triggerBody()?['EntryDate']}
      Project: @{triggerBody()?['ProjectName']}
      Description: @{triggerBody()?['Description']}
      Billable: @{triggerBody()?['Billable']}

  Condition: Check approval outcome
    If Approved:
      Action 2a: Update item (SharePoint)
        ID: @{triggerBody()?['ID']}
        ApprovalStatus: "Approved"

      Action 3a: Send email to employee
        Subject: "Time Entry Approved"
        Body: "Your time entry for @{triggerBody()?['Hours']} hours has been approved."

    Else (Rejected):
      Action 2b: Update item (SharePoint)
        ID: @{triggerBody()?['ID']}
        ApprovalStatus: "Rejected"

      Action 3b: Send email to employee
        Subject: "Time Entry Rejected"
        Body: "Your time entry for @{triggerBody()?['Hours']} hours requires revision. Please contact your manager."
```

---

## Flow 4: SLA Breach Alert

**Purpose:** Monitor tickets for SLA breaches and alert team

### Trigger
- **Type:** Recurrence
- **Frequency:** Every 30 minutes

### SLA Thresholds

| Priority | Max Response Time |
|----------|-------------------|
| Critical | 4 hours |
| High | 8 hours |
| Medium | 24 hours |
| Low | 72 hours |

### Flow Steps

```yaml
Trigger: Recurrence
  Frequency: Minute
  Interval: 30

Action 1: Get open tickets
  Site Address: https://oberaconnect.sharepoint.com/sites/Engineering
  List Name: Tickets
  Filter Query: Status ne 'Closed' and Status ne 'Resolved'

Action 2: Apply to each ticket
  For each: @{body('Get_items')?['value']}

  Action 3: Compose SLA threshold
    Based on Priority:
      Critical: 4
      High: 8
      Medium: 24
      Low: 72

  Action 4: Calculate hours since created
    Expression: div(sub(ticks(utcNow()),ticks(items('Apply_to_each')?['Created'])),36000000000)

  Condition: Check if SLA breached
    If: @{outputs('Calculate_hours')} > @{outputs('SLA_threshold')}

    AND SLAAlerted is not true:

      Action 5: Post urgent alert to Teams
        Channel: #engineering-alerts
        Message: |
          @channel SLA BREACH ALERT

          Ticket: @{items('Apply_to_each')?['Title']}
          Priority: @{items('Apply_to_each')?['Priority']}
          Age: @{outputs('Calculate_hours')} hours
          SLA Limit: @{outputs('SLA_threshold')} hours
          Customer: @{items('Apply_to_each')?['Customer']}

          Immediate action required!

      Action 6: Send email to ticket owner + manager
        To: ticket-owner; manager@oberaconnect.com
        Subject: "URGENT: SLA Breach - @{items('Apply_to_each')?['Title']}"
        Importance: High

      Action 7: Update ticket
        SLAStatus: "Breached"
        SLAAlerted: true
```

---

## Flow 5: Weekly Status Report

**Purpose:** Generate and send weekly engineering status report

### Trigger
- **Type:** Recurrence
- **Frequency:** Weekly, Monday 8:00 AM

### Flow Steps

```yaml
Trigger: Recurrence
  Frequency: Week
  Interval: 1
  On days: Monday
  At time: 08:00

Action 1: Get all active projects
  Filter: Status eq 'In Progress' or Status eq 'Planning'

Action 2: Get tasks completed this week
  Filter: Status eq 'Done' and Modified ge '@{addDays(utcNow(), -7)}'

Action 3: Get time entries this week
  Filter: EntryDate ge '@{addDays(utcNow(), -7)}'

Action 4: Compose report HTML
  Expression: |
    <html>
    <body>
      <h1>Engineering Weekly Status Report</h1>
      <p>Week of @{formatDateTime(utcNow(), 'MMMM dd, yyyy')}</p>

      <h2>Summary</h2>
      <ul>
        <li>Active Projects: @{length(body('Get_projects')?['value'])}</li>
        <li>Tasks Completed: @{length(body('Get_completed_tasks')?['value'])}</li>
        <li>Total Hours Logged: @{sum(body('Get_time_entries')?['value'], 'Hours')}</li>
      </ul>

      <h2>Project Status</h2>
      <table border="1">
        <tr><th>Project</th><th>Status</th><th>% Complete</th><th>Tasks Done</th></tr>
        <!-- Loop through projects -->
      </table>

      <h2>Team Utilization</h2>
      <table border="1">
        <tr><th>Employee</th><th>Hours</th><th>Billable</th></tr>
        <!-- Loop through time entries grouped by employee -->
      </table>
    </body>
    </html>

Action 5: Send email
  To: engineering-team@oberaconnect.com; leadership@oberaconnect.com
  Subject: "Engineering Weekly Status - @{formatDateTime(utcNow(), 'MMMM dd')}"
  Body: @{outputs('Compose_report')}

Action 6: Post summary to Teams
  Channel: #engineering
  Message: Weekly status report sent. @{length(body('Get_completed_tasks')?['value'])} tasks completed, @{sum(body('Get_time_entries')?['value'], 'Hours')} hours logged.
```

---

## Deployment Checklist

### Prerequisites
- [ ] Power Automate license (M365 or Premium)
- [ ] SharePoint connection configured
- [ ] Teams connection configured
- [ ] Outlook connection configured

### Flow Deployment Order
1. [ ] Task Overdue Alert (immediate value)
2. [ ] Task Assignment Notification
3. [ ] SLA Breach Alert
4. [ ] Time Entry Approval
5. [ ] Weekly Status Report

### Testing
- [ ] Test each flow with sample data
- [ ] Verify email delivery
- [ ] Verify Teams posts
- [ ] Check SharePoint item updates

---

## Webhook Endpoints

For ECC to trigger flows programmatically:

### HTTP Request Trigger Setup

1. Create new flow with "When a HTTP request is received" trigger
2. Define JSON schema for expected payload
3. Copy the HTTP POST URL
4. Add to ECC configuration

### Example Webhook Payload

```json
{
  "eventType": "task_created",
  "taskId": "123",
  "taskTitle": "Implement feature X",
  "assignedTo": "john@oberaconnect.com",
  "priority": "High",
  "projectName": "Customer Portal",
  "dueDate": "2025-12-15"
}
```

---

**Created:** 2025-12-04
**Version:** 1.0
**Author:** OberaConnect Engineering
