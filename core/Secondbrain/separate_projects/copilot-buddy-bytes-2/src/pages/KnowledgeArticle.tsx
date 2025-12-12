import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, Edit, History, Download, Sparkles } from "lucide-react";
import { toast } from "sonner";
import Navigation from "@/components/Navigation";

export default function KnowledgeArticle() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isEnhancing, setIsEnhancing] = useState(false);

  useEffect(() => {
    loadArticle();
    loadVersions();
  }, [id]);

  const loadArticle = async () => {
    try {
      const { data, error } = await supabase
        .from("knowledge_articles")
        .select("*")
        .eq("id", id)
        .single();

      if (error) throw error;
      setArticle(data);

      // Log access
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        await supabase.from("knowledge_access_logs").insert({
          user_id: user.id,
          customer_id: data.customer_id,
          article_id: id,
          access_type: "view"
        });
      }
    } catch (error) {
      console.error("Error loading article:", error);
      toast.error("Failed to load article");
    } finally {
      setIsLoading(false);
    }
  };

  const loadVersions = async () => {
    try {
      const { data, error } = await supabase
        .from("knowledge_versions")
        .select("*")
        .eq("article_id", id)
        .order("version", { ascending: false });

      if (error) throw error;
      setVersions(data || []);
    } catch (error) {
      console.error("Error loading versions:", error);
    }
  };

  const enhanceWithAI = async () => {
    setIsEnhancing(true);
    try {
      const { data, error } = await supabase.functions.invoke("knowledge-processor", {
        body: {
          action: "enhance_article",
          articleContent: article.content
        }
      });

      if (error) throw error;
      toast.success("AI enhancement generated! Review the suggestions.");
      // You could show the enhanced version in a modal for review
    } catch (error) {
      console.error("Error enhancing article:", error);
      toast.error("Failed to enhance article");
    } finally {
      setIsEnhancing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 pt-56 pb-8">
          <p>Loading article...</p>
        </main>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 pt-56 pb-8">
          <p>Article not found</p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8 max-w-4xl">
        {/* Header */}
        <div className="mb-6">
          <Button variant="ghost" onClick={() => navigate("/knowledge")} className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Knowledge Base
          </Button>
          
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Badge>{article.article_type.toUpperCase()}</Badge>
                <Badge variant="outline">Version {article.version}</Badge>
                {article.source_type && (
                  <Badge variant="secondary">{article.source_type}</Badge>
                )}
              </div>
              <h1 className="text-4xl font-bold mb-2">{article.title}</h1>
              <p className="text-muted-foreground">
                Last updated {new Date(article.updated_at).toLocaleString()}
              </p>
            </div>
            
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={enhanceWithAI} disabled={isEnhancing}>
                <Sparkles className="mr-2 h-4 w-4" />
                {isEnhancing ? "Enhancing..." : "Enhance with AI"}
              </Button>
              <Button variant="outline" size="sm" onClick={() => navigate(`/knowledge/${id}/edit`)}>
                <Edit className="mr-2 h-4 w-4" />
                Edit
              </Button>
              <Button variant="outline" size="sm">
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            </div>
          </div>
        </div>

        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-6">
            {article.tags.map((tag: string, idx: number) => (
              <Badge key={idx} variant="outline">
                {tag}
              </Badge>
            ))}
          </div>
        )}

        <Separator className="mb-6" />

        {/* Content */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="prose prose-slate dark:prose-invert max-w-none">
              {article.content.split('\n').map((paragraph: string, idx: number) => (
                <p key={idx} className="mb-4">{paragraph}</p>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Version History */}
        {versions.length > 0 && (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <History className="h-5 w-5" />
                <CardTitle>Version History</CardTitle>
              </div>
              <CardDescription>
                Track changes and revisions to this article
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {versions.map((version) => (
                  <div key={version.id} className="border-l-2 border-primary pl-4 py-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold">Version {version.version}</span>
                      <span className="text-sm text-muted-foreground">
                        {new Date(version.created_at).toLocaleString()}
                      </span>
                    </div>
                    {version.change_summary && (
                      <p className="text-sm text-muted-foreground">{version.change_summary}</p>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}