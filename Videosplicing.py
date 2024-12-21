import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re

def get_frame_count(video_path):
    # Use FFmpeg to get the total frame count of the video
    command = f'ffmpeg -i "{video_path}"'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr = process.communicate()[1].decode('utf-8')
    
    # Look for frame count in the output
    frame_count_match = re.search(r'(\d+) fps', stderr)
    if frame_count_match:
        return int(frame_count_match.group(1))  # Return the number of frames
    return 0

def run_ffmpeg(video_path, output_folder, format_option, frame_interval, use_original_fps):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # Create the folder if it doesn't exist

    # Construct the FFmpeg command based on user selection
    if use_original_fps:
        ffmpeg_command = f'ffmpeg -i "{video_path}" "{output_folder}/frame_%04d.{format_option}"'
    else:
        ffmpeg_command = f'ffmpeg -i "{video_path}" -vf "fps={frame_interval}" "{output_folder}/frame_%04d.{format_option}"'

    # Get total frame count
    total_frames = get_frame_count(video_path)
    if total_frames == 0:
        messagebox.showerror("Error", "Could not determine frame count.")
        return

    try:
        messagebox.showinfo("Processing", "Extraction started. Please wait...")
        
        # Run the command and update progress
        process = subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Monitor the process
        while True:
            output = process.stderr.readline()
            if output == b"" and process.poll() is not None:
                break
            if output:
                # Print FFmpeg output (optional)
                print(output.strip())  # Optional for debugging
                # Simulate progress update
                progress_bar['value'] += 1  # Increment progress
                root.update_idletasks()
        
        process.wait()
        messagebox.showinfo("Success", "Frames extracted successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to extract frames: {e}")

def select_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])
    if file_path:
        video_entry.delete(0, tk.END)
        video_entry.insert(0, file_path)

def select_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder_path)

def extract_frames():
    video_path = video_entry.get()
    output_folder = output_entry.get()
    format_option = format_var.get()
    frame_interval = frame_rate_var.get()
    use_original_fps = original_fps_var.get()

    if not video_path or not output_folder:
        messagebox.showwarning("Missing Information", "Please select both a video file and output folder.")
    else:
        # Reset progress bar
        progress_bar['value'] = 0
        # Start frame extraction with the progress bar
        run_ffmpeg(video_path, output_folder, format_option, frame_interval, use_original_fps)

# GUI setup
root = tk.Tk()
root.title("Frame Extractor")
root.geometry("550x350")

# Video file input
tk.Label(root, text="Select Video File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
video_entry = tk.Entry(root, width=50)
video_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_video, bg='darkgreen', fg='white').grid(row=0, column=2, padx=5, pady=5)

# Output folder input
tk.Label(root, text="Select Output Folder:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_output_folder, bg='darkgreen', fg='white').grid(row=1, column=2, padx=5, pady=5)

# Frame rate option
tk.Label(root, text="Frame Interval (fps):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
frame_rate_var = tk.StringVar(value="1")
frame_rate_entry = tk.Entry(root, textvariable=frame_rate_var, width=5)
frame_rate_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

# Original frame rate option
original_fps_var = tk.BooleanVar()
original_fps_check = tk.Checkbutton(root, text="Use Original Frame Rate", variable=original_fps_var)
original_fps_check.grid(row=2, column=2, padx=5, pady=5, sticky="w")

# Format option
tk.Label(root, text="Frame Format:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
format_var = tk.StringVar(value="png")
format_menu = ttk.Combobox(root, textvariable=format_var, values=["png", "jpg"], width=5)
format_menu.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=5, column=0, columnspan=3, padx=5, pady=10)

# Extract frames button
tk.Button(root, text="Extract Frames", command=extract_frames, width=20, bg='darkgreen', fg='white').grid(row=4, column=1, pady=20)

root.mainloop()