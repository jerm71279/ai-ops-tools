import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, Upload, FileText, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";

export default function KnowledgeUpload() {
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!selectedFiles || selectedFiles.length === 0) {
      toast.error("Please select files to upload");
      return;
    }

    setIsUploading(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        toast.error("You must be logged in to upload files");
        return;
      }

      // Process each file
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        const formData = new FormData();
        formData.append("file", file);

        // Call the knowledge processor to extract content
        const { data, error } = await supabase.functions.invoke("knowledge-processor", {
          body: {
            action: "process_file",
            fileName: file.name,
            fileType: file.type,
            fileContent: await file.text()
          }
        });

        if (error) throw error;
      }

      toast.success(`Successfully uploaded ${selectedFiles.length} file(s)`);
      navigate("/knowledge");
    } catch (error) {
      console.error("Error uploading files:", error);
      toast.error("Failed to upload files");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8 max-w-2xl">
        <Button variant="ghost" onClick={() => navigate("/knowledge")} className="mb-6">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Knowledge Base
        </Button>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Upload className="h-6 w-6" />
              <CardTitle>Upload Knowledge Files</CardTitle>
            </div>
            <CardDescription>
              Upload documents to automatically extract and store knowledge
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="files">Select Files</Label>
              <Input
                id="files"
                type="file"
                multiple
                onChange={handleFileChange}
                accept=".txt,.md,.pdf,.doc,.docx"
                disabled={isUploading}
              />
              <p className="text-sm text-muted-foreground">
                Supported formats: TXT, MD, PDF, DOC, DOCX
              </p>
            </div>

            {selectedFiles && selectedFiles.length > 0 && (
              <div className="space-y-2">
                <Label>Selected Files ({selectedFiles.length})</Label>
                <div className="border rounded-md p-4 space-y-2">
                  {Array.from(selectedFiles).map((file, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <span>{file.name}</span>
                      <span className="text-muted-foreground">
                        ({(file.size / 1024).toFixed(2)} KB)
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-2">
              <Button
                onClick={handleUpload}
                disabled={isUploading || !selectedFiles || selectedFiles.length === 0}
                className="flex-1"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Files
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate("/knowledge")}
                disabled={isUploading}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
