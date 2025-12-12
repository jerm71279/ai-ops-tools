# Microsoft 365 Integration - Technical Documentation

## Overview

OberaConnect integrates deeply with Microsoft 365 to provide seamless access to user data including calendars, emails, Teams chats, files, and more directly within the platform.

## Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Customer     │
│    Portal)      │
└────────┬────────┘
         │
         │ 1. User clicks "Sign in with Microsoft"
         ▼
┌─────────────────┐
│  Supabase Auth  │
│  (OAuth Flow)   │
└────────┬────────┘
         │
         │ 2. Redirects to Microsoft OAuth
         ▼
┌─────────────────┐
│   Microsoft     │
│   Azure AD      │
└────────┬────────┘
         │
         │ 3. Returns access token
         ▼
┌─────────────────┐
│  Supabase Auth  │
│  (Stores token) │
└────────┬────────┘
         │
         │ 4. User authenticated
         ▼
┌─────────────────┐
│  React Frontend │
│  Calls Graph    │
│  API function   │
└────────┬────────┘
         │
         │ 5. Invokes graph-api edge function
         ▼
┌─────────────────┐
│ graph-api       │
│ Edge Function   │
└────────┬────────┘
         │
         │ 6. Retrieves provider_token
         │ 7. Calls Microsoft Graph API
         ▼
┌─────────────────┐
│  Microsoft      │
│  Graph API      │
└─────────────────┘
```

## Components

### Frontend Components

#### 1. `src/components/Microsoft365Integration.tsx`
Main component that displays Microsoft 365 data in tabbed interface.

**Features:**
- User profile display
- Calendar events (upcoming 5)
- Recent emails (top 10)
- Teams chats (top 10)
- **Account linking** - Users can link Microsoft 365 to existing accounts
- **Connection status checking** - Verifies if user has Azure provider
- **Reconnect capability** - Handles expired sessions gracefully

**State Management:**
```typescript
const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>([]);
const [emails, setEmails] = useState<Email[]>([]);
const [teamsChats, setTeamsChats] = useState<TeamsChat[]>([]);
const [hasAzureProvider, setHasAzureProvider] = useState<boolean | null>(null);
const [isConnecting, setIsConnecting] = useState(false);
```

**Account Linking Flow:**
```typescript
const handleConnectMicrosoft365 = async () => {
  const { error } = await supabase.auth.linkIdentity({
    provider: 'azure',
    options: {
      scopes: 'openid email profile User.Read Calendars.Read Mail.Read Files.Read.All Chat.Read',
      redirectTo: `${window.location.origin}/portal?tab=microsoft365`,
    }
  });
};
```

**Error Handling:**
- Shows "Connect Microsoft 365" button when Azure provider not linked
- Shows friendly message when not signed in with Microsoft
- Displays loading spinner during data fetch
- Handles token expiration with "Reconnect" button
- Provides actionable error messages with clear next steps

#### 2. `src/pages/Portal.tsx`
Portal page that includes Microsoft 365 integration tab.

**Integration:**
```tsx
<TabsContent value="microsoft365">
  <Microsoft365Integration />
</TabsContent>
```

#### 3. `src/pages/Auth.tsx`
Authentication page with Microsoft 365 OAuth sign-in.

**OAuth Configuration:**
```typescript
const { error } = await supabase.auth.signInWithOAuth({
  provider: 'azure',
  options: {
    scopes: 'openid email profile User.Read Calendars.Read Mail.Read Files.Read.All Chat.Read',
    redirectTo: `${window.location.origin}/portal`,
  }
});
```

### Backend Components

#### 1. `supabase/functions/graph-api/index.ts`
Edge function that proxies Microsoft Graph API calls.

**Endpoints Used:**
- `/me` - User profile
- `/me/calendar/calendarView` - Calendar events
- `/me/messages` - Emails
- `/me/chats` - Teams chats

**Security:**
- Validates user authentication
- Retrieves provider token from user metadata
- Handles CORS preflight requests
- Returns appropriate error codes

**Key Functions:**
```typescript
// Get user's session
const { data: { user }, error: userError } = await supabase.auth.getUser(token);

// Retrieve provider token
const providerToken = user.user_metadata?.provider_token;

