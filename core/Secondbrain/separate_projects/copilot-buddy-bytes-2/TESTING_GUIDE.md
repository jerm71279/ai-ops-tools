# OberaConnect Testing & Validation Guide

## Overview

OberaConnect includes comprehensive testing and validation tools to ensure system reliability, security, and performance. This guide covers all available testing dashboards, validation flows, and best practices.

## Testing Dashboards

### 1. System Validation Dashboard
**Location:** `/test/validation`  
**Access:** Admin Only

#### Features
- **Database Schema Validation**: Verifies all critical tables exist and are accessible
- **Row Level Security Testing**: Validates RLS policies are working correctly
- **Edge Function Health Checks**: Tests all serverless functions are accessible
- **Data Integrity Checks**: Verifies referential integrity across tables
- **Performance Testing**: Measures query performance and identifies bottlenecks
- **UI Component Validation**: Ensures all critical routes are accessible

#### How to Use
1. Navigate to `/test/validation`
2. Click "Start Validation" button
3. Monitor progress bar as tests run (takes ~30-60 seconds)
4. Review results by category in detailed tabs
5. Address any failed or warning tests

#### Test Categories

**Database Schema (6 tests)**
- Validates existence of: workflows, workflow_executions, knowledge_articles, evidence_files, audit_logs
- Checks record counts

**Row Level Security (1+ tests)**
- Tests authenticated user access
- Validates policy enforcement

**Edge Functions (4+ tests)**
- workflow-insights
- intelligent-assistant
- department-assistant
- comprehensive-test-data-generator

**Data Integrity (1+ tests)**
- Validates workflow execution references
- Checks for orphaned records

**Performance (1+ tests)**
- Query execution time
- Response time benchmarks

**UI Components (4 tests)**
- Route accessibility checks

---

### 2. Comprehensive Test Dashboard
**Location:** `/test/comprehensive`  
**Access:** Admin Only

#### Features
- **Test Data Generation**: Creates realistic test data across 8 components
- **Security Fuzz Testing**: Tests for SQL injection, XSS, and buffer overflow vulnerabilities
- **Database Flow Tracing**: Traces data flows through the system

#### Components Tested
1. Knowledge Base (articles, categories, insights)
2. AI Interactions (chatbot history, responses)
3. Audit Logs (security events, actions)
4. Behavioral Events (user analytics)
5. Anomaly Detection (security alerts)
6. MCP Servers (AI agents, tools)
7. ML Insights (predictions, recommendations)
8. Client Onboarding (tasks, milestones)

#### How to Use

**Generate Test Data**
1. Click "Generate Data" or "Run All Tests"
2. Wait for completion (~10-30 seconds)
3. Review summary showing:
   - Total components tested
   - Records created
   - Errors encountered
   - Total duration

**Run Fuzz Tests**
1. Click "Fuzz Tests" or "Run All Tests"
2. System tests multiple attack vectors
3. Review results:
   - Total tests run
   - Tests passed/failed
   - Vulnerabilities found

**Trace Data Flows**
1. Select flow type: Workflow, Compliance, or Knowledge
2. Click trace button
3. View step-by-step data flow:
   - Tables affected
   - Operations performed
   - Related data connections

---

## Test Flows

### End-to-End Workflow Testing

#### 1. Workflow Execution Flow
```
User Action → Workflow Trigger → Execution Start → 
Step Processing → Evidence Generation → Audit Logging → 
Completion → Metrics Update
```

**Validation Points:**
- Workflow triggers correctly
- All steps execute in sequence
- Errors are logged properly
- Evidence is generated and linked
- Audit trail is complete

#### 2. Knowledge Base Flow
```
Article Creation → AI Processing → Categorization → 
Publishing → Access Logging → Insight Generation
```

**Validation Points:**
- Articles save correctly
- AI summaries generate
- Categories are assigned
- Search indexing works
- Access is tracked

#### 3. Compliance Evidence Flow
```
Evidence Upload → Framework Tagging → Control Mapping → 
Audit Trail → Report Generation → Verification
```

