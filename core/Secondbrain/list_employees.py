#!/usr/bin/env python3
"""
Extract employee information from Second Brain notes
"""
from pathlib import Path
import re

OBSIDIAN_VAULT_PATH = Path("/mnt/c/Users/JeremySmith/OneDrive - Obera Connect/MyVault")

def extract_employees():
    """Find and list all employees mentioned in notes"""
    notes_dir = OBSIDIAN_VAULT_PATH / "notes"

    # Employee names to search for
    employee_names = [
        "Devon Harris", "Chris Ingram", "Christopher Ingram",
        "Amanda Johnson", "Steven Harris", "Madison Cruz",
        "Forrest Beeco", "James Johnson", "Misty",
        "Jeremy Smith", "Blake", "Tiffany Luckenbaugh",
        "Sara Francis", "Devon H", "Ally Wilson"
    ]

    employees_found = {}

    print("=" * 70)
    print("👥 OberaConnect Employee List")
    print("=" * 70)
    print()

    # Search through all notes
    for note_path in notes_dir.rglob("*.md"):
        content = note_path.read_text(encoding='utf-8')
        content_lower = content.lower()

        for name in employee_names:
            if name.lower() in content_lower:
                if name not in employees_found:
                    employees_found[name] = {
                        'notes': [],
                        'roles': set(),
                        'mentions': 0
                    }

                employees_found[name]['notes'].append(note_path.name)
                employees_found[name]['mentions'] += content_lower.count(name.lower())

                # Try to extract role/title info
                for line in content.split('\n'):
                    if name.lower() in line.lower():
                        # Look for common title patterns
                        if any(word in line.lower() for word in ['ceo', 'president', 'manager', 'director', 'engineer', 'sales', 'tech']):
                            employees_found[name]['roles'].add(line.strip()[:100])

    # Display results
    print(f"📊 Found {len(employees_found)} employees mentioned in your Second Brain\n")

    # Sort by mention count
    sorted_employees = sorted(employees_found.items(), key=lambda x: x[1]['mentions'], reverse=True)

    for name, info in sorted_employees:
        print(f"👤 {name}")
        print(f"   Mentioned in: {len(info['notes'])} notes ({info['mentions']} times)")

        if info['roles']:
            print(f"   Context found:")
            for role in list(info['roles'])[:3]:  # Show top 3 contexts
                print(f"     • {role}")

        print(f"   Notes: {', '.join(info['notes'][:3])}")
        if len(info['notes']) > 3:
            print(f"     ... and {len(info['notes']) - 3} more")
        print()

    # Look for org chart or employee list documents
    print("\n" + "=" * 70)
    print("📋 Documents that may contain employee lists:")
    print("=" * 70)
    print()

    keywords = ['employee', 'staff', 'team', 'roster', 'org chart', 'onboarding', 'new hire']
    relevant_docs = set()

    for note_path in notes_dir.rglob("*.md"):
        for keyword in keywords:
            if keyword in note_path.stem.lower():
                relevant_docs.add(note_path.name)
                break

    for doc in sorted(relevant_docs):
        print(f"  • {doc}")

if __name__ == "__main__":
    extract_employees()
