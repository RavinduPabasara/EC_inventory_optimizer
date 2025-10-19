import json
import os
from openai import OpenAI
from typing import List, Dict, Any
from dotenv import load_dotenv

# --- 1. DEFINE THE "TOOLS" (THE ENVIRONMENT'S CAPABILITIES) ---
# These are the Python functions our agent can call. In a real-world
# scenario, these would control a robot, update a database, etc.

def pick_up(item_id: str):
    """Picks up the specified item from the staging area."""
    print(f"ACTION: Robot arm is picking up item '{item_id}'.")
    # Simulate a successful action
    return f"Successfully holding item '{item_id}'."

def move_to_bin(bin_id: int):
    """Moves the robot arm to the specified inventory bin."""
    print(f"ACTION: Robot is moving to bin #{bin_id}.")
    # Simulate a successful action
    return f"Successfully arrived at bin #{bin_id}."

def place_item(item_id: str, x: int, y: int):
    """Places the currently held item at coordinates (x, y) within the current bin."""
    print(f"ACTION: Placing item '{item_id}' at position (x={x}, y={y}).")
    # Simulate a successful action
    return f"Item '{item_id}' has been placed successfully."

# --- 2. SCRIPT EXECUTION STARTS HERE ---

def main():
    """Main function to run the agent executor."""
    print("--- Starting AI Agent Executor ---")
    
    # --- 2a. LOAD ENVIRONMENT VARIABLES ---
    # Load the .env file from the executor directory
    load_dotenv()
    
    # --- 2b. LOAD THE OPTIMIZED PLAN ---
    # The plan is the bridge between the Java optimizer and the Python agent.
    try:
        # The JSON file is in the parent directory, as created by the Java app.
        with open("../optimized_plan.json", "r") as f:
            packing_plan: List[Dict[str, Any]] = json.load(f)
    except FileNotFoundError:
        print("\nERROR: 'optimized_plan.json' not found in the root directory.")
        print("Please run the Java optimizer first to generate the plan.")
        return

    # --- 2b. CONVERT THE PLAN INTO A NATURAL LANGUAGE STRING FOR THE PROMPT ---
    plan_text = "Execute the following packing plan step-by-step:\n"
    for bin_data in packing_plan:
        plan_text += f"\nFor Bin {bin_data['binId']}:"
        for item_data in bin_data['items']:
            plan_text += f"\n- Place item {item_data['id']} at position (x={item_data['x']}, y={item_data['y']})."

    # --- 3. SETUP THE OPENAI CLIENT AND AGENT ---
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\nERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file in the executor directory with:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"\nERROR: Failed to initialize OpenAI client: {e}")
        return

    # Define the functions available to the model, mapping names to actual functions.
    available_tools = {
        "pick_up": pick_up,
        "move_to_bin": move_to_bin,
        "place_item": place_item,
    }

    # Define the schema for the tools, which tells the model what they are and what
    # parameters they expect. This is crucial for function calling.
    tools_schema = [
        {
            "type": "function",
            "function": {
                "name": "pick_up",
                "description": "Picks up a specified item from the general staging area.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "The unique ID of the item to pick up, e.g., 'A_1'."}
                    },
                    "required": ["item_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "move_to_bin",
                "description": "Physically moves the robot to a specific bin location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bin_id": {"type": "integer", "description": "The destination bin number."}
                    },
                    "required": ["bin_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "place_item",
                "description": "Places the currently held item into the current bin at specific coordinates.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "The ID of the item being placed."},
                        "x": {"type": "integer", "description": "The x-coordinate for placement."},
                        "y": {"type": "integer", "description": "The y-coordinate for placement."},
                    },
                    "required": ["item_id", "x", "y"],
                },
            },
        }
    ]

    # --- 3b. DEFINE THE CONVERSATION (MESSAGES) ---
    messages = [
        {
            "role": "system",
            "content": (
                "You are an inventory management robot assistant. Your task is to execute a packing plan by calling the available tools in the correct logical sequence. "
                "For each item in the plan, you must follow this exact sequence: "
                "1. Call `pick_up` with the item's ID. "
                "2. Call `move_to_bin` with the item's destination bin ID. "
                "3. Call `place_item` with the item's ID and its destination coordinates. "
                "Do not perform actions for multiple items at once. Complete the full sequence for one item before starting the next. "
                "When the entire plan is complete, respond with a single sentence: 'The packing plan has been fully executed.'"
            )
        },
        {
            "role": "user",
            "content": plan_text
        }
    ]

    print("\n--- Plan loaded. Starting agent loop... ---\n")

    # --- 4. RUN THE AGENT LOOP ---
    while True:
        # Send the current conversation state to the model
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Or another model that supports parallel tool use
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
        )
        response_message = response.choices[0].message
        


        # Check if the model wants to call one or more tools
        if response_message.tool_calls:
            # Add the assistant's turn to the conversation history
            messages.append(response_message)
            
            # Execute all tool calls requested by the model in this turn
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_tools[function_name]
                function_args = json.loads(tool_call.function.arguments)
                
                # Call the actual Python function with the arguments from the model
                function_response = function_to_call(**function_args)
                
                # Add the result of the tool call to the conversation history
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
        else:
            # If there are no tool calls, the model is finished or has a final message.
            final_response = response_message.content
            print(f"\nAGENT: {final_response}")
            break # Exit the loop

    print("\n--- Agent loop finished. ---")


if __name__ == "__main__":
    main()