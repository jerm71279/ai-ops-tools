# Repetitive Task Detection & Automation Suggestions

## Overview

The platform now automatically detects when employees perform the same task 3+ times and suggests automation workflows using AI. This feature helps identify automation opportunities and improve efficiency.

## Architecture

### Database
- **Table**: `task_repetition_analysis`
- Tracks task patterns per user with repetition counts
- Stores AI-generated workflow suggestions
- Real-time updates enabled

### Edge Functions
1. **repetitive-task-detector**: Tracks task repetitions
2. **automation-suggester**: Generates AI-powered workflow suggestions using Lovable AI (Gemini 2.5 Flash)

### Frontend Components
- **AutomationSuggestions**: Displays suggested automations in the Portal
- **useRepetitiveTaskDetection**: React hook for tracking tasks

## How It Works

1. **Detection**: When an employee performs an action, the system tracks it
2. **Pattern Recognition**: After 3 repetitions, the pattern is flagged
3. **AI Analysis**: Lovable AI analyzes the task and generates a workflow suggestion
4. **Notification**: User sees a toast notification and card in the Portal
5. **Action**: User can create the workflow, view details, or dismiss

## Usage

### In Your Components

```typescript
import { useRepetitiveTaskDetection } from "@/hooks/useRepetitiveTaskDetection";

function MyComponent() {
  const { detectTask } = useRepetitiveTaskDetection();

  const handleUserAction = async () => {
    // Your action logic here
    await someAction();
    
    // Track the task
    await detectTask({
      actionType: "export_report",
      systemName: "compliance",
      context: {
        reportType: "SOC2",
        department: "IT"
      }
    });
  };

  return <Button onClick={handleUserAction}>Export Report</Button>;
}
```

### Examples of Trackable Actions

- **Document exports** (action: "export_document", system: "knowledge_base")
- **Report generation** (action: "generate_report", system: "compliance")
- **Data entry** (action: "manual_data_entry", system: "cmdb")
- **Approval requests** (action: "request_approval", system: "change_management")
- **File uploads** (action: "upload_file", system: "evidence_management")
- **Search queries** (action: "search", system: "global_search")
- **Status updates** (action: "update_status", system: "workflow")

## AI Suggestion Structure

```json
{
  "workflowName": "Auto-Generate SOC2 Compliance Reports",
  "description": "Automatically generates and emails SOC2 reports on a schedule",
  "steps": [
    { "order": 1, "action": "Trigger on schedule", "details": "Run every Monday at 9am" },
    { "order": 2, "action": "Query compliance data", "details": "Fetch latest SOC2 metrics" },
    { "order": 3, "action": "Generate PDF report", "details": "Format data into report template" },
    { "order": 4, "action": "Send email", "details": "Email to compliance team" }
  ],
  "triggerType": "schedule",
  "triggerConfig": { "cron": "0 9 * * 1" },
  "estimatedTimeSavingsMinutes": 15,
  "implementationDifficulty": "medium",
  "requiredIntegrations": ["compliance", "email"],
  "confidence": 85
}
```

## Viewing Suggestions

Users see automation suggestions in:
1. **Portal Dashboard**: Cards with workflow details and action buttons
2. **Toast Notifications**: When the 3rd repetition triggers a suggestion
3. **Knowledge Insights**: High-confidence suggestions create knowledge articles

## Status Flow

- **detected**: Task pattern identified, counting repetitions
- **suggested**: AI has generated a workflow suggestion (shown to user)
- **automated**: User created the workflow
- **dismissed**: User dismissed the suggestion
- **ignored**: System marked as not suitable for automation

## Configuration

### Edge Function Settings
Both functions require JWT verification (user must be authenticated).

### AI Model
Uses **google/gemini-2.5-flash** via Lovable AI Gateway (no API key needed).

### Thresholds
- **Suggestion Trigger**: 3 repetitions
- **Knowledge Insight**: confidence > 70%
- **Knowledge Article**: confidence > 85%

## Integration Points

### Current Integrations
- Employee Portal
- Workflow Automation system
- Knowledge Base
- AI Learning Metrics

### Future Enhancements
- Department-specific automation templates
- Cross-user pattern detection
- Automated workflow creation (with approval)
- ROI tracking for implemented automations
- Integration with Microsoft Power Automate
- Slack notifications for suggestions

## Security

- Row Level Security enabled on `task_repetition_analysis`
- Users can only view their own repetitions
- Admin users can view organization-wide patterns
- All AI suggestions logged for audit

## Performance

- Real-time updates via Supabase Realtime
- Indexed queries for fast lookups
- Async suggestion generation (non-blocking)
- Task signatures normalized for pattern matching

## Monitoring

Track these metrics:
- Total suggestions generated
- Acceptance rate (suggestions → workflows created)
- Time savings from automated workflows
- Most common repetitive tasks
- Department-level automation opportunities

## Troubleshooting

**Suggestions not appearing?**
- Ensure user is authenticated
- Check that task is tracked correctly (check `task_repetition_analysis` table)
- Verify edge functions are deployed
- Check browser console for errors

**AI suggestions low quality?**
- Review task context data (more context = better suggestions)
- Check AI confidence score
- Ensure task signature is meaningful

**Performance issues?**
- Review indexes on `task_repetition_analysis`
- Consider batching detection calls
- Use debouncing for rapid repeated actions
