from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image
from io import BytesIO
import requests
import logging
import os
from flask import Blueprint, jsonify, current_app, request

from utils.app_utils import resolve_path
import random

logger = logging.getLogger(__name__)

class Gallery(BasePlugin):
    def generate_image(self, settings, device_config):
        img_index = settings.get("image_index", 0)

        folder = resolve_path(os.path.join("static", "images", "gallery"))
        if not folder or not os.path.isdir(folder):
            logger.error("Configured gallery folder not found")
            return None

        supported_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        image_locations = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in supported_exts
        ]

        if not image_locations:
            logger.error("No images found in gallery folder")
            return None

        img_index = self.select_new_index(img_index, len(image_locations))
        image_path = image_locations[img_index]

        try:
            image = Image.open(image_path)
        except Exception as e:
            logger.error(f"Error opening image: {str(e)}")
            return None

        settings['image_index'] = img_index
        return image
    
    def select_new_index(self, current_index, total_images):
        if total_images <= 1:
            return 0
        new_index = current_index
        while new_index == current_index:
            new_index = random.randint(0, total_images - 1)
        return new_index
    
gallery_bp = Blueprint('gallery_folder', __name__)

@gallery_bp.route('/gallery/image', methods=['GET'])
def list_images():
    folder = resolve_path(os.path.join("static", "images", "gallery"))
    if not folder or not os.path.isdir(folder):
        return jsonify({"error": "Configured folder not found"}), 400

    supported_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
    images = [
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in supported_exts
    ]
    return jsonify({"images": images})

@gallery_bp.route('/gallery/image/<filename>', methods=['GET'])
def get_image(filename):
    folder = resolve_path(os.path.join("static", "images", "gallery"))
    if not folder or not os.path.isdir(folder):
        return jsonify({"error": "Configured folder not found"}), 400

    file_path = os.path.join(folder, filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": "Image not found"}), 404

    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()
        return image_data, 200, {'Content-Type': 'image/jpeg'}  
    except Exception as e:
        logger.error(f"Error reading image file: {str(e)}")
        return jsonify({"error": "Failed to read image file"}), 500
    
@gallery_bp.route('/gallery/image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    folder = resolve_path(os.path.join("static", "images", "gallery"))
    if not os.path.exists(folder):
        os.makedirs(folder)

    file_path = os.path.join(folder, image_file.filename)
    try:
        image_file.save(file_path)
        return jsonify({"message": "Image uploaded successfully", "filename": image_file.filename}), 201
    except Exception as e:
        logger.error(f"Error saving image file: {str(e)}")
        return jsonify({"error": "Failed to save image file"}), 500
    
@gallery_bp.route('/gallery/image/<filename>', methods=['DELETE'])
def delete_image(filename):
    folder = resolve_path(os.path.join("static", "images", "gallery"))
    if not folder or not os.path.isdir(folder):
        return jsonify({"error": "Configured folder not found"}), 400

    file_path = os.path.join(folder, filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": "Image not found"}), 404

    try:
        os.remove(file_path)
        return jsonify({"message": "Image deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting image file: {str(e)}")
        return jsonify({"error": "Failed to delete image file"}), 500