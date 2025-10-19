import json
import os
from openai import OpenAI
from typing import List, Dict, Any
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation
import threading

# --- VISUALIZATION CLASS ---
class LivePackingVisualizer:
    """Live visualization that updates as items are placed."""
    
    def __init__(self, num_bins=4):
        self.num_bins = num_bins
        self.fig, self.axes = plt.subplots(2, 2, figsize=(16, 12))
        self.axes = self.axes.flatten()
        
        # Color map for different item types
        self.colors = {
            'A': '#FF6B6B',  # Red
            'B': '#4ECDC4',  # Teal  
            'C': '#45B7D1',  # Blue
            'D': '#96CEB4'   # Green
        }
        
        # Track bin states
        self.bin_items = {i: [] for i in range(1, num_bins+1)}
        self.current_bin = None
        self.current_item = None
        
        # Setup initial plot
        self.setup_plot()
        
        # Enable interactive mode
        plt.ion()
        plt.show()
    
    def setup_plot(self):
        """Setup the initial plot with empty bins."""
        for i, ax in enumerate(self.axes):
            if i < 4:
                ax.clear()
                ax.set_xlim(0, 30)
                ax.set_ylim(0, 10)
                ax.set_aspect('equal')
                ax.set_xlabel('Width (cm)', fontsize=10)
                ax.set_ylabel('Height (cm)', fontsize=10)
                ax.set_title(f'Bin {i+1} (30×10 cm)', fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3)
                
                # Draw bin border
                border = patches.Rectangle((0, 0), 30, 10, linewidth=2, 
                                          edgecolor='black', facecolor='none')
                ax.add_patch(border)
            else:
                ax.axis('off')
        
        self.fig.suptitle('Live Bin Packing Visualization - Waiting for actions...', 
                         fontsize=16, fontweight='bold')
        plt.tight_layout()
    
    def get_item_type(self, item_id):
        """Extract the item type from item ID."""
        return item_id.split('_')[0] if '_' in item_id else 'A'
    
    def get_item_dimensions(self, item_id):
        """Get default dimensions for an item based on its ID."""
        if item_id.startswith('A_'):
            return 10, 3
        elif item_id.startswith('B_'):
            return 5, 5
        elif item_id.startswith('C_'):
            return 4, 4
        elif item_id.startswith('D_'):
            return 8, 2
        return 1, 1
    
    def update_current_item(self, item_id):
        """Update which item is currently being handled."""
        self.current_item = item_id
        self.fig.suptitle(f'Live Bin Packing - Handling: {item_id}', 
                         fontsize=16, fontweight='bold', color='blue')
        plt.pause(0.1)
    
    def update_current_bin(self, bin_id):
        """Update which bin the robot is at."""
        self.current_bin = bin_id
        if self.current_item:
            self.fig.suptitle(f'Live Bin Packing - Moving {self.current_item} to Bin {bin_id}', 
                             fontsize=16, fontweight='bold', color='orange')
        plt.pause(0.1)
    
    def place_item(self, item_id, bin_id, x, y, width=None, height=None):
        """Place an item in the visualization."""
        if bin_id < 1 or bin_id > 4:
            return
        
        # Get dimensions if not provided
        if width is None or height is None:
            width, height = self.get_item_dimensions(item_id)
        
        bin_idx = bin_id - 1
        ax = self.axes[bin_idx]
        
        item_type = self.get_item_type(item_id)
        color = self.colors.get(item_type, '#CCCCCC')
        
        # Draw the item
        rect = patches.Rectangle(
            (x, y), width, height,
            linewidth=2,
            edgecolor='yellow',
            facecolor=color,
            alpha=0.8
        )
        ax.add_patch(rect)
        
        # Add label
        center_x = x + width / 2
        center_y = y + height / 2
        ax.text(center_x, center_y, item_id,
               ha='center', va='center', fontsize=8, fontweight='bold',
               color='white', bbox=dict(boxstyle='round,pad=0.3', 
               facecolor='black', alpha=0.5))
        
        # Store item info
        self.bin_items[bin_id].append({
            'id': item_id,
            'x': x, 'y': y,
            'width': width, 'height': height
        })
        
        # Update bin info
        items_count = len(self.bin_items[bin_id])
        area_used = sum(item['width'] * item['height'] for item in self.bin_items[bin_id])
        
        ax.set_title(f'Bin {bin_id} - Items: {items_count} | Area: {area_used}/300 cm²',
                    fontsize=12, fontweight='bold')
        
        self.fig.suptitle(f'Live Bin Packing - Placed {item_id} in Bin {bin_id}!', 
                         fontsize=16, fontweight='bold', color='green')
        
        # Redraw
        plt.draw()
        plt.pause(0.5)  # Pause to show the placement
    
    def finalize(self):
        """Finalize the visualization."""
        self.fig.suptitle('Live Bin Packing - COMPLETE!', 
                         fontsize=16, fontweight='bold', color='green')
        plt.ioff()
        
        # Save final image
        plt.savefig('live_packing_final.png', dpi=150, bbox_inches='tight')
        print("\nVisualization saved as 'live_packing_final.png'")
        plt.show()

