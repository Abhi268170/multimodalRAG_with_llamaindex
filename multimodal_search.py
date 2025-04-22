from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from qdrant_client import QdrantClient, models
import numpy as np
import os
from PIL import Image
from clip_embedder import CLIPEmbedder
import uuid

class MultimodalSearch:
    def __init__(self, collection_name="pdf-search", qdrant_url="http://localhost:6333/"):
        print("Initializing embedding model...")
        self.model = CLIPEmbedder(device="cpu")

        print(f"Connecting to Qdrant at {qdrant_url}...")
        self.client = QdrantClient(url=qdrant_url)

        self.collection_name = collection_name

        placeholder_path = os.path.join("images", "placeholder.jpg")
        if not os.path.exists(placeholder_path):
            if not os.path.exists("images"):
                os.makedirs("images")
            placeholder = Image.new('RGB', (100, 100), color = 'white')
            placeholder.save(placeholder_path)

        self._ensure_collection_exists(placeholder_path)

    def _ensure_collection_exists(self, placeholder_image_path):
        print(f"Attempting to manage collection: {self.collection_name}")

        try:
            sample_text_embedding = self.model.get_text_embedding("Sample text")
            sample_image_embedding = self.model.get_image_embedding(placeholder_image_path)

            text_vector_size = len(sample_text_embedding)
            image_vector_size = len(sample_image_embedding)

        except Exception as e:
             print(f"Error getting sample embeddings: {e}")
             print("Ensure CLIPEmbedder is initialized correctly and the model is loaded.")
             raise

        try:
            if self.client.collection_exists(self.collection_name):
                 print(f"Collection '{self.collection_name}' exists. Deleting...")
                 self.client.delete_collection(collection_name=self.collection_name)
                 print(f"Collection '{self.collection_name}' deleted successfully.")
            else:
                 print(f"Collection '{self.collection_name}' does not exist. No deletion needed.")
        except Exception as e:
             print(f"Warning: Could not delete collection '{self.collection_name}'. Error: {e}")

        print(f"Creating collection: {self.collection_name}")
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "text": models.VectorParams(
                    size=text_vector_size,
                    distance=models.Distance.COSINE
                ),
                "image": models.VectorParams(
                    size=image_vector_size,
                    distance=models.Distance.COSINE
                ),
            },
        )
        print("Collection created successfully!")

    def index_pdf_pages(self, pdf_pages, pdf_id):
        print(f"Indexing {len(pdf_pages)} pages from PDF {pdf_id}...")

        batch_size = 5
        for i in range(0, len(pdf_pages), batch_size):
            batch = pdf_pages[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(pdf_pages) + batch_size - 1)//batch_size}")

            text_contents = [page["text"] for page in batch]
            image_paths = [page["image_path"] for page in batch]

            try:
                text_embeddings = self.model.get_text_embedding_batch(text_contents)
                image_embeddings = self.model.get_image_embedding_batch(image_paths)
            except Exception as e:
                print(f"Error generating embeddings for batch starting at page {i}: {e}")
                continue

            points = []
            for j, page in enumerate(batch):
                point_id = str(uuid.uuid4())

                payload = {
                    "pdf_id": pdf_id,
                    "page_num": page["page_num"],
                    "text": page["text"][:1000] if len(page["text"]) > 1000 else page["text"],
                    "image_path": page["image_path"],
                }

                point = models.PointStruct(
                    id=point_id,
                    vector={
                        "text": text_embeddings[j].tolist(),
                        "image": image_embeddings[j].tolist(),
                    },
                    payload=payload,
                )

                points.append(point)

            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    wait=True,
                    points=points,
                )
            except Exception as e:
                print(f"Error upserting points for batch starting at page {i}: {e}")
                continue

        print(f"Successfully indexed {len(pdf_pages)} pages from PDF {pdf_id}")

    def search_by_text(self, query_text, limit=3, using="text"):
        print(f"Searching for: '{query_text}'")

        try:
            query_embedding = self.model.get_query_embedding(query_text)
        except Exception as e:
            print(f"Error generating query embedding for text: {e}")
            return []

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=(using, query_embedding.tolist()),
                limit=limit,
                with_payload=True,
            )
        except Exception as e:
             print(f"Error searching Qdrant by text: {e}")
             return []

        formatted_results = []
        for result in results:
            formatted_results.append({
                "pdf_id": result.payload.get("pdf_id"),
                "page_num": result.payload.get("page_num"),
                "text_preview": result.payload.get("text"),
                "image_path": result.payload.get("image_path"),
                "score": float(result.score),
            })

        return formatted_results

    def search_by_image(self, image_path, limit=3):
        print(f"Searching with image: {image_path}")

        try:
            image_embedding = self.model.get_image_embedding(image_path)
        except Exception as e:
             print(f"Error generating query embedding for image: {e}")
             return []

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=("image", image_embedding.tolist()),
                limit=limit,
                with_payload=True,
            )
        except Exception as e:
            print(f"Error searching Qdrant by image: {e}")
            return []

        formatted_results = []
        for result in results:
            formatted_results.append({
                "pdf_id": result.payload.get("pdf_id"),
                "page_num": result.payload.get("page_num"),
                "text_preview": result.payload.get("text"),
                "image_path": result.payload.get("image_path"),
                "score": float(result.score),
            })

        return formatted_results