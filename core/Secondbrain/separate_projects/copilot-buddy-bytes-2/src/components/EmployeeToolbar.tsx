import { Link } from "react-router-dom";
import { 
  BookOpen, 
  Workflow, 
  Brain, 
  Zap, 
  Users, 
  Calendar, 
  MessagesSquare, 
  FileText, 
  Settings, 
  BarChart3,
  Headphones,
  Briefcase,
  CreditCard,
  Shield,
  Home,
  DollarSign
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface ToolbarItem {
  name: string;
  icon: any;
  path: string;
  description: string;
}

const EmployeeToolbar = () => {
  const toolbarItems: ToolbarItem[] = [
    { name: "Home", icon: Home, path: "/portal", description: "Employee workspace home" },
    { name: "Knowledge Base", icon: BookOpen, path: "/knowledge", description: "SOPs, guides, documentation" },
    { name: "Workflows", icon: Workflow, path: "/workflow/automation", description: "Process automation" },
    { name: "AI Assistant", icon: Brain, path: "/portal", description: "AI-powered help" },
    { name: "HR Portal", icon: Users, path: "/dashboard/hr", description: "Payroll, benefits, time-off" },
    { name: "Calendar", icon: Calendar, path: "/portal", description: "Schedule and meetings" },
    { name: "Messages", icon: MessagesSquare, path: "/portal", description: "Team communication" },
    { name: "Documents", icon: FileText, path: "/knowledge", description: "Shared documents and files" },
    { name: "IT Support", icon: Headphones, path: "/dashboard/it", description: "Help desk and IT support" },
    { name: "Finance", icon: CreditCard, path: "/dashboard/finance", description: "Expenses and reimbursements" },
    { name: "Revio", icon: DollarSign, path: "/dashboard/sales", description: "Customer billing and revenue" },
    { name: "Compliance", icon: Shield, path: "/dashboard/compliance", description: "Training and certifications" },
    
  ];

  return (
    <div className="bg-card border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center gap-1 py-2 overflow-x-auto">
          <TooltipProvider delayDuration={300}>
            {toolbarItems.map((item) => (
              <Tooltip key={item.name}>
                <TooltipTrigger asChild>
                  <Link to={item.path}>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex flex-col items-center gap-1 h-auto py-2 px-3 min-w-[60px] hover:bg-primary/10"
                    >
                      <item.icon className="h-5 w-5" />
                      <span className="text-xs">{item.name}</span>
                    </Button>
                  </Link>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{item.description}</p>
                </TooltipContent>
              </Tooltip>
            ))}
          </TooltipProvider>
        </div>
      </div>
    </div>
  );
};

export default EmployeeToolbar;
