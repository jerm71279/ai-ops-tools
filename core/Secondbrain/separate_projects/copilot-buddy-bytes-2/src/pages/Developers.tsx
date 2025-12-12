import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Github, BookOpen, Code2, Database, FileText, ExternalLink, Workflow, Shield, Zap, Network } from "lucide-react";
import { Link } from "react-router-dom";

const Developers = () => {
  const docs = [
    {
      title: "Architecture",
      description: "Complete system architecture and design patterns",
      icon: Database,
      file: "ARCHITECTURE.md",
      category: "Core",
      diagram: true
    },
    {
      title: "API Reference",
      description: "Full API documentation for all endpoints",
      icon: Code2,
      file: "API_REFERENCE.md",
      category: "Integration"
    },
    {
      title: "Component Library",
      description: "UI component documentation and usage",
      icon: FileText,
      file: "COMPONENT_LIBRARY.md",
      category: "Frontend"
    },
    {
      title: "Dashboard Data Flows",
      description: "Data flow diagrams for all dashboards",
      icon: Workflow,
      file: "DASHBOARD_DATA_FLOWS.md",
      category: "Architecture"
    },
    {
      title: "Testing Guide",
      description: "Testing procedures and validation",
      icon: Shield,
      file: "TESTING_GUIDE.md",
      category: "QA"
    },
    {
      title: "Platform Features",
      description: "Complete feature index and capabilities",
      icon: Zap,
      file: "PLATFORM_FEATURE_INDEX.md",
      category: "Reference"
    }
  ];

  const integrationDocs = [
    {
      title: "CIPP Integration",
      description: "Microsoft 365 tenant management integration",
      file: "CIPP_INTEGRATION_GUIDE.md"
    },
    {
      title: "Revio Integration",
      description: "Billing and revenue data integration",
      file: "REVIO_INTEGRATION_GUIDE.md"
    },
    {
      title: "Microsoft 365",
      description: "Calendar, email, and Teams integration",
      file: "MICROSOFT365_INTEGRATION.md"
    },
    {
      title: "CMDB & Change Management",
      description: "Configuration management database guide",
      file: "CMDB_CHANGE_MANAGEMENT_GUIDE.md"
    }
  ];

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navigation />
      
      <main className="flex-1 pt-32 pb-16">
        <div className="container mx-auto px-4 max-w-7xl">
          {/* Header */}
          <div className="text-center mb-16">
            <Badge variant="secondary" className="mb-4">
              <Github className="h-3 w-3 mr-1" />
              Open Source
            </Badge>
            <h1 className="text-5xl font-bold mb-4">
              Developer Portal
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Access the full codebase, documentation, and API references. Built with React, TypeScript, and Supabase.
            </p>
          </div>

          {/* GitHub Repository */}
          <Card className="mb-12 bg-gradient-to-br from-primary/5 to-accent/5 border-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <Github className="h-6 w-6" />
                GitHub Repository
              </CardTitle>
              <CardDescription>
                View the complete source code, commit history, and contribute to the project
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-4">
                <a 
                  href="https://github.com/yourusername/oberaconnect" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex-1 min-w-[250px]"
                >
                  <Button variant="default" size="lg" className="w-full">
                    <Github className="mr-2 h-5 w-5" />
                    View on GitHub
                    <ExternalLink className="ml-2 h-4 w-4" />
                  </Button>
                </a>
                <a 
                  href="https://github.com/yourusername/oberaconnect/issues" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex-1 min-w-[250px]"
                >
                  <Button variant="outline" size="lg" className="w-full">
                    <FileText className="mr-2 h-5 w-5" />
                    Issues & Bug Reports
                    <ExternalLink className="ml-2 h-4 w-4" />
                  </Button>
                </a>
              </div>
              
              <div className="grid md:grid-cols-3 gap-4 pt-4">
                <div className="text-center p-4 bg-background/50 rounded-lg">
                  <div className="text-2xl font-bold text-primary">64+</div>
                  <div className="text-sm text-muted-foreground">Pages</div>
                </div>
                <div className="text-center p-4 bg-background/50 rounded-lg">
                  <div className="text-2xl font-bold text-primary">55+</div>
                  <div className="text-sm text-muted-foreground">Database Tables</div>
                </div>
                <div className="text-center p-4 bg-background/50 rounded-lg">
                  <div className="text-2xl font-bold text-primary">17</div>
                  <div className="text-sm text-muted-foreground">Edge Functions</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Core Documentation */}
          <div className="mb-12">
            <div className="flex items-center gap-2 mb-6">
              <BookOpen className="h-6 w-6 text-primary" />
              <h2 className="text-3xl font-bold">Core Documentation</h2>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {docs.map((doc) => {
                const Icon = doc.icon;
                return (
                  <Card key={doc.file} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between mb-2">
                        <Icon className="h-8 w-8 text-primary" />
                        <Badge variant="secondary">{doc.category}</Badge>
                      </div>
                      <CardTitle className="text-lg">{doc.title}</CardTitle>
                      <CardDescription>{doc.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <a 
                          href={`https://github.com/yourusername/oberaconnect/blob/main/${doc.file}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <Button variant="outline" className="w-full">
                            <FileText className="mr-2 h-4 w-4" />
                            View Documentation
                            <ExternalLink className="ml-2 h-4 w-4" />
                          </Button>
                        </a>
                        {doc.diagram && (
                          <Link to="/architecture-diagram">
                            <Button variant="secondary" className="w-full">
                              <Network className="mr-2 h-4 w-4" />
                              View Full Diagram
                            </Button>
                          </Link>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Integration Guides */}
          <div className="mb-12">
            <div className="flex items-center gap-2 mb-6">
              <Code2 className="h-6 w-6 text-primary" />
              <h2 className="text-3xl font-bold">Integration Guides</h2>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              {integrationDocs.map((doc) => (
                <Card key={doc.file} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{doc.title}</CardTitle>
                    <CardDescription>{doc.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <a 
                      href={`https://github.com/yourusername/oberaconnect/blob/main/${doc.file}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Button variant="outline" className="w-full">
                        <FileText className="mr-2 h-4 w-4" />
                        View Guide
                        <ExternalLink className="ml-2 h-4 w-4" />
                      </Button>
                    </a>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Tech Stack */}
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Technology Stack</CardTitle>
              <CardDescription>
                Modern, scalable architecture built on proven technologies
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">Frontend</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• React 18</li>
                    <li>• TypeScript</li>
                    <li>• Vite</li>
                    <li>• Tailwind CSS</li>
                    <li>• shadcn/ui</li>
                  </ul>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">Backend</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Supabase</li>
                    <li>• PostgreSQL</li>
                    <li>• Edge Functions</li>
                    <li>• Row Level Security</li>
                    <li>• Real-time</li>
                  </ul>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">State Management</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• TanStack Query</li>
                    <li>• React Router v6</li>
                    <li>• Custom Hooks</li>
                    <li>• Context API</li>
                  </ul>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">Integrations</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Microsoft 365</li>
                    <li>• CIPP</li>
                    <li>• NinjaOne</li>
                    <li>• Revio</li>
                    <li>• Lovable AI</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Start */}
          <Card className="mt-12">
            <CardHeader>
              <CardTitle className="text-2xl">Quick Start</CardTitle>
              <CardDescription>
                Get the project running locally in minutes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-muted p-4 rounded-lg font-mono text-sm space-y-2">
                <div># Clone the repository</div>
                <div className="text-primary">git clone https://github.com/yourusername/oberaconnect.git</div>
                <div className="mt-4"># Install dependencies</div>
                <div className="text-primary">npm install</div>
                <div className="mt-4"># Set up environment variables</div>
                <div className="text-primary">cp .env.example .env</div>
                <div className="mt-4"># Run development server</div>
                <div className="text-primary">npm run dev</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Developers;
