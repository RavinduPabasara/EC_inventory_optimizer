package com.example.binpacking.model;

import com.google.gson.annotations.SerializedName;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Represents the final packing solution for a single bin.
 * This class is structured specifically for easy serialization to JSON.
 *
 * @param binId The ID of the bin.
 * @param items A list of items with their final placement coordinates within this bin.
 */
public record BinSolution(
    @SerializedName("binId") int binId,
    @SerializedName("items") List<ItemPlacement> items
) {
    /**
     * A nested record to control the JSON output for each item.
     * Includes ID, coordinates, and actual dimensions (accounting for rotation).
     */
    public record ItemPlacement(
        @SerializedName("id") String id,
        @SerializedName("x") int x,
        @SerializedName("y") int y,
        @SerializedName("width") int width,
        @SerializedName("height") int height
    ) {}

    /**
     * A factory method to create a BinSolution from a Bin and a list of PlacedItems.
     * This simplifies the creation process and handles the conversion to ItemPlacement.
     */
    public static BinSolution from(Bin bin, List<PlacedItem> placedItems) {
        List<ItemPlacement> placements = placedItems.stream()
            .map(pi -> new ItemPlacement(
                pi.id(), 
                pi.x(), 
                pi.y(), 
                pi.item().width(), 
                pi.item().height()
            ))
            .collect(Collectors.toList());
        return new BinSolution(bin.id(), placements);
    }
}