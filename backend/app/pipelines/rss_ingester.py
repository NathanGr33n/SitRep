"""
RSS feed ingestion adapter.
Fetches articles from RSS feeds and queues them for processing.
"""
import logging
from datetime import datetime
from typing import List, Dict
import feedparser
from dateutil import parser as date_parser

from app.config import settings

logger = logging.getLogger(__name__)


class RSSIngester:
    """
    Ingests articles from RSS feeds.
    Supports standard RSS 2.0 and Atom feeds.
    """
    
    def __init__(self):
        self.max_articles = settings.max_articles_per_source
    
    def fetch_feed(self, feed_url: str) -> List[Dict]:
        """
        Fetch and parse an RSS feed.
        
        Args:
            feed_url: URL of the RSS feed
        
        Returns:
            List of article dictionaries with title, content, url, published_date
        """
        try:
            logger.info(f"Fetching RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
            
            articles = []
            
            for entry in feed.entries[:self.max_articles]:
                article = self._parse_entry(entry, feed_url)
                if article:
                    articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from {feed_url}")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to fetch RSS feed {feed_url}: {e}")
            return []
    
    def _parse_entry(self, entry, feed_url: str) -> Dict:
        """
        Parse a single feed entry into article dictionary.
        
        Args:
            entry: feedparser entry object
            feed_url: Source feed URL
        
        Returns:
            Article dictionary or None if parsing fails
        """
        try:
            # Extract title
            title = entry.get("title", "Untitled")
            
            # Extract content (try multiple fields)
            content = ""
            if hasattr(entry, "content"):
                content = entry.content[0].value
            elif hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "description"):
                content = entry.description
            
            if not content:
                logger.warning(f"No content found for entry: {title}")
                return None
            
            # Clean HTML tags if present
            content = self._strip_html(content)
            
            # Extract URL
            url = entry.get("link", feed_url)
            
            # Extract published date
            published_date = self._parse_date(entry)
            
            return {
                "title": title,
                "content": content,
                "url": url,
                "published_date": published_date
            }
            
        except Exception as e:
            logger.error(f"Failed to parse entry: {e}")
            return None
    
    def _parse_date(self, entry) -> datetime:
        """
        Parse published date from entry.
        Tries multiple date fields and formats.
        """
        date_fields = ["published_parsed", "updated_parsed", "published", "updated"]
        
        for field in date_fields:
            if hasattr(entry, field):
                date_value = getattr(entry, field)
                
                # Handle time.struct_time
                if hasattr(date_value, "tm_year"):
                    return datetime(*date_value[:6])
                
                # Handle string dates
                if isinstance(date_value, str):
                    try:
                        return date_parser.parse(date_value)
                    except:
                        pass
        
        # Fallback to current time
        logger.warning("Could not parse date, using current time")
        return datetime.utcnow()
    
    def _strip_html(self, html_text: str) -> str:
        """
        Remove HTML tags from text.
        Simple regex-based approach.
        """
        import re
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', html_text)
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        
        return text


# Example security-related RSS feeds
EXAMPLE_FEEDS = [
    # Defense and security news
    "https://www.defense.gov/News/News-Stories/RSS/",
    "https://www.nato.int/cps/en/natohq/news.rss",
    
    # General news (filter for security topics)
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    
    # Think tanks
    "https://www.csis.org/programs/international-security-program/rss.xml",
    
    # Government sources
    "https://www.state.gov/rss-feed/press-releases/feed/",
]


# Singleton instance
rss_ingester = RSSIngester()
