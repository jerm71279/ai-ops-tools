import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, TrendingUp, Zap, Network } from "lucide-react";

const mlCapabilities = [
  {
    icon: Brain,
    title: "Predictive Analytics",
    description: "Forecast operational issues before they happen",
    examples: [
      "Predict staffing shortages 2 weeks in advance",
      "Forecast cash flow gaps from sales pipeline",
      "Identify compliance risks before audits",
      "Anticipate inventory shortages from demand patterns"
    ]
  },
  {
    icon: TrendingUp,
    title: "Pattern Recognition",
    description: "Discover insights humans miss across systems",
    examples: [
      "Detect approval bottlenecks across departments",
      "Identify burnout patterns from ITSM + HRIS data",
      "Spot fraud patterns in financial workflows",
      "Find process inefficiencies in cross-system workflows"
    ]
  },
  {
    icon: Zap,
    title: "Automated Recommendations",
    description: "AI suggests optimizations based on your data",
    examples: [
      "Recommend workflow automation opportunities",
      "Suggest resource reallocation for efficiency",
      "Identify redundant approvals to eliminate",
      "Propose risk mitigation strategies"
    ]
  },
  {
    icon: Network,
    title: "Network Effect Intelligence",
    description: "More systems = exponentially better insights",
    examples: [
      "3 systems: Basic cross-system visibility",
      "6 systems: Pattern detection and insights",
      "10 systems: Predictive intelligence",
      "15+ systems: Enterprise-wide optimization"
    ]
  }
];

const MLIntelligence = () => {
  return (
    <section className="py-24 bg-accent/5">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 bg-accent/10 border border-accent/20 rounded-full px-6 py-2 mb-6">
            <Brain className="h-4 w-4 text-accent" />
            <span className="text-sm font-medium text-accent">Machine Learning Powered</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            More Employees Using = Exponentially Smarter Intelligence
          </h2>
          <p className="text-xl text-muted-foreground">
            Every employee logging in and working across systems is training our ML models. Real behavioral data—not just APIs. 
            The network effect is powerful: 10 employees = baseline insights. 100 employees = predictive intelligence. 
            1,000+ employees = enterprise-wide transformation.
          </p>
        </div>

        {/* ML Capabilities Grid */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          {mlCapabilities.map((capability, index) => {
            const Icon = capability.icon;
            return (
              <Card key={index} className="border-border hover:shadow-elevated transition-all duration-300">
                <CardHeader>
                  <div className="w-14 h-14 rounded-xl bg-accent/10 flex items-center justify-center mb-4">
                    <Icon className="h-7 w-7 text-accent" />
                  </div>
                  <CardTitle className="text-2xl mb-2">{capability.title}</CardTitle>
                  <CardDescription className="text-base">
                    {capability.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {capability.examples.map((example, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-accent mt-2 flex-shrink-0" />
                        <span className="text-sm text-muted-foreground">{example}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Network Effect Visualization */}
        <Card className="border-border shadow-elevated bg-gradient-to-br from-background to-accent/5">
          <CardHeader>
            <CardTitle className="text-2xl">The Network Effect in Action</CardTitle>
            <CardDescription>
              ML model accuracy improves exponentially with more data sources
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {[
                { systems: "10 Employees", accuracy: 60, description: "Basic behavioral patterns and workflow visibility", color: "bg-blue-500" },
                { systems: "100 Employees", accuracy: 75, description: "Department-level insights and bottleneck detection", color: "bg-purple-500" },
                { systems: "500 Employees", accuracy: 88, description: "Predictive intelligence across all departments", color: "bg-green-500" },
                { systems: "1,000+ Employees", accuracy: 95, description: "Enterprise-wide transformation and optimization", color: "bg-orange-500" },
              ].map((stage, idx) => (
                <div key={idx} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${stage.color}`} />
                      <div>
                        <span className="font-semibold block">{stage.systems}</span>
                        <span className="text-xs text-muted-foreground">{stage.description}</span>
                      </div>
                    </div>
                    <span className="text-2xl font-bold text-accent">{stage.accuracy}%</span>
                  </div>
                  <div className="h-3 bg-muted rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${stage.color} transition-all duration-1000`}
                      style={{ width: `${stage.accuracy}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default MLIntelligence;