package com.example.binpacking.model;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Encapsulates the complete result of a single packing attempt.
 * This object is what the fitness function will evaluate.
 */
public class PackingResult {
    // Maps a Bin to the list of items placed within it.
    private final Map<Bin, List<PlacedItem>> solutionMap;
    private final List<Item> unpackedItems;
    private final List<Bin> originalBins;

    public PackingResult(Map<Bin, List<PlacedItem>> solutionMap, List<Item> unpackedItems, List<Bin> originalBins) {
        this.solutionMap = solutionMap;
        this.unpackedItems = unpackedItems;
        this.originalBins = originalBins;
    }

    public List<Item> getUnpackedItems() {
        return unpackedItems;
    }

    /**
     * Calculates the total wasted space across all bins for this packing solution.
     * Wastage = (Total Area of Bins) - (Total Area of Packed Items)
     * @return The total wastage value.
     */
    public double calculateWastage() {
        double totalBinArea = originalBins.stream().mapToDouble(Bin::getArea).sum();
        double totalItemArea = 0;

        for (List<PlacedItem> itemsInBin : solutionMap.values()) {
            totalItemArea += itemsInBin.stream()
                .mapToDouble(placedItem -> placedItem.item().width() * placedItem.item().height())
                .sum();
        }
        return totalBinArea - totalItemArea;
    }

    /**
     * Converts the internal map representation into the final, clean list of BinSolution
     * objects ready for JSON serialization.
     * @return A list of BinSolution objects.
     */
    public List<BinSolution> getSolutionAsJsonFormat() {
        return solutionMap.entrySet().stream()
                .map(entry -> BinSolution.from(entry.getKey(), entry.getValue()))
                .collect(Collectors.toList());
    }
}