#!/usr/bin/env python3
"""
Generate link clusters organized by team
Teams: IT Services, Engineering, Plant (customer equipment install), Sales
"""
import sys
from pathlib import Path
from collections import defaultdict
import re

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

def categorize_note_by_team(file_path: Path) -> list:
    """Categorize a note into one or more teams based on content"""
    try:
        content = file_path.read_text(encoding='utf-8').lower()
        teams = []

        # Check each team's keywords
        for team, keywords in TEAM_KEYWORDS.items():
            keyword_count = sum(1 for keyword in keywords if keyword in content)
            if keyword_count >= 2:  # Must match at least 2 keywords
                teams.append((team, keyword_count))

        # Return teams sorted by relevance (keyword count)
        return [team for team, _ in sorted(teams, key=lambda x: x[1], reverse=True)]

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def extract_concepts_from_note(file_path: Path) -> list:
    """Extract key concepts from a note"""
    try:
        content = file_path.read_text(encoding='utf-8')
        concepts = []

        # Extract from frontmatter tags
        tag_match = re.search(r'tags:\s*(.+)', content)
        if tag_match:
            tags = [t.strip() for t in tag_match.group(1).split(',')]
            concepts.extend(tags)

        # Extract title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            concepts.append(title_match.group(1).strip())

        return concepts

    except Exception as e:
        return []

def find_related_notes(note_path: Path, all_notes: list, team: str) -> list:
    """Find notes related to this one within the same team"""
    try:
        content = note_path.read_text(encoding='utf-8').lower()
        concepts = extract_concepts_from_note(note_path)

        related = []
        for other_note in all_notes:
            if other_note == note_path:
                continue

            # Check if other note is in same team
            other_teams = categorize_note_by_team(other_note)
            if team not in other_teams:
                continue

            # Calculate relevance score
            other_content = other_note.read_text(encoding='utf-8').lower()
            score = 0

            # Shared concepts
            other_concepts = extract_concepts_from_note(other_note)
            shared_concepts = set(c.lower() for c in concepts) & set(c.lower() for c in other_concepts)
            score += len(shared_concepts) * 3

            # Team keyword co-occurrence
            team_keywords = TEAM_KEYWORDS[team]
            for keyword in team_keywords:
                if keyword in content and keyword in other_content:
                    score += 1

            if score >= 3:  # Minimum relevance threshold
                related.append((other_note, score, list(shared_concepts)))

        # Return top 10 most related
        return sorted(related, key=lambda x: x[1], reverse=True)[:10]

    except Exception as e:
        return []

def generate_team_clusters():
    """Generate link clusters organized by team"""
    vault_path = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault/notes")

    print("=" * 80)
    print("🔗 TEAM LINK CLUSTERS")
    print("=" * 80)
    print()

    # Get all notes
    all_notes = list(vault_path.glob("*.md"))
    print(f"📊 Analyzing {len(all_notes)} notes...")
    print()

    # Categorize notes by team
    team_notes = defaultdict(list)
    for note_path in all_notes:
        teams = categorize_note_by_team(note_path)
        for team in teams:
            team_notes[team].append(note_path)

    # Generate clusters for each team
    for team in ['IT Services', 'Engineering', 'Plant', 'Sales']:
        notes = team_notes[team]

        print("=" * 80)
        print(f"🏢 {team.upper()} TEAM - {len(notes)} notes")
        print("=" * 80)
        print()

        if not notes:
            print("No notes found for this team.")
            print()
            continue

        # Sample top notes and find their clusters
        sample_notes = sorted(notes, key=lambda x: x.stat().st_size, reverse=True)[:20]

        cluster_count = 0
        for note_path in sample_notes:
            related = find_related_notes(note_path, all_notes, team)

            if len(related) >= 2:  # Only show if at least 2 related notes
                cluster_count += 1
                print(f"📄 Hub Note: [[{note_path.stem.replace('_', ' ')}]]")
                print(f"   Related Notes ({len(related)}):")

                for related_note, score, concepts in related[:5]:  # Show top 5
                    print(f"   • [[{related_note.stem.replace('_', ' ')}]] (score: {score})")
                    if concepts:
                        print(f"     Shared: {', '.join(concepts[:3])}")

                print()

                if cluster_count >= 10:  # Limit to 10 clusters per team
                    break

        if cluster_count == 0:
            print("No significant link clusters found for this team.")
            print()

    print("=" * 80)
    print("✅ TEAM CLUSTER ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    generate_team_clusters()
