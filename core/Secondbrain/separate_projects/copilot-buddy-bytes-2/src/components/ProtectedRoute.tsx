import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Loader2 } from "lucide-react";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

const ProtectedRoute = ({ children, requireAdmin = false }: ProtectedRouteProps) => {
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    checkAccess();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(() => {
      checkAccess();
    });

    return () => subscription.unsubscribe();
  }, []);

  const checkAccess = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      setIsAuthenticated(!!session);

      if (session && requireAdmin) {
        // Check for admin role
        const { data: roles } = await supabase
          .from("user_roles")
          .select("role_id, roles(name)")
          .eq("user_id", session.user.id);
        
        let hasAdmin = roles?.some((ur: any) => 
          ur.roles?.name === 'Super Admin' || ur.roles?.name === 'Admin'
        );

        // Fallback to RPC function
        if (!hasAdmin) {
          const { data: rpcHasAdmin } = await supabase.rpc('has_role', {
            _user_id: session.user.id,
            _role: 'admin'
          });
          hasAdmin = !!rpcHasAdmin;
        }

        setIsAdmin(!!hasAdmin);
      } else {
        setIsAdmin(true); // If not requiring admin, consider authorized
      }
    } catch (error) {
      console.error("Error checking access:", error);
      setIsAuthenticated(false);
      setIsAdmin(false);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">Access Denied</h1>
          <p className="text-muted-foreground">You don't have permission to access this page.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
