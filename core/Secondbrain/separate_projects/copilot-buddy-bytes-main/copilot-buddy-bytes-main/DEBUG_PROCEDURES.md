# OberaConnect Debug Procedures

**Version:** 1.0.0  
**Last Updated:** 2025-10-08  
**Status:** Active

---

## Quick Reference

### Emergency Debug Checklist
1. ✅ Check console logs for errors
2. ✅ Verify authentication status
3. ✅ Check network requests (failed API calls)
4. ✅ Review edge function logs
5. ✅ Verify RLS policies
6. ✅ Check database connectivity
7. ✅ Review recent code changes

### Critical Tools
- **Console Logs:** Browser DevTools (F12)
- **Network Tab:** Browser DevTools > Network
- **Lovable Cloud Backend:** "View Backend" button in UI
- **System Validation:** `/test/validation`
- **Comprehensive Tests:** `/test/comprehensive`
- **Supabase Linter:** Built-in RLS policy checker

---

## Debug Workflow by Issue Type

### 1. Authentication Issues

#### Symptoms
- Users can't log in
- "Unauthorized" errors
- Session expires immediately
- Infinite redirect loops

#### Debug Steps

**Step 1: Check Authentication Status**
```typescript
// In browser console
const { data: { session }, error } = await supabase.auth.getSession();
console.log('Session:', session);
console.log('Error:', error);
```

**Step 2: Verify User Profile**
```typescript
// Check if user profile exists
const { data: profile } = await supabase
  .from('user_profiles')
  .select('*')
  .eq('user_id', session.user.id)
  .single();
console.log('Profile:', profile);
```

**Step 3: Check User Roles**
```typescript
// Verify roles are assigned
const { data: roles } = await supabase
  .from('user_roles')
  .select('*, roles(*)')
  .eq('user_id', session.user.id);
console.log('User Roles:', roles);
```

**Common Fixes:**
- **No Profile:** User profile didn't auto-create → Manually insert into `user_profiles`
- **No Roles:** User has no role assigned → Assign appropriate role in `user_roles`
- **Session Expired:** Token needs refresh → Clear localStorage and re-login
- **RLS Blocking:** User can't read own profile → Check RLS policies on `user_profiles`

---

### 2. Database Query Failures

#### Symptoms
- "permission denied for table" errors
- Empty results when data should exist
- "policy violation" errors
- Infinite loading states

#### Debug Steps

**Step 1: Check RLS Policies**
```bash
# Use Supabase Linter
# Navigate to Lovable Cloud Backend
# Run: Database > Linter
```

**Step 2: Test Query in SQL Editor**
```sql
-- Test if data exists (as service role)
SELECT * FROM incidents WHERE customer_id = 'your-customer-id';

-- Test if RLS allows access (as authenticated user)
SELECT * FROM incidents WHERE customer_id = 'your-customer-id';
```

**Step 3: Check User's Customer ID**
```typescript
// Verify user's customer_id
const { data: profile } = await supabase
  .from('user_profiles')
  .select('customer_id')
  .eq('user_id', session.user.id)
  .single();
console.log('Customer ID:', profile.customer_id);
```

**Step 4: Verify Foreign Key Constraints**
```sql
-- Check if foreign keys are valid
SELECT * FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY' 
AND table_name = 'incidents';
```

**Common Fixes:**
- **RLS Denying Access:** Policy doesn't match user → Add/update RLS policy
- **Missing customer_id:** User profile missing customer_id → Update `user_profiles`
- **Invalid Foreign Key:** Referenced record doesn't exist → Create parent record first
- **Wrong Filter:** Querying with wrong customer_id → Use correct customer_id from profile

---

### 3. Edge Function Errors

#### Symptoms
- 500 Internal Server Error
- Function timeout
- CORS errors
- "Function not found" errors

#### Debug Steps

**Step 1: Check Function Logs**
```typescript
// In Lovable Cloud Backend
// Navigate to: Functions > Select Function > Logs
// Look for recent errors and stack traces
```

**Step 2: Test Function Directly**
```typescript
// Test edge function call
const { data, error } = await supabase.functions.invoke('function-name', {
  body: { test: 'data' }
});
console.log('Function Response:', data);
console.log('Function Error:', error);
```

