import { useState } from "react";
import { Settings, Bell, Palette, Lock, Database, Download, Upload, Sun, Moon } from "lucide-react";
import { AccessHistoryDialog } from "./AccessHistoryDialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

interface DashboardSettingsMenuProps {
  dashboardName: string;
  onExportData?: () => void;
}

export const DashboardSettingsMenu = ({ dashboardName, onExportData }: DashboardSettingsMenuProps) => {
  const [notificationDialogOpen, setNotificationDialogOpen] = useState(false);
  const [privacyDialogOpen, setPrivacyDialogOpen] = useState(false);
  const [accessHistoryOpen, setAccessHistoryOpen] = useState(false);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(false);
  const [weeklyReports, setWeeklyReports] = useState(true);

  const handleExportData = () => {
    if (onExportData) {
      onExportData();
    } else {
      // Default export functionality
      const data = {
        dashboard: dashboardName,
        exportDate: new Date().toISOString(),
        message: "Export functionality - connect your data source"
      };
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${dashboardName.toLowerCase()}-export-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success("Data exported successfully");
    }
  };

  const handleImportData = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json,.csv';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        toast.success(`Importing ${file.name}...`);
        // Add import logic here
      }
    };
    input.click();
  };

  const toggleTheme = (theme: 'light' | 'dark') => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    toast.success(`Switched to ${theme} mode`);
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="icon" className="h-9 w-9">
            <Settings className="h-4 w-4" />
            <span className="sr-only">Dashboard Settings</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56 bg-background z-[60]">
          <DropdownMenuLabel>{dashboardName} Settings</DropdownMenuLabel>
          <DropdownMenuSeparator />
          
          <DropdownMenuItem onClick={() => setNotificationDialogOpen(true)}>
            <Bell className="h-4 w-4 mr-2" />
            Notifications
          </DropdownMenuItem>
          
          <DropdownMenuSub>
            <DropdownMenuSubTrigger>
              <Palette className="h-4 w-4 mr-2" />
              Appearance
            </DropdownMenuSubTrigger>
            <DropdownMenuSubContent className="bg-background">
              <DropdownMenuItem onClick={() => toggleTheme('light')}>
                <Sun className="h-4 w-4 mr-2" />
                Light Mode
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => toggleTheme('dark')}>
                <Moon className="h-4 w-4 mr-2" />
                Dark Mode
              </DropdownMenuItem>
            </DropdownMenuSubContent>
          </DropdownMenuSub>
          
          <DropdownMenuSeparator />
          
          <DropdownMenuSub>
            <DropdownMenuSubTrigger>
              <Database className="h-4 w-4 mr-2" />
              Data Management
            </DropdownMenuSubTrigger>
            <DropdownMenuSubContent className="bg-background">
              <DropdownMenuItem onClick={handleExportData}>
                <Download className="h-4 w-4 mr-2" />
                Export Data
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleImportData}>
                <Upload className="h-4 w-4 mr-2" />
                Import Data
              </DropdownMenuItem>
            </DropdownMenuSubContent>
          </DropdownMenuSub>
          
          <DropdownMenuSeparator />
          
          <DropdownMenuItem onClick={() => setPrivacyDialogOpen(true)}>
            <Lock className="h-4 w-4 mr-2" />
            Privacy & Security
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Notification Settings Dialog */}
      <Dialog open={notificationDialogOpen} onOpenChange={setNotificationDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Notification Settings</DialogTitle>
            <DialogDescription>
              Manage your notification preferences for {dashboardName}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6 py-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="email-notifications">Email Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive email updates about important events
                </p>
              </div>
              <Switch
                id="email-notifications"
                checked={emailNotifications}
                onCheckedChange={(checked) => {
                  setEmailNotifications(checked);
                  toast.success(`Email notifications ${checked ? 'enabled' : 'disabled'}`);
                }}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="push-notifications">Push Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive browser push notifications
                </p>
              </div>
              <Switch
                id="push-notifications"
                checked={pushNotifications}
                onCheckedChange={(checked) => {
                  setPushNotifications(checked);
                  toast.success(`Push notifications ${checked ? 'enabled' : 'disabled'}`);
                }}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="weekly-reports">Weekly Reports</Label>
                <p className="text-sm text-muted-foreground">
                  Get weekly summary reports via email
                </p>
              </div>
              <Switch
                id="weekly-reports"
                checked={weeklyReports}
                onCheckedChange={(checked) => {
                  setWeeklyReports(checked);
                  toast.success(`Weekly reports ${checked ? 'enabled' : 'disabled'}`);
                }}
              />
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Privacy Settings Dialog */}
      <Dialog open={privacyDialogOpen} onOpenChange={setPrivacyDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Privacy & Security</DialogTitle>
            <DialogDescription>
              Manage your privacy and security settings
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <h4 className="font-medium">Data Privacy</h4>
              <p className="text-sm text-muted-foreground">
                Your data is encrypted and stored securely. We never share your information with third parties.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Session Security</h4>
              <p className="text-sm text-muted-foreground">
                Sessions expire after 24 hours of inactivity. You'll be automatically logged out for security.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Access Logs</h4>
              <Button 
                variant="outline" 
                className="w-full" 
                onClick={() => {
                  setPrivacyDialogOpen(false);
                  setAccessHistoryOpen(true);
                }}
              >
                View Access History
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Access History Dialog */}
      <AccessHistoryDialog 
        open={accessHistoryOpen} 
        onOpenChange={setAccessHistoryOpen}
      />
    </>
  );
};
