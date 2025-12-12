import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import Footer from "@/components/Footer";
import { Shield, Lock, Database, Zap, CheckCircle2, AlertCircle } from "lucide-react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { useNavigate } from "react-router-dom";

const integrationDetails = [
  {
    category: "Billing & Revenue Management",
    systems: [
      {
        name: "Onebill",
        logo: "💳",
        authMethod: "API Keys + OAuth 2.0",
        permissions: ["Read billing data", "Access customer accounts", "View invoices", "Read payment history"],
        dataAccessed: ["Customer billing records", "Invoice history", "Payment transactions", "Subscription data", "Revenue reports"],
        setupTime: "2-3 hours",
        complexity: "Medium"
      },
      {
        name: "rev.io",
        logo: "💰",
        authMethod: "API Keys",
        permissions: ["Read billing data", "Access revenue streams", "View subscriptions", "Read usage data"],
        dataAccessed: ["Billing records", "Revenue analytics", "Subscription management", "Usage tracking"],
        setupTime: "1-2 hours",
        complexity: "Low"
      }
    ]
  },
  {
    category: "Cloud & Identity Management",
    systems: [
      {
        name: "Microsoft Azure",
        logo: "☁️",
        authMethod: "OAuth 2.0 + Service Principal",
        permissions: ["Read tenant data", "Access Azure AD", "View resources", "Manage subscriptions"],
        dataAccessed: ["Tenant configuration", "User identities", "Resource inventory", "Security logs", "Billing data"],
        setupTime: "2-4 hours",
        complexity: "High"
      },
      {
        name: "Azure Lighthouse",
        logo: "🔦",
        authMethod: "Azure AD Integration",
        permissions: ["Manage customer tenants", "Delegate access", "View resources", "Read activity logs"],
        dataAccessed: ["Multi-tenant management", "Customer resources", "Delegation records", "Activity logs"],
        setupTime: "3-4 hours",
        complexity: "High"
      },
      {
        name: "CIPP (CyberDrain)",
        logo: "🔷",
        authMethod: "API Keys + Azure Integration",
        permissions: ["Read tenant data", "Access automation logs", "View security alerts", "Manage policies"],
        dataAccessed: ["Tenant configurations", "Security baselines", "Automation logs", "Policy compliance"],
        setupTime: "1-2 hours",
        complexity: "Medium"
      }
    ]
  },
  {
    category: "Network Security Infrastructure",
    systems: [
      {
        name: "SonicWall",
        logo: "🔥",
        authMethod: "API Keys + SNMP",
        permissions: ["Read firewall logs", "Access security events", "View VPN connections", "Read threat data"],
        dataAccessed: ["Firewall logs", "Intrusion detection", "VPN activity", "Threat intelligence", "Network traffic"],
        setupTime: "1-2 hours",
        complexity: "Medium"
      },
      {
        name: "UniFi",
        logo: "📡",
        authMethod: "Local Controller API",
        permissions: ["Read network stats", "Access device info", "View client data", "Read event logs"],
        dataAccessed: ["Network topology", "Device health", "Client connections", "Bandwidth usage", "Event logs"],
        setupTime: "30 minutes",
        complexity: "Low"
      },
      {
        name: "MikroTik",
        logo: "🌐",
        authMethod: "API + SSH",
        permissions: ["Read router config", "Access logs", "View interfaces", "Read routing tables"],
        dataAccessed: ["Router configuration", "System logs", "Interface statistics", "Routing data", "Bandwidth metrics"],
        setupTime: "1 hour",
        complexity: "Medium"
      }
    ]
  },
  {
    category: "Security & Access Management",
    systems: [
      {
        name: "Keeper Security Vault",
        logo: "🔐",
        authMethod: "SSO + API Keys",
        permissions: ["Read vault data", "Access shared folders", "View audit logs", "Manage policies"],
        dataAccessed: ["Password vault entries", "Shared credentials", "Access logs", "Security policies", "User activity"],
        setupTime: "1-2 hours",
        complexity: "Low"
      },
      {
        name: "Keeper Connection Manager",
        logo: "🔑",
        authMethod: "SSO + API Integration",
        permissions: ["Read connection logs", "Access session data", "View policies", "Manage gateways"],
        dataAccessed: ["Remote connections", "Session recordings", "Access policies", "Gateway health", "User sessions"],
        setupTime: "2-3 hours",
        complexity: "Medium"
      }
    ]
  },
  {
    category: "RMM & Infrastructure Management",
    systems: [
      {
        name: "NinjaOne",
        logo: "🥷",
        authMethod: "OAuth 2.0 + API Keys",
        permissions: ["Read device data", "Access monitoring", "View tickets", "Read patch status"],
        dataAccessed: ["Device inventory", "System health", "Patch management", "Backup status", "Ticket history", "Script logs"],
        setupTime: "2-3 hours",
        complexity: "Medium"
      }
    ]
  },
  {
    category: "Cybersecurity & Threat Management",
    systems: [
      {
        name: "Threatdown",
        logo: "⚔️",
        authMethod: "API Keys",
        permissions: ["Read threat data", "Access alerts", "View quarantine", "Read scan logs"],
        dataAccessed: ["Threat detections", "Security alerts", "Quarantine events", "Scan results", "Malware intelligence"],
        setupTime: "1 hour",
        complexity: "Low"
      },
      {
        name: "OpenText (Webroot)",
        logo: "🛡️",
        authMethod: "API Keys + Console Access",
        permissions: ["Read endpoint data", "Access threat intelligence", "View policies", "Read reports"],
        dataAccessed: ["Endpoint protection status", "Threat intelligence", "Security policies", "Compliance reports", "Agent health"],
        setupTime: "1-2 hours",
        complexity: "Medium"
      }
    ]
  }
];

