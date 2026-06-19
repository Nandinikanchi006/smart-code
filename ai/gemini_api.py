import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load the hidden API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)

# This holds the ongoing chat memory for the Copilot Sidebar
copilot_chat = None

def analyze_and_fix_code(broken_code):
    """Used for the Auto-Fix button."""
    if not client:
        return "# Error: API key missing. Please set GEMINI_API_KEY in your .env file.\n" + broken_code

    try:
        prompt = f"""
        You are an expert code auto-fixer integrated into an IDE.
        Analyze the following code. Identify the language, find any bugs, and fix them.
        IMPORTANT RULES: Return ONLY the corrected code. No markdown. No explanations.
        Code to fix:
        {broken_code}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        fixed_code = response.text.strip()
        
        # Safety check to strip markdown
        if fixed_code.startswith("```") and fixed_code.endswith("```"):
            lines = fixed_code.split('\n')
            fixed_code = '\n'.join(lines[1:-1])
            
        return fixed_code
    except Exception as e:
        return f"# AI Error: {str(e)}\n\n" + broken_code

def ask_copilot(prompt, current_code=""):
    """Used for the Copilot Chat Sidebar."""
    global copilot_chat
    if not client:
        return "Error: API key missing."
    
    # Initialize the chat session if it doesn't exist yet
    if copilot_chat is None:
        copilot_chat = client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction="You are an expert AI Copilot integrated directly into the user's IDE. Be concise, helpful, and friendly. Provide code snippets directly when needed."
            )
        )
        
    full_prompt = prompt
    # Automatically attach the user's current code so the AI has context!
    if current_code.strip():
        full_prompt += f"\n\n[FOR YOUR CONTEXT: Here is the code currently in my editor:]\n```\n{current_code}\n```"
        
    try:
        response = copilot_chat.send_message(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Copilot Error: {str(e)}"