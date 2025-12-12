#!/usr/bin/env python3
"""
Slab Importer - Fetches content from Slab knowledge base via GraphQL API
Similar to SharePoint importer but for Slab

Requirements:
- Slab Business or Enterprise plan (API access)
- API token from Slab workspace settings

Setup:
1. Go to your Slab workspace settings
2. Navigate to Developer Tools / API & Webhooks
3. Copy the API token
4. Add to .env: SLAB_API_TOKEN=your_token_here
"""
import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Slab GraphQL endpoint
SLAB_GRAPHQL_URL = "https://api.slab.com/v1/graphql"


class SlabImporter:
    """Fetches content from Slab knowledge base"""

    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv("SLAB_API_TOKEN")

        if not self.api_token:
            raise ValueError(
                "SLAB_API_TOKEN not set. Get it from your Slab workspace settings > Developer Tools"
            )

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        print("Slab importer initialized")

    def _execute_query(self, query: str, variables: Dict = None) -> Dict:
        """Execute a GraphQL query against Slab API"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            SLAB_GRAPHQL_URL,
            headers=self.headers,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"Slab API error: {response.status_code} - {response.text}")

        result = response.json()

        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")

        return result.get("data", {})

    def get_organization_info(self) -> Dict:
        """Get organization information"""
        query = """
        query {
            organization {
                id
                name
                subdomain
            }
        }
        """
        return self._execute_query(query)

    def list_topics(self) -> List[Dict]:
        """List all topics (folders) in the knowledge base"""
        query = """
        query {
            topics {
                id
                name
                description
                postsCount
                parent {
                    id
                    name
                }
            }
        }
        """
        data = self._execute_query(query)
        return data.get("topics", [])

    def list_posts(self, topic_id: str = None, limit: int = 100) -> List[Dict]:
        """
        List posts, optionally filtered by topic

        Args:
            topic_id: Optional topic ID to filter posts
            limit: Maximum number of posts to fetch
        """
        if topic_id:
            query = """
            query($topicId: ID!, $limit: Int!) {
                topic(id: $topicId) {
                    posts(first: $limit) {
                        id
                        title
                        insertedAt
                        updatedAt
                        version
                    }
                }
            }
            """
            data = self._execute_query(query, {"topicId": topic_id, "limit": limit})
            return data.get("topic", {}).get("posts", [])
        else:
            query = """
            query($limit: Int!) {
                posts(first: $limit) {
                    id
                    title
                    insertedAt
                    updatedAt
                    version
                }
            }
            """
            data = self._execute_query(query, {"limit": limit})
            return data.get("posts", [])

    def get_post_content(self, post_id: str) -> Dict:
        """
        Get full content of a specific post

        Args:
            post_id: The post ID

        Returns:
            Post data including content
        """
        query = """
        query($postId: ID!) {
            post(id: $postId) {
                id
                title
                content
                insertedAt
                updatedAt
                version
                topics {
                    id
                    name
                }
                contributors {
                    id
                    name
                    email
                }
            }
        }
        """
        data = self._execute_query(query, {"postId": post_id})
        return data.get("post", {})

    def search_posts(self, query_text: str, limit: int = 20) -> List[Dict]:
        """
        Search posts by text

        Args:
            query_text: Search query
            limit: Maximum results
        """
        query = """
        query($query: String!, $limit: Int!) {
            searchPosts(query: $query, first: $limit) {
                id
                title
                insertedAt
            }
        }
        """
        data = self._execute_query(query, {"query": query_text, "limit": limit})
        return data.get("searchPosts", [])

    def download_all_posts(self, output_dir: Path, limit: int = 500) -> List[Path]:
        """
        Download all posts to local directory

        Args:
            output_dir: Directory to save posts
            limit: Maximum posts to download

        Returns:
            List of downloaded file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get all posts
        posts = self.list_posts(limit=limit)
        downloaded = []

        print(f"Found {len(posts)} posts to download")

        for i, post_summary in enumerate(posts, 1):
            try:
                post_id = post_summary["id"]
                title = post_summary["title"]

                print(f"[{i}/{len(posts)}] Downloading: {title[:50]}")

                # Get full content
                post = self.get_post_content(post_id)

                if not post:
                    continue

                # Create safe filename
                safe_title = "".join(
                    c for c in title if c.isalnum() or c in (' ', '-', '_')
                ).strip()
                safe_title = safe_title[:100]  # Limit length

                # Determine subfolder from topics
                topics = post.get("topics", [])
                if topics:
                    topic_name = topics[0].get("name", "general")
                    topic_folder = "".join(
                        c for c in topic_name if c.isalnum() or c in (' ', '-', '_')
                    ).strip()
                else:
                    topic_folder = "general"

                # Save as JSON for full data preservation
                post_dir = output_dir / topic_folder
                post_dir.mkdir(parents=True, exist_ok=True)

                json_path = post_dir / f"{safe_title}.json"
                json_path.write_text(json.dumps(post, indent=2), encoding='utf-8')

                # Also save content as plain text for processing
                txt_path = post_dir / f"{safe_title}.txt"
                content = post.get("content", "")

                # Convert Slab content format to plain text
                plain_text = self._extract_plain_text(content)
                txt_path.write_text(plain_text, encoding='utf-8')

                downloaded.append(txt_path)

            except Exception as e:
                print(f"   Error: {e}")
                continue

        print(f"\nDownloaded {len(downloaded)} posts to {output_dir}")
        return downloaded

    def _extract_plain_text(self, content: Any) -> str:
        """
        Extract plain text from Slab content format

        Slab uses a JSON-based content format (similar to ProseMirror)
        """
        if not content:
            return ""

        if isinstance(content, str):
            # Try to parse as JSON
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                return content

        if isinstance(content, dict):
            return self._extract_text_from_node(content)

        return str(content)

    def _extract_text_from_node(self, node: Dict) -> str:
        """Recursively extract text from Slab content nodes"""
        text_parts = []

        # Get text from this node
        if "text" in node:
            text_parts.append(node["text"])

        # Process child content
        if "content" in node and isinstance(node["content"], list):
            for child in node["content"]:
                if isinstance(child, dict):
                    text_parts.append(self._extract_text_from_node(child))

        # Add spacing for block elements
        node_type = node.get("type", "")
        if node_type in ["paragraph", "heading", "listItem", "codeBlock"]:
            return "\n".join(text_parts) + "\n"

        return " ".join(text_parts)


def main():
    """Test the Slab importer"""
    print("=" * 60)
    print("Slab Importer Test")
    print("=" * 60)
    print()

    try:
        importer = SlabImporter()

        # Get org info
        print("Organization Info:")
        org = importer.get_organization_info()
        print(json.dumps(org, indent=2))
        print()

        # List topics
        print("Topics:")
        topics = importer.list_topics()
        for topic in topics[:10]:
            print(f"  - {topic['name']} ({topic.get('postsCount', 0)} posts)")
        print()

        # List recent posts
        print("Recent Posts:")
        posts = importer.list_posts(limit=10)
        for post in posts:
            print(f"  - {post['title']}")

    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Make sure you have:")
        print("1. SLAB_API_TOKEN set in your .env file")
        print("2. A Slab Business or Enterprise plan with API access")


if __name__ == "__main__":
    main()
