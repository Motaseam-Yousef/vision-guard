from flask import Flask, request, jsonify, send_file
import os
import tempfile
from werkzeug.utils import secure_filename
from PIL import Image
import traceback

from models.background_remover import remove_background
from models.image_analyzer import analyze_image_quality

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_image(file_path):
    """Validate that the file is actually an image."""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

@app.route('/')
def home():
    """API documentation endpoint."""
    return jsonify({
        "message": "Image Processing API",
        "endpoints": {
            "/analyze": "POST - Analyze image quality (resolution, blur detection)",
            "/remove-background": "POST - Remove background from image"
        },
        "usage": "Send image file as 'image' in form-data"
    })

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    Analyze image quality including resolution and blur detection.
    
    Expected: multipart/form-data with 'image' file
    Returns: JSON with analysis results
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file type. Allowed types: " + ", ".join(ALLOWED_EXTENSIONS)
            }), 400
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Validate it's actually an image
            if not is_valid_image(temp_path):
                return jsonify({"error": "File is not a valid image"}), 400
            
            # Analyze image quality
            results = analyze_image_quality(temp_path)
            
            # Add file info
            results["filename"] = secure_filename(file.filename)
            results["status"] = "success"
            
            return jsonify(results)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        return jsonify({
            "error": "Analysis failed",
            "details": str(e)
        }), 500

@app.route('/remove-background', methods=['POST'])
def remove_bg():
    """
    Remove background from uploaded image.
    
    Expected: multipart/form-data with 'image' file
    Returns: Processed image file or error
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file type. Allowed types: " + ", ".join(ALLOWED_EXTENSIONS)
            }), 400
        
        # Create temporary files
        input_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        
        try:
            # Save uploaded file
            file.save(input_temp.name)
            input_temp.close()
            
            # Validate it's actually an image
            if not is_valid_image(input_temp.name):
                return jsonify({"error": "File is not a valid image"}), 400
            
            # Remove background
            remove_background(input_temp.name, output_temp.name)
            output_temp.close()
            
            # Return processed image
            return send_file(
                output_temp.name,
                as_attachment=True,
                download_name=f"no_bg_{secure_filename(file.filename)}.png",
                mimetype='image/png'
            )
            
        finally:
            # Clean up temporary files
            if os.path.exists(input_temp.name):
                os.unlink(input_temp.name)
            # Note: output_temp will be cleaned up by Flask after sending
                
    except Exception as e:
        return jsonify({
            "error": "Background removal failed",
            "details": str(e)
        }), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("Starting Image Processing API...")
    print("Available endpoints:")
    print("  POST /analyze - Analyze image quality")
    print("  POST /remove-background - Remove image background")
    print("  GET / - API documentation")
    
    app.run(debug=True, host='0.0.0.0', port=5000)