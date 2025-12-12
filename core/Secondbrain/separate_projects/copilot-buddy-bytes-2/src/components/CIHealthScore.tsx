import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Activity, 
  RefreshCw, 
  TrendingUp, 
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock
} from "lucide-react";
import { toast } from "sonner";

interface HealthMetric {
  health_score: number;
  uptime_percentage?: number;
  alert_count?: number;
  critical_alerts?: number;
  relationship_health?: number;
  compliance_score?: number;
  calculated_at: string;
}

interface CIHealthScoreProps {
  ciId: string;
  customerId: string;
}

const CIHealthScore = ({ ciId, customerId }: CIHealthScoreProps) => {
  const [health, setHealth] = useState<HealthMetric | null>(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    loadHealthMetrics();
  }, [ciId]);

  const loadHealthMetrics = async () => {
    try {
      const { data, error } = await supabase
        .from("ci_health_metrics")
        .select("*")
        .eq("ci_id", ciId)
        .order("calculated_at", { ascending: false })
        .limit(1)
        .maybeSingle();

      if (error) throw error;
      
      if (data) {
        setHealth(data);
      } else {
        // Calculate health if no metrics exist
        await calculateHealth();
      }
    } catch (error) {
      console.error("Error loading health metrics:", error);
      toast.error("Failed to load health metrics");
    } finally {
      setLoading(false);
    }
  };

  const calculateHealth = async () => {
    try {
      setCalculating(true);
      
      // Call the health calculation function
      const { data: healthScore, error: funcError } = await supabase
        .rpc("calculate_ci_health", { ci_id_param: ciId });

      if (funcError) throw funcError;

      // Insert new health metric
      const { data: newMetric, error: insertError } = await supabase
        .from("ci_health_metrics")
        .insert({
          ci_id: ciId,
          customer_id: customerId,
          health_score: healthScore,
          calculated_at: new Date().toISOString(),
        })
        .select()
        .single();

      if (insertError) throw insertError;

      setHealth(newMetric);
      toast.success("Health score calculated");
    } catch (error) {
      console.error("Error calculating health:", error);
      toast.error("Failed to calculate health score");
    } finally {
      setCalculating(false);
    }
  };

  const getHealthStatus = (score: number) => {
    if (score >= 80) return { label: "Excellent", color: "text-green-600", variant: "default" as const };
    if (score >= 60) return { label: "Good", color: "text-blue-600", variant: "secondary" as const };
    if (score >= 40) return { label: "Fair", color: "text-yellow-600", variant: "outline" as const };
    return { label: "Poor", color: "text-red-600", variant: "destructive" as const };
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Health Score</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const status = health ? getHealthStatus(health.health_score) : null;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>CI Health Score</CardTitle>
            <CardDescription>
              Overall health and performance metrics
            </CardDescription>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={calculateHealth}
            disabled={calculating}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${calculating ? "animate-spin" : ""}`} />
            Recalculate
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {health ? (
          <div className="space-y-6">
            {/* Overall Score */}
            <div className="text-center">
              <div className="flex items-center justify-center gap-3 mb-2">
                <Activity className="h-8 w-8 text-primary" />
                <div className={`text-5xl font-bold ${status?.color}`}>
                  {health.health_score}
                </div>
              </div>
              <Badge variant={status?.variant}>{status?.label}</Badge>
              <Progress value={health.health_score} className="mt-4 h-3" />
            </div>

            {/* Detailed Metrics */}
            <div className="grid grid-cols-2 gap-4">
              {health.uptime_percentage !== null && health.uptime_percentage !== undefined && (
                <div className="flex items-center justify-between p-3 bg-accent/10 rounded-lg">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium">Uptime</span>
                  </div>
                  <span className="font-bold">{health.uptime_percentage}%</span>
                </div>
              )}

              {health.alert_count !== null && health.alert_count !== undefined && (
                <div className="flex items-center justify-between p-3 bg-accent/10 rounded-lg">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-yellow-600" />
                    <span className="text-sm font-medium">Alerts</span>
                  </div>
                  <span className="font-bold">{health.alert_count}</span>
                </div>
              )}

              {health.critical_alerts !== null && health.critical_alerts !== undefined && (
                <div className="flex items-center justify-between p-3 bg-accent/10 rounded-lg">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <span className="text-sm font-medium">Critical</span>
                  </div>
                  <span className="font-bold text-red-600">{health.critical_alerts}</span>
                </div>
              )}

              {health.compliance_score !== null && health.compliance_score !== undefined && (
                <div className="flex items-center justify-between p-3 bg-accent/10 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium">Compliance</span>
                  </div>
                  <span className="font-bold">{health.compliance_score}%</span>
                </div>
              )}
            </div>

            {/* Last Calculated */}
            <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              Last calculated: {new Date(health.calculated_at).toLocaleString()}
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <Activity className="h-12 w-12 mx-auto text-muted-foreground mb-4 opacity-50" />
            <p className="text-muted-foreground mb-4">No health metrics available</p>
            <Button onClick={calculateHealth} disabled={calculating}>
              <RefreshCw className={`h-4 w-4 mr-2 ${calculating ? "animate-spin" : ""}`} />
              Calculate Health Score
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CIHealthScore;
