# clip_embedder.py
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

class CLIPEmbedder:
    def __init__(self, device="cpu"):
        self.device = device
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def get_text_embedding(self, text):
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            return self.model.get_text_features(**inputs)[0].cpu().numpy()

    def get_image_embedding(self, image_path):
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            return self.model.get_image_features(**inputs)[0].cpu().numpy()

    def get_text_embedding_batch(self, texts):
        inputs = self.processor(text=texts, return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            return self.model.get_text_features(**inputs).cpu().numpy()

    def get_image_embedding_batch(self, image_paths):
        images = [Image.open(p).convert("RGB") for p in image_paths]
        inputs = self.processor(images=images, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            return self.model.get_image_features(**inputs).cpu().numpy()
    
    def get_query_embedding(self, text):
        return self.get_text_embedding(text)
