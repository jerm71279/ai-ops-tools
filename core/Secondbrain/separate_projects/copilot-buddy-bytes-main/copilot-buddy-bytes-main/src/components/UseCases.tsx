import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, Heart, DollarSign, PackageCheck, Briefcase, Globe } from "lucide-react";

const useCases = [
  {
    icon: Heart,
    industry: "Healthcare",
    title: "Eliminate Patient Onboarding Delays",
    description: "Identified 3-day bottleneck in consent workflows. Automated HIPAA-compliant approvals across EHR, HRIS, and CRM. Reduced onboarding from 7 days to 2 days.",
    frameworks: ["HIPAA", "ISO 27001"],
    features: ["67% faster onboarding", "100% audit trail", "Zero compliance gaps"],
  },
  {
    icon: DollarSign,
    industry: "Financial Services",
    title: "Speed Up Loan Approvals 5x",
    description: "Detected approval chain inefficiencies across 4 systems. Automated risk scoring and SOX controls in ERP workflows. Reduced approval time from 10 days to 2 days.",
    frameworks: ["SOX", "PCI DSS", "SOC 2"],
    features: ["80% faster approvals", "Real-time risk scoring", "Full audit readiness"],
  },
  {
    icon: PackageCheck,
    industry: "Manufacturing",
    title: "Fix Supply Chain Bottlenecks",
    description: "Identified supplier onboarding delays and quality control gaps. Unified SCM, ERP, and QMS with ISO 9001 tagging. Reduced supplier onboarding by 60%.",
    frameworks: ["ISO 9001", "ISO 27001"],
    features: ["60% faster onboarding", "Real-time quality tracking", "Supply chain visibility"],
  },
  {
    icon: Globe,
    industry: "SaaS Companies",
    title: "Accelerate Feature Releases",
    description: "Found deployment bottlenecks in CI/CD approval chains. Automated SOC 2 compliance gates and risk assessments. Increased release velocity by 45%.",
    frameworks: ["SOC 2", "ISO 27001"],
    features: ["45% more releases", "Automated compliance", "Zero rollback incidents"],
  },
  {
    icon: Briefcase,
    industry: "Professional Services",
    title: "Streamline Client Onboarding",
    description: "Detected GDPR workflow delays across Legal, Sales, and Finance. Automated DPAs and consent tracking in CRM. Cut onboarding time from 2 weeks to 3 days.",
    frameworks: ["GDPR", "ISO 27001"],
    features: ["78% time savings", "Automated DPAs", "Privacy compliance"],
  },
  {
    icon: Building2,
    industry: "Enterprise",
    title: "Unify Cross-Department Operations",
    description: "Identified redundant workflows across HR, Finance, IT, and Legal. Unified 12 systems with clause-linked schema. Eliminated 40% of manual processes.",
    frameworks: ["Multi-Framework"],
    features: ["40% efficiency gain", "12 systems unified", "Single audit trail"],
  },
];

const UseCases = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Solving Real Business Problems
          </h2>
          <p className="text-xl text-muted-foreground">
            See how organizations use our unified intelligence platform to identify bottlenecks, optimize workflows, 
            and solve operational challenges while maintaining continuous compliance.
          </p>
        </div>

        {/* Use Cases Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {useCases.map((useCase, index) => {
            const Icon = useCase.icon;
            return (
              <Card 
                key={index} 
                className="border-border hover:shadow-elevated transition-all duration-300 hover:-translate-y-1"
              >
                <CardHeader>
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                      <Icon className="h-6 w-6 text-accent" />
                    </div>
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      {useCase.industry}
                    </span>
                  </div>
                  <CardTitle className="text-xl mb-2">{useCase.title}</CardTitle>
                  <CardDescription className="leading-relaxed">
                    {useCase.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {/* Frameworks */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {useCase.frameworks.map((framework, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-accent/10 text-accent text-xs rounded font-medium"
                      >
                        {framework}
                      </span>
                    ))}
                  </div>
                  
                  {/* Key Features */}
                  <div className="border-t border-border pt-3">
                    <div className="text-xs font-semibold text-muted-foreground mb-2">
                      Key Features:
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {useCase.features.map((feature, idx) => (
                        <span
                          key={idx}
                          className="text-xs text-muted-foreground"
                        >
                          {feature}
                          {idx < useCase.features.length - 1 && " • "}
                        </span>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default UseCases;
