import io
import logging
import queue
from typing import List, NamedTuple

import av
import cv2
import numpy as np
import requests
import streamlit as st
from PIL import Image
from streamlit_webrtc import WebRtcMode, webrtc_streamer

logger = logging.getLogger(__name__)


CLASSES = [
    "rider",
    "pedestrian",
]


class Detection(NamedTuple):
    class_id: int
    label: str
    score: float
    box: np.ndarray


@st.cache_resource
def generate_label_colors():
    return np.random.uniform(0, 255, size=(len(CLASSES), 3))


COLORS = generate_label_colors()


# NOTE: The callback will be called in another thread,
#       so use a queue here for thread-safety to pass the data
#       from inside to outside the callback.
result_queue: "queue.Queue[List[Detection]]" = queue.Queue()


def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format="bgr24")
    img_pil = Image.fromarray(image)
    img_io_bytes = io.BytesIO()
    img_pil.save(img_io_bytes, "PNG")
    img_bytes = img_io_bytes.getvalue()

    # Call inference API
    url = "http://3.132.96.178:8000/api/v1/detect"
    res = requests.post(url, files={"file": img_bytes})
    output = res.json()

    h, w = image.shape[:2]

    # Convert the output array into a structured form
    detections = [
        Detection(
            class_id=detection["class_id"],
            label=detection["label"],
            score=detection["score"],
            box=(detection["xyxyn"] * np.array([w, h, w, h])),
        )
        for detection in output
    ]

    # Render bounding boxes and captions
    for detection in detections:
        caption = f"{detection.label}: {round(detection.score * 100, 2)}%"
        color = COLORS[detection.class_id]
        xmin, ymin, xmax, ymax = detection.box.astype("int")

        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(
            image,
            caption,
            (xmin, ymin - 15 if ymin - 15 > 15 else ymin + 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
        )

    result_queue.put(detections)

    return av.VideoFrame.from_ndarray(image, format="bgr24")


webrtc_ctx = webrtc_streamer(
    key="object-detection",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration={
        # "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}],
        "iceServers": [{"urls": ["stun:stun.xten.com:3478"]}],
    },
    video_frame_callback=video_frame_callback,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

if st.checkbox("Show the detected labels", value=True):
    if webrtc_ctx.state.playing:
        labels_placeholder = st.empty()
        # NOTE: The video transformation with object detection and
        # this loop displaying the result labels are running
        # in different threads asynchronously.
        # Then the rendered video frames and the labels displayed here
        # are not strictly synchronized.
        while True:
            result = result_queue.get()
            labels_placeholder.table(result)
