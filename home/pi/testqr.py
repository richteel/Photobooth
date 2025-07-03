#!/usr/bin/env python3
"""
Tkinter Keyboard Input Test - Displays all keyboard input including special characters
This app helps test if barcode scanners and other input devices work with tkinter.
"""

import tkinter as tk
from tkinter import scrolledtext
import time
# import subprocess

class KeyboardTester(tk.Tk):
    """Tkinter application to test keyboard input and special characters."""

    def __init__(self):
        super().__init__()

        self.title("Keyboard Input Tester - Barcode Scanner Test")
        self.geometry("800x600")
        self.configure(bg="white")

        # Make window stay on top for testing
        self.attributes("-topmost", True)

        # QR code detection
        self.qr_buffer = ""

        # Create GUI components
        self.create_widgets()

        # Bind all possible keyboard events
        self.bind_keyboard_events()

        # Focus on the window so it receives keyboard events
        self.focus_set()

        # Counter for events
        self.event_counter = 0

    def create_widgets(self):
        """Create the GUI widgets."""
        # Title label
        title_label = tk.Label(
            self,
            text="Keyboard Input Tester",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title_label.pack(pady=10)

        # Instructions
        instructions = tk.Label(
            self,
            text="Focus this window and type or scan barcodes.\n" +
                 "All keyboard input will be displayed below.\n\n" +
                 "Note: Keycodes are hardware scan codes (not ASCII).\n" +
                 "QR/Barcode scanners typically only send printable text + Return.",
            font=("Arial", 10),
            bg="white",
            justify=tk.LEFT
        )
        instructions.pack(pady=5)

        # Frame for controls
        controls_frame = tk.Frame(self, bg="white")
        controls_frame.pack(pady=10)

        # Clear button
        clear_btn = tk.Button(
            controls_frame,
            text="Clear Log",
            command=self.clear_log,
            font=("Arial", 10)
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Test buttons for known key combinations
        test_esc_btn = tk.Button(
            controls_frame,
            text="Test <Esc> Bind",
            command=self.test_escape_function,
            font=("Arial", 10),
            bg="lightblue"
        )
        test_esc_btn.pack(side=tk.LEFT, padx=5)

        test_ctrl_q_btn = tk.Button(
            controls_frame,
            text="Test <Ctrl>+Q Bind",
            command=self.test_ctrl_q_function,
            font=("Arial", 10),
            bg="lightgreen"
        )
        test_ctrl_q_btn.pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = tk.Label(
            self,
            text="Ready - Waiting for keyboard input...",
            font=("Arial", 10),
            bg="white",
            fg="blue"
        )
        self.status_label.pack(pady=5)

        # Text area for displaying input
        self.text_area = scrolledtext.ScrolledText(
            self,
            width=80,
            height=25,
            font=("Courier", 10),
            bg="black",
            fg="lime",
            wrap=tk.WORD
        )
        self.text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Initial message
        self.text_area.insert(tk.END, "=== Keyboard Input Tester Started ===\n")
        self.text_area.insert(tk.END, "Time: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
        self.text_area.insert(tk.END, "KEYCODE INFO:\n")
        self.text_area.insert(tk.END, "- 'keycode' = Hardware scan code (Linux/X11 keycode)\n")
        self.text_area.insert(tk.END, "- 'ascii' = ASCII value (for printable chars)\n")
        self.text_area.insert(tk.END, "- QR/Barcode scanners send text + Return key\n")
        self.text_area.insert(tk.END, "- Test <Esc> and <Ctrl>+Q manually on keyboard\n\n")

    def bind_keyboard_events(self):
        """Bind all keyboard events to capture input."""
        # Bind key press events
        self.bind('<KeyPress>', self.on_key_press)
        self.bind('<KeyRelease>', self.on_key_release)

        # Bind specific special keys that might be used by barcode scanners
        special_keys = [
            '<Escape>', '<Return>', '<Tab>', '<BackSpace>', '<Delete>',
            '<Control_L>', '<Control_R>', '<Alt_L>', '<Alt_R>',
            '<Shift_L>', '<Shift_R>', '<Super_L>', '<Super_R>',
            '<F1>', '<F2>', '<F3>', '<F4>', '<F5>', '<F6>',
            '<F7>', '<F8>', '<F9>', '<F10>', '<F11>', '<F12>',
            '<Up>', '<Down>', '<Left>', '<Right>',
            '<Home>', '<End>', '<Page_Up>', '<Page_Down>',
            '<Insert>', '<Pause>', '<Scroll_Lock>', '<Num_Lock>',
            '<Caps_Lock>', '<Menu>'
        ]

        for key in special_keys:
            self.bind(key, lambda event, k=key: self.on_special_key(event, k))

        # Bind Control combinations
        ctrl_combinations = [
            '<Control-q>', '<Control-Q>', '<Control-c>', '<Control-C>',
            '<Control-v>', '<Control-V>', '<Control-a>', '<Control-A>',
            '<Control-z>', '<Control-Z>', '<Control-y>', '<Control-Y>'
        ]

        for combo in ctrl_combinations:
            self.bind(combo, lambda event, c=combo: self.on_ctrl_combination(event, c))

        # Ensure window can receive focus
        self.focus_force()

    def on_key_press(self, event):
        """Handle regular key press events."""
        self.event_counter += 1

        # Collect printable characters for QR sequence detection
        if event.char and event.char.isprintable():
            self.qr_buffer += event.char

        # Get key information
        key_char = event.char
        key_code = event.keycode
        key_sym = event.keysym

        # Format the output
        timestamp = time.strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds

        # Determine what to display
        if key_char and key_char.isprintable():
            display_char = f"'{key_char}'"
        elif key_char:
            # Non-printable character
            display_char = f"<{repr(key_char)[1:-1]}>"
        else:
            display_char = f"<{key_sym}>"

        # Log the event with additional keycode info
        ascii_info = f" ascii={ord(key_char)}" if key_char and len(key_char) == 1 else ""
        log_entry = (
            f"[{self.event_counter:04d}] {timestamp} KeyPress: "
            f"char={display_char} sym={key_sym} keycode={key_code}{ascii_info}\n"
        )

        self.text_area.insert(tk.END, log_entry)
        self.text_area.see(tk.END)

        # Update status
        self.status_label.config(
            text=f"Last key: {display_char} | Events: {self.event_counter}",
            fg="green"
        )

        return "break"  # Prevent default handling

    def on_key_release(self, _event):
        """Handle key release events (optional, for detailed logging)."""
        # Uncomment the next lines if you want to see key release events too
        # timestamp = time.strftime("%H:%M:%S.%f")[:-3]
        # log_entry = f"[{self.event_counter:04d}] {timestamp} KeyRelease: sym={_event.keysym}\n"
        # self.text_area.insert(tk.END, log_entry)
        return "break"

    def on_special_key(self, event, key_name):
        """Handle special key events."""
        self.event_counter += 1
        timestamp = time.strftime("%H:%M:%S.%f")[:-3]

        # Handle QR sequence detection for Return key
        if key_name == '<Return>':
            if self.qr_buffer.strip():
                self.handle_qr_sequence(self.qr_buffer.strip())
            self.qr_buffer = ""

        log_entry = (
            f"[{self.event_counter:04d}] {timestamp} SpecialKey: "
            f"{key_name} sym={event.keysym} keycode={event.keycode}\n"
        )

        self.text_area.insert(tk.END, log_entry)
        self.text_area.see(tk.END)

        # Update status
        self.status_label.config(
            text=f"Special key: {key_name} | Events: {self.event_counter}",
            fg="orange"
        )

        # Test specific bindings
        if key_name == '<Escape>':
            self.text_area.insert(tk.END, "*** ESCAPE KEY DETECTED - Function called! ***\n")
            self.test_escape_function()

        return "break"

    def on_ctrl_combination(self, event, combo_name):
        """Handle Control key combinations."""
        self.event_counter += 1
        timestamp = time.strftime("%H:%M:%S.%f")[:-3]

        log_entry = (
            f"[{self.event_counter:04d}] {timestamp} CtrlCombo: "
            f"{combo_name} sym={event.keysym} keycode={event.keycode}\n"
        )

        self.text_area.insert(tk.END, log_entry)
        self.text_area.see(tk.END)

        # Update status
        self.status_label.config(
            text=f"Ctrl combo: {combo_name} | Events: {self.event_counter}",
            fg="red"
        )

        # Test specific bindings
        if combo_name in ['<Control-q>', '<Control-Q>']:
            self.text_area.insert(tk.END, "*** CTRL+Q DETECTED - Function called! ***\n")
            self.test_ctrl_q_function()

        return "break"

    def test_escape_function(self):
        """Function that should be called when Escape is pressed."""
        self.text_area.insert(tk.END, "==> Escape function executed successfully!\n")
        self.text_area.see(tk.END)

    def test_ctrl_q_function(self):
        """Function that should be called when Ctrl+Q is pressed."""
        self.text_area.insert(tk.END, "==> Ctrl+Q function executed successfully!\n")
        self.text_area.see(tk.END)

    def clear_log(self):
        """Clear the text area."""
        self.text_area.delete(1.0, tk.END)
        self.event_counter = 0
        self.text_area.insert(tk.END, "=== Log Cleared ===\n")
        self.text_area.insert(tk.END, "Time: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
        self.status_label.config(text="Log cleared - Ready for input...", fg="blue")

    def handle_qr_sequence(self, qr_text):
        """Handle complete QR sequence input with exact matching."""
        qr_clean = qr_text.strip().lower()  # Clean and normalize

        self.text_area.insert(tk.END, f"\n*** QR SEQUENCE DETECTED: '{qr_text}' ***\n")

        # Exact matches only for security
        if qr_clean == "shutdown":
            self.text_area.insert(tk.END, "==> SHUTDOWN command recognized!\n")
            self.shutdown_system()
        elif qr_clean == "reboot":
            self.text_area.insert(tk.END, "==> REBOOT command recognized!\n")
            self.reboot_system()
        elif qr_clean == "photo":
            self.text_area.insert(tk.END, "==> PHOTO command recognized!\n")
            self.take_photo()
        elif qr_clean == "exit":
            self.text_area.insert(tk.END, "==> EXIT command recognized!\n")
            self.quit_application()
        elif qr_clean == "test":
            self.text_area.insert(tk.END, "==> TEST command - no action taken\n")
        else:
            self.text_area.insert(tk.END, f"==> Unknown QR command: '{qr_text}'\n")

        self.text_area.insert(tk.END, "\n")
        self.text_area.see(tk.END)

    def shutdown_system(self):
        """Safely shutdown the system."""
        self.text_area.insert(tk.END, "==> SHUTDOWN: System shutdown initiated...\n")
        self.text_area.see(tk.END)

        # On actual Raspberry Pi, you would use:
        # subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)

        # For testing, just show the message
        self.text_area.insert(tk.END, "    (In production: sudo shutdown -h now)\n")

    def reboot_system(self):
        """Safely reboot the system."""
        self.text_area.insert(tk.END, "==> REBOOT: System reboot initiated...\n")
        self.text_area.see(tk.END)

        # On actual Raspberry Pi, you would use:
        # subprocess.run(['sudo', 'reboot'], check=False)

        # For testing, just show the message
        self.text_area.insert(tk.END, "    (In production: sudo reboot)\n")

    def take_photo(self):
        """Trigger photo capture."""
        self.text_area.insert(tk.END, "==> PHOTO: Photo capture triggered!\n")
        self.text_area.see(tk.END)

        # In your photobooth, this would call your photo function
        # self.photobooth.capture_photo()

        self.text_area.insert(tk.END, "    (In production: trigger photobooth capture)\n")

    def quit_application(self):
        """Safely quit the application."""
        self.text_area.insert(tk.END, "==> EXIT: Application quit requested...\n")
        self.text_area.see(tk.END)

        # Give user a moment to see the message
        self.after(2000, self.destroy)  # Quit after 2 seconds

def main():
    """Main function to run the keyboard tester."""
    print("Starting Keyboard Input Tester...")
    print("This will help test if your barcode scanner works with tkinter.")
    print("Close the window or use Ctrl+C in terminal to exit.")

    app = KeyboardTester()

    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting...")
    finally:
        print("Keyboard tester closed.")

if __name__ == "__main__":
    main()
