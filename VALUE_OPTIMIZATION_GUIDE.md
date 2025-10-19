# Value-Based Bin Packing Optimization

## Overview

The bin packing optimizer has been enhanced with **multi-objective optimization** that considers both physical packing constraints and economic value. The system now:

1. **Minimizes unpacked items** (physical constraint)
2. **Maximizes the value of packed items** (economic objective)

This means if items cannot all fit, the algorithm will prioritize packing high-value items and leave lower-value items unpacked.

---

## Item Configuration

### Current Items and Pricing

| Shape | ID | Quantity | Unit Price | Total Value | Dimensions | Rotatable |
|-------|-----|----------|------------|-------------|------------|-----------|
| **Rectangle01** | A | 10 | $10.00 | $100.00 | 10×3 cm | Yes |
| **Rectangle02** | B | 20 | $7.50 | $150.00 | 8×2 cm | Yes |
| **Circle** | C | 5 | $16.00 | $80.00 | 5×5 cm | No |
| **Right Triangle** | D | 100 | $3.00 | $300.00 | 4×4 cm | No |

**Total Items:** 135  
**Total Value:** $630.00

### Shape Representations

- **Circles** are approximated as 5×5 squares (bounding box)
- **Right Triangles** are approximated as 4×4 squares (bounding box)
- **Rectangles** can be rotated 90° for better packing efficiency

---

## How the Fitness Function Works

### Multi-Objective Cost Function

The genetic algorithm uses the following fitness calculation:

```java
double unpackedArea = result.calculateUnpackedArea();
double unpackedValue = result.calculateUnpackedValue();
double normalizedValue = unpackedValue / 10.0;
double emptySpace = result.calculateWastage();

double totalCost = unpackedArea + normalizedValue + (emptySpace * 0.01);
return 1.0 / (1.0 + totalCost);  // Higher fitness = better solution
```

### Component Breakdown

1. **Unpacked Area** (primary constraint)
   - Total cm² of items that couldn't be packed
   - Minimizing this ensures we pack as many items as possible

2. **Unpacked Value** (economic objective)
   - Total dollar value of items left outside bins
   - Normalized by dividing by 10 to balance with area metric
   - Prioritizes packing expensive items over cheap ones

3. **Empty Space Penalty** (tertiary optimization)
   - Weighted at 0.01× to be a minor tiebreaker
   - Prefers tighter packing when other factors are equal

### Priority Hierarchy

The algorithm optimizes in this order:
1. Pack as much total area as possible
2. Among solutions with similar packed area, maximize packed value
3. Among solutions with similar area and value, minimize waste

---

## Genetic Algorithm Configuration

### Optimized Parameters

```java
Population Size: 300        // Increased for better diversity
Tournament Size: 3          // Reduced for less selection pressure
Crossover Rate: 0.7 (70%)  // Partially Matched Crossover
Mutation Rate: 0.3 (30%)   // Swap Mutator - HIGH for exploration
Generations: 100
```

### Why These Settings?

- **High mutation rate (30%)** prevents premature convergence
- **Smaller tournament (3)** maintains population diversity longer
- **Larger population (300)** explores more solution space
- These settings allow continuous improvement across all 100 generations

---

## Output Statistics

When the optimizer completes, it displays:

```
=== PACKING STATISTICS ===
Total Items: 135
Packed Items: 127
Unpacked Items: 8

=== VALUE STATISTICS ===
Total Value: $630.00
Packed Value: $606.00 (96.2%)
Unpacked Value: $24.00
Unpacked Area: 128 cm²
Wastage (Empty Space): 142 cm²
```

### Key Metrics

- **Packed Value %**: Percentage of total value successfully packed
- **Unpacked Value**: Dollar value left outside (should be minimized)
- **Unpacked Area**: Physical area that didn't fit
- **Wastage**: Empty space inside bins (efficiency metric)

---

## Optimization Strategy

### Value-Driven Packing

The genetic algorithm evolves item ordering to:

1. **Try high-value items first** in the packing sequence
2. **Leave low-value items for last** (more likely to be unpacked)
3. **Balance between quantity and value**
   - 1× Circle ($16) might be preferred over 2× Right Triangles ($6 total)
   - But area constraints still matter

### Example Scenario

Given limited bin space:
- **Good:** Pack 5 Circles ($80) + 10 Rectangle01s ($100) = $180
- **Bad:** Pack 40 Right Triangles ($120) leaving expensive items out

The GA learns to find orderings that maximize the value of what fits.

---

## Running the Optimizer

### Compile and Run

```bash
cd java-optimizer
mvn clean compile exec:java
```

### Expected Behavior

You should see evolution progress:

```
Generation 10: Best = 0.004513 | Worst = 0.003201 | Avg = 0.003845
Generation 20: Best = 0.004827 | Worst = 0.003312 | Avg = 0.003921
Generation 30: Best = 0.005104 | Worst = 0.003498 | Avg = 0.004102
...
Generation 100: Best = 0.006215 | Worst = 0.004102 | Avg = 0.005089
```

**Fitness should continue improving throughout** (not flatline after gen 10).

---

## Customization

### Adjusting the Value Weight

To change how much the algorithm prioritizes value vs. area, modify the normalization factor in `BinPackingProblem.java`:

```java
// Current: Equal weight to area and value
double normalizedValue = unpackedValue / 10.0;

// Prioritize value more (make it "costlier" to leave out)
double normalizedValue = unpackedValue / 5.0;

// Prioritize area more (value matters less)
double normalizedValue = unpackedValue / 20.0;
```

### Adding New Items

Update `Main.createAllItems()`:

```java
// Format: id, width, height, canRotate, price
items.add(new Item("E_Square_0", 6, 6, false, 12.0));
```

---

## Technical Implementation

### Modified Files

1. **`Item.java`** - Added `price` field to the record
2. **`PackingResult.java`** - Added `calculateUnpackedValue()` and `calculatePackedValue()` methods
3. **`BinPackingProblem.java`** - Updated fitness function to consider value
4. **`FirstFitPlacer.java`** - Fixed rotation logic to preserve price
5. **`Main.java`** - Updated item creation and added value statistics output

### Key Methods

```java
// Calculate total value of unpacked items
public double calculateUnpackedValue() {
    return unpackedItems.stream()
            .mapToDouble(Item::price)
            .sum();
}

// Calculate total value of packed items
public double calculatePackedValue() {
    return solutionMap.values().stream()
            .flatMap(List::stream)
            .mapToDouble(placedItem -> placedItem.item().price())
            .sum();
}
```

---

## Benefits of Value-Based Optimization

✅ **Economic Efficiency**: Maximize revenue from packed items  
✅ **Smart Prioritization**: High-value items packed first  
✅ **Business-Aware**: Consider both physical and financial constraints  
✅ **Transparent**: Clear reporting of value metrics  
✅ **Flexible**: Easy to adjust value vs. area priority

---

## Next Steps

1. **Run Multiple Times**: Compare results across runs
2. **Adjust Weights**: Tune the value normalization factor
3. **Visualize**: Use the Python visualizer to see packed items
4. **Analyze**: Check which item types are being left out

The optimizer will naturally evolve to leave out lower-value items (like Right Triangles at $3 each) when space is limited, preferring to pack higher-value items (like Circles at $16 each).

