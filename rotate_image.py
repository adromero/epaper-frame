#!/usr/bin/env python3
import os
import sys
import json
import random
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
STATE_FILE = os.path.join(BASE_DIR, 'state.json')
DISPLAY_SCRIPT = os.path.join(BASE_DIR, 'display_image.py')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_image():
    """Get the currently displayed image from state file"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                return state.get('current_image')
        except:
            pass
    return None

def set_current_image(filename):
    """Save the currently displayed image to state file"""
    state = {
        'current_image': filename,
        'updated': datetime.now().isoformat()
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_all_images():
    """Get list of all uploaded images"""
    images = []
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                images.append(filename)
    return sorted(images)

def get_next_image():
    """Get the next image to display (random selection excluding current)"""
    all_images = get_all_images()

    if not all_images:
        logger.info("No images available to display")
        return None

    if len(all_images) == 1:
        logger.info("Only one image available")
        return all_images[0]

    current = get_current_image()

    # Filter out current image to avoid showing the same one
    available = [img for img in all_images if img != current]

    if not available:
        available = all_images

    # Pick a random image
    next_image = random.choice(available)
    logger.info(f"Selected next image: {next_image}")
    return next_image

def rotate_image():
    """Rotate to the next image and display it"""
    try:
        next_image = get_next_image()

        if not next_image:
            logger.warning("No images to display")
            return 1

        image_path = os.path.join(UPLOAD_FOLDER, next_image)

        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return 1

        logger.info(f"Displaying: {next_image}")

        # Call the display script
        result = os.system(f'python3 "{DISPLAY_SCRIPT}" "{image_path}"')

        if result == 0:
            set_current_image(next_image)
            logger.info("Image rotation successful")
            return 0
        else:
            logger.error("Failed to display image")
            return 1

    except Exception as e:
        logger.error(f"Error during rotation: {str(e)}")
        return 1

if __name__ == '__main__':
    exit_code = rotate_image()
    sys.exit(exit_code)
