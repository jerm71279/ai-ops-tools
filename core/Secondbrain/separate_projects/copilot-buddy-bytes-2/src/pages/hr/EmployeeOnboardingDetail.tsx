import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Mail, Phone, Calendar, Building, Briefcase, User, MapPin, Home, Pencil, CheckCircle2, Circle, Clock } from "lucide-react";
import DashboardNavigation from "@/components/DashboardNavigation";

interface Onboarding {
  id: string;
  employee_name: string;
  employee_email: string;
  employee_phone: string | null;
  department: string | null;
  job_title: string | null;
  employment_type: string;
  start_date: string;
  status: string;
  completion_percentage: number;
  notes: string | null;
  created_at: string;
  date_of_birth: string | null;
  work_location: string | null;
  address_line1: string | null;
  address_line2: string | null;
  city: string | null;
  state_province: string | null;
  postal_code: string | null;
  country: string | null;
  manager_id: string | null;
  template_id: string | null;
}

interface Template {
  id: string;
  template_name: string;
  description: string | null;
}

interface OnboardingTask {
  id: string;
  task_name: string;
  description: string | null;
  task_category: string;
  status: string;
  sequence_order: number;
  assigned_role: string | null;
  estimated_hours: number | null;
  completed_at: string | null;
  due_date: string | null;
}

