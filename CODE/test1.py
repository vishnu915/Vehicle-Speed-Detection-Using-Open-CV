import cv2
import time
import math
import streamlit as st
import numpy as np
import os
import tempfile

# Constants
WIDTH = 1280
HEIGHT = 720
FPS = 15
RECTANGLE_COLOR = (0, 0, 150)
IOU_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4
MIN_DISTANCE = 50

def calculate_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area > 0 else 0

def calculate_distance(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    center1 = (x1 + w1 / 2, y1 + h1 / 2)
    center2 = (x2 + w2 / 2, y2 + h2 / 2)
    return math.sqrt((center2[0] - center1[0]) ** 2 + (center2[1] - center1[1]) ** 2)

def estimateSpeed(location1, location2):
    d_pixels = math.sqrt((location2[0] - location1[0]) ** 2 + (location2[1] - location1[1]) ** 2)
    ppm = 8.8
    d_meters = d_pixels / ppm
    speed = d_meters * FPS * 3.6
    return speed

def process_video(video_path, cascade_path, status_placeholder, progress_bar, debug_placeholder):
    if not os.path.exists(video_path):
        st.error(f"Video file {video_path} not found.")
        return
    if not os.path.exists(cascade_path):
        st.error(f"Cascade file {cascade_path} not found.")
        return

    carCascade = cv2.CascadeClassifier(cascade_path)
    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        st.error("Error opening video file.")
        return

    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frameCounter = 0
    currentCarID = 0
    carTracker = {}
    carLocation1 = {}
    carLocation2 = {}
    speed = [None] * 1000

    frame_placeholder = st.empty()

    while 'running' in st.session_state and st.session_state.running:
        start_time = time.time()
        rc, image = video.read()
        if not rc:
            status_placeholder.write("Video ended.")
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frameCounter = 0
            carTracker.clear()
            carLocation1.clear()
            carLocation2.clear()
            speed = [None] * 1000
            currentCarID = 0
            progress_bar.progress(0.0)
            continue

        image = cv2.resize(image, (WIDTH, HEIGHT))
        resultImage = image.copy()
        frameCounter += 1
        progress = frameCounter / total_frames if total_frames > 0 else 0
        progress_bar.progress(min(progress, 1.0))

        # Remove failed trackers
        carIDtoDelete = []
        for carID in carTracker.keys():
            success, bbox = carTracker[carID].update(image)
            if not success:
                carIDtoDelete.append(carID)

        for carID in carIDtoDelete:
            carTracker.pop(carID, None)
            carLocation1.pop(carID, None)
            carLocation2.pop(carID, None)

        # Detect vehicles every 10 frames
        if not (frameCounter % 10):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cars = carCascade.detectMultiScale(gray, 1.05, 15, minSize=(24, 24), maxSize=(100, 100))
            
            if len(cars) > 0:
                boxes = [(x, y, w, h) for x, y, w, h in cars]
                scores = [(w * h) / (WIDTH * HEIGHT) for _, _, w, h in cars]
                boxes_np = np.array([[x, y, x + w, y + h] for x, y, w, h in boxes], dtype=np.float32)
                scores_np = np.array(scores, dtype=np.float32)
                indices = cv2.dnn.NMSBoxes(boxes_np.tolist(), scores_np.tolist(), 0.1, NMS_THRESHOLD)

                # SAFE handling of NMS output
                if isinstance(indices, tuple) or indices is None or len(indices) == 0:
                    indices = []
                elif isinstance(indices, np.ndarray):
                    indices = indices.flatten().tolist()
                else:
                    indices = list(indices)

                cars = [boxes[i] for i in indices] if indices else []
                debug_placeholder.write(f"Frame {frameCounter}: {len(cars)} detections after NMS")

            for (x, y, w, h) in cars:
                new_box = [x, y, w, h]
                matchCarID = None

                for carID in carTracker.keys():
                    success, bbox = carTracker[carID].update(image)
                    if success:
                        t_x, t_y, t_w, t_h = map(int, bbox)
                        tracked_box = [t_x, t_y, t_w, t_h]
                        iou = calculate_iou(new_box, tracked_box)
                        distance = calculate_distance(new_box, tracked_box)
                        if iou > IOU_THRESHOLD or (iou > 0.3 and distance < MIN_DISTANCE):
                            matchCarID = carID
                            break

                if matchCarID is None:
                    tracker = cv2.TrackerCSRT_create()
                    tracker.init(image, (x, y, w, h))
                    carTracker[currentCarID] = tracker
                    carLocation1[currentCarID] = [x, y, w, h]
                    currentCarID += 1

        cv2.line(resultImage, (0, 480), (1280, 480), (255, 0, 0), 5)

        for carID in carTracker.keys():
            success, bbox = carTracker[carID].update(image)
            if success:
                t_x, t_y, t_w, t_h = map(int, bbox)
                cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), RECTANGLE_COLOR, 4)
                carLocation2[carID] = [t_x, t_y, t_w, t_h]

        debug_placeholder.write(f"Frame {frameCounter}: {len(carTracker)} active trackers")

        end_time = time.time()
        if end_time != start_time:
            fps = 1.0 / (end_time - start_time)
            cv2.putText(resultImage, f'FPS: {int(fps)}', (620, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        for i in carLocation1.keys():
            if frameCounter % 1 == 0 and i in carLocation2:
                [x1, y1, w1, h1] = carLocation1[i]
                [x2, y2, w2, h2] = carLocation2[i]
                carLocation1[i] = [x2, y2, w2, h2]
                if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                    if (speed[i] is None or speed[i] == 0) and 275 <= y1 <= 285:
                        speed[i] = estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2])
                    if speed[i] is not None and y1 >= 180:
                        cv2.putText(resultImage, f"{int(speed[i])} km/hr", (int(x1 + w1/2), int(y1-5)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.80, (0, 255, 0), 2)

        resultImage = cv2.cvtColor(resultImage, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(resultImage, caption="Processed Video Frame", use_container_width=True)
        status_placeholder.write(f"Processing frame {frameCounter}/{total_frames}")

    video.release()

def main():
    st.title("Vehicle Tracking with Speed Estimation")
    st.write("Upload a video and use Haar + CSRT to track and estimate vehicle speed.")

    if 'running' not in st.session_state:
        st.session_state.running = False

    video_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])
    cascade_path = 'myhaar.xml'

    status_placeholder = st.empty()
    progress_bar = st.progress(0.0)
    debug_placeholder = st.empty()

    if st.button("Start/Stop Video Processing", disabled=not video_file):
        st.session_state.running = not st.session_state.running
        if not st.session_state.running:
            status_placeholder.write("Stopped.")
            progress_bar.progress(0.0)
            debug_placeholder.empty()

    if st.session_state.running and video_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(video_file.read())
            video_path = tmp_file.name

        process_video(video_path, cascade_path, status_placeholder, progress_bar, debug_placeholder)
        os.unlink(video_path)
    else:
        status_placeholder.write("Upload a video and press the button to start.")

if __name__ == "__main__":
    main()
