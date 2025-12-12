import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, Save, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { z } from "zod";

const changeRequestSchema = z.object({
  title: z.string().trim().min(1, "Title is required").max(200),
  description: z.string().trim().min(1, "Description is required").max(2000),
  change_type: z.string().min(1, "Change type is required"),
  priority: z.string().min(1, "Priority is required"),
  justification: z.string().trim().min(1, "Justification is required").max(2000),
  implementation_plan: z.string().trim().min(1, "Implementation plan is required").max(5000),
  rollback_plan: z.string().trim().min(1, "Rollback plan is required").max(5000),
  testing_plan: z.string().max(5000).optional(),
  business_impact: z.string().max(2000).optional(),
  technical_impact: z.string().max(2000).optional(),
  estimated_downtime_minutes: z.number().min(0).optional(),
  affected_users: z.number().min(0).optional(),
});

interface ConfigurationItem {
  id: string;
  ci_name: string;
  ci_type: string;
}

const ChangeManagementNew = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [analyzingImpact, setAnalyzingImpact] = useState(false);
  const [cis, setCis] = useState<ConfigurationItem[]>([]);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    change_type: "normal",
    priority: "medium",
    justification: "",
    implementation_plan: "",
    rollback_plan: "",
    testing_plan: "",
    business_impact: "",
    technical_impact: "",
    estimated_downtime_minutes: "",
    affected_users: "",
    affected_ci_ids: [] as string[],
  });

  useEffect(() => {
    loadCIs();
  }, []);

  const loadCIs = async () => {
    try {
      const { data, error } = await supabase
        .from("configuration_items")
        .select("id, ci_name, ci_type")
        .eq("ci_status", "active")
        .order("ci_name");

      if (error) throw error;
      setCis(data || []);
    } catch (error) {
      console.error("Error loading CIs:", error);
    }
  };

  const analyzeImpact = async () => {
    try {
      setAnalyzingImpact(true);
      toast.info("Analyzing change impact with AI...");

      const { data, error } = await supabase.functions.invoke("change-impact-analyzer", {
        body: {
          title: formData.title,
          description: formData.description,
          change_type: formData.change_type,
          affected_ci_ids: formData.affected_ci_ids,
          implementation_plan: formData.implementation_plan,
        },
      });

      if (error) throw error;

      if (data.success) {
        toast.success("Impact analysis complete");
        // Update form with AI recommendations
        if (data.analysis?.recommended_approach) {
          setFormData(prev => ({
            ...prev,
            business_impact: data.analysis.business_impact_summary || prev.business_impact,
            technical_impact: data.analysis.technical_impact_summary || prev.technical_impact,
          }));
        }
      }
    } catch (error) {
      console.error("Error analyzing impact:", error);
      toast.error("Failed to analyze impact");
    } finally {
      setAnalyzingImpact(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setLoading(true);

      // Validate form data
      const validatedData = changeRequestSchema.parse({
        ...formData,
        estimated_downtime_minutes: formData.estimated_downtime_minutes
          ? parseInt(formData.estimated_downtime_minutes)
          : undefined,
        affected_users: formData.affected_users
          ? parseInt(formData.affected_users)
          : undefined,
      });

      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        toast.error("You must be logged in");
        return;
      }

      // Get customer_id
      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) {
        toast.error("User profile not found");
        return;
      }

      // Create change request
      const insertData: any = {
        ...validatedData,
        customer_id: profile.customer_id,
        requested_by: user.id,
        affected_ci_ids: formData.affected_ci_ids,
        change_status: "draft",
      };

      const { data, error } = await supabase
        .from("change_requests")
        .insert(insertData)
        .select()
        .single();

      if (error) throw error;

      toast.success("Change request created successfully");
      navigate(`/change-management/${data.id}`);
    } catch (error) {
      console.error("Error creating change request:", error);
      if (error instanceof z.ZodError) {
        toast.error(error.errors[0].message);
      } else {
        toast.error("Failed to create change request");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="container mx-auto px-4 pt-56 pb-8">
        <DashboardNavigation
          title="New Change Request"
          dashboards={[
            { name: "Change Management", path: "/change-management" },
            { name: "CMDB Dashboard", path: "/cmdb" },
          ]}
        />

        <div className="flex items-center justify-between mb-6">
          <Button variant="ghost" onClick={() => navigate("/change-management")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Change Management
          </Button>
          {formData.title && formData.description && formData.affected_ci_ids.length > 0 && (
            <Button
              variant="outline"
              onClick={analyzeImpact}
              disabled={analyzingImpact}
            >
              <Sparkles className="h-4 w-4 mr-2" />
              {analyzingImpact ? "Analyzing..." : "Analyze Impact with AI"}
            </Button>
          )}
        </div>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Change Request Details</CardTitle>
                <CardDescription>Provide basic information about the change</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Title *</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => handleChange("title", e.target.value)}
                    placeholder="Brief description of the change"
                    required
                    maxLength={200}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description *</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleChange("description", e.target.value)}
                    placeholder="Detailed description of what will be changed"
                    rows={4}
                    required
                    maxLength={2000}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="change_type">Change Type *</Label>
                    <Select value={formData.change_type} onValueChange={(v) => handleChange("change_type", v)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="standard">Standard</SelectItem>
                        <SelectItem value="normal">Normal</SelectItem>
                        <SelectItem value="emergency">Emergency</SelectItem>
                        <SelectItem value="routine">Routine</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="priority">Priority *</Label>
                    <Select value={formData.priority} onValueChange={(v) => handleChange("priority", v)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Justification & Planning */}
            <Card>
              <CardHeader>
                <CardTitle>Planning & Justification</CardTitle>
                <CardDescription>Explain why this change is needed and how it will be implemented</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="justification">Justification *</Label>
                  <Textarea
                    id="justification"
                    value={formData.justification}
                    onChange={(e) => handleChange("justification", e.target.value)}
                    placeholder="Why is this change necessary?"
                    rows={3}
                    required
                    maxLength={2000}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="implementation_plan">Implementation Plan *</Label>
                  <Textarea
                    id="implementation_plan"
                    value={formData.implementation_plan}
                    onChange={(e) => handleChange("implementation_plan", e.target.value)}
                    placeholder="Step-by-step plan for implementing the change"
                    rows={5}
                    required
                    maxLength={5000}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="rollback_plan">Rollback Plan *</Label>
                  <Textarea
                    id="rollback_plan"
                    value={formData.rollback_plan}
                    onChange={(e) => handleChange("rollback_plan", e.target.value)}
                    placeholder="How to revert the change if it fails"
                    rows={4}
                    required
                    maxLength={5000}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="testing_plan">Testing Plan</Label>
                  <Textarea
                    id="testing_plan"
                    value={formData.testing_plan}
                    onChange={(e) => handleChange("testing_plan", e.target.value)}
                    placeholder="How will you verify the change was successful?"
                    rows={3}
                    maxLength={5000}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Impact Assessment */}
            <Card>
              <CardHeader>
                <CardTitle>Impact Assessment</CardTitle>
                <CardDescription>Describe the potential impact of this change</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="business_impact">Business Impact</Label>
                  <Textarea
                    id="business_impact"
                    value={formData.business_impact}
                    onChange={(e) => handleChange("business_impact", e.target.value)}
                    placeholder="How will this affect business operations?"
                    rows={3}
                    maxLength={2000}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="technical_impact">Technical Impact</Label>
                  <Textarea
                    id="technical_impact"
                    value={formData.technical_impact}
                    onChange={(e) => handleChange("technical_impact", e.target.value)}
                    placeholder="Technical systems and services affected"
                    rows={3}
                    maxLength={2000}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="estimated_downtime_minutes">Estimated Downtime (minutes)</Label>
                    <Input
                      id="estimated_downtime_minutes"
                      type="number"
                      min="0"
                      value={formData.estimated_downtime_minutes}
                      onChange={(e) => handleChange("estimated_downtime_minutes", e.target.value)}
                      placeholder="0"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="affected_users">Affected Users</Label>
                    <Input
                      id="affected_users"
                      type="number"
                      min="0"
                      value={formData.affected_users}
                      onChange={(e) => handleChange("affected_users", e.target.value)}
                      placeholder="0"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex justify-end gap-4">
              <Button type="button" variant="outline" onClick={() => navigate("/change-management")}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                <Save className="h-4 w-4 mr-2" />
                {loading ? "Creating..." : "Create Change Request"}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChangeManagementNew;
