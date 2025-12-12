import { Link, useLocation, useNavigate } from "react-router-dom";
import { 
  Settings, 
  Shield, 
  TrendingUp, 
  DollarSign, 
  Users, 
  BarChart3,
  ArrowLeft,
  ChevronDown,
  Search
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";
import { useEffect, useState, useRef } from "react";
import { supabase } from "@/integrations/supabase/client";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { GlobalSearch } from "@/components/GlobalSearch";

// Portals are the main navigation items (non-dashboard pages) with optional children
interface Portal {
  name: string;
  path: string;
  children?: { name: string; path: string; }[];
}

// Categories organize dashboards by theme
interface Category {
  name: string;
  icon: any;
  dashboards: { name: string; path: string; }[];
}

const portals: Portal[] = [
  {
    name: "Employee Portal",
    path: "/portal",
    children: [
      { name: "Employees", path: "/employees" },
      { name: "Departments", path: "/departments" },
      { name: "Leave Requests", path: "/leave-management" },
      { name: "Time Tracking", path: "/time-tracking" },
    ],
  },
  {
    name: "Client Portal",
    path: "/client-portal",
  },
  {
    name: "Operations Portal",
    path: "/dashboard/operations",
    children: [
      { name: "CMDB", path: "/cmdb" },
      { name: "Add CMDB Item", path: "/cmdb/add" },
      { name: "Edit CMDB Item", path: "/cmdb/edit" },
      { name: "CMDB Item Detail", path: "/cmdb/item" },
      { name: "Change Management", path: "/change-management" },
      { name: "New Change", path: "/change/new" },
      { name: "Change Details", path: "/change/details" },
      { name: "Incidents", path: "/incidents" },
      { name: "Network Monitoring", path: "/network-monitoring" },
      { name: "New Network Device", path: "/network/device/new" },
      { name: "SLA Management", path: "/sla-management" },
      { name: "Client Onboarding", path: "/onboarding" },
      { name: "New Client", path: "/onboarding/new" },
      { name: "Onboarding Templates", path: "/onboarding/templates" },
    ],
  },
  {
    name: "Admin Portal",
    path: "/admin",
    children: [
      { name: "Applications", path: "/admin/applications" },
      { name: "Products", path: "/admin/products" },
      { name: "MCP Servers", path: "/mcp-servers" },
      { name: "RBAC", path: "/rbac" },
      { name: "Privileged Access", path: "/audit/privileged-access" },
      { name: "Customers", path: "/customers" },
    ],
  },
  {
    name: "Integrations Portal",
    path: "/integrations",
    children: [
      { name: "NinjaOne", path: "/ninjaone" },
      { name: "CIPP", path: "/cipp" },
    ],
  },
  {
    name: "Compliance Portal",
    path: "/compliance",
    children: [
      { name: "Audit Reports", path: "/compliance/audit-reports" },
      { name: "Frameworks", path: "/compliance/frameworks" },
      { name: "Evidence Upload", path: "/compliance/evidence" },
      { name: "Remediation Rules", path: "/remediation-rules" },
    ],
  },
  {
    name: "Sales Portal",
    path: "/sales-portal",
    children: [
      { name: "Leads", path: "/leads" },
      { name: "Opportunities", path: "/opportunities" },
      { name: "Quotes", path: "/quotes" },
      { name: "Contracts", path: "/contracts" },
      { name: "Projects", path: "/projects" },
    ],
  },
  {
    name: "Finance Portal",
    path: "/budgets",
    children: [
      { name: "Invoices", path: "/invoices" },
      { name: "Expenses", path: "/expenses" },
      { name: "Purchase Orders", path: "/purchase-orders" },
      { name: "Asset Financials", path: "/asset-financials" },
      { name: "Financial Reports", path: "/financial-reports" },
      { name: "Vendors", path: "/vendors" },
      { name: "Inventory", path: "/inventory" },
      { name: "Warehouses", path: "/warehouses" },
    ],
  },
  {
    name: "Analytics Portal",
    path: "/analytics",
    children: [
      { name: "Data Flows", path: "/data-flows" },
      { name: "Predictive Insights", path: "/predictive-insights" },
      { name: "Custom Reports", path: "/custom-reports" },
    ],
  },
  {
    name: "Automation Portal",
    path: "/workflow-automation",
    children: [
      { name: "Workflow Builder", path: "/workflow-builder" },
      { name: "Workflow Orchestration", path: "/workflow-orchestration" },
      { name: "Visual Builder", path: "/workflows/visual-build" },
      { name: "Workflow Intelligence", path: "/workflow-intelligence" },
      { name: "Intelligent Assistant", path: "/intelligent-assistant" },
    ],
  },
  {
    name: "Knowledge Portal",
    path: "/knowledge-base",
    children: [
      { name: "Articles", path: "/knowledge-base" },
      { name: "Upload", path: "/knowledge-base/upload" },
    ],
  },
];

const categories: Category[] = [
  {
    name: "IT Services",
    icon: Settings,
    dashboards: [
      { name: "Operations", path: "/dashboard/operations" },
      { name: "IT", path: "/dashboard/it" },
    ],
  },
  {
    name: "Compliance & Security",
    icon: Shield,
    dashboards: [
      { name: "Compliance", path: "/dashboard/compliance" },
      { name: "SOC", path: "/dashboard/soc" },
    ],
  },
  {
    name: "Business & Sales",
    icon: TrendingUp,
    dashboards: [
      { name: "Sales", path: "/dashboard/sales" },
    ],
  },
  {
    name: "Finance",
    icon: DollarSign,
    dashboards: [
      { name: "Finance", path: "/dashboard/finance" },
    ],
  },
  {
    name: "HR & People",
    icon: Users,
    dashboards: [
      { name: "HR", path: "/dashboard/hr" },
      { name: "Employee Onboarding", path: "/hr/employee-onboarding" },
    ],
  },
  {
    name: "Analytics & Automation",
    icon: BarChart3,
    dashboards: [
      { name: "Executive", path: "/dashboard/executive" },
    ],
  },
];

export default function DashboardPortalLanes() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentPath = location.pathname;
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [enabledPortals, setEnabledPortals] = useState<string[]>([]);
  const [enabledModules, setEnabledModules] = useState<Record<string, boolean>>({});
  const [openPortals, setOpenPortals] = useState<{ [key: string]: boolean }>(() => 
    portals.reduce((acc, p) => ({ ...acc, [p.path]: false }), {})
  );
  const [openCategories, setOpenCategories] = useState<{ [key: string]: boolean }>(() =>
    categories.reduce((acc, c) => ({ ...acc, [c.name]: false }), {})
  );
  const lanesRef = useRef<HTMLDivElement>(null);
  const [searchOpen, setSearchOpen] = useState(false);

  const hideOnRoutes = ['/', '/auth', '/demo', '/integrations', '/developers', '/architecture-diagram'];
  const shouldHide = !isLoggedIn || hideOnRoutes.includes(currentPath);

  // Map portal paths to slugs for filtering
  const portalSlugMap: Record<string, string> = {
    '/portal': 'employee',
    '/client-portal': 'client',
    '/dashboard/operations': 'operations',
    '/admin': 'admin',
    '/integrations': 'integrations',
    '/compliance': 'compliance',
    '/analytics': 'analytics',
    '/data-flow': 'data_flow',
  };

  // Map category names to module slugs
  const categorySlugMap: Record<string, string> = {
    'IT Services': 'it_services',
    'Compliance & Security': 'compliance_security',
    'Business & Sales': 'sales_marketing',
    'Finance': 'finance',
    'HR & People': 'hr',
    'Analytics & Automation': 'executive',
  };

  useEffect(() => {
    const loadSettings = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", session.user.id)
        .single();

      if (!profile?.customer_id) return;

      const { data: customization } = await supabase
        .from("customer_customizations")
        .select("enabled_portals, enabled_modules")
        .eq("customer_id", profile.customer_id)
        .maybeSingle();

      if (customization) {
        const portals = customization.enabled_portals 
          ? (customization.enabled_portals as any[]).filter((p): p is string => typeof p === 'string')
          : [];
        const modules = customization.enabled_modules && typeof customization.enabled_modules === 'object'
          ? customization.enabled_modules as Record<string, boolean>
          : {};
        
        setEnabledPortals(portals);
        setEnabledModules(modules);
      }
    };

    loadSettings();
  }, []);

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setIsLoggedIn(!!session);
    };

    checkAuth();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(() => {
      checkAuth();
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (shouldHide) return;

    const updateOffset = () => {
      if (!lanesRef.current) return;
      const height = lanesRef.current.offsetHeight;
      const safeExtra = 12;
      document.documentElement.style.setProperty('--lanes-height', `${height}px`);
      document.documentElement.style.setProperty('--lanes-bottom', `${height + safeExtra}px`);
    };

    const id = window.requestAnimationFrame(updateOffset);
    window.addEventListener('resize', updateOffset);
    const ro = new ResizeObserver(updateOffset);
    if (lanesRef.current) {
      ro.observe(lanesRef.current);
    }

    return () => {
      window.cancelAnimationFrame(id);
      window.removeEventListener('resize', updateOffset);
      ro.disconnect();
    };
  }, [shouldHide]);

  if (shouldHide) {
    return null;
  }

  const togglePortal = (path: string) => {
    const isCurrentlyOpen = openPortals[path];
    // Close all portals and categories
    setOpenPortals(portals.reduce((acc, p) => ({ ...acc, [p.path]: false }), {}));
    setOpenCategories(categories.reduce((acc, c) => ({ ...acc, [c.name]: false }), {}));
    // Open this one if it was closed
    if (!isCurrentlyOpen) {
      setOpenPortals(prev => ({ ...prev, [path]: true }));
    }
  };

  const toggleCategory = (name: string) => {
    const isCurrentlyOpen = openCategories[name];
    // Close all portals and categories
    setOpenPortals(portals.reduce((acc, p) => ({ ...acc, [p.path]: false }), {}));
    setOpenCategories(categories.reduce((acc, c) => ({ ...acc, [c.name]: false }), {}));
    // Open this one if it was closed
    if (!isCurrentlyOpen) {
      setOpenCategories(prev => ({ ...prev, [name]: true }));
    }
  };

  const closeAll = () => {
    setOpenPortals(portals.reduce((acc, p) => ({ ...acc, [p.path]: false }), {}));
    setOpenCategories(categories.reduce((acc, c) => ({ ...acc, [c.name]: false }), {}));
  };

  // Calculate grid columns based on item count (minimum space for 4 items)
  const getGridColumns = (itemCount: number): string => {
    if (itemCount <= 4) return "grid-cols-1 sm:grid-cols-2";
    if (itemCount <= 8) return "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3";
    return "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4";
  };

  // Check if current page is a main portal/dashboard page
  const allPages = [
    ...portals.map(p => p.path),
    ...portals.flatMap(p => p.children?.map(c => c.path) || []),
    ...categories.flatMap(c => c.dashboards.map(d => d.path)),
  ];
  const isMainPage = allPages.some((path) => currentPath === path);

  // Filter portals and categories based on customer settings
  const filteredPortals = enabledPortals.length > 0 
    ? portals.filter(portal => {
        const slug = portalSlugMap[portal.path];
        return !slug || enabledPortals.includes(slug);
      })
    : portals;

  const filteredCategories = Object.keys(enabledModules).length > 0
    ? categories.filter(category => {
        const slug = categorySlugMap[category.name];
        return !slug || enabledModules[slug] !== false;
      })
    : categories;

  return (
    <div ref={lanesRef} className="fixed top-0 left-0 right-0 z-[9999] w-full isolate overflow-visible bg-background/95 backdrop-blur-sm border-b border-border shadow-md">
      {/* Row 1: Portals with dropdowns */}
      <div className="border-b border-border">
        <div className="container mx-auto px-4 py-2">
          <div className="relative overflow-x-auto overflow-y-visible">
            <div className="flex gap-2 pb-2 min-w-max">
              {filteredPortals.map((portal) => {
                const isActive = currentPath === portal.path || 
                  (portal.children && portal.children.some(child => currentPath.startsWith(child.path)));
                const isOpen = openPortals[portal.path];

                return (
                  <div key={portal.path} className="relative inline-block">
                    {portal.children && portal.children.length > 0 ? (
                      <Collapsible open={isOpen} onOpenChange={() => togglePortal(portal.path)}>
                        <div className="flex items-center gap-1">
                          <Link
                            to={portal.path}
                            className={cn(
                              "inline-flex items-center px-4 py-2 text-sm font-medium rounded-md transition-all",
                              isActive
                                ? "bg-primary text-primary-foreground shadow-sm"
                                : "bg-muted/30 text-foreground hover:bg-muted/50"
                            )}
                          >
                            {portal.name}
                          </Link>
                          <CollapsibleTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              className={cn(
                                "h-8 w-8 p-0 transition-transform",
                                isOpen && "rotate-180"
                              )}
                            >
                              <ChevronDown className="h-3 w-3" />
                            </Button>
                          </CollapsibleTrigger>
                        </div>
                        <CollapsibleContent className="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0">
                          {isOpen && (
                            <>
                              <div 
                                className="fixed inset-0 bg-background/60 backdrop-blur-sm z-[10000]" 
                                onClick={closeAll}
                              />
                              <div 
                                className="fixed left-1/2 -translate-x-1/2 z-[10001] bg-popover border border-border rounded-lg shadow-2xl p-6 max-w-4xl w-[90vw]"
                                style={{ top: 'var(--lanes-bottom)' }}
                              >
                                <div className={cn("grid gap-3", getGridColumns(portal.children.length))}>
                                  {portal.children.map((child) => (
                                    <Link
                                      key={child.path}
                                      to={child.path}
                                      onClick={closeAll}
                                      className={cn(
                                        "block px-4 py-3 text-sm rounded-md transition-colors",
                                        currentPath === child.path
                                          ? "bg-primary text-primary-foreground font-medium"
                                          : "text-foreground hover:bg-muted"
                                      )}
                                    >
                                      {child.name}
                                    </Link>
                                  ))}
                                </div>
                              </div>
                            </>
                          )}
                        </CollapsibleContent>
                      </Collapsible>
                    ) : (
                      <Link
                        to={portal.path}
                        className={cn(
                          "inline-flex items-center px-4 py-2 text-sm font-medium rounded-md transition-all",
                          isActive
                            ? "bg-primary text-primary-foreground shadow-sm"
                            : "bg-muted/30 text-foreground hover:bg-muted/50"
                        )}
                      >
                        {portal.name}
                      </Link>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Categories with Dashboard dropdowns */}
      <div className="border-b border-border">
        <div className="container mx-auto px-4 py-2">
          <div className="relative overflow-x-auto overflow-y-visible">
            <div className="flex gap-2 pb-2 min-w-max">
              {filteredCategories.map((category) => {
                const CategoryIcon = category.icon;
                const isActive = category.dashboards.some((d) => currentPath === d.path || currentPath.startsWith(d.path + '/'));
                const isOpen = openCategories[category.name];

                return (
                  <div key={category.name} className="relative inline-block">
                    <Collapsible open={isOpen} onOpenChange={() => toggleCategory(category.name)}>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          className={cn(
                            "inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-md transition-all",
                            isActive
                              ? "bg-primary/10 text-primary"
                              : "bg-muted/30 text-muted-foreground hover:bg-muted/50"
                          )}
                          onClick={() => toggleCategory(category.name)}
                        >
                          <CategoryIcon className="h-4 w-4" />
                          {category.name}
                        </Button>
                        <CollapsibleTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className={cn(
                              "h-8 w-8 p-0 transition-transform",
                              isOpen && "rotate-180"
                            )}
                          >
                            <ChevronDown className="h-3 w-3" />
                          </Button>
                        </CollapsibleTrigger>
                      </div>
                      <CollapsibleContent className="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0">
                        {isOpen && (
                          <>
                            <div 
                              className="fixed inset-0 bg-background/60 backdrop-blur-sm z-[10000]" 
                              onClick={closeAll}
                            />
                            <div 
                              className="fixed left-1/2 -translate-x-1/2 z-[10001] bg-popover border border-border rounded-lg shadow-2xl p-6 max-w-4xl w-[90vw]"
                              style={{ top: 'var(--lanes-bottom)' }}
                            >
                              <div className={cn("grid gap-3", getGridColumns(category.dashboards.length))}>
                                {category.dashboards.map((dashboard) => (
                                  <Link
                                    key={dashboard.path}
                                    to={dashboard.path}
                                    onClick={closeAll}
                                    className={cn(
                                      "block px-4 py-3 text-sm rounded-md transition-colors",
                                      currentPath === dashboard.path
                                        ? "bg-primary text-primary-foreground font-medium"
                                        : "text-foreground hover:bg-muted"
                                    )}
                                  >
                                    {dashboard.name}
                                  </Link>
                                ))}
                              </div>
                            </div>
                          </>
                        )}
                      </CollapsibleContent>
                    </Collapsible>
                  </div>
                );
              })}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSearchOpen(true)}
                className="gap-2 px-4 py-2 text-sm font-medium"
              >
                <Search className="h-4 w-4" />
                Search
                <kbd className="ml-2 pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                  <span className="text-xs">⌘</span>K
                </kbd>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Back Button - Only show on non-main pages */}
      {!isMainPage && (
        <div className="border-t border-border">
          <div className="container mx-auto px-4 py-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate(-1)}
              className="gap-2 h-8"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
          </div>
        </div>
      )}

      <GlobalSearch open={searchOpen} onOpenChange={setSearchOpen} />
    </div>
  );
}
