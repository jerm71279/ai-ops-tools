import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRepetitiveTaskDetection } from "@/hooks/useRepetitiveTaskDetection";
import { Info } from "lucide-react";

export const RepetitiveTaskTester = () => {
  const [clickCount, setClickCount] = useState(0);
  const { detectTask } = useRepetitiveTaskDetection();

  const handleTestClick = async () => {
    setClickCount(prev => prev + 1);
    
    await detectTask({
      actionType: "create_invoice",
      systemName: "Finance Portal",
      context: {
        clickNumber: clickCount + 1,
        timestamp: new Date().toISOString()
      }
    });
  };

  const handleResetClick = async () => {
    setClickCount(prev => prev + 1);
    
    await detectTask({
      actionType: "password_reset",
      systemName: "User Management",
      context: {
        clickNumber: clickCount + 1,
        timestamp: new Date().toISOString()
      }
    });
  };

  return (
    <Card className="border-primary/20">
      <CardHeader>
        <div className="flex items-start gap-2">
          <Info className="h-5 w-5 text-primary mt-0.5" />
          <div>
            <CardTitle>Task Detection Tester</CardTitle>
            <CardDescription>
              Click any button 3 times to trigger automation suggestion
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Button onClick={handleTestClick} variant="default">
            Test: Create Invoice ({clickCount})
          </Button>
          <Button onClick={handleResetClick} variant="secondary">
            Test: Reset Password
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">
          💡 After 3 clicks of the same button, you should see:
          <br />• A toast notification about automation opportunity
          <br />• An AI-generated suggestion card below
        </p>
      </CardContent>
    </Card>
  );
};