**Step 3: Check CORS Configuration**
```typescript
// Verify CORS headers in function
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// Ensure OPTIONS handler exists
if (req.method === 'OPTIONS') {
  return new Response(null, { headers: corsHeaders });
}
```

**Step 4: Verify Function is Deployed**
```bash
# Check supabase/config.toml
[functions.function-name]
verify_jwt = true  # or false
```

**Common Fixes:**
- **CORS Error:** Missing CORS headers → Add corsHeaders to all responses
- **JWT Error:** Function requires auth but not provided → Pass JWT token or set `verify_jwt = false`
- **Timeout:** Function taking too long → Optimize queries, add indexes
- **Not Found:** Function not deployed → Verify in config.toml, redeploy

---

### 4. UI Component Issues

#### Symptoms
- Components not rendering
- Blank pages
- Infinite loading spinners
- "Cannot read property of undefined" errors

#### Debug Steps

**Step 1: Check React Query State**
```typescript
// In component, add console logs
const { data, error, isLoading } = useQuery({
  queryKey: ['incidents'],
  queryFn: async () => {
    console.log('Query Starting...');
    const { data, error } = await supabase.from('incidents').select('*');
    console.log('Query Data:', data);
    console.log('Query Error:', error);
    if (error) throw error;
    return data;
  }
});

console.log('isLoading:', isLoading);
console.log('data:', data);
console.log('error:', error);
```

**Step 2: Verify Props and State**
```typescript
// Add prop validation
useEffect(() => {
  console.log('Props:', { prop1, prop2, prop3 });
  console.log('State:', { state1, state2 });
}, [prop1, prop2, prop3, state1, state2]);
```

**Step 3: Check for Null/Undefined**
```typescript
// Guard against null/undefined
if (!data) {
  return <div>Loading...</div>;
}

// Use optional chaining
const value = data?.nested?.property;

// Provide defaults
const items = data || [];
```

**Common Fixes:**
- **Blank Page:** Component throwing error → Check console for stack trace
- **Infinite Loading:** Query never resolves → Check network tab for failed requests
- **Undefined Error:** Accessing property of null → Add null checks and optional chaining
- **Not Updating:** React Query cache stale → Invalidate query or set `staleTime`

---

### 5. Route/Navigation Issues

#### Symptoms
- 404 Not Found on valid routes
- Routes redirect to wrong page
- Protected routes not blocking access
- Navigation links not working

#### Debug Steps

**Step 1: Verify Route Definition**
```typescript
// Check App.tsx for route
<Route path="/incidents" element={
  <ProtectedRoute>
    <IncidentsDashboard />
  </ProtectedRoute>
} />
```

**Step 2: Check ProtectedRoute Logic**
```typescript
// In ProtectedRoute component
useEffect(() => {
  console.log('Auth State:', { user, loading, session });
  console.log('Require Admin:', requireAdmin);
  console.log('Is Admin:', isAdmin);
}, [user, loading, session, requireAdmin, isAdmin]);
```

**Step 3: Test Navigation**
```typescript
// In browser console
window.location.href = '/incidents';
// Or
import { useNavigate } from 'react-router-dom';
const navigate = useNavigate();
navigate('/incidents');
```

**Common Fixes:**
- **404 on Valid Route:** Route not defined in App.tsx → Add route definition
- **Not Protected:** Missing ProtectedRoute wrapper → Wrap in <ProtectedRoute>
- **Admin Check Failing:** User doesn't have admin role → Assign admin role or remove requireAdmin
- **Redirect Loop:** useEffect causing navigation → Add dependency array to useEffect

---

### 6. Performance Issues

#### Symptoms
- Slow page loads
- Laggy interactions
- High memory usage
- App freezing

#### Debug Steps

**Step 1: Check Network Waterfall**
```
1. Open DevTools > Network
2. Reload page
3. Look for:
   - Large file downloads
   - Slow API requests (>1s)
   - Failed requests causing retries
   - Too many simultaneous requests
```

**Step 2: Profile React Rendering**
```
1. Open React DevTools > Profiler
2. Start recording
3. Perform slow action
4. Stop recording
5. Analyze component render times
```

