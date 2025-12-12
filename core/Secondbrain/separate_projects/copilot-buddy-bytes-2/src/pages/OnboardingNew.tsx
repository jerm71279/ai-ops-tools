import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Plus } from "lucide-react";
import DashboardNavigation from "@/components/DashboardNavigation";

interface Template {
  id: string;
  template_name: string;
  description: string | null;
  client_type: string;
  estimated_days: number | null;
}

export default function OnboardingNew() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    client_name: "",
    client_contact_email: "",
    client_contact_name: "",
    template_id: "",
    notes: "",
    start_date: new Date().toISOString().split('T')[0],
    target_completion_date: "",
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const { data, error } = await supabase
        .from('onboarding_templates')
        .select('*')
        .eq('is_active', true)
        .order('template_name');

      if (error) throw error;
      setTemplates(data || []);
    } catch (error) {
      console.error('Error loading templates:', error);
      toast({
        title: "Error",
        description: "Failed to load templates",
        variant: "destructive"
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.client_name || !formData.template_id || !formData.client_contact_email) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from('user_profiles')
        .select('customer_id')
        .eq('user_id', user.id)
        .single();

      if (!profile?.customer_id) throw new Error("No customer profile found");

      // Create the onboarding
      const { data: onboarding, error: onboardingError } = await supabase
        .from('client_onboardings')
        .insert({
          client_name: formData.client_name,
          client_contact_email: formData.client_contact_email,
          client_contact_name: formData.client_contact_name || null,
          template_id: formData.template_id,
          notes: formData.notes || null,
          start_date: formData.start_date,
          target_completion_date: formData.target_completion_date || null,
          status: 'not_started',
          completion_percentage: 0,
          customer_id: profile.customer_id,
          created_by: user.id
        })
        .select()
        .single();

      if (onboardingError) throw onboardingError;

      toast({
        title: "Success",
        description: "Client onboarding created successfully"
      });

      navigate(`/onboarding/${onboarding.id}`);
    } catch (error) {
      console.error('Error creating onboarding:', error);
      toast({
        title: "Error",
        description: "Failed to create onboarding",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 pb-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>
        <DashboardNavigation 
          title="New Client Onboarding"
          dashboards={[
            { name: "Onboarding Dashboard", path: "/onboarding" },
            { name: "Templates", path: "/onboarding/templates" },
          ]}
        />

        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/onboarding')}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Onboarding
          </Button>
          
          <h1 className="text-4xl font-bold mb-2">Create New Client Onboarding</h1>
          <p className="text-muted-foreground">Set up onboarding for a new MSP customer</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Client Information</CardTitle>
            <CardDescription>Enter the MSP customer information and select an onboarding template</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="client_name">Client Name *</Label>
                <Input
                  id="client_name"
                  value={formData.client_name}
                  onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                  placeholder="Enter client name"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="client_contact_email">Client Contact Email *</Label>
                <Input
                  id="client_contact_email"
                  type="email"
                  value={formData.client_contact_email}
                  onChange={(e) => setFormData({ ...formData, client_contact_email: e.target.value })}
                  placeholder="Enter client contact email"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="client_contact_name">Client Contact Name</Label>
                <Input
                  id="client_contact_name"
                  value={formData.client_contact_name}
                  onChange={(e) => setFormData({ ...formData, client_contact_name: e.target.value })}
                  placeholder="Enter client contact name"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="template">Onboarding Template *</Label>
                <Select
                  value={formData.template_id}
                  onValueChange={(value) => setFormData({ ...formData, template_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a template" />
                  </SelectTrigger>
                  <SelectContent>
                    {templates.map((template) => (
                      <SelectItem key={template.id} value={template.id}>
                        {template.template_name}
                        {template.estimated_days && ` (${template.estimated_days} days)`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {templates.length === 0 && (
                  <p className="text-sm text-muted-foreground">
                    No templates available. <a href="/onboarding/templates" className="underline">Create one first</a>.
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Optional notes about this onboarding"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start_date">Start Date *</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="target_completion_date">Target Completion Date</Label>
                  <Input
                    id="target_completion_date"
                    type="date"
                    value={formData.target_completion_date}
                    onChange={(e) => setFormData({ ...formData, target_completion_date: e.target.value })}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/onboarding')}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  <Plus className="mr-2 h-4 w-4" />
                  {isLoading ? "Creating..." : "Create Onboarding"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
