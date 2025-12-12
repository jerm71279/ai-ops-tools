# OberaConnect Developer Onboarding

Welcome to the OberaConnect development team! This guide will help you get up to speed quickly on the platform architecture, codebase, and development workflows.

## 🎯 What You're Building

OberaConnect is a **multi-tenant SaaS platform** for MSPs (Managed Service Providers) that provides:
- **Department-specific dashboards** for different roles (Compliance, IT, HR, Finance, Sales, etc.)
- **Customer customization** (per-tenant branding, features, layouts)
- **AI-powered assistants** for each department
- **Integration management** with billing, security, RMM, and compliance systems

## 📅 Your First Week

### Day 1: Environment Setup

#### 1. Clone and Run
```bash
# Clone the repository
git clone <YOUR_GIT_URL>
cd oberaconnect-platform

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

#### 2. Create a Test Account
1. Navigate to `/auth` in your browser
2. Create an account with any email (auto-confirmed in dev)
3. You'll be assigned to a department automatically
4. Explore the dashboard for your assigned role

#### 3. Explore the Codebase
- Read [README.md](./README.md) for project overview
- Review [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Open `src/App.tsx` to see routing structure

### Day 2-3: Understanding the Architecture

#### Key Concepts to Master

**1. Customer Isolation**
Every customer is isolated via Row Level Security (RLS):
```typescript
// Example: Fetching customer-specific data
const { data } = await supabase
  .from('integrations')
  .select('*')
  .eq('customer_id', customerId);  // RLS enforces access automatically
```

**2. Department-Based Routing**
Each role has its own dashboard:
- `/dashboard/compliance` → ComplianceDashboard.tsx
- `/dashboard/it` → ITDashboard.tsx
- `/dashboard/hr` → HRDashboard.tsx
- etc.

**3. Customer Customization**
Branding applied via CSS variables:
```typescript
// Hook loads customization from database
const { customization } = useCustomerCustomization(customerId);

// Applies to CSS variables automatically
root.style.setProperty('--primary', customization.primary_color);
```

#### Hands-On Exercise
**Task**: Add a new metric card to the HR Dashboard
1. Open `src/pages/HRDashboard.tsx`
2. Find the stats grid (around line 84-140)
3. Add a new `Card` component with a sample metric
4. Test in preview environment

### Day 4-5: Making Your First Contribution

#### Choose a Starter Task
Pick one of these beginner-friendly tasks:

**Option A: Add a New Integration**
1. Open `src/components/Integrations.tsx`
2. Add a new integration to the appropriate category
3. Update `src/pages/IntegrationsPage.tsx` with integration details
4. Test that it displays correctly

**Option B: Customize Dashboard Styling**
1. Review current design tokens in `src/index.css`
2. Adjust color values to improve contrast
3. Test in both light and dark mode
4. Ensure accessibility (WCAG AA compliance)

**Option C: Add a Dashboard Widget**
1. Choose a department dashboard
2. Create a new widget component in `src/components/`
3. Import and render it in the dashboard
4. Add sample data fetch from Supabase

## 🧩 Codebase Tour

### Frontend Structure

```
src/
├── components/
│   ├── ui/                      # shadcn base components (DON'T edit directly)
│   ├── CallToAction.tsx         # Landing page CTA
│   ├── Features.tsx             # Feature showcase
│   ├── Hero.tsx                 # Landing hero section
│   ├── Integrations.tsx         # Integration grid
│   ├── DepartmentAIAssistant.tsx # AI chat interface
│   ├── MCPServerStatus.tsx      # MCP server health display
│   └── Navigation.tsx           # Global nav bar
│
├── pages/
│   ├── Index.tsx                # Landing page (/)
│   ├── Auth.tsx                 # Login/Signup (/auth)
│   ├── DemoSelector.tsx         # Demo mode entry
│   ├── IntegrationsPage.tsx     # Integration details
│   ├── AdminDashboard.tsx       # Admin panel (/admin)
│   └── [Department]Dashboard.tsx # Role-specific dashboards
│
├── hooks/
│   ├── useCustomerCustomization.tsx  # Load/apply customer branding
│   └── useDemoMode.tsx               # Detect preview mode
│
├── integrations/
│   └── supabase/
│       ├── client.ts            # Supabase client (auto-generated)
│       └── types.ts             # DB types (auto-generated)
│
└── lib/
    └── utils.ts                 # Helper functions (cn for classnames)
