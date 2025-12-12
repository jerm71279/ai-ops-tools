import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, FileText, BookOpen, Lightbulb, Plus, Upload, Download, Cloud, Brain } from "lucide-react";
import { toast } from "sonner";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";

export default function KnowledgeBase() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [articles, setArticles] = useState<any[]>([]);
  const [insights, setInsights] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadKnowledgeBase();
  }, []);

  const loadKnowledgeBase = async () => {
    try {
      // Load articles
      const { data: articlesData, error: articlesError } = await supabase
        .from("knowledge_articles")
        .select("*")
        .eq("status", "published")
        .order("updated_at", { ascending: false });

      if (articlesError) throw articlesError;

      // Load insights
      const { data: insightsData, error: insightsError } = await supabase
        .from("knowledge_insights")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(10);

      if (insightsError) throw insightsError;

      // Load categories
      const { data: categoriesData, error: categoriesError } = await supabase
        .from("knowledge_categories")
        .select("*")
        .order("name");

      if (categoriesError) throw categoriesError;

      setArticles(articlesData || []);
      setInsights(insightsData || []);
      setCategories(categoriesData || []);
    } catch (error) {
      console.error("Error loading knowledge base:", error);
      toast.error("Failed to load knowledge base");
    } finally {
      setIsLoading(false);
    }
  };

  const filteredArticles = articles.filter(article =>
    article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    article.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    article.tags?.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const getArticleIcon = (type: string) => {
    switch (type) {
      case "sop": return <FileText className="h-4 w-4" />;
      case "guide": return <BookOpen className="h-4 w-4" />;
      case "faq": return <Lightbulb className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  const getArticleTypeColor = (type: string) => {
    switch (type) {
      case "sop": return "bg-primary/10 text-primary";
      case "guide": return "bg-secondary/10 text-secondary";
      case "faq": return "bg-accent/10 text-accent";
      default: return "bg-muted text-muted-foreground";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8">
        <DashboardNavigation 
          title="Knowledge Base"
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
        
        <div className="mb-8">
          <p className="text-muted-foreground">
            Search SOPs, guides, and AI-generated insights from your workflows
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative mb-8">
          <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
          <Input
            placeholder="Search knowledge base..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 h-12"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 mb-6">
          <Link to="/intelligent-assistant">
            <Button size="lg" className="gap-2">
              <Brain className="h-5 w-5" />
              Ask AI Assistant
            </Button>
          </Link>
          <Button onClick={() => navigate("/knowledge/new")}>
            <Plus className="mr-2 h-4 w-4" />
            New Article
          </Button>
          <Button variant="outline" onClick={() => navigate("/knowledge/upload")}>
            <Upload className="mr-2 h-4 w-4" />
            Upload Files
          </Button>
          <Link to="/sharepoint-sync">
            <Button variant="outline">
              <Cloud className="mr-2 h-4 w-4" />
              SharePoint Sync
            </Button>
          </Link>
          <Button variant="outline" onClick={() => navigate("/knowledge/generate")}>
            <Lightbulb className="mr-2 h-4 w-4" />
            Generate from Workflows
          </Button>
        </div>

        <Tabs defaultValue="articles" className="space-y-6">
          <TabsList>
            <TabsTrigger value="articles">All Articles ({filteredArticles.length})</TabsTrigger>
            <TabsTrigger value="sops">SOPs</TabsTrigger>
            <TabsTrigger value="insights">AI Insights ({insights.length})</TabsTrigger>
            <TabsTrigger value="categories">Categories</TabsTrigger>
          </TabsList>

          <TabsContent value="articles" className="space-y-4">
            {isLoading ? (
              <Card>
                <CardContent className="pt-6">Loading articles...</CardContent>
              </Card>
            ) : filteredArticles.length === 0 ? (
              <Card>
                <CardContent className="pt-6 text-center text-muted-foreground">
                  No articles found. Create your first knowledge article!
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredArticles.map((article) => (
                  <Card
                    key={article.id}
                    className="cursor-pointer hover:shadow-lg transition-shadow"
                    onClick={() => navigate(`/knowledge/${article.id}`)}
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          {getArticleIcon(article.article_type)}
                          <Badge className={getArticleTypeColor(article.article_type)}>
                            {article.article_type.toUpperCase()}
                          </Badge>
                        </div>
                        <span className="text-xs text-muted-foreground">v{article.version}</span>
                      </div>
                      <CardTitle className="text-lg">{article.title}</CardTitle>
                      <CardDescription className="line-clamp-2">
                        {article.content.substring(0, 150)}...
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-1">
                        {article.tags?.slice(0, 3).map((tag: string, idx: number) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        Updated {new Date(article.updated_at).toLocaleDateString()}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="sops">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredArticles
                .filter(a => a.article_type === 'sop')
                .map((article) => (
                  <Card
                    key={article.id}
                    className="cursor-pointer hover:shadow-lg transition-shadow"
                    onClick={() => navigate(`/knowledge/${article.id}`)}
                  >
                    <CardHeader>
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-4 w-4" />
                        <Badge>SOP v{article.version}</Badge>
                      </div>
                      <CardTitle className="text-lg">{article.title}</CardTitle>
                      <CardDescription className="line-clamp-2">
                        {article.content.substring(0, 150)}...
                      </CardDescription>
                    </CardHeader>
                  </Card>
                ))}
            </div>
          </TabsContent>

          <TabsContent value="insights" className="space-y-4">
            {insights.map((insight) => (
              <Card key={insight.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Lightbulb className="h-5 w-5 text-yellow-500" />
                      <CardTitle>{insight.title}</CardTitle>
                    </div>
                    <Badge variant="outline">{insight.insight_type}</Badge>
                  </div>
                  <CardDescription>{insight.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>Confidence: {(insight.confidence_score * 100).toFixed(0)}%</span>
                    <span>{new Date(insight.created_at).toLocaleDateString()}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="categories">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {categories.map((category) => (
                <Card key={category.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{category.name}</CardTitle>
                    <CardDescription>{category.description}</CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}