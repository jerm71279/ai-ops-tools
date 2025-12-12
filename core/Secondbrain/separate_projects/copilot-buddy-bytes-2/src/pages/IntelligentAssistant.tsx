import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import {
  LogOut,
  Brain,
  Send,
  Lightbulb,
  FileText,
  TrendingUp,
  Sparkles,
} from "lucide-react";
import DashboardNavigation from "@/components/DashboardNavigation";
import { v4 as uuidv4 } from "uuid";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: { id: string; title: string; type: string }[];
  insight?: { title: string; confidence: number };
  timestamp: Date;
}

interface LearningMetric {
  total_interactions: number;
  insights_generated: number;
  articles_created: number;
  avg_confidence_score: number;
  knowledge_base_size: number;
}

const IntelligentAssistant = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [conversationId] = useState(uuidv4());
  const [customerId, setCustomerId] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<LearningMetric | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    checkAuth();
    loadMetrics();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  const checkAuth = async () => {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
      navigate("/auth");
      return;
    }

    setUserId(session.user.id);

    const { data: profile } = await supabase
      .from("user_profiles")
      .select("customer_id")
      .eq("user_id", session.user.id)
      .maybeSingle();

    if (profile?.customer_id) {
      setCustomerId(profile.customer_id);
    }
  };

  const loadMetrics = async () => {
    const { data, error } = await supabase
      .from("ai_learning_metrics")
      .select("*")
      .order("metric_date", { ascending: false })
      .limit(1)
      .maybeSingle();

    if (!error && data) {
      setMetrics(data);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !customerId || !userId) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const { data, error } = await supabase.functions.invoke(
        "intelligent-assistant",
        {
          body: {
            query: input,
            conversationId: conversationId,
            customerId: customerId,
            userId: userId,
          },
        }
      );

      if (error) throw error;

      const assistantMessage: Message = {
        role: "assistant",
        content: data.response,
        sources: data.sources,
        insight: data.insight_generated ? data.insight : undefined,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (data.insight_generated) {
        toast.success("New insight generated!", {
          description: data.insight.title,
        });
        await loadMetrics();
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("Failed to get response");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    navigate("/auth");
  };

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold">Intelligent Assistant</h1>
            <Badge variant="outline" className="ml-2">
              <Sparkles className="h-3 w-3 mr-1" />
              Self-Learning AI
            </Badge>
          </div>
          <Button onClick={handleSignOut} variant="outline" size="sm">
            <LogOut className="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-4 pt-56 pb-8">
        <DashboardNavigation 
          title="Intelligent Assistant"
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

        {/* Learning Metrics */}
        {metrics && (
          <div className="grid gap-4 md:grid-cols-4 mb-6">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Total Interactions
                    </p>
                    <p className="text-2xl font-bold">{metrics.total_interactions}</p>
                  </div>
                  <Brain className="h-8 w-8 text-primary opacity-50" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Insights Generated
                    </p>
                    <p className="text-2xl font-bold text-yellow-600">
                      {metrics.insights_generated}
                    </p>
                  </div>
                  <Lightbulb className="h-8 w-8 text-yellow-600 opacity-50" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Articles Created
                    </p>
                    <p className="text-2xl font-bold text-green-600">
                      {metrics.articles_created}
                    </p>
                  </div>
                  <FileText className="h-8 w-8 text-green-600 opacity-50" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Avg Confidence
                    </p>
                    <p className="text-2xl font-bold">
                      {metrics.avg_confidence_score
                        ? `${(metrics.avg_confidence_score * 100).toFixed(0)}%`
                        : "N/A"}
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-primary opacity-50" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Chat Interface */}
        <Card className="h-[600px] flex flex-col">
          <CardHeader>
            <CardTitle>AI-Powered Knowledge Assistant</CardTitle>
            <CardDescription>
              Ask questions and get intelligent responses powered by your entire
              knowledge base. The system learns from every interaction.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col p-0">
            <ScrollArea className="flex-1 px-4" ref={scrollRef}>
              <div className="space-y-4 py-4">
                {messages.length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">
                    <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="font-medium mb-2">
                      Start a conversation with the Intelligent Assistant
                    </p>
                    <p className="text-sm">
                      The AI will learn from each interaction and generate insights
                      to improve your knowledge base
                    </p>
                  </div>
                )}

                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      <div className="flex items-start gap-2 mb-2">
                        {message.role === "assistant" && (
                          <Brain className="h-5 w-5 mt-0.5" />
                        )}
                        <div className="flex-1">
                          <p className="whitespace-pre-wrap">{message.content}</p>

                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-border/40">
                              <p className="text-xs font-medium mb-2">Sources:</p>
                              <div className="flex flex-wrap gap-1">
                                {message.sources.map((source) => (
                                  <Badge
                                    key={source.id}
                                    variant="outline"
                                    className="text-xs"
                                  >
                                    <FileText className="h-3 w-3 mr-1" />
                                    {source.title}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}

                          {message.insight && (
                            <div className="mt-3 pt-3 border-t border-yellow-500/40">
                              <div className="flex items-center gap-2 mb-1">
                                <Lightbulb className="h-4 w-4 text-yellow-500" />
                                <p className="text-xs font-medium">
                                  New Insight Generated
                                </p>
                              </div>
                              <p className="text-xs">{message.insight.title}</p>
                              <p className="text-xs text-muted-foreground mt-1">
                                Confidence: {(message.insight.confidence * 100).toFixed(0)}%
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                      <p className="text-xs text-right opacity-70">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-lg p-4">
                      <div className="flex items-center gap-2">
                        <Brain className="h-5 w-5 animate-pulse" />
                        <p className="text-sm">Thinking...</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            <div className="p-4 border-t">
              <div className="flex gap-2">
                <Input
                  placeholder="Ask anything about your organization..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSend}
                  disabled={isLoading || !input.trim()}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Powered by your knowledge base • Learns from every interaction
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default IntelligentAssistant;
