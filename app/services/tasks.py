import torch
from PIL import Image

import app.services.model_loader as ml
from app.celery_app import app


@app.task
def process_image_task(image_path: str) -> dict:
    raw_image = Image.open(image_path).convert("RGB")
    inputs = ml.processor(raw_image, return_tensors="pt").to(ml.device)

    with torch.no_grad():
        out = ml.model.generate(**inputs, max_new_tokens=50)

    caption = ml.processor.decode(out[0], skip_special_tokens=True)

    return {"caption": caption}
