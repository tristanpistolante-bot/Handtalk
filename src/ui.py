import os
import cv2
from datetime import datetime
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox # For watchtutorial thing
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from database import insert_translation
from tkinter import messagebox

print("🚀 Starting HandTalk UI...")

# -----------------------
# GLOBAL VARIABLE
# -----------------------
frame_id = 0                    # int
frame_count = 0                 # int
landmarker = None               # NoneType — None is Python's way of saying "empty/not set yet"
model = None                    # NoneType — same, will be replaced with TensorFlow model later
running = False                 # bool
cap = None                      # NoneType — will be replaced with OpenCV camera object later
last_letter = ""                # str
display_text = "Detected: None" # str
stable_letter = ""              # str
stable_confidence = 0           # int
same_count = 0                  # int
current_letter = ""             # str


# -----------------------
# LOAD SYSTEMS (SAFE)
# -----------------------
def load_systems():
    global model, landmarker # global is need so it does not create new variable    

    try:
        from tensorflow.keras.models import load_model # Import only load_model function
        model = load_model("model.h5")
        print("✅ Model loaded (A-Z Landmark-Model)")
    except Exception as e:
        print("❌ Model error:", e)

    try:
        MODEL_PATH = "hand_landmarker.task" # All caps because it would be constant variable
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
# WRAPPED EVERYTHING INSIDE launch_ui()
# SO TKINTER STARTS FRESH AFTER LOGIN WINDOW CLOSES
# -----------------------
def launch_ui(username="Guest"): # Default to "Guest" if pass no value
    # -----------------------
    # GLOBALS DECLARED INSIDE launch_ui()
    # SO update_frame() AND BUTTONS CAN STILL ACCESS THEM
    # -----------------------
    global frame_id, frame_count, landmarker, model, running, cap
    global last_letter, display_text, stable_letter, stable_confidence
    global same_count, current_letter

    # -----------------------
    # TKINTER INIT
    # -----------------------
    root = tk.Tk()
    root.title("HandTalk - Real-time Translation")

    # force fullscreen size
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.geometry(f"{screen_w}x{screen_h}+0+0")
    root.state("zoomed") # Automatically triggers the window to maximize 
    root.configure(bg="#1e293b")  # Dark slate background

    # Set window icon
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        icon_path = os.path.join(parent_dir, "Assets", "Logo", "highfive-removebg-preview.ico")
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"⚠️ Could not set window icon: {e}")

    root.lift() # Make the ui window to appears in front of everything else 
    root.attributes("-topmost", True) # Forces the window to always stay on top of every other window on your screen even if you click on another app
    root.after(500, lambda: root.attributes("-topmost", False)) #  After 0.5 seconds, Release the lock so it behaves like a normal window, Creates a small anonymous function with no name,  

    # Layout fix
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # -----------------------
    # TOP BAR with gradient-like effect
    # -----------------------
    top_bar = tk.Frame(root, bg="#22c55e", height=70)
    top_bar.grid(row=0, column=0, sticky="ew")
    top_bar.grid_propagate(False)

    # Left side - Logo and Title
    left_frame = tk.Frame(top_bar, bg="#22c55e")
    left_frame.pack(side="left", padx=20, pady=10)

    # Hand icon
    icon_frame = tk.Frame(left_frame, bg="#16a34a", width=45, height=45)
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
        
        icon_label = tk.Label(icon_frame, image=hand_photo, bg="#16a34a")
        icon_label.image = hand_photo
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
    except:
        tk.Label(icon_frame, text="✋", font=("Arial", 20), bg="#16a34a", fg="white").place(relx=0.5, rely=0.5, anchor="center")

    # Title text
    title_text_frame = tk.Frame(left_frame, bg="#22c55e")
    title_text_frame.pack(side="left")

    tk.Label(
        title_text_frame,
        text="HandTalk",
        font=("Arial", 18, "bold"),
        bg="#22c55e",
        fg="white"
    ).pack(anchor="w")

    tk.Label(
        title_text_frame,
        text="Real-time Translation",
        font=("Arial", 10),
        bg="#22c55e",
        fg="#dcfce7"
    ).pack(anchor="w")

    # Right side - Username
    right_frame = tk.Frame(top_bar, bg="#22c55e")
    right_frame.pack(side="right", padx=20, pady=10)

    user_container = tk.Frame(right_frame, bg="#16a34a")
    user_container.pack()

    tk.Label(
        user_container,
        text=f"👤 {username}",
        font=("Arial", 11, "bold"),
        bg="#16a34a",
        fg="white",
        padx=16,
        pady=8
    ).pack()

    # -----------------------
    # MAIN FRAME FOR WEBCAM
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
    # TRANSLATION LOG FRAME (30%)
    # -----------------------
    log_container = tk.Frame(main_frame, bg="#334155", relief="solid", bd=2)
    log_container.grid(row=0, column=1, sticky="nsew")

    # Header
    log_header = tk.Frame(log_container, bg="#475569", height=40)
    log_header.pack(fill="x")
    log_header.pack_propagate(False)

    tk.Label(
        log_header,
        text="Translation Log",
        font=("Arial", 12, "bold"),
        bg="#475569",
        fg="white"
    ).pack(side="left", padx=15, pady=8)

    # Log text area
    log_text = tk.Text(
        log_container,
        bg="#1e293b",
        fg="#e2e8f0",
        font=("Consolas", 11),
        insertbackground="white",
        relief="flat",
        padx=10,
        pady=10
    )
    log_text.pack(fill="both", expand=True, padx=2, pady=2)

    # -----------------------
    # BUTTONS
    # -----------------------
    button_container = tk.Frame(root, bg="#1e293b") # acts like a dashboard control panel where you can group all your interaction buttons Start, Stop, Save, Clear
    button_container.grid(row=2, column=0, pady=20) 

    # ASL Label Map
    class_names = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    # track scheduled loop
    after_id = None
   
    # -----------------------
    # CAMERA LOOP
    # -----------------------
    def update_frame():
        nonlocal after_id   

        global cap, running, last_letter, frame_id
        global stable_letter, stable_confidence, same_count, current_letter
        global display_text

        if not running or cap is None: # IF camera is OFF OR webcam is not opened
            after_id = None # Reset the loop tracker cause if camera is OFF there should be NO running loop scheduled
            return

        ret, frame = cap.read() # Grab one frame from webcam
        if not ret: # If camera failed to read frame
            after_id = root.after(30, update_frame) # delay for 0.03 seconds so instead of crashing, it keeps retrying camera input.
            return

        frame = cv2.flip(frame, 1) # Flip the webcam so its not inverted 1(mirror model)
        h, w, _ = frame.shape # Get the size(height, width) of the webcam frame so we can correctly map hand positions and draw UI overlays _ ignored this varaible

        try:
            if landmarker is not None:

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert webcam image from OpenCV format (BGR) to MediaPipe format (RGB)   cause OpenCv uses BGR format (Blue, Green, Red), But MediaPipe expects: RGB format (Red, Green, Blue)

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB, # Tells MediaPipe image color format type ie RGB format 
                    data=rgb_frame # Converting the image format and wrapping it so MediaPipe can process the NumPy array correctly
                )

                result = landmarker.detect_for_video(mp_image, frame_id) # Detect Hands, Landmarks base on the mp_image and frame_id
                frame_id += 1 # Tracks hand movement over time by frame 

                if result.hand_landmarks: # Did MediaPipe detect any hands?

                    for hand_landmarks in result.hand_landmarks: # hand_landmarks is TEMP variable that take one hand at a time, in means "take items from", Loops through every detected hand, 

                        points            = [] # Will stores screen positions of hand landmarks ex: [(320, 240), (330, 250), ...], used later for drawing skeleton lines, bounding box etc
                        landmark_features = [] # Stores normalized landmark coordinates for TensorFlow model

                        for lm in hand_landmarks: # lm represent 1 landmark and loops through all 21 landmarks, Processes each finger joint one by one 
                            x = int(lm.x * w) # Converts landmark x-position into real screen coordinate.
                            y = int(lm.y * h) # Converts landmark y-position into real screen coordinate.

                            points.append((x, y)) # Add new item into list ex:(320, 240), Stores landmark positions for: skeleton drawing, bounding box etc...

                            landmark_features.append(lm.x) # Stores x-position as AI model input
                            landmark_features.append(lm.y) # Stores y-coordinate for AI prediction
                            landmark_features.append(lm.z) # Stores depth coordinate ie distance from camera negtive closer to cam, postive farther from cam

                            cv2.circle(frame, (x, y), 5, (34, 197, 94), -1)  # Draws a circle on image on webcam frame green dots

                        if len(points) != 21: # "Did we successfully detect ALL 21 hand landmarks?" so that AI wouldnt confuse len iis func that count items
                            continue

                        index_tip  = hand_landmarks[8] # Gets the position of the INDEX fingertip
                        middle_tip = hand_landmarks[12] # Gets the position of the MIDDLE fingertip

                        spread_x = abs(index_tip.x - middle_tip.x) # abs get rid negative value ex: -5 → 5, Determines how far apart the fingers are horizontally
                        spread_y = abs(index_tip.y - middle_tip.y) # same with spread_x Measures vertical finger spacing

                        landmark_features.append(spread_x) # Adds item into list ie Horizontal finger spacing value, Adds extra feature into AI input to better recognize finger separation, hand shape differences etc
                        landmark_features.append(spread_y) # same with above Adds Vertical finger spacing value into AI features

                        landmark_features = np.array(landmark_features).reshape(1, -1) # Convert features into model input format

                        # Bounding box
                        x_vals = [p[0] for p in points] # Get all x coordinates
                        y_vals = [p[1] for p in points] # Get all y coordinates

                        xmin, xmax = min(x_vals), max(x_vals) # Left/right edges
                        ymin, ymax = min(y_vals), max(y_vals) # Top/bottom edges

                        pad  = 20 # Box padding
                        xmin = max(0, xmin - pad) # Expand left
                        ymin = max(0, ymin - pad) # Expand top  
                        xmax = min(w, xmax + pad) # Expand right
                        ymax = min(h, ymax + pad) # Expand bottom

                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (34, 197, 94), 3)  # Draw green handbox

                        # Skeleton
                        HAND_CONNECTIONS = [
                            (0,1),(1,2),(2,3),(3,4),
                            (0,5),(5,6),(6,7),(7,8),
                            (5,9),(9,10),(10,11),(11,12),    # Define which points connect ex: (0 , 1) means connect landmark 0 to landmark 1
                            (9,13),(13,14),(14,15),(15,16),
                            (13,17),(17,18),(18,19),(19,20),
                            (0,17)
                        ]

                        for start, end in HAND_CONNECTIONS: # Processes every hand connection one by one, Take one connection pair -> Draw line between landmarks -> Repeat for all fingers
                            cv2.line(frame, points[start], points[end], (59, 130, 246), 2)  # Blue lines

                        # Prediction
                        if model is not None:

                            prediction = model.predict(landmark_features, verbose=0)

                            confidence = np.max(prediction)
                            pred_index = np.argmax(prediction)
                            letter     = class_names[pred_index] if pred_index < len(class_names) else "?"

                            print("DEBUG:", letter, confidence)

                            # Stability filter
                            if letter == current_letter:
                                same_count += 1
                            else:
                                current_letter = letter
                                same_count     = 1

                            if same_count >= 5 and confidence > 0.7:
                                stable_letter     = current_letter
                                stable_confidence = confidence

                            if stable_letter and stable_letter != last_letter and same_count >= 5:

                                timestamp = datetime.now().strftime("%I:%M:%S %p") # Change to standard timezone
                                log_entry = f"{stable_letter}  —  {timestamp}\n"

                                log_text.insert(tk.END, log_entry)
                                log_text.see(tk.END)
                                last_letter = stable_letter

                                insert_translation(stable_letter, stable_confidence)

                            # UI text
                            display_text = f"Live: {letter} ({confidence*100:.1f}%) | Stable: {stable_letter}"

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

                            if stable_letter:
                                cv2.putText(
                                    frame,
                                    f"Stable: {stable_letter} ({stable_confidence*100:.1f}%)",
                                    (xmin, ymax + 30),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8,
                                    (250, 204, 21),  # Yellow
                                    2,
                                    cv2.LINE_AA
                                )

                else:
                    same_count     = 0
                    current_letter = ""
                    display_text   = "Detected: None"

            # Status text
            cv2.putText(
                frame,
                display_text,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (34, 197, 94),  # Green
                2,
                cv2.LINE_AA
            )

        except Exception as e:
            print("⚠️ Frame error:", e)

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
                after_id = None

            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            running = True
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

    def save_log():
        # Get translation log and remove spaces/newlines
        content = log_text.get("1.0", tk.END).strip()

        if content == "":
            messagebox.showwarning("No Log Found", "There is no translation log to save.")

        else:
            with open("log.txt", "a") as f:  # "a" append | "w" overwrite
                f.write(content)
                f.write("\n")

            messagebox.showinfo("Saved", "Translation log has been saved successfully!")


    def clear_log():
        log_text.delete("1.0", tk.END)

    def on_close():
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

    save_btn = create_button(button_container, "💾 Save", save_log, "#3b82f6")
    save_btn.pack(side="left", padx=5)

    clear_btn = create_button(button_container, "🗑 Clear", clear_log, "#f97316")
    clear_btn.pack(side="left", padx=5)

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
    add_hover(save_btn, "#2563eb", "#3b82f6")
    add_hover(clear_btn, "#ea580c", "#f97316")
    add_hover(tutorial_btn, "#9333ea", "#a855f7")
    add_hover(exit_btn, "#475569", "#64748b")

    root.protocol("WM_DELETE_WINDOW", on_close)

    # -----------------------
    # START SYSTEM
    # -----------------------
    load_systems()
    root.mainloop()

    # -----------------------
    # AFTER MAINLOOP EXITS (exit button was pressed)
    # go back to menu using direct import (avoids WinError 6)
    # -----------------------
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from menu import launch_menu
    launch_menu(username)


# -----------------------
# [CHANGED] ENTRY POINT
# run directly = launch_ui() | called from login = launch_ui(username)
# -----------------------
if __name__ == "__main__":
    launch_ui()