"""
Solar Panel Defect Detection - Web Application
AI-Powered Electroluminescence Image Analysis System

This is a self-contained deployable application that demonstrates
solar panel defect detection using pre-computed YOLO inference results.
"""
import os
import time
import random
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

# Initialize Flask app
app = Flask(__name__)

# Configuration - All paths relative to app directory
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
STATIC_DIR = BASE_DIR / 'static'
ORIGINAL_IMAGES_DIR = STATIC_DIR / 'images' / 'original'
RESULTS_IMAGES_DIR = STATIC_DIR / 'images' / 'results'
DETECTION_REPORT = DATA_DIR / 'detection_report.json'
SUMMARY_STATS_FILE = DATA_DIR / 'summary_statistics.json'

# Load detection data at startup
detection_data = {}
summary_stats = {}


def load_detection_data():
    """Load detection report and summary statistics from JSON files"""
    global detection_data, summary_stats

    if DETECTION_REPORT.exists():
        with open(DETECTION_REPORT, 'r') as f:
            detection_data = json.load(f)
        print(f"[INFO] Loaded detection data: {detection_data.get('metadata', {}).get('total_detected_objects', 0)} objects")

    if SUMMARY_STATS_FILE.exists():
        with open(SUMMARY_STATS_FILE, 'r') as f:
            summary_stats = json.load(f)
        print(f"[INFO] Loaded summary: {summary_stats.get('total_images', 0)} images, {summary_stats.get('total_detected_objects', 0)} defects")


def get_available_images():
    """Get list of images available for testing"""
    images = []
    if RESULTS_IMAGES_DIR.exists():
        images = [f.name for f in RESULTS_IMAGES_DIR.glob('*.jpg')]
    return sorted(images)


def get_image_detection_info(image_name):
    """Get detection information for a specific image from the JSON report"""
    if not detection_data:
        return None

    # Find all detected objects for this image
    detected_objects = []
    for obj in detection_data.get('detected_objects', []):
        if obj.get('source_image', {}).get('image_name') == image_name:
            detected_objects.append(obj)

    if not detected_objects:
        return {
            'detections_count': 0,
            'detected_objects': [],
            'damage_status': 'GOOD CONDITION',
            'coverage_percentage': 0,
            'total_defect_area': 0,
            'max_confidence': 0
        }

    # Calculate metrics
    total_defect_area = sum(
        obj['detection_details']['bounding_box']['dimensions']['area']
        for obj in detected_objects
    )

    # Get image dimensions from first detection
    img_dims = detected_objects[0]['source_image']['image_dimensions']
    image_area = img_dims['width'] * img_dims['height']
    coverage_percentage = (total_defect_area / image_area) * 100

    # Calculate damage status based on coverage percentage
    if coverage_percentage >= 15:
        damage_status = "FULLY DAMAGED"
    elif coverage_percentage >= 8:
        damage_status = "CRITICAL"
    elif coverage_percentage >= 2:
        damage_status = "NEEDS REPAIR"
    else:
        damage_status = "GOOD CONDITION"

    # Get max confidence score
    max_confidence = max(
        obj['detection_details']['confidence']
        for obj in detected_objects
    )

    return {
        'detections_count': len(detected_objects),
        'detected_objects': detected_objects,
        'damage_status': damage_status,
        'coverage_percentage': coverage_percentage,
        'total_defect_area': total_defect_area,
        'max_confidence': max_confidence,
        'image_dimensions': img_dims
    }


# Routes
@app.route('/')
def index():
    """Main page - Solar Panel Defect Detection Dashboard"""
    images = get_available_images()
    return render_template('index.html', images=images, summary_stats=summary_stats)


@app.route('/api/images')
def api_images():
    """API endpoint to get list of available images"""
    return jsonify({'images': get_available_images()})


@app.route('/api/summary')
def api_summary():
    """API endpoint to get summary statistics"""
    return jsonify(summary_stats)


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    API endpoint to analyze an image.
    Simulates AI processing time and returns pre-computed results.
    """
    data = request.get_json()
    image_name = data.get('image_name', '')

    if not image_name:
        return jsonify({'error': 'No image specified'}), 400

    # Check if result image exists
    result_path = RESULTS_IMAGES_DIR / image_name
    if not result_path.exists():
        return jsonify({'error': 'Result not found for this image'}), 404

    # Simulate AI processing time (5-8 seconds)
    delay = random.uniform(5, 8)
    time.sleep(delay)

    # Get detection info from pre-computed results
    detection_info = get_image_detection_info(image_name)

    if detection_info:
        return jsonify({
            'success': True,
            'image_name': image_name,
            'result_url': f'/results/{image_name}',
            'original_url': f'/original/{image_name}',
            'processing_time': round(delay, 2),
            'has_defects': detection_info['detections_count'] > 0,
            'defect_count': detection_info['detections_count'],
            'confidence': round(detection_info['max_confidence'], 4),
            'status': detection_info['damage_status'],
            'coverage_percentage': round(detection_info['coverage_percentage'], 2),
            'total_defect_area': round(detection_info['total_defect_area'], 2),
            'image_dimensions': detection_info.get('image_dimensions', {}),
            'detected_objects': detection_info['detected_objects'][:10]
        })
    else:
        return jsonify({
            'success': True,
            'image_name': image_name,
            'result_url': f'/results/{image_name}',
            'original_url': f'/original/{image_name}',
            'processing_time': round(delay, 2),
            'has_defects': False,
            'defect_count': 0,
            'confidence': 0,
            'status': 'GOOD CONDITION',
            'coverage_percentage': 0,
            'total_defect_area': 0
        })


@app.route('/results/<filename>')
def serve_result(filename):
    """Serve annotated result images"""
    return send_from_directory(RESULTS_IMAGES_DIR, filename)


@app.route('/original/<filename>')
def serve_original(filename):
    """Serve original grayscale images"""
    return send_from_directory(ORIGINAL_IMAGES_DIR, filename)


# Load data when app starts
load_detection_data()


if __name__ == '__main__':
    # Get port from environment variable (for cloud deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"[INFO] Starting Solar Panel Defect Detection App")
    print(f"[INFO] Data Directory: {DATA_DIR}")
    print(f"[INFO] Original Images: {ORIGINAL_IMAGES_DIR}")
    print(f"[INFO] Result Images: {RESULTS_IMAGES_DIR}")
    print(f"[INFO] Available Images: {len(get_available_images())}")
    print(f"[INFO] Running on port {port}")

    app.run(host='0.0.0.0', port=port, debug=debug)
