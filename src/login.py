import tkinter as tk
from PIL import Image, ImageTk
from database import login_user
import os

print("🔐 Loading Login Window...")


# -----------------------
# LAUNCH LOGIN (ENTRY)
# -----------------------
def launch_login():

    # -----------------------
    # TKINTER INIT
    # -----------------------
    root = tk.Tk() # Create window
    root.title("HandTalk - Login")
    root.resizable(False, False) # Window size locked

    # center window
    window_width  = 420
    window_height = 600

    screen_w = root.winfo_screenwidth() # Gets monitor's WIDTH for example 1920 now screen_w = 1920
    screen_h = root.winfo_screenheight() # Gets monitor's HEIGHT for example 420 now screeh_h = 420

    x = (screen_w // 2) - (window_width  // 2) # Floor division example Move right/left depends on calculation
    y = (screen_h // 2) - (window_height // 2) # Floor division Move down depends on calculation

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg="white")

    # Set window icon
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__)) # Gets folder of a file ex: C:\Handtalk\src\login.py -> C:\Handtalk\src
        parent_dir = os.path.dirname(script_dir) # Get parent folder ex: C:\Handtalk\src -> "C:\\Handtalk"
        icon_path = os.path.join(parent_dir, "Assets", "Logo", "highfive-removebg-preview.ico") # Safely builds file paths instead of manually writing ex: C:\Handtalk\Assets\Logo\highfive.ico
        root.iconbitmap(icon_path) # Set Logo icon
    except Exception as e:
        print(f"⚠️ Could not set window icon: {e}")

    # -----------------------
    # LOGO ICON (green square + hand PNG)
    # -----------------------
    icon_frame = tk.Frame(root, bg="#22c55e", width=80, height=80)
    icon_frame.pack(pady=(50, 14))
    icon_frame.pack_propagate(False)

    # Load and resize hand PNG from assets/images folder
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir) # Go up one level to C:\Handtalk
        hand_path = os.path.join(parent_dir, "Assets", "Images", "highfive-removebg-preview.png")
        
        hand_img = Image.open(hand_path) # Load/Open the file image from hand_path
        hand_img = hand_img.resize((50, 50), Image.Resampling.LANCZOS)  # Resize to fit inside the green square 50pixels width and 50pixels height and LANCZOS is quality of sizing like Nearest, Bilinear
        hand_photo = ImageTk.PhotoImage(hand_img) # Converts PIL image into something Tkinter understands cause Tk cant directly use hand_img that's why it need conversion from hand_photo
        
        icon_label = tk.Label(
            icon_frame,
            image=hand_photo,
            bg="#22c55e"
        )
        icon_label.image = hand_photo  # Keeps image stored in memory to prevent garbage collection cause sometimes python does that
        icon_label.place(relx=0.5, rely=0.5, anchor="center") # Positions the widget
    except Exception as e:
        print(f"⚠️ Could not load hand image: {e}")

        # Fallback to text if image fails
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
        root,
        text="HandTalk",
        font=("Arial", 26, "bold"),
        bg="white",
        fg="#1e293b"
    ).pack(pady=(0, 6)) # So there is space under "HandTalk"

    tk.Label(
        root, # Affects everything
        text="Sign in to continue",
        font=("Arial", 11),
        bg="white",
        fg="#64748b"
    ).pack(pady=(0, 30))

    # -----------------------
    # FORM FRAME
    # -----------------------
    form = tk.Frame(root, bg="white") # Creates a container (like a box) for Username and Password
    form.pack(padx=40, fill="x")

    # -----------------------
    # USERNAME FIELD
    # -----------------------
    tk.Label(
        form, # Affects only a grouped of widgets
        text="Username",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#334155",
        anchor="w" # Align text to the LEFT 
    ).pack(fill="x", pady=(0, 6))

    username_entry = tk.Entry( # Creates input box tk.Entry
        form,
        font=("Arial", 11),
        relief="solid",
        bd=1,
        fg="#94a3b8"
    )
    username_entry.pack(fill="x", ipady=10) # Place adjustment
    username_entry.insert(0, "Enter your username")

    def on_username_focus_in(e): # Runs when user clicks inside entry box
        if username_entry.get() == "Enter your username":
            username_entry.delete(0, tk.END) # Delete text
            username_entry.config(fg="#1e293b")

    def on_username_focus_out(e): # Runs when user clicks outside box
        if not username_entry.get(): # If box is empty
            username_entry.insert(0, "Enter your username") # Put placeholder back
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

    password_entry = tk.Entry( # Creates input box tk.Entry
        form,
        font=("Arial", 11),
        relief="solid",
        bd=1,
        fg="#94a3b8"
    )
    password_entry.pack(fill="x", ipady=10)
    password_entry.insert(0, "Enter your password")

   # -----------------------
    # PASSWORD FIELD PLACEHOLDER STATE
    # use a flag instead of checking text content
    # -----------------------
    password_is_placeholder = [True]  # list so it can be modified inside nested functions

    def on_password_focus_in(e): # Runs when user clicks inside entry box
        if password_is_placeholder[0]:
            password_entry.delete(0, tk.END)
            password_entry.config(fg="#1e293b", show="*")
            password_is_placeholder[0] = False

    def on_password_focus_out(e): # Runs when user clicks outside box
        if not password_entry.get():
            password_entry.insert(0, "Enter your password")
            password_entry.config(fg="#94a3b8", show="")
            password_is_placeholder[0] = True

    password_entry.bind("<FocusIn>",  on_password_focus_in)
    password_entry.bind("<FocusOut>", on_password_focus_out)

    # -----------------------
    # ERROR LABEL (hidden by default) just to add space between password field and login btn
    # -----------------------
    error_label = tk.Label(
        form,
        text="",
        font=("Arial", 9),
        bg="white",
        fg="#ef4444"
    )
    error_label.pack(pady=(10, 0))

    # -----------------------
    # LOGIN FUNCTION
    # -----------------------
    def handle_login():

        username = username_entry.get().strip()
        password = password_entry.get().strip()

        # ignore placeholder text si if user enter nothing it will not return "Enter your username/password" only  "" empty
        if username == "Enter your username": 
            username = ""
        if password == "Enter your password":
            password = ""

        # basic validation
        if not username or not password: # Check if both are empty 
            error_label.config(text="⚠️ Please fill in all fields.")
            return

        # check database
        result = login_user(username, password)

        if result:
            print(f"✅ Login success: {username}") # Print in terminal
            root.destroy()
            open_menu(username)

        else:
            error_label.config(text="⚠️ Invalid username or password.")
            password_entry.delete(0, tk.END) # Reset password field
            password_entry.insert(0, "Enter your password") 
            password_entry.config(fg="#94a3b8", show="")
            password_is_placeholder[0] = True  # ← reset the flag
            
            # Click outside (root.focus) Click back inside (password_entry.focus) like refreshing a broken input field to prevent bugs
            root.focus()                        # move focus away
            password_entry.focus()              # move focus back — triggers focus_in

    # -----------------------
    # LOGIN BUTTON
    # -----------------------
    login_btn = tk.Button(
        form,
        text="→|  Login",
        font=("Arial", 12, "bold"),
        bg="#22c55e",
        fg="white",
        activebackground="#16a34a", # Color when button is CLICKED
        activeforeground="white", # Text color when CLICKED
        relief="flat", # Removes 3D border look
        cursor="hand2", # Change cursor when hovering to the button
        command=handle_login # Run the handle_login function
    )
    login_btn.pack(fill="x", ipady=12, pady=(16, 0))

    # hover effect
    def on_enter(e):
        login_btn.config(bg="#16a34a")

    def on_leave(e):
        login_btn.config(bg="#22c55e")

    login_btn.bind("<Enter>", on_enter) # When mouse enter run 
    login_btn.bind("<Leave>", on_leave) # When mouse leave

    # -----------------------
    # REGISTER LINK
    # -----------------------
    def open_register():
        from register import launch_register # Import register window function
        root.withdraw() # Hide Register window 
        launch_register(root, on_close=root.deiconify) # Show login again when register closes
    register_frame = tk.Frame(root, bg="white")
    register_frame.pack(pady=(24, 40))

    tk.Label(
        register_frame,
        text="Don't have an account? ",
        font=("Arial", 10),
        bg="white",
        fg="#64748b"
    ).pack(side="left")

    register_link = tk.Label(
        register_frame,
        text="Register here",
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#22c55e",
        cursor="hand2"
    )
    register_link.pack(side="left")
    register_link.bind("<Button-1>", lambda e: open_register()) # This is a shortcut function that catches the event but ignores it so your login function can run normally

    # hover effect for register link
    def on_reg_enter(e):
        register_link.config(fg="#16a34a")

    def on_reg_leave(e):
        register_link.config(fg="#22c55e")

    register_link.bind("<Enter>", on_reg_enter)
    register_link.bind("<Leave>", on_reg_leave)

    # bind Enter key to login
    root.bind("<Return>", lambda e: handle_login()) # This is a shortcut function that catches the event but ignores it so your login function can run normally

    # focus on username field
    username_entry.focus()

    root.mainloop() # Starts the program loop cause IF you dont have this Run program → finish → close window IF have this Run program → keep listening forever


# -----------------------
# OPEN MENU AFTER LOGIN
# -----------------------
def open_menu(username):
    import importlib.util # used to run for ex: menu.py without normal import menu
    import os
    import traceback # Prints FULL error details (debug info)

    print(f"🚀 Opening HandTalk for: {username}")

    base_dir  = os.path.dirname(os.path.abspath(__file__))
    menu_path = os.path.join(base_dir, "menu.py") # C:\Handtalk\src + menu.py -> C:\Handtalk\src\menu.py

    try:
        spec        = importlib.util.spec_from_file_location("menu", menu_path) # Create a blueprint to load menu.py and call it 'menu' in memory
        menu_module = importlib.util.module_from_spec(spec) # Prepares menu.py to run
        spec.loader.exec_module(menu_module) # Runs menu.py code

        menu_module.launch_menu(username) # Pass the User's name to the launch_menu function 

    except Exception as e:
        print("❌ Menu Error:", e)
        traceback.print_exc() # Print Full errors
        input("Press Enter to close...")


# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    launch_login()