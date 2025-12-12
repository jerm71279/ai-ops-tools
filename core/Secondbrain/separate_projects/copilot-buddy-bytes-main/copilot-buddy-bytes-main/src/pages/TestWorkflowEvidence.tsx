import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Play, CheckCircle, AlertCircle } from "lucide-react";

export default function TestWorkflowEvidence() {
  const { toast } = useToast();
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const generateEvidence = async () => {
    setIsGenerating(true);
    setResult(null);

    try {
      console.log('Calling batch-evidence-generator...');
      
      const { data, error } = await supabase.functions.invoke('batch-evidence-generator', {
        body: {}
      });

      if (error) {
        console.error('Error calling function:', error);
        throw error;
      }

      console.log('Function response:', data);
      setResult(data);

      toast({
        title: "Success",
        description: `Generated evidence for ${data.evidence_generated} workflows`,
      });
    } catch (error) {
      console.error('Error generating evidence:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate evidence",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8">
        <h1 className="text-3xl font-bold mb-6">Test Workflow Evidence Generation</h1>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Play className="h-5 w-5" />
              Batch Evidence Generator
            </CardTitle>
            <CardDescription>
              Generate evidence files for all completed workflow executions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={generateEvidence} 
              disabled={isGenerating}
              size="lg"
            >
              {isGenerating ? "Generating..." : "Generate Evidence for All Workflows"}
            </Button>

            {result && (
              <div className="mt-4 p-4 bg-muted rounded-lg space-y-2">
                <div className="flex items-center gap-2">
                  {result.errors > 0 ? (
                    <AlertCircle className="h-5 w-5 text-yellow-500" />
                  ) : (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  )}
                  <h3 className="font-semibold">Results</h3>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Total Executions</p>
                    <p className="text-2xl font-bold">{result.total_executions}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Evidence Generated</p>
                    <p className="text-2xl font-bold text-green-600">{result.evidence_generated}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Errors</p>
                    <p className="text-2xl font-bold text-yellow-600">{result.errors}</p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