```

### Backend Structure

```
supabase/
├── functions/
│   ├── department-assistant/    # AI assistant edge function
│   │   └── index.ts
│   └── mcp-server/              # MCP server integration
│       └── index.ts
│
└── migrations/                  # Database schema changes
    └── [timestamp]_*.sql        # Auto-generated migration files
```

## 🔧 Common Development Tasks

### Adding a New Dashboard

**Step 1**: Create the component
```typescript
// src/pages/MyNewDashboard.tsx
import { useEffect, useState } from 'react';
import { supabase } from '@/integrations/supabase/client';

const MyNewDashboard = () => {
  const [stats, setStats] = useState({});
  
  useEffect(() => {
    // Check auth and fetch data
    checkAccess();
  }, []);

  return (
    <div>
      {/* Dashboard UI */}
    </div>
  );
};

export default MyNewDashboard;
```

**Step 2**: Add route to App.tsx
```typescript
import MyNewDashboard from "./pages/MyNewDashboard";

// In Routes:
<Route path="/dashboard/mynew" element={<MyNewDashboard />} />
```

**Step 3**: Update Navigation (if needed)

### Fetching Data from Supabase

**Basic Query**
```typescript
const { data, error } = await supabase
  .from('table_name')
  .select('*')
  .eq('customer_id', customerId);

if (error) console.error('Error:', error);
else console.log('Data:', data);
```

**With Relationships**
```typescript
const { data } = await supabase
  .from('user_profiles')
  .select(`
    *,
    customers (
      company_name,
      plan
    )
  `)
  .eq('user_id', userId)
  .single();
```

### Calling an Edge Function

```typescript
const { data, error } = await supabase.functions.invoke('department-assistant', {
  body: {
    department: 'compliance',
    message: 'What frameworks are we tracking?',
    customerId: customerId
  }
});
```

### Styling with Design Tokens

**✅ CORRECT** (Uses design system)
```typescript
<div className="bg-background text-foreground border border-border">
  <h2 className="text-primary font-semibold">Title</h2>
  <Button variant="default">Click Me</Button>
</div>
```

**❌ WRONG** (Hardcoded colors)
```typescript
<div className="bg-white text-black border border-gray-200">
  <h2 className="text-blue-600 font-semibold">Title</h2>
