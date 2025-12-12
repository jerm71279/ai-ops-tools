import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FolderKanban, DollarSign, Clock, TrendingUp, Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const ProjectManagement = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [selectedTab, setSelectedTab] = useState("active");
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  const [newProject, setNewProject] = useState({
    project_name: "",
    project_type: "client",
    priority: "medium",
    start_date: "",
    end_date: "",
    budget_amount: "",
    description: "",
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) return;

      const { data, error } = await supabase
        .from("projects")
        .select("*")
        .eq("customer_id", profile.customer_id)
        .order("created_at", { ascending: false });

      if (error) throw error;
      setProjects(data || []);
    } catch (error) {
      console.error("Error fetching projects:", error);
      toast({
        title: "Error",
        description: "Failed to load projects",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) return;

      const { error } = await supabase.from("projects").insert([
        {
          customer_id: profile.customer_id,
          project_number: "",
          ...newProject,
          budget_amount: parseFloat(newProject.budget_amount) || null,
        },
      ]);

      if (error) throw error;

      toast({
        title: "Success",
        description: "Project created successfully",
      });

      setIsCreateDialogOpen(false);
      setNewProject({
        project_name: "",
        project_type: "client",
        priority: "medium",
        start_date: "",
        end_date: "",
        budget_amount: "",
        description: "",
      });
      fetchProjects();
    } catch (error) {
      console.error("Error creating project:", error);
      toast({
        title: "Error",
        description: "Failed to create project",
        variant: "destructive",
      });
    }
  };

  // Calculate stats
  const activeProjects = projects?.filter(p => p.project_status === 'active').length || 0;
  const totalBudget = projects?.reduce((sum, p) => sum + (Number(p.budget_amount) || 0), 0) || 0;
  const totalHours = projects?.reduce((sum, p) => sum + (Number(p.actual_hours) || 0), 0) || 0;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'default';
      case 'planning': return 'secondary';
      case 'completed': return 'default';
      case 'on_hold': return 'outline';
      case 'cancelled': return 'destructive';
      default: return 'default';
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Project Management</h1>
              <p className="text-muted-foreground">Professional Services Automation (PSA)</p>
            </div>
            
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  New Project
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Create New Project</DialogTitle>
                </DialogHeader>
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <Label htmlFor="project_name">Project Name*</Label>
                    <Input
                      id="project_name"
                      value={newProject.project_name}
                      onChange={(e) => setNewProject({ ...newProject, project_name: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="project_type">Project Type</Label>
                    <Select
                      value={newProject.project_type}
                      onValueChange={(value) => setNewProject({ ...newProject, project_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="client">Client</SelectItem>
                        <SelectItem value="internal">Internal</SelectItem>
                        <SelectItem value="r_and_d">R&D</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="priority">Priority</Label>
                    <Select
                      value={newProject.priority}
                      onValueChange={(value) => setNewProject({ ...newProject, priority: value })}
                    >
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
                  <div>
                    <Label htmlFor="start_date">Start Date</Label>
                    <Input
                      id="start_date"
                      type="date"
                      value={newProject.start_date}
                      onChange={(e) => setNewProject({ ...newProject, start_date: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="end_date">End Date</Label>
                    <Input
                      id="end_date"
                      type="date"
                      value={newProject.end_date}
                      onChange={(e) => setNewProject({ ...newProject, end_date: e.target.value })}
                    />
                  </div>
                  <div className="col-span-2">
                    <Label htmlFor="budget_amount">Budget Amount</Label>
                    <Input
                      id="budget_amount"
                      type="number"
                      value={newProject.budget_amount}
                      onChange={(e) => setNewProject({ ...newProject, budget_amount: e.target.value })}
                    />
                  </div>
                  <div className="col-span-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={newProject.description}
                      onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateProject}>Create Project</Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
              <FolderKanban className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{activeProjects}</div>
              <p className="text-xs text-muted-foreground mt-1">In progress</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Budget</CardTitle>
              <DollarSign className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalBudget.toFixed(0)}</div>
              <p className="text-xs text-muted-foreground mt-1">All projects</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Hours Logged</CardTitle>
              <Clock className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalHours.toFixed(0)}h</div>
              <p className="text-xs text-muted-foreground mt-1">Total time</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Projects</CardTitle>
              <TrendingUp className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{projects?.length || 0}</div>
              <p className="text-xs text-muted-foreground mt-1">All time</p>
            </CardContent>
          </Card>
        </div>

        {/* Project List */}
        <Tabs value={selectedTab} onValueChange={setSelectedTab}>
          <TabsList>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="planning">Planning</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="all">All Projects</TabsTrigger>
          </TabsList>

          <TabsContent value={selectedTab} className="space-y-4">
            {loading ? (
              <p>Loading...</p>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {projects
                  ?.filter(p => selectedTab === 'all' || p.project_status === selectedTab)
                  .map((project) => {
                    const progress = project.completion_percentage || 0;

                    return (
                      <Card
                        key={project.id}
                        className="cursor-pointer hover:border-primary/50 transition-colors"
                        onClick={() => navigate(`/projects/${project.id}`)}
                      >
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <CardTitle className="text-xl">{project.project_name}</CardTitle>
                                <Badge variant={getStatusColor(project.project_status) as any}>
                                  {project.project_status}
                                </Badge>
                                <Badge variant="outline">{project.project_type}</Badge>
                              </div>
                              <CardDescription>{project.description || "No description"}</CardDescription>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/projects/${project.id}`);
                              }}
                            >
                              View Details
                            </Button>
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          {/* Progress */}
                          <div className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-muted-foreground">Progress</span>
                              <span className="font-medium">{progress}%</span>
                            </div>
                            <Progress value={progress} />
                          </div>

                          {/* Project Details */}
                          <div className="grid grid-cols-4 gap-4 pt-2 border-t">
                            <div>
                              <p className="text-xs text-muted-foreground">Budget</p>
                              <p className="font-medium">
                                {project.budget_amount
                                  ? `$${project.budget_amount.toLocaleString()}`
                                  : "N/A"}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Start Date</p>
                              <p className="font-medium">
                                {project.start_date
                                  ? new Date(project.start_date).toLocaleDateString()
                                  : "Not set"}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">End Date</p>
                              <p className="font-medium">
                                {project.end_date
                                  ? new Date(project.end_date).toLocaleDateString()
                                  : "Not set"}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Priority</p>
                              <Badge variant="outline" className="mt-1">{project.priority}</Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}

                {(!projects ||
                  projects.filter(p => selectedTab === 'all' || p.project_status === selectedTab)
                    .length === 0) && (
                  <Card>
                    <CardContent className="py-12">
                      <p className="text-center text-muted-foreground">No projects found</p>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>
        </div>
      </main>
    </div>
  );
};

export default ProjectManagement;
