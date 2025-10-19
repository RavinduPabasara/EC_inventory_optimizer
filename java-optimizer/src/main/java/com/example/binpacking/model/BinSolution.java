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
     * Includes ID, shape, coordinates, dimensions, rotation angle, and price.
     */
    public record ItemPlacement(
        @SerializedName("id") String id,
        @SerializedName("shape") String shape,
        @SerializedName("x") int x,
        @SerializedName("y") int y,
        @SerializedName("width") int width,
        @SerializedName("height") int height,
        @SerializedName("rotation") int rotation,
        @SerializedName("price") double price
    ) {}

    /**
     * A factory method to create a BinSolution from a Bin and a list of PlacedItems.
     * This simplifies the creation process and handles the conversion to ItemPlacement.
     */
    public static BinSolution from(Bin bin, List<PlacedItem> placedItems) {
        List<ItemPlacement> placements = placedItems.stream()
            .map(pi -> new ItemPlacement(
                pi.id(),
                pi.item().shape(),
                pi.x(), 
                pi.y(), 
                pi.item().width(), 
                pi.item().height(),
                pi.item().rotation(),
                pi.item().price()
            ))
            .collect(Collectors.toList());
        return new BinSolution(bin.id(), placements);
    }
}