const securityFeatures = [
  {
    icon: Lock,
    title: "End-to-End Encryption",
    description: "All data in transit uses TLS 1.3. Data at rest encrypted with AES-256."
  },
  {
    icon: Shield,
    title: "Zero-Knowledge Architecture",
    description: "Your credentials are encrypted with keys only you control. We never see them."
  },
  {
    icon: Database,
    title: "Secure Credential Storage",
    description: "All API keys and OAuth tokens stored in encrypted vaults with HSM backing."
  },
  {
    icon: CheckCircle2,
    title: "Compliance-Ready",
    description: "SOC 2 Type II, ISO 27001, GDPR, and HIPAA compliant infrastructure."
  }
];

const IntegrationsPage = () => {
  const navigate = useNavigate();

  const scrollToSection = (sectionId: string) => {
    navigate('/');
    setTimeout(() => {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  };
  return (
    <div className="min-h-screen">
      <Navigation />
      
      <main className="pt-24 pb-16">
        <div className="container mx-auto px-4">
          <DashboardNavigation 
            title="Integrations"
            dashboards={[
              { name: "Admin Dashboard", path: "/admin" },
              { name: "Employee Portal", path: "/portal" },
              { name: "Analytics Portal", path: "/analytics" },
              { name: "Compliance Portal", path: "/compliance" },
              { name: "Change Management", path: "/change-management" },
              { name: "Executive Dashboard", path: "/dashboard/executive" },
              { name: "Finance Dashboard", path: "/dashboard/finance" },
              { name: "HR Dashboard", path: "/dashboard/hr" },
              { name: "IT Dashboard", path: "/dashboard/it" },
              { name: "Operations Dashboard", path: "/dashboard/operations" },
              { name: "Sales Dashboard", path: "/dashboard/sales" },
              { name: "SOC Dashboard", path: "/dashboard/soc" },
            ]}
          />
        </div>
        {/* Hero Section */}
        <section className="py-16 bg-gradient-primary text-white">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center">
              <Badge className="mb-4 bg-white/20 text-white border-white/30">
                <Zap className="h-3 w-3 mr-1" />
                Complete MSP Stack Integration
              </Badge>
              <h1 className="text-4xl md:text-5xl font-bold mb-6">
                Connect Your Business Systems
              </h1>
              <p className="text-xl text-white/90 mb-8">
                Securely integrate with billing platforms, Azure, network security, RMM, and cybersecurity tools. 
                The more systems you connect, the smarter your ML-powered insights become.
              </p>
            </div>
          </div>
        </section>

        {/* Security Section */}
        <section className="py-16 bg-background">
          <div className="container mx-auto px-4">
            <div className="text-center max-w-3xl mx-auto mb-12">
              <h2 className="text-3xl font-bold mb-4">Enterprise-Grade Security</h2>
              <p className="text-lg text-muted-foreground">
                Your data security is our top priority. Every integration is protected with multiple layers of encryption and security controls.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
              {securityFeatures.map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <Card key={index} className="border-border">
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

        {/* Integration Details */}
        <section className="py-16 bg-accent/5">
          <div className="container mx-auto px-4">
            <div className="text-center max-w-3xl mx-auto mb-12">
              <h2 className="text-3xl font-bold mb-4">Integration Details</h2>
              <p className="text-lg text-muted-foreground">
                See exactly what permissions are needed, what data is accessed, and how long setup takes for each MSP platform.
              </p>
            </div>

            <div className="max-w-5xl mx-auto space-y-8">
              {integrationDetails.map((category, catIndex) => (
                <Card key={catIndex} className="border-border shadow-elevated">
                  <CardHeader>
                    <CardTitle className="text-2xl">{category.category}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Accordion type="single" collapsible className="w-full">
                      {category.systems.map((system, sysIndex) => (
                        <AccordionItem key={sysIndex} value={`system-${catIndex}-${sysIndex}`}>
                          <AccordionTrigger className="hover:no-underline">
                            <div className="flex items-center gap-3 text-left">
                              <span className="text-2xl">{system.logo}</span>
                              <div>
                                <div className="font-semibold text-lg">{system.name}</div>
                                <div className="text-sm text-muted-foreground">
                                  {system.authMethod} • Setup: {system.setupTime}
                                </div>
                              </div>
                              <Badge 
                                variant="outline" 
                                className={`ml-auto ${
                                  system.complexity === 'Low' ? 'bg-green-500/10 text-green-700 border-green-500/20' :
                                  system.complexity === 'Medium' ? 'bg-yellow-500/10 text-yellow-700 border-yellow-500/20' :
                                  'bg-red-500/10 text-red-700 border-red-500/20'
                                }`}
                              >
                                {system.complexity} Complexity
                              </Badge>
                            </div>
                          </AccordionTrigger>
                          <AccordionContent>
                            <div className="pt-4 space-y-6">
                              {/* Authentication Method */}
                              <div>
                                <h4 className="font-semibold mb-2 flex items-center gap-2">
                                  <Lock className="h-4 w-4 text-accent" />
                                  Authentication Method
                                </h4>
                                <p className="text-sm text-muted-foreground">{system.authMethod}</p>
                              </div>

                              {/* Permissions Required */}
                              <div>
                                <h4 className="font-semibold mb-2 flex items-center gap-2">
                                  <CheckCircle2 className="h-4 w-4 text-accent" />
                                  Permissions Required
                                </h4>
                                <ul className="space-y-1">
                                  {system.permissions.map((perm, permIndex) => (
                                    <li key={permIndex} className="text-sm text-muted-foreground flex items-center gap-2">
                                      <div className="w-1.5 h-1.5 rounded-full bg-accent" />
                                      {perm}
                                    </li>
                                  ))}
                                </ul>
                              </div>

                              {/* Data Accessed */}
                              <div>
                                <h4 className="font-semibold mb-2 flex items-center gap-2">
                                  <Database className="h-4 w-4 text-accent" />
                                  Data Accessed
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                  {system.dataAccessed.map((data, dataIndex) => (
                                    <Badge key={dataIndex} variant="outline" className="bg-accent/5">
                                      {data}
                                    </Badge>
                                  ))}
                                </div>
                              </div>

                              {/* Setup Information */}
                              <div className="bg-muted/50 rounded-lg p-4">
                                <div className="flex items-start gap-2">
                                  <AlertCircle className="h-5 w-5 text-accent mt-0.5" />
                                  <div>
                                    <h4 className="font-semibold mb-1">Setup Notes</h4>
                                    <p className="text-sm text-muted-foreground">
                                      Estimated setup time: {system.setupTime}. You'll need admin access to {system.name} 
                                      to authorize the connection. All credentials are encrypted and never stored in plain text.
                                    </p>
                                  </div>
                                </div>
                              </div>

                              <Button className="w-full" onClick={() => navigate('/auth')}>
                                Connect {system.name}
                              </Button>
                            </div>
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 bg-background">
          <div className="container mx-auto px-4">
            <Card className="border-border shadow-elevated bg-gradient-to-br from-accent/5 to-background max-w-4xl mx-auto">
              <CardHeader className="text-center">
                <CardTitle className="text-3xl mb-4">Ready to Connect Your Systems?</CardTitle>
                <CardDescription className="text-lg">
                  Start with your core MSP systems and expand as you see the value. 
                  The more you connect, the smarter your operational intelligence becomes.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg" variant="hero" onClick={() => navigate('/auth')}>
                  Start Free Trial
                </Button>
                <Button size="lg" variant="outline" onClick={() => scrollToSection('case-study')}>
                  Schedule Demo
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default IntegrationsPage;