# Smart Python IDE with AI Copilot 🚀

A lightweight, modern Python IDE built entirely in Python using `CustomTkinter`. It features an integrated terminal, file management, and a dual-purpose AI engine driven by the Google Gemini API (`gemini-2.5-flash`), including an autonomous code-fixer and a context-aware Copilot sidebar.

## ✨ Features

* **Context-Aware AI Copilot:** A built-in chat sidebar that automatically reads the code in your editor. Ask questions, request explanations, or generate new code without having to copy and paste.
* **✨ Auto-Fix Engine:** Highlight broken sections of code (or scan the entire document) to fix syntax, indentation, and logic errors instantaneously. 
* **Integrated Terminal:** Execute Python scripts directly inside the application console and view standard output or errors in real-time.
* **Local File Management:** Seamlessly read, write, open, and save `.py` files locally.
* **Non-Blocking UI:** All AI requests and terminal executions are handled on background threads to ensure the editor never freezes.

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Nandinikanchi006/smart-code.git](https://github.com/Nandinikanchi006/smart-code.git)
   cd smart-code
1.Install the required dependencies:

Bash
pip install customtkinter google-genai python-dotenv
2.Set up the AI Engine:
Create a .env file in the root directory and add your Google AI Studio key:

Code snippet
GEMINI_API_KEY=your_api_key_here
(Note: The .env file must be kept secret and is included in .gitignore).

3.Run the application:
Bash
python main.py

🏗️Project Architecture
The codebase is strictly modularized for scalability and easy maintenance:

main.py: The application entry point and main process runner.

ui/main_window.py: Contains the visual shell, layout grids, and multi-threading logic for the Copilot and Editor panels.

core/file_manager.py: Handles pure Python file I/O operations isolated from the UI.

ai/gemini_api.py: Manages the Google GenAI SDK integration, prompt engineering, and the persistent chat memory for the Copilot.

📦 Building a Standalone Executable
If you wish to share this application with users who do not have Python installed, you can package it into a single .exe file using PyInstaller:

Bash
pip install pyinstaller
python -m PyInstaller --noconfirm --onedir --windowed --add-data "PATH_TO_CUSTOMTKINTER;customtkinter/" main.py
(Users running the .exe will still need to provide a .env file with their own API key next to the executable).
## 👨‍💻 Author
Developed by **Nandini Kanchi**.
