#!/usr/bin/env python3
"""
Slack Message & File Importer
Downloads messages and files from Slack channels and DMs
"""
import os
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import requests

class SlackImporter:
    """Import messages and files from Slack"""

    def __init__(self, token: str = None):
        """
        Initialize Slack importer

        Get your token from: https://api.slack.com/apps
        Required scopes:
        - channels:history
        - channels:read
        - files:read
        - users:read
        """
        self.token = token or os.getenv('SLACK_BOT_TOKEN')

        if not self.token:
            print("⚠️  Slack token not configured.")
            print("   Set SLACK_BOT_TOKEN environment variable")
            print("   or run with --setup for instructions")

        self.base_url = "https://slack.com/api"

    def list_channels(self) -> List[Dict]:
        """List all channels"""
        if not self.token:
            return []

        url = f"{self.base_url}/conversations.list"
        headers = {'Authorization': f'Bearer {self.token}'}
        params = {'types': 'public_channel,private_channel'}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get('ok'):
                print(f"❌ Slack API error: {data.get('error')}")
                return []

            channels = data.get('channels', [])

            print(f"📺 Found {len(channels)} channels:")
            for channel in channels:
                print(f"   - #{channel['name']} (ID: {channel['id']})")

            return channels

        except Exception as e:
            print(f"❌ Failed to list channels: {e}")
            return []

    def export_channel_messages(self, channel_id: str, channel_name: str,
                                output_dir: Path, days: int = 30):
        """Export messages from a channel"""
        if not self.token:
            return

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        url = f"{self.base_url}/conversations.history"
        headers = {'Authorization': f'Bearer {self.token}'}

        # Calculate oldest timestamp (30 days ago by default)
        from datetime import timedelta
        oldest_time = datetime.now() - timedelta(days=days)
        oldest_ts = str(oldest_time.timestamp())

        params = {
            'channel': channel_id,
            'oldest': oldest_ts,
            'limit': 1000
        }

        all_messages = []
        cursor = None

        print(f"📥 Exporting messages from #{channel_name}...")

        try:
            while True:
                if cursor:
                    params['cursor'] = cursor

                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                if not data.get('ok'):
                    print(f"❌ Slack API error: {data.get('error')}")
                    break

                messages = data.get('messages', [])
                all_messages.extend(messages)

                # Check for pagination
                cursor = data.get('response_metadata', {}).get('next_cursor')
                if not cursor:
                    break

            # Save as markdown
            markdown_file = output_dir / f"slack_{channel_name}_{datetime.now().strftime('%Y%m%d')}.md"

            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(f"# Slack Channel: #{channel_name}\n\n")
                f.write(f"**Exported:** {datetime.now().isoformat()}\n")
                f.write(f"**Messages:** {len(all_messages)}\n\n")
                f.write("---\n\n")

                for msg in reversed(all_messages):  # Chronological order
                    timestamp = datetime.fromtimestamp(float(msg.get('ts', 0)))
                    user = msg.get('user', 'Unknown')
                    text = msg.get('text', '')

                    f.write(f"## {timestamp.strftime('%Y-%m-%d %H:%M')}\n")
                    f.write(f"**User:** {user}\n\n")
                    f.write(f"{text}\n\n")

                    # Include attachments/files info
                    if msg.get('files'):
                        f.write("**Files:**\n")
                        for file in msg['files']:
                            f.write(f"- {file.get('name')} ({file.get('mimetype')})\n")
                        f.write("\n")

                    f.write("---\n\n")

            print(f"✅ Exported {len(all_messages)} messages to {markdown_file}")

            # Also save as JSON for reference
            json_file = output_dir / f"slack_{channel_name}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(all_messages, f, indent=2)

            print(f"✅ Raw data saved to {json_file}")

        except Exception as e:
            print(f"❌ Export failed: {e}")

    def download_files_from_channel(self, channel_id: str, output_dir: Path, days: int = 30):
        """Download all files shared in a channel"""
        if not self.token:
            return

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # First get messages with files
        url = f"{self.base_url}/conversations.history"
        headers = {'Authorization': f'Bearer {self.token}'}

        from datetime import timedelta
        oldest_time = datetime.now() - timedelta(days=days)
        oldest_ts = str(oldest_time.timestamp())

        params = {
            'channel': channel_id,
            'oldest': oldest_ts,
            'limit': 1000
        }

        downloaded = 0

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get('ok'):
                print(f"❌ Slack API error: {data.get('error')}")
                return

            messages = data.get('messages', [])

            for msg in messages:
                if msg.get('files'):
                    for file in msg['files']:
                        file_url = file.get('url_private_download')
                        file_name = file.get('name', 'unknown')

                        if file_url:
                            print(f"⬇️  Downloading: {file_name}")

                            file_response = requests.get(
                                file_url,
                                headers={'Authorization': f'Bearer {self.token}'}
                            )
                            file_response.raise_for_status()

                            file_path = output_dir / file_name
                            file_path.write_bytes(file_response.content)
                            downloaded += 1

            print(f"\n✅ Downloaded {downloaded} files")

        except Exception as e:
            print(f"❌ Download failed: {e}")


def setup_slack_app():
    """Print instructions for setting up Slack app"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Slack Importer - App Setup Instructions                      ║
╚════════════════════════════════════════════════════════════════╝

To use the Slack importer, you need to create a Slack app:

1. Go to: https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
   - Name: "SecondBrain Importer"
   - Pick your workspace
4. Click "Create App"

5. Add OAuth Scopes:
   - Go to "OAuth & Permissions"
   - Scroll to "Bot Token Scopes"
   - Add these scopes:
     * channels:history (Read messages in public channels)
     * channels:read (View basic info about channels)
     * files:read (View files shared in channels)
     * groups:history (Read messages in private channels)
     * users:read (View people in workspace)

6. Install to Workspace:
   - Scroll up to "OAuth Tokens for Your Workspace"
   - Click "Install to Workspace"
   - Authorize the app
   - Copy the "Bot User OAuth Token" (starts with xoxb-)

7. Invite bot to channels:
   - In Slack, go to each channel you want to export
   - Type: /invite @SecondBrain Importer
   - This gives the bot access to channel history

8. Set environment variable:
   export SLACK_BOT_TOKEN="xoxb-your-token-here"

Or add to .env file:
   SLACK_BOT_TOKEN=xoxb-your-token-here
""")


if __name__ == "__main__":
    import sys

    if '--setup' in sys.argv:
        setup_slack_app()
        sys.exit(0)

    # Initialize importer
    importer = SlackImporter()

    if not importer.token:
        print("\n💡 Run with --setup for configuration instructions")
        sys.exit(1)

    # List available channels
    print("\n📺 Listing Slack channels...")
    channels = importer.list_channels()

    if channels:
        print("\n💡 To export a channel:")
        print("   importer.export_channel_messages(channel_id, channel_name, output_dir)")
        print("\n💡 To download files:")
        print("   importer.download_files_from_channel(channel_id, output_dir)")