export default function EmployeeOnboardingDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [onboarding, setOnboarding] = useState<Onboarding | null>(null);
  const [template, setTemplate] = useState<Template | null>(null);
  const [tasks, setTasks] = useState<OnboardingTask[]>([]);
  const [managerName, setManagerName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadOnboarding();
  }, [id]);

  const loadOnboarding = async () => {
    if (!id) return;

    try {
      const { data: onboardingData, error: onboardingError } = await supabase
        .from('employee_onboardings')
        .select(`
          *,
          template_id
        `)
        .eq('id', id)
        .single();

      if (onboardingError) throw onboardingError;
      setOnboarding(onboardingData as any as Onboarding);

      // Load tasks
      const { data: tasksData, error: tasksError } = await supabase
        .from('employee_onboarding_tasks')
        .select('*')
        .eq('onboarding_id', id)
        .order('sequence_order');

      if (!tasksError && tasksData) {
        setTasks(tasksData as any);
      }

      if (onboardingData.template_id) {
        const { data: templateData, error: templateError } = await supabase
          .from('employee_onboarding_templates')
          .select('id, template_name, description')
          .eq('id', onboardingData.template_id)
          .single();

        if (!templateError && templateData) {
          setTemplate(templateData);
        }
      }

      if (onboardingData.manager_id) {
        const { data: managerData, error: managerError } = await supabase
          .from('user_profiles')
          .select('full_name')
          .eq('user_id', onboardingData.manager_id)
          .single();

        if (!managerError && managerData) {
          setManagerName(managerData.full_name);
        }
      }
    } catch (error) {
      console.error('Error loading onboarding:', error);
      toast({
        title: "Error",
        description: "Failed to load employee onboarding details",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTaskStatusChange = async (taskId: string, newStatus: string) => {
    try {
      const updates: any = { status: newStatus };
      if (newStatus === 'completed') {
        updates.completed_at = new Date().toISOString();
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
          updates.completed_by = user.id;
        }
      }

      const { error } = await supabase
        .from('employee_onboarding_tasks')
        .update(updates)
        .eq('id', taskId);

      if (error) throw error;

      // Recalculate completion percentage
      const completedTasks = tasks.filter(t => 
        t.id === taskId ? newStatus === 'completed' : t.status === 'completed'
      ).length;
      const completionPercentage = Math.round((completedTasks / tasks.length) * 100);

      await supabase
        .from('employee_onboardings')
        .update({ 
          completion_percentage: completionPercentage,
          status: completionPercentage === 100 ? 'completed' : 'in_progress'
        })
        .eq('id', id);

      toast({
        title: "Success",
        description: "Task status updated"
      });

      loadOnboarding();
    } catch (error) {
      console.error('Error updating task:', error);
      toast({
        title: "Error",
        description: "Failed to update task status",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
      not_started: { label: "Not Started", variant: "secondary" },
      in_progress: { label: "In Progress", variant: "default" },
      completed: { label: "Completed", variant: "outline" },
      on_hold: { label: "On Hold", variant: "destructive" }
    };
    
    const config = statusConfig[status] || { label: status, variant: "secondary" };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getTaskIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'in_progress':
        return <Clock className="h-5 w-5 text-blue-600" />;
      default:
        return <Circle className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const groupedTasks = tasks.reduce((acc, task) => {
    if (!acc[task.task_category]) {
      acc[task.task_category] = [];
    }
    acc[task.task_category].push(task);
    return acc;
  }, {} as Record<string, OnboardingTask[]>);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <main className="container mx-auto px-4 pb-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>
          <div className="text-center py-12">Loading...</div>
        </main>
      </div>
    );
  }

  if (!onboarding) {
    return (
      <div className="min-h-screen bg-background">
        <main className="container mx-auto px-4 pb-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>
          <div className="text-center py-12">
            <p className="text-muted-foreground mb-4">Employee onboarding not found</p>
            <Button onClick={() => navigate('/hr/employee-onboarding')}>
              Back to Dashboard
            </Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 pb-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>
        <DashboardNavigation 
          title="Employee Onboarding Details"
          dashboards={[
            { name: "Employee Onboarding", path: "/hr/employee-onboarding" },
            { name: "Templates", path: "/hr/employee-onboarding/templates" },
          ]}
        />

        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/hr/employee-onboarding')}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">{onboarding.employee_name}</h1>
              <p className="text-muted-foreground">{onboarding.job_title || 'No job title specified'}</p>
            </div>
            <div className="flex items-center gap-2">
              {getStatusBadge(onboarding.status)}
              <Button onClick={() => navigate(`/hr/employee-onboarding/${id}/edit`)}>
                <Pencil className="mr-2 h-4 w-4" />
                Edit Demographics
              </Button>
            </div>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2 mb-6">
          <Card>
            <CardHeader>
              <CardTitle>Employee Information</CardTitle>
              <CardDescription>Contact and employment details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{onboarding.employee_email}</p>
                </div>
              </div>
              
              {onboarding.employee_phone && (
                <div className="flex items-center gap-3">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Phone</p>
                    <p className="font-medium">{onboarding.employee_phone}</p>
                  </div>
                </div>
              )}
              
              <div className="flex items-center gap-3">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Start Date</p>
                  <p className="font-medium">{new Date(onboarding.start_date).toLocaleDateString()}</p>
                </div>
              </div>
              
              {onboarding.department && (
                <div className="flex items-center gap-3">
                  <Building className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Department</p>
                    <p className="font-medium">{onboarding.department}</p>
                  </div>
                </div>
              )}
              
              <div className="flex items-center gap-3">
                <Briefcase className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Employment Type</p>
                  <p className="font-medium capitalize">{onboarding.employment_type.replace('-', ' ')}</p>
                </div>
              </div>

              {onboarding.date_of_birth && (
                <div className="flex items-center gap-3">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Date of Birth</p>
                    <p className="font-medium">{new Date(onboarding.date_of_birth).toLocaleDateString()}</p>
                  </div>
                </div>
              )}

              {onboarding.work_location && (
                <div className="flex items-center gap-3">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Work Location</p>
                    <p className="font-medium">{onboarding.work_location}</p>
                  </div>
                </div>
              )}

              {managerName && (
                <div className="flex items-center gap-3">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Manager</p>
                    <p className="font-medium">{managerName}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Onboarding Progress</CardTitle>
              <CardDescription>Current completion status</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Completion</span>
                  <span className="text-sm font-medium">{onboarding.completion_percentage}%</span>
                </div>
                <Progress value={onboarding.completion_percentage} />
              </div>

              {template && (
                <div className="pt-4 border-t">
                  <p className="text-sm text-muted-foreground mb-1">Template</p>
                  <p className="font-medium">{template.template_name}</p>
                  {template.description && (
                    <p className="text-sm text-muted-foreground mt-2">{template.description}</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {(onboarding.address_line1 || onboarding.city || onboarding.country) && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Home className="h-5 w-5" />
                Address Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {onboarding.address_line1 && <p className="font-medium">{onboarding.address_line1}</p>}
                {onboarding.address_line2 && <p className="font-medium">{onboarding.address_line2}</p>}
                {(onboarding.city || onboarding.state_province || onboarding.postal_code) && (
                  <p className="text-muted-foreground">
                    {[onboarding.city, onboarding.state_province, onboarding.postal_code].filter(Boolean).join(', ')}
                  </p>
                )}
                {onboarding.country && <p className="text-muted-foreground">{onboarding.country}</p>}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Onboarding Tasks */}
        {tasks.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Onboarding Tasks ({tasks.filter(t => t.status === 'completed').length}/{tasks.length} Completed)</CardTitle>
              <CardDescription>Complete these steps to finish onboarding</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {Object.entries(groupedTasks).map(([category, categoryTasks]) => (
                  <div key={category} className="space-y-3">
                    <h3 className="font-semibold text-lg">{category}</h3>
                    <div className="space-y-2">
                      {categoryTasks.map((task) => (
                        <div 
                          key={task.id} 
                          className="flex items-start gap-3 p-3 border rounded-lg hover:bg-accent/50 transition-colors"
                        >
                          <div className="mt-1">
                            {getTaskIcon(task.status)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1">
                                <p className="font-medium">{task.task_name}</p>
                                {task.description && (
                                  <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
                                )}
                                <div className="flex flex-wrap gap-2 mt-2">
                                  {task.assigned_role && (
                                    <Badge variant="outline" className="text-xs">
                                      {task.assigned_role}
                                    </Badge>
                                  )}
                                  {task.estimated_hours && (
                                    <Badge variant="outline" className="text-xs">
                                      {task.estimated_hours}h estimated
                                    </Badge>
                                  )}
                                  {task.due_date && (
                                    <Badge variant="outline" className="text-xs">
                                      Due: {new Date(task.due_date).toLocaleDateString()}
                                    </Badge>
                                  )}
                                </div>
                              </div>
                              <Select
                                value={task.status}
                                onValueChange={(value) => handleTaskStatusChange(task.id, value)}
                              >
                                <SelectTrigger className="w-[140px]">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="pending">Pending</SelectItem>
                                  <SelectItem value="in_progress">In Progress</SelectItem>
                                  <SelectItem value="completed">Completed</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {onboarding.notes && (
          <Card>
            <CardHeader>
              <CardTitle>Notes</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{onboarding.notes}</p>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
