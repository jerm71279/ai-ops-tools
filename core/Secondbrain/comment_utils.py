#!/usr/bin/env python3
"""
Comment Management Utilities
Handles adding, retrieving, and logging comments for projects and tickets
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


class CommentManager:
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
        if self.projects_list_id and self.tickets_list_id:
            return

        url = f'{BASE_URL}/sites/{SITE_ID}/lists'
        response = requests.get(url, headers=self.get_headers())
        lists = response.json().get('value', [])

        for lst in lists:
            if lst['displayName'] == 'Engineering Projects':
                self.projects_list_id = lst['id']
            elif lst['displayName'] == 'Engineering Tickets':
                self.tickets_list_id = lst['id']

    def get_comments(self, item_id, item_type='project'):
        """Get comments for a project or ticket"""
        self.get_list_ids()
        list_id = self.projects_list_id if item_type == 'project' else self.tickets_list_id

        url = f'{BASE_URL}/sites/{SITE_ID}/lists/{list_id}/items/{item_id}?expand=fields'
        response = requests.get(url, headers=self.get_headers())

        if response.status_code == 200:
            item = response.json()
            comments_json = item.get('fields', {}).get('Comments', '[]')
            try:
                return json.loads(comments_json)
            except:
                return []
        return []

    def add_comment(self, item_id, item_type, author, comment_text, item_name=''):
        """Add a comment to a project or ticket"""
        self.get_list_ids()
        list_id = self.projects_list_id if item_type == 'project' else self.tickets_list_id

        # Get existing comments
        existing_comments = self.get_comments(item_id, item_type)

        # Create new comment
        new_comment = {
            'id': f"{item_id}_{len(existing_comments) + 1}_{int(datetime.now().timestamp())}",
            'author': author,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'comment': comment_text
        }

        # Add to existing comments
        existing_comments.append(new_comment)

        # Update SharePoint
        url = f'{BASE_URL}/sites/{SITE_ID}/lists/{list_id}/items/{item_id}/fields'
        data = {
            'Comments': json.dumps(existing_comments)
        }

        response = requests.patch(url, headers=self.get_headers(), json=data)

        if response.status_code in [200, 204]:
            # Log to markdown file
            self.log_comment_to_md(item_id, item_type, item_name, new_comment)
            print(f"✅ Comment added successfully to {item_type} {item_id}")
            return True
        else:
            print(f"❌ Failed to add comment: {response.status_code}")
            print(response.text)
            return False

    def log_comment_to_md(self, item_id, item_type, item_name, comment):
        """Log comment to a markdown file"""
        # Create comments directory structure
        type_dir = COMMENTS_DIR / item_type
        type_dir.mkdir(parents=True, exist_ok=True)

        # Create/append to md file
        md_file = type_dir / f"{item_id}.md"

        # Format timestamp
        timestamp = datetime.fromisoformat(comment['timestamp'].replace('Z', '+00:00'))
        formatted_time = timestamp.strftime('%B %d, %Y at %I:%M %p')

        # Prepare comment content
        comment_md = f"""
## Comment by {comment['author']} on {formatted_time}

{comment['comment']}

---
"""

        if not md_file.exists():
            # Create new file with header
            header = f"""# Comments for {item_type.capitalize()}: {item_name}

**Item ID:** {item_id}
**Created:** {datetime.now().strftime('%B %d, %Y')}

---
"""
            md_file.write_text(header + comment_md)
        else:
            # Append to existing file
            with open(md_file, 'a') as f:
                f.write(comment_md)

        print(f"📝 Comment logged to {md_file}")

    def get_all_comments_for_item(self, item_id, item_type):
        """Get all comments formatted as markdown"""
        comments = self.get_comments(item_id, item_type)
        if not comments:
            return "No comments yet."

        md_output = ""
        for comment in comments:
            timestamp = datetime.fromisoformat(comment['timestamp'].replace('Z', '+00:00'))
            formatted_time = timestamp.strftime('%B %d, %Y at %I:%M %p')
            md_output += f"**{comment['author']}** - {formatted_time}\n"
            md_output += f"{comment['comment']}\n\n"

        return md_output


def add_comment_cli():
    """CLI interface for adding comments"""
    import sys

    if len(sys.argv) < 5:
        print("Usage: python comment_utils.py <item_id> <type:project|ticket> <author> <comment>")
        print("Example: python comment_utils.py 123 project john@oberaconnect.com 'This is a test comment'")
        sys.exit(1)

    item_id = sys.argv[1]
    item_type = sys.argv[2]
    author = sys.argv[3]
    comment = ' '.join(sys.argv[4:])

    if item_type not in ['project', 'ticket']:
        print("❌ Type must be 'project' or 'ticket'")
        sys.exit(1)

    manager = CommentManager()
    manager.add_comment(item_id, item_type, author, comment)


if __name__ == '__main__':
    add_comment_cli()
