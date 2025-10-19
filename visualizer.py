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

def draw_shape_patch(ax, shape, x, y, width, height, color, item_id, price, rotation=0):
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

def create_visualization(packing_plan, output_file='bin_packing_visualization.png'):
    """Create a visual representation of the bin packing solution."""
    
    # Set up the figure with subplots for each bin
    num_bins = len(packing_plan)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    # Color function for different shapes and items
    def get_color(item_data):
        """Get color based on item type and ID."""
        shape = item_data.get('shape', 'Rectangle')
        item_id = item_data['id']
        
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
    
    # Bin dimensions from Main.java
    bin_dimensions = {
        1: (30, 20),   # 600 cm²
        2: (25, 20),   # 500 cm²
        3: (25, 18),   # 450 cm²
        4: (20, 20)    # 400 cm²
    }
    
    # Process each bin
    for bin_idx, bin_data in enumerate(packing_plan):
        if bin_idx >= 4:  # Only show first 4 bins
            break
            
        ax = axes[bin_idx]
        bin_id = bin_data['binId']
        items = bin_data['items']
        
        # Get bin dimensions
        bin_width, bin_height = bin_dimensions.get(bin_id, (40, 25))
        
        # Draw bin outline
        bin_rect = patches.Rectangle((0, 0), bin_width, bin_height, 
                                   linewidth=2, edgecolor='black', 
                                   facecolor='lightgray', alpha=0.3)
        ax.add_patch(bin_rect)
        
        # Track statistics
        total_value = 0
        
        # Draw each item
        for item in items:
            item_id = item['id']
            shape = item.get('shape', 'Rectangle')  # Default to Rectangle if missing
            x, y = item['x'], item['y']
            width, height = item['width'], item['height']
            price = item.get('price', 0)
            total_value += price
            
            # Get rotation angle
            rotation = item.get('rotation', 0)
            
            # Get color for item (distinguishes between Rectangle types)
            color = get_color(item)
            
            # Draw the shape with rotation
            draw_shape_patch(ax, shape, x, y, width, height, color, item_id, price, rotation)
        
        # Set axis properties
        ax.set_xlim(0, bin_width)
        ax.set_ylim(0, bin_height)
        ax.set_aspect('equal')
        ax.set_title(f'Bin {bin_id} | {len(items)} items | ${total_value:.2f}', 
                    fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Width (cm)')
        ax.set_ylabel('Height (cm)')
    
    # Hide unused subplots
    for i in range(num_bins, 4):
        axes[i].set_visible(False)
    
    # Add legend
    legend_elements = [
        patches.Patch(color=colors['Rectangle'], label='Rectangles'),
        patches.Patch(color=colors['Circle'], label='Circles'),
        patches.Patch(color=colors['Triangle'], label='Triangles')
    ]
    fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # Calculate statistics
    total_items = sum(len(bin_data['items']) for bin_data in packing_plan)
    total_value = sum(item.get('price', 0) 
                     for bin_data in packing_plan 
                     for item in bin_data['items'])
    
    # Add main title
    fig.suptitle(f'Bin Packing Optimization Results\n{total_items} items packed | Total Value: ${total_value:.2f}', 
                 fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Visualization saved as: {output_file}")
    print(f"Total items packed: {total_items}")
    print(f"Total value: ${total_value:.2f}")

def calculate_actual_area(shape, width, height):
    """Calculate actual area based on shape type."""
    if shape == "Triangle":
        return (width * height) / 2.0  # Right triangle
    elif shape == "Circle":
        import math
        radius = min(width, height) / 2.0
        return math.pi * radius * radius  # Inscribed circle
    else:
        return width * height  # Rectangle

def analyze_packing(packing_plan):
    """Analyze packing statistics by shape."""
    print("\n=== Packing Analysis by Shape ===")
    
    shape_stats = {}
    
    for bin_data in packing_plan:
        for item in bin_data['items']:
            shape = item.get('shape', 'Unknown')
            price = item.get('price', 0)
            width = item['width']
            height = item['height']
            
            if shape not in shape_stats:
                shape_stats[shape] = {
                    'count': 0,
                    'total_value': 0,
                    'total_area': 0,
                    'bounding_area': 0
                }
            
            shape_stats[shape]['count'] += 1
            shape_stats[shape]['total_value'] += price
            shape_stats[shape]['total_area'] += calculate_actual_area(shape, width, height)
            shape_stats[shape]['bounding_area'] += width * height
    
    for shape, stats in sorted(shape_stats.items()):
        efficiency = (stats['total_area'] / stats['bounding_area'] * 100) if stats['bounding_area'] > 0 else 100
        print(f"{shape}s: {stats['count']} items | "
              f"${stats['total_value']:.2f} value | "
              f"{stats['total_area']:.1f} cm² actual ({efficiency:.0f}% of bounding box)")

if __name__ == "__main__":
    # Load and visualize the packing plan
    packing_plan = load_packing_plan('optimized_plan.json')
    create_visualization(packing_plan)
    analyze_packing(packing_plan)
