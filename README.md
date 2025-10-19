# EC Inventory Optimizer - Real-time Visualization

A complete bin packing optimization system with real-time visualization capabilities.

## 🚀 Quick Start Guide

### Step 1: Generate the Optimized Packing Plan
```bash
cd java-optimizer
mvn clean compile exec:java
cd ..
```
This creates `optimized_plan.json` with the optimal packing solution.

### Step 2: Choose Your Visualization Method

#### Option A: Fast Real-time Animation (Recommended for demos)
```bash
python realtime_visualizer.py
```
- ✅ **Fast** - No API calls needed
- ✅ **Free** - No OpenAI credits required
- ✅ **Smooth** - Shows items being placed step-by-step
- ✅ **Auto-saves** - Creates `bin_packing_animation_final.png`

#### Option B: Live AI Agent Simulation
```bash
cd python-executor
python executor_with_viz.py
```
- 🤖 **Realistic** - AI agent makes decisions in real-time
- 📊 **Live stats** - Shows bin utilization as it happens
- 💾 **Auto-saves** - Creates `live_packing_final.png`
- ⚠️ **Requires** - OpenAI API key in `.env` file

---

## 📋 Complete Command Sequence

### For First-time Setup:
```bash
# 1. Generate the packing plan
cd java-optimizer
mvn clean compile exec:java
cd ..

# 2. Run the fast visualizer (recommended)
python realtime_visualizer.py
```

### For AI Agent Simulation:
```bash
# 1. Generate the packing plan
cd java-optimizer
mvn clean compile exec:java
cd ..

# 2. Setup OpenAI API (one-time)
cd python-executor
echo "OPENAI_API_KEY=your_api_key_here" > .env
cd ..

# 3. Run the AI agent with visualization
cd python-executor
python executor_with_viz.py
```

---

## 🎯 What You'll See

### Real-time Animation Features:
- **4 bins** arranged in a 2×2 grid (30×10 cm each)
- **Color-coded items:**
  - 🔴 Type A items (10×3 cm) - Red
  - 🔵 Type B items (5×5 cm) - Teal  
  - 💙 Type C items (4×4 cm) - Blue
  - 🟢 Type D items (8×2 cm) - Green
- **Live statistics** showing items count and area utilization
- **Progress tracking** with percentage completion
- **Yellow highlights** for newly placed items

### AI Agent Features:
- **Live robot actions** (pick, move, place)
- **Current item highlighting** as it's being handled
- **Bin switching** with visual feedback
- **Real-time decision making** by the AI agent

---

## 📁 Generated Files

After running either visualizer, you'll get:
- `bin_packing_animation_final.png` - Final static image (Option A)
- `live_packing_final.png` - Final static image (Option B)
- `optimized_plan.json` - The packing plan data

---

## ⚙️ Customization

### Speed Control:
```python
# In realtime_visualizer.py, line ~180
visualizer.animate(interval=200)  # Faster (200ms)
visualizer.animate(interval=1000) # Slower (1000ms)
```

### Visual Settings:
- **Bin size:** 30×10 cm (editable in code)
- **Colors:** Customizable in the `colors` dictionary
- **Animation:** Adjustable pause intervals

---

## 🔧 Troubleshooting

### "optimized_plan.json not found"
```bash
# Make sure you ran the Java optimizer first
cd java-optimizer
mvn clean compile exec:java
cd ..
```

### "OPENAI_API_KEY not found"
```bash
# Create .env file in python-executor directory
cd python-executor
echo "OPENAI_API_KEY=your_actual_api_key" > .env
cd ..
```

### Visualization window not showing
```bash
# Install matplotlib if missing
pip install matplotlib
# Or use python3 instead of python
python3 realtime_visualizer.py
```

### Java compilation issues
```bash
# Make sure Maven is installed
mvn --version
# If not installed: brew install maven (on macOS)
```

---

## 📊 Performance

| Method | Speed | Cost | Realism | Best For |
|--------|-------|------|---------|----------|
| Real-time Animation | ⚡ Fast | 💚 Free | 📋 Pre-planned | Quick demos |
| AI Agent Simulation | 🐌 Slower | 💰 API cost | 🤖 Realistic | Full simulation |


Watch your bins pack themselves in real-time! The visualization shows the optimal solution found by the genetic algorithm, with each item being placed exactly where the algorithm determined it should go.

**Pro tip:** Try both methods to see the difference between a pre-planned animation and a live AI agent making decisions!
