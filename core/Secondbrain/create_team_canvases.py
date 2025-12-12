#!/usr/bin/env python3
"""
Create Obsidian canvas files for each team showing link clusters
"""
import json
from pathlib import Path
from collections import defaultdict
import re
import math

# Team keyword mappings (same as before)
TEAM_KEYWORDS = {
    'IT Services': [
        'ninjaone', 'it service', 'itsm', 'helpdesk', 'ticket', 'support',
        'remote access', 'vpn', 'patch', 'backup', 'monitoring', 'atera',
        'microsoft 365', 'azure', 'active directory', 'domain controller',
        'cybersecurity', 'security policy', 'vulnerability', 'compliance'
    ],
    'Engineering': [
        'network', 'router', 'switch', 'firewall', 'mikrotik', 'unifi',
        'sonicwall', 'configuration', 'vlan', 'dns', 'dhcp', 'wifi',
        'ubiquiti', 'cabling', 'fiber', 'bandwidth', 'bgp', 'ospf',
        'engineering', 'technical design', 'architecture', 'infrastructure'
    ],
    'Plant': [
        'install', 'deployment', 'site survey', 'cabling', 'rack',
        'plant', 'construction', 'buildout', 'equipment install',
        'site preparation', 'floor plan', 'cable run', 'termination',
        'equipment placement', 'mounting', 'customer site', 'onsite'
    ],
    'Sales': [
        'proposal', 'quote', 'pricing', 'sales', 'customer', 'contract',
        'case study', 'marketing', 'branding', 'lead', 'prospect',
        'rfp', 'service offering', 'pricing', 'revenue', 'account',
        'municipality', 'senior living', 'pain points', 'value proposition'
    ]
}

TEAM_COLORS = {
    'IT Services': '#4a9eff',  # Blue
    'Engineering': '#ff6b6b',  # Red
    'Plant': '#51cf66',        # Green
    'Sales': '#ffd43b'         # Yellow
}

def categorize_note_by_team(file_path: Path) -> list:
    """Categorize a note into one or more teams based on content"""
    try:
        content = file_path.read_text(encoding='utf-8').lower()
        teams = []
        for team, keywords in TEAM_KEYWORDS.items():
            keyword_count = sum(1 for keyword in keywords if keyword in content)
            if keyword_count >= 2:
                teams.append((team, keyword_count))
        return [team for team, _ in sorted(teams, key=lambda x: x[1], reverse=True)]
    except:
        return []

def find_related_notes(note_path: Path, all_notes: list, team: str, max_related: int = 5) -> list:
    """Find notes related to this one within the same team"""
    try:
        content = note_path.read_text(encoding='utf-8').lower()
        related = []

        for other_note in all_notes:
            if other_note == note_path:
                continue

            other_teams = categorize_note_by_team(other_note)
            if team not in other_teams:
                continue

            other_content = other_note.read_text(encoding='utf-8').lower()
            score = 0

            # Team keyword co-occurrence
            team_keywords = TEAM_KEYWORDS[team]
            for keyword in team_keywords:
                if keyword in content and keyword in other_content:
                    score += 1

            if score >= 3:
                related.append((other_note, score))

        return sorted(related, key=lambda x: x[1], reverse=True)[:max_related]
    except:
        return []

def create_canvas_for_team(team: str, vault_path: Path, output_path: Path):
    """Create an Obsidian canvas file for a team"""
    print(f"\n📊 Creating canvas for {team}...")

    all_notes = list(vault_path.glob("*.md"))

    # Find notes for this team
    team_notes = []
    for note_path in all_notes:
        teams = categorize_note_by_team(note_path)
        if team in teams:
            team_notes.append(note_path)

    print(f"   Found {len(team_notes)} notes for {team}")

    if not team_notes:
        print(f"   Skipping - no notes found")
        return

    # Find top hub notes (largest files with most potential connections)
    hub_candidates = sorted(team_notes, key=lambda x: x.stat().st_size, reverse=True)[:10]

    nodes = []
    edges = []
    node_id = 0

    # Create canvas with multiple hub clusters
    hubs_to_show = 3  # Show top 3 hubs
    hub_spacing = 800

    for hub_index, hub_note in enumerate(hub_candidates[:hubs_to_show]):
        # Find related notes for this hub
        related = find_related_notes(hub_note, all_notes, team, max_related=5)

        if len(related) < 2:
            continue

        # Position hub node
        hub_x = -300 + (hub_index * hub_spacing)
        hub_y = 0

        # Create hub node
        hub_node_id = f"node{node_id}"
        node_id += 1

        nodes.append({
            "id": hub_node_id,
            "type": "file",
            "file": f"notes/{hub_note.name}",
            "x": hub_x,
            "y": hub_y,
            "width": 300,
            "height": 200,
            "color": TEAM_COLORS[team]
        })

        # Create related nodes in a circle around the hub
        num_related = len(related)
        radius = 400

        for i, (related_note, score) in enumerate(related):
            angle = (2 * math.pi * i) / num_related
            related_x = hub_x + int(radius * math.cos(angle))
            related_y = hub_y + int(radius * math.sin(angle))

            related_node_id = f"node{node_id}"
            node_id += 1

            nodes.append({
                "id": related_node_id,
                "type": "file",
                "file": f"notes/{related_note.name}",
                "x": related_x,
                "y": related_y,
                "width": 250,
                "height": 150
            })

            # Create edge from hub to related note (straight line)
            edges.append({
                "id": f"edge{hub_node_id}-{related_node_id}",
                "fromNode": hub_node_id,
                "toNode": related_node_id,
                "label": f"score: {score}"
            })

    # Add title card
    title_node = {
        "id": "title",
        "type": "text",
        "text": f"# {team} Team\n\n**{len(team_notes)} notes**\n\nShowing top {min(hubs_to_show, len([n for n in nodes if n.get('color')]))} hub notes with their related clusters",
        "x": -400,
        "y": -400,
        "width": 400,
        "height": 200,
        "color": TEAM_COLORS[team]
    }
    nodes.insert(0, title_node)

    # Create canvas JSON
    canvas_data = {
        "nodes": nodes,
        "edges": edges
    }

    # Write canvas file
    canvas_file = output_path / f"{team.replace(' ', '_')}_Links.canvas"
    canvas_file.write_text(json.dumps(canvas_data, indent=2))

    print(f"   ✅ Created canvas with {len(nodes)} nodes and {len(edges)} edges")
    print(f"      Saved to: {canvas_file}")

def main():
    vault_path = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault/notes")
    output_path = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault")

    print("=" * 80)
    print("🎨 CREATING TEAM CANVASES")
    print("=" * 80)

    for team in ['IT Services', 'Engineering', 'Plant', 'Sales']:
        create_canvas_for_team(team, vault_path, output_path)

    print("\n" + "=" * 80)
    print("✅ ALL TEAM CANVASES CREATED")
    print("=" * 80)
    print("\nOpen Obsidian and look for:")
    print("  • IT_Services_Links.canvas")
    print("  • Engineering_Links.canvas")
    print("  • Plant_Links.canvas")
    print("  • Sales_Links.canvas")

if __name__ == "__main__":
    main()
