# PDF Multimodal Search

This project implements a multimodal search engine for PDF documents. It processes PDFs, extracts both text and images from each page, generates multimodal embeddings (using CLIP), and stores them in a Qdrant vector database. Users can then perform searches using either a text query or an image query to find relevant pages within the indexed PDFs.

The project provides both a Command Line Interface (CLI) and a Web User Interface (Web UI) to interact with the search engine.

## Features

*   **PDF Processing:** Extracts text and converts each page into an image file.
*   **Multimodal Indexing:** Generates embeddings for both the text content and the image of each PDF page using the CLIP model.
*   **Vector Database Storage:** Stores the multimodal embeddings and page metadata in Qdrant.
*   **Text Search:** Query the indexed PDFs using natural language text.
*   **Image Search:** Query the indexed PDFs using an image.
*   **CLI Interface:** Perform upload and search operations from the command line.
*   **Web UI Interface:** A simple web application for uploading PDFs and performing searches via a browser.
*   **Search Results:** Displays relevant pages with text previews, image thumbnails, and similarity scores.
*   **Image Fullscreen View:** Click on result images in the Web UI to view them in fullscreen.

## Prerequisites

Before running the application, ensure you have the following installed:

1.  **Python 3.8+:** The application is written in Python.
2.  **Qdrant Vector Database:** The project uses Qdrant as the vector store. You need to have a Qdrant instance running and accessible. The default connection URL is `http://localhost:6333/`.
    *   Refer to the official Qdrant documentation for installation instructions (e.g., using Docker).
3.  **Poppler:** `pdf2image` (used by `pdf_processor.py`) requires the Poppler library.
    *   On Debian/Ubuntu: `sudo apt-get install -y libpoppler-cpp-dev`
    *   On Fedora: `sudo dnf install -y poppler-cpp-devel`
    *   On macOS (using Homebrew): `brew install poppler`
    *   On Windows: Install Poppler for Windows (e.g., via conda, or download pre-compiled binaries). Make sure the `bin` directory is in your system's PATH.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url> # Replace with the actual repo URL
    cd abhi268170-multimodalrag_with_llamaindex
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Make sure your Qdrant instance is running and accessible (default: `http://localhost:6333/`).

### Command Line Interface (CLI)

You can use `cli.py` to upload PDFs and perform searches directly from your terminal.

1.  **Upload and Index a PDF:**
    ```bash
    python cli.py upload /path/to/your/document.pdf
    ```
    This command will process the PDF, index its pages in Qdrant, and print the generated PDF ID.

2.  **Search by Text:**
    ```bash
    python cli.py search-text "Query text about something in the PDF" --limit 5
    ```
    This command searches the indexed pages using the provided text query and displays the top results.

3.  **Search by Image:**
    ```bash
    python cli.py search-image /path/to/your/query_image.jpg --limit 5
    ```
    This command searches the indexed pages using the provided image file and displays the top results.

### Web User Interface (Web UI)

The project includes a simple Flask web application.

1.  **Start the Flask application:**
    ```bash
    python app.py
    ```
    The application will typically run on `http://127.0.0.1:5000/`.

2.  **Open in Browser:** Navigate to `http://127.0.0.1:5000/` in your web browser.

3.  **Upload PDF:** Use the "Upload PDF" section to select a PDF file and click "Upload and Index". The UI will show a status message upon completion.

4.  **Search:** Use the "Search PDF" section.
    *   Switch between "Text Search" and "Image Search" tabs.
    *   Enter your query (text or select an image file).
    *   Adjust the result limit if needed.
    *   Click "Search".
    *   Results will appear below, showing page metadata, text preview, and the image thumbnail of the page. Click on an image thumbnail to view it in fullscreen.

## Project Structure
multimodalrag_with_llamaindex/
├── app.py # Flask web application
├── cli.py # Command line interface
├── clip_embedder.py # Handles generating CLIP embeddings
├── multimodal_search.py # Manages Qdrant interaction (indexing and searching)
├── pdf_processor.py # Handles PDF text extraction and image conversion
├── requirements.txt # Python dependencies
├── images/ # Directory to temporarily store PDF page images
├── static/
│ └── css/
│ └── style.css # CSS for the web UI
└── templates/
└── index.html # HTML for the web UI


## Dependencies

The project relies on the following key libraries, listed in `requirements.txt`:

*   `qdrant-client`: Python client for Qdrant.
*   `llama-index`, `llama-index-embeddings-huggingface`: Used for integrating Hugging Face embeddings (specifically CLIP via `transformers`).
*   `transformers`: Provides access to the CLIP model.
*   `pdf2image`: Converts PDF pages to images (requires Poppler).
*   `PyPDF2`: Extracts text from PDFs.
*   `pillow`: Image processing library (dependency of pdf2image).
*   `flask`: Web framework for the UI.
*   `tqdm`: Progress bars (used in pdf_processor).
*   `torch`, `numpy`: Tensor/numerical computation libraries for embeddings.

## Notes and Considerations

*   **Qdrant Collection Persistence:** Currently, the `MultimodalSearch` class is initialized in both `app.py` and `cli.py` and configured to *delete and recreate* the Qdrant collection (`pdf-search`) upon startup. This means any indexed data is **not persistent** across restarts of `app.py` or runs of `cli.py`. To make the index persistent, you would need to modify `_ensure_collection_exists` in `multimodal_search.py` to check if the collection exists and *not* delete it if it does.
*   **Image Storage:** Processed page images are stored locally in the `images/` directory. The `pdf_processor.py` currently clears this directory before processing a *new* PDF when called from `app.py`. This design choice might be temporary and limits the scalability and persistence of images across multiple PDFs or runs.
*   **Performance:** Processing PDFs and generating embeddings can be resource-intensive, especially for large documents or when running on a CPU. The `CLIPEmbedder` is initialized on `cpu` by default. You might gain performance by configuring it to use a GPU if available (`device="cuda"` or `device="mps"`).

## Future Improvements (Potential)

*   Add options for persistent storage of the Qdrant index and images.
*   Implement more robust error handling and logging.
*   Improve PDF processing, potentially adding OCR capabilities for image-only PDFs.
*   Allow searching across a collection of multiple *uploaded* PDFs within the Web UI.
*   Add configuration options for Qdrant URL, collection name, etc. (e.g., via environment variables).
*   Enhance the Web UI with pagination, sorting, and more detailed result information.
*   Explore other multimodal embedding models.
*   Implement a mechanism to delete specific indexed PDFs from Qdrant.