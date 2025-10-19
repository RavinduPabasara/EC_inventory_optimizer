package com.example.binpacking.model;

/**
 * Represents a single item to be packed.
 * We use a Java Record for an immutable data carrier.
 *
 * @param id        A unique identifier for the item (e.g., "A_1", "B_5").
 * @param shape     The actual shape type (e.g., "Rectangle", "Circle", "Triangle").
 * @param width     The width of the item (bounding box).
 * @param height    The height of the item (bounding box).
 * @param canRotate Whether this item can be rotated 90 degrees during packing.
 * @param price     The price/value of this individual item.
 * @param rotation  The rotation angle in degrees (0, 90, 180, 270) for triangles.
 */
public record Item(String id, String shape, int width, int height, boolean canRotate, double price, int rotation) {
    // Convenience constructor for non-rotated items
    public Item(String id, String shape, int width, int height, boolean canRotate, double price) {
        this(id, shape, width, height, canRotate, price, 0);
    }
    
    /**
     * Calculates the actual area of the item based on its shape.
     * - Rectangle: width × height
     * - Circle: π × r² (approximated as 0.785 × width × height for inscribed circle)
     * - Triangle: (width × height) / 2 (right triangle)
     */
    public double actualArea() {
        return switch (shape) {
            case "Triangle" -> (width * height) / 2.0;  // Right triangle is half the bounding box
            case "Circle" -> Math.PI * Math.pow(Math.min(width, height) / 2.0, 2);  // Inscribed circle
            default -> width * height;  // Rectangle or unknown
        };
    }
}