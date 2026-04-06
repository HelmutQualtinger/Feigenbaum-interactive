# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Feigenbaum** is an interactive visualization of the logistic map equation and its bifurcation diagram. It shows how the dynamics of the equation Xₙ₊₁ = r · Xₙ · (1 - Xₙ) change as the parameter r varies from 0 to 4, leading to the famous Feigenbaum bifurcation cascade.

**Stack**: Python + Dash (interactive web framework) + Plotly (visualization) + NumPy (numerical computation)

## Quick Start

```bash
# Run the app (runs on http://127.0.0.1:8050)
python3 app.py
```

The server runs in debug mode and will auto-reload on file changes.

## Architecture

### File Structure
- **app.py** - Main application file (only file, ~220 lines)
  - Pre-calculated Feigenbaum diagram (computed once at startup for performance)
  - Dash layout with two-column design
  - Single callback (`update_graphs`) that generates plots when slider moves

### Layout & Visualization

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
  - **Alignment**: slider padding (30px) is tuned to align with graph margins (80px)

### Key Design Decisions

1. **Pre-calculated Feigenbaum diagram** - Computed at app startup (`feigenbaum_x_cached`, `feigenbaum_y_cached`) to keep slider interactions responsive. Without this, the slider would lag.

2. **Two separate figures** - `fig_left` (cobweb + sequence) and `fig_right` (Feigenbaum) are returned from the callback. This allows optimal layout and prevents re-rendering unnecessarily.

3. **Animation frames** - Cobweb spirals animate frame-by-frame to show iteration progression. The `Play` button triggers the animation (50ms per frame).

4. **Dual starting points** - Red (0.05) and blue (0.90) trajectories show that different initial conditions converge to the same attractor, illustrating chaos theory principles.

## Common Development Tasks

### Modifying the visualization

- **Change iteration counts**: See lines 63-64 (`iterations` for cobweb, `iterations_long` for sequence)
- **Adjust Feigenbaum resolution**: Change 500 in line 10 (r-steps) or line 18 (attractors per r)
- **Change starting points**: Lines 65-66 (red/blue starting values)
- **Modify colors**: Lines 127, 134 (cobweb spirals), 193 (Feigenbaum), 200 (red line)

### Adjusting layout/alignment

- **Graph margins**: Lines 175, 208 (affects red line and slider alignment)
- **Slider padding**: Line 48 (padding adjustment)
- **Column widths**: Lines 35, 49 (48% + 50% split)
- **Heights**: Lines 34, 39 (700px and 600px)

### Performance tuning

The biggest bottleneck is **Feigenbaum pre-calculation** at app startup. For faster startup:
- Reduce r-steps from 500 to fewer (e.g., 300)
- Reduce attractors from 100 to fewer (e.g., 50)

The callback (`update_graphs`) is called on every slider change and is very fast because:
- Feigenbaum is cached (not recalculated)
- Cobweb/sequence calculations are O(n) with small n (50-100 iterations)

## Dependencies

- **dash**: Web framework and interactive callbacks
- **plotly**: Graph rendering (via `go.Figure` and `make_subplots`)
- **numpy**: Numerical arrays and calculations

See `pyproject.toml` for versions.

## Notes for Future Work

- The animation frame calculation (line 156) uses `iterations * 1` which seems odd — may want to clarify this constant.
- English/German language mix in comments (e.g., "Linke Spalte", "Attraktor") — consider standardizing.
- Currently hard-coded for logistic map; could be made more generic for other chaotic systems.
