"""Crawling helper utilities for testing."""

import requests
from typing import Dict, List, Set, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class SimpleCrawler:
    """
    Simple breadth-first crawler for testing purposes.

    Not a full-featured crawler - designed specifically for
    deterministic test site crawling.
    """

    def __init__(self, session: requests.Session, max_pages: int = 100):
        """
        Initialize crawler.

        Args:
            session: HTTP session to use
            max_pages: Maximum pages to crawl
        """
        self.session = session
        self.max_pages = max_pages
        self.visited: Set[str] = set()
        self.pages: List[Dict] = []
        self.errors: List[Dict] = []

    def crawl(self, start_url: str) -> Dict:
        """
        Crawl starting from URL.

        Args:
            start_url: Starting URL

        Returns:
            Dict with crawl results
        """
        to_visit = [start_url]
        base_domain = urlparse(start_url).netloc

        while to_visit and len(self.visited) < self.max_pages:
            url = to_visit.pop(0)

            if url in self.visited:
                continue

            # Skip if different domain
            if urlparse(url).netloc != base_domain:
                continue

            try:
                response = self.session.get(url, timeout=10, allow_redirects=True)
                self.visited.add(url)

                page_data = {
                    'url': response.url,
                    'requested_url': url,
                    'status_code': response.status_code,
                    'content_type': response.headers.get('Content-Type', ''),
                    'content_length': len(response.content),
                    'redirect_count': len(response.history),
                    'links': []
                }

                # Extract links if HTML
                if response.status_code == 200 and 'html' in page_data['content_type']:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = extract_links(soup, response.url)
                    page_data['links'] = links

                    # Add new links to queue
                    for link in links:
                        if link not in self.visited and link not in to_visit:
                            # Only crawl same domain
                            if urlparse(link).netloc == base_domain:
                                to_visit.append(link)

                self.pages.append(page_data)

            except Exception as e:
                self.errors.append({
                    'url': url,
                    'error': str(e)
                })

        return {
            'pages_crawled': len(self.pages),
            'pages': self.pages,
            'errors': self.errors,
            'urls_visited': list(self.visited)
        }


def extract_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """
    Extract all links from HTML.

    Args:
        soup: BeautifulSoup object
        base_url: Base URL for relative links

    Returns:
        List of absolute URLs
    """
    links = []

    for anchor in soup.find_all('a', href=True):
        href = anchor['href']

        # Skip anchors and javascript
        if href.startswith('#') or href.startswith('javascript:'):
            continue

        # Convert to absolute URL
        absolute_url = urljoin(base_url, href)

        # Remove fragments
        absolute_url = absolute_url.split('#')[0]

        links.append(absolute_url)

    return list(set(links))  # Deduplicate


def follow_redirects(session: requests.Session, url: str, max_redirects: int = 10) -> Dict:
    """
    Follow redirect chain and return details.

    Args:
        session: HTTP session
        url: Starting URL
        max_redirects: Maximum redirects to follow

    Returns:
        Dict with redirect chain details
    """
    response = session.get(url, allow_redirects=True, timeout=10)

    chain = []
    for redirect in response.history:
        chain.append({
            'url': redirect.url,
            'status_code': redirect.status_code,
            'location': redirect.headers.get('Location', '')
        })

    return {
        'start_url': url,
        'final_url': response.url,
        'redirect_count': len(response.history),
        'redirect_chain': chain,
        'final_status': response.status_code
    }
