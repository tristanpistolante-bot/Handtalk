import os
import cv2
import random
import importlib.util
import tkinter as tk
import pygame # Help with SoundFX
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from database import save_training_session, update_letter_accuracy

print("✋ Loading Training Mode...")


# -----------------------
# GLOBAL VARIABLES
# -----------------------
frame_id       = 0
landmarker     = None
model          = None
cap            = None
running        = False
current_letter = ""
same_count     = 0
stable_letter  = ""
score          = 0
total          = 0
target_letter  = ""

# all ASL letters
class_names    = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# -----------------------
# SOUND SYSTEM
# -----------------------
pygame.mixer.init()

try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)

    correct_sound_path = os.path.join(
        parent_dir,
        "Assets",
        "Sounds",
        "correctSFX.mp3"
    )

    wrong_sound_path = os.path.join(
        parent_dir,
        "Assets",
        "Sounds",
        "incorrectSFX.mp3"
    )

    correct_sound = pygame.mixer.Sound(correct_sound_path)
    wrong_sound = pygame.mixer.Sound(wrong_sound_path)

    print("✅ Sounds loaded")

except Exception as e:
    print("❌ Sound error:", e)
    correct_sound = None
    wrong_sound = None

# -----------------------
# LOAD SYSTEMS (SAFE)
# -----------------------
def load_systems():
    global model, landmarker

    try:
        from tensorflow.keras.models import load_model
        model = load_model("model.h5")
        print("✅ Model loaded")
    except Exception as e:
        print("❌ Model error:", e)

    try:
        MODEL_PATH = "hand_landmarker.task"

        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1
        )

        landmarker = vision.HandLandmarker.create_from_options(options)

        print("✅ MediaPipe Tasks loaded")

    except Exception as e:
        print("❌ MediaPipe error:", e)


# -----------------------
# HELPER: GO BACK TO MENU
# -----------------------
def go_to_menu(username):
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from menu import launch_menu
    launch_menu(username)


