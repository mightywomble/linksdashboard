# Add this function to app.py to get latest articles across all feeds

def get_latest_articles_across_feeds():
    """Gets the latest article from each RSS feed and sorts by publication date."""
    config = get_config()
    feeds = config.get('rss_feeds', [])
    
    latest_articles = []
    
    for feed in feeds:
        try:
            parsed_feed = feedparser.parse(feed['url'])
            if parsed_feed.entries:
                # Get the most recent entry
                latest_entry = parsed_feed.entries[0]
                
                # Parse publication date for sorting
                pub_date = None
                if hasattr(latest_entry, 'published_parsed') and latest_entry.published_parsed:
                    pub_date = datetime(*latest_entry.published_parsed[:6])
                elif hasattr(latest_entry, 'updated_parsed') and latest_entry.updated_parsed:
                    pub_date = datetime(*latest_entry.updated_parsed[:6])
                
                article = {
                    'title': getattr(latest_entry, 'title', 'Untitled'),
                    'link': getattr(latest_entry, 'link', ''),
                    'summary': getattr(latest_entry, 'summary', getattr(latest_entry, 'description', ''))[:150] + '...' if getattr(latest_entry, 'summary', getattr(latest_entry, 'description', '')) else '',
                    'published': getattr(latest_entry, 'published', ''),
                    'feed_name': feed['name'],
                    'feed_link': getattr(parsed_feed.feed, 'link', feed['url']),
                    'pub_date': pub_date or datetime.now()
                }
                latest_articles.append(article)
        except Exception as e:
            print(f"Error fetching latest from {feed['name']}: {str(e)}")
    
    # Sort by publication date (newest first)
    latest_articles.sort(key=lambda x: x['pub_date'], reverse=True)
    return latest_articles[:5]  # Return top 5 latest articles

@app.route('/get_latest_articles', methods=['GET'])
def get_latest_articles():
    """Gets the latest articles across all RSS feeds."""
    articles = get_latest_articles_across_feeds()
    return jsonify({'articles': articles})
