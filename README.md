# Image Processing API

A Flask-based API for image processing tasks including background removal and image quality analysis.

## Features

- **Background Removal**: Remove backgrounds from images using AI
- **Image Quality Analysis**: 
  - Resolution scoring
  - Blur detection
  - Clarity assessment

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## API Endpoints

### GET /
Returns API documentation and available endpoints.

### POST /analyze
Analyze image quality including resolution and blur detection.

**Request**: Multipart form-data with 'image' file
**Response**: JSON with analysis results

Example response:
```json
{
  "resolution_score": 75.5,
  "is_blurry": false,
  "blur_score": 245.67,
  "clarity": "Clear",
  "filename": "example.jpg",
  "status": "success"
}
```

### POST /remove-background
Remove background from uploaded image.

**Request**: Multipart form-data with 'image' file
**Response**: PNG image file with transparent background

## Supported Image Formats
- PNG, JPG, JPEG, GIF, BMP, TIFF, WebP

## Usage Examples

### Using curl:

Analyze image:
```bash
curl -X POST -F "image=@your_image.jpg" http://localhost:5000/analyze
```

Remove background:
```bash
curl -X POST -F "image=@your_image.jpg" http://localhost:5000/remove-background -o result.png
```

### Using Python requests:
```python
import requests

# Analyze image
with open('image.jpg', 'rb') as f:
    response = requests.post('http://localhost:5000/analyze', 
                           files={'image': f})
    print(response.json())

# Remove background
with open('image.jpg', 'rb') as f:
    response = requests.post('http://localhost:5000/remove-background', 
                           files={'image': f})
    if response.status_code == 200:
        with open('output.png', 'wb') as out:
            out.write(response.content)
```

## Error Handling

The API handles various error cases:
- Invalid file types
- Corrupted or non-image files
- File size limits (16MB max)
- Processing failures

All errors return JSON responses with error descriptions.
