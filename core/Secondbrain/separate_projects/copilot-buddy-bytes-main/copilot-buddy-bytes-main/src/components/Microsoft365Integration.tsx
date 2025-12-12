import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar, Mail, User, FileText, Loader2, MessageSquare } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";

interface UserProfile {
  displayName: string;
  mail: string;
  jobTitle?: string;
  department?: string;
  officeLocation?: string;
}

interface CalendarEvent {
  subject: string;
  start: { dateTime: string; timeZone: string };
  end: { dateTime: string; timeZone: string };
  location?: { displayName: string };
  organizer: { emailAddress: { name: string; address: string } };
}

interface Email {
  subject: string;
  from: { emailAddress: { name: string; address: string } };
  receivedDateTime: string;
  bodyPreview: string;
  isRead: boolean;
}

interface TeamsChat {
  id: string;
  topic: string;
  lastUpdatedDateTime: string;
  chatType: string;
}

interface TeamsMessage {
  id: string;
  createdDateTime: string;
  body: { content: string };
  from: { user: { displayName: string } };
}

export const Microsoft365Integration = () => {
  const [loading, setLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>([]);
  const [emails, setEmails] = useState<Email[]>([]);
  const [teamsChats, setTeamsChats] = useState<TeamsChat[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [hasAzureProvider, setHasAzureProvider] = useState<boolean | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);

  useEffect(() => {
    checkAuthProvider();
  }, []);

  const checkAuthProvider = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        setError('Please sign in to access Microsoft 365 integration');
        setLoading(false);
        return;
      }

      // Check if user has Azure provider
      const hasAzure = user.app_metadata?.providers?.includes('azure') || 
                       user.app_metadata?.provider === 'azure';
      
      setHasAzureProvider(hasAzure);

      if (hasAzure) {
        await loadMicrosoftData();
      } else {
        setLoading(false);
      }
    } catch (err) {
      console.error('Error checking auth provider:', err);
      setError('Failed to verify authentication');
      setLoading(false);
    }
  };

  const handleConnectMicrosoft365 = async () => {
    setIsConnecting(true);
    try {
      const { error } = await supabase.auth.linkIdentity({
        provider: 'azure',
        options: {
          scopes: 'openid email profile User.Read Calendars.Read Mail.Read Files.Read.All Chat.Read',
          redirectTo: `${window.location.origin}/portal?tab=microsoft365`,
        }
      });

      if (error) throw error;
      
      // The user will be redirected to Microsoft login
      toast.info('Redirecting to Microsoft 365...');
    } catch (err: any) {
      console.error('Error connecting Microsoft 365:', err);
      toast.error(err.message || 'Failed to connect Microsoft 365');
      setIsConnecting(false);
    }
  };

  const callGraphAPI = async (endpoint: string) => {
    const { data, error } = await supabase.functions.invoke('graph-api', {
      body: { endpoint }
    });

    if (error) throw error;
    if (data.error) throw new Error(data.error);
    return data;
  };

  const loadMicrosoftData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load user profile
      const profile = await callGraphAPI('/me');
      setUserProfile(profile);

      // Load calendar events (next 5 events)
      const today = new Date().toISOString();
      const endDate = new Date();
      endDate.setMonth(endDate.getMonth() + 1);
      const events = await callGraphAPI(
        `/me/calendar/calendarView?startDateTime=${today}&endDateTime=${endDate.toISOString()}&$top=5&$orderby=start/dateTime`
      );
      setCalendarEvents(events.value || []);

      // Load recent emails (top 10)
      const messages = await callGraphAPI('/me/messages?$top=10&$orderby=receivedDateTime DESC');
      setEmails(messages.value || []);

      // Load Teams chats (top 10)
      const chats = await callGraphAPI('/me/chats?$top=10&$orderby=lastUpdatedDateTime DESC');
      setTeamsChats(chats.value || []);

    } catch (err: any) {
      console.error('Error loading Microsoft data:', err);
      
      // Handle different error types
      if (err.message?.includes('WRONG_PROVIDER')) {
        setError('This account is not connected to Microsoft 365. Please sign out and sign in with your Microsoft 365 account.');
      } else if (err.message?.includes('TOKEN_EXPIRED') || err.message?.includes('NO_PROVIDER_TOKEN')) {
        setError('Your Microsoft 365 session has expired. Please sign out and sign in again.');
      } else if (err.message?.includes('PERMISSION_DENIED')) {
        setError('Permission denied. Your administrator needs to grant consent in Azure AD. Please contact your IT department.');
      } else if (err.message?.includes('RATE_LIMIT')) {
        setError('Too many requests. Please wait a moment and try again.');
      } else if (err.message?.includes('sign in with Microsoft')) {
        setError('Please sign in with Microsoft 365 to access this data.');
      } else {
        setError(err.message || 'Failed to load Microsoft 365 data. Please try again later.');
        toast.error('Failed to load Microsoft 365 data');
      }
    } finally {
      setLoading(false);
    }
  };

  // Show connect button if user doesn't have Azure provider
  if (hasAzureProvider === false && !loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Connect Microsoft 365
          </CardTitle>
          <CardDescription>
            Link your Microsoft 365 account to access Outlook, Calendar, Teams, and more
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg border bg-muted p-4">
            <p className="text-sm mb-4">
              To access your Microsoft 365 applications and data, connect your Microsoft account. This will enable:
            </p>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground ml-2">
              <li>Outlook email access</li>
              <li>Calendar events and scheduling</li>
              <li>OneDrive file management</li>
              <li>Teams chats and channels</li>
              <li>SharePoint documents</li>
            </ul>
          </div>
          
          <button
            onClick={handleConnectMicrosoft365}
            disabled={isConnecting}
            className="w-full h-12 flex items-center justify-center gap-2 bg-primary text-primary-foreground hover:bg-primary/90 rounded-md font-medium transition-colors disabled:opacity-50"
          >
            {isConnecting ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Connecting...
              </>
            ) : (
              <>
                <svg className="h-5 w-5" viewBox="0 0 23 23">
                  <path fill="currentColor" opacity="0.6" d="M0 0h11v11H0z"/>
                  <path fill="currentColor" opacity="0.8" d="M12 0h11v11H12z"/>
                  <path fill="currentColor" opacity="0.6" d="M0 12h11v11H0z"/>
                  <path fill="currentColor" d="M12 12h11v11H12z"/>
                </svg>
                Connect Microsoft 365 Account
              </>
            )}
          </button>
          
          <p className="text-xs text-muted-foreground text-center">
            You'll be redirected to Microsoft to authorize access. Your existing account will remain unchanged.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    const isAuthError = error.includes('sign in') || error.includes('session has expired') || error.includes('not connected');
    const isPermissionError = error.includes('Permission denied') || error.includes('administrator');
    
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Microsoft 365 Integration
          </CardTitle>
          <CardDescription>
            {isAuthError && "Authentication required to access Microsoft 365 data"}
            {isPermissionError && "Additional permissions needed"}
            {!isAuthError && !isPermissionError && "Unable to load Microsoft 365 data"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-800 dark:bg-yellow-950">
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              {error}
            </p>
          </div>
          
          {isAuthError && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Your Microsoft 365 session has expired or is not connected.
              </p>
              <button
                onClick={handleConnectMicrosoft365}
                disabled={isConnecting}
                className="w-full h-10 flex items-center justify-center gap-2 bg-primary text-primary-foreground hover:bg-primary/90 rounded-md font-medium transition-colors disabled:opacity-50"
              >
                {isConnecting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Reconnecting...
                  </>
                ) : (
                  'Reconnect Microsoft 365'
                )}
              </button>
            </div>
          )}
          
          {isPermissionError && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Your IT administrator needs to:
              </p>
              <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
                <li>Open Azure Portal → App registrations</li>
                <li>Find the OberaConnect app</li>
                <li>Navigate to API permissions</li>
                <li>Grant admin consent for all permissions</li>
              </ol>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Microsoft 365 Profile
          </CardTitle>
        </CardHeader>
        <CardContent>
          {userProfile && (
            <div className="space-y-2">
              <div>
                <span className="font-semibold">Name:</span> {userProfile.displayName}
              </div>
              <div>
                <span className="font-semibold">Email:</span> {userProfile.mail}
              </div>
              {userProfile.jobTitle && (
                <div>
                  <span className="font-semibold">Title:</span> {userProfile.jobTitle}
                </div>
              )}
              {userProfile.department && (
                <div>
                  <span className="font-semibold">Department:</span> {userProfile.department}
                </div>
              )}
              {userProfile.officeLocation && (
                <div>
                  <span className="font-semibold">Office:</span> {userProfile.officeLocation}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="calendar" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="calendar">
            <Calendar className="h-4 w-4 mr-2" />
            Calendar
          </TabsTrigger>
          <TabsTrigger value="email">
            <Mail className="h-4 w-4 mr-2" />
            Email
          </TabsTrigger>
          <TabsTrigger value="teams">
            <MessageSquare className="h-4 w-4 mr-2" />
            Teams
          </TabsTrigger>
        </TabsList>

        <TabsContent value="calendar" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Events</CardTitle>
              <CardDescription>Your next calendar events</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {calendarEvents.length === 0 ? (
                <p className="text-muted-foreground">No upcoming events</p>
              ) : (
                calendarEvents.map((event, idx) => (
                  <div key={idx} className="border-l-4 border-primary pl-4 py-2">
                    <div className="font-semibold">{event.subject}</div>
                    <div className="text-sm text-muted-foreground">
                      {new Date(event.start.dateTime).toLocaleString()}
                    </div>
                    {event.location?.displayName && (
                      <div className="text-sm text-muted-foreground">
                        📍 {event.location.displayName}
                      </div>
                    )}
                    <div className="text-sm text-muted-foreground">
                      Organizer: {event.organizer.emailAddress.name}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="email" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Emails</CardTitle>
              <CardDescription>Your latest messages</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {emails.length === 0 ? (
                <p className="text-muted-foreground">No recent emails</p>
              ) : (
                emails.map((email, idx) => (
                  <div key={idx} className="border-b pb-4 last:border-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="font-semibold flex-1">{email.subject}</div>
                      {!email.isRead && (
                        <Badge variant="default">New</Badge>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      From: {email.from.emailAddress.name} ({email.from.emailAddress.address})
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {new Date(email.receivedDateTime).toLocaleString()}
                    </div>
                    <div className="text-sm mt-2 line-clamp-2">
                      {email.bodyPreview}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="teams" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Teams Chats</CardTitle>
              <CardDescription>Your latest Teams conversations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {teamsChats.length === 0 ? (
                <p className="text-muted-foreground">No recent chats</p>
              ) : (
                teamsChats.map((chat, idx) => (
                  <div key={idx} className="border-b pb-4 last:border-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className="font-semibold flex items-center gap-2">
                          <MessageSquare className="h-4 w-4 text-primary" />
                          {chat.topic || "Untitled Chat"}
                        </div>
                        <div className="text-sm text-muted-foreground mt-1">
                          Type: {chat.chatType}
                        </div>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {new Date(chat.lastUpdatedDateTime).toLocaleDateString()}
                      </Badge>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