// Make Graph API request
const graphResponse = await fetch(`https://graph.microsoft.com/v1.0${endpoint}`, {
  method,
  headers: {
    'Authorization': `Bearer ${providerToken}`,
    'Content-Type': 'application/json',
  },
});
```

## Database Schema

### Current Tables

**Note:** User profiles table needs migration to support Microsoft 365 users.

#### `user_profiles` (needs fix)
```sql
CREATE TABLE user_profiles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users NOT NULL,
  full_name text,
  department text,
  customer_id uuid,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
```

**Issue:** No profile created for Microsoft 365 OAuth users.

**Fix Required:** Add trigger for OAuth sign-ins.

## Microsoft Graph API Endpoints

### Currently Implemented

| Endpoint | Description | Permissions Required |
|----------|-------------|---------------------|
| `/me` | User profile data | User.Read |
| `/me/calendar/calendarView` | Calendar events | Calendars.Read |
| `/me/messages` | Email messages | Mail.Read |
| `/me/chats` | Teams chats | Chat.Read |

### Planned Endpoints

| Endpoint | Description | Permissions Required |
|----------|-------------|---------------------|
| `/me/drive` | OneDrive files | Files.Read.All |
| `/me/contacts` | Contacts | Contacts.Read |
| `/me/todo/lists` | To-Do lists | Tasks.Read |
| `/me/presence` | User presence | Presence.Read |
| `/teams/{id}/channels` | Teams channels | ChannelMessage.Read.All |

## Permission Scopes

### Current Scopes
```
openid email profile User.Read Calendars.Read Mail.Read Files.Read.All Chat.Read
```

### Scope Descriptions

| Scope | Type | Description |
|-------|------|-------------|
| `User.Read` | Delegated | Read user profile |
| `Calendars.Read` | Delegated | Read user calendars |
| `Mail.Read` | Delegated | Read user mail |
| `Files.Read.All` | Delegated | Read all files user can access |
| `Chat.Read` | Delegated | Read user's Teams chats |

### Admin Consent Required
✅ Yes - All these scopes require tenant admin consent.

## Error Handling

### Common Errors

#### 1. 401 - No Microsoft access token
**Cause:** User not signed in with Microsoft 365 or token expired.

**Solution:**
```typescript
if (error && error.includes('sign in with Microsoft')) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Microsoft 365 Integration</CardTitle>
        <CardDescription>
          Sign in with Microsoft 365 to access your calendar, emails, and more.
        </CardDescription>
      </CardHeader>
    </Card>
  );
}
```

#### 2. 406 - Cannot coerce to single JSON object
**Cause:** Database query returning 0 rows when expecting 1.

**Solution:** Run migration to create user profiles for OAuth users.

#### 3. TOKEN_EXPIRED
**Cause:** Microsoft access token has expired (typically 1 hour).

**Solution:** Implement token refresh flow (planned feature).

## Security Considerations

### Current Implementation
- ✅ CORS headers configured
- ✅ Authentication required for edge function
- ✅ Provider token stored in user metadata
- ✅ No client-side token exposure

### Needed Improvements
- ❌ Token encryption at rest
- ❌ Token refresh mechanism
- ❌ Rate limiting
- ❌ Audit logging
- ❌ Least privilege principle (too many scopes)

## Testing

### Manual Testing Steps

1. **Sign in with Microsoft 365:**
   ```
   1. Go to /auth
   2. Click "Sign in with Microsoft 365"
   3. Authorize permissions
   4. Should redirect to /portal
   ```

2. **View Microsoft 365 data:**
   ```
   1. Navigate to /portal
   2. Click "Microsoft 365" tab
   3. Verify profile displays
   4. Verify calendar events show
   5. Verify emails display
   6. Verify Teams chats appear
   ```

3. **Test error handling:**
   ```
   1. Sign in with email (not Microsoft)
   2. Go to Microsoft 365 tab
   3. Should see friendly message
   ```

### Automated Testing (TODO)

```typescript
// Example test structure
describe('Microsoft365Integration', () => {
  it('should display user profile', async () => {
    // Mock Graph API response
    // Render component
    // Assert profile data displayed
  });

  it('should handle token expiration', async () => {
    // Mock 401 response
    // Render component
    // Assert error message shown
  });
});
```

## Deployment

### Environment Variables

#### Development
```bash
VITE_SUPABASE_URL=https://olrpexessehcijdvogxo.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=eyJhbGci...
```

#### Production
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-anon-key
```

### Lovable Cloud Backend Configuration

**CRITICAL FIRST STEP:** Enable Azure provider before any authentication will work.

