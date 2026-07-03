import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os


# ---------- Helper ----------
def format_time(seconds):
    """Convert seconds to hh:mm:ss.mmm"""
    msec = int((seconds % 1) * 1000)
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}.{msec:03}"


# ---------- Video Player ----------
class VideoPlayer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Cannot open video:\n{video_path}")
            return

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0

        # --- State ---
        self.paused = False
        self.current_frame = 0
        self.playback_speed = 1.0
        self.seeking = False

        # Max displayed video size
        self.max_display_w = 1100
        self.max_display_h = 650

        # GUI setup
        self.root = tk.Tk()
        self.root.title(os.path.basename(video_path))
        self.root.geometry("1280x940")
        self.root.minsize(1000, 780)

        # ---------- Top controls ----------
        top_container = tk.Frame(self.root)
        top_container.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        # Speed control layout
        control_frame = tk.Frame(top_container)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # Reverse side
        reverse_frame = tk.Frame(control_frame)
        reverse_frame.pack(side=tk.LEFT, padx=10)
        for spd in [8.0, 4.0, 2.0, 1.0]:
            tk.Button(
                reverse_frame,
                text=f"⏪ -{spd}x",
                command=lambda s=-spd: self.set_speed(s),
                font=("Arial", 10),
                padx=6,
                pady=4
            ).pack(side=tk.LEFT, padx=2)

        # Speed label
        self.speed_label = tk.Label(
            control_frame,
            text="Speed: ▶ 1.0x",
            font=("Consolas", 11)
        )
        self.speed_label.pack(side=tk.LEFT, expand=True)

        # Forward side
        forward_frame = tk.Frame(control_frame)
        forward_frame.pack(side=tk.RIGHT, padx=10)
        for spd in [0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 16.0]:
            tk.Button(
                forward_frame,
                text=f"▶ {spd}x",
                command=lambda s=spd: self.set_speed(s),
                font=("Arial", 10),
                padx=6,
                pady=4
            ).pack(side=tk.LEFT, padx=2)

        # Time/frame info
        self.text = tk.Label(self.root, text="", font=("Consolas", 13))
        self.text.pack(side=tk.TOP, pady=(2, 6))

        # ---------- Jump controls ----------
        jump_frame = tk.Frame(self.root)
        jump_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 8))

        tk.Label(jump_frame, text="Go to frame:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.frame_entry = tk.Entry(jump_frame, width=12, font=("Consolas", 11))
        self.frame_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(
            jump_frame,
            text="Jump Frame",
            command=self.jump_to_frame,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(jump_frame, text="Go to time [s]:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.time_entry = tk.Entry(jump_frame, width=12, font=("Consolas", 11))
        self.time_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(
            jump_frame,
            text="Jump Time",
            command=self.jump_to_time,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        self.frame_entry.bind("<Return>", lambda e: self.jump_to_frame())
        self.time_entry.bind("<Return>", lambda e: self.jump_to_time())

        # Progress bar
        self.progress_canvas = tk.Canvas(
            self.root,
            height=20,
            bg="lightgray",
            highlightthickness=0
        )
        self.progress_canvas.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 10))
        self.progress_bar = self.progress_canvas.create_rectangle(0, 0, 0, 20, fill="red")
        self.progress_handle = self.progress_canvas.create_line(0, 0, 0, 20, fill="black", width=2)
        self.progress_canvas.bind("<Button-1>", self.seek_click)
        self.progress_canvas.bind("<B1-Motion>", self.seek_drag)

        # Video area
        self.label = tk.Label(self.root, bg="black")
        self.label.pack(side=tk.TOP, expand=True, pady=5)

        # Helper text
        self.help_label = tk.Label(
            self.root,
            text="Space = Pause/Play   |   Left/Right = Frame step   |   Q/A = Speed +/-   |   Enter in boxes = Jump",
            font=("Arial", 10),
            fg="gray25"
        )
        self.help_label.pack(side=tk.TOP, pady=(4, 8))

        # --- Key bindings ---
        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("<Right>", self.next_frame)
        self.root.bind("<Left>", self.prev_frame)
        self.root.bind("q", lambda e: self.change_speed(0.5))
        self.root.bind("a", lambda e: self.change_speed(-0.5))

        # Cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.play_video()
        self.root.mainloop()

    # --- Cleanup ---
    def on_close(self):
        if self.cap is not None:
            self.cap.release()
        self.root.destroy()

    # --- Playback controls ---
    def set_speed(self, speed):
        if speed == 0:
            speed = 0.1
        self.playback_speed = max(-16.0, min(speed, 16.0))
        dir_symbol = "▶" if self.playback_speed > 0 else "⏪"
        self.speed_label.config(text=f"Speed: {dir_symbol} {abs(self.playback_speed):.1f}x")

    def change_speed(self, delta):
        self.set_speed(self.playback_speed + delta)

    def toggle_pause(self, event=None):
        self.paused = not self.paused

    def next_frame(self, event=None):
        self.paused = True
        self.show_frame(self.current_frame + 1)

    def prev_frame(self, event=None):
        self.paused = True
        self.show_frame(self.current_frame - 1)

    def seek_click(self, event):
        width = max(1, self.progress_canvas.winfo_width())
        frac = max(0, min(1, event.x / width))
        frame = int(frac * self.total_frames)
        self.show_frame(frame)

    def seek_drag(self, event):
        width = max(1, self.progress_canvas.winfo_width())
        frac = max(0, min(1, event.x / width))
        frame = int(frac * self.total_frames)
        self.paused = True
        self.show_frame(frame)

    def jump_to_frame(self):
        value = self.frame_entry.get().strip()
        if not value:
            return
        try:
            frame_idx = int(value)
        except ValueError:
            messagebox.showwarning("Invalid input", "Please enter a valid integer frame number.")
            return

        frame_idx = max(0, min(frame_idx, self.total_frames - 1))
        self.paused = True
        self.show_frame(frame_idx)
        self.frame_entry.delete(0, tk.END)
        self.frame_entry.insert(0, str(frame_idx))

    def jump_to_time(self):
        value = self.time_entry.get().strip()
        if not value:
            return
        try:
            time_sec = float(value)
        except ValueError:
            messagebox.showwarning("Invalid input", "Please enter a valid time in seconds.")
            return

        time_sec = max(0.0, min(time_sec, self.duration))
        frame_idx = int(time_sec * self.fps) if self.fps > 0 else 0
        frame_idx = max(0, min(frame_idx, self.total_frames - 1))

        self.paused = True
        self.show_frame(frame_idx)
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, f"{time_sec:.3f}")

    # --- Frame rendering ---
    def show_frame(self, frame_idx):
        if self.total_frames <= 0:
            return

        if frame_idx < 0:
            frame_idx = 0
        elif frame_idx >= self.total_frames:
            frame_idx = self.total_frames - 1

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        if not ret:
            return

        self.current_frame = frame_idx

        # Convert to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

        # Resize while keeping aspect ratio
        w, h = img.size
        scale = min(self.max_display_w / w, self.max_display_h / h, 1.0)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))

        if scale < 1.0:
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        imgtk = ImageTk.PhotoImage(image=img)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)

        time_sec = self.current_frame / self.fps if self.fps > 0 else 0
        formatted_time = format_time(time_sec)
        self.text.config(
            text=f"Frame: {self.current_frame}/{self.total_frames}    "
                 f"Time: {time_sec:.3f}s ({formatted_time})"
        )

        # Keep inputs in sync
        self.frame_entry.delete(0, tk.END)
        self.frame_entry.insert(0, str(self.current_frame))
        d
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, f"{time_sec:.3f}")

        width = max(1, self.progress_canvas.winfo_width())
        frac = self.current_frame / self.total_frames if self.total_frames > 0 else 0
        x = frac * width
        self.progress_canvas.coords(self.progress_bar, 0, 0, x, 20)
        self.progress_canvas.coords(self.progress_handle, x, 0, x, 20)

    # --- Main loop ---
    def play_video(self):
        if not self.root.winfo_exists():
            return

        if not self.paused:
            self.show_frame(self.current_frame)

            step = int(abs(self.playback_speed))
            step = max(1, step)

            if self.playback_speed > 0:
                self.current_frame += step
                if self.current_frame >= self.total_frames:
                    self.current_frame = 0
            else:
                self.current_frame -= step
                if self.current_frame < 0:
                    self.current_frame = self.total_frames - 1

        if self.fps > 0:
            delay = int(1000 / (self.fps * max(abs(self.playback_speed), 0.1)))
        else:
            delay = 30

        self.root.after(max(1, delay), self.play_video)


