# FrameSync

A web-based photo frame server that can serve images to multiple displays on your local network. Originally designed for Waveshare 5.65" 7-color e-paper displays, it now supports any display device that can fetch images via HTTP API.

## Features

- 📱 Mobile-friendly web interface for uploading photos
- 👥 Multi-user support with IP-based user tracking
- 🔍 Filter images by user (all photos, my photos, or specific users)
- 📺 Multi-device support - serve images to any display via HTTP API
- 🔐 Per-image device permissions - control which displays can see each image
- 🔄 Automatic hourly image rotation (for e-paper displays)
- 🎨 Optimized image processing for 7-color e-paper displays
- 🌐 Accessible via local network or Tailscale
- 🚀 Auto-starts on boot via systemd

## Hardware Requirements

### Server
- Raspberry Pi (tested on Pi 4) or any Linux server

### Optional: E-Paper Display
- Waveshare 5.65" 7-Color E-Paper Display (600x448)
- Waveshare e-Paper library

### Or: Any Display Device
- Any device that can make HTTP requests and display images (tablets, smart displays, Raspberry Pi with LCD, etc.)

## Setup

### 1. (Optional) Install Waveshare e-Paper Library

Only required if using an e-paper display:

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

### Web Interface

1. Open the web interface on your phone or computer
2. Upload photos using the upload button
3. Manage which devices can see each image using the device assignment controls
4. For e-paper displays: Images will automatically rotate every hour
5. Manually display any image using the "Display" button (for e-paper)

### Multi-User Features

Each uploader is identified by their IP address:

- **Your IP Badge**: Shows your current IP address (appears after first upload)
- **Filter Options**:
  - **All Photos**: View all images from all users
  - **My Photos**: View only images you uploaded
  - **Specific User**: Filter by a specific user's IP address
- **Image Attribution**: Each image shows who uploaded it ("Your Photo" or "By [IP]")
- **User List**: The filter dropdown shows all users and their photo counts

Perfect for families or roommates sharing the same photo frame!

### Multi-Device API

Connect any display device to fetch images via the HTTP API. See [multi-device-instructions.md](multi-device-instructions.md) for detailed API documentation and integration examples.

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
- **Display dimensions** (e-paper only): 600x448 (hardcoded for Waveshare 5.65")
- **Rotation interval** (e-paper only): Edit `epaper-rotate.timer` (default: hourly)
- **Path to e-Paper library** (e-paper only): `/home/r2/e-Paper/RaspberryPi_JetsonNano/python/lib`

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
