import tkinter as tk
from PIL import Image, ImageTk
from database import get_training_sessions, get_letter_accuracy
import os

print("📊 Loading Progress Window...")


# -----------------------
# LAUNCH PROGRESS (ENTRY)
# -----------------------
def launch_progress(username="Guest"):

    # -----------------------
    # TKINTER INIT
    # -----------------------
    root = tk.Toplevel()
    root.title("HandTalk - Progress")

    root.resizable(False, False)
    root.grab_set()  # lock focus

    # center window
    window_width  = 540
    window_height = 680

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

    # -----------------------
    # HEADER with ICON
    # -----------------------
    header_frame = tk.Frame(root, bg="white")
    header_frame.pack(fill="x", padx=30, pady=(30, 0))

    # Icon
    icon_frame = tk.Frame(header_frame, bg="#22c55e", width=50, height=50)
    icon_frame.pack(side="left", padx=(0, 15))
    icon_frame.pack_propagate(False)

    tk.Label(
        icon_frame,
        text="📊",
        font=("Arial", 24),
        bg="#22c55e"
    ).place(relx=0.5, rely=0.5, anchor="center")

    # Title text
    title_text_frame = tk.Frame(header_frame, bg="white")
    title_text_frame.pack(side="left")

    tk.Label(
        title_text_frame,
        text="Your Progress",
        font=("Arial", 22, "bold"),
        bg="white",
        fg="#1e293b",
        anchor="w"
    ).pack(anchor="w")

    tk.Label(
        title_text_frame,
        text=username,
        font=("Arial", 11),
        bg="white",
        fg="#64748b",
        anchor="w"
    ).pack(anchor="w")

    # -----------------------
    # TAB BUTTONS
    # -----------------------
    tab_frame = tk.Frame(root, bg="white")
    tab_frame.pack(fill="x", padx=30, pady=(20, 0))

    def show_sessions():
        accuracy_frame.pack_forget()
        session_frame.pack(fill="both", expand=True, padx=30, pady=(10, 0))
        btn_sessions.config(bg="#22c55e", fg="white")
        btn_accuracy.config(bg="#f1f5f9", fg="#64748b")

    def show_accuracy():
        session_frame.pack_forget()
        accuracy_frame.pack(fill="both", expand=True, padx=30, pady=(10, 0))
        btn_accuracy.config(bg="#22c55e", fg="white")
        btn_sessions.config(bg="#f1f5f9", fg="#64748b")

    btn_sessions = tk.Button(
        tab_frame,
        text="Session History",
        font=("Arial", 11, "bold"),
        bg="#22c55e",
        fg="white",
        relief="flat",
        cursor="hand2",
        command=show_sessions,
        padx=20,
        pady=8
    )
    btn_sessions.pack(side="left", padx=(0, 8))

    btn_accuracy = tk.Button(
        tab_frame,
        text="Letter Accuracy",
        font=("Arial", 11, "bold"),
        bg="#f1f5f9",
        fg="#64748b",
        relief="flat",
        cursor="hand2",
        command=show_accuracy,
        padx=20,
        pady=8
    )
    btn_accuracy.pack(side="left")

    # -----------------------
    # CONTENT CONTAINER
    # -----------------------
    content_container = tk.Frame(root, bg="white")
    content_container.pack(fill="both", expand=True)

    # -----------------------
    # SESSION HISTORY FRAME
    # -----------------------
    session_frame = tk.Frame(content_container, bg="white")

    sessions = get_training_sessions(username)

    if not sessions:
        empty_frame = tk.Frame(session_frame, bg="#f8fafc", relief="solid", bd=1)
        empty_frame.pack(fill="both", expand=True, pady=20)
        
        tk.Label(
            empty_frame,
            text="No training sessions yet",
            font=("Arial", 12, "bold"),
            bg="#f8fafc",
            fg="#64748b"
        ).pack(pady=(40, 5))
        
        tk.Label(
            empty_frame,
            text="Complete a training session to see results here!",
            font=("Arial", 10),
            bg="#f8fafc",
            fg="#94a3b8"
        ).pack(pady=(0, 40))

    else:
        # Header row
        header = tk.Frame(session_frame, bg="#f1f5f9", height=40)
        header.pack(fill="x", pady=(0, 2))
        header.pack_propagate(False)

        tk.Label(header, text="Score", font=("Arial", 10, "bold"), bg="#f1f5f9", fg="#475569", width=8).pack(side="left", padx=8, pady=10)
        tk.Label(header, text="Total", font=("Arial", 10, "bold"), bg="#f1f5f9", fg="#475569", width=8).pack(side="left", padx=8, pady=10)
        tk.Label(header, text="Accuracy", font=("Arial", 10, "bold"), bg="#f1f5f9", fg="#475569", width=10).pack(side="left", padx=8, pady=10)
        tk.Label(header, text="Timestamp", font=("Arial", 10, "bold"), bg="#f1f5f9", fg="#475569", width=20).pack(side="left", padx=8, pady=10)

        # Scrollable session rows
        canvas = tk.Canvas(session_frame, height=350, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(session_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


        # Session rows
        for idx, (score, total, timestamp) in enumerate(sessions):
            pct = int((score / total) * 100) if total > 0 else 0

            # Color code accuracy
            if pct >= 70:
                color = "#22c55e"
                bg_color = "#f0fdf4"
            elif pct >= 40:
                color = "#f97316"
                bg_color = "#fff7ed"
            else:
                color = "#ef4444"
                bg_color = "#fef2f2"

            row = tk.Frame(scroll_frame, bg="white", relief="solid", bd=1)
            row.pack(fill="x", pady=1)

            tk.Label(row, text=str(score), font=("Arial", 11), bg="white", fg="#1e293b", width=8).pack(side="left", padx=8, pady=12)
            tk.Label(row, text=str(total), font=("Arial", 11), bg="white", fg="#1e293b", width=8).pack(side="left", padx=8, pady=12)
            
            # Accuracy badge
            acc_label = tk.Label(row, text=f"{pct}%", font=("Arial", 10, "bold"), bg=bg_color, fg=color, width=8)
            acc_label.pack(side="left", padx=8, pady=8)
            
            tk.Label(row, text=str(timestamp), font=("Arial", 10), bg="white", fg="#64748b", width=20).pack(side="left", padx=8, pady=12)

    # -----------------------
    # LETTER ACCURACY FRAME
    # -----------------------
    accuracy_frame = tk.Frame(content_container, bg="white")

    letters_data = get_letter_accuracy(username)

    if not letters_data:
        empty_frame = tk.Frame(accuracy_frame, bg="#f8fafc", relief="solid", bd=1)
        empty_frame.pack(fill="both", expand=True, pady=20)
        
        tk.Label(
            empty_frame,
            text="No letter data yet",
            font=("Arial", 12, "bold"),
            bg="#f8fafc",
            fg="#64748b"
        ).pack(pady=(40, 5))
        
        tk.Label(
            empty_frame,
            text="Complete a training session to see accuracy here!",
            font=("Arial", 10),
            bg="#f8fafc",
            fg="#94a3b8"
        ).pack(pady=(0, 40))

    else:
        # Scrollable area for letters
        canvas = tk.Canvas(accuracy_frame, height=400, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(accuracy_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Draw each letter row
        for letter, correct, attempts in letters_data:
            pct = int((correct / attempts) * 100) if attempts > 0 else 0
            
            # Color based on accuracy
            if pct >= 70:
                color = "#22c55e"
                bg_color = "#f0fdf4"
            elif pct >= 40:
                color = "#f97316"
                bg_color = "#fff7ed"
            else:
                color = "#ef4444"
                bg_color = "#fef2f2"

            row = tk.Frame(scroll_frame, bg=bg_color, relief="solid", bd=1)
            row.pack(fill="x", pady=3, padx=2)

            # Letter badge
            letter_badge = tk.Frame(row, bg="#3b82f6", width=40, height=40)
            letter_badge.pack(side="left", padx=12, pady=8)
            letter_badge.pack_propagate(False)
            
            tk.Label(
                letter_badge,
                text=letter,
                font=("Arial", 16, "bold"),
                bg="#3b82f6",
                fg="white"
            ).place(relx=0.5, rely=0.5, anchor="center")

            # Progress bar container
            bar_container = tk.Frame(row, bg="white")
            bar_container.pack(side="left", fill="x", expand=True, padx=12, pady=8)

            # Fraction text
            tk.Label(
                bar_container,
                text=f"{correct} / {attempts}",
                font=("Arial", 9),
                bg="white",
                fg="#64748b"
            ).pack(anchor="w")

            # Progress bar
            bar_bg = tk.Frame(bar_container, bg="#e2e8f0", height=8, width=250)
            bar_bg.pack(fill="x", pady=(2, 0))
            bar_bg.pack_propagate(False)

            bar_width = int(250 * pct / 100)
            tk.Frame(bar_bg, bg=color, height=8, width=max(0, bar_width)).pack(side="left")

            # Percentage badge
            pct_label = tk.Label(
                row,
                text=f"{pct}%",
                font=("Arial", 11, "bold"),
                bg=bg_color,
                fg=color,
                width=8
            )
            pct_label.pack(side="left", padx=12, pady=8)

    # -----------------------
    # CLOSE BUTTON
    # -----------------------
    footer = tk.Frame(root, bg="white")
    footer.pack(fill="x", padx=30, pady=(15, 25))

    # Separator
    tk.Frame(footer, bg="#e2e8f0", height=1).pack(fill="x", pady=(0, 15))

    close_btn = tk.Button(
        footer,
        text="Close",
        font=("Arial", 11, "bold"),
        bg="#f1f5f9",
        fg="#64748b",
        activebackground="#e2e8f0",
        relief="flat",
        cursor="hand2",
        command=root.destroy,
        padx=40,
        pady=10
    )
    close_btn.pack()

    # Hover effect
    def on_close_enter(e):
        close_btn.config(bg="#e2e8f0")

    def on_close_leave(e):
        close_btn.config(bg="#f1f5f9")

    close_btn.bind("<Enter>", on_close_enter)
    close_btn.bind("<Leave>", on_close_leave)

    # Show sessions tab by default
    show_sessions()

    root.mainloop()


# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    launch_progress()