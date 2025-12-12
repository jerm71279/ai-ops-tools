#!/usr/bin/env python3
"""
Sync Comments to Markdown Files
Synchronizes all comments from SharePoint to individual .md files
Run this script periodically or after adding comments to keep files updated
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/home/mavrick/Projects/Secondbrain/.env')

# Configuration
SITE_ID = 'oberaconnect.sharepoint.com,3894a9a1-76ac-4955-88b2-a1d335f35f78,522e18b4-c876-4c61-b74b-53adb0e6ddef'
BASE_URL = 'https://graph.microsoft.com/v1.0'
COMMENTS_DIR = Path('/home/mavrick/Projects/Secondbrain/comments')


class CommentsSync:
    def __init__(self):
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.token = None
        self.projects_list_id = None
        self.tickets_list_id = None

    def get_token(self):
        """Get OAuth token"""
        if self.token:
            return self.token

        token_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        response = requests.post(token_url, data=data)
        self.token = response.json().get('access_token')
        return self.token

    def get_headers(self):
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.get_token()}',
            'Content-Type': 'application/json'
        }

    def get_list_ids(self):
        """Get SharePoint list IDs"""
        url = f'{BASE_URL}/sites/{SITE_ID}/lists'
        response = requests.get(url, headers=self.get_headers())
        lists = response.json().get('value', [])

        for lst in lists:
            if lst['displayName'] == 'Engineering Projects':
                self.projects_list_id = lst['id']
            elif lst['displayName'] == 'Engineering Tickets':
                self.tickets_list_id = lst['id']

    def sync_comments(self, item_type='project'):
        """Sync comments for all items of a given type"""
        self.get_list_ids()
        list_id = self.projects_list_id if item_type == 'project' else self.tickets_list_id

        if not list_id:
            print(f"❌ Could not find list for {item_type}")
            return

        # Get all items
        url = f'{BASE_URL}/sites/{SITE_ID}/lists/{list_id}/items?expand=fields'
        response = requests.get(url, headers=self.get_headers())
        items = response.json().get('value', [])

        synced_count = 0
        for item in items:
            item_id = item['id']
            fields = item['fields']

            # Get item name
            item_name = fields.get('ProjectName') or fields.get('TicketTitle') or f"Item {item_id}"

            # Get comments
            comments_json = fields.get('Comments', '[]')
            try:
                comments = json.loads(comments_json)
            except:
                comments = []

            if comments:
                self.save_to_md(item_id, item_type, item_name, comments)
                synced_count += 1

        print(f"✅ Synced {synced_count} {item_type}(s) with comments to .md files")

    def save_to_md(self, item_id, item_type, item_name, comments):
        """Save comments to markdown file"""
        # Create directory structure
        type_dir = COMMENTS_DIR / item_type
        type_dir.mkdir(parents=True, exist_ok=True)

        # Create md file
        md_file = type_dir / f"{item_id}.md"

        # Build markdown content
        md_content = f"""# Comments for {item_type.capitalize()}: {item_name}

**Item ID:** {item_id}
**Last Updated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Total Comments:** {len(comments)}

---

"""

        # Add each comment
        for comment in comments:
            try:
                timestamp = datetime.fromisoformat(comment['timestamp'].replace('Z', '+00:00'))
                formatted_time = timestamp.strftime('%B %d, %Y at %I:%M %p')
            except:
                formatted_time = comment.get('timestamp', 'Unknown time')

            md_content += f"""## Comment by {comment.get('author', 'Unknown')}
**Date:** {formatted_time}

{comment.get('comment', '')}

---

"""

        # Write to file
        md_file.write_text(md_content)
        print(f"  📝 Saved: {md_file}")


def main():
    print("=" * 60)
    print("Syncing Comments to Markdown Files")
    print("=" * 60)

    syncer = CommentsSync()

    print("\n🔄 Syncing project comments...")
    syncer.sync_comments('project')

    print("\n🔄 Syncing ticket comments...")
    syncer.sync_comments('ticket')

    print("\n✅ All comments synced successfully!")
    print(f"\n📁 Comments saved to: {COMMENTS_DIR}")


if __name__ == '__main__':
    main()
