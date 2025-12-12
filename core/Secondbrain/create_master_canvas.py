#!/usr/bin/env python3
"""
Create one master Obsidian canvas showing all 4 teams in hub-and-spoke layout
"""
import json
from pathlib import Path
from collections import defaultdict
import math

# Team keyword mappings
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

# Team positions on canvas (quadrants)
TEAM_POSITIONS = {
    'IT Services': {'x': -1200, 'y': -800},    # Top left
    'Engineering': {'x': 600, 'y': -800},      # Top right
    'Plant': {'x': -1200, 'y': 600},           # Bottom left
    'Sales': {'x': 600, 'y': 600}              # Bottom right
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

def find_related_notes(note_path: Path, all_notes: list, team: str, max_related: int = 8) -> list:
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

def create_master_canvas():
    """Create one master canvas with all 4 teams"""
    vault_path = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault/notes")
    output_path = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault")

    print("=" * 80)
    print("🎨 CREATING MASTER TEAM CANVAS (All Teams)")
    print("=" * 80)

    all_notes = list(vault_path.glob("*.md"))

    nodes = []
    edges = []
    node_id = 0

    # Add master title
    nodes.append({
        "id": "master-title",
        "type": "text",
        "text": f"# OberaConnect Knowledge Map\n\n**All Teams Hub-and-Spoke View**\n\n{len(all_notes)} total notes analyzed\n\n🔵 IT Services | 🔴 Engineering | 🟢 Plant | 🟡 Sales",
        "x": -300,
        "y": -1200,
        "width": 600,
        "height": 250,
        "color": "#6c757d"
    })

    # Process each team
    for team in ['IT Services', 'Engineering', 'Plant', 'Sales']:
        print(f"\n📊 Processing {team}...")

        # Find notes for this team
        team_notes = []
        for note_path in all_notes:
            teams = categorize_note_by_team(note_path)
            if team in teams:
                team_notes.append(note_path)

        print(f"   Found {len(team_notes)} notes")

        if not team_notes:
            continue

        # Get team position
        team_pos = TEAM_POSITIONS[team]
        hub_x = team_pos['x']
        hub_y = team_pos['y']

        # Find best hub note (largest, most connections)
        hub_candidates = sorted(team_notes, key=lambda x: x.stat().st_size, reverse=True)[:5]

        best_hub = None
        best_hub_related = []
        for candidate in hub_candidates:
            related = find_related_notes(candidate, all_notes, team, max_related=8)
            if len(related) > len(best_hub_related):
                best_hub = candidate
                best_hub_related = related

        if not best_hub or len(best_hub_related) < 3:
            print(f"   ⚠️  No strong hub found, using largest file")
            best_hub = hub_candidates[0]
            best_hub_related = find_related_notes(best_hub, all_notes, team, max_related=8)

        # Create team label
        team_label_id = f"team-label-{team.replace(' ', '-')}"
        nodes.append({
            "id": team_label_id,
            "type": "text",
            "text": f"## {team}\n\n**{len(team_notes)} notes**\n\nHub: {best_hub.stem.replace('_', ' ')[:40]}...",
            "x": hub_x - 150,
            "y": hub_y - 250,
            "width": 300,
            "height": 150,
            "color": TEAM_COLORS[team]
        })

        # Create hub node (larger, centered for this team)
        hub_node_id = f"hub-{node_id}"
        node_id += 1

        nodes.append({
            "id": hub_node_id,
            "type": "file",
            "file": f"notes/{best_hub.name}",
            "x": hub_x,
            "y": hub_y,
            "width": 350,
            "height": 250,
            "color": TEAM_COLORS[team]
        })

        print(f"   Hub: {best_hub.stem[:50]}")
        print(f"   Spokes: {len(best_hub_related)}")

        # Create spoke nodes in a circle
        num_spokes = len(best_hub_related)
        radius = 500

        for i, (related_note, score) in enumerate(best_hub_related):
            angle = (2 * math.pi * i) / num_spokes - (math.pi / 2)  # Start at top
            spoke_x = hub_x + int(radius * math.cos(angle))
            spoke_y = hub_y + int(radius * math.sin(angle))

            spoke_node_id = f"spoke-{node_id}"
            node_id += 1

            nodes.append({
                "id": spoke_node_id,
                "type": "file",
                "file": f"notes/{related_note.name}",
                "x": spoke_x,
                "y": spoke_y,
                "width": 220,
                "height": 140
            })

            # Create edge from hub to spoke (straight line)
            edges.append({
                "id": f"edge-{hub_node_id}-{spoke_node_id}",
                "fromNode": hub_node_id,
                "toNode": spoke_node_id,
                "color": TEAM_COLORS[team],
                "label": f"{score}"
            })

    # Create canvas JSON
    canvas_data = {
        "nodes": nodes,
        "edges": edges
    }

    # Write canvas file
    canvas_file = output_path / "All_Teams_Hub_And_Spoke.canvas"
    canvas_file.write_text(json.dumps(canvas_data, indent=2))

    print("\n" + "=" * 80)
    print("✅ MASTER CANVAS CREATED")
    print("=" * 80)
    print(f"Total nodes: {len(nodes)}")
    print(f"Total edges: {len(edges)}")
    print(f"\nSaved to: {canvas_file}")
    print("\nOpen 'All_Teams_Hub_And_Spoke.canvas' in Obsidian!")

if __name__ == "__main__":
    create_master_canvas()
