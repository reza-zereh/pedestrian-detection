from functools import lru_cache
from PIL import Image
import io
import pooch
from ultralytics import YOLO


def get_checkpoint_fp():
    url = (
        "https://github.com/ironcladgeek/pedestrian-detection/"
        "releases/download/v0.0.0/yolov8s_imgsz1024_mAP50_0.593.pt"
    )
    md5 = "79c93d519af453cef1a0ae2b1cd5a461"
    model_path = pooch.retrieve(
        url=url, known_hash=f"md5:{md5}", progressbar=True
    )
    return model_path


@lru_cache(maxsize=10)
def get_detection_model():
    model = YOLO(get_checkpoint_fp())
    return model


def get_image_from_bytes(binary_image, max_size=1024):
    input_image =Image.open(io.BytesIO(binary_image)).convert("RGB")
    width, height = input_image.size
    resize_factor = min(max_size / width, max_size / height)
    resized_image = input_image.resize((
        int(input_image.width * resize_factor),
        int(input_image.height * resize_factor)
    ))
    return resized_image
