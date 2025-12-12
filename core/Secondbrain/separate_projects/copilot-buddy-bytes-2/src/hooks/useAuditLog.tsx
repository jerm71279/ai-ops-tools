import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

interface AuditLogEntry {
  action_type: string;
  system_name: string;
  action_details: Record<string, any>;
  compliance_tags?: string[];
}

export const useAuditLog = () => {
  const { toast } = useToast();

  const logAction = async (entry: AuditLogEntry) => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        console.error('No authenticated user for audit log');
        return;
      }

      const { data: profile } = await supabase
        .from('user_profiles')
        .select('customer_id')
        .eq('user_id', user.id)
        .maybeSingle();

      if (!profile?.customer_id) {
        console.error('No customer profile found for audit log');
        return;
      }

      const { error } = await supabase
        .from('audit_logs')
        .insert({
          user_id: user.id,
          customer_id: profile.customer_id,
          action_type: entry.action_type,
          system_name: entry.system_name,
          action_details: entry.action_details,
          compliance_tags: entry.compliance_tags || ['general'],
          timestamp: new Date().toISOString()
        });

      if (error) {
        console.error('Error logging audit entry:', error);
        throw error;
      }

      console.log(`✅ Audit logged: ${entry.action_type} on ${entry.system_name}`);
    } catch (error) {
      console.error('Failed to log audit entry:', error);
      // Don't block the main operation if audit logging fails
    }
  };

  const logPrivilegedAccess = async (
    system: string,
    action: string,
    details: Record<string, any>
  ) => {
    await logAction({
      action_type: `privileged_${action}`,
      system_name: system,
      action_details: {
        ...details,
        privileged: true,
        timestamp: new Date().toISOString()
      },
      compliance_tags: ['privileged_access', 'rmm', system.toLowerCase()]
    });
  };

  return { logAction, logPrivilegedAccess };
};
