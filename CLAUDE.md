# CLAUDE.md

This file provides guidance to Claude Code (Clause.ai/code) when working with code in this repository.

## Project Overview

**Feigenbaum** is an interactive visualization of the logistic map equation and its bifurcation diagram. It shows how the dynamics of the equation Xₙ₊₁ = r · Xₙ · (1 - Xₙ) change as the parameter r varies from 0 to 4, leading to the famous Feigenbaum bifurcation cascade.

Two implementations are available:
1. **`index.html`** - Pure JavaScript/HTML (no server required, runs in browser)
2. **`app.py`** - Python/Dash web application (interactive server)

## Quick Start

### JavaScript Version (Recommended for Quick Testing)
```bash
# Just open in browser
open index.html
```

### Python Version (Interactive Development)
```bash
# Run the server (runs on http://127.0.0.1:8050)
python3 app.py
```
The server runs in debug mode and will auto-reload on file changes.

## Architecture

### JavaScript/HTML Version (`index.html`)

**File Structure:**
- Single HTML file (~500 lines) with embedded CSS and JavaScript
- Pure client-side implementation (no build tools, no server required)
- Uses Plotly.js from CDN for visualization

**Core Logic:**
1. **On page load:**
   - Compute Feigenbaum diagram (500 r-steps × 100 attractors = 50,000 points)
   - Pre-cache 41 cobweb plots at regular r intervals
   - Display loading spinner during computation (~5 seconds)

2. **On slider change:**
   - Retrieve or compute cobweb data for current r value
   - Update both plots via Plotly.newPlot()
   - Animation frames computed on-demand in JavaScript

3. **On Play button:**
   - Animate cobweb spirals and iteration sequence frame-by-frame
   - Use Plotly.restyle() to update traces (fast visual updates)
   - 50 animation steps at 200ms per frame

**Configuration:**
```javascript
const CONFIG = {
    r_steps: 500,           // Feigenbaum resolution
    transient_iterations: 500,  // Discard transients
    attractor_points: 100,  // Points per r-value
    cobweb_iterations: 100, // Spiral length
    animation_steps: 50     // Frames in Play animation
};
```

**Performance:**
- Initial load: ~5 seconds (computing Feigenbaum)
- Slider response: ~100ms (retrieving cached or computing cobweb)
- Animation: 200ms per frame
- File size: ~14 KB HTML (Plotly.js loaded from CDN)

### Python/Dash Version (`app.py`)

**File Structure:**
- **app.py** - Main application file (~220 lines)
  - Pre-calculated Feigenbaum diagram (computed once at startup for performance)
  - Dash layout with two-column design
  - Single callback (`update_graphs`) that generates plots when slider moves

**Layout & Visualization**

The UI is a **two-column layout**:

**Left Column (48% width):**
- Top: Cobweb diagram (interactive, animatable)
  - Shows two starting points (red: 0.05, blue: 0.90) converging to attractors
  - Can click "Play" button to animate the iteration spirals
- Bottom: Xₙ sequence plot (0-100 iterations)
  - Red and blue lines show convergence behavior over time

**Right Column (50% width):**
- Top: Feigenbaum bifurcation diagram (0-4 on r axis)
  - Red dashed vertical line shows current r value (linked to slider)
  - Pre-computed with 500 r-steps and 100 attractors per r-value
- Bottom: Slider to control r parameter (0.0 to 4.0, step 0.01)

**Key Design Decisions:**

1. **Pre-calculated Feigenbaum diagram** - Computed at app startup to keep slider interactions responsive

2. **Two separate figures** - `fig_left` (cobweb + sequence) and `fig_right` (Feigenbaum) are returned from the callback

3. **Deep copy for thread safety** - Uses `copy.deepcopy()` instead of shallow copy to prevent race conditions in multi-user deployments (e.g., Gunicorn)

4. **Dual starting points** - Red (0.05) and blue (0.90) trajectories show that different initial conditions converge to the same attractor

## Common Development Tasks

### JavaScript/HTML Version (`index.html`)

**Modifying computation:**

- **Feigenbaum resolution**: Edit `CONFIG.r_steps` (higher = more detail, slower startup)
- **Transient iterations**: Edit `CONFIG.transient_iterations` (higher = more stable)
- **Attractor points**: Edit `CONFIG.attractor_points` (higher = denser bifurcation diagram)
- **Cobweb length**: Edit `CONFIG.cobweb_iterations`
- **Animation speed**: Edit `CONFIG.animation_frame_duration` (milliseconds per frame)

**Modifying visualization:**

- **Colors**: Change `color: 'red'`, `'blue'`, `'green'` in trace definitions (~line 270-300)
- **Plot heights**: Edit `height: 480` in layout (~line 380, 415)
- **Font sizes**: Search for `titlefont: { size: 10 }` in layout definitions

**Theme:**

- **Color scheme**: Update CSS variables in `<style>` tag (dark blue `#2c3e50`, light background `#f8f9fa`)
- **Typography**: Change `font-family: 'Georgia'` for different fonts
- **Spacing**: Edit `padding`, `margin`, `gap` in CSS

### Python/Dash Version - Development Tasks

**Modifying the visualization:**

- **Change iteration counts**: See lines 84-85 (`iterations` for cobweb, `iterations_long` for sequence)
- **Adjust Feigenbaum resolution**: Change 500 in line 10 (r-steps) or 100 in lines 18 (attractors per r)
- **Change starting points**: Lines 86-87 (red/blue starting values)
- **Modify colors**: Search for `line=dict(color=...)` and `marker=dict(color=...)`

**Performance tuning:**

The biggest bottleneck in both versions is **Feigenbaum pre-calculation**. For faster startup:

- Reduce `r_steps` from 500 to fewer (e.g., 300)
- Reduce `attractor_points` from 100 to fewer (e.g., 50)

## Dependencies

### JavaScript/HTML Version

- **Plotly.js** - Loaded from CDN (<https://cdn.plot.ly/plotly-latest.min.js>)
- No build tools or npm packages required
- Works with just a modern web browser (Chrome, Firefox, Safari, Edge)

### Python/Dash Version


- **dash**: Web framework and interactive callbacks
- **plotly**: Graph rendering (via `go.Figure` and `make_subplots`)
- **numpy**: Numerical arrays and calculations

See `pyproject.toml` for Python package versions.

## Notes for Future Work

- **JavaScript version**: Could add export/screenshot functionality (save PNG of current state)
- **Python version**: Consider making more generic for other chaotic systems beyond logistic map
- **Both versions**: Consider language toggle between English and German for explanatory text
- **Documentation**: Add more interactive tooltips explaining the mathematics in real-time
