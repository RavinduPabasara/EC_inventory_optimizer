#!/usr/bin/env python3
"""
Real-time Bin Packing Visualizer
Shows the bin packing process as it happens, step by step.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
import time

class RealtimeVisualizer:
    def __init__(self, packing_plan):
        self.packing_plan = packing_plan
        self.fig, self.axes = plt.subplots(2, 2, figsize=(16, 12))
        self.axes = self.axes.flatten()
        
        # Color map for different item types
        self.colors = {
            'A': '#FF6B6B',  # Red for A items
            'B': '#4ECDC4',  # Teal for B items  
            'C': '#45B7D1',  # Blue for C items
            'D': '#96CEB4'   # Green for D items
        }
        
        # Track which items have been placed
        self.current_step = 0
        self.all_placements = []
        
        # Build the list of all placements in order
        for bin_data in packing_plan:
            bin_id = bin_data['binId']
            for item_data in bin_data['items']:
                # Calculate dimensions based on item ID
                width, height = self.get_item_dimensions(item_data['id'])
                self.all_placements.append({
                    'bin_id': bin_id,
                    'item_id': item_data['id'],
                    'x': item_data['x'],
                    'y': item_data['y'],
                    'width': width,
                    'height': height,
                    'rotated': item_data.get('rotated', False)
                })
        
        # Initialize the plot
        self.setup_plot()
    
    def get_item_type(self, item_id):
        """Extract the item type from item ID (e.g., 'A_0' -> 'A')"""
        return item_id.split('_')[0]
    
    def get_item_dimensions(self, item_id):
        """Get dimensions for an item based on its ID."""
        if item_id.startswith('A_'):
            return 10, 3
        elif item_id.startswith('B_'):
            return 5, 5
        elif item_id.startswith('C_'):
            return 4, 4
        elif item_id.startswith('D_'):
            return 8, 2
        return 1, 1  # fallback
    
    def setup_plot(self):
        """Setup the initial plot with empty bins."""
        for i, ax in enumerate(self.axes):
            if i < 4:
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
                
                # Add info text
                ax.text(15, -1, 'Items: 0 | Area: 0/300 cm²', 
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
        item_type = self.get_item_type(item_id)
        color = self.colors.get(item_type, '#CCCCCC')
        
        # Draw the item with a highlight effect
        rect = patches.Rectangle(
            (placement['x'], placement['y']), 
            placement['width'], 
            placement['height'],
            linewidth=2,
            edgecolor='yellow',  # Highlight with yellow border
            facecolor=color,
            alpha=0.8
        )
        ax.add_patch(rect)
        
        # Add item label
        center_x = placement['x'] + placement['width'] / 2
        center_y = placement['y'] + placement['height'] / 2
        rotation_marker = '↻' if placement['rotated'] else ''
        ax.text(center_x, center_y, f"{item_id}\n{rotation_marker}",
               ha='center', va='center', fontsize=8, fontweight='bold',
               color='white', bbox=dict(boxstyle='round,pad=0.3', 
               facecolor='black', alpha=0.5))
        
        # Update bin info
        items_in_bin = sum(1 for p in self.all_placements[:step+1] 
                          if p['bin_id'] == placement['bin_id'])
        area_used = sum(p['width'] * p['height'] for p in self.all_placements[:step+1] 
                       if p['bin_id'] == placement['bin_id'])
        
        # Clear old text and add new
        texts = [t for t in ax.texts if t.get_position()[1] == -1]
        for t in texts:
            t.remove()
        
        ax.text(15, -1, f'Items: {items_in_bin} | Area: {area_used}/300 cm²', 
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

