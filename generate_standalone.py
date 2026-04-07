#!/usr/bin/env python3
"""
Generate a standalone, interactive HTML file for the Feigenbaum bifurcation diagram.
No server required - opens directly in browser with client-side animation.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# Pre-calculate Feigenbaum diagram
print("Calculating Feigenbaum diagram...")
r_values_feig = np.linspace(0.0, 4.0, 500)
feigenbaum_x = []
feigenbaum_y = []

for r_val in r_values_feig:
    x = 0.1
    for _ in range(500):  # Transient
        x = r_val * x * (1 - x)
    for _ in range(100):  # 100 points per r-value
        x = r_val * x * (1 - x)
        feigenbaum_x.append(r_val)
        feigenbaum_y.append(x)

# Create base Feigenbaum figure
feigenbaum_fig = go.Figure()
feigenbaum_fig.add_trace(go.Scatter(
    x=feigenbaum_x, y=feigenbaum_y,
    mode='markers', name='Feigenbaum',
    marker=dict(size=2, color='steelblue'), showlegend=False
))
feigenbaum_fig.update_xaxes(range=[0.0, 4.0], title_text="r")
feigenbaum_fig.update_yaxes(range=[0, 1], title_text="Attraktor")
feigenbaum_fig.update_layout(
    template="plotly_white",
    height=700,
    margin=dict(l=80, r=80, t=40, b=50),
    showlegend=False
)

# Generate cobweb plots for all slider positions (no embedded frames to keep size small)
print("Generating cobweb plots for all r values...")
r_slider_values = np.arange(0.0, 4.01, 0.01)
cobweb_data = {}

for i, r in enumerate(r_slider_values):
    if i % 50 == 0:
        print(f"  {i}/{len(r_slider_values)}")

    x_val = np.linspace(0, 1, 100)
    y_val = r * x_val * (1 - x_val)

    iterations = 100
    iterations_long = 100
    x_start_red = 0.05
    x_start_blue = 0.90

    # Red spiral
    cobweb_x_red = []
    cobweb_y_red = []
    current_x = x_start_red
    for _ in range(iterations):
        next_x = r * current_x * (1 - current_x)
        cobweb_x_red.extend([current_x, current_x])
        cobweb_y_red.extend([current_x, next_x])
        cobweb_x_red.append(next_x)
        cobweb_y_red.append(next_x)
        current_x = next_x

    # Blue spiral
    cobweb_x_blue = []
    cobweb_y_blue = []
    current_x = x_start_blue
    for _ in range(iterations):
        next_x = r * current_x * (1 - current_x)
        cobweb_x_blue.extend([current_x, current_x])
        cobweb_y_blue.extend([current_x, next_x])
        cobweb_x_blue.append(next_x)
        cobweb_y_blue.append(next_x)
        current_x = next_x

    # Sequences
    sequence_red = []
    current_x = x_start_red
    for _ in range(iterations_long):
        sequence_red.append(current_x)
        current_x = r * current_x * (1 - current_x)
    sequence_red.append(current_x)

    sequence_blue = []
    current_x = x_start_blue
    for _ in range(iterations_long):
        sequence_blue.append(current_x)
        current_x = r * current_x * (1 - current_x)
    sequence_blue.append(current_x)

    # Store raw data for this r (used for client-side animation)
    cobweb_data[f"{r:.2f}"] = {
        "r": r,
        "x_func": x_val.tolist(),
        "y_func": y_val.tolist(),
        "cobweb_x_red": cobweb_x_red,
        "cobweb_y_red": cobweb_y_red,
        "cobweb_x_blue": cobweb_x_blue,
        "cobweb_y_blue": cobweb_y_blue,
        "sequence_red": sequence_red,
        "sequence_blue": sequence_blue
    }

# Create HTML with client-side animation
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Feigenbaum Bifurcation Diagram</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2 {{
            margin-bottom: 20px;
        }}
        .layout {{
            display: flex;
            gap: 20px;
        }}
        .left-column {{
            width: 48%;
            position: relative;
        }}
        .right-column {{
            width: 50%;
        }}
        #cobweb-plot, #feigenbaum-plot {{
            width: 100%;
        }}
        .play-button {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            z-index: 10;
        }}
        .play-button:hover {{
            background: #45a049;
        }}
        .slider-container {{
            padding: 0 30px 15px 30px;
            box-sizing: border-box;
        }}
        label {{
            font-weight: bold;
            margin-bottom: 10px;
            display: block;
        }}
        input[type="range"] {{
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
        }}
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #4CAF50;
            cursor: pointer;
        }}
        input[type="range"]::-moz-range-thumb {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #4CAF50;
            cursor: pointer;
            border: none;
        }}
        .value-display {{
            margin-top: 10px;
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Logistische Gleichung: X<sub>n+1</sub> = r · X<sub>n</sub> · (1 - X<sub>n</sub>)</h2>

        <div class="layout">
            <div class="left-column">
                <button class="play-button" onclick="playAnimation()">Play</button>
                <div id="cobweb-plot"></div>
            </div>

            <div class="right-column">
                <div id="feigenbaum-plot"></div>
                <div class="slider-container">
                    <label for="r-slider">Parameter r:</label>
                    <input type="range" id="r-slider" min="0" max="400" step="1" value="280">
                    <div class="value-display">r = <span id="r-value">2.80</span></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Feigenbaum diagram data
        const feigenbaum_json = {feigenbaum_fig.to_json()};

        // Cobweb data for all r values
        const cobweb_data = {json.dumps(cobweb_data)};

        let current_r = 2.80;
        let isAnimating = false;

        // Create figure for current r value
        function createCobwebFigure(data) {{
            const fig = {{
                data: [
                    {{
                        x: data.x_func,
                        y: data.y_func,
                        mode: 'lines',
                        name: 'f(x) = r*x(1-x)',
                        line: {{ color: 'green' }},
                        xaxis: 'x',
                        yaxis: 'y'
                    }},
                    {{
                        x: [0, 1],
                        y: [0, 1],
                        mode: 'lines',
                        name: 'y = x',
                        line: {{ color: 'black', dash: 'dash' }},
                        xaxis: 'x',
                        yaxis: 'y'
                    }},
                    {{
                        x: data.cobweb_x_red,
                        y: data.cobweb_y_red,
                        mode: 'lines+markers',
                        name: 'Start: 0.05',
                        line: {{ color: 'red', width: 1 }},
                        marker: {{ size: 4 }},
                        xaxis: 'x',
                        yaxis: 'y'
                    }},
                    {{
                        x: data.cobweb_x_blue,
                        y: data.cobweb_y_blue,
                        mode: 'lines+markers',
                        name: 'Start: 0.90',
                        line: {{ color: 'blue', width: 1 }},
                        marker: {{ size: 4 }},
                        xaxis: 'x',
                        yaxis: 'y'
                    }},
                    {{
                        x: Array.from({{length: data.sequence_red.length}}, (_, i) => i),
                        y: data.sequence_red,
                        mode: 'lines+markers',
                        name: 'Start: 0.05',
                        line: {{ color: 'red', width: 2 }},
                        marker: {{ size: 3 }},
                        showlegend: false,
                        xaxis: 'x2',
                        yaxis: 'y2'
                    }},
                    {{
                        x: Array.from({{length: data.sequence_blue.length}}, (_, i) => i),
                        y: data.sequence_blue,
                        mode: 'lines+markers',
                        name: 'Start: 0.90',
                        line: {{ color: 'blue', width: 2 }},
                        marker: {{ size: 3 }},
                        showlegend: false,
                        xaxis: 'x2',
                        yaxis: 'y2'
                    }}
                ],
                layout: {{
                    template: 'plotly_white',
                    height: 700,
                    showlegend: true,
                    margin: {{ l: 50, r: 20, t: 60, b: 50 }},
                    xaxis: {{ range: [0, 1], title: 'Xn', domain: [0, 1] }},
                    yaxis: {{ range: [0, 1], title: 'Xn+1', domain: [0.55, 1] }},
                    xaxis2: {{ range: [0, 100], title: 'Iteration', domain: [0, 1] }},
                    yaxis2: {{ range: [0, 1], title: 'Xn', domain: [0, 0.45] }}
                }}
            }};
            return fig;
        }}

        // Update plots
        function updatePlots(r_value) {{
            current_r = r_value;
            document.getElementById('r-value').textContent = r_value.toFixed(2);

            const cobweb_key = r_value.toFixed(2);
            if (cobweb_data[cobweb_key]) {{
                const data = cobweb_data[cobweb_key];
                const fig = createCobwebFigure(data);
                Plotly.newPlot('cobweb-plot', fig.data, fig.layout, {{responsive: true}});
            }}

            const feig_json = JSON.parse(feigenbaum_json);
            feig_json.data.push({{
                x: [r_value, r_value],
                y: [0, 1],
                mode: 'lines',
                name: 'Aktuelles r',
                line: {{ color: 'red', width: 2, dash: 'dash' }}
            }});
            Plotly.newPlot('feigenbaum-plot', feig_json.data, feig_json.layout, {{responsive: true}});
        }}

        // Play animation
        function playAnimation() {{
            if (isAnimating) return;
            isAnimating = true;

            const cobweb_key = current_r.toFixed(2);
            if (!cobweb_data[cobweb_key]) return;

            const data = cobweb_data[cobweb_key];
            const maxSteps = Math.max(data.cobweb_x_red.length, data.cobweb_x_blue.length);
            const step = Math.max(1, Math.floor(maxSteps / 50));
            let frameIdx = 0;

            const interval = setInterval(() => {{
                frameIdx += step;
                if (frameIdx >= maxSteps) {{
                    clearInterval(interval);
                    isAnimating = false;
                    return;
                }}

                const seqIdx = Math.min(Math.floor(frameIdx / 3), data.sequence_red.length - 1);

                Plotly.restyle('cobweb-plot', {{
                    x: [
                        undefined, undefined,
                        data.cobweb_x_red.slice(0, frameIdx),
                        data.cobweb_x_blue.slice(0, frameIdx),
                        Array.from({{length: seqIdx + 1}}, (_, i) => i),
                        Array.from({{length: seqIdx + 1}}, (_, i) => i)
                    ],
                    y: [
                        undefined, undefined,
                        data.cobweb_y_red.slice(0, frameIdx),
                        data.cobweb_y_blue.slice(0, frameIdx),
                        data.sequence_red.slice(0, seqIdx + 1),
                        data.sequence_blue.slice(0, seqIdx + 1)
                    ]
                }}, [2, 3, 4, 5]);
            }}, 200);
        }}

        // Initialize
        updatePlots(2.80);

        // Slider listener
        document.getElementById('r-slider').addEventListener('input', function() {{
            const slider_value = parseFloat(this.value) / 100;
            updatePlots(slider_value);
        }});
    </script>
</body>
</html>
"""

# Write to file
output_file = "feigenbaum_interactive.html"
with open(output_file, "w") as f:
    f.write(html_content)

print(f"\nDone! Generated {output_file}")
print(f"File size: {len(html_content) / 1024 / 1024:.1f} MB")
print("Open it in your browser to view the interactive diagram.")
