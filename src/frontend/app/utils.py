import io
import os
import time
from typing import NamedTuple

import cv2
import moviepy.editor as moviepy
import numpy as np
import requests
import streamlit as st
from PIL import Image

URL_DETECT_BOX_OUTPUT = "http://3.132.96.178:8000/api/v1/detect"
COLORS = [(206, 3, 252), (3, 252, 20)]


class Detection(NamedTuple):
    class_id: int
    label: str
    score: float
    box: np.ndarray


def draw_bboxes(image, detection_results, rgb=True):
    if type(image) != np.ndarray:
        img = cv2.imread(image)
    else:
        img = image.copy()
    h, w = img.shape[:2]

    # Convert the output array into a structured form
    detections = [
        Detection(
            class_id=int(detection["class_id"]),
            label=str(detection["label"]),
            score=float(detection["score"]),
            box=(detection["xyxyn"] * np.array([w, h, w, h])),
        )
        for detection in detection_results
    ]

    # Render bounding boxes and captions
    for detection in detections:
        caption = f"{detection.label}: {round(detection.score * 100, 2)}%"
        color = COLORS[detection.class_id]
        xmin, ymin, xmax, ymax = detection.box.astype("int")

        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(
            img,
            caption,
            (xmin, ymin - 15 if ymin - 15 > 15 else ymin + 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )
    if rgb:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def object_detection_image():
    uploaded_file = st.file_uploader(
        label="Image", type=["png", "jpg", "jpeg"]
    )
    if uploaded_file is not None:
        # store the uploaded image into disk
        fp = f"./{uploaded_file.name}"
        with open(fp, "wb") as f:
            f.write(uploaded_file.getvalue())
        response = requests.post(
            URL_DETECT_BOX_OUTPUT, files={"file": open(str(fp), "rb")}
        )
        if response.status_code == 200:
            results = response.json()["results"]
            image_with_bboxes = draw_bboxes(
                image=fp, detection_results=results
            )
            # show the output image
            st.image(image=image_with_bboxes, width=640)
        os.remove(fp)  # remove the uploaded image


def object_detection_video():
    uploaded_video = st.file_uploader(
        "Upload Video", type=["mp4", "mpeg", "mov"]
    )
    if uploaded_video is not None:
        with st.spinner("Detecting objects ... "):
            input_vid_fp = uploaded_video.name
            with open(input_vid_fp, mode="wb") as f:
                f.write(uploaded_video.read())  # save video to disk
            cap = cv2.VideoCapture(input_vid_fp)
            # Get the Default resolutions
            frame_width = int(cap.get(3))
            frame_height = int(cap.get(4))
            ret, frame = cap.read()

            intermediate_vid_fp = "detected_video.avi"
            out = cv2.VideoWriter(
                intermediate_vid_fp,
                cv2.VideoWriter_fourcc(*"MJPG"),
                30.0,
                (frame_width, frame_height),
            )
            count = 0
            while True:
                ret, frame = cap.read()
                if ret is False:
                    break
                h, w = frame.shape[:2]
                start = time.perf_counter()
                img_pil = Image.fromarray(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                )
                img_io_bytes = io.BytesIO()
                img_pil.save(img_io_bytes, "PNG")
                img_bytes = img_io_bytes.getvalue()
                response = requests.post(
                    URL_DETECT_BOX_OUTPUT, files={"file": img_bytes}
                )
                time_took = time.perf_counter() - start
                count += 1
                print(f"Time took: {count}", time_took)
                if response.status_code == 200:
                    results = response.json()["results"]
                    frame_with_bboxes = draw_bboxes(
                        image=frame, detection_results=results, rgb=False
                    )
                    out.write(frame_with_bboxes)
            cap.release()
            out.release()
            cv2.destroyAllWindows()
        with st.spinner("Preparing the output video ... "):
            # convert avi video to mp4 format
            start = time.perf_counter()
            clip = moviepy.VideoFileClip(intermediate_vid_fp)
            output_vid_fp = "./output_video.mp4"
            clip.write_videofile(output_vid_fp)
            time_took = time.perf_counter() - start
            print(f"Converting video took: {time_took}")

        os.remove(input_vid_fp)  # remove the uploaded video
        os.remove(intermediate_vid_fp)  # remove the avi intermediate video
        return output_vid_fp
