import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Button } from "@/components/ui/button";
import { ArrowLeft, LayoutDashboard } from "lucide-react";
import EvidenceUpload from "@/components/EvidenceUpload";

export default function ComplianceEvidenceUpload() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>

        <DashboardNavigation 
          title="Evidence Upload"
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
        
        <div className="flex items-center gap-3 mb-6">
          <Button 
            onClick={() => navigate(-1)} 
            variant="outline" 
            size="sm"
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
          <Button 
            onClick={() => navigate('/portal')} 
            variant="outline" 
            size="sm"
            className="gap-2"
          >
            <LayoutDashboard className="h-4 w-4" />
            Dashboards
          </Button>
        </div>

        <EvidenceUpload onUploadComplete={() => navigate('/compliance')} />
      </main>
    </div>
  );
}
