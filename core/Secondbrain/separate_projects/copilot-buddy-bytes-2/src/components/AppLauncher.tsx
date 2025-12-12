import { useEffect, useState } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Loader2, ExternalLink } from 'lucide-react';
import * as Icons from 'lucide-react';

interface Application {
  id: string;
  name: string;
  description: string | null;
  icon_name: string;
  app_url: string | null;
  category: string;
  auth_type: string;
}

interface AppLauncherProps {
  userDepartment?: string | null;
}

export const AppLauncher = ({ userDepartment }: AppLauncherProps) => {
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadApplications();
  }, [userDepartment]);

  const loadApplications = async () => {
    try {
      setLoading(true);

      // Get all active applications
      const { data: allApps, error: appsError } = await supabase
        .from('applications')
        .select('*')
        .eq('is_active', true)
        .order('display_order');

      if (appsError) throw appsError;

      // Filter by department access if user has a department
      if (userDepartment && allApps) {
        const { data: accessData, error: accessError } = await supabase
          .from('application_access')
          .select('application_id')
          .eq('department', userDepartment);

        if (accessError) throw accessError;

        const accessibleAppIds = new Set(accessData?.map(a => a.application_id) || []);
        const filteredApps = allApps.filter(app => accessibleAppIds.has(app.id));
        setApps(filteredApps);
      } else {
        setApps(allApps || []);
      }
    } catch (error) {
      console.error('Error loading applications:', error);
      toast({
        title: 'Error',
        description: 'Failed to load applications',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAppClick = (app: Application) => {
    if (app.app_url) {
      if (app.app_url.startsWith('http')) {
        window.open(app.app_url, '_blank');
      } else {
        window.location.href = app.app_url;
      }
    }
  };

  const getIconComponent = (iconName: string) => {
    const IconComponent = (Icons as any)[iconName] || Icons.Package;
    return <IconComponent className="h-8 w-8" />;
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      communication: 'bg-blue-500/10 text-blue-700 dark:text-blue-400',
      productivity: 'bg-green-500/10 text-green-700 dark:text-green-400',
      security: 'bg-red-500/10 text-red-700 dark:text-red-400',
      analytics: 'bg-purple-500/10 text-purple-700 dark:text-purple-400',
      finance: 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400',
    };
    return colors[category] || 'bg-gray-500/10 text-gray-700 dark:text-gray-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (apps.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">No applications available for your department.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {apps.map((app) => (
        <Card
          key={app.id}
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => handleAppClick(app)}
        >
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                {getIconComponent(app.icon_name)}
                <div>
                  <CardTitle className="text-lg">{app.name}</CardTitle>
                  <Badge className={getCategoryColor(app.category)} variant="secondary">
                    {app.category}
                  </Badge>
                </div>
              </div>
              {app.app_url && <ExternalLink className="h-4 w-4 text-muted-foreground" />}
            </div>
          </CardHeader>
          {app.description && (
            <CardContent>
              <CardDescription>{app.description}</CardDescription>
            </CardContent>
          )}
        </Card>
      ))}
    </div>
  );
};
