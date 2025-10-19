package com.example.binpacking.ga;

import com.example.binpacking.model.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * A simple, deterministic packer that uses a "First Fit" algorithm.
 * It attempts to place items in the first available position in the first available bin.
 * This class is the "evaluator" for a given item order (a chromosome).
 */
public class FirstFitPlacer {

    public PackingResult pack(List<Item> itemsToPack, List<Bin> bins) {
        // This map will store the final placement of items for each bin.
        Map<Bin, List<PlacedItem>> solutionMap = new HashMap<>();
        for (Bin bin : bins) {
            solutionMap.put(bin, new ArrayList<>());
        }

        List<Item> unpackedItems = new ArrayList<>();

        // For each item in the given order...
        for (Item item : itemsToPack) {
            boolean isPlaced = false;
            // ...try to place it in the first possible bin.
            for (Bin bin : bins) {
                // ...at the first possible position.
                if (tryPlaceItemInBin(item, bin, solutionMap.get(bin))) {
                    isPlaced = true;
                    break; // Move to the next item once placed.
                }
            }
            if (!isPlaced) {
                unpackedItems.add(item);
            }
        }

        return new PackingResult(solutionMap, unpackedItems, bins);
    }

    /**
     * Tries to place a single item into a bin by checking for overlaps with items already in it.
.     * Attempts both original and rotated orientations if rotation is enabled.
     */
    private boolean tryPlaceItemInBin(Item newItem, Bin bin, List<PlacedItem> existingItems) {
        // --- Try placing with original orientation ---
        if (tryPlaceAtBestFit(newItem, bin, existingItems)) {
            return true;
        }

        // --- If it can be rotated and isn't a square, try rotated orientation ---
        if (newItem.canRotate() && newItem.width() != newItem.height()) {
            Item rotatedItem = new Item(newItem.id(), newItem.height(), newItem.width(), newItem.canRotate());
            if (tryPlaceAtBestFit(rotatedItem, bin, existingItems)) {
                return true;
            }
        }
        
        return false; // Could not be placed in either orientation.
    }

    /**
     * Attempts to place an item at the first available position using a simple horizontal scan.
     * A more advanced algorithm could be used here (e.g., skyline, guillotine).
     */
    private boolean tryPlaceAtBestFit(Item itemToPlace, Bin bin, List<PlacedItem> existingItems) {
        // Iterate through all possible y positions, then x positions.
        for (int y = 0; y <= bin.height() - itemToPlace.height(); y++) {
            for (int x = 0; x <= bin.width() - itemToPlace.width(); x++) {
                // Check for collision with existing items at this (x, y) position.
                if (!collides(itemToPlace, x, y, existingItems)) {
                    // No collision, so place the item and return true.
                    existingItems.add(new PlacedItem(itemToPlace, x, y));
                    return true;
                }
            }
        }
        // Could not find a position in this bin.
        return false;
    }

    /**
     * Checks if a new item at a given (x, y) position would overlap with any existing items.
     */
    private boolean collides(Item newItem, int newX, int newY, List<PlacedItem> existingItems) {
        for (PlacedItem placed : existingItems) {
            // Standard Axis-Aligned Bounding Box (AABB) collision detection.
            if (newX < placed.x() + placed.item().width() &&
                newX + newItem.width() > placed.x() &&
                newY < placed.y() + placed.item().height() &&
                newY + newItem.height() > placed.y()) {
                return true; // Collision detected.
            }
        }
        return false; // No collision.
    }
}