**Step 3: Check Database Query Performance**
```sql
-- In Lovable Cloud Backend SQL Editor
EXPLAIN ANALYZE
SELECT * FROM incidents 
WHERE customer_id = 'uuid' 
AND status = 'open';

-- Look for:
-- Seq Scan (bad) vs Index Scan (good)
-- High execution time
-- Large row counts
```

**Step 4: Monitor Memory Usage**
```
1. Open DevTools > Performance
2. Record performance
3. Take heap snapshot
4. Look for memory leaks (growing heap)
```

**Common Fixes:**
- **Slow Queries:** Missing indexes → Add database indexes on filtered columns
- **Too Many Re-renders:** Missing React.memo or useCallback → Memoize components and callbacks
- **Large Data Fetches:** Fetching all records → Add pagination or limit
- **Memory Leak:** Not cleaning up subscriptions → Add cleanup in useEffect
- **Unoptimized Images:** Large image files → Compress and optimize images

---

### 7. Mobile App Issues

#### Symptoms
- Blank screen on mobile
- App won't build
- Native features not working
- Hot reload not working

#### Debug Steps

**Step 1: Check Capacitor Configuration**
```typescript
// Verify capacitor.config.ts
const config: CapacitorConfig = {
  appId: 'app.lovable.2e37e4cf64eb4e9a8cf114b876d69899',
  appName: 'copilot-buddy-bytes',
  webDir: 'dist',
  server: {
    url: 'https://2e37e4cf-64eb-4e9a-8cf1-14b876d69899.lovableproject.com?forceHideBadge=true',
    cleartext: true
  }
};
```

**Step 2: Rebuild and Sync**
```bash
npm run build
npx cap sync
npx cap run ios  # or android
```

**Step 3: Check Mobile Console Logs**
```
iOS: Safari > Develop > [Your Device] > [Your App]
Android: Chrome > chrome://inspect > Devices
```

**Step 4: Verify Web App is Accessible**
```bash
# Test if web app URL is accessible
curl https://2e37e4cf-64eb-4e9a-8cf1-14b876d69899.lovableproject.com
```

**Common Fixes:**
- **Blank Screen:** Web URL not accessible → Fix web app deployment
- **Build Fails:** Missing dependencies → Run `npm install`
- **Hot Reload Not Working:** Wrong server.url → Update capacitor.config.ts
- **Native Feature Fails:** Plugin not installed → Install required Capacitor plugin

---

## Systematic Debugging Process

### Level 1: Quick Checks (2 minutes)
1. Check browser console for errors
2. Check network tab for failed requests
3. Verify user is authenticated
4. Refresh page (clear cache)

### Level 2: Component Debugging (10 minutes)
1. Add console.logs to component lifecycle
2. Check React Query state (loading, error, data)
3. Verify props being passed correctly
4. Check for null/undefined access

### Level 3: API/Database Debugging (20 minutes)
1. Test API call in isolation
2. Check edge function logs
3. Test database query in SQL editor
4. Verify RLS policies
5. Check user's customer_id

### Level 4: Deep Dive (60+ minutes)
1. Review recent code changes (git diff)
2. Check for breaking changes in dependencies
3. Profile performance (React DevTools, Chrome DevTools)
4. Review database schema changes
5. Check for race conditions
6. Examine state management flow

---

## Common Error Messages

### "permission denied for table X"
**Cause:** RLS policy blocking access  
**Fix:** Add/update RLS policy or check user's customer_id

### "relation 'X' does not exist"
**Cause:** Table not created or wrong schema  
**Fix:** Run database migration or check table name spelling

### "null value in column 'X' violates not-null constraint"
**Cause:** Required field not provided  
**Fix:** Provide value or make column nullable

### "insert or update on table 'X' violates foreign key constraint"
**Cause:** Referenced record doesn't exist  
**Fix:** Create parent record first or fix foreign key value

### "Failed to fetch"
**Cause:** Network error or CORS issue  
**Fix:** Check network connectivity, verify CORS headers

### "TypeError: Cannot read property 'X' of undefined"
**Cause:** Accessing property on null/undefined object  
**Fix:** Add null check or optional chaining (?.  operator)

