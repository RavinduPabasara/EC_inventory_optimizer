package com.example.binpacking;

import com.example.binpacking.ga.BinPackingProblem;
import com.example.binpacking.ga.FirstFitPlacer;
import com.example.binpacking.model.*;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import io.jenetics.EnumGene;
import io.jenetics.Phenotype;
import io.jenetics.PartiallyMatchedCrossover;
import io.jenetics.SwapMutator;
import io.jenetics.TournamentSelector;
import io.jenetics.engine.Engine;
import io.jenetics.engine.EvolutionResult;
import io.jenetics.util.ISeq;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        System.out.println("Starting bin packing optimization...");

        List<Item> allItems = createAllItems();
        List<Bin> allBins = createAllBins();
        
        System.out.printf("Problem: %d items to pack into %d bins.%n", allItems.size(), allBins.size());

        BinPackingProblem problem = new BinPackingProblem(allItems, allBins);

        Engine<EnumGene<Item>, Double> engine = Engine.builder(problem)
                .populationSize(300)
                .survivorsSelector(new TournamentSelector<>(3))
                .offspringSelector(new TournamentSelector<>(3))
                .alterers(
                        new PartiallyMatchedCrossover<>(0.7),
                        new SwapMutator<>(0.3)
                )
                .build();

        System.out.println("Running Genetic Algorithm for 100 generations...");
        Phenotype<EnumGene<Item>, Double> bestPhenotype = engine.stream()
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
                .collect(EvolutionResult.toBestPhenotype());

        System.out.println("\nOptimization finished. Generating final plan...");
        
        // Correctly extract the sequence from the best gene
        ISeq<Item> bestOrder = bestPhenotype.genotype().gene().validAlleles();

        PackingResult finalResult = new FirstFitPlacer().pack(bestOrder.asList(), allBins);
        
        String outputFilePath = "../optimized_plan.json"; // Place in parent dir
        try (FileWriter writer = new FileWriter(outputFilePath)) {
            Gson gson = new GsonBuilder().setPrettyPrinting().create();
            gson.toJson(finalResult.getSolutionAsJsonFormat(), writer);
            System.out.println("Successfully wrote optimized plan to: " + outputFilePath);
            if (!finalResult.getUnpackedItems().isEmpty()) {
                System.out.println("WARNING: " + finalResult.getUnpackedItems().size() + " items could not be packed.");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static List<Item> createAllItems() {
        List<Item> items = new ArrayList<>();
        // Rectangles can be rotated for better packing efficiency
        for (int i = 0; i < 30; i++) items.add(new Item("A_" + i, 10, 3, true));
        // Squares cannot benefit from rotation
        for (int i = 0; i < 50; i++) items.add(new Item("B_" + i, 5, 5, false));
        for (int i = 0; i < 20; i++)  items.add(new Item("C_" + i, 4, 4, false));
        // Rectangles can be rotated
        for (int i = 0; i < 40; i++) items.add(new Item("D_" + i, 8, 2, true));
        return items;
    }

    private static List<Bin> createAllBins() {
        List<Bin> bins = new ArrayList<>();
        bins.add(new Bin(1, 40, 25));   // 1000 cm²
        bins.add(new Bin(2, 35, 20));   // 700 cm²
        bins.add(new Bin(3, 30, 25));   // 750 cm²
        bins.add(new Bin(4, 30, 20));   // 600 cm²
        return bins;                     // Total: 3050 cm²
    }
}