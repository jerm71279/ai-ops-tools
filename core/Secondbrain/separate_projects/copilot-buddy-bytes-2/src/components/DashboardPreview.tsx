import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, AlertCircle, CheckCircle2, Clock } from "lucide-react";

const DashboardPreview = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            See Every Bottleneck. Fix Every Issue.
          </h2>
          <p className="text-xl text-muted-foreground">
            Real-time visibility into workflow efficiency, process bottlenecks, and system health across your entire tech stack. 
            Identify problems instantly, get actionable insights, and maintain continuous compliance across all departments.
          </p>
        </div>

        {/* Dashboard Grid */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Compliance Score */}
          <Card className="border-border shadow-elevated">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Compliance Score</CardTitle>
                <TrendingUp className="h-5 w-5 text-success" />
              </div>
              <CardDescription>Overall compliance posture</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-5xl font-bold text-success mb-4">94%</div>
              <Progress value={94} className="h-3 mb-3" />
              <p className="text-sm text-muted-foreground">
                +12% from last quarter
              </p>
            </CardContent>
          </Card>

          {/* Active Controls */}
          <Card className="border-border shadow-elevated">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Active Controls</CardTitle>
                <CheckCircle2 className="h-5 w-5 text-accent" />
              </div>
              <CardDescription>Implemented & monitored</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-5xl font-bold text-accent mb-4">247</div>
              <div className="flex items-center gap-2 mb-3">
                <Badge variant="outline" className="bg-success/10 text-success border-success/20">
                  203 Compliant
                </Badge>
                <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">
                  44 Review
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Bottlenecks Detected */}
          <Card className="border-border shadow-elevated">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Bottlenecks Detected</CardTitle>
                <AlertCircle className="h-5 w-5 text-warning" />
              </div>
              <CardDescription>Workflow inefficiencies</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-5xl font-bold text-warning mb-4">8</div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Approval Delays</span>
                  <span className="font-semibold">5</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Data Sync Issues</span>
                  <span className="font-semibold">3</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Workflow Efficiency Metrics */}
        <Card className="border-border shadow-elevated">
          <CardHeader>
            <CardTitle className="text-xl">Cross-System Workflow Efficiency</CardTitle>
            <CardDescription>
              Process performance and bottleneck resolution across all departments
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {[
                { name: "HR Onboarding (HRIS → ATS → LMS)", efficiency: 87, avgTime: "2.3 days", color: "bg-blue-500", issue: "None" },
                { name: "Finance Approval (ERP → Workflow)", efficiency: 94, avgTime: "4.1 hours", color: "bg-green-500", issue: "None" },
                { name: "Sales Pipeline (CRM → CPQ)", efficiency: 72, avgTime: "8.7 days", color: "bg-orange-500", issue: "Approval delays" },
                { name: "IT Service Requests (ITSM)", efficiency: 89, avgTime: "1.2 days", color: "bg-purple-500", issue: "None" },
              ].map((workflow, idx) => (
                <div key={idx}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${workflow.color}`} />
                      <div>
                        <span className="font-semibold block">{workflow.name}</span>
                        <span className="text-xs text-muted-foreground">Avg time: {workflow.avgTime}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {workflow.issue !== "None" && (
                        <span className="text-xs bg-warning/10 text-warning px-2 py-1 rounded">
                          {workflow.issue}
                        </span>
                      )}
                      <span className="font-semibold text-lg">{workflow.efficiency}%</span>
                    </div>
                  </div>
                  <Progress value={workflow.efficiency} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default DashboardPreview;
