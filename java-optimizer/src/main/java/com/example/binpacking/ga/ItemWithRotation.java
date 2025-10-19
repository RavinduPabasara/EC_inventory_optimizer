package com.example.binpacking.ga;

import com.example.binpacking.model.Item;

/**
 * Represents an item with its assigned rotation from the chromosome.
 * Used by the genetic algorithm to encode both item order and rotation.
 */
public record ItemWithRotation(Item item, int rotation) {
}

