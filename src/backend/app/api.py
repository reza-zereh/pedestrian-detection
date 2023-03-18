import time

from app import utils
from fastapi import APIRouter, File

router = APIRouter()

model = utils.get_detection_model()


@router.get("/health")
def get_health():
    return {"message": "OK"}


@router.post("/detect")
async def detect(file: bytes = File(...)):
    start = time.perf_counter()
    input_image = utils.get_image_from_bytes(binary_image=file)
    results = model.predict(input_image)
    detection_results = utils.get_detection_results(results=results[0])
    end = time.perf_counter()
    return {
        "results": detection_results,
        "inference_time": end - start,
    }
