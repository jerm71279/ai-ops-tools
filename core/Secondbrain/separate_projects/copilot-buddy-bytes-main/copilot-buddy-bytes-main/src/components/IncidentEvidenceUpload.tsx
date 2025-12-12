import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Upload, FileText, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface IncidentEvidenceUploadProps {
  incidentId: string;
  incidentNumber: string;
  onUploadComplete?: () => void;
}

export default function IncidentEvidenceUpload({ 
  incidentId, 
  incidentNumber, 
  onUploadComplete 
}: IncidentEvidenceUploadProps) {
  const { toast } = useToast();
  const [isOpen, setIsOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");
  const [complianceTags, setComplianceTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState("");

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAddTag = () => {
    if (newTag && !complianceTags.includes(newTag)) {
      setComplianceTags([...complianceTags, newTag]);
      setNewTag("");
    }
  };

  const handleRemoveTag = (tag: string) => {
    setComplianceTags(complianceTags.filter(t => t !== tag));
  };

  const handleUpload = async () => {
    if (!file || !description) {
      toast({
        title: "Missing information",
        description: "Please fill in all required fields and select a file",
        variant: "destructive"
      });
      return;
    }

    setIsUploading(true);

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from('user_profiles')
        .select('customer_id')
        .eq('user_id', user.id)
        .single();

      if (!profile?.customer_id) throw new Error("Customer ID not found");

      // Insert evidence file record
      const { error } = await supabase
        .from('evidence_files')
        .insert({
          customer_id: profile.customer_id,
          incident_id: incidentId,
          file_name: file.name,
          file_type: file.type,
          file_size: file.size,
          storage_path: `/evidence/incidents/${incidentId}/${file.name}`,
          description,
          uploaded_by: user.id,
          compliance_tags: complianceTags.length > 0 ? complianceTags : null
        });

      if (error) throw error;

      toast({
        title: "Success",
        description: "Evidence file uploaded successfully"
      });

      // Reset form
      setFile(null);
      setDescription("");
      setComplianceTags([]);
      setIsOpen(false);
      
      if (onUploadComplete) {
        onUploadComplete();
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: "Error",
        description: "Failed to upload evidence file",
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="outline">
          <Upload className="h-4 w-4 mr-1" />
          Upload Evidence
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Evidence for {incidentNumber}
          </DialogTitle>
          <DialogDescription>
            Upload files, screenshots, or logs related to this incident
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="file">File *</Label>
            <div className="flex items-center gap-2">
              <Input
                id="file"
                type="file"
                onChange={handleFileSelect}
                accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.zip,.png,.jpg,.jpeg,.log"
              />
              {file && (
                <div className="flex items-center gap-2 text-sm">
                  <FileText className="h-4 w-4" />
                  <span className="truncate max-w-[200px]">{file.name}</span>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the evidence and how it relates to the incident"
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label>Tags (Optional)</Label>
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add tag (e.g., 'screenshot', 'logs', 'network')"
                onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
              />
              <Button type="button" variant="outline" onClick={handleAddTag}>
                Add
              </Button>
            </div>
            {complianceTags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {complianceTags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    {tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setIsOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={isUploading || !file || !description}
            >
              {isUploading ? "Uploading..." : "Upload Evidence"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
