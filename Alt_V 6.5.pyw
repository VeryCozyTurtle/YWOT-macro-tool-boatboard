import time
import keyboard
import tkinter as tk
import pyautogui
import os
from tkinter import filedialog, messagebox
import threading
from tkinter import messagebox

char_delay = 0.010  # Time between keystrokes
countdown_id = None
file_path = None  # Initialize file_path to None
lines = []
current_line = 0
pause_event = threading.Event()
version = "Alt_v 6.5.10"
lasts_line = False
max_dimension = 100
status_label = None


def estimate_completion_time():
    global file_path, lines, current_line

    if file_path is None:
        return None  # If no file is loaded, return None for estimation

    start_line, end_line = select_lines()

    if end_line is None:
        lines_to_print = [lines[current_line + start_line - 1]]
    else:
        lines_to_print = lines[current_line + start_line - 1: current_line + end_line]

    total_chars = sum(len(line) for line in lines_to_print)
    chars_per_second = 1 / char_delay  # Calculate characters typed per second based on the delay

    time_seconds = total_chars / chars_per_second
    return time_seconds

def select_file():
    return filedialog.askopenfilename(title="Select a Text File", filetypes=[("Text files", "*.txt")])

def select_lines():
    start_line = int(entry_start.get())
    end_line_entry = entry_end.get()

    try:
        end_line = int(end_line_entry) if end_line_entry.isdigit() else None
    except ValueError:
        end_line = None

    return start_line, end_line

def type_content(lines_to_print):
    for line in lines_to_print:
        for char in line.replace('\t', ''):
            if pause_event.is_set():  # Check if the pause event is set
                pause_event.clear()   # Clear the event to allow resuming
                return  # Exit the function to pause/halt printing

            if char == '\n':
                keyboard.press_and_release('enter')
            else:
                keyboard.write(char, delay=char_delay)
                time.sleep(char_delay)  # Wait for the character to be typed

def restart_countdown(delay=True):
    global countdown_id, current_line
    if countdown_id is not None:
        root.after_cancel(countdown_id)
    current_line = 0
    if not delay:  # If delay is set to False, print immediately
        print_content()  # Immediately print without the delay
    else:
        update_countdown_label()

def update_countdown_label(delay_seconds=3):
    global countdown_id, file_path, lines, current_line
    start_line, end_line = select_lines()

    if file_path is None:
        return

    if end_line is None:
        lines_to_print = [lines[current_line + start_line - 1]]
    else:
        lines_to_print = lines[current_line + start_line - 1: current_line + end_line]

    time_estimate = estimate_completion_time()  # Estimate completion time

    root.after(int(delay_seconds * 1000), lambda: type_content(lines_to_print))
    root.title(f"{file_name}  X {file_width}  Y {file_height}  ETA: {time_estimate:.2f} seconds")


def load_new_file():
    global file_path, lines, current_line, lasts_line

    try:
        file_path = select_file()

        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            current_line = 0
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            file_height = len(lines)
            file_width = max(len(line) for line in lines)

            if lasts_line and (file_height > max_dimension or file_width > max_dimension):
                messagebox.showwarning("File Loading Locked", f"File dimensions exceed {max_dimension} characters in either X or Y direction.")
                file_path = None  # Reset file_path if dimensions exceed limits
            else:
                root.title(f"{file_name}  X {file_height}  Y {file_width}")   # Update window title with file name, height, and width

                entry_start.delete(0, tk.END)
                entry_start.insert(0, "1")

                entry_end.delete(0, tk.END)
                entry_end.insert(0, str(file_height))

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def print_content():
    global file_path, lines, current_line

    if file_path is None:
        return

    start_line, end_line = select_lines()

    if end_line is None:
        lines_to_print = [lines[current_line + start_line - 1]]
    else:
        lines_to_print = lines[current_line + start_line - 1: current_line + end_line]

    threading.Thread(target=type_content, args=(lines_to_print,), daemon=True).start()

def pause_printing():
    toggle_hotkey(status_label)
    pause_event.set()  # Set the event to pause printing

def on_closing():
    if messagebox.askokcancel("Quit?", "Close ALT_V?"):
        root.destroy()

hotkey_enabled = True  # Initialize the hotkey flag

def trigger_print():
    if hotkey_enabled:
        restart_countdown(delay=False)  # Trigger immediate printing    
        disable_hotkey()

def toggle_hotkey(label):
    global hotkey_enabled
    hotkey_enabled = not hotkey_enabled  # Toggle the hotkey flag
    if hotkey_enabled:
        label.config(text="Currently Armed")
    else:
        label.config(text="Currently Disabled")

def disable_hotkey():
    global hotkey_enabled
    hotkey_enabled = False
    status_label.config(text="Currently Disabled")



if __name__ == '__main__':
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.title(f"{version}")

    root.attributes('-topmost', True)  # Keep the window on top

    static_box = tk.Frame(root, bd=2, relief=tk.GROOVE)
    static_box.pack(side=tk.TOP, fill=tk.X)

    load_button = tk.Button(static_box, text="Load", command=load_new_file)
    load_button.pack(side=tk.LEFT, padx=10)

    label_start = tk.Label(static_box, text="Line")
    label_start.pack(side=tk.LEFT, padx=5)

    entry_start = tk.Entry(static_box, width=5)
    entry_start.pack(side=tk.LEFT, padx=5)

    label_to = tk.Label(static_box, text=" through ")
    label_to.pack(side=tk.LEFT)

    entry_end = tk.Entry(static_box, width=5)
    entry_end.pack(side=tk.LEFT, padx=5)

    countdown_label = tk.Label(static_box, text="")
    countdown_label.pack(side=tk.LEFT, padx=5)

    print_button = tk.Button(static_box, text="P rint", command=restart_countdown)
    print_button.pack(side=tk.RIGHT, padx=10)

    pause_button = tk.Button(static_box, text="Halt", command=pause_printing)
    pause_button.pack(side=tk.RIGHT, padx=10)

    keyboard.add_hotkey('p', trigger_print)  # Set hotkey for instant printing

    # Bind the toggle_hotkey function to the toggle_button
    toggle_button = tk.Button(static_box, text="Toggle Hotkey", command=lambda: toggle_hotkey(status_label))
    toggle_button.pack(side=tk.RIGHT, padx=10)

    status_label = tk.Label(static_box, text="Currently Armed")
    status_label.pack(side=tk.RIGHT, padx=10)

    root.mainloop()