import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  RefreshCw,
  Sparkles,
  Ticket,
  ExternalLink,
} from "lucide-react";
import { toast } from "sonner";

const ChangeManagementDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [change, setChange] = useState<any>(null);
  const [impactAnalysis, setImpactAnalysis] = useState<any>(null);
  const [creatingTicket, setCreatingTicket] = useState(false);
  const [syncingTicket, setSyncingTicket] = useState(false);

  useEffect(() => {
    loadChangeData();
  }, [id]);

  const loadChangeData = async () => {
    try {
      setLoading(true);

      // Fetch change request
      const { data: changeData, error: changeError } = await supabase
        .from("change_requests")
        .select("*")
        .eq("id", id)
        .single();

      if (changeError) throw changeError;
      setChange(changeData);

      // Fetch impact analysis if exists
      const { data: analysisData } = await supabase
        .from("change_impact_analysis")
        .select("*")
        .eq("change_request_id", id)
        .order("analyzed_at", { ascending: false })
        .limit(1)
        .maybeSingle();

      setImpactAnalysis(analysisData);
    } catch (error) {
      console.error("Error loading change data:", error);
      toast.error("Failed to load change request");
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (newStatus: "draft" | "submitted" | "pending_approval" | "approved" | "rejected" | "scheduled" | "in_progress" | "implemented" | "completed" | "failed" | "rolled_back" | "cancelled") => {
    try {
      const { error } = await supabase
        .from("change_requests")
        .update({ change_status: newStatus })
        .eq("id", id);

      if (error) throw error;

      toast.success(`Change request ${newStatus.replace("_", " ")}`);
      loadChangeData();
    } catch (error) {
      console.error("Error updating status:", error);
      toast.error("Failed to update status");
    }
  };

  const createNinjaOneTicket = async () => {
    try {
      setCreatingTicket(true);
      toast.info("Creating NinjaOne ticket...");

      const { data, error } = await supabase.functions.invoke("ninjaone-ticket", {
        body: {
          change_request_id: id,
          action: "create",
        },
      });

      if (error) throw error;

      if (data.success) {
        toast.success("NinjaOne ticket created successfully");
        loadChangeData();
      } else {
        toast.error(data.error || "Failed to create ticket");
      }
    } catch (error) {
      console.error("Error creating ticket:", error);
      toast.error("Failed to create NinjaOne ticket");
    } finally {
      setCreatingTicket(false);
    }
  };

  const syncNinjaOneTicket = async () => {
    try {
      setSyncingTicket(true);
      toast.info("Syncing ticket status...");

      const { data, error } = await supabase.functions.invoke("ninjaone-ticket", {
        body: {
          change_request_id: id,
          action: "sync",
        },
      });

      if (error) throw error;

      if (data.success) {
        toast.success("Ticket status synced");
        loadChangeData();
      } else {
        toast.error(data.error || "Failed to sync ticket");
      }
    } catch (error) {
      console.error("Error syncing ticket:", error);
      toast.error("Failed to sync ticket status");
    } finally {
      setSyncingTicket(false);
    }
  };

  if (loading || !change) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="container mx-auto px-4 pt-56 pb-8">
        <DashboardNavigation
          title="Change Request Details"
          dashboards={[
            { name: "Change Management", path: "/change-management" },
            { name: "CMDB Dashboard", path: "/cmdb" },
          ]}
        />

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Button variant="ghost" onClick={() => navigate("/change-management")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Change Management
          </Button>
          <div className="flex gap-2">
            {!change.ninjaone_ticket_id && (
              <Button
                variant="outline"
                onClick={createNinjaOneTicket}
                disabled={creatingTicket}
              >
                <Ticket className="h-4 w-4 mr-2" />
                {creatingTicket ? "Creating..." : "Create NinjaOne Ticket"}
              </Button>
            )}
            {change.ninjaone_ticket_id && (
              <>
                <Button
                  variant="outline"
                  onClick={syncNinjaOneTicket}
                  disabled={syncingTicket}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${syncingTicket ? "animate-spin" : ""}`} />
                  Sync Status
                </Button>
                <Button
                  variant="outline"
                  onClick={() => window.open(change.ninjaone_ticket_url, "_blank")}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  View in NinjaOne
                </Button>
              </>
            )}
            {change.change_status === "draft" && (
              <Button onClick={() => updateStatus("pending_approval")}>
                Submit for Approval
              </Button>
            )}
            {change.change_status === "pending_approval" && (
              <>
                <Button variant="outline" onClick={() => updateStatus("approved")}>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Approve
                </Button>
                <Button variant="destructive" onClick={() => updateStatus("rejected")}>
                  <XCircle className="h-4 w-4 mr-2" />
                  Reject
                </Button>
              </>
            )}
            {change.change_status === "approved" && (
              <Button onClick={() => updateStatus("scheduled")}>
                <Clock className="h-4 w-4 mr-2" />
                Schedule
              </Button>
            )}
            {change.change_status === "scheduled" && (
              <Button onClick={() => updateStatus("in_progress")}>
                Start Implementation
              </Button>
            )}
            {change.change_status === "in_progress" && (
              <>
                <Button onClick={() => updateStatus("completed")}>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Mark Complete
                </Button>
                <Button variant="destructive" onClick={() => updateStatus("failed")}>
                  <XCircle className="h-4 w-4 mr-2" />
                  Mark Failed
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Overview Card */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <Badge variant="outline">{change.change_number}</Badge>
                  <CardTitle className="text-2xl">{change.title}</CardTitle>
                  {change.ninjaone_ticket_number && (
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Ticket className="h-3 w-3" />
                      NinjaOne #{change.ninjaone_ticket_number}
                    </Badge>
                  )}
                </div>
                <CardDescription className="mt-2">{change.description}</CardDescription>
                {change.ninjaone_ticket_status && (
                  <p className="text-sm text-muted-foreground mt-2">
                    NinjaOne Status: <Badge variant="outline">{change.ninjaone_ticket_status}</Badge>
                    {change.ninjaone_ticket_synced_at && (
                      <span className="ml-2">
                        Last synced: {new Date(change.ninjaone_ticket_synced_at).toLocaleString()}
                      </span>
                    )}
                  </p>
                )}
              </div>
              <div className="flex gap-2">
                <Badge variant={
                  change.priority === "critical" ? "destructive" :
                  change.priority === "high" ? "default" : "secondary"
                }>
                  {change.priority}
                </Badge>
                <Badge variant={
                  change.risk_level === "high" ? "destructive" :
                  change.risk_level === "medium" ? "default" : "secondary"
                }>
                  Risk: {change.risk_level || "Not assessed"}
                </Badge>
                <Badge variant={
                  change.change_status === "completed" ? "default" :
                  change.change_status === "failed" ? "destructive" : "secondary"
                }>
                  {change.change_status.replace("_", " ")}
                </Badge>
              </div>
            </div>
          </CardHeader>
        </Card>

        <Tabs defaultValue="details" className="space-y-6">
          <TabsList>
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="planning">Planning</TabsTrigger>
            <TabsTrigger value="impact">
              Impact Analysis {impactAnalysis && <Sparkles className="h-3 w-3 ml-1 inline" />}
            </TabsTrigger>
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
          </TabsList>

          <TabsContent value="details">
            <div className="grid gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Change Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Type</p>
                      <p className="font-medium capitalize">{change.change_type.replace("_", " ")}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Priority</p>
                      <p className="font-medium capitalize">{change.priority}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Status</p>
                      <p className="font-medium capitalize">{change.change_status.replace("_", " ")}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Risk Level</p>
                      <p className="font-medium capitalize">{change.risk_level || "Not assessed"}</p>
                    </div>
                    {change.estimated_downtime_minutes && (
                      <div>
                        <p className="text-sm text-muted-foreground">Estimated Downtime</p>
                        <p className="font-medium">{change.estimated_downtime_minutes} minutes</p>
                      </div>
                    )}
                    {change.affected_users && (
                      <div>
                        <p className="text-sm text-muted-foreground">Affected Users</p>
                        <p className="font-medium">{change.affected_users}</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {change.justification && (
                <Card>
                  <CardHeader>
                    <CardTitle>Justification</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm whitespace-pre-wrap">{change.justification}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="planning">
            <div className="grid gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Implementation Plan</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm whitespace-pre-wrap">{change.implementation_plan}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Rollback Plan</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm whitespace-pre-wrap">{change.rollback_plan}</p>
                </CardContent>
              </Card>

              {change.testing_plan && (
                <Card>
                  <CardHeader>
                    <CardTitle>Testing Plan</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm whitespace-pre-wrap">{change.testing_plan}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="impact">
            {impactAnalysis ? (
              <div className="grid gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Sparkles className="h-5 w-5 text-primary" />
                      AI-Powered Impact Analysis
                    </CardTitle>
                    <CardDescription>
                      Analyzed on {new Date(impactAnalysis.analyzed_at).toLocaleString()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {impactAnalysis.business_impact_score && (
                        <div>
                          <p className="text-sm text-muted-foreground">Business Impact</p>
                          <p className="text-2xl font-bold">{impactAnalysis.business_impact_score}/10</p>
                        </div>
                      )}
                      {impactAnalysis.technical_impact_score && (
                        <div>
                          <p className="text-sm text-muted-foreground">Technical Impact</p>
                          <p className="text-2xl font-bold">{impactAnalysis.technical_impact_score}/10</p>
                        </div>
                      )}
                      {impactAnalysis.security_impact_score && (
                        <div>
                          <p className="text-sm text-muted-foreground">Security Impact</p>
                          <p className="text-2xl font-bold">{impactAnalysis.security_impact_score}/10</p>
                        </div>
                      )}
                      {impactAnalysis.success_probability && (
                        <div>
                          <p className="text-sm text-muted-foreground">Success Probability</p>
                          <p className="text-2xl font-bold">{Math.round(impactAnalysis.success_probability * 100)}%</p>
                        </div>
                      )}
                    </div>

                    {impactAnalysis.recommended_approach && (
                      <div>
                        <h4 className="font-semibold mb-2">Recommended Approach</h4>
                        <p className="text-sm">{impactAnalysis.recommended_approach}</p>
                      </div>
                    )}

                    {impactAnalysis.mitigation_strategies && impactAnalysis.mitigation_strategies.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Mitigation Strategies</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {impactAnalysis.mitigation_strategies.map((strategy: string, idx: number) => (
                            <li key={idx} className="text-sm">{strategy}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card>
                <CardContent className="pt-12 pb-12 text-center">
                  <AlertTriangle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Impact Analysis Available</h3>
                  <p className="text-muted-foreground mb-4">
                    Impact analysis has not been performed for this change request yet
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="timeline">
            <Card>
              <CardHeader>
                <CardTitle>Change Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <Clock className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div>
                      <p className="font-medium">Created</p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(change.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {change.submitted_at && (
                    <div className="flex items-start gap-3">
                      <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div>
                        <p className="font-medium">Submitted for Approval</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(change.submitted_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )}

                  {change.approved_at && (
                    <div className="flex items-start gap-3">
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium">Approved</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(change.approved_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )}

                  {change.scheduled_start_time && (
                    <div className="flex items-start gap-3">
                      <Clock className="h-5 w-5 text-purple-600 mt-0.5" />
                      <div>
                        <p className="font-medium">Scheduled Start</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(change.scheduled_start_time).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )}

                  {change.completed_at && (
                    <div className="flex items-start gap-3">
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium">Completed</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(change.completed_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ChangeManagementDetail;
