import tkinter as tk
from PIL import Image, ImageTk
import importlib.util
import os
import traceback

print("📋 Loading Menu Window...")


# -----------------------
# HELPER: LOAD AND LAUNCH MODULE
# -----------------------
def open_module(filename, function_name, username):

    base_dir  = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)

    try:
        spec   = importlib.util.spec_from_file_location(filename, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        getattr(module, function_name)(username)

    except Exception as e:
        print(f"❌ Error loading {filename}:", e)
        traceback.print_exc()


# -----------------------
# HELPER: BIND CLICK TO ALL CHILDREN RECURSIVELY
# fixes the issue where clicking text/icon inside button doesnt register
# -----------------------
def bind_all_children(widget, event, callback):
    widget.bind(event, callback)
    for child in widget.winfo_children():
        bind_all_children(child, event, callback)


# -----------------------
# HELPER: SHOW LOADING WINDOW
# displays while TensorFlow and MediaPipe load
# uses Toplevel so it works within existing tkinter instance
# -----------------------
def show_loading(parent, title="Loading...", message="Please wait..."):

    loading = tk.Toplevel(parent)
    loading.title("HandTalk")
    loading.resizable(False, False)
    loading.overrideredirect(True)  # no title bar — clean popup

    # center window
    w, h = 320, 160
    sw = loading.winfo_screenwidth()
    sh = loading.winfo_screenheight()
    loading.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    loading.configure(bg="white")

    # border effect
    tk.Frame(loading, bg="#22c55e", height=4).pack(fill="x")

    # icon + title
    top = tk.Frame(loading, bg="white")
    top.pack(pady=(20, 8))

    tk.Label(top, text="✋", font=("Arial", 22), bg="white").pack(side="left", padx=(20, 10))

    tk.Label(
        top,
        text=title,
        font=("Arial", 14, "bold"),
        bg="white",
        fg="#1e293b"
    ).pack(side="left")

    # message
    tk.Label(
        loading,
        text=message,
        font=("Arial", 10),
        bg="white",
        fg="#64748b"
    ).pack()

    # animated dots label
    dots_label = tk.Label(
        loading,
        text="Loading ●○○",
        font=("Arial", 10),
        bg="white",
        fg="#22c55e"
    )
    dots_label.pack(pady=(10, 0))

    # animate the dots
    dots = ["Loading ●○○", "Loading ○●○", "Loading ○○●"]
    dot_idx = [0]

    def animate():
        try:
            dots_label.config(text=dots[dot_idx[0] % 3])
            dot_idx[0] += 1
            loading.after(400, animate)
        except:
            pass

    animate()
    loading.update()

    return loading


# -----------------------
# LAUNCH MENU (ENTRY)
# -----------------------
def launch_menu(username="Guest"):

    # track which mode was selected
    selected = {"action": None}

    # -----------------------
    # TKINTER INIT
    # -----------------------
    root = tk.Tk()
    root.title("HandTalk - Menu")

    # center window
    window_width  = 450
    window_height = 620

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    x = (screen_w // 2) - (window_width  // 2)
    y = (screen_h // 2) - (window_height // 2)

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg="white")

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

    # -----------------------
    # LOGO ICON (green square + hand PNG)
    # -----------------------
    icon_frame = tk.Frame(root, bg="#22c55e", width=90, height=90)
    icon_frame.pack(pady=(40, 16))
    icon_frame.pack_propagate(False)

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        hand_path  = os.path.join(parent_dir, "Assets", "Images", "highfive-removebg-preview.png")

        hand_img   = Image.open(hand_path)
        hand_img   = hand_img.resize((60, 60), Image.Resampling.LANCZOS)
        hand_photo = ImageTk.PhotoImage(hand_img)

        icon_label = tk.Label(icon_frame, image=hand_photo, bg="#22c55e")
        icon_label.image = hand_photo
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

    except Exception as e:
        print(f"⚠️ Could not load hand image: {e}")
        tk.Label(
            icon_frame,
            text="✋",
            font=("Arial", 45),
            bg="#22c55e",
            fg="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

    # -----------------------
    # TITLE
    # -----------------------
    tk.Label(
        root,
        text="HandTalk",
        font=("Arial", 28, "bold"),
        bg="white",
        fg="#1e293b"
    ).pack(pady=(0, 10))

    # welcome message
    welcome_frame = tk.Frame(root, bg="white")
    welcome_frame.pack(pady=(0, 30))

    tk.Label(welcome_frame, text="👤", font=("Arial", 14), bg="white").pack(side="left", padx=(0, 5))
    tk.Label(welcome_frame, text="Welcome, ",  font=("Arial", 12),         bg="white", fg="#22c55e").pack(side="left")
    tk.Label(welcome_frame, text=f"{username}!", font=("Arial", 12, "bold"), bg="white", fg="#22c55e").pack(side="left")

    # -----------------------
    # MENU BUTTONS FRAME
    # -----------------------
    btn_frame = tk.Frame(root, bg="white")
    btn_frame.pack(padx=30, fill="x")

    # -----------------------
    # HELPER: BUILD MENU BUTTON
    # avoids repeating the same structure 3 times
    # -----------------------
    def make_menu_btn(parent, icon, title, subtitle, on_click):

        btn = tk.Frame(parent, bg="#22c55e", cursor="hand2")
        btn.pack(fill="x", pady=(0, 12))

        content = tk.Frame(btn, bg="#22c55e")
        content.pack(fill="both", padx=20, pady=16)

        # icon box
        icon_box = tk.Frame(content, bg="#4ade80", width=48, height=48)
        icon_box.pack(side="left", padx=(0, 12))
        icon_box.pack_propagate(False)
        tk.Label(icon_box, text=icon, font=("Arial", 20), bg="#4ade80").place(relx=0.5, rely=0.5, anchor="center")

        # text
        text_frame = tk.Frame(content, bg="#22c55e")
        text_frame.pack(side="left", fill="x", expand=True)

        tk.Label(text_frame, text=title,    font=("Arial", 13, "bold"), bg="#22c55e", fg="white",   anchor="w").pack(fill="x")
        tk.Label(text_frame, text=subtitle, font=("Arial", 9),          bg="#22c55e", fg="#bbf7d0", anchor="w").pack(fill="x")

        # hover effect
        def on_enter(e):
            for w in [btn, content, text_frame, icon_box] + list(text_frame.winfo_children()):
                try: w.config(bg="#16a34a")
                except: pass

        def on_leave(e):
            for w in [btn, content, text_frame]:
                try: w.config(bg="#22c55e")
                except: pass
            try: icon_box.config(bg="#4ade80")
            except: pass
            for w in text_frame.winfo_children():
                try: w.config(bg="#22c55e")
                except: pass

        # [FIXED] bind click and hover to ALL children recursively
        bind_all_children(btn, "<Button-1>", lambda e: on_click())
        bind_all_children(btn, "<Enter>",    on_enter)
        bind_all_children(btn, "<Leave>",    on_leave)

        return btn

    # -----------------------
    # REAL-TIME TRANSLATION BUTTON
    # -----------------------
    def open_realtime():
        selected["action"] = "realtime"
        root.quit()
        root.destroy()

    make_menu_btn(btn_frame, "🎥", "Real-time Translation", "Detect ASL signs from webcam", open_realtime)

    # -----------------------
    # TRAINING MODE BUTTON
    # -----------------------
    def open_training():
        selected["action"] = "training"
        root.quit()
        root.destroy()

    make_menu_btn(btn_frame, "✋", "ASL Training Mode", "Practice and improve your signs", open_training)

    # -----------------------
    # VIEW PROGRESS BUTTON
    # -----------------------
    def open_progress():
        open_module("progress.py", "launch_progress", username)

    make_menu_btn(btn_frame, "📊", "View Progress", "Track your learning journey", open_progress)

    # -----------------------
    # LOGOUT BUTTON
    # -----------------------
    def logout():
        selected["action"] = "logout"
        root.quit()
        root.destroy()

    # separator line
    tk.Frame(root, bg="#e2e8f0", height=1).pack(fill="x", padx=30, pady=(20, 16))

    logout_link = tk.Label(
        root,
        text="🚪 Logout",
        font=("Arial", 10),
        bg="white",
        fg="#64748b",
        cursor="hand2"
    )
    logout_link.pack(pady=(0, 20))
    logout_link.bind("<Button-1>", lambda e: logout())

    # hover effect for logout
    logout_link.bind("<Enter>", lambda e: logout_link.config(fg="#ef4444"))
    logout_link.bind("<Leave>", lambda e: logout_link.config(fg="#64748b"))

    root.mainloop()

    # -----------------------
    # AFTER MAINLOOP EXITS
    # launch selected action
    # -----------------------
    action = selected["action"]

    if action == "realtime":

        # show loading as fresh Tk window after menu is fully gone
        loading = tk.Tk()
        loading.title("HandTalk")
        loading.resizable(False, False)
        loading.overrideredirect(True)
        w, h = 320, 160
        sw = loading.winfo_screenwidth()
        sh = loading.winfo_screenheight()
        loading.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        loading.configure(bg="white")
        tk.Frame(loading, bg="#22c55e", height=4).pack(fill="x")
        top_f = tk.Frame(loading, bg="white")
        top_f.pack(pady=(20, 8))
        tk.Label(top_f, text="✋", font=("Arial", 22), bg="white").pack(side="left", padx=(20, 10))
        tk.Label(top_f, text="Real-time Translation", font=("Arial", 14, "bold"), bg="white", fg="#1e293b").pack(side="left")
        tk.Label(loading, text="Starting webcam and AI model...", font=("Arial", 10), bg="white", fg="#64748b").pack()
        tk.Label(loading, text="Loading ●○○", font=("Arial", 10), bg="white", fg="#22c55e").pack(pady=(10, 0))
        loading.update()
        loading.destroy()
        open_module("ui.py", "launch_ui", username)

    elif action == "training":

        # show loading as fresh Tk window after menu is fully gone
        loading = tk.Tk()
        loading.title("HandTalk")
        loading.resizable(False, False)
        loading.overrideredirect(True)
        w, h = 320, 160
        sw = loading.winfo_screenwidth()
        sh = loading.winfo_screenheight()
        loading.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        loading.configure(bg="white")
        tk.Frame(loading, bg="#22c55e", height=4).pack(fill="x")
        top_f = tk.Frame(loading, bg="white")
        top_f.pack(pady=(20, 8))
        tk.Label(top_f, text="✋", font=("Arial", 22), bg="white").pack(side="left", padx=(20, 10))
        tk.Label(top_f, text="ASL Training Mode", font=("Arial", 14, "bold"), bg="white", fg="#1e293b").pack(side="left")
        tk.Label(loading, text="Starting webcam and AI model...", font=("Arial", 10), bg="white", fg="#64748b").pack()
        tk.Label(loading, text="Loading ●○○", font=("Arial", 10), bg="white", fg="#22c55e").pack(pady=(10, 0))
        loading.update()
        loading.destroy()
        open_module("training.py", "launch_training", username)

    elif action == "logout":
        from login import launch_login
        launch_login()

    # action is None means X was pressed — do nothing, app closes cleanly


# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    launch_menu()