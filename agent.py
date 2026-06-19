import os
import ast
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys # Added to gracefully exit if key is missing

# Load the hidden API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: Could not find GEMINI_API_KEY!")
    print("Make sure you have a .env file in the same folder as this script, and it contains:")
    print("GEMINI_API_KEY=your_actual_key_here")
    sys.exit()

client = genai.Client(api_key=api_key)

# ---------------------------------------------------------
# 1. THE TOOL (The Agent's Hands)
# This is a normal Python function. The docstring (""") is 
# CRITICAL because this is how Gemini learns what the tool does.
# ---------------------------------------------------------
def calculator(math_expression: str) -> float:
    """
    Evaluates a mathematical expression and returns the result. 
    Use this for ALL math operations.
    Args:
        math_expression: A string containing a math expression (e.g., '15 * 42 / 3')
    """
    print(f"\n   [TOOL TRIGGERED] The AI is typing '{math_expression}' into the calculator...")
    # ast.literal_eval is a safe way to do math in Python
    node = ast.parse(math_expression, mode='eval')
    return float(eval(compile(node, '<string>', 'eval')))

# ---------------------------------------------------------
# 2. THE AGENT LOOP (The Agent's Brain)
# ---------------------------------------------------------
def run_agent(user_prompt: str):
    print(f"\n🧑‍💻 USER: {user_prompt}")
    print("-" * 50)
    
    # We create a Chat Session and explicitly give Gemini our calculator tool
    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            tools=[calculator], # <--- Giving the AI the tool here!
            temperature=0       # Keep it logical and focused
        )
    )

    # Step 1: Send the initial problem to the AI
    response = chat.send_message(user_prompt)

    # Step 2: The ReAct Loop (Reason -> Act -> Observe)
    # We loop because the AI might need to use the tool multiple times!
    while True:
        # Check if the AI decided it needs to use a tool
        if response.function_calls:
            for function_call in response.function_calls:
                
                # Check which tool the AI wants to use
                if function_call.name == "calculator":
                    # Grab the exact math expression the AI wants to solve
                    expression = function_call.args["math_expression"]
                    
                    # 1. ACT: Execute our Python function
                    result = calculator(expression)
                    print(f"   [OBSERVATION] The calculator returned: {result}")
                    
                    # 2. OBSERVE: Send the answer back to the AI's brain
                    print("   [THINKING] Sending result back to the AI...")
                    response = chat.send_message(
                        types.Part.from_function_response(
                            name="calculator",
                            response={"result": result}
                        )
                    )
        else:
            # If the AI didn't call a tool, it means it has figured out the final answer!
            print("\n🤖 AGENT FINAL ANSWER:")
            print(response.text)
            break # Exit the loop, the job is done.

# ---------------------------------------------------------
# 3. RUN IT
# ---------------------------------------------------------
if __name__ == "__main__":
    # Let's give it a trick question that requires math!
    complex_question = (
        "If I have 15 boxes, each containing 42 apples, and I divide "
        "them equally among 3 friends, how many apples does each friend get? "
        "Please use your calculator tool to find the exact number."
    )
    
    run_agent(complex_question)