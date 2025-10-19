import json
import os
import math
from openai import OpenAI
from typing import List, Dict, Any
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation
import threading

# --- UTILITY FUNCTIONS ---
def calculate_actual_area(shape, width, height):
    """Calculate actual area based on shape type."""
    if shape == "Triangle":
        return (width * height) / 2.0  # Right triangle
    elif shape == "Circle":
        radius = min(width, height) / 2.0
        return math.pi * radius * radius  # Inscribed circle
    else:
        return width * height  # Rectangle

# --- VISUALIZATION CLASS ---
class LivePackingVisualizer:
    """Live visualization that updates as items are placed."""
    
    def __init__(self, num_bins=4):
        self.num_bins = num_bins
        self.fig, self.axes = plt.subplots(2, 2, figsize=(16, 12))
        self.axes = self.axes.flatten()
        
        # Define bin dimensions: [width, height]
        self.bin_dimensions = {
            1: (30, 20),   # 600 cm²
            2: (25, 20),   # 500 cm²
            3: (25, 18),   # 450 cm²
            4: (20, 20)    # 400 cm²
        }
        
        # Track bin states
        self.bin_items = {i: [] for i in range(1, num_bins+1)}
        self.current_bin = None
        self.current_item = None
        
        # Track total and packed value
        self.total_value = 0
        self.packed_value = 0
        
        # Setup initial plot
        self.setup_plot()
        
        # Enable interactive mode
        plt.ion()
        plt.show()
    
    def get_color(self, item_id, shape):
        """Get color based on item type and ID."""
        if shape == 'Circle':
            return '#4ECDC4'  # Teal
        elif shape == 'Triangle':
            return '#96CEB4'  # Green
        elif shape == 'Rectangle':
            if 'B_Rectangle02' in item_id:
                return '#D4A5D4'  # Pastel purple for smaller rectangle
            else:
                return '#FF6B6B'  # Red for Rectangle01
        else:
            return '#CCCCCC'  # Gray
    
    def setup_plot(self):
        """Setup the initial plot with empty bins."""
        for i, ax in enumerate(self.axes):
            if i < 4:
                bin_id = i + 1
                width, height = self.bin_dimensions[bin_id]
                area = width * height
                
                ax.clear()
                ax.set_xlim(0, width)
                ax.set_ylim(0, height)
                ax.set_aspect('equal')
                ax.set_xlabel('Width (cm)', fontsize=10)
                ax.set_ylabel('Height (cm)', fontsize=10)
                ax.set_title(f'Bin {bin_id} ({width}×{height} cm = {area} cm²)', 
                           fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3)
                
                # Draw bin border
                border = patches.Rectangle((0, 0), width, height, linewidth=2, 
                                          edgecolor='black', facecolor='none')
                ax.add_patch(border)
            else:
                ax.axis('off')
        
        self.fig.suptitle('Live Bin Packing Visualization - Waiting for actions...', 
                         fontsize=16, fontweight='bold')
        plt.tight_layout()
    
    def draw_shape_patch(self, ax, shape, x, y, width, height, color, item_id, rotation=0):
        """Draw different shapes based on the shape type with rotation support."""
        if shape == "Circle":
            # Draw a circle inscribed in the bounding box
            center_x = x + width / 2
            center_y = y + height / 2
            radius = min(width, height) / 2
            circle = patches.Circle((center_x, center_y), radius,
                                   linewidth=2, edgecolor='yellow',
                                   facecolor=color, alpha=0.8)
            ax.add_patch(circle)
            # Add label
            ax.text(center_x, center_y, item_id,
                   ha='center', va='center', fontsize=8, fontweight='bold',
                   color='white', bbox=dict(boxstyle='round,pad=0.3', 
                   facecolor='black', alpha=0.5))
        
        elif shape == "Triangle":
            # Draw a right triangle with rotation support (0°, 90°, 180°, 270°)
            # 0°: right angle at bottom-left
            # 90°: right angle at bottom-right
            # 180°: right angle at top-right
            # 270°: right angle at top-left
            if rotation == 90:
                triangle_points = [(x, y), (x + width, y), (x + width, y + height)]
            elif rotation == 180:
                triangle_points = [(x + width, y), (x + width, y + height), (x, y + height)]
            elif rotation == 270:
                triangle_points = [(x, y + height), (x + width, y + height), (x, y)]
            else:  # 0° (default)
                triangle_points = [(x, y), (x + width, y), (x, y + height)]
            
            triangle = patches.Polygon(triangle_points,
                                      linewidth=2, edgecolor='yellow',
                                      facecolor=color, alpha=0.8)
            ax.add_patch(triangle)
            # Add label at centroid
            centroid_x = x + width / 3 + (width / 3 if rotation in [90, 180] else 0)
            centroid_y = y + height / 3 + (height / 3 if rotation in [180, 270] else 0)
            ax.text(centroid_x, centroid_y, item_id,
                   ha='center', va='center', fontsize=7, fontweight='bold',
                   color='white', bbox=dict(boxstyle='round,pad=0.3', 
                   facecolor='black', alpha=0.5))
        
        else:  # Rectangle or default
            # Draw rectangle
            rect = patches.Rectangle((x, y), width, height,
                                    linewidth=2, edgecolor='yellow',
                                    facecolor=color, alpha=0.8)
            ax.add_patch(rect)
            # Add label
            center_x = x + width / 2
            center_y = y + height / 2
            ax.text(center_x, center_y, item_id,
                   ha='center', va='center', fontsize=8, fontweight='bold',
                   color='white', bbox=dict(boxstyle='round,pad=0.3', 
                   facecolor='black', alpha=0.5))
    
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
    
    def place_item(self, item_id, bin_id, x, y, width, height, shape='Rectangle', price=0, rotation=0):
        """Place an item in the visualization."""
        if bin_id < 1 or bin_id > 4:
            return
        
        bin_idx = bin_id - 1
        ax = self.axes[bin_idx]
        
        # Get color based on item type
        color = self.get_color(item_id, shape)
        
        # Draw the shape with rotation
        self.draw_shape_patch(ax, shape, x, y, width, height, color, item_id, rotation)
        
        # Store item info
        self.bin_items[bin_id].append({
            'id': item_id,
            'shape': shape,
            'x': x, 'y': y,
            'width': width, 'height': height,
            'price': price,
            'rotation': rotation
        })
        
        # Update packed value
        self.packed_value += price
        
        # Update bin info
        items_count = len(self.bin_items[bin_id])
        area_used = sum(calculate_actual_area(item['shape'], item['width'], item['height']) 
                       for item in self.bin_items[bin_id])
        value_packed = sum(item['price'] for item in self.bin_items[bin_id])
        bin_width, bin_height = self.bin_dimensions[bin_id]
        bin_area = bin_width * bin_height
        
        # ax.set_title(f'Bin {bin_id} ({bin_width}×{bin_height}) - Items: {items_count} | Area: {area_used:.1f}/{bin_area} | ${value_packed:.2f}',
        #             fontsize=12, fontweight='bold')
        ax.set_title(f'Bin {bin_id} ({bin_width}×{bin_height}) - Items: {items_count} | Area: {area_used:.1f}/{bin_area}',
                    fontsize=12, fontweight='bold')
        
        # Calculate unpacked value
        unpacked_value = self.total_value - self.packed_value
        
        # self.fig.suptitle(f'Live Bin Packing - Placed {item_id} ({shape}) in Bin {bin_id}! | '
        #                  f'Packed: ${self.packed_value:.2f} | Unpacked: ${unpacked_value:.2f}', 
        #                  fontsize=16, fontweight='bold', color='green')
        self.fig.suptitle(f'Live Bin Packing - Placed {item_id} ({shape}) in Bin {bin_id}!', 
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

def place_item(item_id: str, x: int, y: int, width: int, height: int, shape: str = 'Rectangle', price: float = 0, rotation: int = 0):
    """Places the currently held item at coordinates (x, y) within the current bin."""
    print(f"ACTION: Placing item '{item_id}' ({shape}, {rotation}°) at position (x={x}, y={y}).")
    
    # Update visualization
    if visualizer and visualizer.current_bin:
        visualizer.place_item(item_id, visualizer.current_bin, x, y, width, height, shape, price, rotation)
    
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
    
    # Calculate total value from all items in the plan
    total_value = 0
    for bin_data in packing_plan:
        for item_data in bin_data['items']:
            total_value += item_data.get('price', 0)
    
    # Initialize visualizer
    print("\nInitializing live visualizer...")
    visualizer = LivePackingVisualizer(num_bins=4)
    visualizer.total_value = total_value
    # print(f"Total value of items to pack: ${total_value:.2f}")
    
    # Convert plan to text for the agent
    plan_text = "Execute the following packing plan step-by-step:\n"
    for bin_data in packing_plan:
        plan_text += f"\nFor Bin {bin_data['binId']}:"
        for item_data in bin_data['items']:
            width = item_data.get('width', 0)
            height = item_data.get('height', 0)
            shape = item_data.get('shape', 'Rectangle')
            price = item_data.get('price', 0)
            rotation = item_data.get('rotation', 0)
            # plan_text += f"\n- Place {shape} item {item_data['id']} (size {width}×{height}, ${price:.1f}, {rotation}°) at position (x={item_data['x']}, y={item_data['y']})."
            plan_text += f"\n- Place {shape} item {item_data['id']} (size {width}×{height}, {rotation}°) at position (x={item_data['x']}, y={item_data['y']})."
    
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
                "description": "Places the held item at specific coordinates with its dimensions, shape, and price.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "The item ID."},
                        "x": {"type": "integer", "description": "X coordinate."},
                        "y": {"type": "integer", "description": "Y coordinate."},
                        "width": {"type": "integer", "description": "Item width."},
                        "height": {"type": "integer", "description": "Item height."},
                        "shape": {"type": "string", "description": "Shape type (Rectangle, Circle, Triangle)."},
                        "price": {"type": "number", "description": "Item price."},
                        "rotation": {"type": "integer", "description": "Rotation angle in degrees (0, 90, 180, 270)."}
                    },
                    "required": ["item_id", "x", "y", "width", "height"],
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

