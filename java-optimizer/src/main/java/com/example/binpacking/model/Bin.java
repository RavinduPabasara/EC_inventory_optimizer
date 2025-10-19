package com.example.binpacking.model;

/**
 * Represents a single bin in the inventory space.
 *
 * @param id     A unique identifier for the bin (e.g., 1, 2, 3).
 * @param width  The width of the bin.
 * @param height The height of the bin.
 */
public record Bin(int id, int width, int height) {

    /**
     * Calculates the total area of the bin.
     * @return The area (width * height).
     */
    public int getArea() {
        return width * height;
    }
}