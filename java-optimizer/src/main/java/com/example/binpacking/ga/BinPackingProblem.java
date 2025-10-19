package com.example.binpacking.ga;

import com.example.binpacking.model.Bin;
import com.example.binpacking.model.Item;
import com.example.binpacking.model.PackingResult;
import io.jenetics.*;
import io.jenetics.engine.Codec;
import io.jenetics.engine.Problem;
import io.jenetics.util.ISeq;
import io.jenetics.util.IntRange;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

public class BinPackingProblem implements Problem<List<ItemWithRotation>, IntegerGene, Double> {

    private final ISeq<Item> items;
    private final List<Bin> bins;
    private final FirstFitPlacer placer = new FirstFitPlacer();

    public BinPackingProblem(List<Item> items, List<Bin> bins) {
        this.items = ISeq.of(items);
        this.bins = bins;
    }

    @Override
    public Function<List<ItemWithRotation>, Double> fitness() {
        return itemsWithRotations -> {
            // Convert to items with applied rotations
            List<Item> rotatedItems = new ArrayList<>();
            for (ItemWithRotation iwr : itemsWithRotations) {
                Item item = iwr.item();
                int rotation = iwr.rotation();
                
                // Create item with specified rotation
                Item rotatedItem = new Item(
                    item.id(),
                    item.shape(),
                    item.width(),
                    item.height(),
                    item.canRotate(),
                    item.price(),
                    rotation
                );
                rotatedItems.add(rotatedItem);
            }
            
            PackingResult result = placer.packWithPresetRotations(rotatedItems, bins);
            
            // Primary objectives:
            // 1. Minimize unpacked area (physical constraint)
            // 2. Minimize unpacked value (economic objective - maximize value inside bins)
            double unpackedArea = result.calculateUnpackedArea();
            double unpackedValue = result.calculateUnpackedValue();
            
            // Normalize unpacked value to similar scale as area
            double normalizedValue = unpackedValue / 10.0;
            
            // Small penalty for empty space to prefer tighter packing when other factors are equal
            double emptySpace = result.calculateWastage();
            
            // Combined cost: unpacked area + unpacked value + wastage penalty
            double totalCost = unpackedArea + normalizedValue + (emptySpace * 0.01);
            
            return 1.0 / (1.0 + totalCost);
        };
    }

    @Override
    public Codec<List<ItemWithRotation>, IntegerGene> codec() {
        int n = items.length();
        
        return Codec.of(
            // Single IntegerChromosome with UNIFORM range [0, n-1]
            // First n genes: item indices (used directly)
            // Next n genes: rotation values (use modulo 4 to get 0-3)
            () -> {
                // Create random permutation
                List<Integer> permutation = new ArrayList<>();
                for (int i = 0; i < n; i++) {
                    permutation.add(i);
                }
                java.util.Collections.shuffle(permutation);
                
                // Create genes: permutation + random values for rotations
                List<IntegerGene> genes = new ArrayList<>();
                java.util.Random rand = new java.util.Random();
                
                // Add permutation genes
                for (int idx : permutation) {
                    genes.add(IntegerGene.of(idx, 0, n - 1));
                }
                // Add rotation genes (will use modulo 4 later)
                for (int i = 0; i < n; i++) {
                    genes.add(IntegerGene.of(rand.nextInt(n), 0, n - 1));
                }
                
                return Genotype.of(IntegerChromosome.of(ISeq.of(genes)));
            },
            gt -> {
                // Decode
                IntegerChromosome chromosome = (IntegerChromosome) gt.chromosome();
                
                List<ItemWithRotation> result = new ArrayList<>();
                for (int i = 0; i < n; i++) {
                    int itemIndex = chromosome.get(i).allele();
                    int rotationValue = chromosome.get(n + i).allele();
                    int rotationIndex = rotationValue % 4;  // Convert to 0, 1, 2, or 3
                    int rotation = rotationIndex * 90;  // Convert to degrees
                    
                    Item item = items.get(itemIndex);
                    result.add(new ItemWithRotation(item, rotation));
                }
                return result;
            }
        );
    }
}