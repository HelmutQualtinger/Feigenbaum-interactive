import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import copy

app = dash.Dash(__name__)

# Pre-calculate Feigenbaum diagram (once at startup)
r_values_feig = np.linspace(0.0, 4.0, 500)
feigenbaum_x_cached = []
feigenbaum_y_cached = []

for r_val in r_values_feig:
    x = 0.1
    for _ in range(500):  # Transient verwerfen
        x = r_val * x * (1 - x)
    for _ in range(100):  # 100 Punkte pro r-Wert sammeln
        x = r_val * x * (1 - x)
        feigenbaum_x_cached.append(r_val)
        feigenbaum_y_cached.append(x)

# Create Feigenbaum figure once at startup (static, doesn't change)
feigenbaum_fig_base = go.Figure()
feigenbaum_fig_base.add_trace(go.Scatter(
    x=feigenbaum_x_cached, y=feigenbaum_y_cached,
    mode='markers', name='Feigenbaum',
    marker=dict(size=2, color='steelblue'), showlegend=False
))
feigenbaum_fig_base.add_trace(go.Scatter(
    x=[2.8, 2.8], y=[0, 1],
    mode='lines', name='Aktuelles r',
    line=dict(color='red', width=2, dash='dash'), showlegend=False
))
feigenbaum_fig_base.update_xaxes(range=[0.0, 4.0], title_text="r")
feigenbaum_fig_base.update_yaxes(range=[0, 1], title_text="Attraktor")
feigenbaum_fig_base.update_layout(
    template="plotly_white",
    height=700,
    margin=dict(l=80, r=80, t=40, b=50),
    showlegend=False
)

