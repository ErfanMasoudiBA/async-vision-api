import torch
from celery.signals import worker_process_init
from transformers import BlipForConditionalGeneration, BlipProcessor

model = None
processor = None
device = "cuda" if torch.cuda.is_available() else "cpu"


@worker_process_init.connect
def init_model(**kwargs):
    global model, processor
    if model is None:
        print(f"Loading BLIP Model on {device}...")

        model_id = "Salesforce/blip-image-captioning-base"

        processor = BlipProcessor.from_pretrained(model_id)
        model = BlipForConditionalGeneration.from_pretrained(model_id)

        model.to(device)
        model.eval()

        print("BLIP Model loaded successfully!")
