#!/usr/bin/env python3
import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import json

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state.json')
METADATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metadata.json')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_metadata():
    """Load image metadata from file"""
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'images': {}, 'users': {}}

def save_metadata(metadata):
    """Save image metadata to file"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def add_image_metadata(filename, uploader_ip):
    """Add metadata for a newly uploaded image"""
    metadata = load_metadata()
    metadata['images'][filename] = {
        'uploader_ip': uploader_ip,
        'upload_time': datetime.now().isoformat()
    }
    save_metadata(metadata)

def remove_image_metadata(filename):
    """Remove metadata for a deleted image"""
    metadata = load_metadata()
    if filename in metadata['images']:
        del metadata['images'][filename]
        save_metadata(metadata)

def set_user_name(ip, name):
    """Set a display name for a user IP"""
    metadata = load_metadata()
    if 'users' not in metadata:
        metadata['users'] = {}
    metadata['users'][ip] = {
        'name': name,
        'updated': datetime.now().isoformat()
    }
    save_metadata(metadata)

def get_user_name(ip):
    """Get the display name for a user IP, or return the IP if no name set"""
    metadata = load_metadata()
    if 'users' in metadata and ip in metadata['users']:
        return metadata['users'][ip].get('name', ip)
    return ip

def get_all_users():
    """Get list of all unique uploader IPs with their names"""
    metadata = load_metadata()
    users = set()
    for img_data in metadata['images'].values():
        users.add(img_data['uploader_ip'])

    # Build user list with names
    user_list = []
    for ip in sorted(list(users)):
        user_list.append({
            'ip': ip,
            'name': get_user_name(ip)
        })
    return user_list

def get_image_list(filter_user=None):
    """Get list of uploaded images with metadata

    Args:
        filter_user: Optional IP address to filter images by uploader
    """
    metadata = load_metadata()
    images = []

    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                stat = os.stat(filepath)

                # Get uploader info from metadata
                img_metadata = metadata['images'].get(filename, {})
                uploader_ip = img_metadata.get('uploader_ip', 'unknown')

                # Apply user filter if specified
                if filter_user and uploader_ip != filter_user:
                    continue

                images.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'uploaded': img_metadata.get('upload_time', datetime.fromtimestamp(stat.st_mtime).isoformat()),
                    'uploader_ip': uploader_ip,
                    'uploader_name': get_user_name(uploader_ip)
                })

    images.sort(key=lambda x: x['uploaded'], reverse=True)
    return images

def get_current_image():
    """Get the currently displayed image"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                return state.get('current_image')
        except:
            pass
    return None

def set_current_image(filename):
    """Set the currently displayed image"""
    state = {'current_image': filename, 'updated': datetime.now().isoformat()}
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/images')
def list_images():
    """API endpoint to list all uploaded images"""
    filter_user = request.args.get('user')  # Optional filter by user IP
    images = get_image_list(filter_user=filter_user)
    current = get_current_image()
    return jsonify({'images': images, 'current_image': current})

@app.route('/api/users')
def list_users():
    """API endpoint to list all unique uploaders"""
    users = get_all_users()
    # Count images per user
    metadata = load_metadata()
    user_counts = {}
    for img_data in metadata['images'].values():
        ip = img_data['uploader_ip']
        user_counts[ip] = user_counts.get(ip, 0) + 1

    users_with_counts = [{'ip': user['ip'], 'name': user['name'], 'image_count': user_counts.get(user['ip'], 0)} for user in users]
    return jsonify({'users': users_with_counts})

@app.route('/api/user/name', methods=['POST'])
def set_user_name_endpoint():
    """API endpoint to set a display name for the current user"""
    data = request.get_json()
    name = data.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    if len(name) > 50:
        return jsonify({'error': 'Name too long (max 50 characters)'}), 400

    # Get the user's IP
    user_ip = request.remote_addr
    if request.headers.get('X-Forwarded-For'):
        user_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()

    set_user_name(user_ip, name)

    return jsonify({'success': True, 'name': name, 'ip': user_ip})

@app.route('/api/server-info')
def server_info():
    """API endpoint to get server network information"""
    import socket
    import subprocess

    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "Unable to detect"

    # Get Tailscale IP
    try:
        result = subprocess.run(['tailscale', 'ip', '-4'], capture_output=True, text=True, timeout=2)
        tailscale_ip = result.stdout.strip() if result.returncode == 0 else "Not available"
    except:
        tailscale_ip = "Not available"

    return jsonify({
        'local_ip': local_ip,
        'tailscale_ip': tailscale_ip,
        'port': 5000
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API endpoint to handle image uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use PNG, JPG, GIF, or BMP'}), 400

    filename = secure_filename(file.filename)
    # Add timestamp to avoid conflicts
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    filename = f"{name}_{timestamp}{ext}"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Get uploader's IP address
    uploader_ip = request.remote_addr
    if request.headers.get('X-Forwarded-For'):
        # If behind a proxy, get the real IP
        uploader_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()

    # Store metadata
    add_image_metadata(filename, uploader_ip)

    return jsonify({
        'success': True,
        'filename': filename,
        'message': 'Image uploaded successfully',
        'uploader_ip': uploader_ip
    })

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_image(filename):
    """API endpoint to delete an image"""
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    try:
        os.remove(filepath)
        # Remove metadata
        remove_image_metadata(filename)
        # If this was the current image, clear it
        if get_current_image() == filename:
            set_current_image(None)
        return jsonify({'success': True, 'message': 'Image deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/display/<filename>', methods=['POST'])
def display_image(filename):
    """API endpoint to display an image on the e-paper"""
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    try:
        # Call the display script
        display_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'display_image.py')
        result = os.system(f'python3 "{display_script}" "{filepath}"')

        if result == 0:
            set_current_image(filename)
            return jsonify({'success': True, 'message': 'Image displayed on e-paper'})
        else:
            return jsonify({'error': 'Failed to display image'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Run on all interfaces so it's accessible from network
    app.run(host='0.0.0.0', port=5000, debug=False)