### "Maximum update depth exceeded"
**Cause:** Infinite useEffect loop  
**Fix:** Add proper dependencies to useEffect or use useCallback

### "The edge function crashed with an unexpected error"
**Cause:** Unhandled exception in edge function  
**Fix:** Add try-catch blocks and check function logs

---

## Debug Tools Reference

### Browser DevTools
- **Console:** `Ctrl+Shift+J` (Windows) / `Cmd+Option+J` (Mac)
- **Network:** `Ctrl+Shift+I` > Network tab
- **React DevTools:** Browser extension required
- **Sources/Debugger:** Set breakpoints in code

### Lovable Cloud Backend
```
Access: "View Backend" button in UI
Features:
- Table Editor: View/edit database records
- SQL Editor: Run custom queries
- Functions: View logs and invoke functions
- Authentication: Manage users
- Policies: View/edit RLS policies
- Database: View schema and relationships
```

### System Validation Dashboard
```
Path: /test/validation
Features:
- Database schema validation
- RLS policy testing
- Edge function health checks
- Performance benchmarks
- UI component validation
```

### Comprehensive Test Dashboard
```
Path: /test/comprehensive
Features:
- Test data generation
- Security fuzz testing
- Data flow tracing
- Integration testing
```

### React Query Devtools
```typescript
// Add to App.tsx for development
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

---

## Prevention Best Practices

### Code Review Checklist
- [ ] Null/undefined checks added where needed
- [ ] Error handling implemented (try-catch)
- [ ] Loading states handled in UI
- [ ] RLS policies verified
- [ ] Foreign keys valid
- [ ] CORS headers on edge functions
- [ ] TypeScript types correct
- [ ] React Query keys unique
- [ ] useEffect dependencies correct
- [ ] Console.logs removed (or debug mode only)

### Testing Checklist
- [ ] Unit tests for utility functions
- [ ] Integration tests for API calls
- [ ] E2E tests for critical flows
- [ ] Manual testing in all user roles
- [ ] Mobile responsiveness tested
- [ ] Performance profiling done
- [ ] Security audit completed
- [ ] Accessibility check passed

### Deployment Checklist
- [ ] Database migrations tested in staging
- [ ] Edge functions deployed and tested
- [ ] Environment variables configured
- [ ] RLS policies applied
- [ ] Indexes created
- [ ] Monitoring enabled
- [ ] Backup verified
- [ ] Rollback plan ready

---

## Emergency Response

### Production Issue (Critical)

**Immediate Actions (< 5 min):**
1. Check if issue is widespread or isolated
2. Review recent deployments (last 24 hours)
3. Check system health (database, edge functions)
4. Notify team via communication channel

**Diagnosis (5-15 min):**
1. Reproduce issue in production
2. Check error logs (browser console, edge functions)
3. Identify root cause
4. Determine if rollback needed

**Resolution (15-60 min):**
1. If simple fix: Deploy hotfix
2. If complex: Rollback to previous version
3. Verify fix resolves issue
4. Monitor for recurrence

**Post-Mortem (24 hours):**
1. Document issue and resolution
2. Update runbooks if needed
3. Add tests to prevent recurrence
4. Review deployment process

---

## Getting Help

### Self-Service Resources
1. Check this document first
2. Review [TESTING_GUIDE.md](./TESTING_GUIDE.md)
3. Search [MODULE_STRUCTURE.md](./MODULE_STRUCTURE.md)
4. Check [API_REFERENCE.md](./API_REFERENCE.md)
5. Review [ARCHITECTURE.md](./ARCHITECTURE.md)

### Escalation Path
1. **Level 1:** Check documentation and logs
2. **Level 2:** Review code with team member
3. **Level 3:** Consult senior developer
4. **Level 4:** Contact system administrator

### Information to Provide
- **What:** Description of the issue
- **When:** When did it start?
- **Where:** Which page/component/function?
- **Who:** Which user(s) affected?
- **How:** Steps to reproduce
- **Logs:** Error messages and stack traces
- **Environment:** Browser, OS, mobile/desktop

---

**Document Maintained By:** Development Team  
**Last Review:** 2025-10-08  
**Next Review:** 2025-10-15 (Weekly)
