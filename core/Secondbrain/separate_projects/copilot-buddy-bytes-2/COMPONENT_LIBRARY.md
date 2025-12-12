# OberaConnect Component Library

**Last Updated:** October 9, 2025  
**Component Count**: 50+  
**Custom Hooks**: 10+

---

## Table of Contents

1. [Custom Hooks](#custom-hooks)
2. [Shared Components](#shared-components)
3. [Feature Components](#feature-components)
4. [UI Components](#ui-components)
5. [Layout Components](#layout-components)
6. [Integration Components](#integration-components)
7. [Usage Examples](#usage-examples)

---

## Custom Hooks

### Authentication & User Management

#### `useDemoMode`
**Location**: `src/hooks/useDemoMode.tsx`

Detects if the app is running in demo/preview mode.

```typescript
const { isDemoMode } = useDemoMode();
```

**Returns**:
- `isDemoMode: boolean` - True if in demo environment

**Use Cases**:
- Disable destructive actions in demo
- Show demo banners
- Modify behavior for previews

---

#### `useCustomerCustomization`
**Location**: `src/hooks/useCustomerCustomization.tsx`

Loads and applies customer-specific branding and settings.

```typescript
const { customization, isLoading } = useCustomerCustomization(customerId);
```

**Interface**:
```typescript
interface CustomerCustomization {
  id: string;
  customer_id: string;
  company_logo_url: string | null;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  enabled_integrations: string[];
  enabled_features: string[];
  default_dashboard: string;
  dashboard_layout: Record<string, any>;
  custom_settings: Record<string, any>;
}
```

**Features**:
- Auto-applies CSS variables for theming
- Fetches from `customer_customizations` table
- Handles loading states

---

### Audit & Compliance

#### `useAuditLog`
**Location**: `src/hooks/useAuditLog.tsx`

Centralized audit logging for compliance and security tracking.

```typescript
const { logAction, logPrivilegedAccess } = useAuditLog();

// General audit log
await logAction({
  action_type: 'view_dashboard',
  system_name: 'compliance',
  action_details: { dashboard: 'soc2' },
  compliance_tags: ['soc2']
});

// Privileged access log
await logPrivilegedAccess({
  system_name: 'ninjaone',
  action_type: 'device_access',
  action_details: { device_id: '123' }
});
```

**Use Cases**:
- SOC2/HIPAA compliance auditing
- RMM privileged access tracking
- Security incident investigation

---

### Data Management

#### `useProducts`
**Location**: `src/hooks/useProducts.tsx`

Product catalog management with CRUD operations.

```typescript
const { 
  products, 
  loading, 
  createProduct, 
  updateProduct, 
  deleteProduct, 
  refetch 
} = useProducts();

await createProduct({
  product_name: 'Enterprise Plan',
  base_price: 199.99,
  billing_cycle: 'monthly',
  enabled_features: ['compliance', 'workflows']
});
```

**Interface**:
```typescript
interface Product {
  id: string;
  product_name: string;
  base_price: number;
  billing_cycle: string;
  enabled_features: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

---

#### `useRevioData`
**Location**: `src/hooks/useRevioData.tsx`

Fetch revenue and billing data from Revio integration.

```typescript
const { 
  billingData, 
  isLoading, 
  error, 
  refetch 
} = useRevioData(customerId);
```

---

### Task Automation

#### `useRepetitiveTaskDetection`
**Location**: `src/hooks/useRepetitiveTaskDetection.tsx`

Detects repetitive user actions and suggests automation.

```typescript
const { 
  detectedTasks, 
  suggestions, 
  isLoading 
} = useRepetitiveTaskDetection(customerId);
```

**Features**:
- Real-time task detection
- ML-powered pattern recognition
- Automation suggestions

---

### Mobile Detection

#### `use-mobile`
**Location**: `src/hooks/use-mobile.tsx`

Detects mobile viewport for responsive design.

```typescript
const isMobile = useMobile();
```

---

### Toast Notifications

#### `useToast`
**Location**: `src/hooks/use-toast.ts`

Global toast notification system.

```typescript
const { toast } = useToast();

toast({
  title: "Success",
  description: "Product created successfully",
  variant: "default"
});
```

**Variants**:
- `default` - Standard notification
- `destructive` - Error/warning

---

## Shared Components

### Navigation & Layout

#### `Navigation`
**Location**: `src/components/Navigation.tsx`

Global navigation bar with department dropdowns.

**Features**:
- Department-specific navigation
- Authentication state handling
- Mobile responsive
- Dropdown menus for dashboards

**Dropdowns**:
- Admin Tools
- Compliance
- CMDB & Change
- Workflows
- AI & Knowledge
- Integrations
- Testing

---

#### `DashboardNavigation`
**Location**: `src/components/DashboardNavigation.tsx`

Department dashboard navigation component.

---

#### `Footer`
**Location**: `src/components/Footer.tsx`

Global footer with links and branding.

---

### Dashboard Components

#### `DashboardSettingsMenu`
**Location**: `src/components/DashboardSettingsMenu.tsx`

Quick settings menu for dashboards.

---

#### `DashboardPreview`
**Location**: `src/components/DashboardPreview.tsx`

Preview component for dashboard layouts.

---

#### `ExternalSystemsBar`
**Location**: `src/components/ExternalSystemsBar.tsx`

External system integration status bar.

---

### Employee Portal

#### `AppLauncher`
**Location**: `src/components/AppLauncher.tsx`

Launches applications based on user department.

```typescript
<AppLauncher userDepartment="it" />
```

**Features**:
- Department-based filtering
- Dynamic icon rendering
- Category badges
- Click-to-launch

---

#### `EmployeeToolbar`
**Location**: `src/components/EmployeeToolbar.tsx`

Horizontal toolbar with quick access tools.

---

### Landing Page

#### `Hero`
**Location**: `src/components/Hero.tsx`

Landing page hero section.

---

#### `Features`
**Location**: `src/components/Features.tsx`

Feature showcase section.

---

#### `Integrations`
**Location**: `src/components/Integrations.tsx`

Integration showcase carousel.

---

#### `Testimonials`
**Location**: `src/components/Testimonials.tsx`

Customer testimonials section.

---

#### `Pricing`
**Location**: `src/components/Pricing.tsx`

Pricing tiers display.

---

#### `CaseStudy`
**Location**: `src/components/CaseStudy.tsx`

Case study showcase component.

---

#### `UseCases`
**Location**: `src/components/UseCases.tsx`

Use case examples.

---

#### `CallToAction`
**Location**: `src/components/CallToAction.tsx`

CTA section with signup prompt.

---

## Feature Components

### AI & Intelligence

#### `DepartmentAIAssistant`
**Location**: `src/components/DepartmentAIAssistant.tsx`

Department-specific AI chat assistant.

**Features**:
- Context-aware responses
- Department-specific knowledge
- Conversation history
- Real-time streaming

---

#### `MLIntelligence`
**Location**: `src/components/MLIntelligence.tsx`

Machine learning insights display.

---

#### `AutomationSuggestions`
**Location**: `src/components/AutomationSuggestions.tsx`

AI-powered automation suggestions.

---

### Workflow Components

#### `WorkflowBuilder`
**Location**: `src/components/WorkflowBuilder.tsx`

Visual workflow builder interface.

---

#### `WorkflowExecutionHistory`
**Location**: `src/components/WorkflowExecutionHistory.tsx`

Workflow execution logs and history.

---

#### `WorkflowTriggerManager`
**Location**: `src/components/WorkflowTriggerManager.tsx`

Manage workflow triggers (webhooks, schedules).

---

### MCP Components

#### `MCPServerStatus`
**Location**: `src/components/MCPServerStatus.tsx`

MCP server health status display.

---

#### `MCPServerConfig`
**Location**: `src/components/MCPServerConfig.tsx`

MCP server configuration interface.

---

#### `MCPExecutionLogs`
**Location**: `src/components/MCPExecutionLogs.tsx`

MCP execution log viewer.

---

#### `AIMCPGenerator`
**Location**: `src/components/AIMCPGenerator.tsx`

AI-powered MCP server generator.

---

### CMDB Components

#### `CIHealthScore`
**Location**: `src/components/CIHealthScore.tsx`

Configuration item health score display.

---

#### `CIRelationshipMap`
**Location**: `src/components/CIRelationshipMap.tsx`

Visual CI relationship mapping.

---

#### `CIAuditLog`
**Location**: `src/components/CIAuditLog.tsx`

CI audit log viewer.

---

### Compliance Components

#### `EvidenceUpload`
**Location**: `src/components/EvidenceUpload.tsx`

Compliance evidence file uploader.

---

#### `Frameworks`
**Location**: `src/components/Frameworks.tsx`

Compliance framework display.

---

### Integration Components

#### `Microsoft365Integration`
**Location**: `src/components/Microsoft365Integration.tsx`

Microsoft 365 data integration display.

**Features**:
- Calendar events
- Email insights
- Teams activity
- User data

---

### RBAC Components

#### `RoleManagement`
**Location**: `src/components/rbac/RoleManagement.tsx`

Role creation and editing interface.

---

#### `PermissionManagement`
**Location**: `src/components/rbac/PermissionManagement.tsx`

Permission assignment interface.

---

#### `RoleHierarchy`
**Location**: `src/components/rbac/RoleHierarchy.tsx`

Visual role hierarchy display.

---

#### `RoleTemplates`
**Location**: `src/components/rbac/RoleTemplates.tsx`

Pre-configured role templates.

---

#### `TemporaryPrivileges`
**Location**: `src/components/rbac/TemporaryPrivileges.tsx`

Time-limited privilege grants.

---

#### `PermissionAuditLog`
**Location**: `src/components/rbac/PermissionAuditLog.tsx`

Permission change audit log.

---

#### `AccessHistoryDialog`
**Location**: `src/components/AccessHistoryDialog.tsx`

User access history viewer.

---

### Testing Components

#### `RepetitiveTaskTester`
**Location**: `src/components/RepetitiveTaskTester.tsx`

Repetitive task detection tester.

---

### Utility Components

#### `GlobalSearch`
**Location**: `src/components/GlobalSearch.tsx`

Platform-wide search functionality.

---

#### `FlowDiagram`
**Location**: `src/components/FlowDiagram.tsx`

Visual data flow diagram renderer.

---

#### `ProtectedRoute`
**Location**: `src/components/ProtectedRoute.tsx`

Route protection with authentication check.

```typescript
<Route
  path="/admin"
  element={
    <ProtectedRoute>
      <AdminDashboard />
    </ProtectedRoute>
  }
/>
```

---

## UI Components

All UI components are based on **shadcn/ui** + **Radix UI** primitives.

**Location**: `src/components/ui/`

### Core Components
- `button.tsx` - Button with variants
- `card.tsx` - Card container
- `dialog.tsx` - Modal dialogs
- `dropdown-menu.tsx` - Dropdown menus
- `form.tsx` - Form components
- `input.tsx` - Text inputs
- `select.tsx` - Select dropdowns
- `table.tsx` - Data tables
- `tabs.tsx` - Tab navigation
- `toast.tsx` / `toaster.tsx` / `sonner.tsx` - Notifications
- `tooltip.tsx` - Tooltips

### Advanced Components
- `accordion.tsx` - Collapsible sections
- `alert.tsx` / `alert-dialog.tsx` - Alerts
- `avatar.tsx` - User avatars
- `badge.tsx` - Status badges
- `calendar.tsx` - Date picker
- `carousel.tsx` - Image carousel
- `chart.tsx` - Chart components
- `checkbox.tsx` - Checkboxes
- `collapsible.tsx` - Collapsible content
- `command.tsx` - Command palette
- `context-menu.tsx` - Right-click menus
- `drawer.tsx` - Slide-out drawers
- `hover-card.tsx` - Hover popups
- `menubar.tsx` - Menu bars
- `navigation-menu.tsx` - Navigation
- `pagination.tsx` - Pagination
- `popover.tsx` - Popovers
- `progress.tsx` - Progress bars
- `radio-group.tsx` - Radio buttons
- `scroll-area.tsx` - Scrollable areas
- `separator.tsx` - Dividers
- `sheet.tsx` - Side sheets
- `sidebar.tsx` - Sidebars
- `skeleton.tsx` - Loading skeletons
- `slider.tsx` - Range sliders
- `switch.tsx` - Toggle switches
- `textarea.tsx` - Text areas
- `toggle.tsx` / `toggle-group.tsx` - Toggles

---

## Usage Examples

### Building a Dashboard with AI Assistant

```tsx
import { DepartmentAIAssistant } from '@/components/DepartmentAIAssistant';
import { useCustomerCustomization } from '@/hooks/useCustomerCustomization';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export default function MyDashboard() {
  const { customization, isLoading } = useCustomerCustomization(customerId);

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Dashboard content */}
        </CardContent>
      </Card>

      <DepartmentAIAssistant 
        department="compliance"
        customerId={customerId}
      />
    </div>
  );
}
```

### Audit Logging in Integration

```tsx
import { useAuditLog } from '@/hooks/useAuditLog';

export function NinjaOneDeviceView({ deviceId }: { deviceId: string }) {
  const { logPrivilegedAccess } = useAuditLog();

  const handleViewDevice = async () => {
    // Log the privileged access
    await logPrivilegedAccess({
      system_name: 'ninjaone',
      action_type: 'device_view',
      action_details: {
        device_id: deviceId,
        action: 'viewed device details'
      }
    });

    // ... fetch device data
  };

  return <button onClick={handleViewDevice}>View Device</button>;
}
```

### Product Management

```tsx
import { useProducts } from '@/hooks/useProducts';

export function ProductsAdmin() {
  const { products, loading, createProduct, updateProduct } = useProducts();

  const handleCreate = async () => {
    await createProduct({
      product_name: 'Professional Plan',
      base_price: 99.99,
      billing_cycle: 'monthly',
      enabled_features: ['workflows', 'compliance'],
      is_active: true
    });
  };

  if (loading) return <div>Loading products...</div>;

  return (
    <div>
      {products.map(product => (
        <div key={product.id}>{product.product_name}</div>
      ))}
    </div>
  );
}
```

### Building Protected Routes

```tsx
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Route } from 'react-router-dom';

<Route
  path="/admin/products"
  element={
    <ProtectedRoute>
      <ProductsAdmin />
    </ProtectedRoute>
  }
/>
```

---

## Design Patterns

### 1. Compound Components
Components like `Card` use compound pattern:
```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content</CardContent>
  <CardFooter>Footer</CardFooter>
</Card>
```

### 2. Render Props
AI Assistant uses render props for flexibility:
```tsx
<DepartmentAIAssistant
  department="it"
  renderHeader={() => <CustomHeader />}
/>
```

### 3. Controlled Components
Forms use controlled pattern:
```tsx
const [value, setValue] = useState('');
<Input value={value} onChange={(e) => setValue(e.target.value)} />
```

### 4. Custom Hooks for Logic
Extract business logic into hooks:
```tsx
// ❌ Bad
function Dashboard() {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    // Fetch products logic
  }, []);
}

// ✅ Good
function Dashboard() {
  const { products, loading } = useProducts();
}
```

---

## Styling Guidelines

### 1. Use Design Tokens
```tsx
// ❌ Bad
<div className="text-white bg-black">

// ✅ Good
<div className="text-foreground bg-background">
```

### 2. Semantic Colors
All colors defined in `src/index.css` as HSL tokens:
```css
:root {
  --primary: 263 70% 50%;
  --secondary: 263 70% 40%;
  --accent: 263 70% 60%;
}
```

### 3. Component Variants
Use `class-variance-authority` for variants:
```tsx
const buttonVariants = cva("base-classes", {
  variants: {
    variant: {
      default: "bg-primary text-primary-foreground",
      destructive: "bg-destructive text-destructive-foreground"
    },
    size: {
      default: "h-10 px-4",
      sm: "h-8 px-3"
    }
  }
});
```

---

## Performance Best Practices

### 1. Lazy Load Heavy Components
```tsx
const WorkflowBuilder = lazy(() => import('@/pages/WorkflowBuilder'));
```

### 2. Memoize Expensive Calculations
```tsx
const expensiveValue = useMemo(() => calculateValue(data), [data]);
```

### 3. Use React Query for Data
```tsx
const { data } = useQuery({
  queryKey: ['products'],
  queryFn: fetchProducts
});
```

---

## Testing Components

All components should be testable:
```tsx
import { render, screen } from '@testing-library/react';
import { ProductsAdmin } from './ProductsAdmin';

test('renders products list', () => {
  render(<ProductsAdmin />);
  expect(screen.getByText(/products/i)).toBeInTheDocument();
});
```

---

## Contributing New Components

1. **Location**: Place in appropriate directory
   - Shared: `/components`
   - Feature-specific: `/components/[feature]`
   - UI: `/components/ui`

2. **Naming**: Use PascalCase
   - Component: `MyComponent.tsx`
   - Hook: `useMyHook.tsx`

3. **Documentation**: Add to this file with:
   - Purpose
   - Props interface
   - Usage example
   - Location

4. **TypeScript**: Always use TypeScript
5. **Accessibility**: Follow ARIA guidelines
6. **Styling**: Use design tokens

---

**Last Updated**: October 9, 2025  
**Maintainer**: OberaConnect Development Team
