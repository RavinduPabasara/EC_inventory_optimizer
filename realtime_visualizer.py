#!/usr/bin/env python3
"""
Real-time Bin Packing Visualizer
Shows the bin packing process as it happens, step by step.
"""

import json
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
import time

def calculate_actual_area(shape, width, height):
    """Calculate actual area based on shape type."""
    if shape == "Triangle":
        return (width * height) / 2.0  # Right triangle
    elif shape == "Circle":
        radius = min(width, height) / 2.0
        return math.pi * radius * radius  # Inscribed circle
    else:
        return width * height  # Rectangle

class RealtimeVisualizer:
    def __init__(self, packing_plan):
        self.packing_plan = packing_plan
        self.fig, self.axes = plt.subplots(2, 2, figsize=(16, 12))
        self.axes = self.axes.flatten()
        
        # Define bin dimensions: [width, height]
        self.bin_dimensions = {
            1: (30, 20),   # 600 cm²
            2: (25, 20),   # 500 cm²
            3: (25, 18),   # 450 cm²
            4: (20, 20)    # 400 cm²
        }
        
        # Color function for different shapes
        def get_color(item_id, shape):
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
        
        self.get_color = get_color
        
        # Track which items have been placed
        self.current_step = 0
        self.all_placements = []
        
        # Build the list of all placements in order
        for bin_data in packing_plan:
            bin_id = bin_data['binId']
            for item_data in bin_data['items']:
                self.all_placements.append({
                    'bin_id': bin_id,
                    'item_id': item_data['id'],
                    'x': item_data['x'],
                    'y': item_data['y'],
                    'width': item_data['width'],
                    'height': item_data['height'],
                    'shape': item_data.get('shape', 'Rectangle'),
                    'price': item_data.get('price', 0),
                    'rotation': item_data.get('rotation', 0)
                })
        
        # Initialize the plot
        self.setup_plot()
    
    def draw_shape_patch(self, ax, shape, x, y, width, height, color, item_id, price, rotation=0):
        """Draw different shapes based on the shape type with rotation support."""
        if shape == "Circle":
            # Draw a circle inscribed in the bounding box
            center_x = x + width / 2
            center_y = y + height / 2
            radius = min(width, height) / 2
            circle = patches.Circle((center_x, center_y), radius,
                                   linewidth=1, edgecolor='black',
                                   facecolor=color, alpha=0.7)
            ax.add_patch(circle)
            # Add label
            ax.text(center_x, center_y, f"{item_id}\n${price:.1f}",
                   ha='center', va='center', fontsize=7, fontweight='bold')
        
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
                                      linewidth=1, edgecolor='black',
                                      facecolor=color, alpha=0.7)
            ax.add_patch(triangle)
            # Add label at centroid
            centroid_x = x + width / 3 + (width / 3 if rotation in [90, 180] else 0)
            centroid_y = y + height / 3 + (height / 3 if rotation in [180, 270] else 0)
            ax.text(centroid_x, centroid_y, f"{item_id}\n${price:.1f}",
                   ha='center', va='center', fontsize=6, fontweight='bold')
        
        else:  # Rectangle or default
            # Draw rectangle
            rect = patches.Rectangle((x, y), width, height,
                                    linewidth=1, edgecolor='black',
                                    facecolor=color, alpha=0.7)
            ax.add_patch(rect)
            # Add label
            center_x = x + width / 2
            center_y = y + height / 2
            ax.text(center_x, center_y, f"{item_id}\n${price:.1f}",
                   ha='center', va='center', fontsize=7, fontweight='bold')
    
    def setup_plot(self):
        """Setup the initial plot with empty bins."""
        for i, ax in enumerate(self.axes):
            if i < 4:
                bin_id = i + 1
                width, height = self.bin_dimensions[bin_id]
                area = width * height
                
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
                
                # Add info text
                ax.text(width/2, -0.8, f'Items: 0 | Area: 0/{area} cm²', 
                       ha='center', fontsize=9, color='gray')
            else:
                ax.axis('off')
        
        self.fig.suptitle('Real-time Bin Packing Visualization - Starting...', 
                         fontsize=16, fontweight='bold')
        plt.tight_layout()
    
    def update_plot(self, step):
        """Update the plot for a given step."""
        if step >= len(self.all_placements):
            self.fig.suptitle('Real-time Bin Packing Visualization - COMPLETE!', 
                             fontsize=16, fontweight='bold', color='green')
            return
        
        placement = self.all_placements[step]
        bin_idx = placement['bin_id'] - 1
        
        if bin_idx >= 4:
            return
        
        ax = self.axes[bin_idx]
        
        # Get item info
        item_id = placement['item_id']
        shape = placement['shape']
        price = placement['price']
        rotation = placement.get('rotation', 0)
        color = self.get_color(item_id, shape)
        
        # Draw the shape with rotation
        self.draw_shape_patch(ax, shape, placement['x'], placement['y'],
                             placement['width'], placement['height'], 
                             color, item_id, price, rotation)
        
        # Update bin info
        bin_id = placement['bin_id']
        items_in_bin = sum(1 for p in self.all_placements[:step+1] 
                          if p['bin_id'] == bin_id)
        area_used = sum(calculate_actual_area(p['shape'], p['width'], p['height']) 
                       for p in self.all_placements[:step+1] 
                       if p['bin_id'] == bin_id)
        value_in_bin = sum(p['price'] for p in self.all_placements[:step+1] 
                          if p['bin_id'] == bin_id)
        
        bin_width, bin_height = self.bin_dimensions[bin_id]
        bin_area = bin_width * bin_height
        
        # Clear old text and add new
        texts = [t for t in ax.texts if t.get_position()[1] < 0]
        for t in texts:
            t.remove()
        
        ax.text(bin_width/2, -0.8, f'Items: {items_in_bin} | Area: {area_used:.1f}/{bin_area} cm² | Value: ${value_in_bin:.2f}', 
               ha='center', fontsize=9, color='gray')
        
        # Update title
        progress = (step + 1) / len(self.all_placements) * 100
        self.fig.suptitle(
            f'Real-time Bin Packing Visualization - Placing {item_id} in Bin {placement["bin_id"]} '
            f'({step+1}/{len(self.all_placements)} - {progress:.1f}%)', 
            fontsize=16, fontweight='bold'
        )
        
        # After a brief moment, change the highlight to normal border
        plt.pause(0.01)
    
    def animate(self, interval=500, save_gif=False):
        """Animate the packing process."""
        for step in range(len(self.all_placements)):
            self.update_plot(step)
            plt.pause(interval / 1000.0)  # Convert ms to seconds
        
        # Keep the final result displayed
        self.fig.suptitle('Real-time Bin Packing Visualization - COMPLETE!', 
                         fontsize=16, fontweight='bold', color='green')
        
        if save_gif:
            print("Saving final image...")
            plt.savefig('bin_packing_animation_final.png', dpi=150, bbox_inches='tight')
            print("Saved as 'bin_packing_animation_final.png'")
        
        plt.show()

def main():
    """Main function to run the real-time visualizer."""
    print("Loading packing plan...")
    
    try:
        with open('optimized_plan.json', 'r') as f:
            packing_plan = json.load(f)
    except FileNotFoundError:
        print("ERROR: 'optimized_plan.json' not found.")
        print("Please run the Java optimizer first.")
        return
    
    print(f"Found {len(packing_plan)} bins with items to pack.")
    print("Starting real-time visualization...")
    print("(Close the window when done)\n")
    
    visualizer = RealtimeVisualizer(packing_plan)
    
    # Animate with 500ms between each item placement
    # Set to lower value (e.g., 200) for faster animation
    visualizer.animate(interval=500, save_gif=True)

if __name__ == '__main__':
    main()