# -----------------------
# LAUNCH TRAINING (ENTRY)
# -----------------------
def launch_training(username="Guest"):

    # -----------------------
    # RESET GLOBALS
    # -----------------------
    global frame_id, cap, running, current_letter, same_count
    global stable_letter, score, total, target_letter, landmarker, model

    frame_id       = 0
    running        = False
    current_letter = ""
    same_count     = 0
    stable_letter  = ""
    score          = 0
    total          = 0

    # -----------------------
    # TKINTER INIT
    # -----------------------
    root = tk.Tk()
    root.title("HandTalk - Training Mode")

    # force fullscreen size
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.geometry(f"{screen_w}x{screen_h}+0+0")
    root.state("zoomed")
    root.configure(bg="#1e293b")  # Dark slate background

    # Set window icon
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        icon_path = os.path.join(parent_dir, "Assets", "Logo", "highfive-removebg-preview.ico")
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"⚠️ Could not set window icon: {e}")

    root.lift()
    root.attributes("-topmost", True)
    root.after(500, lambda: root.attributes("-topmost", False))

    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # -----------------------
    # TOP BAR
    # -----------------------
    top_bar = tk.Frame(root, bg="#a855f7", height=70)  # Purple for training mode
    top_bar.grid(row=0, column=0, sticky="ew")
    top_bar.grid_propagate(False)

    # Left side - Logo and Title
    left_frame = tk.Frame(top_bar, bg="#a855f7")
    left_frame.pack(side="left", padx=20, pady=10)

    # Hand icon
    icon_frame = tk.Frame(left_frame, bg="#9333ea", width=45, height=45)
    icon_frame.pack(side="left", padx=(0, 12))
    icon_frame.pack_propagate(False)

    # Load hand icon
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        hand_path = os.path.join(parent_dir, "Assets", "Images", "highfive-removebg-preview.png")
        
        hand_img = Image.open(hand_path)
        hand_img = hand_img.resize((30, 30), Image.Resampling.LANCZOS)
        hand_photo = ImageTk.PhotoImage(hand_img)
        
        icon_label = tk.Label(icon_frame, image=hand_photo, bg="#9333ea")
        icon_label.image = hand_photo
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
    except:
        tk.Label(icon_frame, text="✋", font=("Arial", 20), bg="#9333ea", fg="white").place(relx=0.5, rely=0.5, anchor="center")

    # Title text
    title_text_frame = tk.Frame(left_frame, bg="#a855f7")
    title_text_frame.pack(side="left")

    tk.Label(
        title_text_frame,
        text="HandTalk",
        font=("Arial", 18, "bold"),
        bg="#a855f7",
        fg="white"
    ).pack(anchor="w")

    tk.Label(
        title_text_frame,
        text="ASL Training Mode",
        font=("Arial", 10),
        bg="#a855f7",
        fg="#e9d5ff"
    ).pack(anchor="w")

    # Right side - Username
    right_frame = tk.Frame(top_bar, bg="#a855f7")
    right_frame.pack(side="right", padx=20, pady=10)

    user_container = tk.Frame(right_frame, bg="#9333ea")
    user_container.pack()

    tk.Label(
        user_container,
        text=f"👤 {username}",
        font=("Arial", 11, "bold"),
        bg="#9333ea",
        fg="white",
        padx=16,
        pady=8
    ).pack()

    # -----------------------
    # MAIN FRAME
    # -----------------------
    main_frame = tk.Frame(root, bg="#1e293b")
    main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

    # 70 / 30 split
    main_frame.columnconfigure(0, weight=7, uniform="group1")
    main_frame.columnconfigure(1, weight=3, uniform="group1")
    main_frame.rowconfigure(0, weight=1)

    # -----------------------
    # WEBCAM FRAME (70%)
    # -----------------------
    webcam_container = tk.Frame(main_frame, bg="#334155", relief="solid", bd=2)
    webcam_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    # Header
    webcam_header = tk.Frame(webcam_container, bg="#475569", height=40)
    webcam_header.pack(fill="x")
    webcam_header.pack_propagate(False)

    tk.Label(
        webcam_header,
        text="Live Webcam Feed",
        font=("Arial", 12, "bold"),
        bg="#475569",
        fg="white"
    ).pack(side="left", padx=15, pady=8)

    # Webcam display
    webcam_label = tk.Label(webcam_container, bg="#1e293b")
    webcam_label.pack(fill="both", expand=True, padx=2, pady=2)

    # -----------------------
    # TRAINING PANEL (30%)
    # -----------------------
    panel_container = tk.Frame(main_frame, bg="#334155", relief="solid", bd=2)
    panel_container.grid(row=0, column=1, sticky="nsew")

    # Header
    panel_header = tk.Frame(panel_container, bg="#475569", height=40)
    panel_header.pack(fill="x")
    panel_header.pack_propagate(False)

    tk.Label(
        panel_header,
        text="Training Panel",
        font=("Arial", 12, "bold"),
        bg="#475569",
        fg="white"
    ).pack(side="left", padx=15, pady=8)

    # Panel content
    panel_content = tk.Frame(panel_container, bg="#1e293b")
    panel_content.pack(fill="both", expand=True, padx=15, pady=15)

    # Target letter section
    tk.Label(
        panel_content,
        text="Sign this letter:",
        font=("Arial", 12),
        bg="#1e293b",
        fg="#94a3b8"
    ).pack(pady=(10, 8))

    # Target letter display with background
    target_bg = tk.Frame(panel_content, bg="#3b82f6", width=180, height=180)
    target_bg.pack(pady=10)
    target_bg.pack_propagate(False)

    target_label = tk.Label(
        target_bg,
        text="?",
        font=("Arial", 80, "bold"),
        bg="#3b82f6",
        fg="white"
    )
    target_label.place(relx=0.5, rely=0.5, anchor="center")

    # Result feedback
    result_label = tk.Label(
        panel_content,
        text="",
        font=("Arial", 13, "bold"),
        bg="#1e293b",
        fg="#e2e8f0"
    )
    result_label.pack(pady=12)

    # Score section
    score_container = tk.Frame(panel_content, bg="#334155")
    score_container.pack(fill="x", pady=15)

    tk.Label(
        score_container,
        text="Score:",
        font=("Arial", 11),
        bg="#334155",
        fg="#94a3b8"
    ).pack(pady=(10, 5))

    score_label = tk.Label(
        score_container,
        text="0 / 0",
        font=("Arial", 28, "bold"),
        bg="#334155",
        fg="white"
    )
    score_label.pack(pady=(0, 10))

    # Progress section
    tk.Label(
        panel_content,
        text="Session Progress:",
        font=("Arial", 11),
        bg="#1e293b",
        fg="#94a3b8"
    ).pack(pady=(5, 8))

    progress_bar_bg = tk.Frame(panel_content, bg="#475569", height=12)
    progress_bar_bg.pack(fill="x", pady=5)
    progress_bar_bg.pack_propagate(False)

    progress_bar_fill = tk.Frame(progress_bar_bg, bg="#22c55e", height=12, width=0)
    progress_bar_fill.pack(side="left")

    # Percentage label
    progress_pct_label = tk.Label(
        panel_content,
        text="0%",
        font=("Arial", 10),
        bg="#1e293b",
        fg="#64748b"
    )
    progress_pct_label.pack(pady=(3, 0))

    # track scheduled loop
    after_id = None

    # -----------------------
    # NEXT LETTER FUNCTION
    # -----------------------
    def next_letter():
        global target_letter, same_count, current_letter, stable_letter

        target_letter  = random.choice(class_names)
        same_count     = 0
        current_letter = ""
        stable_letter  = ""

        target_label.config(text=target_letter)
        target_bg.config(bg="#3b82f6")
        target_label.config(bg="#3b82f6", fg="white")
        result_label.config(text="")

        print(f"🎯 New target: {target_letter}")

    # -----------------------
    # UPDATE PROGRESS BAR
    # -----------------------
    def update_progress():
        if total > 0:
            pct = int((score / total) * 100)
            panel_width = panel_content.winfo_width()
            bar_width = int((panel_width - 30) * (score / total))
            progress_bar_fill.config(width=max(0, bar_width))
            progress_pct_label.config(text=f"{pct}%")

    # -----------------------
    # CAMERA LOOP
    # -----------------------
    def update_frame():
        nonlocal after_id

        global cap, running, frame_id
        global current_letter, same_count, stable_letter
        global score, total

        if not running or cap is None:
            after_id = None
            return

        ret, frame = cap.read()
        if not ret:
            after_id = root.after(30, update_frame)
            return

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        status_text = "Detected: None"

        try:
            if landmarker is not None and target_letter:

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame
                )

                result = landmarker.detect_for_video(mp_image, frame_id)
                frame_id += 1

                if result.hand_landmarks:

                    for hand_landmarks in result.hand_landmarks:

                        points            = []
                        landmark_features = []

                        for lm in hand_landmarks:
                            x = int(lm.x * w)
                            y = int(lm.y * h)

                            points.append((x, y))

                            landmark_features.append(lm.x)
                            landmark_features.append(lm.y)
                            landmark_features.append(lm.z)

                            cv2.circle(frame, (x, y), 5, (34, 197, 94), -1)  # Green dots

                        if len(points) != 21:
                            continue

                        index_tip  = hand_landmarks[8]
                        middle_tip = hand_landmarks[12]

                        spread_x = abs(index_tip.x - middle_tip.x)
                        spread_y = abs(index_tip.y - middle_tip.y)

                        landmark_features.append(spread_x)
                        landmark_features.append(spread_y)

                        landmark_features = np.array(landmark_features).reshape(1, -1)

                        # Bounding box
                        x_vals = [p[0] for p in points]
                        y_vals = [p[1] for p in points]

                        xmin, xmax = min(x_vals), max(x_vals)
                        ymin, ymax = min(y_vals), max(y_vals)

                        pad  = 20
                        xmin = max(0, xmin - pad)
                        ymin = max(0, ymin - pad)
                        xmax = min(w, xmax + pad)
                        ymax = min(h, ymax + pad)

                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (34, 197, 94), 3)  # Green box

                        # Skeleton
                        HAND_CONNECTIONS = [
                            (0,1),(1,2),(2,3),(3,4),
                            (0,5),(5,6),(6,7),(7,8),
                            (5,9),(9,10),(10,11),(11,12),
                            (9,13),(13,14),(14,15),(15,16),
                            (13,17),(17,18),(18,19),(19,20),
                            (0,17)
                        ]

                        for start, end in HAND_CONNECTIONS:
                            cv2.line(frame, points[start], points[end], (59, 130, 246), 2)  # Blue lines

                        # Prediction
                        if model is not None:

                            prediction = model.predict(landmark_features, verbose=0)

                            confidence = float(np.max(prediction))
                            pred_index = int(np.argmax(prediction))
                            letter     = class_names[pred_index] if pred_index < len(class_names) else "?"

                            # Stability filter
                            if letter == current_letter:
                                same_count += 1
                            else:
                                current_letter = letter
                                same_count     = 1

                            # Check answer (stable)
                            if same_count == 10 and confidence > 0.7:
                                stable_letter = current_letter
                                is_correct    = (stable_letter == target_letter)

                                total += 1

                                # update letter accuracy in db
                                update_letter_accuracy(username, target_letter, is_correct)

                                if is_correct:
                                    score += 1
                                    result_label.config(text="✅ Correct!", fg="#22c55e")
                                    target_bg.config(bg="#22c55e")
                                    target_label.config(bg="#22c55e")
                                    
                                    if correct_sound: 
                                        correct_sound.play() # Play correct sound
                                else:
                                    result_label.config(text=f"❌ Wrong! You signed: {stable_letter}", fg="#ef4444")
                                    target_bg.config(bg="#ef4444")
                                    target_label.config(bg="#ef4444")

                                    if wrong_sound: 
                                        wrong_sound.play() # Play incorrect sound 

                                score_label.config(text=f"{score} / {total}")
                                update_progress()

                                # auto next letter after 1.5 seconds
                                root.after(1500, next_letter)

                            # Overlay on frame
                            cv2.putText(
                                frame,
                                f"{letter} ({confidence*100:.1f}%)",
                                (xmin, ymin - 15),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.0,
                                (34, 197, 94),  # Green
                                2,
                                cv2.LINE_AA
                            )

                            status_text = f"Detected: {letter} ({confidence*100:.1f}%)"

                else:
                    current_letter = ""
                    same_count     = 0
                    status_text    = "Detected: None"

        except Exception as e:
            print("⚠️ Frame error:", e)

        # Status text
        cv2.putText(
            frame,
            status_text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (34, 197, 94),  # Green
            2,
            cv2.LINE_AA
        )

        # Display frame
        w_label = webcam_label.winfo_width()
        h_label = webcam_label.winfo_height()

        if w_label > 1 and h_label > 1:
            frame = cv2.resize(frame, (w_label, h_label))

        img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        webcam_label.imgtk = img
        webcam_label.config(image=img)

        after_id = root.after(30, update_frame)

    # -----------------------
    # BUTTON FUNCTIONS
    # -----------------------
    def start_camera():
        nonlocal after_id

        global cap, running

        if not running:

            if after_id is not None:
                root.after_cancel(after_id)

            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            running = True

            # pick first target letter
            next_letter()

            after_id = root.after(0, update_frame)

    def stop_camera():
        nonlocal after_id

        global cap, running
        running = False

        if after_id is not None:
            root.after_cancel(after_id)
            after_id = None

        if cap:
            cap.release()
            cap = None

        webcam_label.config(image="")
        webcam_label.imgtk = None

    def end_session():
        if total > 0:
            save_training_session(username, score, total)
            print(f"✅ Session ended: {score}/{total}")

        stop_camera()
        root.quit()
        root.destroy()

    def on_close():
        if total > 0:
            save_training_session(username, score, total)

        stop_camera()
        root.quit()
        root.destroy()

    def watch_tutorial():
        base_dir   = os.path.dirname(os.path.abspath(__file__))
        video_path = os.path.join(base_dir, "..", "Assets", "Videos", "Learn ASL Alphabet Video.mp4")
        video_path = os.path.normpath(video_path)

        if os.path.exists(video_path):
            os.startfile(video_path)
        else:
            messagebox.showerror(
                "Video Not Found",
                f"Tutorial video not found at:\n{video_path}"
            )

    # -----------------------
    # STYLED BUTTONS
    # -----------------------
    button_container = tk.Frame(root, bg="#1e293b")
    button_container.grid(row=2, column=0, pady=20)

    def create_button(parent, text, command, bg_color):
        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 11, "bold"),
            bg=bg_color,
            fg="white",
            activebackground=bg_color,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=command,
            padx=20,
            pady=10
        )
        return btn

    start_btn = create_button(button_container, "▶ Start", start_camera, "#22c55e")
    start_btn.pack(side="left", padx=5)

    stop_btn = create_button(button_container, "■ Stop", stop_camera, "#ef4444")
    stop_btn.pack(side="left", padx=5)

    next_btn = create_button(button_container, "⏭ Next Letter", next_letter, "#3b82f6")
    next_btn.pack(side="left", padx=5)

    end_btn = create_button(button_container, "🏁 End Session", end_session, "#f97316")
    end_btn.pack(side="left", padx=5)

    tutorial_btn = create_button(button_container, "📺 Watch Tutorial", watch_tutorial, "#a855f7")
    tutorial_btn.pack(side="left", padx=5)

    exit_btn = create_button(button_container, "✕ Exit", on_close, "#64748b")
    exit_btn.pack(side="left", padx=5)

    # Hover effects
    def add_hover(button, hover_color, normal_color):
        button.bind("<Enter>", lambda e: button.config(bg=hover_color))
        button.bind("<Leave>", lambda e: button.config(bg=normal_color))

    add_hover(start_btn, "#16a34a", "#22c55e")
    add_hover(stop_btn, "#dc2626", "#ef4444")
    add_hover(next_btn, "#2563eb", "#3b82f6")
    add_hover(end_btn, "#ea580c", "#f97316")
    add_hover(tutorial_btn, "#9333ea", "#a855f7")
    add_hover(exit_btn, "#475569", "#64748b")

    root.protocol("WM_DELETE_WINDOW", on_close)

    # -----------------------
    # START SYSTEM
    # -----------------------
    load_systems()
    root.mainloop()

    # -----------------------
    # AFTER MAINLOOP EXITS
    # go back to menu
    # -----------------------
    go_to_menu(username)


# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    launch_training()