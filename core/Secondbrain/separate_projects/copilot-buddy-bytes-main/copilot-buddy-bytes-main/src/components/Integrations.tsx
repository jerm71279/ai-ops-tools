import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { 
  Webhook, 
  Database, 
  Cloud, 
  Mail, 
  MessageSquare, 
  FileSpreadsheet,
  Lock,
  GitBranch,
  Users2,
  Building,
  CalendarCheck,
  FileText,
  ArrowRight
} from "lucide-react";

const integrationCategories = [
  {
    category: "Billing & Revenue",
    icon: Building,
    integrations: [
      { name: "Onebill", logo: "💳" },
      { name: "rev.io", logo: "💰" },
    ],
  },
  {
    category: "Cloud & Identity Management",
    icon: Cloud,
    integrations: [
      { name: "Azure", logo: "☁️" },
      { name: "Lighthouse", logo: "🔦" },
      { name: "CIPP", logo: "🔷" },
    ],
  },
  {
    category: "Network Security",
    icon: Lock,
    integrations: [
      { name: "SonicWall", logo: "🔥" },
      { name: "UniFi", logo: "📡" },
      { name: "MikroTik", logo: "🌐" },
    ],
  },
  {
    category: "Security & Access Management",
    icon: Lock,
    integrations: [
      { name: "Keeper Security", logo: "🔐" },
      { name: "Keeper MSP", logo: "🛡️" },
      { name: "Connection Manager", logo: "🔑" },
    ],
  },
  {
    category: "RMM & Infrastructure",
    icon: GitBranch,
    integrations: [
      { name: "NinjaOne", logo: "🥷" },
    ],
  },
  {
    category: "Cybersecurity & Threat Management",
    icon: Lock,
    integrations: [
      { name: "Threatdown", logo: "⚔️" },
      { name: "OpenText", logo: "🛡️" },
    ],
  },
];

const apiFeatures = [
  {
    icon: Webhook,
    title: "Real-Time Cross-System Sync",
    description: "Bi-directional data flow across billing, Azure, RMM, network security, and all connected MSP systems with compliance tagging preserved.",
  },
  {
    icon: Database,
    title: "Intelligent Schema Mapping",
    description: "AI-powered field mapping across systems with automatic clause linkage—map Azure controls to SOC 2, RMM logs to ISO 27001.",
  },
  {
    icon: FileSpreadsheet,
    title: "Universal Workflow Engine",
    description: "Automate MSP processes that span multiple systems while maintaining full audit trails and compliance tagging.",
  },
];

const Integrations = () => {
  return (
    <section className="py-24 bg-secondary/30">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Unified System Integration
          </h2>
          <p className="text-xl text-muted-foreground">
            Connect your MSP tech stack—billing, cloud management, network security, RMM, and cybersecurity. 
            Our clause-linked architecture maps operational data across all systems for unified intelligence and compliance.
          </p>
        </div>

        {/* Integration Categories */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {integrationCategories.map((category, index) => {
            const Icon = category.icon;
            return (
              <Card key={index} className="border-border hover:shadow-elevated transition-all duration-300">
                <CardHeader>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                      <Icon className="h-5 w-5 text-accent" />
                    </div>
                    <CardTitle className="text-lg">{category.category}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {category.integrations.map((integration, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 p-2 rounded-lg bg-background border border-border hover:border-accent/50 transition-colors"
                      >
                        <span className="text-2xl">{integration.logo}</span>
                        <span className="text-sm font-medium truncate">
                          {integration.name}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* API Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {apiFeatures.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="border-border text-center">
                <CardHeader>
                  <div className="w-12 h-12 mx-auto rounded-lg bg-gradient-accent flex items-center justify-center mb-3">
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>

        {/* CTA Card */}
        <Card className="bg-gradient-hero border-0 text-white text-center">
          <CardHeader>
            <CardTitle className="text-2xl text-white mb-2">
              Ready to Connect Your Systems?
            </CardTitle>
            <CardDescription className="text-white/80 text-base mb-4">
              See detailed integration guides, security information, and setup requirements for all MSP platforms.
            </CardDescription>
            <Link to="/integrations">
              <Button size="lg" variant="hero" className="bg-white text-primary hover:bg-white/90">
                View All Integrations
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Badge variant="outline" className="bg-white/10 border-white/30 text-white text-sm py-2 px-4">
                <FileText className="h-4 w-4 mr-2" />
                API Documentation
              </Badge>
              <Badge variant="outline" className="bg-white/10 border-white/30 text-white text-sm py-2 px-4">
                <CalendarCheck className="h-4 w-4 mr-2" />
                Schedule Integration Call
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default Integrations;