# --- GLOBAL VISUALIZER INSTANCE ---
visualizer = None

# --- ACTION FUNCTIONS WITH VISUALIZATION ---
def pick_up(item_id: str):
    """Picks up the specified item from the staging area."""
    print(f"ACTION: Robot arm is picking up item '{item_id}'.")
    if visualizer:
        visualizer.update_current_item(item_id)
    return f"Successfully holding item '{item_id}'."

def move_to_bin(bin_id: int):
    """Moves the robot arm to the specified inventory bin."""
    print(f"ACTION: Robot is moving to bin #{bin_id}.")
    if visualizer:
        visualizer.update_current_bin(bin_id)
    return f"Successfully arrived at bin #{bin_id}."

def place_item(item_id: str, x: int, y: int):
    """Places the currently held item at coordinates (x, y) within the current bin."""
    print(f"ACTION: Placing item '{item_id}' at position (x={x}, y={y}).")
    
    # Update visualization
    if visualizer and visualizer.current_bin:
        # Try to get width/height from the plan
        width, height = visualizer.get_item_dimensions(item_id)
        visualizer.place_item(item_id, visualizer.current_bin, x, y, width, height)
    
    return f"Item '{item_id}' has been placed successfully."

# --- MAIN EXECUTION ---
def main():
    """Main function to run the agent executor with live visualization."""
    global visualizer
    
    print("--- Starting AI Agent Executor with Live Visualization ---")
    
    # Load environment
    load_dotenv()
    
    # Load packing plan
    try:
        with open("../optimized_plan.json", "r") as f:
            packing_plan: List[Dict[str, Any]] = json.load(f)
    except FileNotFoundError:
        print("\nERROR: 'optimized_plan.json' not found.")
        print("Please run the Java optimizer first.")
        return
    
    # Initialize visualizer
    print("\nInitializing live visualizer...")
    visualizer = LivePackingVisualizer(num_bins=4)
    
    # Convert plan to text for the agent
    plan_text = "Execute the following packing plan step-by-step:\n"
    for bin_data in packing_plan:
        plan_text += f"\nFor Bin {bin_data['binId']}:"
        for item_data in bin_data['items']:
            plan_text += f"\n- Place item {item_data['id']} at position (x={item_data['x']}, y={item_data['y']})."
    
    # Setup OpenAI client
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\nERROR: OPENAI_API_KEY not found.")
        return
    
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"\nERROR: Failed to initialize OpenAI client: {e}")
        return
    
    # Define tools
    available_tools = {
        "pick_up": pick_up,
        "move_to_bin": move_to_bin,
        "place_item": place_item,
    }
    
    tools_schema = [
        {
            "type": "function",
            "function": {
                "name": "pick_up",
                "description": "Picks up a specified item from the staging area.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "The unique ID of the item."}
                    },
                    "required": ["item_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "move_to_bin",
                "description": "Moves the robot to a specific bin location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bin_id": {"type": "integer", "description": "The bin number."}
                    },
                    "required": ["bin_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "place_item",
                "description": "Places the held item at specific coordinates.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string"},
                        "x": {"type": "integer"},
                        "y": {"type": "integer"}
                    },
                    "required": ["item_id", "x", "y"],
                },
            },
        },
    ]
    
    # Run agent loop
    messages = [
        {
            "role": "system",
            "content": (
                "You are a warehouse robot control agent. Execute the packing plan "
                "using pick_up, move_to_bin, and place_item functions. "
                "Work through each bin systematically."
            )
        },
        {
            "role": "user",
            "content": plan_text
        }
    ]
    
    print("\n--- Plan loaded. Starting agent loop... ---\n")
    
    max_iterations = 200
    for iteration in range(max_iterations):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools_schema,
                tool_choice="auto",
            )
            
            assistant_message = response.choices[0].message
            messages.append(assistant_message)
            
            # Check if finished
            if assistant_message.content and not assistant_message.tool_calls:
                print(f"\n{assistant_message.content}")
                break
            
            # Execute tool calls
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name in available_tools:
                        result = available_tools[function_name](**function_args)
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": result,
                        })
        
        except Exception as e:
            print(f"\nERROR during agent execution: {e}")
            break
    
    print("\n--- Agent execution complete. ---")
    
    # Finalize visualization
    if visualizer:
        visualizer.finalize()

if __name__ == "__main__":
    main()

