import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, ChevronDown, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

const frameworks = [
  {
    name: "ISO 27001",
    description: "Information Security Management",
    clauses: 114,
    status: "Fully Supported",
    color: "bg-blue-500",
  },
  {
    name: "SOC 2",
    description: "Service Organization Control",
    clauses: 64,
    status: "Fully Supported",
    color: "bg-purple-500",
  },
  {
    name: "HIPAA",
    description: "Health Insurance Portability",
    clauses: 48,
    status: "Fully Supported",
    color: "bg-green-500",
  },
  {
    name: "NIST CSF",
    description: "Cybersecurity Framework",
    clauses: 108,
    status: "Fully Supported",
    color: "bg-orange-500",
  },
];

const Frameworks = () => {
  const [openFramework, setOpenFramework] = useState<number | null>(null);

  return (
    <section className="py-24 bg-secondary/30">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Compliance Tagging Across All Systems
          </h2>
          <p className="text-xl text-muted-foreground">
            Comprehensive clause mappings embedded in your operational schema. Every ERP transaction, HRIS record, CRM activity, and workflow step is tagged to compliance requirements.
          </p>
        </div>

        {/* Frameworks List */}
        <div className="space-y-4 mb-12">
          {frameworks.map((framework, index) => (
            <Collapsible
              key={index}
              open={openFramework === index}
              onOpenChange={(isOpen) => setOpenFramework(isOpen ? index : null)}
            >
              <Card className="border-border hover:shadow-elevated transition-all duration-300">
                <CollapsibleTrigger asChild>
                  <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 flex-1">
                        <div className={`w-3 h-3 rounded-full ${framework.color}`} />
                        <div>
                          <CardTitle className="text-xl">{framework.name}</CardTitle>
                          <CardDescription>{framework.description}</CardDescription>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge variant="outline" className="bg-success/10 text-success border-success/20">
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          {framework.status}
                        </Badge>
                        <Button variant="ghost" size="sm">
                          {openFramework === index ? (
                            <ChevronDown className="h-4 w-4" />
                          ) : (
                            <ChevronRight className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <CardContent className="pt-0">
                    <div className="bg-muted/50 rounded-lg p-6 space-y-4">
                      <div className="grid md:grid-cols-3 gap-4">
                        <div>
                          <div className="text-3xl font-bold text-accent mb-1">
                            {framework.clauses}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Mapped Clauses
                          </div>
                        </div>
                        <div>
                          <div className="text-3xl font-bold text-primary mb-1">
                            100%
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Coverage
                          </div>
                        </div>
                        <div>
                          <div className="text-3xl font-bold text-success mb-1">
                            Active
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Status
                          </div>
                        </div>
                      </div>
                      <div className="pt-4 border-t border-border">
                        <p className="text-sm text-muted-foreground">
                          All controls and requirements are mapped to your operational workflows, 
                          ensuring continuous compliance monitoring and automated evidence collection.
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </CollapsibleContent>
              </Card>
            </Collapsible>
          ))}
        </div>

        {/* Additional Info */}
        <Card className="bg-gradient-primary border-0 text-white">
          <CardHeader>
            <CardTitle className="text-2xl text-white">Universal Schema Architecture</CardTitle>
            <CardDescription className="text-white/80 text-base">
              Compliance tagging built into every layer of your business operations. Map ERP financial controls to SOC 2, 
              HRIS access logs to ISO 27001, CRM data handling to GDPR, supply chain records to regulatory requirements—all 
              in one unified schema engine that maintains audit readiness across your entire tech stack.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {["GDPR", "PCI DSS", "FedRAMP", "ISO 9001", "Custom Frameworks", "Operational KPIs", "Process Controls"].map((tag, idx) => (
                <span
                  key={idx}
                  className="px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-sm font-medium"
                >
                  {tag}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default Frameworks;
