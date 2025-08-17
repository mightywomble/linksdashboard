# Dashboard - Personal Link Management & RSS Reader

A modern, responsive web dashboard for organizing links, managing RSS feeds, and integrating AI assistance. Built with Flask, featuring a glass-morphism UI design and comprehensive admin functionality.

## Executive Summary

This dashboard application provides a centralized hub for managing bookmarks, monitoring RSS feeds, and accessing AI-powered assistance. It features a responsive 4-column layout with organized link groups, integrated RSS feed reader, and real-time AI chat functionality using OpenAI or Google Gemini APIs.

## Features

### 🔗 Link Management
- **Organized Groups**: Create custom groups with icons and descriptions
- **Drag & Drop Organization**: Move groups and links up/down for custom ordering
- **Rich Link Cards**: Display links with custom icons, names, and descriptions
- **Bulk Operations**: Edit, delete, and reorganize links in bulk
- **Icon Support**: Upload custom icons or use system-provided icons

### 📰 RSS Feed Reader
- **Multi-Feed Support**: Add and manage multiple RSS feeds
- **Real-Time Updates**: Automatically fetch and display latest articles
- **Navigation Controls**: Browse between feeds with next/previous buttons
- **Feed Information**: Display feed title, description, and source links
- **Article Preview**: Show article titles, summaries, and publication dates
- **Responsive Layout**: RSS column adjusts to match link columns height

### 🤖 AI Assistant
- **Dual AI Support**: Choose between OpenAI GPT-4o or Google Gemini 2.5 Flash
- **Slide-out Chat**: Elegant chat interface that doesn't interfere with main content
- **Technical Focus**: Optimized for server management and troubleshooting assistance
- **Session Persistence**: Maintain conversation context during session
- **API Key Management**: Secure storage and configuration of API credentials

### 🎨 Modern UI/UX
- **Glass Morphism Design**: Modern translucent design with backdrop blur effects
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile devices
- **4-Column Layout**: Optimized display with 3 link columns + 1 RSS column
- **Dark Theme**: Eye-friendly dark color scheme with gradient backgrounds
- **Smooth Animations**: Polished transitions and hover effects
- **Typography**: Clean, readable fonts with proper spacing and hierarchy

### 🔐 Security & Administration
- **Admin Authentication**: Secure login system with session management
- **Password Management**: Change admin passwords through the interface
- **API Key Protection**: Masked display of sensitive API keys
- **Input Validation**: Comprehensive validation and sanitization
- **CSRF Protection**: Built-in security measures against common attacks

### ⚙️ Configuration Management
- **JSON Storage**: Simple, portable configuration format
- **Backup Support**: Easy export/import of settings
- **Runtime Configuration**: Change settings without restarting the service
- **Multi-Environment**: Support for development and production configurations

## Usage Guide

### Initial Setup
1. **Access the Application**: Navigate to `http://your-server:5066`
2. **Admin Login**: Click the admin icon (top-right) and login with default credentials:
   - Username: `admin`
   - Password: `admin`
3. **Change Default Password**: Go to Settings → Change Admin Password
4. **Configure Dashboard**: Set your dashboard title in Settings → Dashboard Settings

### Managing Links
1. **Create Groups**: 
   - Go to Settings → Add New Group
   - Provide a name and optionally select an icon
   - Click "Add Group"

2. **Add Links**:
   - In Settings → Add New Link
   - Select target group
   - Enter link name, URL, and description
   - Upload custom icon (optional)
   - Click "Add Link"

3. **Organize Content**:
   - Use arrow buttons to move groups/links up/down
   - Edit existing items using the edit buttons
   - Delete items using the delete buttons (with confirmation)

### RSS Feed Management
1. **Add RSS Feeds**:
   - Go to Settings → RSS Feeds
   - Enter feed name and URL
   - Click "Add RSS Feed"
   - System validates feed before adding

2. **Browse RSS Content**:
   - Return to main dashboard
   - Use next/previous arrows to navigate between feeds
   - Click feed titles to visit source websites
   - Click article titles to read full articles

### AI Assistant
1. **Configure API Keys**:
   - Go to Settings → AI API Keys
   - Add your OpenAI and/or Google Gemini API keys
   - Click "Save API Keys"

2. **Using the Assistant**:
   - Click the robot icon on the left side
   - Select your preferred AI service (ChatGPT-4o or Gemini-2.5-flash)
   - Type your question and press Enter
   - Chat history is maintained during your session

## Installation & Setup

### Prerequisites
- Ubuntu 18.04 or later
- Python 3.8 or later
- Git
- Systemd (for service setup)

### Manual Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url> /opt/dashboard
   cd /opt/dashboard
   ```

2. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Test the Application**:
   ```bash
   python app.py
   ```

### Systemd Service Setup

1. **Create Service User**:
   ```bash
   sudo useradd --system --shell /bin/false dashboard
   sudo chown -R dashboard:dashboard /opt/dashboard
   ```

2. **Create Systemd Service File**:
   ```bash
   sudo tee /etc/systemd/system/dashboard.service << 'EOL'
   [Unit]
   Description=Dashboard Web Application
   After=network.target
   
   [Service]
   Type=simple
   User=dashboard
   Group=dashboard
   WorkingDirectory=/opt/dashboard
   Environment=PATH=/opt/dashboard/venv/bin
   ExecStart=/opt/dashboard/venv/bin/python app.py
   ExecReload=/bin/kill -HUP $MAINPID
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   EOL
   ```

3. **Enable and Start Service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable dashboard.service
   sudo systemctl start dashboard.service
   ```

4. **Check Service Status**:
   ```bash
   sudo systemctl status dashboard.service
   sudo journalctl -u dashboard.service -f
   ```

### Configuration Options

#### Environment Variables
- `FLASK_ENV`: Set to `production` for production deployment
- `SECRET_KEY`: Override default secret key for enhanced security
- `PORT`: Change default port (default: 5066)

#### Reverse Proxy Setup (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5066;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Troubleshooting

#### Common Issues
1. **Port Already in Use**: Change port in `app.py` or kill conflicting process
2. **Permission Errors**: Ensure proper ownership of application directory
3. **Dependencies Missing**: Reinstall requirements with `pip install -r requirements.txt`
4. **Service Won't Start**: Check logs with `journalctl -u dashboard.service`

#### Log Files
- Application logs: `journalctl -u dashboard.service`
- Flask debug logs: Console output when running manually
- Error logs: Check systemd journal for service errors

#### Performance Optimization
- Use `gunicorn` for production deployment
- Configure proper logging levels
- Set up log rotation for long-running instances
- Consider Redis for session storage in multi-instance deployments

## API Endpoints

### Public Endpoints
- `GET /` - Main dashboard
- `GET /login` - Admin login page
- `POST /login` - Login authentication

### Admin Endpoints (Authentication Required)
- `GET /settings` - Admin settings page
- `POST /add_group` - Create new group
- `POST /add_link` - Add link to group
- `POST /add_rss_feed` - Add RSS feed
- `GET /get_rss_feeds` - Fetch all RSS feeds
- `POST /chat` - AI chat endpoint

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainer.

---

**Note**: Remember to secure your API keys and change default passwords in production environments.
