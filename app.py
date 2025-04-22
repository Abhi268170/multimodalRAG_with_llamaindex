from flask import Flask, request, render_template, jsonify, send_file, url_for
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
from pdf_processor import PDFProcessor
from multimodal_search import MultimodalSearch

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize our PDF processor and search engine
pdf_processor = PDFProcessor()
search_engine = MultimodalSearch()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload and indexing."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        # Save file
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        file.save(temp_path)
        
        try:
            # Process PDF
            pdf_id = str(uuid.uuid4())
            pages = pdf_processor.process_pdf(temp_path)
            
            # Index pages in the search engine
            search_engine.index_pdf_pages(pages, pdf_id)
            
            return jsonify({
                'success': True,
                'message': 'PDF uploaded and indexed successfully.',
                'pdf_id': pdf_id,
                'num_pages': len(pages)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    return jsonify({'error': 'Invalid file format, please upload a PDF.'}), 400

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests."""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    query_type = data.get('query_type', 'text')
    limit = int(data.get('limit', 3))
    
    if query_type == 'text':
        query_text = data.get('query', '')
        if not query_text:
            return jsonify({'error': 'No query provided'}), 400
        
        results = search_engine.search_by_text(query_text, limit=limit)
        
    elif query_type == 'image':
        # If image search, we need a file upload
        return jsonify({'error': 'Image search not supported in this endpoint'}), 400
    
    else:
        return jsonify({'error': 'Invalid query type'}), 400
    
    # Update results with image URLs
    for result in results:
        if 'image_path' in result:
            result['image_url'] = url_for('get_image', image_path=result['image_path'])
    
    return jsonify({
        'success': True,
        'results': results
    })

@app.route('/search-image', methods=['POST'])
def search_image():
    """Handle image search requests."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        file.save(temp_path)
        
        try:
            # Search using the image
            limit = int(request.form.get('limit', 3))
            results = search_engine.search_by_image(temp_path, limit=limit)
            
            # Update results with image URLs
            for result in results:
                if 'image_path' in result:
                    result['image_url'] = url_for('get_image', image_path=result['image_path'])
            
            return jsonify({
                'success': True,
                'results': results
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/images/<path:image_path>')
def get_image(image_path):
    """Serve images."""
    return send_file(image_path)

if __name__ == '__main__':
    app.run(debug=True)