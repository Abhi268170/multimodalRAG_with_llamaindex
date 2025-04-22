from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from qdrant_client import QdrantClient, models
import numpy as np
import os
from PIL import Image
from clip_embedder import CLIPEmbedder


class MultimodalSearch:
    def __init__(self, collection_name="pdf-search", qdrant_url="http://localhost:6333/"):
        """Initialize embedding model and vector database."""
        # Initialize embedding model
        print("Initializing embedding model...")
        self.model = CLIPEmbedder(device="cpu")
        
        # Initialize Qdrant client
        print(f"Connecting to Qdrant at {qdrant_url}...")
        self.client = QdrantClient(url=qdrant_url)
        
        # Set collection name
        self.collection_name = collection_name
        
        # Create a placeholder image for initial vector sizing
        placeholder_path = os.path.join("images", "placeholder.jpg")
        if not os.path.exists(placeholder_path):
            if not os.path.exists("images"):
                os.makedirs("images")
            placeholder = Image.new('RGB', (100, 100), color = 'white')
            placeholder.save(placeholder_path)
        
        # Check if collection exists, create if not
        self._ensure_collection_exists(placeholder_path)
    
    def _ensure_collection_exists(self, placeholder_image_path):
        """Create the collection if it doesn't exist."""
        # First, check if we can get a sample embedding to determine vector size
        sample_text_embedding = self.model.get_text_embedding("Sample text")
        sample_image_embedding = self.model.get_image_embedding(placeholder_image_path)
        
        if not self.client.collection_exists(self.collection_name):
            print(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "text": models.VectorParams(
                        size=len(sample_text_embedding), 
                        distance=models.Distance.COSINE
                    ),
                    "image": models.VectorParams(
                        size=len(sample_image_embedding), 
                        distance=models.Distance.COSINE
                    ),
                },
            )
            print("Collection created successfully!")
        else:
            print(f"Collection {self.collection_name} already exists.")
    
    def index_pdf_pages(self, pdf_pages, pdf_id):
        """Index PDF pages with text and image embeddings."""
        print(f"Indexing {len(pdf_pages)} pages from PDF {pdf_id}...")
        
        # Process in batches
        batch_size = 5
        for i in range(0, len(pdf_pages), batch_size):
            batch = pdf_pages[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(pdf_pages) + batch_size - 1)//batch_size}")
            
            # Get text embeddings
            text_contents = [page["text"] for page in batch]
            text_embeddings = self.model.get_text_embedding_batch(text_contents)
            
            # Get image embeddings
            image_paths = [page["image_path"] for page in batch]
            image_embeddings = self.model.get_image_embedding_batch(image_paths)
            
            # Create points for Qdrant
            points = []
            for j, page in enumerate(batch):
                # Create a unique ID for this page: pdf_id_page_num
                point_id = f"{pdf_id}_{page['page_num']}"
                
                # Create payload with metadata
                payload = {
                    "pdf_id": pdf_id,
                    "page_num": page["page_num"],
                    "text": page["text"][:1000] if len(page["text"]) > 1000 else page["text"],  # Store a preview of text
                    "image_path": page["image_path"],
                }
                
                # Create point
                point = models.PointStruct(
                    id=point_id,
                    vector={
                        "text": text_embeddings[j].tolist(),
                        "image": image_embeddings[j].tolist(),
                    },
                    payload=payload,
                )
                
                points.append(point)
            
            # Upload points to Qdrant
            self.client.upsert_points(collection_name=self.collection_name, points=points)
            
        print(f"Successfully indexed {len(pdf_pages)} pages from PDF {pdf_id}")
    
    def search_by_text(self, query_text, limit=3, using="text"):
        """Search for PDF pages by text query."""
        print(f"Searching for: '{query_text}'")
        
        # Get query embedding
        query_embedding = self.model.get_query_embedding(query_text)
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=(using, query_embedding.tolist()),
            limit=limit,
            with_payload=True,
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "pdf_id": result.payload["pdf_id"],
                "page_num": result.payload["page_num"],
                "text_preview": result.payload["text"],
                "image_path": result.payload["image_path"],
                "score": float(result.score),
            })
        
        return formatted_results
    
    def search_by_image(self, image_path, limit=3):
        """Search for PDF pages by image."""
        print(f"Searching with image: {image_path}")
        
        # Get image embedding
        image_embedding = self.model.get_image_embedding(image_path)
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=("image", image_embedding.tolist()),
            limit=limit,
            with_payload=True,
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "pdf_id": result.payload["pdf_id"],
                "page_num": result.payload["page_num"],
                "text_preview": result.payload["text"],
                "image_path": result.payload["image_path"],
                "score": float(result.score),
            })
        
        return formatted_results