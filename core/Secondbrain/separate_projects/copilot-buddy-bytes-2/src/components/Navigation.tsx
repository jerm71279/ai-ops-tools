import { Button } from "@/components/ui/button";
import { Menu, LogOut, Brain, Search, LayoutDashboard, Globe } from "lucide-react";
import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { GlobalSearch } from "./GlobalSearch";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import oberaLogo from "@/assets/obera-logo-cropped.png";

const Navigation = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const isLandingPage = location.pathname === "/" || location.pathname === "/auth";

  useEffect(() => {
    checkAuth();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(() => {
      checkAuth();
    });

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      subscription.unsubscribe();
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const checkAuth = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    setIsLoggedIn(!!session);

    if (session) {
      const { data: roles } = await supabase
        .from("user_roles")
        .select("role_id, roles(name)")
        .eq("user_id", session.user.id);
      
      let hasAdmin = roles?.some((ur: any) => ur.roles?.name === 'Super Admin' || ur.roles?.name === 'Admin');

      if (!hasAdmin) {
        const { data: rpcHasAdmin } = await supabase.rpc('has_role', {
          _user_id: session.user.id,
          _role: 'admin'
        });
        hasAdmin = !!rpcHasAdmin;
      }

      setIsAdmin(!!hasAdmin);
    } else {
      setIsAdmin(false);
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setIsMenuOpen(false);
    navigate("/");
  };

  const scrollToSection = (sectionId: string) => {
    if (window.location.pathname !== '/') {
      navigate('/');
      setTimeout(() => {
        const element = document.getElementById(sectionId);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    } else {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
    setIsMenuOpen(false);
  };

  return (
    <>
      <GlobalSearch open={searchOpen} onOpenChange={setSearchOpen} />
      <nav className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-lg border-b border-border">
        {/* Logo Banner - Full Width Edge to Edge */}
        <div className="w-full bg-gradient-to-r from-background via-accent/5 to-background border-b border-border/50">
          <Link 
            to="/"
            className="block hover:opacity-90 transition-opacity"
          >
            <img 
              src={oberaLogo} 
              alt="OberaConnect Logo" 
              className="w-full h-auto object-contain"
              style={{ minHeight: '40px', maxHeight: '60px', display: 'block' }}
            />
          </Link>
        </div>

        {/* Navigation Menu */}
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-14">
            {/* Mobile Menu Button - Only on Landing/Auth Pages */}
            {isLandingPage && (
              <button
                className="md:hidden p-2 hover:bg-accent/10 rounded-lg transition-colors"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
              >
                <Menu className="h-6 w-6" />
              </button>
            )}

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center justify-center flex-1 gap-6">
              {isLoggedIn && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSearchOpen(true)}
                  className="gap-2"
                >
                  <Search className="h-4 w-4" />
                  <span className="text-muted-foreground">Search</span>
                  <kbd className="pointer-events-none hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
                    <span className="text-xs">⌘</span>K
                  </kbd>
                </Button>
              )}
              <button 
                onClick={() => scrollToSection('features')}
                className="text-sm font-medium hover:text-accent transition-colors"
              >
                Features
              </button>
              <button 
                onClick={() => scrollToSection('frameworks')}
                className="text-sm font-medium hover:text-accent transition-colors"
              >
                Frameworks
              </button>
              <Link 
                to="/integrations"
                className="text-sm font-medium hover:text-accent transition-colors"
              >
                Integrations
              </Link>
              <Link 
                to="/developers"
                className="text-sm font-medium hover:text-accent transition-colors"
              >
                Developers
              </Link>
              
              {/* Portals Dropdown - Always visible */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="text-sm font-medium hover:text-accent transition-colors flex items-center gap-1">
                    <Globe className="h-4 w-4" />
                    Portals
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-56">
                  <DropdownMenuLabel>Portals</DropdownMenuLabel>
                  <ScrollArea className="h-[250px]">
                    <DropdownMenuItem asChild>
                      <Link to="/portal" className="w-full cursor-pointer">Employee Portal</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/analytics" className="w-full cursor-pointer">Analytics Portal</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/client-portal" className="w-full cursor-pointer">Client Portal</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/compliance" className="w-full cursor-pointer">Compliance Portal</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/data-flows" className="w-full cursor-pointer">Data Flow Portal</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/rbac" className="w-full cursor-pointer">RBAC Portal</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/sales-portal" className="w-full cursor-pointer">Sales Portal</Link>
                    </DropdownMenuItem>
                  </ScrollArea>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Dashboards Dropdown - Always visible */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="text-sm font-medium hover:text-accent transition-colors flex items-center gap-1">
                    <LayoutDashboard className="h-4 w-4" />
                    Dashboards
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-56">
                  <DropdownMenuLabel>Dashboards</DropdownMenuLabel>
                  <ScrollArea className="h-[300px]">
                    <DropdownMenuItem asChild>
                      <Link to="/admin" className="w-full cursor-pointer">Admin Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/cmdb" className="w-full cursor-pointer">CMDB Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/cipp" className="w-full cursor-pointer">CIPP Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard/compliance" className="w-full cursor-pointer">Compliance Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard/executive" className="w-full cursor-pointer">Executive Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard/finance" className="w-full cursor-pointer">Finance Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard/hr" className="w-full cursor-pointer">HR Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard/it" className="w-full cursor-pointer">IT Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/mcp-servers" className="w-full cursor-pointer">MCP Server Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/onboarding" className="w-full cursor-pointer">Onboarding Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard/operations" className="w-full cursor-pointer">Operations Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard/sales" className="w-full cursor-pointer">Sales Dashboard</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard/soc" className="w-full cursor-pointer">SOC Dashboard</Link>
                    </DropdownMenuItem>
                  </ScrollArea>
                </DropdownMenuContent>
              </DropdownMenu>
              
              {isLoggedIn && (
                <>
                  <Link 
                    to="/knowledge"
                    className="text-sm font-medium hover:text-accent transition-colors"
                  >
                    Knowledge
                  </Link>
                  <Link 
                    to="/compliance"
                    className="text-sm font-medium hover:text-accent transition-colors"
                  >
                    Compliance
                  </Link>
                  <Link 
                    to="/change-management"
                    className="text-sm font-medium hover:text-accent transition-colors"
                  >
                    Change Management
                  </Link>
                  <Link 
                    to="/workflows"
                    className="text-sm font-medium hover:text-accent transition-colors"
                  >
                    Workflows
                  </Link>
                  <Link
                    to="/ninjaone"
                    className="text-sm font-medium hover:text-accent transition-colors"
                  >
                    Monitoring
                  </Link>
                  <Link
                    to="/network-monitoring"
                    className="text-sm font-medium hover:text-accent transition-colors"
                  >
                    Network
                  </Link>
                  <Link
                    to="/data-flows"
                    className="text-sm font-medium hover:text-accent transition-colors"
                  >
                    Data Flows
                  </Link>
                  <Link
                    to="/incidents"
                    className="text-sm font-medium hover:text-accent transition-colors"
                  >
                    Incidents
                  </Link>
                  <Link
                    to="/client-portal"
                    className="text-sm font-medium hover:text-accent transition-colors"
                  >
                    Client Portal
                  </Link>
                  <Link
                    to="/reports/builder"
                    className="text-sm font-medium hover:text-accent transition-colors"
                  >
                    Reports
                  </Link>
                </>
              )}
              <button
                onClick={() => scrollToSection('case-study')}
                className="text-sm font-medium hover:text-accent transition-colors"
              >
                Demo
              </button>
              <button 
                onClick={() => scrollToSection('pricing')}
                className="text-sm font-medium hover:text-accent transition-colors"
              >
                Pricing
              </button>
            </div>

            {/* CTA Buttons */}
            <div className="hidden md:flex items-center gap-3 ml-auto">
              {isLoggedIn ? (
                <>
                  <Link to="/portal">
                    <Button variant="ghost" size="sm">
                      Portal
                    </Button>
                  </Link>
                  {isAdmin && (
                    <Link to="/admin">
                      <Button variant="ghost" size="sm">
                        Admin
                      </Button>
                    </Link>
                  )}
                  <Link to="/intelligent-assistant">
                    <Button variant="ghost" size="sm">
                      <Brain className="h-4 w-4 mr-2" />
                      AI Assistant
                    </Button>
                  </Link>
                  <Button variant="ghost" size="sm" onClick={handleSignOut}>
                    <LogOut className="h-4 w-4 mr-2" />
                    Sign Out
                  </Button>
                </>
              ) : (
                <>
                  <Link to="/demo">
                    <Button variant="ghost" size="sm">
                      View Demos
                    </Button>
                  </Link>
                  <Link to="/auth">
                    <Button variant="ghost" size="sm">
                      Client Login
                    </Button>
                  </Link>
                  <Link to="/auth">
                    <Button variant="hero" size="sm">
                      Get Started
                    </Button>
                  </Link>
              </>
            )}
          </div>
        </div>
      </div>

        {/* Mobile Dropdown Menu - Only on Landing/Auth Pages */}
        {isLandingPage && isMenuOpen && (
          <div className="md:hidden absolute left-4 top-full mt-2 w-64 bg-background/100 border border-border rounded-lg shadow-xl z-[100] py-2">
            <div className="flex flex-col">
              <button 
                onClick={() => scrollToSection('features')}
                className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 text-left rounded"
              >
                Features
              </button>
              <button 
                onClick={() => scrollToSection('frameworks')}
                className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 text-left rounded"
              >
                Frameworks
              </button>
              <Link 
                to="/integrations"
                className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 rounded"
                onClick={() => setIsMenuOpen(false)}
              >
                Integrations
              </Link>
              <Link 
                to="/developers"
                className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 rounded"
                onClick={() => setIsMenuOpen(false)}
              >
                Developers
              </Link>
              {isLoggedIn && (
                <>
                  <div className="border-b border-border pb-2 mb-2">
                    <div className="text-xs font-semibold text-muted-foreground px-4 py-2">DASHBOARDS</div>
                    <ScrollArea className="h-[200px]">
                      <Link to="/admin" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Admin Dashboard
                      </Link>
                      <Link to="/cmdb" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        CMDB Dashboard
                      </Link>
                      <Link to="/cipp" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        CIPP Dashboard
                      </Link>
                      <Link to="/dashboard/compliance" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Compliance Dashboard
                      </Link>
                      <Link to="/dashboard/executive" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Executive Dashboard
                      </Link>
                      <Link to="/dashboard/finance" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Finance Dashboard
                      </Link>
                      <Link to="/dashboard/hr" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        HR Dashboard
                      </Link>
                      <Link to="/dashboard/it" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        IT Dashboard
                      </Link>
                      <Link to="/mcp-servers" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        MCP Server Dashboard
                      </Link>
                      <Link to="/onboarding" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Onboarding Dashboard
                      </Link>
                      <Link to="/dashboard/operations" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Operations Dashboard
                      </Link>
                      <Link to="/dashboard/sales" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Sales Dashboard
                      </Link>
                      <Link to="/dashboard/soc" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        SOC Dashboard
                      </Link>
                    </ScrollArea>
                  </div>
                  <div className="border-b border-border pb-2 mb-2">
                    <div className="text-xs font-semibold text-muted-foreground px-4 py-2">PORTALS</div>
                    <ScrollArea className="h-[150px]">
                      <Link to="/portal" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Employee Portal
                      </Link>
                      <Link to="/analytics" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Analytics Portal
                      </Link>
                      <Link to="/client-portal" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Client Portal
                      </Link>
                      <Link to="/compliance" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Compliance Portal
                      </Link>
                      <Link to="/data-flows" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Data Flow Portal
                      </Link>
                      <Link to="/rbac" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        RBAC Portal
                      </Link>
                      <Link to="/sales-portal" className="text-sm font-medium hover:bg-accent/10 transition-colors py-2 px-4 rounded block" onClick={() => setIsMenuOpen(false)}>
                        Sales Portal
                      </Link>
                    </ScrollArea>
                  </div>
                  <Link 
                    to="/knowledge"
                    className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 rounded"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Knowledge
                  </Link>
                  <Link 
                    to="/change-management"
                    className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 rounded"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Change Management
                  </Link>
                  <Link 
                    to="/workflows"
                    className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 rounded"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Workflows
                  </Link>
                  <Link
                    to="/ninjaone"
                    className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 rounded"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Monitoring
                  </Link>
                  <Link
                    to="/network-monitoring"
                    className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 rounded"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Network
                  </Link>
                  <Link
                    to="/incidents"
                    className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 rounded"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Incidents
                  </Link>
                  <Link
                    to="/reports/builder"
                    className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 rounded"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Reports
                  </Link>
                </>
              )}
              <button
                onClick={() => scrollToSection('case-study')}
                className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 text-left rounded"
              >
                Demo
              </button>
              <button 
                onClick={() => scrollToSection('pricing')}
                className="text-sm font-medium hover:bg-accent/10 transition-colors py-3 px-4 text-left rounded"
              >
                Pricing
              </button>
              <div className="border-t border-border mt-2 pt-2">
                {isLoggedIn ? (
                  <>
                    <Link to="/portal" onClick={() => setIsMenuOpen(false)}>
                      <Button variant="ghost" size="sm" className="justify-start w-full">
                        Portal
                      </Button>
                    </Link>
                    {isAdmin && (
                      <Link to="/admin" onClick={() => setIsMenuOpen(false)}>
                        <Button variant="ghost" size="sm" className="justify-start w-full">
                          Admin
                        </Button>
                      </Link>
                    )}
                    <Link to="/intelligent-assistant" onClick={() => setIsMenuOpen(false)}>
                      <Button variant="ghost" size="sm" className="justify-start w-full">
                        <Brain className="h-4 w-4 mr-2" />
                        AI Assistant
                      </Button>
                    </Link>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="justify-start w-full"
                      onClick={handleSignOut}
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      Sign Out
                    </Button>
                  </>
                ) : (
                  <>
                    <Link to="/demo" onClick={() => setIsMenuOpen(false)}>
                      <Button variant="ghost" size="sm" className="justify-start w-full">
                        View Demos
                      </Button>
                    </Link>
                    <Link to="/auth" onClick={() => setIsMenuOpen(false)}>
                      <Button variant="ghost" size="sm" className="justify-start w-full">
                        Client Login
                      </Button>
                    </Link>
                    <Link to="/auth" onClick={() => setIsMenuOpen(false)}>
                      <Button variant="hero" size="sm" className="w-full">
                        Get Started
                      </Button>
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>
    </>
  );
};

export default Navigation;