</div>
```

## 🗄️ Database Quick Reference

### Key Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `customers` | Customer organizations | company_name, plan, status |
| `user_profiles` | User accounts | user_id, customer_id, department |
| `customer_customizations` | UI branding/features | primary_color, enabled_integrations |
| `integrations` | External systems | system_name, status, config |
| `mcp_servers` | AI server registry | name, url, capabilities |

### Accessing the Database

**Via Lovable Backend UI**:
1. Click "View Backend" in Lovable interface
2. Navigate to Table Editor or SQL Editor
3. Run queries, view data, check RLS policies

**Via Code** (see examples above)

## 🤖 Working with AI Features

### Department AI Assistant

Each dashboard includes a `DepartmentAIAssistant` component:
```typescript
<DepartmentAIAssistant department="compliance" />
```

This connects to the edge function at `supabase/functions/department-assistant/index.ts`.

### Supported AI Models

The platform uses **Lovable AI** (no API keys required):
- `google/gemini-2.5-pro` - Best for complex reasoning
- `google/gemini-2.5-flash` - Balanced performance
- `openai/gpt-5` - High accuracy
- `openai/gpt-5-mini` - Cost-effective

### Adding AI to a New Feature

```typescript
const { data } = await supabase.functions.invoke('department-assistant', {
  body: {
    department: 'your_department',
    message: userMessage,
    context: additionalContext
  }
});
```

## 🔐 Security Best Practices

### 1. Always Use RLS
Every new table MUST have Row Level Security enabled:
```sql
ALTER TABLE my_new_table ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own data"
ON my_new_table FOR SELECT
USING (customer_id = (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));
```

### 2. Never Expose Sensitive Data
- Don't log API keys or secrets
- Don't expose internal IDs in URLs
- Validate all user inputs

### 3. Check Authentication
Every dashboard should verify the user:
```typescript
const { data: { session } } = await supabase.auth.getSession();
if (!session) {
  navigate('/auth');
  return;
}
```

## 🧪 Testing Your Changes

### Manual Testing Checklist
- [ ] Feature works in preview environment
- [ ] Tested with different user roles/departments
- [ ] Tested with demo mode
- [ ] UI looks good on mobile and desktop
- [ ] No console errors
- [ ] Data saves correctly to database

### Using Debug Tools

**Console Logs**
```typescript
console.log('Debug info:', { variable, state });
```
View in browser DevTools Console

**Network Requests**
Open DevTools → Network tab to see API calls

**Database Queries**
Check Supabase logs in backend UI

## 🔄 Git Workflow

### Branch Naming
```
feature/add-hr-metrics
bugfix/dashboard-loading-issue
refactor/integration-components
```

### Commit Messages
Follow conventional commits:
```
feat: add new metric to HR dashboard
fix: resolve customer customization loading bug
docs: update onboarding guide with testing section
refactor: extract integration card to separate component
```

### Making Changes
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes, test thoroughly

# Commit with clear message
git add .
git commit -m "feat: add your feature"

# Push to GitHub
git push origin feature/your-feature
```

Changes automatically sync to Lovable!

## 📚 Additional Resources

### Documentation
- [Architecture Guide](./ARCHITECTURE.md) - Deep dive into system design
- [Module Structure](./MODULE_STRUCTURE.md) - Component organization
- [API Reference](./API_REFERENCE.md) - Edge functions and endpoints
- [Developer Handoff](./DEVELOPER_HANDOFF.md) - Knowledge transfer protocol

### External Docs
- [React](https://react.dev/) - Frontend framework
- [TypeScript](https://www.typescriptlang.org/docs/) - Language
- [Tailwind CSS](https://tailwindcss.com/docs) - Styling
- [shadcn/ui](https://ui.shadcn.com/) - Component library
- [Supabase](https://supabase.com/docs) - Backend platform

### Getting Help

**Have Questions?**
1. Check the documentation files in this repo
2. Review similar code in existing components
3. Ask your team lead or senior developer
4. Search Lovable Discord community

## 🎓 Learning Path

### Week 1: Foundation
- ✅ Environment setup
- ✅ Understand architecture
- ✅ Make first contribution

### Week 2: Feature Development
- Add a new dashboard widget
- Create a custom integration
- Work with Supabase queries

### Week 3: Advanced Features
- Implement AI assistant integration
- Work with customer customization
- Add RLS policies to new table

### Week 4: Full Autonomy
- Tackle medium-complexity features
- Participate in code reviews
- Help onboard next new developer

## 🎯 Success Criteria

You're ready for independent work when you can:
- [ ] Create a new dashboard component
- [ ] Fetch and display data from Supabase
- [ ] Apply customer customization to UI
- [ ] Add a new integration to the platform
- [ ] Write RLS policies for new tables
- [ ] Call an edge function from frontend
- [ ] Debug using console logs and network inspector

---

**Welcome to the team!** Remember: this platform is designed for continuity. Your contributions are documented and traceable, ensuring your work outlives your tenure and benefits future developers.