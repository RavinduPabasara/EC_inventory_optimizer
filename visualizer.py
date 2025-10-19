#!/usr/bin/env python3
"""
Bin Packing Visualizer
Creates a visual representation of the optimized packing plan.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import numpy as np

def load_packing_plan(file_path):
    """Load the packing plan from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def get_item_dimensions(item_id):
    """Get dimensions for an item based on its ID."""
    # Based on the item creation in Main.java
    if item_id.startswith('A_'):
        return 10, 3  # Original dimensions (will show if rotated)
    elif item_id.startswith('B_'):
        return 5, 5
    elif item_id.startswith('C_'):
        return 4, 4
    elif item_id.startswith('D_'):
        return 8, 2
    return 1, 1  # fallback

def create_visualization(packing_plan, output_file='bin_packing_visualization.png'):
    """Create a visual representation of the bin packing solution."""
    
    # Set up the figure with subplots for each bin
    num_bins = len(packing_plan)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    # Color map for different item types
    colors = {
        'A': '#FF6B6B',  # Red for A items
        'B': '#4ECDC4',  # Teal for B items  
        'C': '#45B7D1',  # Blue for C items
        'D': '#96CEB4'   # Green for D items
    }
    
    # Process each bin
    for bin_idx, bin_data in enumerate(packing_plan):
        if bin_idx >= 4:  # Only show first 4 bins
            break
            
        ax = axes[bin_idx]
        bin_id = bin_data['binId']
        items = bin_data['items']
        
        # Bin dimensions (assuming 25x10 based on Main.java)
        bin_width, bin_height = 25, 10
        
        # Draw bin outline
        bin_rect = patches.Rectangle((0, 0), bin_width, bin_height, 
                                   linewidth=2, edgecolor='black', 
                                   facecolor='lightgray', alpha=0.3)
        ax.add_patch(bin_rect)
        
        # Draw each item
        for item in items:
            item_id = item['id']
            x, y = item['x'], item['y']
            
            # Get original dimensions
            orig_width, orig_height = get_item_dimensions(item_id)
            
            # Determine if item was rotated by checking if it fits in original orientation
            # If the item's position + original dimensions would exceed bin bounds, it was rotated
            if x + orig_width > bin_width or y + orig_height > bin_height:
                # Item was rotated - swap dimensions
                width, height = orig_height, orig_width
                rotation_indicator = " (R)"
            else:
                # Check if there's space for original orientation
                # If not, it was rotated
                width, height = orig_width, orig_height
                rotation_indicator = ""
                
                # Additional check: if item is at a position where original wouldn't fit
                if (item_id.startswith('A_') and (x + 10 > bin_width or y + 3 > bin_height)) or \
                   (item_id.startswith('D_') and (x + 8 > bin_width or y + 2 > bin_height)):
                    width, height = orig_height, orig_width
                    rotation_indicator = " (R)"
            
            # Get color for item type
            item_type = item_id.split('_')[0]
            color = colors.get(item_type, '#CCCCCC')
            
            # Draw item rectangle
            item_rect = patches.Rectangle((x, y), width, height,
                                        linewidth=1, edgecolor='black',
                                        facecolor=color, alpha=0.7)
            ax.add_patch(item_rect)
            
            # Add item label
            ax.text(x + width/2, y + height/2, f"{item_id}{rotation_indicator}", 
                   ha='center', va='center', fontsize=8, fontweight='bold')
        
        # Set axis properties
        ax.set_xlim(0, bin_width)
        ax.set_ylim(0, bin_height)
        ax.set_aspect('equal')
        ax.set_title(f'Bin {bin_id} ({len(items)} items)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Width')
        ax.set_ylabel('Height')
    
    # Hide unused subplots
    for i in range(num_bins, 4):
        axes[i].set_visible(False)
    
    # Add legend
    legend_elements = [
        patches.Patch(color=colors['A'], label='A items (10×3)'),
        patches.Patch(color=colors['B'], label='B items (5×5)'),
        patches.Patch(color=colors['C'], label='C items (4×4)'),
        patches.Patch(color=colors['D'], label='D items (8×2)')
    ]
    fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # Add main title
    total_items = sum(len(bin_data['items']) for bin_data in packing_plan)
    fig.suptitle(f'Bin Packing Optimization Results\n{total_items} items packed across {num_bins} bins', 
                 fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Visualization saved as: {output_file}")
    print(f"Total items packed: {total_items}")

def analyze_rotation_usage(packing_plan):
    """Analyze which items were rotated and provide statistics."""
    print("\n=== Rotation Analysis ===")
    
    rotation_stats = {
        'A': {'total': 0, 'rotated': 0},
        'B': {'total': 0, 'rotated': 0}, 
        'C': {'total': 0, 'rotated': 0},
        'D': {'total': 0, 'rotated': 0}
    }
    
    for bin_data in packing_plan:
        for item in bin_data['items']:
            item_id = item['id']
            item_type = item_id.split('_')[0]
            x, y = item['x'], item['y']
            
            # Get original dimensions
            orig_width, orig_height = get_item_dimensions(item_id)
            
            # Check if rotated
            if x + orig_width > 25 or y + orig_height > 10:
                rotation_stats[item_type]['rotated'] += 1
            rotation_stats[item_type]['total'] += 1
    
    for item_type, stats in rotation_stats.items():
        if stats['total'] > 0:
            rotation_rate = (stats['rotated'] / stats['total']) * 100
            print(f"{item_type} items: {stats['rotated']}/{stats['total']} rotated ({rotation_rate:.1f}%)")

if __name__ == "__main__":
    # Load and visualize the packing plan
    packing_plan = load_packing_plan('optimized_plan.json')
    create_visualization(packing_plan)
    analyze_rotation_usage(packing_plan)
