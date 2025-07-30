import streamlit as st
import tempfile
import os
from PIL import Image
import traceback
from io import BytesIO
import numpy as np

# Try to import custom models with error handling
try:
    from models.background_remover import remove_background
    BACKGROUND_REMOVAL_AVAILABLE = True
except ImportError as e:
    st.error(f"Background removal module not available: {e}")
    BACKGROUND_REMOVAL_AVAILABLE = False
    
    def remove_background(input_path, output_path):
        """Fallback function when rembg is not available"""
        raise ImportError("Background removal dependencies not installed")

try:
    from models.image_analyzer import analyze_image_quality
    IMAGE_ANALYSIS_AVAILABLE = True
except ImportError as e:
    st.error(f"Image analysis module not available: {e}")
    IMAGE_ANALYSIS_AVAILABLE = False
    
    def analyze_image_quality(image_path):
        """Fallback function for basic image analysis using PIL only"""
        try:
            with Image.open(image_path) as img:
                # Basic analysis using PIL
                width, height = img.size
                file_size = os.path.getsize(image_path)
                
                # Convert to numpy array for basic analysis
                img_array = np.array(img.convert('L'))  # Convert to grayscale
                
                # Simple blur detection using Laplacian variance
                laplacian_var = np.var(img_array)
                
                return {
                    "width": width,
                    "height": height,
                    "file_size": file_size,
                    "format": img.format,
                    "mode": img.mode,
                    "blur_score": float(laplacian_var),
                    "blur_assessment": "Sharp" if laplacian_var > 100 else "Blurry" if laplacian_var < 50 else "Moderate",
                    "resolution_category": "High" if width * height > 1000000 else "Medium" if width * height > 300000 else "Low",
                    "aspect_ratio": round(width / height, 2),
                    "total_pixels": width * height
                }
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

# Page config
st.set_page_config(
    page_title="Image Processing App",
    page_icon="🖼️",
    layout="wide"
)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def is_valid_image_extension(filename):
    """Check if file has allowed extension."""
    if not filename:
        return False
    extension = filename.split('.')[-1].lower()
    return extension in ALLOWED_EXTENSIONS

def is_valid_image_file(uploaded_file):
    """Validate that the uploaded file is actually a valid image."""
    try:
        image = Image.open(uploaded_file)
        image.verify()
        return True
    except Exception:
        return False

def main():
    st.title("🖼️ Image Processing App")
    st.markdown("Upload an image to analyze its quality or remove its background.")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    option = st.sidebar.selectbox(
        "Choose an operation:",
        ["Home", "Image Analysis", "Background Removal"]
    )
    
    if option == "Home":
        show_home()
    elif option == "Image Analysis":
        show_image_analysis()
    elif option == "Background Removal":
        show_background_removal()

def show_home():
    """Display home page with app information."""
    st.header("Welcome to Image Processing App")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Image Analysis")
        st.write("""
        Analyze your images to get detailed information about:
        - Image resolution and dimensions
        - Blur detection and quality assessment
        - File size and format details
        """)
        
    with col2:
        st.subheader("✂️ Background Removal")
        st.write("""
        Remove backgrounds from your images:
        - Automatic background detection
        - Clean, transparent background removal
        - Download processed images instantly
        """)
    
    st.markdown("---")
    st.subheader("Supported Formats")
    st.write("PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP")
    st.write("Maximum file size: 16MB")

