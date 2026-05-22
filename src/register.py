import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from database import register_user
import os

print("📝 Loading Register Window...")


# -----------------------
# LAUNCH REGISTER
# -----------------------
def launch_register(parent=None, on_close=None):

    # -----------------------
    # TKINTER INIT
    # -----------------------
    window = tk.Toplevel(parent) if parent else tk.Tk()
    window.title("HandTalk - Register")

    window.resizable(False, False)
    if parent:
        window.grab_set()  # lock focus to this window

    # center window
    window_width  = 420
    window_height = 700

    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()

    x = (screen_w // 2) - (window_width  // 2)
    y = (screen_h // 2) - (window_height // 2)

    window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    window.configure(bg="white")

    # Set window icon
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        icon_path = os.path.join(parent_dir, "Assets", "Logo", "highfive-removebg-preview.ico")
        window.iconbitmap(icon_path)
    except Exception as e:
        print(f"⚠️ Could not set window icon: {e}")

    # -----------------------
    # LOGO ICON (green square + hand image)
    # -----------------------
    icon_frame = tk.Frame(window, bg="#22c55e", width=80, height=80)
    icon_frame.pack(pady=(50, 14))
    icon_frame.pack_propagate(False)

    # load hand PNG from assets or fallback to emoji
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        hand_path  = os.path.join(parent_dir, "Assets", "Images", "highfive-removebg-preview.png")

        hand_img   = Image.open(hand_path)
        hand_img   = hand_img.resize((50, 50), Image.Resampling.LANCZOS)
        hand_photo = ImageTk.PhotoImage(hand_img)

        icon_label = tk.Label(icon_frame, image=hand_photo, bg="#22c55e")
        icon_label.image = hand_photo  # keep reference
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

    except Exception as e:
        print(f"⚠️ Could not load hand image: {e}")
        tk.Label(
            icon_frame,
            text="✋",
            font=("Arial", 40),
            bg="#22c55e",
            fg="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

    # -----------------------
    # TITLE
    # -----------------------
    tk.Label(
        window,
        text="Create Account",
        font=("Arial", 26, "bold"),
        bg="white",
        fg="#1e293b"
    ).pack(pady=(0, 6))

    tk.Label(
        window,
        text="Join HandTalk today",
        font=("Arial", 11),
        bg="white",
        fg="#64748b"
    ).pack(pady=(0, 30))

    # -----------------------
    # FORM FRAME
    # -----------------------
    form = tk.Frame(window, bg="white")
    form.pack(padx=40, fill="x")

    # -----------------------
    # USERNAME FIELD
    # -----------------------
    tk.Label(
        form,
        text="Username",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#334155",
        anchor="w"
    ).pack(fill="x", pady=(0, 6))

    username_entry = tk.Entry(form, font=("Arial", 11), relief="solid", bd=1, fg="#94a3b8")
    username_entry.pack(fill="x", ipady=10)
    username_entry.insert(0, "Choose a username")

    def on_username_focus_in(e):
        if username_entry.get() == "Choose a username":
            username_entry.delete(0, tk.END)
            username_entry.config(fg="#1e293b")

    def on_username_focus_out(e):
        if not username_entry.get():
            username_entry.insert(0, "Choose a username")
            username_entry.config(fg="#94a3b8")

    username_entry.bind("<FocusIn>",  on_username_focus_in)
    username_entry.bind("<FocusOut>", on_username_focus_out)

    # -----------------------
    # PASSWORD FIELD
    # -----------------------
    tk.Label(
        form,
        text="Password",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#334155",
        anchor="w"
    ).pack(fill="x", pady=(16, 6))

    password_entry = tk.Entry(form, font=("Arial", 11), relief="solid", bd=1, fg="#94a3b8")
    password_entry.pack(fill="x", ipady=10)
    password_entry.insert(0, "Create a password")

    def on_password_focus_in(e):
        if password_entry.get() == "Create a password":
            password_entry.delete(0, tk.END)
            password_entry.config(fg="#1e293b", show="*")

    def on_password_focus_out(e):
        if not password_entry.get():
            password_entry.insert(0, "Create a password")
            password_entry.config(fg="#94a3b8", show="")

    password_entry.bind("<FocusIn>",  on_password_focus_in)
    password_entry.bind("<FocusOut>", on_password_focus_out)

    # -----------------------
    # CONFIRM PASSWORD FIELD
    # -----------------------
    tk.Label(
        form,
        text="Confirm Password",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#334155",
        anchor="w"
    ).pack(fill="x", pady=(16, 6))

    confirm_entry = tk.Entry(form, font=("Arial", 11), relief="solid", bd=1, fg="#94a3b8")
    confirm_entry.pack(fill="x", ipady=10)
    confirm_entry.insert(0, "Confirm your password")

    def on_confirm_focus_in(e):
        if confirm_entry.get() == "Confirm your password":
            confirm_entry.delete(0, tk.END)
            confirm_entry.config(fg="#1e293b", show="*")

    def on_confirm_focus_out(e):
        if not confirm_entry.get():
            confirm_entry.insert(0, "Confirm your password")
            confirm_entry.config(fg="#94a3b8", show="")

    confirm_entry.bind("<FocusIn>",  on_confirm_focus_in)
    confirm_entry.bind("<FocusOut>", on_confirm_focus_out)

    # -----------------------
    # MESSAGE LABEL (hidden by default)
    # -----------------------
    message_label = tk.Label(form, text="", font=("Arial", 9), bg="white", fg="#ef4444")
    message_label.pack(pady=(10, 0))

    # -----------------------
    # REGISTER FUNCTION
    # -----------------------
    def handle_register():

        username = username_entry.get().strip()
        password = password_entry.get().strip()
        confirm  = confirm_entry.get().strip()

        # ignore placeholder text
        if username == "Choose a username":    username = ""
        if password == "Create a password":   password = ""
        if confirm  == "Confirm your password": confirm = ""

        # basic validation
        if not username or not password or not confirm:
            message_label.config(text="⚠️ Please fill in all fields.", fg="#ef4444")
            return

        if len(username) < 3:
            message_label.config(text="⚠️ Username must be at least 3 characters.", fg="#ef4444")
            return

        if len(password) < 6:
            message_label.config(text="⚠️ Password must be at least 6 characters.", fg="#ef4444")
            return

        if password != confirm:
            message_label.config(text="⚠️ Passwords do not match.", fg="#ef4444")
            confirm_entry.delete(0, tk.END)
            confirm_entry.insert(0, "Confirm your password")
            confirm_entry.config(fg="#94a3b8", show="")
            return

        # try to register
        success = register_user(username, password)

        if success:
            message_label.config(text="✅ Account created! You can now login.", fg="#22c55e")
            print(f"✅ Registered: {username}")

            # reset fields back to placeholders
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            confirm_entry.delete(0, tk.END)

            username_entry.insert(0, "Choose a username")
            password_entry.insert(0, "Create a password")
            confirm_entry.insert(0, "Confirm your password")

            username_entry.config(fg="#94a3b8")
            password_entry.config(fg="#94a3b8", show="")
            confirm_entry.config(fg="#94a3b8", show="")

            # auto close after 1.5 seconds
            window.after(1500, go_back)

        else:
            message_label.config(text="⚠️ Username already taken. Try another.", fg="#ef4444")

    # -----------------------
    # REGISTER BUTTON
    # -----------------------
    register_btn = tk.Button(
        form,
        text="→|  Register",
        font=("Arial", 12, "bold"),
        bg="#22c55e",
        fg="white",
        activebackground="#16a34a",
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        command=handle_register
    )
    register_btn.pack(fill="x", ipady=12, pady=(16, 0))

    # hover effect
    def on_enter(e):
        register_btn.config(bg="#16a34a")

    def on_leave(e):
        register_btn.config(bg="#22c55e")

    register_btn.bind("<Enter>", on_enter)
    register_btn.bind("<Leave>", on_leave)

    # -----------------------
    # BACK TO LOGIN LINK
    # -----------------------

    # GO BACK FUNCTION — defined first before binding
    def go_back():
        window.destroy()
        if on_close:
            on_close()   # shows login window again

    back_frame = tk.Frame(window, bg="white")
    back_frame.pack(pady=(20, 40))

    tk.Label(
        back_frame,
        text="Already have an account? ",
        font=("Arial", 10),
        bg="white",
        fg="#64748b"
    ).pack(side="left")

    back_link = tk.Label(
        back_frame,
        text="Back to Login",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#22c55e",
        cursor="hand2"
    )
    back_link.pack(side="left")
    back_link.bind("<Button-1>", lambda e: go_back())
    window.protocol("WM_DELETE_WINDOW", go_back) # Also handle X button on register window

    # hover effect for back link
    def on_back_enter(e):
        back_link.config(fg="#16a34a")

    def on_back_leave(e):
        back_link.config(fg="#22c55e")

    back_link.bind("<Enter>", on_back_enter)
    back_link.bind("<Leave>", on_back_leave)

    # bind Enter key to register
    window.bind("<Return>", lambda e: handle_register())

    # focus on username field
    username_entry.focus()

    # only call mainloop if standalone
    if not parent:
        window.mainloop()


# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    launch_register()