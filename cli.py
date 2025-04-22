import os
import argparse
from PIL import Image
import uuid
from pdf_processor import PDFProcessor
from multimodal_search import MultimodalSearch

class PDFSearchCLI:
    def __init__(self, qdrant_url="http://localhost:6333/"):
        """Initialize the PDF search application."""
        self.pdf_processor = PDFProcessor()
        self.search_engine = MultimodalSearch(qdrant_url=qdrant_url)
    
    def upload_and_index_pdf(self, pdf_path):
        """Upload a PDF file and index its contents."""
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"Error: File not found: {pdf_path}")
            return None
        
        # Generate a unique ID for this PDF
        pdf_id = str(uuid.uuid4())
        
        # Process PDF
        pages = self.pdf_processor.process_pdf(pdf_path)
        
        # Index pages in the search engine
        self.search_engine.index_pdf_pages(pages, pdf_id)
        
        return pdf_id
    
    def search_pdf_by_text(self, query_text, limit=3):
        """Search for PDF pages by text query."""
        # Search using text embedding
        results = self.search_engine.search_by_text(query_text, limit=limit)
        
        return results
    
    def search_pdf_by_image(self, image_path, limit=3):
        """Search for PDF pages by image."""
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"Error: Image not found: {image_path}")
            return None
        
        # Search using image embedding
        results = self.search_engine.search_by_image(image_path, limit=limit)
        
        return results
    
    def display_results(self, results):
        """Display search results."""
        if not results:
            print("No results found.")
            return
        
        print(f"\nFound {len(results)} results:")
        print("-" * 50)
        
        for i, result in enumerate(results):
            print(f"Result {i+1} (Score: {result['score']:.4f}):")
            print(f"  PDF ID: {result['pdf_id']}")
            print(f"  Page Number: {result['page_num']}")
            print(f"  Text Preview: {result['text_preview'][:100]}...")
            print(f"  Image Path: {result['image_path']}")
            print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="PDF Multimodal Search")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Upload parser
    upload_parser = subparsers.add_parser("upload", help="Upload and index a PDF")
    upload_parser.add_argument("pdf_path", help="Path to the PDF file")
    
    # Text search parser
    text_search_parser = subparsers.add_parser("search-text", help="Search PDF by text")
    text_search_parser.add_argument("query", help="Text query to search for")
    text_search_parser.add_argument("--limit", type=int, default=3, help="Maximum number of results")
    
    # Image search parser
    image_search_parser = subparsers.add_parser("search-image", help="Search PDF by image")
    image_search_parser.add_argument("image_path", help="Path to the image file")
    image_search_parser.add_argument("--limit", type=int, default=3, help="Maximum number of results")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize app
    app = PDFSearchCLI()
    
    # Execute command
    if args.command == "upload":
        pdf_id = app.upload_and_index_pdf(args.pdf_path)
        if pdf_id:
            print(f"PDF uploaded and indexed successfully. PDF ID: {pdf_id}")
    
    elif args.command == "search-text":
        results = app.search_pdf_by_text(args.query, args.limit)
        app.display_results(results)
    
    elif args.command == "search-image":
        results = app.search_pdf_by_image(args.image_path, args.limit)
        app.display_results(results)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()