**Validation Points:**
- Files upload successfully
- Framework tags apply
- Controls link correctly
- Audit logs capture actions
- Reports generate accurately

---

## Security Testing

### Fuzz Testing Coverage

1. **SQL Injection Tests**
   - Single/double quotes
   - UNION attacks
   - Comment injection
   - Stacked queries

2. **XSS (Cross-Site Scripting) Tests**
   - Script tags
   - Event handlers
   - Data URIs
   - Unicode bypasses

3. **Buffer Overflow Tests**
   - Large string inputs
   - Deeply nested objects
   - Array size limits
   - Resource exhaustion

4. **Input Validation Tests**
   - Null/undefined values
   - Special characters
   - Emoji and unicode
   - HTML entities

### Expected Results
- **Passed**: Input properly sanitized/rejected
- **Failed**: Input accepted without validation
- **Vulnerability**: Security risk identified

---

## Performance Benchmarks

### Query Performance Targets
- Simple SELECT: < 100ms
- Complex JOIN: < 500ms
- Aggregation: < 1000ms
- Full-text search: < 2000ms

### Edge Function Targets
- Cold start: < 2000ms
- Warm execution: < 500ms
- AI inference: < 5000ms

### Page Load Targets
- Initial load: < 3s
- Navigation: < 1s
- Component render: < 500ms

---

## Troubleshooting

### Common Test Failures

**Database Schema Tests Fail**
- **Cause**: Missing tables or RLS blocking access
- **Fix**: Check migration status, verify RLS policies

**Edge Function Tests Fail**
- **Cause**: Function deployment issues or missing secrets
- **Fix**: Check function logs, verify environment variables

**Performance Tests Fail**
- **Cause**: Slow queries, missing indexes, or data volume
- **Fix**: Add indexes, optimize queries, consider pagination

**Security Tests Fail**
- **Cause**: Missing input validation, weak RLS policies
- **Fix**: Add validation schemas, strengthen RLS policies

---

## Best Practices

### Testing Frequency
- **System Validation**: Run weekly or after major changes
- **Fuzz Testing**: Run before each release
- **Test Data Generation**: Use for development/staging only
- **Flow Tracing**: Use when debugging data flow issues

### Test Data Management
- **Never run test data generation in production**
- Always clear test data after use
- Use dedicated test/staging environments
- Mark test records clearly (e.g., customer_id with specific pattern)

### Security Testing
- Run fuzz tests in isolated environment
- Review all vulnerabilities immediately
- Document remediation steps
- Retest after fixes

---

## Integration with CI/CD

The test dashboards can be automated through API calls to the edge functions:

```typescript
// Example: Automated validation in CI/CD
const { data } = await supabase.functions.invoke('comprehensive-test-data-generator');
const { data: fuzzResults } = await supabase.functions.invoke('input-fuzzer');

if (fuzzResults.summary.vulnerabilities_found > 0) {
  throw new Error('Security vulnerabilities detected!');
}
```

---

## Reporting

### Test Reports Include
1. **Summary Statistics**: Pass/fail counts, duration, coverage
2. **Detailed Results**: Individual test outcomes with messages
3. **Recommendations**: Suggested fixes for failures
4. **Trends**: Historical comparison of test results

### Export Options
- JSON format for programmatic access
- Visual dashboards for human review
- Integration with monitoring tools

---

## Additional Resources

- **Database Schema**: See `/ARCHITECTURE.md`
- **API Documentation**: See `/API_REFERENCE.md`
- **Security Guidelines**: See `/AUDIT_LOGGING_GUIDE.md`
- **Edge Functions**: See `/supabase/functions/`

---

## Support

For issues with testing or validation:
1. Check edge function logs in Lovable Cloud dashboard
2. Review console logs in browser DevTools
3. Verify RLS policies are configured correctly
4. Ensure all required secrets are configured

---

**Last Updated**: 2025-10-05  
**Version**: 1.0.0
