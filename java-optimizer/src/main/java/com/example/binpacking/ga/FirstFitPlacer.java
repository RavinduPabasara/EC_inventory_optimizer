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

    /**
     * Original pack method - tries different rotations automatically
     */
    public PackingResult pack(List<Item> itemsToPack, List<Bin> bins) {
        Map<Bin, List<PlacedItem>> solutionMap = new HashMap<>();
        for (Bin bin : bins) {
            solutionMap.put(bin, new ArrayList<>());
        }

        List<Item> unpackedItems = new ArrayList<>();

        for (Item item : itemsToPack) {
            boolean isPlaced = false;
            for (Bin bin : bins) {
                if (tryPlaceItemInBin(item, bin, solutionMap.get(bin))) {
                    isPlaced = true;
                    break;
                }
            }
            if (!isPlaced) {
                unpackedItems.add(item);
            }
        }

        return new PackingResult(solutionMap, unpackedItems, bins);
    }

    /**
     * New method - uses preset rotations from chromosome (for GA optimization)
     */
    public PackingResult packWithPresetRotations(List<Item> itemsToPack, List<Bin> bins) {
        Map<Bin, List<PlacedItem>> solutionMap = new HashMap<>();
        for (Bin bin : bins) {
            solutionMap.put(bin, new ArrayList<>());
        }

        List<Item> unpackedItems = new ArrayList<>();

        for (Item item : itemsToPack) {
            boolean isPlaced = false;
            // Use the rotation already set in the item (from chromosome)
            for (Bin bin : bins) {
                if (tryPlaceAtBestFit(item, bin, solutionMap.get(bin))) {
                    isPlaced = true;
                    break;
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
     * For rectangles: tries original and 90° rotated
     * For triangles: tries 4 orientations (0°, 90°, 180°, 270°) for tessellation
     */
    private boolean tryPlaceItemInBin(Item newItem, Bin bin, List<PlacedItem> existingItems) {
        // --- Try placing with original orientation ---
        if (tryPlaceAtBestFit(newItem, bin, existingItems)) {
            return true;
        }

        // --- For triangles, try all 4 rotations for tessellation ---
        if (newItem.canRotate() && "Triangle".equals(newItem.shape())) {
            // Try 90°, 180°, 270° rotations
            for (int rotation : new int[]{90, 180, 270}) {
                Item rotatedTriangle = new Item(
                    newItem.id(), 
                    newItem.shape(), 
                    newItem.width(), 
                    newItem.height(), 
                    newItem.canRotate(), 
                    newItem.price(),
                    rotation
                );
                if (tryPlaceAtBestFit(rotatedTriangle, bin, existingItems)) {
                    return true;
                }
            }
        }
        // --- For rectangles, try 90° rotation if not square ---
        else if (newItem.canRotate() && newItem.width() != newItem.height()) {
            Item rotatedItem = new Item(newItem.id(), newItem.shape(), newItem.height(), newItem.width(), newItem.canRotate(), newItem.price());
            if (tryPlaceAtBestFit(rotatedItem, bin, existingItems)) {
                return true;
            }
        }
        
        return false; // Could not be placed in any orientation.
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
     * Special handling for triangles: allows TWO triangles to tessellate in the same bounding box
     * if they have complementary rotations.
     */
    private boolean collides(Item newItem, int newX, int newY, List<PlacedItem> existingItems) {
        for (PlacedItem placed : existingItems) {
            // Check for bounding box overlap
            if (newX < placed.x() + placed.item().width() &&
                newX + newItem.width() > placed.x() &&
                newY < placed.y() + placed.item().height() &&
                newY + newItem.height() > placed.y()) {
                
                // SPECIAL CASE: Triangle tessellation
                // Allow two triangles to occupy the SAME bounding box if they tessellate perfectly
                if ("Triangle".equals(newItem.shape()) && "Triangle".equals(placed.item().shape())) {
                    // Check if they're at the EXACT same position (perfect overlap)
                    if (newX == placed.x() && newY == placed.y() &&
                        newItem.width() == placed.item().width() &&
                        newItem.height() == placed.item().height()) {
                        
                        // Check if rotations are complementary (form a complete square)
                        if (areComplementaryRotations(newItem.rotation(), placed.item().rotation())) {
                            // Count how many triangles are already at this exact position
                            long trianglesAtPosition = existingItems.stream()
                                .filter(p -> "Triangle".equals(p.item().shape()) &&
                                            p.x() == newX && p.y() == newY &&
                                            p.item().width() == newItem.width() &&
                                            p.item().height() == newItem.height())
                                .count();
                            
                            // Allow tessellation if only 1 triangle is there (we'll be the 2nd)
                            if (trianglesAtPosition == 1) {
                                continue; // No collision - allow tessellation!
                            }
                        }
                    }
                }
                
                return true; // Collision detected (no tessellation possible)
            }
        }
        return false; // No collision.
    }
    
    /**
     * Check if two triangle rotations are complementary (can tessellate to form a square).
     * Complementary pairs: (0°, 180°) and (90°, 270°)
     */
    private boolean areComplementaryRotations(int rotation1, int rotation2) {
        // Normalize rotations to 0-360 range
        rotation1 = rotation1 % 360;
        rotation2 = rotation2 % 360;
        
        // Check if they differ by exactly 180°
        int diff = Math.abs(rotation1 - rotation2);
        return diff == 180;
    }
}