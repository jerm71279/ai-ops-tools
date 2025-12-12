import { useEffect, useState } from 'react';
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Zap, Clock, X, CheckCircle2, TrendingUp } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface WorkflowSuggestion {
  workflowName: string;
  description: string;
  steps: Array<{ order: number; action: string; details: string }>;
  triggerType: string;
  estimatedTimeSavingsMinutes: number;
  implementationDifficulty: string;
  requiredIntegrations: string[];
  confidence: number;
}

interface TaskRepetition {
  id: string;
  action_type: string;
  system_name: string;
  repetition_count: number;
  suggested_workflow: any; // JSON from database
  suggestion_confidence: number;
  status: string;
}

export default function AutomationSuggestions() {
  const { toast } = useToast();
  const [suggestions, setSuggestions] = useState<TaskRepetition[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSuggestions();

    // Subscribe to changes
    const channel = supabase
      .channel('automation_suggestions')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'task_repetition_analysis',
          filter: `status=eq.suggested`
        },
        () => {
          loadSuggestions();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  const loadSuggestions = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase
        .from('task_repetition_analysis')
        .select('*')
        .eq('user_id', user.id)
        .eq('status', 'suggested')
        .order('repetition_count', { ascending: false });

      if (error) throw error;

      setSuggestions(data || []);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const dismissSuggestion = async (id: string) => {
    try {
      const { error } = await supabase
        .from('task_repetition_analysis')
        .update({ status: 'dismissed' })
        .eq('id', id);

      if (error) throw error;

      toast({
        title: "Suggestion dismissed",
        description: "This automation suggestion has been hidden."
      });

      setSuggestions(prev => prev.filter(s => s.id !== id));
    } catch (error) {
      console.error('Error dismissing suggestion:', error);
      toast({
        title: "Error",
        description: "Failed to dismiss suggestion",
        variant: "destructive"
      });
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'hard': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  if (isLoading) {
    return null;
  }

  if (suggestions.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4 mb-6">
      <div className="flex items-center gap-2">
        <Zap className="h-5 w-5 text-yellow-500" />
        <h3 className="text-lg font-semibold">Automation Suggestions</h3>
        <Badge variant="secondary">{suggestions.length}</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {suggestions.map((suggestion) => (
          <Card key={suggestion.id} className="border-yellow-500/50">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Zap className="h-4 w-4 text-yellow-500" />
                    {suggestion.suggested_workflow.workflowName}
                  </CardTitle>
                  <CardDescription className="mt-1">
                    {suggestion.suggested_workflow.description}
                  </CardDescription>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => dismissSuggestion(suggestion.id)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <TrendingUp className="h-4 w-4 text-blue-500" />
                  <span className="text-muted-foreground">Repeated {suggestion.repetition_count}x</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4 text-green-500" />
                  <span className="text-muted-foreground">Save ~{suggestion.suggested_workflow.estimatedTimeSavingsMinutes} min</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {suggestion.suggested_workflow.triggerType}
                </Badge>
                <Badge 
                  variant="outline" 
                  className={`text-xs ${getDifficultyColor(suggestion.suggested_workflow.implementationDifficulty)} text-white`}
                >
                  {suggestion.suggested_workflow.implementationDifficulty}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {Math.round(suggestion.suggested_workflow.confidence)}% confident
                </Badge>
              </div>

              <div className="pt-2 border-t">
                <p className="text-xs font-medium mb-2">Workflow Steps:</p>
                <ol className="text-xs space-y-1 text-muted-foreground">
                  {suggestion.suggested_workflow.steps.slice(0, 3).map((step, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle2 className="h-3 w-3 mt-0.5 flex-shrink-0 text-green-500" />
                      <span>{step.action}</span>
                    </li>
                  ))}
                  {suggestion.suggested_workflow.steps.length > 3 && (
                    <li className="text-xs text-muted-foreground/60">
                      +{suggestion.suggested_workflow.steps.length - 3} more steps
                    </li>
                  )}
                </ol>
              </div>

              <div className="flex gap-2 pt-2">
                <Button className="flex-1" size="sm">
                  Create Workflow
                </Button>
                <Button variant="outline" size="sm">
                  View Details
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
