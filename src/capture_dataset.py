import cv2
import os
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time


print("🚀 Landmark Dataset Capture Started")

# -----------------------
# MODEL
# -----------------------
MODEL_PATH = "hand_landmarker.task"

# -----------------------
# DATASET FOLDER
# -----------------------
DATASET_FOLDER = "handsigns"
os.makedirs(DATASET_FOLDER, exist_ok=True)

# -----------------------
# ASK LETTER AND SAMPLES
# -----------------------
letter = input("Enter ASL letter (A-Z): ").upper()
target_samples = int(input("How many samples do you want to collect?: "))

letter_folder = os.path.join(DATASET_FOLDER, letter)
os.makedirs(letter_folder, exist_ok=True)

# -----------------------
# MEDIAPIPE LANDMARKER
# -----------------------
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1
)

landmarker = vision.HandLandmarker.create_from_options(options)

# -----------------------
# CAMERA
# -----------------------
cap = cv2.VideoCapture(0)

frame_id     = 0
capture_count = 0

# AUTO CAPTURE TIMER
last_capture_time = 0
capture_delay     = 0.2

print("Auto capture started... show your hand")
print("📌 Each sample = 63 landmarks + 2 spread features = 65 values")

# -----------------------
# LOOP
# -----------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame
    )

    result = landmarker.detect_for_video(mp_image, frame_id)
    frame_id += 1

    landmark_data = None

    # -----------------------
    # DRAW + EXTRACT LANDMARKS
    # -----------------------
    if result.hand_landmarks:

        for hand_landmarks in result.hand_landmarks:

            landmark_data = []

            for lm in hand_landmarks:
                x = int(lm.x * w)
                y = int(lm.y * h)

                # draw points
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                # save normalized landmarks
                landmark_data.append(lm.x)
                landmark_data.append(lm.y)
                landmark_data.append(lm.z)

            # -----------------------
            # EXTRA FEATURES (FIX U/V/R CONFUSION)
            # landmark 8  = index fingertip
            # landmark 12 = middle fingertip
            # landmark 7  = index DIP joint
            # landmark 11 = middle DIP joint
            # -----------------------

            # horizontal spread between index and middle fingertips
            index_tip  = hand_landmarks[8]
            middle_tip = hand_landmarks[12]

            spread_x = abs(index_tip.x - middle_tip.x)
            spread_y = abs(index_tip.y - middle_tip.y)

            landmark_data.append(spread_x)  # feature 64
            landmark_data.append(spread_y)  # feature 65

            # draw connections
            HAND_CONNECTIONS = [
                (0,1),(1,2),(2,3),(3,4),
                (0,5),(5,6),(6,7),(7,8),
                (5,9),(9,10),(10,11),(11,12),
                (9,13),(13,14),(14,15),(15,16),
                (13,17),(17,18),(18,19),(19,20),
                (0,17)
            ]

            for start, end in HAND_CONNECTIONS:
                x1 = int(hand_landmarks[start].x * w)
                y1 = int(hand_landmarks[start].y * h)
                x2 = int(hand_landmarks[end].x * w)
                y2 = int(hand_landmarks[end].y * h)

                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

            # -----------------------
            # AUTO CAPTURE DATASETS
            # now expects 65 values (63 + 2 spread features)
            # -----------------------
            if len(landmark_data) == 65:
                current_time = time.time()

                if current_time - last_capture_time > capture_delay:
                    capture_count    += 1
                    last_capture_time = current_time

                    file_path = os.path.join(
                        letter_folder,
                        f"{letter}_{capture_count}.npy"
                    )

                    np.save(file_path, np.array(landmark_data))

                    print(f"✅ Auto Saved: {capture_count}/{target_samples}")

                    # stop auto capture when target reached
                    if capture_count >= target_samples:
                        print(f"🎯 Target reached: {target_samples} samples!")
                        break

    # -----------------------
    # AUTO HAND CROP VIEW
    # -----------------------
    if result.hand_landmarks:

        for hand_landmarks in result.hand_landmarks:

            x_vals = [int(lm.x * w) for lm in hand_landmarks]
            y_vals = [int(lm.y * h) for lm in hand_landmarks]

            xmin, xmax = min(x_vals), max(x_vals)
            ymin, ymax = min(y_vals), max(y_vals)

            # padding
            pad  = 40
            xmin = max(0, xmin - pad)
            ymin = max(0, ymin - pad)
            xmax = min(w, xmax + pad)
            ymax = min(h, ymax + pad)

            # draw bounding box on main frame
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            # crop hand
            hand_crop = frame[ymin:ymax, xmin:xmax]

            # resize to fixed size (for consistency)
            if hand_crop.size != 0:
                hand_crop = cv2.resize(hand_crop, (300, 300))

            # show zoom hands window
            cv2.imshow("Hand Focus View", hand_crop)

    # -----------------------
    # SHOW SEPARATE/MAIN WINDOW
    # -----------------------
    cv2.imshow("Landmark Dataset Capture", frame)

    key = cv2.waitKey(1) & 0xFF

    # ESC
    if key == 27:
        break

    # -----------------------
    # MANUAL CAPTURE LANDMARK DATA
    # -----------------------
    elif key == ord('c') and landmark_data is not None:

        capture_count += 1

        file_path = os.path.join(
            letter_folder,
            f"{letter}_{capture_count}.npy"
        )

        np.save(file_path, np.array(landmark_data))

        print(f"✅ Saved: {file_path}")

    if cv2.getWindowProperty("Landmark Dataset Capture", cv2.WND_PROP_VISIBLE) < 1:
        break

    # stop loop when target reached
    if capture_count >= target_samples:
        break

# -----------------------
# CLEANUP
# -----------------------
cap.release()
cv2.destroyAllWindows()
landmarker.close()

print(f"🎯 Done! Total samples saved: {capture_count}")