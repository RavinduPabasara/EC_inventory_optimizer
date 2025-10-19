package com.example.binpacking.model;

/**
 * Represents an item that has been placed into a bin.
 * It combines the original item with its final (x, y) coordinates.
 * This is a key part of the final solution data structure.
 *
 * @param item The original item object.
 * @param x    The x-coordinate of the item's top-left corner within the bin.
 * @param y    The y-coordinate of the item's top-left corner within the bin.
 */
public record PlacedItem(Item item, int x, int y) {

    // Convenience method to get the item's ID directly.
    public String id() {
        return item.id();
    }
}