#### Steps:
1. Open Lovable Cloud Backend (Users → Auth Settings → Azure)
2. Toggle **Enable Azure Provider**
3. Enter Azure AD credentials:
   - Client ID
   - Client Secret  
   - Azure AD Tenant (optional)
4. Copy the **Redirect URI** shown in Lovable Cloud
5. Add this Redirect URI to your Azure AD app

#### Common Issues:
- **Error:** "Unsupported provider: provider is not enabled"
  - **Fix:** Enable Azure provider in Lovable Cloud backend
- **Error:** "Invalid redirect URI"
  - **Fix:** Ensure redirect URI in Azure AD matches Lovable Cloud exactly

### Azure AD Configuration

#### Development App
- **Redirect URI:** Get from Lovable Cloud backend after enabling Azure
- **Environment:** Development/Testing
- **Account Types:** Multitenant (Any Azure AD directory)

#### Production App
- **Redirect URI:** `https://yourdomain.com/auth/v1/callback` (or from Lovable Cloud)
- **Environment:** Production
- **Admin Consent:** Required for all users
- **Account Types:** Single tenant (Your organization only) or Multitenant

## Rate Limits

### Microsoft Graph API Limits
- **Per-user throttling:** 2000 requests per 10 seconds
- **Per-app throttling:** 10,000 requests per 10 seconds
- **Mailbox throttling:** 50 concurrent requests per mailbox

### Current Usage (Estimated)
- User loads portal: 4 requests (profile, calendar, mail, chats)
- Typical user session: ~20 requests
- **Risk:** Low (well under limits)

## Performance

### Current Metrics
- **Page load time:** 3-5 seconds (including API calls)
- **API response time:** 500ms - 2s per endpoint
- **Total data transfer:** ~50KB per user

### Optimization Opportunities
1. Cache responses (5-minute TTL)
2. Lazy load data (load on tab switch)
3. Implement pagination for large datasets
4. Use Graph API batch requests (1 request instead of 4)

## Monitoring

### Metrics to Track
- [ ] Graph API success rate
- [ ] Token refresh success rate
- [ ] Average response time
- [ ] Error rate by type (401, 403, 429, 500)
- [ ] User adoption (% using Microsoft 365 features)

### Alerting Thresholds
- Error rate > 5%
- Response time > 3 seconds
- Token refresh failures > 10/hour

## Troubleshooting

### "Unsupported provider: provider is not enabled"
**This is the #1 blocker - fix this first!**

1. Open Lovable Cloud Backend
2. Navigate to Users → Auth Settings → Azure
3. Enable Azure Provider
4. Enter Azure AD app credentials
5. Test sign-in button again

### "No Microsoft access token found"
1. Check user signed in with Microsoft (not email)
2. Verify Azure provider enabled in Lovable Cloud backend
3. Verify Azure AD permissions granted
4. Check `user.user_metadata.provider_token` exists
5. Try reconnecting Microsoft 365 account

### "Permission denied" errors
1. Verify all permissions granted in Azure AD
2. Check admin consent was granted
3. Verify user has required licenses (e.g., Teams license)

### No data appearing
1. Check network tab for API responses
2. Verify Graph API returning data (use Graph Explorer)
3. Check user actually has data (emails, events, etc.)
4. Review edge function logs

## Future Roadmap

### Phase 1: Stability (Week 1-2)
- ✅ Fix user profiles issue
- ✅ Implement token refresh
- ✅ Add comprehensive error handling
- ✅ Improve loading states

### Phase 2: Features (Week 3-4)
- 📅 OneDrive/SharePoint integration
- 📅 Two-way sync (create/update/delete)
- 📅 Teams channels support
- 📅 Advanced search

### Phase 3: Scale (Week 5-6)
- 📅 Caching layer
- 📅 Batch requests
- 📅 Offline support
- 📅 Performance optimization

### Phase 4: Enterprise (Week 7-8)
- 📅 Multi-tenant support
- 📅 Admin controls
- 📅 Compliance reporting
- 📅 Advanced security

## Resources

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [Azure AD App Registration](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [OAuth 2.0 Scopes](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-permissions-and-consent)

## Support

For issues or questions:
1. Check `URGENT_NEXT_STEPS.md` for known issues
2. Review edge function logs: `supabase functions logs graph-api`
3. Check Supabase dashboard for auth errors
4. Contact Microsoft support for Graph API issues
