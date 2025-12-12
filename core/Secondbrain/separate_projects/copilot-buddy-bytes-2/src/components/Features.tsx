import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield, Workflow, BarChart3, Database, Users, FileCheck } from "lucide-react";
import complianceIcon from "@/assets/compliance-icon.png";
import workflowIcon from "@/assets/workflow-icon.png";
import dashboardIcon from "@/assets/dashboard-icon.png";

const features = [
  {
    icon: complianceIcon,
    title: "Single Sign-On Access Portal",
    description: "Employees log in once and access every business system—SAP, Workday, Salesforce, ServiceNow, and more. No more password fatigue. Every login tracked and compliance-tagged automatically.",
    highlights: ["One Login", "Universal Access", "Activity Tracking", "Compliance Logging", "Audit Trail"],
  },
  {
    icon: workflowIcon,
    title: "Behavioral Intelligence Engine",
    description: "ML models learn from every employee action across all systems. Capture real workflow patterns, not just API data. The more your team uses the platform, the smarter the predictions become.",
    highlights: ["User Behavior Analysis", "Workflow Learning", "Pattern Detection", "Usage Intelligence"],
  },
  {
    icon: dashboardIcon,
    title: "Predictive Command Center",
    description: "Real-time dashboards powered by actual employee workflows. See bottlenecks as they happen, predict delays before they occur, and get AI recommendations based on how your team actually works.",
    highlights: ["Real-Time Insights", "Bottleneck Prediction", "AI Recommendations", "Cross-System View"],
  },
];

const additionalFeatures = [
  {
    icon: Database,
    title: "Employee Usage = Better Models",
    description: "Every employee using the platform is training data. 100 employees = 100x more behavioral insights. 1,000 employees = enterprise-wide intelligence that predicts and prevents problems.",
  },
  {
    icon: Users,
    title: "Zero-Trust Security Built In",
    description: "Enterprise-grade SSO with MFA, session management, and granular access controls. Every system access logged and compliance-tagged. Security and intelligence in one platform.",
  },
  {
    icon: FileCheck,
    title: "Unified Audit Trail",
    description: "Every login, transaction, and approval across all systems captured in one compliance-tagged audit trail. Instant audit readiness with evidence for every control.",
  },
];

const Features = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Your Team's Daily Portal. Your Company's Intelligence Engine.
          </h2>
          <p className="text-xl text-muted-foreground">
            Employees log in once to access all systems—SAP, Workday, Salesforce, ServiceNow. Every click, approval, and transaction 
            trains our ML models. The result? Predictive intelligence that gets smarter with every user, every day.
          </p>
        </div>

        {/* Main Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="border-border hover:shadow-floating transition-all duration-300">
              <CardHeader>
                <div className="w-20 h-20 mb-4 rounded-xl bg-gradient-accent p-4 shadow-elevated">
                  <img 
                    src={feature.icon} 
                    alt={feature.title}
                    className="w-full h-full object-contain"
                  />
                </div>
                <CardTitle className="text-2xl mb-2">{feature.title}</CardTitle>
                <CardDescription className="text-base leading-relaxed">
                  {feature.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {feature.highlights.map((highlight, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-accent/10 text-accent text-sm rounded-full font-medium"
                    >
                      {highlight}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Additional Features Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {additionalFeatures.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="border-border hover:border-accent/50 transition-colors">
                <CardHeader>
                  <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-3">
                    <Icon className="h-6 w-6 text-accent" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Features;
