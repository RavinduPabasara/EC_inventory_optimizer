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
                .populationSize(200)
                .survivorsSelector(new TournamentSelector<>(5))
                .offspringSelector(new TournamentSelector<>(5))
                .alterers(
                        new PartiallyMatchedCrossover<>(0.8),
                        new SwapMutator<>(0.1)
                )
                .build();

        System.out.println("Running Genetic Algorithm for 100 generations...");
        Phenotype<EnumGene<Item>, Double> bestPhenotype = engine.stream()
                .limit(100)
                .peek(result -> {
                    if (result.generation() % 10 == 0) {
                        System.out.printf("Generation %d: Best fitness = %.6f%n",
                                result.generation(), result.bestFitness());
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
        for (int i = 0; i < 10; i++) items.add(new Item("A_" + i, 10, 3, true));
        // Squares cannot benefit from rotation
        for (int i = 0; i < 20; i++) items.add(new Item("B_" + i, 5, 5, false));
        for (int i = 0; i < 5; i++)  items.add(new Item("C_" + i, 4, 4, false));
        // Rectangles can be rotated
        for (int i = 0; i < 10; i++) items.add(new Item("D_" + i, 8, 2, true));
        return items;
    }

    private static List<Bin> createAllBins() {
        List<Bin> bins = new ArrayList<>();
        bins.add(new Bin(1, 25, 10));
        bins.add(new Bin(2, 25, 10));
        bins.add(new Bin(3, 25, 10));
        bins.add(new Bin(4, 25, 10));
        return bins;
    }
}