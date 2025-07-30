from rembg import remove
from PIL import Image
import os

def remove_background(input_path: str, output_path: str):
    """
    Remove background from an image.
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output image
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        Exception: If processing fails
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    try:
        with open(input_path, 'rb') as i:
            input_bytes = i.read()
            output_bytes = remove(input_bytes)
            with open(output_path, 'wb') as o:
                o.write(output_bytes)
    except Exception as e:
        raise Exception(f"Failed to remove background: {str(e)}")