# Layer 2: INTELLIGENCE Review Summary

## Dual-Purpose System

OberaConnect has **two intelligence components**:

| Component | Type | Purpose |
|-----------|------|---------|
| Notion Dashboards | Sync Tool | Push data to Notion |
| UniFi Analyzer | Query Engine | Natural language fleet queries |

This review focuses on **Notion Dashboards** (sync tool).

## Data Intelligence Features

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| Data Transformation | Python scripts | Convert API → Notion format |
| Health Scoring | Calculated aggregates | Device/site health metrics |
| Change Detection | Diff comparison | Track config changes |
| Maker/Checker | Threshold rules | Flag anomalies for review |

## Context Awareness

- Correlation IDs track requests across components
- Audit logs capture operation context
- Error messages include relevant state
- Health thresholds trigger alerts

## Related: UniFi Analyzer (Query Engine)

The companion **UniFi Analyzer** provides:
- Natural language queries ("top 10 by clients")
- Intent classification (SUMMARY, FILTER, TOP, FIND)
- Aggregations (sum, average, count)

## Score: 7/10

**Strengths**: Good data transformation, health scoring
**Gap**: Sync tool has limited query capabilities (by design)
