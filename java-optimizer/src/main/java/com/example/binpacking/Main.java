package com.example.binpacking;

import com.example.binpacking.ga.BinPackingProblem;
import com.example.binpacking.ga.FirstFitPlacer;
import com.example.binpacking.ga.ItemWithRotation;
import com.example.binpacking.model.*;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import io.jenetics.*;
import io.jenetics.engine.Engine;
import io.jenetics.engine.EvolutionResult;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class Main {
    public static void main(String[] args) {
        System.out.println("Starting bin packing optimization...");

        List<Item> allItems = createAllItems();
        List<Bin> allBins = createAllBins();
        
        System.out.printf("Problem: %d items to pack into %d bins.%n", allItems.size(), allBins.size());
        
        // Show inventory breakdown by shape
        System.out.println("\n=== INVENTORY BY SHAPE ===");
        Map<String, List<Item>> itemsByShape = allItems.stream()
            .collect(Collectors.groupingBy(Item::shape));
        
        itemsByShape.forEach((shape, items) -> {
            Item sample = items.get(0);
            int count = items.size();
            double totalValue = items.stream().mapToDouble(Item::price).sum();
            String rotatable = sample.canRotate() ? "Yes" : "No";
            System.out.printf("  %s: %d items | %d×%d cm | Rotatable: %s | $%.2f each | Total: $%.2f%n",
                shape, count, sample.width(), sample.height(), rotatable, sample.price(), totalValue);
        });

        BinPackingProblem problem = new BinPackingProblem(allItems, allBins);

        var engine = Engine.builder(problem)
                .populationSize(300)
                .survivorsSelector(new TournamentSelector<>(3))
                .offspringSelector(new TournamentSelector<>(3))
                .alterers(
                        new SinglePointCrossover<>(0.7),  // Use SinglePoint instead of PMX for IntegerGene
                        new Mutator<>(0.3)  // Standard mutator for integers
                )
                .build();

        System.out.println("Running Genetic Algorithm for 100 generations...");
        var bestResult = engine.stream()
                .limit(100)
                .peek(result -> {
                    if (result.generation() % 10 == 0) {
                        System.out.printf("Generation %d: Best = %.6f | Worst = %.6f | Avg = %.6f%n",
                                result.generation(), 
                                result.bestFitness(),
                                result.worstFitness(),
                                result.population().stream()
                                    .mapToDouble(p -> p.fitness())
                                    .average()
                                    .orElse(0.0));
                    }
                })
                .collect(EvolutionResult.toBestEvolutionResult());

        System.out.println("\nOptimization finished. Generating final plan...");
        
        // Extract items with rotations from best solution
        var bestSolution = problem.codec().decode(bestResult.bestPhenotype().genotype());
        
        // Convert back to Item list with rotations applied
        List<Item> rotatedItems = bestSolution.stream()
            .map(iwr -> new Item(
                iwr.item().id(),
                iwr.item().shape(),
                iwr.item().width(),
                iwr.item().height(),
                iwr.item().canRotate(),
                iwr.item().price(),
                iwr.rotation()
            ))
            .collect(Collectors.toList());

        PackingResult finalResult = new FirstFitPlacer().packWithPresetRotations(rotatedItems, allBins);
        
        // Calculate and display statistics
        double totalValue = allItems.stream().mapToDouble(Item::price).sum();
        double packedValue = finalResult.calculatePackedValue();
        double unpackedValue = finalResult.calculateUnpackedValue();
        double valuePercentage = (packedValue / totalValue) * 100.0;
        
        System.out.println("\n=== PACKING STATISTICS ===");
        System.out.printf("Total Items: %d%n", allItems.size());
        System.out.printf("Packed Items: %d%n", allItems.size() - finalResult.getUnpackedItems().size());
        System.out.printf("Unpacked Items: %d%n", finalResult.getUnpackedItems().size());
        System.out.println("\n=== VALUE STATISTICS ===");
        System.out.printf("Total Value: $%.2f%n", totalValue);
        System.out.printf("Packed Value: $%.2f (%.1f%%)%n", packedValue, valuePercentage);
        System.out.printf("Unpacked Value: $%.2f%n", unpackedValue);
        System.out.printf("Unpacked Area: %.0f cm²%n", finalResult.calculateUnpackedArea());
        System.out.printf("Wastage (Empty Space): %.0f cm²%n", finalResult.calculateWastage());
        
        // Show rotation statistics for triangles
        long triangleCount = finalResult.getSolutionAsJsonFormat().stream()
            .flatMap(bin -> bin.items().stream())
            .filter(item -> "Triangle".equals(item.shape()))
            .count();
        
        if (triangleCount > 0) {
            System.out.println("\n=== TRIANGLE ROTATION STATISTICS ===");
            Map<Integer, Long> rotationCounts = finalResult.getSolutionAsJsonFormat().stream()
                .flatMap(bin -> bin.items().stream())
                .filter(item -> "Triangle".equals(item.shape()))
                .collect(Collectors.groupingBy(
                    BinSolution.ItemPlacement::rotation,
                    Collectors.counting()
                ));
            
            rotationCounts.forEach((rotation, count) -> 
                System.out.printf("  %d°: %d triangles (%.1f%%)%n", 
                    rotation, count, (count * 100.0 / triangleCount))
            );
        }
        
        // Show unpacked items grouped by shape
        if (!finalResult.getUnpackedItems().isEmpty()) {
            System.out.println("\n=== UNPACKED ITEMS BY SHAPE ===");
            Map<String, List<Item>> unpackedByShape = finalResult.getUnpackedItems().stream()
                .collect(Collectors.groupingBy(Item::shape));
            
            unpackedByShape.forEach((shape, items) -> {
                int count = items.size();
                double shapeValue = items.stream().mapToDouble(Item::price).sum();
                double avgPrice = shapeValue / count;
                System.out.printf("  %s: %d items ($%.2f each) = $%.2f total%n", 
                    shape, count, avgPrice, shapeValue);
            });
        }
        
        String outputFilePath = "../optimized_plan.json"; // Place in parent dir
        try (FileWriter writer = new FileWriter(outputFilePath)) {
            Gson gson = new GsonBuilder().setPrettyPrinting().create();
            gson.toJson(finalResult.getSolutionAsJsonFormat(), writer);
            System.out.println("\nSuccessfully wrote optimized plan to: " + outputFilePath);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static List<Item> createAllItems() {
        List<Item> items = new ArrayList<>();
        
        // A - Rectangle01 - Quantity: 10, Price: $10 each (10x3 cm)
        for (int i = 0; i < 10; i++) {
            items.add(new Item("A_Rectangle01_" + i, "Rectangle", 10, 3, true, 10.0));
        }
        
        // B - Rectangle02 - Quantity: 20, Price: $7.5 each (8x2 cm)
        for (int i = 0; i < 20; i++) {
            items.add(new Item("B_Rectangle02_" + i, "Rectangle", 8, 2, true, 7.5));
        }
        
        // C - Circle - Quantity: 5, Price: $16 each (represented as 5x5 square bounding box)
        for (int i = 0; i < 5; i++) {
            items.add(new Item("C_Circle_" + i, "Circle", 5, 5, false, 16.0));
        }
        
        // D - Right Triangle - Quantity: 100, Price: $3 each (represented as 4x4 square bounding box)
        // Triangles CAN rotate - allows tessellation where two triangles form a square!
        for (int i = 0; i < 100; i++) {
            items.add(new Item("D_RightTriangle_" + i, "Triangle", 4, 4, true, 3.0));
        }
        
        return items;
    }

    private static List<Bin> createAllBins() {
        List<Bin> bins = new ArrayList<>();
        bins.add(new Bin(1, 30, 20));   // 600 cm²
        bins.add(new Bin(2, 25, 20));   // 500 cm²
        bins.add(new Bin(3, 25, 18));   // 450 cm²
        bins.add(new Bin(4, 20, 20));   // 400 cm²
        return bins;                     // Total: 1950 cm² (vs 2345 cm² items - tight fit!)
    }
}