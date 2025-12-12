import { useEffect, useCallback } from 'react';
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

interface TaskDetectionParams {
  actionType: string;
  systemName: string;
  context?: Record<string, any>;
}

export const useRepetitiveTaskDetection = () => {
  const { toast } = useToast();

  const detectTask = useCallback(async ({ actionType, systemName, context }: TaskDetectionParams) => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        console.log('No authenticated user for task detection');
        return;
      }

      console.log(`Detecting task: ${actionType} on ${systemName}`);

      const { data, error } = await supabase.functions.invoke('repetitive-task-detector', {
        body: {
          userId: user.id,
          actionType,
          systemName,
          context
        }
      });

      if (error) {
        console.error('Error detecting task:', error);
        return;
      }

      console.log('Task detection result:', data);

      // If we should suggest automation, trigger the suggester
      if (data?.shouldSuggest) {
        // Query to find the task that needs a suggestion
        const { data: tasks } = await supabase
          .from('task_repetition_analysis')
          .select('id')
          .eq('user_id', user.id)
          .eq('action_type', actionType)
          .eq('system_name', systemName)
          .eq('status', 'detected')
          .order('repetition_count', { ascending: false })
          .limit(1);

        if (tasks && tasks.length > 0) {
          // Trigger automation suggester
          const { data: suggestion, error: suggestionError } = await supabase.functions.invoke('automation-suggester', {
            body: { taskId: tasks[0].id }
          });

          if (suggestionError) {
            console.error('Error generating suggestion:', suggestionError);
            return;
          }

          // Show notification
          toast({
            title: "🤖 Automation Opportunity Detected!",
            description: `We've noticed you've repeated this task ${data.repetitionCount} times. Check your suggestions for automation ideas.`,
            duration: 8000,
          });
        }
      }
    } catch (error) {
      console.error('Failed to detect task:', error);
    }
  }, [toast]);

  return { detectTask };
};
