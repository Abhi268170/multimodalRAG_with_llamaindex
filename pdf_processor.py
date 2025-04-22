import os
import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
import uuid
import tempfile
from tqdm import tqdm
import shutil

class PDFProcessor:
    def __init__(self, pdf_dir="pdfs", image_dir="images", temp_dir="temp"):
        """Initialize directories for PDFs, images, and temporary files."""
        self.pdf_dir = pdf_dir
        self.image_dir = image_dir
        self.temp_dir = temp_dir
        
        # Ensure directories exist
        os.makedirs(pdf_dir, exist_ok=True)
        os.makedirs(image_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
    
    def save_uploaded_pdf(self, file_upload, filename=None):
        """Save an uploaded PDF file to the PDF directory."""
        if filename is None:
            filename = f"{uuid.uuid4()}.pdf"
        
        pdf_path = os.path.join(self.pdf_dir, filename)
        
        # If file_upload is a file-like object
        if hasattr(file_upload, 'read'):
            with open(pdf_path, 'wb') as f:
                f.write(file_upload.read())
        # If file_upload is a path
        else:
            shutil.copy(file_upload, pdf_path)
            
        return filename, pdf_path
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from each page of a PDF."""
        page_texts = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                page_texts.append({
                    "page_num": page_num + 1,  # 1-based page numbering
                    "text": text
                })
        
        return page_texts
    
    def convert_pdf_to_images(self, pdf_path, dpi=200):
        """Convert PDF pages to images."""
        # Generate a unique identifier for this PDF
        pdf_id = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Path to save images
        image_paths = []
        
        # Convert PDF to images
        with tempfile.TemporaryDirectory() as temp_path:
            images = convert_from_path(pdf_path, dpi=dpi, output_folder=temp_path)
            
            for i, image in enumerate(images):
                # Save the image
                image_filename = f"{pdf_id}_page_{i+1}.png"
                image_path = os.path.join(self.image_dir, image_filename)
                image.save(image_path, "PNG")
                
                image_paths.append({
                    "page_num": i + 1,  # 1-based page numbering
                    "image_path": image_path
                })
        
        return image_paths
    
    def process_pdf(self, pdf_path):
        """Process a PDF: extract text and convert to images."""
        print(f"Processing PDF: {pdf_path}")
        
        # Extract text from PDF
        print("Extracting text...")
        page_texts = self.extract_text_from_pdf(pdf_path)
        
        # Convert PDF to images
        print("Converting pages to images...")
        page_images = self.convert_pdf_to_images(pdf_path)
        
        # Combine text and image information
        pages = []
        for text_info, image_info in zip(page_texts, page_images):
            if text_info["page_num"] != image_info["page_num"]:
                print(f"Warning: Page number mismatch - Text: {text_info['page_num']}, Image: {image_info['page_num']}")
                continue
                
            pages.append({
                "page_num": text_info["page_num"],
                "text": text_info["text"],
                "image_path": image_info["image_path"]
            })
        
        return pages