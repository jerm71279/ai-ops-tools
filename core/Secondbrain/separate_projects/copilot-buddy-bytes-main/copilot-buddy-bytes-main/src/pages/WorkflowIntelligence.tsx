import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Brain, TrendingUp, AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const WorkflowIntelligence = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [queryType, setQueryType] = useState<'analyze' | 'workflows' | 'compliance' | 'anomalies'>('analyze');
  const [timeframe, setTimeframe] = useState('7d');
  const { toast } = useToast();

  const suggestedQueries = {
    analyze: [
      "Summarize workflow performance over the past week",
      "What compliance gaps have been detected?",
      "Which workflows are failing most frequently?",
      "Show me trends in change request success rates"
    ],
    workflows: [
      "Which workflows need optimization?",
      "Compare workflow execution times",
      "Show workflow dependency analysis"
    ],
    compliance: [
      "Check SOC2 compliance status",
      "List all ISO 27001 clause violations",
      "Generate HIPAA audit trail summary"
    ],
    anomalies: [
      "What unusual patterns have been detected?",
      "Show critical anomalies requiring attention",
      "Analyze security-related anomalies"
    ]
  };

  const handleQuery = async () => {
    if (!query.trim()) {
      toast({
        title: "Query Required",
        description: "Please enter a query to analyze",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    setResponse("");

    try {
      const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
      const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

      const response = await fetch(
        `${SUPABASE_URL}/functions/v1/workflow-intelligence`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          },
          body: JSON.stringify({
            query,
            type: queryType,
            timeframe
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get response');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response stream');
      }

      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process complete lines
        const lines = buffer.split('\n');
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6).trim();
            
            if (jsonStr === '[DONE]') continue;

            try {
              const data = JSON.parse(jsonStr);
              const content = data.choices?.[0]?.delta?.content;
              
              if (content) {
                setResponse(prev => prev + content);
              }
            } catch (e) {
              console.error('Error parsing SSE:', e);
            }
          }
        }
      }

      toast({
        title: "Analysis Complete",
        description: "Workflow intelligence query processed successfully",
      });

    } catch (error) {
      console.error('Query error:', error);
      toast({
        title: "Query Failed",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Brain className="h-8 w-8 text-primary" />
              Workflow Intelligence
            </h1>
            <p className="text-muted-foreground mt-1">
              AI-powered analysis of business processes, compliance, and outcomes
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="outline" className="gap-1">
              <CheckCircle2 className="h-3 w-3" />
              Lovable AI
            </Badge>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="px-3 py-2 rounded-md border bg-background"
            >
              <option value="1d">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>
        </div>

        <Tabs value={queryType} onValueChange={(v) => setQueryType(v as any)}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="analyze" className="gap-2">
              <TrendingUp className="h-4 w-4" />
              Full Analysis
            </TabsTrigger>
            <TabsTrigger value="workflows" className="gap-2">
              <Brain className="h-4 w-4" />
              Workflows
            </TabsTrigger>
            <TabsTrigger value="compliance" className="gap-2">
              <CheckCircle2 className="h-4 w-4" />
              Compliance
            </TabsTrigger>
            <TabsTrigger value="anomalies" className="gap-2">
              <AlertTriangle className="h-4 w-4" />
              Anomalies
            </TabsTrigger>
          </TabsList>

          <TabsContent value={queryType} className="space-y-4">
            <Card className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Ask About Your Business Processes
                  </label>
                  <Textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={`e.g., "${suggestedQueries[queryType][0]}"`}
                    className="min-h-[100px]"
                    disabled={isLoading}
                  />
                </div>

                <div className="flex flex-wrap gap-2">
                  <span className="text-sm text-muted-foreground">Suggestions:</span>
                  {suggestedQueries[queryType].map((suggestion, i) => (
                    <Button
                      key={i}
                      variant="outline"
                      size="sm"
                      onClick={() => setQuery(suggestion)}
                      disabled={isLoading}
                    >
                      {suggestion}
                    </Button>
                  ))}
                </div>

                <Button 
                  onClick={handleQuery} 
                  disabled={isLoading || !query.trim()}
                  className="w-full"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Brain className="mr-2 h-4 w-4" />
                      Analyze
                    </>
                  )}
                </Button>
              </div>
            </Card>

            {response && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Intelligence Report
                </h3>
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <pre className="whitespace-pre-wrap font-sans text-sm">
                    {response}
                  </pre>
                </div>
              </Card>
            )}
          </TabsContent>
        </Tabs>

        <Card className="p-6 bg-muted/50">
          <h3 className="font-semibold mb-2">💡 What This Does</h3>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• <strong>Queries your live database</strong> - Analyzes actual workflow executions, audit logs, change requests</li>
            <li>• <strong>Maintains clause linkages</strong> - Connects findings to compliance frameworks (ISO, SOC2, HIPAA)</li>
            <li>• <strong>Streams insights in real-time</strong> - See analysis as it's generated</li>
            <li>• <strong>Learns from outcomes</strong> - Each query improves future recommendations</li>
            <li>• <strong>Native integration</strong> - No external tools, uses your Lovable AI</li>
          </ul>
        </Card>
      </div>
    </div>
  );
};

export default WorkflowIntelligence;