app.layout = html.Div([
    html.H2("Logistische Gleichung: X", style={'marginBottom': '10px', 'marginLeft': '10px', 'display': 'inline'}),
    html.Sub("n+1", style={'display': 'inline'}),
    html.Span(" = r · X", style={'display': 'inline'}),
    html.Sub("n", style={'display': 'inline'}),
    html.Span(" · (1 - X", style={'display': 'inline'}),
    html.Sub("n", style={'display': 'inline'}),
    html.Span(")", style={'display': 'inline'}),
    html.Div([
        # Linke Spalte: Cobweb + Xn-Folge
        html.Div([
            dcc.Graph(id='cobweb-plot', style={'height': '700px'}, config={'responsive': True})
        ], style={'display': 'inline-block', 'width': '48%', 'verticalAlign': 'top', 'marginRight': '1%'}),

        # Rechte Spalte: Feigenbaum + Slider
        html.Div([
            dcc.Graph(id='feigenbaum-plot', style={'height': '600px'}, config={'responsive': True}),
            html.Div([
                html.Label("Parameter r:", style={'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
                dcc.Slider(
                    id='r-slider',
                    min=0.0, max=4.0, step=0.01, value=2.8,
                    marks={i: str(i) for i in range(0, 5)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], style={'padding': '0 30px 15px 30px', 'boxSizing': 'border-box'})
        ], style={'display': 'inline-block', 'width': '50%', 'verticalAlign': 'top'})
    ], style={'display': 'block', 'width': '100%'})
], style={'width': '100%', 'padding': '10px'})

@app.callback(
    Output('cobweb-plot', 'figure'),
    Output('feigenbaum-plot', 'figure'),
    Input('r-slider', 'value')
)
def update_graphs(r):
    x_val = np.linspace(0, 1, 100)
    y_val = r * x_val * (1 - x_val)

    # Iterationen berechnen für zwei verschiedene Startpunkte
    iterations = 100
    iterations_long = 100
    x_start_red = 0.05
    x_start_blue = 0.90

    # Rote Spirale (Start 0.05)
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

    # Blaue Spirale (Start 0.90)
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

    # Lange Sequenzen für Iterations Plot (bis 100)
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

    # === LINKER PLOT: Cobweb + Xn-Folge ===
    fig_left = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Cobweb-Diagramm", "Xn-Folge (bis 100)"),
        vertical_spacing=0.1,
        row_heights=[0.5, 0.5]
    )

    # Cobweb: Parabel
    fig_left.add_trace(go.Scatter(x=x_val, y=y_val, mode='lines', name='f(x) = r*x(1-x)',
                            line=dict(color='green'), showlegend=True), row=1, col=1)

    # Cobweb: Diagonale
    fig_left.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='y = x',
                            line=dict(color='black', dash='dash'), showlegend=True), row=1, col=1)

    # Cobweb: Rote Spirale (Start 0.05)
    fig_left.add_trace(go.Scatter(
        x=cobweb_x_red, y=cobweb_y_red,
        mode='lines+markers', name='Start: 0.05',
        line=dict(color='red', width=1), marker=dict(size=4)
    ), row=1, col=1)

    # Cobweb: Blaue Spirale (Start 0.90)
    fig_left.add_trace(go.Scatter(
        x=cobweb_x_blue, y=cobweb_y_blue,
        mode='lines+markers', name='Start: 0.90',
        line=dict(color='blue', width=1), marker=dict(size=4)
    ), row=1, col=1)

    # Xn-Folge: Rote (Start 0.05)
    fig_left.add_trace(go.Scatter(
        x=list(range(len(sequence_red))), y=sequence_red,
        mode='lines+markers', name='Start: 0.05',
        line=dict(color='red', width=2), marker=dict(size=3), showlegend=False
    ), row=2, col=1)

    # Xn-Folge: Blaue (Start 0.90)
    fig_left.add_trace(go.Scatter(
        x=list(range(len(sequence_blue))), y=sequence_blue,
        mode='lines+markers', name='Start: 0.90',
        line=dict(color='blue', width=2), marker=dict(size=3), showlegend=False
    ), row=2, col=1)

    # Animation Frames für Cobweb-Diagramm und Xn-Folge
    frames = []
    max_cobweb_points = iterations * 3  # 3 points per iteration (vertical, diagonal, point on curve)
    cobweb_step = max(1, max_cobweb_points // 50)

    for i in range(cobweb_step, min(max_cobweb_points, max(len(cobweb_x_red), len(cobweb_x_blue))), cobweb_step):
        frame_red_cobweb = go.Scatter(x=cobweb_x_red[:i], y=cobweb_y_red[:i])
        frame_blue_cobweb = go.Scatter(x=cobweb_x_blue[:i], y=cobweb_y_blue[:i])

        # Calculate sequence frame index based on cobweb points (3 points per iteration)
        seq_idx = min(i // 3, len(sequence_red) - 1)
        frame_red_seq = go.Scatter(x=list(range(seq_idx + 1)), y=sequence_red[:seq_idx + 1])
        frame_blue_seq = go.Scatter(x=list(range(seq_idx + 1)), y=sequence_blue[:seq_idx + 1])

        frames.append(go.Frame(
            data=[frame_red_cobweb, frame_blue_cobweb, frame_red_seq, frame_blue_seq],
            traces=[2, 3, 4, 5]
        ))

    fig_left.frames = frames

    fig_left.update_xaxes(range=[0, 1], title_text="Xn", row=1, col=1)
    fig_left.update_yaxes(range=[0, 1], title_text="Xn+1", row=1, col=1)
    fig_left.update_xaxes(range=[0, 100], title_text="Iteration", row=2, col=1)
    fig_left.update_yaxes(range=[0, 1], title_text="Xn", row=2, col=1)

    fig_left.update_layout(
        template="plotly_white",
        height=700,
        showlegend=True,
        margin=dict(l=50, r=20, t=60, b=50),
        updatemenus=[{
            "type": "buttons",
            "buttons": [{
                "label": "Play",
                "method": "animate",
                "args": [None, {"frame": {"duration": 200, "redraw": False}, "fromcurrent": True}]
            }]
        }]
    )

    # === RECHTER PLOT: Feigenbaum (only update red line) ===
    # Deep copy to avoid mutating the cached base figure (prevents race conditions in multi-user setups)
    fig_right = copy.deepcopy(feigenbaum_fig_base)
    fig_right.data[1].x = [r, r]  # Update red line x-coordinates

    return fig_left, fig_right

if __name__ == '__main__':
    app.run(debug=True)

