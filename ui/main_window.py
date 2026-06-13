# ui/main_window.py
import customtkinter as ctk
import tkinter  # <--- ADD THIS LINE
from tkinter import filedialog
import subprocess
import threading
from core import file_manager
from ai import gemini_api
class SmartIDE(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Smart Python IDE")
        self.geometry("950x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.current_filepath = None

        self._build_top_bar()
        self._build_editor()
        self._build_console()

    def _build_top_bar(self):
        self.button_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.button_frame.pack(side="top", fill="x", padx=10, pady=5)

        self.open_btn = ctk.CTkButton(self.button_frame, text="Open File", command=self.handle_open, width=100)
        self.open_btn.pack(side="left", padx=5)

        self.save_btn = ctk.CTkButton(self.button_frame, text="Save File", command=self.handle_save, width=100)
        self.save_btn.pack(side="left", padx=5)

        # FIX 1: We added command=self.handle_run to activate the button
        self.run_btn = ctk.CTkButton(self.button_frame, text="Run Code ▶", fg_color="#2ea043", hover_color="#238636", width=100, command=self.handle_run)
        self.run_btn.pack(side="left", padx=5)

        self.ai_btn = ctk.CTkButton(
            self.button_frame, 
            text="✨ Auto-Fix", 
            fg_color="#8957e5", 
            hover_color="#6e40c9", 
            width=100,
            command=self.handle_auto_fix
        )
        self.ai_btn.pack(side="right", padx=5)

    def _build_editor(self):
        self.text_editor = ctk.CTkTextbox(self, font=("Consolas", 15), wrap="none")
        self.text_editor.pack(expand=True, fill="both", padx=10, pady=(0, 5))

    def _build_console(self):
        self.output_console = ctk.CTkTextbox(self, font=("Consolas", 13), height=130, text_color="#00ff00", fg_color="#1e1e1e")
        self.output_console.pack(fill="x", padx=10, pady=(0, 10))
        self.log_to_console("System Ready. Terminal Output will appear here...")

    def log_to_console(self, message):
        """Helper to write to the read-only console."""
        self.output_console.configure(state="normal")
        self.output_console.insert("end", message + "\n")
        self.output_console.configure(state="disabled")
        self.output_console.see("end")

    # --- Button Actions ---
    def handle_open(self):
        filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if filepath:
            self.current_filepath = filepath
            code = file_manager.read_file(filepath)
            self.text_editor.delete("1.0", "end")
            self.text_editor.insert("1.0", code)
            self.title(f"Smart IDE - {filepath}")
            self.log_to_console(f"Opened: {filepath}")

    def handle_save(self):
        if not self.current_filepath:
            self.current_filepath = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
            )
        if self.current_filepath:
            code = self.text_editor.get("1.0", "end-1c")
            file_manager.write_file(self.current_filepath, code)
            self.title(f"Smart IDE - {self.current_filepath} (Saved)")
            self.log_to_console("File saved successfully.")

    # FIX 1: The execution logic
    def handle_run(self):
        if not self.current_filepath:
            self.log_to_console("⚠️ Please save your code to a file before running it!")
            return

        # Always save right before running, just like real IDEs
        self.handle_save()
        self.log_to_console(f"\n--- Running {self.current_filepath} ---")
        
        try:
            # This asks your computer's terminal to run the python file
            result = subprocess.run(["python", self.current_filepath], capture_output=True, text=True, timeout=10)
            
            if result.stdout:
                self.log_to_console(result.stdout)
            if result.stderr:
                self.log_to_console("ERRORS:\n" + result.stderr)
        except Exception as e:
            self.log_to_console(f"Execution failed: {e}")

    # FIX 2: Threading for the AI
    def handle_auto_fix(self):
        try:
            target_code = self.text_editor.get("sel.first", "sel.last")
            is_selection = True
        except tkinter.TclError:
            target_code = self.text_editor.get("1.0", "end-1c")
            is_selection = False

        if not target_code.strip():
            self.log_to_console("⚠️ No code to fix.")
            return

        self.log_to_console("✨ AI is thinking... (Window will not freeze anymore!)")
        self.ai_btn.configure(state="disabled") # Prevent clicking twice

        # We put the API call in a background worker so the UI stays alive
        def ai_worker():
            fixed_code = gemini_api.analyze_and_fix_code(target_code)
            # Send the result back to the main UI thread safely
            self.after(0, apply_fix, fixed_code, is_selection)

        def apply_fix(fixed_code, is_selection):
            if is_selection:
                self.text_editor.delete("sel.first", "sel.last")
                self.text_editor.insert("insert", fixed_code)
            else:
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", fixed_code)
                
            self.log_to_console("✅ AI fix applied.")
            self.ai_btn.configure(state="normal") # Turn button back on

        # Start the background worker
        threading.Thread(target=ai_worker, daemon=True).start()