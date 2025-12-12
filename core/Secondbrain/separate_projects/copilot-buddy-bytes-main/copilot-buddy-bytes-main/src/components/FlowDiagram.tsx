import React from "react";

type Node = {
  id: string;
  label: string;
  x: number;
  y: number;
  w?: number;
  h?: number;
  hidden?: boolean; // when true, node is used only for routing (no rect/text)
};

type Edge = {
  from: string;
  to: string;
};

interface Props {
  title: string;
  accent: string; // must match an HSL token name from the design system (e.g., blue, purple, green)
  nodes: Node[];
  edges: Edge[];
  width?: number;
  height?: number;
}

const DEFAULT_NODE_W = 180;
const DEFAULT_NODE_H = 56;

export default function FlowDiagram({
  title,
  accent,
  nodes,
  edges,
  width = 800,
  height = 300,
}: Props) {
  const stroke = `hsl(var(--${accent}))`;
  const fill = `hsl(var(--${accent}) / 0.12)`;
  const text = `hsl(var(--foreground))`;

  const nodeMap = new Map(nodes.map((n) => [n.id, n]));

  return (
    <figure aria-label={title} className="w-full overflow-hidden rounded-lg bg-background/60">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-labelledby="diagramTitle"
        className="w-full h-auto"
      >
        <title id="diagramTitle">{title}</title>
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="10"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill={stroke} />
          </marker>
        </defs>

        {/* Edges */}
        {edges.map((e, idx) => {
          const from = nodeMap.get(e.from);
          const to = nodeMap.get(e.to);
          if (!from || !to) return null;
          const fw = from.w ?? DEFAULT_NODE_W;
          const fh = from.h ?? DEFAULT_NODE_H;
          const tw = to.w ?? DEFAULT_NODE_W;
          const th = to.h ?? DEFAULT_NODE_H;
          
          // Determine if connection is primarily vertical (similar x)
          const isVertical = Math.abs(from.x - to.x) < 50;
          
          let x1, y1, x2, y2;
          
          if (isVertical) {
            // Vertical flow: connect top/bottom centers based on direction
            if (to.y >= from.y) {
              // downwards: bottom of from to top of to
              x1 = from.x;
              y1 = from.y + fh / 2;
              x2 = to.x;
              y2 = to.y - th / 2;
            } else {
              // upwards: top of from to bottom of to
              x1 = from.x;
              y1 = from.y - fh / 2;
              x2 = to.x;
              y2 = to.y + th / 2;
            }
          } else {
            // Horizontal flow: right of from to left of to
            x1 = from.x + fw / 2;
            y1 = from.y;
            x2 = to.x - tw / 2;
            y2 = to.y;
          }

          // Don't show arrows on edges ending at small junction nodes (< 20px)
          const isJunction = tw < 20 && th < 20;

          return (
            <line
              key={`edge-${idx}`}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke={stroke}
              strokeWidth={2}
              markerEnd={isJunction ? undefined : "url(#arrow)"}
            />
          );
        })}

        {/* Nodes */}
        {nodes.map((n) => {
          if (n.hidden) return null; // Skip rendering hidden routing nodes
          const w = n.w ?? DEFAULT_NODE_W;
          const h = n.h ?? DEFAULT_NODE_H;
          const x = n.x - w / 2;
          const y = n.y - h / 2;
          const lines = n.label.split("\n");
          const lineHeight = 16;
          const totalTextHeight = lines.length * lineHeight;
          const startY = n.y - totalTextHeight / 2 + 12; // center text vertically
          return (
            <g key={n.id}>
              <rect
                x={x}
                y={y}
                width={w}
                height={h}
                rx={12}
                fill={fill}
                stroke={stroke}
                strokeWidth={2}
              />
              {lines.map((t, i) => (
                <text
                  key={i}
                  x={n.x}
                  y={startY + i * lineHeight}
                  fontSize={13}
                  fontFamily="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial, 'Apple Color Emoji', 'Segoe UI Emoji'"
                  textAnchor="middle"
                  fill={text}
                >
                  {t}
                </text>
              ))}
            </g>
          );
        })}
      </svg>
      <figcaption className="sr-only">{title}</figcaption>
    </figure>
  );
}
