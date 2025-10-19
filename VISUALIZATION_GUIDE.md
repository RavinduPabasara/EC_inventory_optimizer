# Real-time Visualization Guide

## Overview
You now have **two options** for visualizing the bin packing process in real-time:

---

## Option 1: Standalone Real-time Animator 🎬

**File:** `realtime_visualizer.py`

**What it does:** Animates the packing plan from the JSON file, showing each item being placed step-by-step.

**How to use:**
```bash
# First, generate the optimized plan with the Java optimizer
cd java-optimizer
mvn clean compile exec:java

# Then run the real-time visualizer
cd ..
python realtime_visualizer.py
```

**Features:**
- ✅ Shows items being placed one by one
- ✅ Highlights each new item as it's placed
- ✅ Displays progress percentage
- ✅ Shows bin utilization in real-time
- ✅ Saves final image automatically
- ⚡ Fast and doesn't require API calls

**Customization:**
- Change animation speed by editing the `interval` parameter in the `animate()` call (default: 500ms)
- Faster: `interval=200`
- Slower: `interval=1000`

---

## Option 2: Live Executor with Visualization 🤖

**File:** `python-executor/executor_with_viz.py`

**What it does:** Runs the AI agent executor AND shows live visualization as the agent makes decisions.

**How to use:**
```bash
# First, generate the optimized plan
cd java-optimizer
mvn clean compile exec:java

# Then run the executor with live visualization
cd ../python-executor
python executor_with_viz.py
```

**Features:**
- ✅ Shows LIVE updates as the AI agent executes
- ✅ Syncs with actual robot actions (pick, move, place)
- ✅ Highlights current item being handled
- ✅ Shows which bin the robot is moving to
- ✅ Real-time bin statistics
- ✅ Saves final image when complete
- 🤖 Uses OpenAI API to simulate intelligent agent behavior

**Requirements:**
- Needs `.env` file with `OPENAI_API_KEY` in the `python-executor` directory
- Requires OpenAI API credits

---

## Comparison

| Feature | Standalone Animator | Live Executor |
|---------|-------------------|---------------|
| Speed | Fast (no API calls) | Slower (AI agent) |
| Cost | Free | Uses OpenAI API |
| Visualization | Pre-planned sequence | Real AI decisions |
| Best for | Quick preview | Full simulation |
| Setup | Just run it | Needs API key |

---

## Visual Features

Both visualizers include:

- 🎨 **Color-coded items:**
  - 🔴 Type A items (Red)
  - 🔵 Type B items (Teal)
  - 💙 Type C items (Blue)
  - 🟢 Type D items (Green)

- 📊 **Real-time statistics:**
  - Number of items in each bin
  - Area utilization (used/total cm²)
  - Overall progress percentage

- ✨ **Visual effects:**
  - Yellow highlight when items are placed
  - Item labels with IDs
  - Rotation indicators
  - Grid overlay for precision

---

## Example Output

After running either visualizer, you'll see:
- A window with 2×2 grid showing 4 bins
- Items appearing one by one
- Live statistics updating
- Final image saved to disk

**Saved files:**
- Standalone: `bin_packing_animation_final.png`
- Live executor: `live_packing_final.png`

---

## Tips

1. **For quick demos:** Use the standalone animator
2. **For full simulation:** Use the executor with visualization
3. **Slow down animation:** Increase the `plt.pause()` value or `interval` parameter
4. **Speed up animation:** Decrease the pause/interval values
5. **Close window:** The visualization stays open at the end - close it manually when done

---

## Troubleshooting

**Visualizer window not showing:**
- Make sure matplotlib is installed: `pip install matplotlib`
- Try running with `python3` instead of `python`

**"optimized_plan.json not found":**
- Run the Java optimizer first to generate the plan

**API errors in executor:**
- Check your `.env` file has valid `OPENAI_API_KEY`
- Verify you have API credits available

---

Enjoy watching your bins pack themselves! 🎉

