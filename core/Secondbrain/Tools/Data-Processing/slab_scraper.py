import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Slab Browser Scraper - Uses Playwright to scrape all posts from Slab
Launches a browser where you can log in, then automatically downloads all content

Requirements:
    pip install playwright
    playwright install chromium
"""
import asyncio
import json
import re
from pathlib import Path
from datetime import datetime

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright not installed. Run:")
    print("  pip install playwright")
    print("  playwright install chromium")
    exit(1)

# Configuration
SLAB_URL = "https://oberaconnect.slab.com"
OUTPUT_DIR = Path("input_documents/slab_scraped")


async def scrape_slab():
    """Main scraper function"""
    print("=" * 60)
    print("Slab Browser Scraper")
    print("=" * 60)
    print()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        # Launch browser in headed mode so user can log in
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to Slab
        print(f"Opening {SLAB_URL}")
        print("Please log in to your Slab account...")
        print()
        await page.goto(SLAB_URL)

        # Wait for user to log in - look for the workspace indicator
        print("Waiting for login... (you have 2 minutes)")
        try:
            await page.wait_for_selector('text="Home"', timeout=120000)
            print("Login detected!")
        except Exception:
            print("Timeout waiting for login. Please try again.")
            await browser.close()
            return

        print()
        print("Scraping posts...")

        # Get all topics first
        topics = await get_all_topics(page)
        print(f"Found {len(topics)} topics")

        # Get all posts
        all_posts = []

        # First get posts from each topic
        for topic in topics:
            topic_name = topic['name']
            topic_url = topic['url']
            print(f"\nScraping topic: {topic_name}")

            await page.goto(topic_url)
            await page.wait_for_load_state('networkidle')

            # Scroll to load all posts (Slab may use infinite scroll)
            await scroll_to_load_all(page)

            # Get post links from this topic page using multiple strategies
            post_links = await get_posts_from_topic_page(page, topic_name)

            for post in post_links:
                if post['url'] not in [p['url'] for p in all_posts]:
                    all_posts.append(post)

        print(f"\nFound {len(all_posts)} unique posts")
        print()

        # Now scrape each post
        scraped = 0
        failed = 0

        for i, post in enumerate(all_posts, 1):
            try:
                url = post['url']
                title = post.get('title', 'Untitled')
                topic = post.get('topic', 'general')

                print(f"[{i}/{len(all_posts)}] {title[:50]}")

                await page.goto(url)
                await page.wait_for_load_state('networkidle')

                # Wait for content to load
                try:
                    await page.wait_for_selector('article, [data-testid="post-content"], .post-content, .ProseMirror, main', timeout=10000)
                except Exception:
                    # Continue anyway, might still have content
                    pass

                # Extract content
                content, page_title = await extract_post_content(page)

                # Extract author information
                author_info = await extract_author(page)

                # Use page title if we got one (more reliable)
                if page_title:
                    title = page_title

                if not content:
                    print(f"   Warning: No content extracted")
                    failed += 1
                    continue

                # Save to file
                safe_title = re.sub(r'[^\w\s-]', '', title)[:100].strip()
                if not safe_title:
                    # Fallback to URL slug
                    slug = url.split('/posts/')[-1] if '/posts/' in url else f'post_{i}'
                    safe_title = re.sub(r'[^\w\s-]', '', slug)[:100].strip()

                safe_topic = re.sub(r'[^\w\s-]', '', topic)[:50].strip()
                if not safe_topic:
                    safe_topic = 'general'

                topic_dir = OUTPUT_DIR / safe_topic
                topic_dir.mkdir(parents=True, exist_ok=True)

                # Save as text
                txt_path = topic_dir / f"{safe_title}.txt"
                txt_path.write_text(content, encoding='utf-8')

                # Save metadata as JSON
                meta_path = topic_dir / f"{safe_title}.json"
                meta = {
                    'title': title,
                    'url': url,
                    'topic': topic,
                    'author': author_info.get('name', ''),
                    'author_email': author_info.get('email', ''),
                    'source': 'slab',
                    'scraped_at': datetime.now().isoformat()
                }
                meta_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')

                scraped += 1
                author_str = author_info.get('name', 'Unknown') or 'Unknown'
                print(f"   Saved: {safe_title[:40]} (Author: {author_str})")

            except Exception as e:
                print(f"   Error: {e}")
                failed += 1
                continue

        await browser.close()

        print()
        print("=" * 60)
        print("Scraping Complete")
        print("=" * 60)
        print(f"Scraped: {scraped}")
        print(f"Failed: {failed}")
        print(f"Output: {OUTPUT_DIR}")
        print()
        print("Now run: python3 process_slab_export.py")


async def scroll_to_load_all(page, max_scrolls=10):
    """Scroll down to load all content (for infinite scroll pages)"""
    previous_height = 0
    for _ in range(max_scrolls):
        current_height = await page.evaluate('document.body.scrollHeight')
        if current_height == previous_height:
            break
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(1000)
        previous_height = current_height


async def get_posts_from_topic_page(page, topic_name):
    """Extract all post links from a topic page using multiple strategies"""
    posts = []
    seen_urls = set()

    # Strategy 1: Standard post links
    post_elements = await page.query_selector_all('a[href*="/posts/"]')

    for elem in post_elements:
        try:
            url = await elem.get_attribute('href')
            if not url or url in seen_urls:
                continue

            # Build full URL
            full_url = url if url.startswith('http') else f"{SLAB_URL}{url}"

            # Try to get title from various sources
            title = ""

            # Try direct text content first
            text = await elem.inner_text()
            if text:
                # Clean up the text - take first meaningful line
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                if lines:
                    # Filter out common UI elements
                    for line in lines:
                        if len(line) > 3 and not line.lower() in ['edit', 'delete', 'share', 'more']:
                            title = line
                            break

            # If still no title, extract from URL slug
            if not title:
                # URL format: /posts/title-slug-id
                slug = url.split('/posts/')[-1] if '/posts/' in url else ''
                if slug:
                    # Remove the ID suffix (usually last segment after -)
                    parts = slug.rsplit('-', 1)
                    if len(parts) > 1 and len(parts[1]) < 10:
                        slug = parts[0]
                    title = slug.replace('-', ' ').title()

            if title:
                seen_urls.add(full_url)
                posts.append({
                    'url': full_url,
                    'title': title,
                    'topic': topic_name
                })
        except Exception:
            continue

    # Strategy 2: Look for post list items with specific structure
    list_items = await page.query_selector_all('[data-testid*="post"], .post-item, .post-list-item, article a')

    for elem in list_items:
        try:
            # Check if it's a link or contains a link
            if await elem.get_attribute('href'):
                link = elem
            else:
                link = await elem.query_selector('a[href*="/posts/"]')

            if not link:
                continue

            url = await link.get_attribute('href')
            if not url:
                continue

            full_url = url if url.startswith('http') else f"{SLAB_URL}{url}"

            if full_url in seen_urls:
                continue

            # Try to find title in parent structure
            title = ""
            parent = elem
            title_elem = await parent.query_selector('h1, h2, h3, h4, [class*="title"], [class*="name"]')
            if title_elem:
                title = await title_elem.inner_text()

            if not title:
                text = await elem.inner_text()
                lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 3]
                if lines:
                    title = lines[0]

            if not title:
                slug = url.split('/posts/')[-1] if '/posts/' in url else ''
                if slug:
                    parts = slug.rsplit('-', 1)
                    if len(parts) > 1 and len(parts[1]) < 10:
                        slug = parts[0]
                    title = slug.replace('-', ' ').title()

            if title:
                seen_urls.add(full_url)
                posts.append({
                    'url': full_url,
                    'title': title,
                    'topic': topic_name
                })
        except Exception:
            continue

    return posts


async def get_all_topics(page):
    """Get all topic URLs from the sidebar"""
    # Wait for sidebar to load
    await page.wait_for_selector('.sidebar, nav, [data-testid="sidebar"]', timeout=10000)

    # Try multiple selectors for topics
    topics = []

    # Method 1: Look for topic links in sidebar
    topic_elements = await page.query_selector_all('a[href*="/topics/"]')

    for elem in topic_elements:
        try:
            url = await elem.get_attribute('href')
            text = await elem.inner_text()
            if url and text:
                full_url = url if url.startswith('http') else f"{SLAB_URL}{url}"
                topics.append({'name': text.strip(), 'url': full_url})
        except Exception:
            continue

    # Method 2: Look for "All Topics" section
    if not topics:
        # Click on "All Topics" if it exists
        all_topics_btn = await page.query_selector('text="All Topics"')
        if all_topics_btn:
            await all_topics_btn.click()
            await page.wait_for_timeout(1000)

            # Now get topic links
            topic_elements = await page.query_selector_all('a[href*="/topics/"]')
            for elem in topic_elements:
                try:
                    url = await elem.get_attribute('href')
                    text = await elem.inner_text()
                    if url and text:
                        full_url = url if url.startswith('http') else f"{SLAB_URL}{url}"
                        topics.append({'name': text.strip(), 'url': full_url})
                except Exception:
                    continue

    # Deduplicate
    seen = set()
    unique_topics = []
    for t in topics:
        if t['url'] not in seen:
            seen.add(t['url'])
            unique_topics.append(t)

    return unique_topics


async def extract_author(page):
    """Extract author information from a post page - finds the document creator, not logged-in user"""
    author_info = {"name": "", "email": ""}

    # Strategy 1: Look for "Created by" or "Written by" patterns
    try:
        # Get all text on page and look for author attribution patterns
        page_text = await page.inner_text('body')

        # Look for patterns like "Created by Name" or "Written by Name"
        import re
        patterns = [
            r'[Cc]reated by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'[Ww]ritten by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'[Aa]uthor[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'[Bb]y\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, page_text)
            if match:
                author_info["name"] = match.group(1).strip()
                return author_info
    except Exception:
        pass

    # Strategy 2: Look for contributor/author section that's NOT the current user menu
    try:
        # Look for elements that show document metadata (not user menu)
        meta_selectors = [
            '[class*="contributor"]:not([class*="menu"])',
            '[class*="creator"]',
            '[class*="written"]',
            '[class*="posted-by"]',
            'article [class*="author"]',
            '.post-meta [class*="name"]',
            '[data-testid="post-creator"]',
            '[data-testid="contributor"]'
        ]

        for selector in meta_selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    text = text.strip()
                    if text and 2 < len(text) < 50:
                        author_info["name"] = text
                        return author_info
            except Exception:
                continue
    except Exception:
        pass

    # Strategy 3: Look at the post header/info area for contributor avatars with names
    try:
        # Find all user links in the article/post area only (not sidebar/header)
        post_area = await page.query_selector('article, main, .post-content, [class*="post"]')
        if post_area:
            user_links = await post_area.query_selector_all('a[href*="/users/"], a[href*="/user/"]')
            for link in user_links:
                text = await link.inner_text()
                text = text.strip()
                # Skip if it looks like the current user menu or navigation
                if text and 2 < len(text) < 50:
                    skip_words = ['edit', 'delete', 'share', 'settings', 'profile', 'logout']
                    if not any(skip in text.lower() for skip in skip_words):
                        author_info["name"] = text
                        return author_info
    except Exception:
        pass

    # Strategy 4: Check for version/edit history which often shows original author
    try:
        # Click on version history if available to see original author
        version_btn = await page.query_selector('[class*="version"], [class*="history"], text="History"')
        if version_btn:
            # Don't click, but look nearby for author info
            pass
    except Exception:
        pass

    return author_info


async def extract_post_content(page):
    """Extract the main content from a post page"""
    content_parts = []
    extracted_title = ""

    # Try to get the title from the h1
    title_selectors = ['h1', '[data-testid="post-title"]', '.post-title', 'article h1']
    for selector in title_selectors:
        try:
            title_elem = await page.query_selector(selector)
            if title_elem:
                title_text = await title_elem.inner_text()
                if title_text and len(title_text.strip()) > 2:
                    extracted_title = title_text.strip()
                    content_parts.append(f"# {extracted_title}\n")
                    break
        except Exception:
            continue

    # Try to get the main content using more specific selectors
    content_selectors = [
        '.ProseMirror',  # Slab uses ProseMirror editor
        '[data-testid="post-content"]',
        'article .content',
        'article',
        '.post-content',
        '.post-body',
        'main [role="article"]',
        'main article'
    ]

    for selector in content_selectors:
        try:
            content_elem = await page.query_selector(selector)
            if content_elem:
                # Get text content
                text = await content_elem.inner_text()
                if text and len(text) > 50:
                    # Clean up the content
                    cleaned = clean_content(text, extracted_title)
                    if cleaned:
                        content_parts.append(cleaned)
                        break
        except Exception:
            continue

    # If no content found with specific selectors, try main as fallback
    if len(content_parts) <= 1:
        try:
            main_elem = await page.query_selector('main')
            if main_elem:
                text = await main_elem.inner_text()
                if text:
                    cleaned = clean_content(text, extracted_title)
                    if cleaned and len(cleaned) > 50:
                        content_parts.append(cleaned)
        except Exception:
            pass

    return '\n\n'.join(content_parts), extracted_title


def clean_content(text, title=""):
    """Remove navigation elements and clean up extracted content"""
    if not text:
        return ""

    lines = text.split('\n')
    cleaned_lines = []

    # Patterns to filter out
    skip_patterns = [
        'edited', 'published', 'ago', 'minute', 'hour', 'day', 'week', 'month',
        'home', 'search', 'settings', 'profile', 'logout', 'login',
        'create', 'new post', 'all topics', 'back to'
    ]

    # Skip the first few lines if they match navigation
    skip_initial = True

    for line in lines:
        stripped = line.strip()

        # Skip empty lines at the start
        if not stripped:
            if not skip_initial:
                cleaned_lines.append('')
            continue

        # Skip very short lines that look like UI elements
        lower = stripped.lower()

        # Skip if it matches the title (already added as header)
        if title and stripped == title:
            continue

        # Skip navigation/metadata patterns
        if any(pattern in lower for pattern in skip_patterns):
            if len(stripped) < 50:  # Only skip short lines with these patterns
                continue

        # Skip single character lines
        if len(stripped) <= 1:
            continue

        # This looks like content
        skip_initial = False
        cleaned_lines.append(stripped)

    # Join and clean up multiple empty lines
    result = '\n'.join(cleaned_lines)
    # Remove multiple consecutive empty lines
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')

    return result.strip()


def main():
    """Entry point"""
    asyncio.run(scrape_slab())


if __name__ == "__main__":
    main()
