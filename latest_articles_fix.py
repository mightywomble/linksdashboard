def get_latest_articles_across_feeds():
    """Gets the latest article from each RSS feed and sorts by publication date."""
    config = get_config()
    feeds = config.get('rss_feeds', [])
    
    latest_articles = []
    
    for feed in feeds:
        try:
            parsed_feed = feedparser.parse(feed['url'])
            if parsed_feed.entries:
                latest_entry = parsed_feed.entries[0]
                
                pub_date = None
                if hasattr(latest_entry, 'published_parsed') and latest_entry.published_parsed:
                    try:
                        pub_date = datetime(*latest_entry.published_parsed[:6])
                    except:
                        pub_date = datetime.now()
                elif hasattr(latest_entry, 'updated_parsed') and latest_entry.updated_parsed:
                    try:
                        pub_date = datetime(*latest_entry.updated_parsed[:6])
                    except:
                        pub_date = datetime.now()
                else:
                    pub_date = datetime.now()
                
                article = {
                    'title': getattr(latest_entry, 'title', 'Untitled'),
                    'link': getattr(latest_entry, 'link', ''),
                    'summary': getattr(latest_entry, 'summary', getattr(latest_entry, 'description', ''))[:150] + '...' if getattr(latest_entry, 'summary', getattr(latest_entry, 'description', '')) else '',
                    'published': getattr(latest_entry, 'published', ''),
                    'feed_name': feed['name'],
                    'feed_link': getattr(parsed_feed.feed, 'link', feed['url']),
                    'sort_timestamp': pub_date.timestamp()
                }
                latest_articles.append(article)
        except Exception as e:
            print(f"Error fetching latest from {feed['name']}: {str(e)}")
    
    latest_articles.sort(key=lambda x: x['sort_timestamp'], reverse=True)
    
    # Remove sort_timestamp before returning
    for article in latest_articles:
        del article['sort_timestamp']
    
    return latest_articles[:5]

@app.route('/get_latest_articles', methods=['GET'])
def get_latest_articles():
    """Gets the latest articles across all RSS feeds."""
    try:
        articles = get_latest_articles_across_feeds()
        return jsonify({'articles': articles})
    except Exception as e:
        print(f"Error in get_latest_articles: {str(e)}")
        return jsonify({'error': 'Failed to fetch latest articles', 'articles': []}), 500
