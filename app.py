import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from werkzeug.utils import secure_filename
from openai import OpenAI
import google.generativeai as genai

# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key' # Replace with a real secret key
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['CONFIG_FILE'] = 'config.json'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

# --- Helper Functions ---

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_config():
    """Reads the configuration data from the JSON file."""
    if 'config' not in g:
        try:
            with open(app.config['CONFIG_FILE'], 'r') as f:
                g.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            g.config = {
                "admin": {"username": "admin", "password": "admin"},
                "groups": [],
                "api_keys": {
                    "openai_api_key": "",
                    "gemini_api_key": ""
                },
                "dashboard_title": "My Dashboard"
            }
            save_config(g.config)
    return g.config

def save_config(data):
    """Saves the configuration data to the JSON file."""
    with open(app.config['CONFIG_FILE'], 'w') as f:
        json.dump(data, f, indent=4)

@app.teardown_appcontext
def teardown_config(exception):
    """Closes the config on app context teardown."""
    g.pop('config', None)

# --- Routes ---

@app.route('/')
def index():
    """Renders the main dashboard page."""
    config = get_config()
    return render_template('index.html', 
                         groups=config.get('groups', []),
                         dashboard_title=config.get('dashboard_title', 'My Dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the admin login."""
    if request.method == 'POST':
        config = get_config()
        username = request.form['username']
        password = request.form['password']
        admin_creds = config.get('admin', {})

        if username == admin_creds.get('username') and password == admin_creds.get('password'):
            session['logged_in'] = True
            flash('You were successfully logged in!', 'success')
            return redirect(url_for('settings'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs the admin out."""
    session.pop('logged_in', None)
    flash('You were successfully logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET'])
def settings():
    """Displays the settings page."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    config = get_config()
    icon_path = os.path.join(app.static_folder, 'icons')
    available_icons = []
    if os.path.exists(icon_path):
        available_icons = [f for f in os.listdir(icon_path) if os.path.isfile(os.path.join(icon_path, f))]
    
    return render_template('settings.html', 
                           groups=config.get('groups', []), 
                           available_icons=available_icons)

@app.route('/add_group', methods=['POST'])
def add_group():
    """Handles the creation of a new group."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    config = get_config()
    group_name = request.form.get('group_name')
    group_icon = request.form.get('group_icon')

    if not group_name:
        flash('Group name is required.', 'danger')
        return redirect(url_for('settings'))

    if any(g['name'].lower() == group_name.lower() for g in config['groups']):
        flash('A group with this name already exists.', 'danger')
        return redirect(url_for('settings'))

    new_group = {
        "name": group_name,
        "icon": group_icon,
        "links": []
    }
    config['groups'].append(new_group)
    save_config(config)
    flash(f'Group "{group_name}" has been added.', 'success')
    return redirect(url_for('settings'))

@app.route('/delete_group', methods=['POST'])
def delete_group():
    """Handles deleting a group."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    config = get_config()
    group_name_to_delete = request.form.get('group_name')
    
    original_group_count = len(config['groups'])
    config['groups'] = [group for group in config['groups'] if group['name'] != group_name_to_delete]

    if len(config['groups']) < original_group_count:
        save_config(config)
        flash(f'Group "{group_name_to_delete}" has been deleted.', 'success')
    else:
        flash(f'Group "{group_name_to_delete}" not found.', 'danger')
        
    return redirect(url_for('settings'))

@app.route('/get_api_keys', methods=['GET'])
def get_api_keys():
    """Gets existing API keys for display in settings."""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authorized'}), 401

    config = get_config()
    api_keys = config.get('api_keys', {})
    
    return jsonify({
        'openai_api_key': api_keys.get('openai_api_key', ''),
        'gemini_api_key': api_keys.get('gemini_api_key', '')
    })

@app.route('/save_api_keys', methods=['POST'])
def save_api_keys():
    """Saves API keys for OpenAI and Gemini."""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authorized'}), 401

    openai_key = request.form.get('openai_api_key')
    gemini_key = request.form.get('gemini_api_key')

    config = get_config()
    
    # Ensure api_keys section exists
    if 'api_keys' not in config:
        config['api_keys'] = {
            'openai_api_key': '',
            'gemini_api_key': ''
        }

    if openai_key:
        config['api_keys']['openai_api_key'] = openai_key
    if gemini_key:
        config['api_keys']['gemini_api_key'] = gemini_key

    save_config(config)
    return jsonify({'success': True})

@app.route('/change_admin_password', methods=['POST'])
def change_admin_password():
    """Changes the admin password."""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authorized'}), 401

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400

    config = get_config()
    admin_creds = config.get('admin', {})

    # Verify current password
    if current_password != admin_creds.get('password'):
        return jsonify({'error': 'Current password is incorrect'}), 400

    # Validate new password length
    if len(new_password) < 4:
        return jsonify({'error': 'New password must be at least 4 characters long'}), 400

    # Update password in config
    config['admin']['password'] = new_password
    save_config(config)
    
    return jsonify({'success': True})

@app.route('/get_dashboard_title', methods=['GET'])
def get_dashboard_title():
    """Gets the current dashboard title."""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authorized'}), 401

    config = get_config()
    return jsonify({'dashboard_title': config.get('dashboard_title', 'My Dashboard')})

@app.route('/save_dashboard_title', methods=['POST'])
def save_dashboard_title():
    """Saves the dashboard title."""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authorized'}), 401

    dashboard_title = request.form.get('dashboard_title')
    
    if not dashboard_title:
        return jsonify({'error': 'Dashboard title is required'}), 400

    # Validate title length
    if len(dashboard_title) > 50:
        return jsonify({'error': 'Dashboard title must be 50 characters or less'}), 400

    config = get_config()
    config['dashboard_title'] = dashboard_title.strip()
    save_config(config)
    
    return jsonify({'success': True})

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat requests using chosen API."""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authorized'}), 401

    config = get_config()
    message = request.json.get('message')
    service = request.json.get('service', 'openai')
    
    # Ensure api_keys section exists
    if 'api_keys' not in config:
        return jsonify({'error': 'API keys not configured. Please add them in Settings.'}), 400
    
    try:
        if service == 'gemini-2.5-flash':
            # Configure Gemini API
            gemini_key = config['api_keys'].get('gemini_api_key')
            if not gemini_key:
                return jsonify({'error': 'Gemini API key not configured'}), 400
            
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            response = model.generate_content(message)
            return jsonify({'message': response.text})
            
        else:  # OpenAI ChatGPT-4o
            openai_key = config['api_keys'].get('openai_api_key')
            if not openai_key:
                return jsonify({'error': 'OpenAI API key not configured'}), 400
            
            client = OpenAI(api_key=openai_key)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a dashboard application. Help users with technical questions, server management, troubleshooting, and general IT support."},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return jsonify({'message': response.choices[0].message.content})
            
    except Exception as e:
        print(f"Chat API Error: {str(e)}")
        return jsonify({'error': f'API Error: {str(e)}'}), 500

@app.route('/add_link', methods=['POST'])
def add_link():
    """Handles the creation of a new link within a group."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    config = get_config()
    group_name = request.form.get('group_name')
    link_name = request.form.get('link_name')
    link_url = request.form.get('link_url')
    link_description = request.form.get('link_description')
    icon_file = request.files.get('link_icon')

    if not all([group_name, link_name, link_url]):
        flash('Group, Link Name, and URL are required fields.', 'danger')
        return redirect(url_for('settings'))

    target_group = next((g for g in config['groups'] if g['name'] == group_name), None)
    if not target_group:
        flash('Group not found.', 'danger')
        return redirect(url_for('settings'))

    icon_filename = None
    if icon_file and allowed_file(icon_file.filename):
        filename = secure_filename(icon_file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        icon_file.save(save_path)
        icon_filename = filename

    new_link = {
        "name": link_name,
        "url": link_url,
        "description": link_description,
        "icon": icon_filename
    }
    
    target_group['links'].append(new_link)
    save_config(config)
    flash(f'Link "{link_name}" has been added to group "{group_name}".', 'success')
    return redirect(url_for('settings'))

@app.route('/delete_link', methods=['POST'])
def delete_link():
    """Handles deleting a link from a group."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    config = get_config()
    group_name = request.form.get('group_name')
    link_name_to_delete = request.form.get('link_name')

    target_group = next((g for g in config['groups'] if g['name'] == group_name), None)
    
    if not target_group:
        flash('Group not found.', 'danger')
        return redirect(url_for('settings'))

    original_link_count = len(target_group['links'])
    target_group['links'] = [link for link in target_group['links'] if link['name'] != link_name_to_delete]

    if len(target_group['links']) < original_link_count:
        save_config(config)
        flash(f'Link "{link_name_to_delete}" has been deleted from "{group_name}".', 'success')
    else:
        flash(f'Link "{link_name_to_delete}" not found in group "{group_name}".', 'danger')

    return redirect(url_for('settings'))

@app.route('/edit_group', methods=['POST'])
def edit_group():
    """Handles editing a group's details."""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authorized'}), 401

    config = get_config()
    old_group_name = request.form.get('old_name')
    new_group_name = request.form.get('new_name')
    new_group_icon = request.form.get('icon')

    if not all([old_group_name, new_group_name]):
        return jsonify({'error': 'Group names are required'}), 400

    # Find the target group
    target_group = next((g for g in config['groups'] if g['name'] == old_group_name), None)
    if not target_group:
        return jsonify({'error': 'Group not found'}), 404

    # Check if new name conflicts with existing groups (except the current one)
    if new_group_name.lower() != old_group_name.lower():
        if any(g['name'].lower() == new_group_name.lower() for g in config['groups']):
            return jsonify({'error': 'A group with this name already exists'}), 400

    # Update the group
    target_group['name'] = new_group_name
    target_group['icon'] = new_group_icon
    save_config(config)
    return jsonify({'success': True})

@app.route('/edit_link', methods=['POST'])
def edit_link():
    """Handles editing a link's details."""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authorized'}), 401

    config = get_config()
    group_name = request.form.get('group_name')
    old_link_name = request.form.get('old_name')
    new_link_name = request.form.get('new_name')
    new_link_url = request.form.get('new_url')
    new_link_description = request.form.get('new_description')
    icon_file = request.files.get('new_icon')

    if not all([group_name, old_link_name, new_link_name, new_link_url]):
        return jsonify({'error': 'Group name, old link name, new link name, and URL are required'}), 400

    # Find the target group
    target_group = next((g for g in config['groups'] if g['name'] == group_name), None)
    if not target_group:
        return jsonify({'error': 'Group not found'}), 404

    # Find the target link
    target_link = next((l for l in target_group['links'] if l['name'] == old_link_name), None)
    if not target_link:
        return jsonify({'error': 'Link not found'}), 404

    # Handle icon upload if provided
    icon_filename = target_link.get('icon')  # Keep existing icon by default
    if icon_file and allowed_file(icon_file.filename):
        filename = secure_filename(icon_file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        icon_file.save(save_path)
        icon_filename = filename

    # Update the link
    target_link['name'] = new_link_name
    target_link['url'] = new_link_url
    target_link['description'] = new_link_description
    target_link['icon'] = icon_filename
    
    save_config(config)
    return jsonify({'success': True})

@app.route('/move_group', methods=['POST'])
def move_group():
    """Handles moving a group up or down in the list."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    config = get_config()
    group_name = request.form.get('group_name')
    direction = request.form.get('direction')  # 'up' or 'down'

    if not all([group_name, direction]):
        flash('Group name and direction are required.', 'danger')
        return redirect(url_for('settings'))

    # Find the group index
    group_index = next((i for i, g in enumerate(config['groups']) if g['name'] == group_name), None)
    if group_index is None:
        flash('Group not found.', 'danger')
        return redirect(url_for('settings'))

    # Move the group
    if direction == 'up' and group_index > 0:
        config['groups'][group_index], config['groups'][group_index - 1] = config['groups'][group_index - 1], config['groups'][group_index]
        save_config(config)
        flash(f'Group "{group_name}" moved up.', 'success')
    elif direction == 'down' and group_index < len(config['groups']) - 1:
        config['groups'][group_index], config['groups'][group_index + 1] = config['groups'][group_index + 1], config['groups'][group_index]
        save_config(config)
        flash(f'Group "{group_name}" moved down.', 'success')
    else:
        flash('Cannot move group in that direction.', 'warning')

    return redirect(url_for('settings'))

@app.route('/move_link', methods=['POST'])
def move_link():
    """Handles moving a link up or down within its group."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    config = get_config()
    group_name = request.form.get('group_name')
    link_name = request.form.get('link_name')
    direction = request.form.get('direction')  # 'up' or 'down'

    if not all([group_name, link_name, direction]):
        flash('Group name, link name, and direction are required.', 'danger')
        return redirect(url_for('settings'))

    # Find the target group
    target_group = next((g for g in config['groups'] if g['name'] == group_name), None)
    if not target_group:
        flash('Group not found.', 'danger')
        return redirect(url_for('settings'))

    # Find the link index
    link_index = next((i for i, l in enumerate(target_group['links']) if l['name'] == link_name), None)
    if link_index is None:
        flash('Link not found.', 'danger')
        return redirect(url_for('settings'))

    # Move the link
    if direction == 'up' and link_index > 0:
        target_group['links'][link_index], target_group['links'][link_index - 1] = target_group['links'][link_index - 1], target_group['links'][link_index]
        save_config(config)
        flash(f'Link "{link_name}" moved up.', 'success')
    elif direction == 'down' and link_index < len(target_group['links']) - 1:
        target_group['links'][link_index], target_group['links'][link_index + 1] = target_group['links'][link_index + 1], target_group['links'][link_index]
        save_config(config)
        flash(f'Link "{link_name}" moved down.', 'success')
    else:
        flash('Cannot move link in that direction.', 'warning')

    return redirect(url_for('settings'))


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(os.path.join(app.static_folder, 'icons')):
        os.makedirs(os.path.join(app.static_folder, 'icons'))
        
    app.run(debug=True, host='0.0.0.0', port=5065)
