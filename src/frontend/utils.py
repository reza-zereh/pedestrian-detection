import os

import requests
import streamlit as st

URL_DETECT_BOX_OUTPUT = "http://3.132.96.178:8000/api/v1/detect"


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
        print(response)
        if response.status_code == 200:
            results = response.json()["results"]
            st.image(image=fp, width=300)  # show the uploaded image
            st.json(results)  # show the predictions

        os.remove(fp)  # remove the uploaded image
