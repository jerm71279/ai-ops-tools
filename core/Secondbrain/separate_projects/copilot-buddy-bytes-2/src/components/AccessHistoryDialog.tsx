import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Clock, Search, Filter, Download } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

interface AccessHistoryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const AccessHistoryDialog = ({ open, onOpenChange }: AccessHistoryDialogProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [customerId, setCustomerId] = useState<string | null>(null);

  useEffect(() => {
    const fetchCustomerId = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        const { data: profile } = await supabase
          .from('user_profiles')
          .select('customer_id')
          .eq('user_id', user.id)
          .single();
        
        if (profile?.customer_id) {
          setCustomerId(profile.customer_id);
        }
      }
    };
    
    if (open) {
      fetchCustomerId();
    }
  }, [open]);

  const { data: auditLogs, isLoading } = useQuery({
    queryKey: ['audit-logs', customerId, filterType],
    enabled: !!customerId && open,
    queryFn: async () => {
      let query = supabase
        .from('audit_logs')
        .select('*')
        .eq('customer_id', customerId)
        .order('timestamp', { ascending: false })
        .limit(100);

      if (filterType !== 'all') {
        query = query.eq('action_type', filterType);
      }

      const { data, error } = await query;
      if (error) throw error;
      return data;
    },
  });

  const filteredLogs = auditLogs?.filter(log => {
    if (!searchQuery) return true;
    const searchLower = searchQuery.toLowerCase();
    return (
      log.system_name?.toLowerCase().includes(searchLower) ||
      log.action_type?.toLowerCase().includes(searchLower) ||
      JSON.stringify(log.action_details)?.toLowerCase().includes(searchLower)
    );
  });

  const actionTypes = [...new Set(auditLogs?.map(log => log.action_type) || [])];

  const handleExportLogs = () => {
    if (!filteredLogs || filteredLogs.length === 0) {
      toast.error("No logs to export");
      return;
    }

    const csvContent = [
      ["Timestamp", "System", "Action Type", "Details"],
      ...filteredLogs.map(log => [
        format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss'),
        log.system_name,
        log.action_type,
        JSON.stringify(log.action_details || {})
      ])
    ].map(row => row.join(",")).join("\n");

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `access-history-${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("Access history exported");
  };

  const getActionColor = (actionType: string) => {
    const colors: Record<string, string> = {
      'login': 'bg-green-500/10 text-green-500 border-green-500/20',
      'logout': 'bg-gray-500/10 text-gray-500 border-gray-500/20',
      'create': 'bg-blue-500/10 text-blue-500 border-blue-500/20',
      'update': 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
      'delete': 'bg-red-500/10 text-red-500 border-red-500/20',
      'view': 'bg-purple-500/10 text-purple-500 border-purple-500/20',
      'credential_access': 'bg-orange-500/10 text-orange-500 border-orange-500/20',
    };
    return colors[actionType.toLowerCase()] || 'bg-muted text-muted-foreground';
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Access History
          </DialogTitle>
          <DialogDescription>
            View detailed audit logs of all activities in your organization
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Search and Filter Bar */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Button variant="outline" size="icon" onClick={handleExportLogs}>
              <Download className="h-4 w-4" />
            </Button>
          </div>

          {/* Filters */}
          <Tabs value={filterType} onValueChange={setFilterType}>
            <TabsList className="w-full justify-start overflow-x-auto">
              <TabsTrigger value="all">All</TabsTrigger>
              {actionTypes.slice(0, 6).map(type => (
                <TabsTrigger key={type} value={type}>
                  {type.replace(/_/g, ' ')}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>

          {/* Logs List */}
          <ScrollArea className="h-[400px] rounded-md border">
            {isLoading ? (
              <div className="flex items-center justify-center h-full">
                <p className="text-muted-foreground">Loading access history...</p>
              </div>
            ) : filteredLogs && filteredLogs.length > 0 ? (
              <div className="p-4 space-y-3">
                {filteredLogs.map((log) => (
                  <div
                    key={log.id}
                    className="p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className={getActionColor(log.action_type)}>
                            {log.action_type.replace(/_/g, ' ')}
                          </Badge>
                          <span className="font-medium">{log.system_name}</span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {format(new Date(log.timestamp), 'PPpp')}
                        </p>
                        {log.action_details && Object.keys(log.action_details).length > 0 && (
                          <details className="mt-2">
                            <summary className="text-sm cursor-pointer text-primary hover:underline">
                              View details
                            </summary>
                            <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-x-auto">
                              {JSON.stringify(log.action_details, null, 2)}
                            </pre>
                          </details>
                        )}
                        {log.compliance_tags && log.compliance_tags.length > 0 && (
                          <div className="flex gap-1 mt-2">
                            {log.compliance_tags.map((tag, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-2">
                  <Clock className="h-12 w-12 mx-auto text-muted-foreground" />
                  <p className="text-muted-foreground">No access history found</p>
                  <p className="text-sm text-muted-foreground">
                    {searchQuery ? "Try adjusting your search" : "Activity will appear here"}
                  </p>
                </div>
              </div>
            )}
          </ScrollArea>

          {/* Stats Footer */}
          {filteredLogs && filteredLogs.length > 0 && (
            <div className="flex items-center justify-between text-sm text-muted-foreground pt-2 border-t">
              <span>
                Showing {filteredLogs.length} {filteredLogs.length === 1 ? 'log' : 'logs'}
              </span>
              <span>
                Last 100 entries
              </span>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
