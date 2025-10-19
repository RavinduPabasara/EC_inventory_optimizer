package com.example.binpacking.ga;

import com.example.binpacking.model.Bin;
import com.example.binpacking.model.Item;
import com.example.binpacking.model.PackingResult;
import io.jenetics.EnumGene;
import io.jenetics.Genotype;
import io.jenetics.PermutationChromosome;
import io.jenetics.engine.Codec;
import io.jenetics.engine.Problem;
import io.jenetics.util.ISeq;

import java.util.List;
import java.util.function.Function;

public class BinPackingProblem implements Problem<ISeq<Item>, EnumGene<Item>, Double> {

    private final ISeq<Item> items;
    private final List<Bin> bins;
    private final FirstFitPlacer placer = new FirstFitPlacer();

    public BinPackingProblem(List<Item> items, List<Bin> bins) {
        this.items = ISeq.of(items);
        this.bins = bins;
    }

    @Override
    public Function<ISeq<Item>, Double> fitness() {
        return itemOrder -> {
            PackingResult result = placer.pack(itemOrder.asList(), bins);
            // Cost is now the area of items that couldn't be packed
            double unpackedArea = result.calculateUnpackedArea();
            // Small penalty to prefer solutions with less empty space when unpacked area is equal
            double emptySpace = result.calculateWastage();
            double totalCost = unpackedArea + (emptySpace * 0.01);
            return 1.0 / (1.0 + totalCost);
        };
    }

    @Override
    public Codec<ISeq<Item>, EnumGene<Item>> codec() {
        return Codec.of(
            Genotype.of(PermutationChromosome.of(this.items)),
            gt -> {
                PermutationChromosome<Item> chromosome = (PermutationChromosome<Item>) gt.chromosome();
                return chromosome.stream()
                    .map(EnumGene::allele)
                    .collect(ISeq.toISeq());
            }
        );
    }
}