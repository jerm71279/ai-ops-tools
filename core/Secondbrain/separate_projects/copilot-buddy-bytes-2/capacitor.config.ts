import { CapacitorConfig } from '@capacitor/core';

const config: CapacitorConfig = {
  appId: 'app.lovable.2e37e4cf64eb4e9a8cf114b876d69899',
  appName: 'copilot-buddy-bytes',
  webDir: 'dist',
  server: {
    url: 'https://2e37e4cf-64eb-4e9a-8cf1-14b876d69899.lovableproject.com?forceHideBadge=true',
    cleartext: true
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 0
    }
  }
};

export default config;
