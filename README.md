# Personal Dashboard Application

A modern, sleek web-based dashboard application built with Flask that allows you to organize and manage your personal links with AI chat integration. Features a beautiful glass-morphism UI design with customizable groups, links, and AI-powered assistance.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure admin login with session management
- **Group & Link Management**: Create, edit, delete, and reorder groups and links
- **File Upload Support**: Custom icons for groups and links with image upload
- **Responsive Design**: Modern glass-morphism UI that works on all devices
- **Configuration Management**: JSON-based configuration system

### AI Integration
- **OpenAI ChatGPT-4o Integration**: Get AI assistance for technical questions
- **Google Gemini 2.5 Flash**: Alternative AI service for varied responses
- **Context-Aware Chat**: AI assistant specialized for dashboard and IT support

### Admin Features
- **API Key Management**: Secure storage and management of AI API keys
- **Password Management**: Change admin credentials through the UI
- **Dashboard Customization**: Set custom dashboard titles
- **Link Organization**: Move groups and links up/down for custom ordering

## 📋 Prerequisites

- Python 3.7 or higher
- Virtual environment tool (recommended)
- OpenAI API key (optional, for AI chat features)
- Google Gemini API key (optional, for AI chat features)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd dashboard
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create necessary directories:**
   ```bash
   mkdir -p static/uploads static/icons
   ```

## ⚙️ Configuration

The application will automatically create a `config.json` file on first run with default settings:

```json
{
    "admin": {
        "username": "admin",
        "password": "admin"
    },
    "groups": [],
    "api_keys": {
        "openai_api_key": "",
        "gemini_api_key": ""
    },
    "dashboard_title": "My Dashboard"
}
```

**⚠️ Important**: Change the default admin password after first login!

## 🚀 Running the Application

1. **Start the development server:**
   ```bash
   python app.py
   ```
   The application will run on `http://0.0.0.0:5065`

2. **Access the dashboard:**
   - Main dashboard: `http://localhost:5065`
   - Admin login: `http://localhost:5065/login`

3. **Default login credentials:**
   - Username: `admin`
   - Password: `admin`

## 📚 Usage Guide

### Getting Started
1. **Login** with the default admin credentials
2. **Change your password** in the Admin Settings section
3. **Add API keys** (optional) for AI chat functionality
4. **Create groups** to organize your links
5. **Add links** to your groups with custom icons

### Managing Groups
- Create new groups with optional icons
- Edit group names and icons
- Reorder groups using up/down arrows
- Delete groups (this will also delete all links in the group)

### Managing Links
- Add links to existing groups
- Upload custom icons for links
- Edit link details including name, URL, and description
- Links without custom icons will show the first letter of their name

### AI Chat Features
- Configure OpenAI or Google Gemini API keys in settings
- Use the chat feature for technical assistance
- AI is specialized for dashboard management and IT support

## 📁 Project Structure

```
dashboard/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── config.json           # Configuration file (auto-generated)
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Main dashboard
│   ├── login.html        # Login page
│   └── settings.html     # Admin settings
├── static/
│   ├── uploads/          # User-uploaded link icons
│   └── icons/            # Group icons
└── README.md
```

## 🔧 Dependencies

- **Flask==3.0.0** - Web framework
- **Werkzeug==3.0.1** - WSGI utilities
- **requests==2.31.0** - HTTP library
- **openai==1.3.7** - OpenAI API client
- **google-generativeai==0.3.2** - Google Gemini API client

## 🔒 Security Notes

- Change default admin credentials immediately after installation
- API keys are stored in the config file - ensure proper file permissions
- The application runs in debug mode by default - disable for production
- Consider using environment variables for sensitive data in production

## 🎨 UI Features

- **Glass-morphism Design**: Modern, translucent UI elements
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Dark Theme**: Easy on the eyes with a space-themed background
- **Interactive Elements**: Hover effects and smooth transitions
- **Icon Support**: Upload custom icons or use auto-generated letter icons

## 🔄 API Endpoints

- `GET /` - Main dashboard
- `GET|POST /login` - Admin authentication
- `GET /settings` - Admin settings page
- `POST /add_group` - Create new group
- `POST /add_link` - Create new link
- `POST /edit_group` - Edit group details
- `POST /edit_link` - Edit link details
- `POST /delete_group` - Delete group
- `POST /delete_link` - Delete link
- `POST /move_group` - Reorder groups
- `POST /chat` - AI chat endpoint
- `POST /save_api_keys` - Save API keys
- `POST /change_admin_password` - Change admin password

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

