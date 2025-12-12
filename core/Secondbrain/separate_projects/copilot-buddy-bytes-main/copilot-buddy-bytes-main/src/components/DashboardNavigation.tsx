import React from "react";

// DashboardNavigation has been deprecated in favor of the global DashboardPortalLanes.
// Keeping the same API to avoid breaking pages that still import/use it.
// It now renders nothing so there are no duplicate back buttons or scrollers.

interface Dashboard {
  name: string;
  path: string;
}

interface DashboardNavigationProps {
  title?: string;
  showTitle?: boolean;
  dashboardPath?: string;
  dashboards?: Dashboard[];
}

const DashboardNavigation: React.FC<DashboardNavigationProps> = () => {
  return null;
};

export default DashboardNavigation;
