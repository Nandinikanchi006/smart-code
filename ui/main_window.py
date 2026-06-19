import customtkinter as ctk
import tkinter
from tkinter import filedialog
import subprocess
import threading
from core import file_manager
from ai import gemini_api

class SmartIDE(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Python IDE with Copilot")
        # Made the window wider to fit the Copilot sidebar
        self.geometry("1200x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.current_filepath = None

        self._build_top_bar()
        
        # Split the screen into Left (Editor) and Right (Copilot)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=10, pady=5)
        
        self.left_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_panel.pack(side="left", expand=True, fill="both", padx=(0, 5))
        
        self.right_panel = ctk.CTkFrame(self.main_container, width=350)
        self.right_panel.pack(side="right", fill="y", padx=(5, 0))

        self._build_editor()
        self._build_console()
        self._build_copilot()

    def _build_top_bar(self):
        self.button_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.button_frame.pack(side="top", fill="x", padx=10, pady=5)

        self.open_btn = ctk.CTkButton(self.button_frame, text="Open File", command=self.handle_open, width=100)
        self.open_btn.pack(side="left", padx=5)

        self.save_btn = ctk.CTkButton(self.button_frame, text="Save File", command=self.handle_save, width=100)
        self.save_btn.pack(side="left", padx=5)

        self.run_btn = ctk.CTkButton(self.button_frame, text="Run Code ▶", fg_color="#2ea043", hover_color="#238636", width=100, command=self.handle_run)
        self.run_btn.pack(side="left", padx=5)

        self.ai_btn = ctk.CTkButton(self.button_frame, text="✨ Auto-Fix", fg_color="#8957e5", hover_color="#6e40c9", width=100, command=self.handle_auto_fix)
        self.ai_btn.pack(side="right", padx=5)

    def _build_editor(self):
        # Editor goes in the left panel
        self.text_editor = ctk.CTkTextbox(self.left_panel, font=("Consolas", 15), wrap="none")
        self.text_editor.pack(expand=True, fill="both", pady=(0, 5))

    def _build_console(self):
        # Console goes in the left panel below the editor
        self.output_console = ctk.CTkTextbox(self.left_panel, font=("Consolas", 13), height=150, text_color="#00ff00", fg_color="#1e1e1e")
        self.output_console.pack(fill="x", pady=(0, 5))
        self.log_to_console("System Ready. Terminal Output will appear here...")

    def _build_copilot(self):
        # --- COPILOT SIDEBAR UI ---
        self.copilot_label = ctk.CTkLabel(self.right_panel, text="🤖 AI Copilot", font=("Arial", 16, "bold"))
        self.copilot_label.pack(pady=(10, 5))

        self.chat_history = ctk.CTkTextbox(self.right_panel, font=("Arial", 13), wrap="word")
        self.chat_history.pack(expand=True, fill="both", padx=10, pady=5)
        self.chat_history.insert("1.0", "Copilot: Hello! Ask me any coding question. I can see the code in your editor automatically.\n\n")
        self.chat_history.configure(state="disabled")

        self.chat_input = ctk.CTkEntry(self.right_panel, placeholder_text="Ask Copilot a question...", font=("Arial", 13))
        self.chat_input.pack(fill="x", padx=10, pady=(5, 0))
        # Bind the Enter key to send the message
        self.chat_input.bind("<Return>", lambda event: self.handle_ask_copilot())

        self.ask_btn = ctk.CTkButton(self.right_panel, text="Send", command=self.handle_ask_copilot)
        self.ask_btn.pack(fill="x", padx=10, pady=10)

    # --- UI Helpers ---
    def log_to_console(self, message):
        self.output_console.configure(state="normal")
        self.output_console.insert("end", message + "\n")
        self.output_console.configure(state="disabled")
        self.output_console.see("end")

    def append_to_chat(self, sender, message):
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"{sender}: {message}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

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

    def handle_run(self):
        if not self.current_filepath:
            self.log_to_console("⚠️ Please save your code to a file before running it!")
            return
        self.handle_save()
        self.log_to_console(f"\n--- Running {self.current_filepath} ---")
        try:
            result = subprocess.run(["python", self.current_filepath], capture_output=True, text=True, timeout=10)
            if result.stdout: self.log_to_console(result.stdout)
            if result.stderr: self.log_to_console("ERRORS:\n" + result.stderr)
        except Exception as e:
            self.log_to_console(f"Execution failed: {e}")

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

        self.log_to_console("✨ AI is thinking...")
        self.ai_btn.configure(state="disabled")

        def ai_worker():
            fixed_code = gemini_api.analyze_and_fix_code(target_code)
            self.after(0, apply_fix, fixed_code, is_selection)

        def apply_fix(fixed_code, is_selection):
            if is_selection:
                self.text_editor.delete("sel.first", "sel.last")
                self.text_editor.insert("insert", fixed_code)
            else:
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", fixed_code)
            self.log_to_console("✅ AI fix applied.")
            self.ai_btn.configure(state="normal")

        threading.Thread(target=ai_worker, daemon=True).start()

    def handle_ask_copilot(self):
        user_message = self.chat_input.get().strip()
        if not user_message:
            return
            
        # Update UI immediately
        self.chat_input.delete(0, "end")
        self.append_to_chat("You", user_message)
        
        # Disable input while AI is typing
        self.ask_btn.configure(state="disabled")
        self.chat_input.configure(state="disabled")
        
        # Grab current code to give the AI context without the user pasting it
        current_code = self.text_editor.get("1.0", "end-1c")

        def chat_worker():
            response = gemini_api.ask_copilot(user_message, current_code)
            self.after(0, finalize_chat, response)

        def finalize_chat(response):
            self.append_to_chat("Copilot", response)
            self.ask_btn.configure(state="normal")
            self.chat_input.configure(state="normal")

        threading.Thread(target=chat_worker, daemon=True).start()