# ai/gemini_api.py
import os
from dotenv import load_dotenv
from google import genai

# Load the hidden API key from the .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_and_fix_code(broken_code):
    """
    Sends code to Gemini API using the NEW SDK, asks it to act as an IDE auto-fixer, 
    and returns the clean, corrected code.
    """
    if not API_KEY:
        return "# Error: API key missing. Please set GEMINI_API_KEY in your .env file.\n" + broken_code

    try:
        # Initialize the new client
        client = genai.Client(api_key=API_KEY)
        
        # The hidden prompt that guides the AI's behavior
        prompt = f"""
        You are an expert code auto-fixer integrated into an IDE.
        Analyze the following code. Identify the language, find any bugs, syntax errors, or bad indentation, and fix them.
        
        IMPORTANT RULES:
        1. Return ONLY the corrected code. 
        2. Do NOT use markdown code blocks (e.g., do not wrap in ```python ... ```).
        3. Do NOT provide explanations or conversational text. Just the raw code.
        
        Code to fix:
        {broken_code}
        """
        
        # Call the new API
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        fixed_code = response.text.strip()
        
        # Safety check: Strip markdown if the AI accidentally includes it anyway
        if fixed_code.startswith("```") and fixed_code.endswith("```"):
            lines = fixed_code.split('\n')
            fixed_code = '\n'.join(lines[1:-1])
            
        return fixed_code

    except Exception as e:
        # If the internet is down or the API fails, return the original code with an error comment
        return f"# AI Error: {str(e)}\n\n" + broken_code