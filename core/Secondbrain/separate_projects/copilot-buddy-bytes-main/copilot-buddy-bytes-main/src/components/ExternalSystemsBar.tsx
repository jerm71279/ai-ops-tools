import { ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface ExternalSystem {
  name: string;
  url: string;
  description: string;
  logo?: string;
}

const ExternalSystemsBar = () => {
  const externalSystems: ExternalSystem[] = [
    { 
      name: "Microsoft 365", 
      url: "https://www.office.com", 
      description: "Email, Office apps, OneDrive" 
    },
    { 
      name: "NinjaOne", 
      url: "https://app.ninjarmm.com", 
      description: "IT management and monitoring" 
    },
    { 
      name: "UniFi", 
      url: "https://unifi.ui.com", 
      description: "Network management" 
    },
    { 
      name: "SonicWall", 
      url: "https://www.mysonicwall.com", 
      description: "Firewall and security management" 
    },
    { 
      name: "SharePoint", 
      url: "https://www.office.com/sharepoint", 
      description: "Document management and collaboration" 
    },
    { 
      name: "Teams", 
      url: "https://teams.microsoft.com", 
      description: "Communication and collaboration" 
    },
    { 
      name: "Azure Portal", 
      url: "https://portal.azure.com", 
      description: "Cloud infrastructure management" 
    },
    { 
      name: "Salesforce", 
      url: "https://login.salesforce.com", 
      description: "CRM and customer management" 
    },
    { 
      name: "Revio", 
      url: "https://app.revio.com", 
      description: "Billing and subscription management" 
    },
  ];

  return (
    <div className="bg-muted/50 border-y border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center gap-4 py-3">
          <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground min-w-fit">
            <ExternalLink className="h-4 w-4" />
            <span className="hidden sm:inline">External Systems:</span>
          </div>
          <div className="flex items-center gap-2 overflow-x-auto flex-1">
            <TooltipProvider delayDuration={300}>
              {externalSystems.map((system) => (
                <Tooltip key={system.name}>
                  <TooltipTrigger asChild>
                    <a 
                      href={system.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      <Button
                        variant="outline"
                        size="sm"
                        className="whitespace-nowrap hover:bg-background hover:border-primary"
                      >
                        {system.name}
                        <ExternalLink className="h-3 w-3 ml-2" />
                      </Button>
                    </a>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{system.description}</p>
                  </TooltipContent>
                </Tooltip>
              ))}
            </TooltipProvider>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExternalSystemsBar;
