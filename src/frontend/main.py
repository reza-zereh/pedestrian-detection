import streamlit as st
import utils


def main():
    new_title = '<p style="font-size: 42px;">Pedestrian Detection App!</p>'
    read_me_0 = st.markdown(new_title, unsafe_allow_html=True)

    read_me = st.markdown(
        """
        This demo was built using Streamlit and OpenCV
        to demonstrate pedestrian detection in images and
        videos (pre-recorded or webcam)."""
    )
    st.sidebar.title("Select Activity")
    choice = st.sidebar.selectbox(
        "MODE",
        (
            "About",
            "Pedestrian Detection (Image)",
            "Pedestrian Detection (Video)",
            "Pedestrian Detection (Webcam)",
        ),
    )

    if choice == "About":
        print()
    else:
        read_me_0.empty()
        read_me.empty()
        title_placeholder = st.empty()
        if choice == "Pedestrian Detection (Image)":
            title_placeholder.title("Pedestrian detection in images")
            utils.object_detection_image()
        elif choice == "Pedestrian Detection (Video)":
            title_placeholder.title(
                "Pedestrian detection in pre-recorded videos"
            )
            # object_detection_video.has_beenCalled = False
            # object_detection_video()
            # if object_detection_video.has_beenCalled:
            # try:
            #     clip = moviepy.VideoFileClip("detected_video.mp4")
            #     clip.write_videofile("myvideo.mp4")
            #     st_video = open("myvideo.mp4", "rb")
            #     video_bytes = st_video.read()
            #     st.video(video_bytes)
            #     st.write("Detected Video")
            # except OSError:
            #     """"""
        elif choice == "Pedestrian Detection (Webcam)":
            title_placeholder.title(
                "Pedestrian detection in webcam video stream"
            )
            st.markdown(
                """**NotImplementedError**: This functionality will be
                implemented in the near future using WebRTC"""
            )


if __name__ == "__main__":
    main()
