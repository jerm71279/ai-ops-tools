/**
 * CaseStudy Component
 * 
 * Displays a detailed case study of how OberaConnect transformed their operations
 * using ComplianceOS. Features customer success metrics, implementation details,
 * and measurable results to demonstrate platform value.
 * 
 * Key sections:
 * - Customer challenge and pain points
 * - Solution implementation and architecture
 * - Measurable results and ROI
 * - Customer testimonial
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  CheckCircle2, 
  TrendingUp, 
  Clock, 
  Users, 
  Shield,
  ArrowRight,
  Database,
  Zap,
  FileCheck
} from "lucide-react";
import { useNavigate } from "react-router-dom";

const CaseStudy = () => {
  const navigate = useNavigate();
  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Badge className="bg-accent/10 text-accent border-accent/20 mb-4">
            Featured Customer
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            How OberaConnect Made One Login Power Their Growing Team
          </h2>
          <p className="text-xl text-muted-foreground">
            From password chaos to predictive intelligence: How this MSP company installing phones, cameras, and IT infrastructure transformed operations with unified access + ML
          </p>
        </div>

        {/* Hero Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <Card className="border-border text-center">
            <CardContent className="pt-6">
              <div className="text-4xl font-bold text-success mb-2">95%</div>
              <div className="text-sm text-muted-foreground">Fewer Password Resets</div>
            </CardContent>
          </Card>
          <Card className="border-border text-center">
            <CardContent className="pt-6">
              <div className="text-4xl font-bold text-accent mb-2">87%</div>
              <div className="text-sm text-muted-foreground">Prediction Accuracy</div>
            </CardContent>
          </Card>
          <Card className="border-border text-center">
            <CardContent className="pt-6">
              <div className="text-4xl font-bold text-warning mb-2">50</div>
              <div className="text-sm text-muted-foreground">Employees = 50x Data</div>
            </CardContent>
          </Card>
          <Card className="border-border text-center">
            <CardContent className="pt-6">
              <div className="text-4xl font-bold text-primary mb-2">1</div>
              <div className="text-sm text-muted-foreground">Login for All Systems</div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-2 gap-12 mb-12">
          {/* Challenge */}
          <div>
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-destructive/10 flex items-center justify-center">
                <Shield className="h-5 w-5 text-destructive" />
              </div>
              The Challenge
            </h3>
            <div className="space-y-4 text-muted-foreground">
              <p className="leading-relaxed">
                OberaConnect, an MSP company with close to 50 employees installing phones, cameras, IT networks and infrastructure, 
                juggled 12+ system logins daily—SAP, Workday, Salesforce, ServiceNow, and more. Password resets consumed IT resources. 
                Compliance teams had no unified view of employee activities across systems, making audits a manual nightmare.
              </p>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full bg-destructive/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Clock className="h-3 w-3 text-destructive" />
                  </div>
                  <span>200+ password reset tickets per month draining IT resources</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full bg-destructive/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Users className="h-3 w-3 text-destructive" />
                  </div>
                  <span>No visibility into actual employee workflows across systems</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full bg-destructive/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <FileCheck className="h-3 w-3 text-destructive" />
                  </div>
                  <span>Fragmented compliance data with no unified audit trail</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Solution */}
          <div>
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                <CheckCircle2 className="h-5 w-5 text-success" />
              </div>
              The Solution
            </h3>
            <div className="space-y-4 text-muted-foreground">
              <p className="leading-relaxed">
                ComplianceOS became OberaConnect's unified access portal and intelligence engine. 
                All employees now log in once to access every system. Every action trains ML models 
                while maintaining automated compliance.
              </p>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full bg-success/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <CheckCircle2 className="h-3 w-3 text-success" />
                  </div>
                  <span>Single Sign-On replacing 12+ passwords for all 50 employees</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full bg-success/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <CheckCircle2 className="h-3 w-3 text-success" />
                  </div>
                  <span>Every employee action captured for ML training and compliance tagging</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full bg-success/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <CheckCircle2 className="h-3 w-3 text-success" />
                  </div>
                  <span>Predictive intelligence from real behavioral data, not just APIs</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Architecture Implementation */}
        <Card className="border-border mb-12">
          <CardHeader>
            <CardTitle className="text-2xl">Implementation Architecture</CardTitle>
            <CardDescription className="text-base">
              How OberaConnect leveraged ComplianceOS's layered architecture
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  icon: Database,
                  title: "Unified Access Portal",
                  description: "One login for all systems—SAP, Workday, Salesforce, ServiceNow. SSO with MFA and session management.",
                },
                {
                  icon: Zap,
                  title: "Behavioral Capture Engine",
                  description: "Every employee action logged, compliance-tagged, and fed to ML models for predictive intelligence.",
                },
                {
                  icon: TrendingUp,
                  title: "ML Intelligence Layer",
                  description: "Predicts approval delays 5 days in advance with 87% accuracy after 3 months of employee usage data.",
                },
                {
                  icon: Users,
                  title: "Network Effect Intelligence",
                  description: "50 employees = 50x more training data. More users = exponentially better predictions.",
                },
                {
                  icon: Shield,
                  title: "Compliance Automation",
                  description: "Every system access compliance-tagged. Unified audit trail across all employee activities.",
                },
                {
                  icon: FileCheck,
                  title: "Role-Based Dashboards",
                  description: "Executives see predictive KPIs. Ops teams get bottleneck alerts. Compliance monitors live controls.",
                },
              ].map((layer, idx) => {
                const Icon = layer.icon;
                return (
                  <div key={idx} className="flex gap-4">
                    <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
                      <Icon className="h-6 w-6 text-accent" />
                    </div>
                    <div>
                      <div className="font-semibold mb-1">{layer.title}</div>
                      <div className="text-sm text-muted-foreground leading-relaxed">
                        {layer.description}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <Card className="bg-gradient-primary border-0 text-white">
          <CardHeader>
            <CardTitle className="text-3xl text-white mb-2">
              Measurable Results
            </CardTitle>
            <CardDescription className="text-white/80 text-base">
              OberaConnect's transformation by the numbers
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              <div>
                <h4 className="font-semibold mb-4 flex items-center gap-2 text-white">
                  <TrendingUp className="h-5 w-5" />
                  Operational Improvements
                </h4>
                <ul className="space-y-3">
                  {[
                    "95% reduction in password reset tickets (200+ → 10/month)",
                    "87% prediction accuracy for approval delays after 3 months",
                    "75% faster audit prep with unified cross-system audit trail",
                    "IT team freed up from password management to strategic work",
                  ].map((result, idx) => (
                    <li key={idx} className="flex items-start gap-3 text-white/90">
                      <CheckCircle2 className="h-5 w-5 text-white flex-shrink-0 mt-0.5" />
                      <span>{result}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-4 flex items-center gap-2 text-white">
                  <Shield className="h-5 w-5" />
                  Strategic Benefits
                </h4>
                <ul className="space-y-3">
                  {[
                    "50 employees using daily = 50x more ML training data",
                    "Predictive intelligence identifies problems 5 days before they occur",
                    "Employee behavioral patterns optimize workflows automatically",
                    "One platform replacing multiple access management tools",
                  ].map((result, idx) => (
                    <li key={idx} className="flex items-start gap-3 text-white/90">
                      <CheckCircle2 className="h-5 w-5 text-white flex-shrink-0 mt-0.5" />
                      <span>{result}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Quote */}
            <div className="border-t border-white/20 pt-6">
              <blockquote className="text-xl italic text-white/95 mb-4">
                "We went from password chaos to predictive intelligence. Our employees love having one login 
                for everything, and we love that every action they take is training our ML models to predict 
                and prevent problems. It's transformational."
              </blockquote>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center text-white font-bold">
                  EF
                </div>
                <div>
                  <div className="font-semibold text-white">Evan Fisher</div>
                  <div className="text-sm text-white/70">CEO, OberaConnect</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* CTA - Navigate to interactive demo selector */}
        <div className="text-center mt-12">
          <Button 
            variant="hero" 
            size="lg" 
            className="text-lg px-8"
            onClick={() => navigate('/demo')}
          >
            See ComplianceOS in Action
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </div>
    </section>
  );
};

export default CaseStudy;
