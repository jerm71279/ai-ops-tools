import { useState, useEffect, useRef } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { GitBranch, Maximize2, RefreshCw, Network } from "lucide-react";
import { toast } from "sonner";

interface RelationshipNode {
  id: string;
  name: string;
  type: string;
  criticality: string;
  x?: number;
  y?: number;
}

interface RelationshipEdge {
  source: string;
  target: string;
  type: string;
  is_critical: boolean;
}

interface CIRelationshipMapProps {
  ciId: string;
  ciName: string;
}

const CIRelationshipMap = ({ ciId, ciName }: CIRelationshipMapProps) => {
  const [nodes, setNodes] = useState<RelationshipNode[]>([]);
  const [edges, setEdges] = useState<RelationshipEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    loadRelationshipData();
  }, [ciId]);

  useEffect(() => {
    if (nodes.length > 0) {
      drawGraph();
    }
  }, [nodes, edges]);

  const loadRelationshipData = async () => {
    try {
      setLoading(true);

      // Get outbound relationships
      const { data: outbound, error: outboundError } = await supabase
        .from("ci_relationships")
        .select(`
          id,
          relationship_type,
          target_ci_id,
          is_critical,
          target:configuration_items!ci_relationships_target_ci_id_fkey(id, ci_name, ci_type, criticality)
        `)
        .eq("source_ci_id", ciId);

      if (outboundError) throw outboundError;

      // Get inbound relationships
      const { data: inbound, error: inboundError } = await supabase
        .from("ci_relationships")
        .select(`
          id,
          relationship_type,
          source_ci_id,
          is_critical,
          source:configuration_items!ci_relationships_source_ci_id_fkey(id, ci_name, ci_type, criticality)
        `)
        .eq("target_ci_id", ciId);

      if (inboundError) throw inboundError;

      // Get current CI details
      const { data: currentCI, error: ciError } = await supabase
        .from("configuration_items")
        .select("ci_name, ci_type, criticality")
        .eq("id", ciId)
        .single();

      if (ciError) throw ciError;

      // Build nodes
      const nodeMap = new Map<string, RelationshipNode>();
      
      // Add center node (current CI)
      nodeMap.set(ciId, {
        id: ciId,
        name: currentCI.ci_name,
        type: currentCI.ci_type,
        criticality: currentCI.criticality,
      });

      // Add outbound nodes
      outbound?.forEach((rel: any) => {
        if (rel.target) {
          nodeMap.set(rel.target.id, {
            id: rel.target.id,
            name: rel.target.ci_name,
            type: rel.target.ci_type,
            criticality: rel.target.criticality,
          });
        }
      });

      // Add inbound nodes
      inbound?.forEach((rel: any) => {
        if (rel.source) {
          nodeMap.set(rel.source.id, {
            id: rel.source.id,
            name: rel.source.ci_name,
            type: rel.source.ci_type,
            criticality: rel.source.criticality,
          });
        }
      });

      // Build edges
      const edgeList: RelationshipEdge[] = [];
      
      outbound?.forEach((rel: any) => {
        if (rel.target) {
          edgeList.push({
            source: ciId,
            target: rel.target.id,
            type: rel.relationship_type,
            is_critical: rel.is_critical,
          });
        }
      });

      inbound?.forEach((rel: any) => {
        if (rel.source) {
          edgeList.push({
            source: rel.source.id,
            target: ciId,
            type: rel.relationship_type,
            is_critical: rel.is_critical,
          });
        }
      });

      // Position nodes in a circle around the center
      const nodeArray = Array.from(nodeMap.values());
      const centerX = 400;
      const centerY = 300;
      const radius = 200;

      nodeArray.forEach((node, index) => {
        if (node.id === ciId) {
          node.x = centerX;
          node.y = centerY;
        } else {
          const angle = (index / (nodeArray.length - 1)) * 2 * Math.PI;
          node.x = centerX + radius * Math.cos(angle);
          node.y = centerY + radius * Math.sin(angle);
        }
      });

      setNodes(nodeArray);
      setEdges(edgeList);
    } catch (error) {
      console.error("Error loading relationship data:", error);
      toast.error("Failed to load relationship map");
    } finally {
      setLoading(false);
    }
  };

  const drawGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw edges
    edges.forEach((edge) => {
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);

      if (sourceNode && targetNode && sourceNode.x && sourceNode.y && targetNode.x && targetNode.y) {
        ctx.beginPath();
        ctx.moveTo(sourceNode.x, sourceNode.y);
        ctx.lineTo(targetNode.x, targetNode.y);
        ctx.strokeStyle = edge.is_critical ? "#ef4444" : "#94a3b8";
        ctx.lineWidth = edge.is_critical ? 3 : 1;
        ctx.stroke();

        // Draw arrow
        const angle = Math.atan2(targetNode.y - sourceNode.y, targetNode.x - sourceNode.x);
        const arrowLength = 15;
        ctx.beginPath();
        ctx.moveTo(targetNode.x - 30 * Math.cos(angle), targetNode.y - 30 * Math.sin(angle));
        ctx.lineTo(
          targetNode.x - 30 * Math.cos(angle) - arrowLength * Math.cos(angle - Math.PI / 6),
          targetNode.y - 30 * Math.sin(angle) - arrowLength * Math.sin(angle - Math.PI / 6)
        );
        ctx.lineTo(
          targetNode.x - 30 * Math.cos(angle) - arrowLength * Math.cos(angle + Math.PI / 6),
          targetNode.y - 30 * Math.sin(angle) - arrowLength * Math.sin(angle + Math.PI / 6)
        );
        ctx.closePath();
        ctx.fillStyle = edge.is_critical ? "#ef4444" : "#94a3b8";
        ctx.fill();
      }
    });

    // Draw nodes
    nodes.forEach((node) => {
      if (node.x && node.y) {
        // Node circle
        ctx.beginPath();
        ctx.arc(node.x, node.y, 30, 0, 2 * Math.PI);
        ctx.fillStyle = node.id === ciId ? "#3b82f6" : 
                        node.criticality === "critical" ? "#ef4444" :
                        node.criticality === "high" ? "#f59e0b" : "#94a3b8";
        ctx.fill();
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Node label
        ctx.fillStyle = "#1e293b";
        ctx.font = "12px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(
          node.name.length > 15 ? node.name.substring(0, 15) + "..." : node.name,
          node.x,
          node.y + 50
        );
      }
    });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Relationship Map</CardTitle>
            <CardDescription>
              Visual representation of CI dependencies and relationships
            </CardDescription>
          </div>
          <Button size="sm" variant="outline" onClick={loadRelationshipData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {nodes.length === 0 ? (
          <div className="text-center py-12">
            <Network className="h-12 w-12 mx-auto text-muted-foreground mb-4 opacity-50" />
            <p className="text-muted-foreground">No relationships to display</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="secondary">
                <GitBranch className="h-3 w-3 mr-1" />
                {nodes.length} CIs
              </Badge>
              <Badge variant="outline">
                {edges.length} Relationships
              </Badge>
              <Badge variant="destructive">
                {edges.filter(e => e.is_critical).length} Critical
              </Badge>
            </div>
            
            <div className="border rounded-lg bg-accent/5 overflow-hidden">
              <canvas
                ref={canvasRef}
                width={800}
                height={600}
                className="w-full h-auto"
              />
            </div>

            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-full bg-blue-600"></span>
                  Current CI
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-full bg-red-600"></span>
                  Critical
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-full bg-gray-400"></span>
                  Normal
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CIRelationshipMap;
