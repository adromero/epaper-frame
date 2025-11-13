# E-Paper Photo Frame

A web-based photo frame for Waveshare 5.65" 7-color e-paper display (600x448) running on Raspberry Pi.

## Features

- 📱 Mobile-friendly web interface for uploading photos
- 👥 Multi-user support with IP-based user tracking
- 🔍 Filter images by user (all photos, my photos, or specific users)
- 🔄 Automatic hourly image rotation
- 🎨 Optimized for 7-color e-paper display
- 🌐 Accessible via local network or Tailscale
- 🚀 Auto-starts on boot via systemd

## Hardware Requirements

- Raspberry Pi (tested on Pi 4)
- Waveshare 5.65" 7-Color E-Paper Display (600x448)
- Waveshare e-Paper library

## Setup

### 1. Install Waveshare e-Paper Library

```bash
cd ~
git clone https://github.com/waveshare/e-Paper
```

### 2. Install Python Dependencies

```bash
cd ~/epaper-frame
pip3 install -r requirements.txt
```

### 3. Install Systemd Services

```bash
sudo cp epaper-frame.service /etc/systemd/system/
sudo cp epaper-rotate.service /etc/systemd/system/
sudo cp epaper-rotate.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable epaper-frame.service
sudo systemctl enable epaper-rotate.timer
sudo systemctl start epaper-frame.service
sudo systemctl start epaper-rotate.timer
```

### 4. Access the Web Interface

The server runs on port 5000:
- **Local network**: `http://<raspberry-pi-ip>:5000`
- **Tailscale**: `http://<tailscale-ip>:5000`

## Usage

### Basic Usage

1. Open the web interface on your phone or computer
2. Upload photos using the upload button
3. Images will automatically rotate every hour
4. Manually switch to any image using the "Display" button

### Multi-User Features

Each device is identified by its IP address:

- **Your IP Badge**: Shows your current IP address (appears after first upload)
- **Filter Options**:
  - **All Photos**: View all images from all users
  - **My Photos**: View only images you uploaded
  - **Specific User**: Filter by a specific user's IP address
- **Image Attribution**: Each image shows who uploaded it ("Your Photo" or "By [IP]")
- **User List**: The filter dropdown shows all users and their photo counts

Perfect for families or roommates sharing the same photo frame!

## File Structure

```
epaper-frame/
├── server.py              # Flask web server with multi-user support
├── display_image.py       # Display image on e-paper
├── rotate_image.py        # Hourly rotation logic
├── metadata.json          # User/image metadata (gitignored)
├── templates/
│   └── index.html        # Web interface with user filtering
├── static/               # Static assets (CSS/JS inline)
├── uploads/              # Uploaded images (gitignored)
├── epaper-frame.service  # Systemd service for web server
├── epaper-rotate.service # Systemd service for rotation
└── epaper-rotate.timer   # Systemd timer (runs hourly)
```

## Configuration

Edit these variables in the Python files if needed:

- **Port**: Change `PORT` in `server.py` (default: 5000)
- **Display dimensions**: 600x448 (hardcoded for Waveshare 5.65")
- **Rotation interval**: Edit `epaper-rotate.timer` (default: hourly)
- **Path to e-Paper library**: `/home/r2/e-Paper/RaspberryPi_JetsonNano/python/lib`

## Troubleshooting

### Check Service Status
```bash
sudo systemctl status epaper-frame.service
sudo systemctl status epaper-rotate.timer
```

### View Logs
```bash
journalctl -u epaper-frame.service -f
journalctl -u epaper-rotate.service -f
```

### Manual Image Display
```bash
python3 display_image.py /path/to/image.jpg
```

### Manual Rotation Test
```bash
python3 rotate_image.py
```

## License

MIT License - Feel free to modify and use for your own projects.
