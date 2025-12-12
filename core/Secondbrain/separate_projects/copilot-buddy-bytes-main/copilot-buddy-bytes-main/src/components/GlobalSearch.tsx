import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Search, FileText, Workflow, Shield, Database, GitBranch, Sparkles } from "lucide-react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

interface SearchResult {
  type: string;
  title: string;
  url: string;
  data: any;
}

interface GlobalSearchProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const typeIcons = {
  workflow: Workflow,
  compliance: Shield,
  cmdb: Database,
  knowledge: FileText,
  change: GitBranch,
};

const typeLabels = {
  workflow: "Workflow",
  compliance: "Compliance",
  cmdb: "CMDB",
  knowledge: "Knowledge",
  change: "Change Request",
};

export function GlobalSearch({ open, onOpenChange }: GlobalSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [aiSummary, setAiSummary] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();

  const performSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setAiSummary("");
      return;
    }

    setLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke("global-search", {
        body: { query: searchQuery },
      });

      if (error) throw error;

      setResults(data.results || []);
      setAiSummary(data.aiSummary || "");
      setSelectedIndex(0);
    } catch (error) {
      console.error("Search error:", error);
      toast.error("Search failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const debounce = setTimeout(() => {
      performSearch(query);
    }, 300);

    return () => clearTimeout(debounce);
  }, [query, performSearch]);

  const handleSelect = (result: SearchResult) => {
    navigate(result.url);
    onOpenChange(false);
    setQuery("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % results.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + results.length) % results.length);
    } else if (e.key === "Enter" && results[selectedIndex]) {
      e.preventDefault();
      handleSelect(results[selectedIndex]);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl p-0 gap-0">
        <DialogTitle className="sr-only">Global Search</DialogTitle>
        <div className="flex items-center border-b px-4 py-3">
          <Search className="mr-2 h-5 w-5 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search workflows, compliance, CMDB, knowledge..."
            className="border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
            autoFocus
          />
        </div>

        {aiSummary && (
          <div className="px-4 py-3 bg-muted/50 border-b flex items-start gap-2">
            <Sparkles className="h-4 w-4 mt-0.5 text-primary" />
            <p className="text-sm text-muted-foreground">{aiSummary}</p>
          </div>
        )}

        <ScrollArea className="max-h-[400px]">
          {loading ? (
            <div className="p-8 text-center text-muted-foreground">Searching...</div>
          ) : results.length === 0 && query ? (
            <div className="p-8 text-center text-muted-foreground">No results found</div>
          ) : (
            <div className="p-2">
              {results.map((result, index) => {
                const Icon = typeIcons[result.type as keyof typeof typeIcons] || FileText;
                const label = typeLabels[result.type as keyof typeof typeLabels] || result.type;
                
                return (
                  <button
                    key={`${result.type}-${result.url}`}
                    onClick={() => handleSelect(result)}
                    className={`w-full flex items-center gap-3 px-3 py-3 rounded-md text-left hover:bg-accent transition-colors ${
                      index === selectedIndex ? "bg-accent" : ""
                    }`}
                  >
                    <div className="flex-shrink-0">
                      <Icon className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{result.title}</div>
                      {result.data.description && (
                        <div className="text-sm text-muted-foreground truncate">
                          {result.data.description}
                        </div>
                      )}
                    </div>
                    <Badge variant="secondary" className="flex-shrink-0">
                      {label}
                    </Badge>
                  </button>
                );
              })}
            </div>
          )}
        </ScrollArea>

        <div className="px-4 py-2 border-t text-xs text-muted-foreground flex items-center justify-between">
          <span>Use ↑↓ to navigate, Enter to select, Esc to close</span>
          <span className="flex items-center gap-1">
            <Sparkles className="h-3 w-3" />
            AI-powered
          </span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