# ---------- Launcher ----------
class LauncherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Player Launcher")
        self.root.geometry("450x220")
        self.root.minsize(420, 220)

        tk.Label(
            self.root,
            text="Select or confirm a video file",
            font=("Arial", 14)
        ).pack(pady=20)

        tk.Button(
            self.root,
            text="Browse Video",
            command=self.open_video,
            font=("Arial", 12),
            width=20
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Play Default Video",
            command=self.play_default,
            font=("Arial", 12),
            width=20
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Exit",
            command=self.root.quit,
            font=("Arial", 12),
            width=20
        ).pack(pady=10)

        self.root.mainloop()

    def open_video(self):
        default_dir = os.path.dirname(DEFAULT_VIDEO_PATH)
        path = filedialog.askopenfilename(
            title="Select a Video File",
            initialdir=default_dir,
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All Files", "*.*")]
        )
        if path:
            self.root.destroy()
            VideoPlayer(path)

    def play_default(self):
        if os.path.exists(DEFAULT_VIDEO_PATH):
            self.root.destroy()
            VideoPlayer(DEFAULT_VIDEO_PATH)
        else:
            messagebox.showerror("Error", f"Default video not found:\n{DEFAULT_VIDEO_PATH}")


# ---------- Default path ----------
DEFAULT_VIDEO_PATH = r"VALIDMP4FILECHOSENHERE.mp4"

# ---------- Run ----------
if __name__ == "__main__":
    LauncherApp()