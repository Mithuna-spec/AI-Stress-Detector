import cv2
import numpy as np
import time
from scipy.signal import find_peaks


def run_breath_detection(duration=15):

    cap = cv2.VideoCapture(0)
    time.sleep(2)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    print("Detecting face...")

    face_box = None

    face_detection_start = time.time()
    
    # Detect face once (with timeout)
    while face_box is None:
        if time.time() - face_detection_start > 10:
            print("Timeout: No face detected.")
            cap.release()
            cv2.destroyAllWindows()
            return 0, "No face detected", []

        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            face_box = faces[0]
            print("Face detected. Starting breathing measurement...")

        cv2.imshow("Breathing Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            cap.release()
            cv2.destroyAllWindows()
            return 0, "Cancelled", []

    x, y, w, h = face_box

    # Define chest ROI once
    chest_y1 = y + h
    chest_y2 = chest_y1 + int(h * 1.5)
    chest_x1 = x
    chest_x2 = x + w

    frame_h, frame_w = frame.shape[:2]
    chest_y2 = min(chest_y2, frame_h - 1)
    chest_x2 = min(chest_x2, frame_w - 1)

    motion_signal = []
    prev_roi = None

    start_time = time.time()

    while time.time() - start_time < duration:

        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        roi = gray[chest_y1:chest_y2, chest_x1:chest_x2]

        if roi.size == 0:
            continue

        roi = cv2.resize(roi, (150, 150))
        roi = cv2.GaussianBlur(roi, (5, 5), 0)

        if prev_roi is not None:
            diff = cv2.absdiff(prev_roi, roi)
            motion_value = np.mean(diff)
            motion_signal.append(motion_value)

        prev_roi = roi

        cv2.rectangle(frame,
                      (chest_x1, chest_y1),
                      (chest_x2, chest_y2),
                      (0, 255, 0), 2)

        cv2.imshow("Breathing Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(motion_signal) < 10:
        return 0, "Not enough data", []

    motion_signal = np.array(motion_signal)

    # Smooth
    motion_signal = np.convolve(
        motion_signal,
        np.ones(10) / 10,  # Less aggressive smoothing
        mode='same'
    )

    # Normalize
    motion_signal = (
        motion_signal - np.mean(motion_signal)
    ) / (np.std(motion_signal) + 1e-6)

    # Sensitivity: Lower prominence and distance
    peaks, _ = find_peaks(
        motion_signal,
        distance=25,      # Allow faster breathing (up to ~70 bpm)
        prominence=0.15   # Very sensitive to small chest movements
    )

    breaths = len(peaks)
    breaths_per_min = round((breaths / duration) * 60, 2)

    # Sanity check for "human" limits (4-60 bpm). 
    # If < 4, it might be holding breath or error.
    # But let's return whatever we find to be "responsive".
    
    status = "Normal Breathing"
    if breaths_per_min < 10:
        status = "Slow / Calm"
    elif breaths_per_min > 20:
        status = "Fast / Stressed"

    # Return the raw signal for the UI graph
    # Convert numpy array to list for JSON serialization
    return breaths_per_min, status, motion_signal.tolist()
