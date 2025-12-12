#!/usr/bin/env python3
"""
Add internal wiki-links to notes so they show up in Obsidian Graph View
"""
from pathlib import Path
from collections import defaultdict

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

def add_links_to_note(note_path: Path, all_notes: list):
    """Add related links section to a note"""
    try:
        # Read current content
        content = note_path.read_text(encoding='utf-8')

        # Check if already has related links section
        if '## Related Notes' in content:
            return False  # Already processed

        # Get teams for this note
        teams = categorize_note_by_team(note_path)
        if not teams:
            return False

        # Find related notes for primary team
        primary_team = teams[0]
        related = find_related_notes(note_path, all_notes, primary_team, max_related=5)

        if len(related) < 2:
            return False  # Not enough connections

        # Build related notes section
        related_section = [
            "",
            "---",
            "",
            "## Related Notes",
            ""
        ]

        for related_note, score in related:
            # Create wiki-link using note name without .md extension
            link_name = related_note.stem
            related_section.append(f"- [[{link_name}]]")

        related_section.append("")

        # Append to note
        new_content = content + '\n'.join(related_section)
        note_path.write_text(new_content, encoding='utf-8')

        return True

    except Exception as e:
        print(f"Error processing {note_path.name}: {e}")
        return False

def main():
    vault_path = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault/notes")

    print("=" * 80)
    print("🔗 ADDING WIKI-LINKS FOR GRAPH VIEW")
    print("=" * 80)
    print()

    # Get all notes
    all_notes = list(vault_path.glob("*.md"))
    print(f"📊 Found {len(all_notes)} notes to process")
    print()

    # Categorize notes by team
    team_notes = defaultdict(list)
    for note_path in all_notes:
        teams = categorize_note_by_team(note_path)
        for team in teams:
            team_notes[team].append(note_path)

    print("Team distribution:")
    for team in ['IT Services', 'Engineering', 'Plant', 'Sales']:
        print(f"  • {team}: {len(team_notes[team])} notes")
    print()

    # Add links to notes
    updated_count = 0
    skipped_count = 0

    for i, note_path in enumerate(all_notes, 1):
        if i % 50 == 0:
            print(f"  Processing {i}/{len(all_notes)}...")

        if add_links_to_note(note_path, all_notes):
            updated_count += 1
        else:
            skipped_count += 1

    print()
    print("=" * 80)
    print("✅ WIKI-LINKS ADDED")
    print("=" * 80)
    print(f"Updated: {updated_count} notes")
    print(f"Skipped: {skipped_count} notes (no strong connections or already linked)")
    print()
    print("🎨 Now open Obsidian and:")
    print("   1. Click the Graph View icon (network/dots icon)")
    print("   2. You'll see all your notes connected by team relationships")
    print("   3. Use filters to show only specific teams")

if __name__ == "__main__":
    main()
