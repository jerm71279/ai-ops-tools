import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Upload, FileText, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface EvidenceUploadProps {
  frameworkId?: string;
  controlId?: string;
  onUploadComplete?: () => void;
}

export default function EvidenceUpload({ frameworkId, controlId, onUploadComplete }: EvidenceUploadProps) {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isUploading, setIsUploading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");
  const [selectedFramework, setSelectedFramework] = useState(frameworkId || "");
  const [selectedControl, setSelectedControl] = useState(controlId || "");
  const [frameworks, setFrameworks] = useState<any[]>([]);
  const [controls, setControls] = useState<any[]>([]);
  const [complianceTags, setComplianceTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState("");

  useEffect(() => {
    loadFrameworks();
  }, []);

  useEffect(() => {
    if (selectedFramework) {
      loadControls(selectedFramework);
    }
  }, [selectedFramework]);

  const loadFrameworks = async () => {
    const { data } = await supabase
      .from('compliance_frameworks')
      .select('id, framework_name, framework_code')
      .eq('is_active', true)
      .order('framework_name');
    
    if (data) setFrameworks(data);
  };

  const loadControls = async (fwId: string) => {
    const { data } = await supabase
      .from('compliance_controls')
      .select('id, control_id, control_name')
      .eq('framework_id', fwId)
      .order('control_id');
    
    if (data) setControls(data);
  };

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
    if (!file || !selectedFramework || !description) {
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
      const { data: evidence, error } = await supabase
        .from('evidence_files')
        .insert({
          customer_id: profile.customer_id,
          framework_id: selectedFramework,
          control_id: selectedControl || null,
          file_name: file.name,
          file_type: file.type,
          file_size: file.size,
          storage_path: `/evidence/${selectedFramework}/${file.name}`,
          description,
          uploaded_by: user.id,
          compliance_tags: complianceTags.length > 0 ? complianceTags : null
        })
        .select()
        .single();

      if (error) throw error;

      toast({
        title: "Success",
        description: "Evidence file uploaded successfully"
      });

      // Reset form
      setFile(null);
      setDescription("");
      setComplianceTags([]);
      
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
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Upload Evidence
        </CardTitle>
        <CardDescription>
          Upload compliance evidence files for frameworks and controls
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="framework">Framework *</Label>
          <Select 
            value={selectedFramework} 
            onValueChange={(value) => {
              setSelectedFramework(value);
              setSelectedControl("");
              loadControls(value);
            }}
            disabled={!!frameworkId}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select framework" />
            </SelectTrigger>
            <SelectContent>
              {frameworks.map((fw) => (
                <SelectItem key={fw.id} value={fw.id}>
                  {fw.framework_code} - {fw.framework_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="control">Control (Optional)</Label>
          <Select 
            value={selectedControl} 
            onValueChange={setSelectedControl}
            disabled={!selectedFramework || !!controlId}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select control (optional)" />
            </SelectTrigger>
            <SelectContent>
              {controls.map((ctrl) => (
                <SelectItem key={ctrl.id} value={ctrl.control_id}>
                  {ctrl.control_id} - {ctrl.control_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="file">File *</Label>
          <div className="flex items-center gap-2">
            <Input
              id="file"
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.zip"
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
            placeholder="Describe the evidence and its relevance to the control"
            rows={3}
          />
        </div>

        <div className="space-y-2">
          <Label>Compliance Tags (Optional)</Label>
          <div className="flex gap-2">
            <Input
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="Add tag (e.g., 'audit', 'quarterly')"
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
            onClick={() => onUploadComplete?.()}
          >
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            disabled={isUploading || !file || !selectedFramework || !description}
          >
            {isUploading ? "Uploading..." : "Upload Evidence"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
