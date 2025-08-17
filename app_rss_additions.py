import feedparser
from datetime import datetime
import threading
import time

# Add these new routes and functions to app.py

def fetch_rss_feed(feed_url):
    """Fetches RSS feed and returns parsed data."""
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            print(f"Warning: RSS feed {feed_url} has malformed XML")
        
        feed_data = {
            'title': getattr(feed.feed, 'title', 'Unknown Feed'),
            'link': getattr(feed.feed, 'link', feed_url),
            'description': getattr(feed.feed, 'description', ''),
            'entries': []
        }
        
        # Get the latest 3 entries
        for entry in feed.entries[:3]:
            entry_data = {
                'title': getattr(entry, 'title', 'Untitled'),
                'link': getattr(entry, 'link', ''),
                'summary': getattr(entry, 'summary', getattr(entry, 'description', ''))[:150] + '...' if getattr(entry, 'summary', getattr(entry, 'description', '')) else '',
                'published': getattr(entry, 'published', '')
            }
            feed_data['entries'].append(entry_data)
        
        return feed_data
    except Exception as e:
        print(f"Error fetching RSS feed {feed_url}: {str(e)}")
        return None

@app.route('/add_rss_feed', methods=['POST'])
def add_rss_feed():
    """Handles adding a new RSS feed."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    config = get_config()
    feed_name = request.form.get('feed_name')
    feed_url = request.form.get('feed_url')

    if not all([feed_name, feed_url]):
        flash('Feed Name and URL are required fields.', 'danger')
        return redirect(url_for('settings'))

    # Ensure rss_feeds section exists
    if 'rss_feeds' not in config:
        config['rss_feeds'] = []

    # Check if feed already exists
    if any(feed['name'].lower() == feed_name.lower() for feed in config['rss_feeds']):
        flash('A feed with this name already exists.', 'danger')
        return redirect(url_for('settings'))

    # Test the RSS feed first
    test_feed = fetch_rss_feed(feed_url)
    if not test_feed:
        flash('Unable to fetch RSS feed. Please check the URL.', 'danger')
        return redirect(url_for('settings'))

    new_feed = {
        "name": feed_name,
        "url": feed_url,
        "last_fetched": None
    }
    
    config['rss_feeds'].append(new_feed)
    save_config(config)
    flash(f'RSS Feed "{feed_name}" has been added.', 'success')
    return redirect(url_for('settings'))

@app.route('/delete_rss_feed', methods=['POST'])
def delete_rss_feed():
    """Handles deleting an RSS feed."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    config = get_config()
    feed_name_to_delete = request.form.get('feed_name')
    
    if 'rss_feeds' not in config:
        config['rss_feeds'] = []
    
    original_feed_count = len(config['rss_feeds'])
    config['rss_feeds'] = [feed for feed in config['rss_feeds'] if feed['name'] != feed_name_to_delete]

    if len(config['rss_feeds']) < original_feed_count:
        save_config(config)
        flash(f'RSS Feed "{feed_name_to_delete}" has been deleted.', 'success')
    else:
        flash(f'RSS Feed "{feed_name_to_delete}" not found.', 'danger')
        
    return redirect(url_for('settings'))

@app.route('/get_rss_feeds', methods=['GET'])
def get_rss_feeds():
    """Gets all RSS feeds with their latest entries."""
    config = get_config()
    feeds = config.get('rss_feeds', [])
    
    feed_data = []
    for feed in feeds:
        data = fetch_rss_feed(feed['url'])
        if data:
            data['name'] = feed['name']
            feed_data.append(data)
    
    return jsonify({'feeds': feed_data})

@app.route('/get_rss_feed_page/<int:page>', methods=['GET'])
def get_rss_feed_page(page):
    """Gets a specific page of RSS feeds (for pagination)."""
    config = get_config()
    feeds = config.get('rss_feeds', [])
    
    if page < 0 or page >= len(feeds):
        return jsonify({'error': 'Invalid page number'}), 400
    
    feed = feeds[page]
    data = fetch_rss_feed(feed['url'])
    if data:
        data['name'] = feed['name']
        return jsonify({'feed': data, 'total_feeds': len(feeds), 'current_page': page})
    
    return jsonify({'error': 'Failed to fetch feed'}), 500
