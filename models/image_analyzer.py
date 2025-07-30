import cv2
from PIL import Image
import os
import numpy as np

def resolution_score(image_path: str) -> float:
    """
    Calculate resolution score based on image dimensions.
    
    Args:
        image_path (str): Path to image file
    
    Returns:
        float: Resolution score (0-100, where 100 is reference 256x256)
    
    Raises:
        FileNotFoundError: If image file doesn't exist
        Exception: If image cannot be processed
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            total_pixels = width * height
            reference_pixels = 256 * 256  # 1K resolution baseline
            score = min((total_pixels / reference_pixels) * 100, 100)
            return round(float(score), 2)  # Ensure it's a Python float
    except Exception as e:
        raise Exception(f"Failed to analyze resolution: {str(e)}")

def is_blurry(image_path: str, threshold: float = 100.0) -> bool:
    """
    Check if image is blurry based on Laplacian variance.
    
    Args:
        image_path (str): Path to image file
        threshold (float): Blur threshold (default: 100.0)
    
    Returns:
        bool: True if image is blurry, False if clear
    
    Raises:
        FileNotFoundError: If image file doesn't exist
        Exception: If image cannot be processed
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise Exception("Could not read image file - may not be a valid image")
        
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        # Convert numpy bool to Python bool for JSON serialization
        return bool(laplacian_var < threshold)  # lower → blurrier
    except Exception as e:
        raise Exception(f"Failed to analyze blur: {str(e)}")

def blur_score(image_path: str) -> float:
    """
    Get Laplacian variance score (higher values indicate sharper images).
    
    Args:
        image_path (str): Path to image file
    
    Returns:
        float: Blur score (higher is sharper)
    
    Raises:
        FileNotFoundError: If image file doesn't exist
        Exception: If image cannot be processed
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise Exception("Could not read image file - may not be a valid image")
        
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        # Ensure it's a Python float, not numpy float
        return round(float(laplacian_var), 2)
    except Exception as e:
        raise Exception(f"Failed to calculate blur score: {str(e)}")

def analyze_image_quality(image_path: str) -> dict:
    """
    Comprehensive image quality analysis.
    
    Args:
        image_path (str): Path to image file
    
    Returns:
        dict: Analysis results containing resolution score, blur status, and blur score
    """
    try:
        # Validate that it's actually an image file
        with Image.open(image_path) as img:
            img.verify()  # Verify it's a valid image
        
        # Get blur status
        is_image_blurry = is_blurry(image_path)
        
        results = {
            "resolution_score": resolution_score(image_path),
            "is_blurry": is_image_blurry,
            "blur_score": blur_score(image_path),
            "clarity": "Clear" if not is_image_blurry else "Blurry"
        }
        
        return results
    except Exception as e:
        raise Exception(f"Image quality analysis failed: {str(e)}")