def show_image_analysis():
    """Display image analysis interface."""
    st.header("🔍 Image Quality Analysis")
    
    if not IMAGE_ANALYSIS_AVAILABLE:
        st.warning("⚠️ Advanced image analysis features are not available. Using basic analysis with PIL.")
    
    uploaded_file = st.file_uploader(
        "Choose an image file for analysis",
        type=list(ALLOWED_EXTENSIONS),
        help="Upload an image to analyze its quality, resolution, and other properties."
    )
    
    if uploaded_file is not None:
        # Validate file
        if not is_valid_image_extension(uploaded_file.name):
            st.error(f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
            return
        
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Original Image")
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=uploaded_file.name, use_column_width=True)
            except Exception as e:
                st.error("Error loading image. Please make sure it's a valid image file.")
                return
        
        with col2:
            st.subheader("Analysis Results")
            
            if st.button("Analyze Image", type="primary"):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Validate image file
                    if not is_valid_image_file(uploaded_file):
                        st.error("File is not a valid image.")
                        return
                    
                    # Reset file pointer again for processing
                    uploaded_file.seek(0)
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                        temp_file.write(uploaded_file.read())
                        temp_path = temp_file.name
                    
                    try:
                        # Analyze image
                        with st.spinner("Analyzing image..."):
                            results = analyze_image_quality(temp_path)
                        
                        # Display results
                        st.success("Analysis completed!")
                        
                        # Create metrics display
                        if 'width' in results and 'height' in results:
                            st.metric("Resolution", f"{results['width']} × {results['height']}")
                        
                        if 'file_size' in results:
                            file_size_mb = results['file_size'] / (1024 * 1024)
                            st.metric("File Size", f"{file_size_mb:.2f} MB")
                        
                        if 'blur_score' in results:
                            st.metric("Blur Score", f"{results['blur_score']:.2f}")
                        
                        # Display full results
                        st.subheader("Detailed Results")
                        st.json(results)
                        
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                            
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    st.error("Please check that your models are properly configured.")

def show_background_removal():
    """Display background removal interface."""
    st.header("✂️ Background Removal")
    
    if not BACKGROUND_REMOVAL_AVAILABLE:
        st.error("❌ Background removal is not available due to missing dependencies.")
        st.info("""
        **To enable background removal, you need to install the following dependencies:**
        
        ```bash
        pip install rembg opencv-python-headless
        ```
        
        **For Streamlit Cloud deployment, add these to your `requirements.txt`:**
        ```
        rembg
        opencv-python-headless
        ```
        
        **You may also need a `packages.txt` file with system dependencies:**
        ```
        libgl1-mesa-glx
        libglib2.0-0
        ```
        """)
        return
    
    uploaded_file = st.file_uploader(
        "Choose an image file for background removal",
        type=list(ALLOWED_EXTENSIONS),
        help="Upload an image to remove its background."
    )
    
    if uploaded_file is not None:
        # Validate file
        if not is_valid_image_extension(uploaded_file.name):
            st.error(f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
            return
        
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Original Image")
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=uploaded_file.name, use_column_width=True)
            except Exception as e:
                st.error("Error loading image. Please make sure it's a valid image file.")
                return
        
        with col2:
            st.subheader("Processed Image")
            
            if st.button("Remove Background", type="primary"):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Validate image file
                    if not is_valid_image_file(uploaded_file):
                        st.error("File is not a valid image.")
                        return
                    
                    # Reset file pointer again for processing
                    uploaded_file.seek(0)
                    
                    # Create temporary files
                    input_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    output_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    
                    try:
                        # Save uploaded file
                        input_temp.write(uploaded_file.read())
                        input_temp.close()
                        
                        # Process image
                        with st.spinner("Removing background..."):
                            remove_background(input_temp.name, output_temp.name)
                        
                        output_temp.close()
                        
                        # Display result
                        processed_image = Image.open(output_temp.name)
                        st.image(processed_image, caption="Background Removed", use_column_width=True)
                        
                        # Provide download button
                        with open(output_temp.name, "rb") as file:
                            btn = st.download_button(
                                label="📥 Download Processed Image",
                                data=file.read(),
                                file_name=f"no_bg_{uploaded_file.name.split('.')[0]}.png",
                                mime="image/png"
                            )
                        
                        st.success("Background removal completed!")
                        
                    finally:
                        # Clean up temporary files
                        if os.path.exists(input_temp.name):
                            os.unlink(input_temp.name)
                        if os.path.exists(output_temp.name):
                            os.unlink(output_temp.name)
                            
                except Exception as e:
                    st.error(f"Background removal failed: {str(e)}")
                    st.error("Please check that your models are properly configured.")
                    # Show detailed error for debugging
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()