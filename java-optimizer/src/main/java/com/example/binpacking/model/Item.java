package com.example.binpacking.model;

/**
 * Represents a single item to be packed.
 * We use a Java Record for an immutable data carrier.
 *
 * @param id        A unique identifier for the item (e.g., "A_1", "B_5").
 * @param width     The width of the item.
 * @param height    The height of the item.
 * @param canRotate Whether this item can be rotated 90 degrees during packing.
 */
public record Item(String id, int width, int height, boolean canRotate) {
}