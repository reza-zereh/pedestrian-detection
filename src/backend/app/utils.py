import io

import pooch
from PIL import Image
from ultralytics import YOLO
from ultralytics.yolo.engine.results import Results


def get_checkpoint_fp():
    """Download trained model checkpoint from remote.

    Returns:
        str: Local path to saved checkpoint.
    """
    url = (
        "https://github.com/ironcladgeek/pedestrian-detection/"
        "releases/download/v0.0.0/yolov8s_imgsz1024_mAP50_0.593.pt"
    )
    md5 = "79c93d519af453cef1a0ae2b1cd5a461"
    model_path = pooch.retrieve(
        url=url, known_hash=f"md5:{md5}", progressbar=True
    )
    return model_path


def get_detection_model() -> YOLO:
    """Get a YOLOv8 model loaded from saved checkpoint.

    Returns:
        YOLO: YOLOv8 model
    """
    model = YOLO(get_checkpoint_fp())
    return model


def get_image_from_bytes(binary_image, max_size=1024):
    """Create a in memory image from BytesIO and resize it.

    Args:
        binary_image (bytes): binary image file.
        max_size (int, optional): Output image size. Defaults to 1024.

    Returns:
        PIL.Image.Image: loaded image
    """
    input_image = Image.open(io.BytesIO(binary_image)).convert("RGB")
    width, height = input_image.size
    resize_factor = min(max_size / width, max_size / height)
    resized_image = input_image.resize(
        (
            int(input_image.width * resize_factor),
            int(input_image.height * resize_factor),
        )
    )
    return resized_image


def get_detection_results(results: Results) -> list[dict]:
    """Build a human readable list of detection results.

    Args:
        results (Results): YOLO detection results.

    Returns:
        list[dict]: List of dictionaries, where each dictionary contains 'cls', 'xyxyn', 'xywhn'
    """
    return [
        {
            "cls": str(results.names[cls]),
            "xyxyn": box.xyxyn.numpy().ravel().tolist(),
            "xywhn": box.xywhn.numpy().ravel().tolist(),
        }
        for box, cls in zip(results.boxes, results.boxes.cls.numpy())
    ]
