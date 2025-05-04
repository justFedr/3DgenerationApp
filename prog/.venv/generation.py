import torch
from transformers import AutoModel
from PIL import Image
from preprocessor import LRMImageProcessor
import os

def generate_3d(path_to_image):
    
    def preprocess_image(path_to_image):
        processor = LRMImageProcessor()
        image = Image.open(path_to_image)

        image, source_camera = processor(image)
        return image, source_camera
    
    image, source_camera = preprocess_image(path_to_image)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = AutoModel.from_pretrained(os.path.abspath('./model/model_vfusion3d'), trust_remote_code=True)
    
    model.to(device)
    m = model(image, source_camera, export_mesh=True)
    model = None
