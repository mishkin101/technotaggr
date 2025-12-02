"""Visualization dashboard for TechnoTaggr results using Dash and Plotly."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html
from plotly.subplots import make_subplots

from .config import DEFAULT_OUTPUT_DIR

logger = logging.getLogger(__name__)

# Custom color palette - vibrant and distinctive
COLORS = [
    "#FF6B6B",  # coral red
    "#4ECDC4",  # teal
    "#45B7D1",  # sky blue
    "#96CEB4",  # sage green
    "#FFEAA7",  # soft yellow
    "#DDA0DD",  # plum
    "#98D8C8",  # mint
    "#F7DC6F",  # gold
    "#BB8FCE",  # lavender
    "#85C1E9",  # light blue
]

# Dark theme styling
DARK_BG = "#0d1117"
DARK_SURFACE = "#161b22"
DARK_BORDER = "#30363d"
TEXT_COLOR = "#e6edf3"
ACCENT_COLOR = "#58a6ff"


def load_session_data(json_path: Path) -> dict[str, Any]:
    """Load session data from a JSON file.

    Args:
        json_path: Path to the JSON results file.

    Returns:
        Parsed JSON data as a dictionary.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(json_path) as f:
        return json.load(f)


def get_available_sessions(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[Path]:
    """Get list of available session files sorted by modification time.

    Args:
        output_dir: Directory containing result files.

    Returns:
        List of JSON file paths sorted by modification time (newest first).
    """
    if not output_dir.exists():
        return []

    json_files = list(output_dir.glob("results_*.json"))
    return sorted(json_files, key=lambda p: p.stat().st_mtime, reverse=True)


def get_latest_session(output_dir: Path = DEFAULT_OUTPUT_DIR) -> Path | None:
    """Get the most recent session file.

    Args:
        output_dir: Directory containing result files.

    Returns:
        Path to the most recent session file, or None if no files exist.
    """
    sessions = get_available_sessions(output_dir)
    return sessions[0] if sessions else None


def create_predictions_line_plot(
    predictions: list[list[float]],
    classes: list[str],
    title: str,
    x_label: str = "Index",
) -> go.Figure:
    """Create a line plot for predictions over time.

    Args:
        predictions: List of prediction arrays, one per segment/bar.
        classes: List of class names.
        title: Plot title.
        x_label: Label for x-axis.

    Returns:
        Plotly Figure object.
    """
    fig = go.Figure()

    for i, class_name in enumerate(classes):
        y_values = [pred[i] for pred in predictions]
        fig.add_trace(
            go.Scatter(
                x=list(range(len(predictions))),
                y=y_values,
                mode="lines",
                name=class_name,
                line=dict(color=COLORS[i % len(COLORS)], width=2),
                hovertemplate=f"<b>{class_name}</b><br>{x_label}: %{{x}}<br>Probability: %{{y:.3f}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=TEXT_COLOR)),
        xaxis=dict(
            title=x_label,
            gridcolor=DARK_BORDER,
            zeroline=False,
            color=TEXT_COLOR,
        ),
        yaxis=dict(
            title="Probability",
            range=[0, 1],
            gridcolor=DARK_BORDER,
            zeroline=False,
            color=TEXT_COLOR,
        ),
        paper_bgcolor=DARK_SURFACE,
        plot_bgcolor=DARK_SURFACE,
        font=dict(color=TEXT_COLOR),
        legend=dict(
            bgcolor=DARK_SURFACE,
            bordercolor=DARK_BORDER,
            borderwidth=1,
        ),
        hovermode="x unified",
        margin=dict(l=60, r=20, t=50, b=50),
    )

    return fig


def create_aggregate_bar_plot(
    aggregated_predictions: dict[str, float],
    title: str,
) -> go.Figure:
    """Create a bar plot for aggregated predictions.

    Args:
        aggregated_predictions: Dictionary mapping class names to probabilities.
        title: Plot title.

    Returns:
        Plotly Figure object.
    """
    classes = list(aggregated_predictions.keys())
    values = list(aggregated_predictions.values())

    fig = go.Figure(
        go.Bar(
            x=classes,
            y=values,
            marker=dict(
                color=COLORS[: len(classes)],
                line=dict(color=DARK_BORDER, width=1),
            ),
            hovertemplate="<b>%{x}</b><br>Probability: %{y:.3f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=TEXT_COLOR)),
        xaxis=dict(
            title="Class",
            gridcolor=DARK_BORDER,
            zeroline=False,
            color=TEXT_COLOR,
            tickangle=-45 if len(classes) > 5 else 0,
        ),
        yaxis=dict(
            title="Probability",
            range=[0, 1],
            gridcolor=DARK_BORDER,
            zeroline=False,
            color=TEXT_COLOR,
        ),
        paper_bgcolor=DARK_SURFACE,
        plot_bgcolor=DARK_SURFACE,
        font=dict(color=TEXT_COLOR),
        margin=dict(l=60, r=20, t=50, b=80),
        showlegend=False,
    )

    return fig


def create_model_visualization(model_data: dict[str, Any]) -> html.Div:
    """Create visualization components for a single model.

    Args:
        model_data: Model result data from JSON.

    Returns:
        Dash Div containing all plots for this model.
    """
    model_name = model_data["model_name"]
    classes = model_data["classes"]

    plots = []

    # Check if bar_predictions exist (post-processed data)
    has_bar_predictions = "bar_predictions" in model_data

    # Segment predictions line plot
    if "segment_predictions" in model_data:
        segment_fig = create_predictions_line_plot(
            model_data["segment_predictions"],
            classes,
            f"Segment Predictions over Time",
            "Segment",
        )
        plots.append(
            html.Div(
                dcc.Graph(figure=segment_fig, config={"displayModeBar": True}),
                style={"marginBottom": "20px"},
            )
        )

    # Bar predictions line plot (if available)
    if has_bar_predictions:
        bar_fig = create_predictions_line_plot(
            model_data["bar_predictions"],
            classes,
            f"Bar (Phrase) Predictions over Time",
            "Bar/Phrase",
        )
        plots.append(
            html.Div(
                dcc.Graph(figure=bar_fig, config={"displayModeBar": True}),
                style={"marginBottom": "20px"},
            )
        )

    # Aggregated predictions - create side by side if both exist
    aggregate_plots = []

    if "aggregated_predictions" in model_data:
        agg_segment_fig = create_aggregate_bar_plot(
            model_data["aggregated_predictions"],
            "Aggregated Segment Predictions",
        )
        aggregate_plots.append(
            html.Div(
                dcc.Graph(figure=agg_segment_fig, config={"displayModeBar": True}),
                style={"flex": "1", "minWidth": "400px"},
            )
        )

    if has_bar_predictions and "aggregated_bar_predictions" in model_data:
        agg_bar_fig = create_aggregate_bar_plot(
            model_data["aggregated_bar_predictions"],
            "Aggregated Bar (Phrase) Predictions",
        )
        aggregate_plots.append(
            html.Div(
                dcc.Graph(figure=agg_bar_fig, config={"displayModeBar": True}),
                style={"flex": "1", "minWidth": "400px"},
            )
        )

    if aggregate_plots:
        plots.append(
            html.Div(
                aggregate_plots,
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "20px",
                    "marginBottom": "20px",
                },
            )
        )

    return html.Div(
        [
            html.H3(
                f"Model: {model_name}",
                style={
                    "color": ACCENT_COLOR,
                    "marginBottom": "15px",
                    "borderBottom": f"2px solid {ACCENT_COLOR}",
                    "paddingBottom": "10px",
                },
            ),
            html.Div(plots),
        ],
        style={
            "backgroundColor": DARK_SURFACE,
            "padding": "20px",
            "borderRadius": "12px",
            "marginBottom": "30px",
            "border": f"1px solid {DARK_BORDER}",
        },
    )


def create_dashboard(session_file: Path | None = None) -> Dash:
    """Create the Dash application for visualizing TechnoTaggr results.

    Args:
        session_file: Optional path to a specific session file.
                     If None, will allow selection from available sessions.

    Returns:
        Configured Dash application instance.
    """
    app = Dash(
        __name__,
        suppress_callback_exceptions=True,
        title="TechnoTaggr Dashboard",
    )

    # Get available sessions
    available_sessions = get_available_sessions()

    if session_file:
        initial_session = str(session_file)
    elif available_sessions:
        initial_session = str(available_sessions[0])
    else:
        initial_session = None

    # Create session options
    session_options = [
        {"label": p.name, "value": str(p)} for p in available_sessions
    ]

    app.layout = html.Div(
        [
            # Header
            html.Div(
                [
                    html.H1(
                        "🎵 TechnoTaggr",
                        style={
                            "margin": "0",
                            "fontSize": "2.5rem",
                            "fontWeight": "700",
                            "background": f"linear-gradient(135deg, {ACCENT_COLOR}, {COLORS[1]})",
                            "WebkitBackgroundClip": "text",
                            "WebkitTextFillColor": "transparent",
                        },
                    ),
                    html.P(
                        "Audio Analysis Visualization Dashboard",
                        style={
                            "margin": "5px 0 0 0",
                            "color": TEXT_COLOR,
                            "opacity": "0.7",
                        },
                    ),
                ],
                style={
                    "padding": "30px 40px",
                    "backgroundColor": DARK_SURFACE,
                    "borderBottom": f"1px solid {DARK_BORDER}",
                },
            ),
            # Controls section
            html.Div(
                [
                    html.Div(
                        [
                            html.Label(
                                "Session File",
                                style={
                                    "color": TEXT_COLOR,
                                    "fontWeight": "600",
                                    "marginBottom": "8px",
                                    "display": "block",
                                },
                            ),
                            dcc.Dropdown(
                                id="session-dropdown",
                                options=session_options,
                                value=initial_session,
                                placeholder="Select a session file...",
                                style={"minWidth": "350px"},
                                className="dark-dropdown",
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Audio File",
                                style={
                                    "color": TEXT_COLOR,
                                    "fontWeight": "600",
                                    "marginBottom": "8px",
                                    "display": "block",
                                },
                            ),
                            dcc.Dropdown(
                                id="audio-file-dropdown",
                                options=[],
                                value=None,
                                placeholder="Select an audio file...",
                                style={"minWidth": "350px"},
                                className="dark-dropdown",
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                ],
                style={
                    "display": "flex",
                    "gap": "30px",
                    "padding": "25px 40px",
                    "backgroundColor": DARK_BG,
                    "flexWrap": "wrap",
                },
            ),
            # Session info panel
            html.Div(
                id="session-info",
                style={
                    "padding": "20px 40px",
                    "backgroundColor": DARK_SURFACE,
                    "borderBottom": f"1px solid {DARK_BORDER}",
                },
            ),
            # Main content area
            html.Div(
                id="visualization-content",
                style={
                    "padding": "30px 40px",
                    "minHeight": "60vh",
                },
            ),
        ],
        style={
            "fontFamily": "'JetBrains Mono', 'Fira Code', 'SF Mono', monospace",
            "backgroundColor": DARK_BG,
            "minHeight": "100vh",
            "color": TEXT_COLOR,
        },
    )

    # Add custom CSS for dark dropdown styling
    app.index_string = """
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                * {
                    box-sizing: border-box;
                }
                body {
                    margin: 0;
                    padding: 0;
                }
                .dark-dropdown .Select-control {
                    background-color: #21262d !important;
                    border: 1px solid #30363d !important;
                    color: #e6edf3 !important;
                }
                .dark-dropdown .Select-menu-outer {
                    background-color: #21262d !important;
                    border: 1px solid #30363d !important;
                }
                .dark-dropdown .Select-option {
                    background-color: #21262d !important;
                    color: #e6edf3 !important;
                }
                .dark-dropdown .Select-option:hover {
                    background-color: #30363d !important;
                }
                .dark-dropdown .Select-value-label {
                    color: #e6edf3 !important;
                }
                .dark-dropdown .Select-placeholder {
                    color: #8b949e !important;
                }
                .dark-dropdown input {
                    color: #e6edf3 !important;
                }
                /* Fix dropdown arrow color */
                .dark-dropdown .Select-arrow {
                    border-color: #8b949e transparent transparent !important;
                }
                .Select.is-open > .Select-control .Select-arrow {
                    border-color: transparent transparent #8b949e !important;
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    """

    @app.callback(
        Output("audio-file-dropdown", "options"),
        Output("audio-file-dropdown", "value"),
        Input("session-dropdown", "value"),
    )
    def update_audio_dropdown(session_path: str | None):
        """Update audio file dropdown based on selected session."""
        if not session_path:
            return [], None

        try:
            data = load_session_data(Path(session_path))
            results = data.get("results", [])

            options = []
            for result in results:
                audio_file = result.get("audio_file", "")
                # Use just the filename for display
                label = Path(audio_file).name if audio_file else "Unknown"
                options.append({"label": label, "value": audio_file})

            initial_value = options[0]["value"] if options else None
            return options, initial_value
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return [], None

    @app.callback(
        Output("session-info", "children"),
        Input("session-dropdown", "value"),
    )
    def update_session_info(session_path: str | None):
        """Update session info panel."""
        if not session_path:
            return html.P(
                "No session selected",
                style={"color": TEXT_COLOR, "opacity": "0.5"},
            )

        try:
            data = load_session_data(Path(session_path))

            info_items = [
                ("Session", data.get("session_timestamp", "Unknown")),
                ("Input Directory", data.get("input_directory", "Unknown")),
                ("Total Files", str(data.get("total_files", 0))),
                ("Successful", str(data.get("successful_files", 0))),
                ("Failed", str(data.get("failed_files", 0))),
            ]

            classifiers = data.get("classifiers_used", [])

            return html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        label + ": ",
                                        style={
                                            "color": TEXT_COLOR,
                                            "opacity": "0.6",
                                            "marginRight": "8px",
                                        },
                                    ),
                                    html.Span(
                                        value,
                                        style={
                                            "color": ACCENT_COLOR,
                                            "fontWeight": "500",
                                        },
                                    ),
                                ],
                                style={
                                    "marginRight": "30px",
                                    "marginBottom": "8px",
                                },
                            )
                            for label, value in info_items
                        ],
                        style={
                            "display": "flex",
                            "flexWrap": "wrap",
                            "marginBottom": "10px",
                        },
                    ),
                    html.Div(
                        [
                            html.Span(
                                "Classifiers: ",
                                style={
                                    "color": TEXT_COLOR,
                                    "opacity": "0.6",
                                    "marginRight": "8px",
                                },
                            ),
                            html.Span(
                                ", ".join(classifiers) if classifiers else "None",
                                style={"color": COLORS[1]},
                            ),
                        ]
                    ),
                ]
            )
        except Exception as e:
            logger.error(f"Error loading session info: {e}")
            return html.P(
                f"Error loading session: {e}",
                style={"color": COLORS[0]},
            )

    @app.callback(
        Output("visualization-content", "children"),
        Input("session-dropdown", "value"),
        Input("audio-file-dropdown", "value"),
    )
    def update_visualization(session_path: str | None, audio_file: str | None):
        """Update main visualization content."""
        if not session_path or not audio_file:
            return html.Div(
                [
                    html.Div(
                        "📊",
                        style={"fontSize": "4rem", "marginBottom": "20px"},
                    ),
                    html.P(
                        "Select a session and audio file to view visualizations",
                        style={
                            "color": TEXT_COLOR,
                            "opacity": "0.5",
                            "fontSize": "1.1rem",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "minHeight": "40vh",
                },
            )

        try:
            data = load_session_data(Path(session_path))
            results = data.get("results", [])

            # Find the selected audio file result
            audio_result = None
            for result in results:
                if result.get("audio_file") == audio_file:
                    audio_result = result
                    break

            if not audio_result:
                return html.P(
                    "Audio file not found in results",
                    style={"color": COLORS[0]},
                )

            # Audio file info header
            audio_info = html.Div(
                [
                    html.H2(
                        Path(audio_file).name,
                        style={
                            "color": TEXT_COLOR,
                            "marginBottom": "10px",
                            "fontWeight": "600",
                        },
                    ),
                    html.Div(
                        [
                            html.Span(
                                f"Duration: {audio_result.get('audio_duration_seconds', 0):.1f}s",
                                style={
                                    "marginRight": "30px",
                                    "color": TEXT_COLOR,
                                    "opacity": "0.7",
                                },
                            ),
                            html.Span(
                                f"Sample Rate: {audio_result.get('sample_rate', 0)} Hz",
                                style={
                                    "color": TEXT_COLOR,
                                    "opacity": "0.7",
                                },
                            ),
                        ],
                    ),
                ],
                style={
                    "marginBottom": "30px",
                    "paddingBottom": "20px",
                    "borderBottom": f"1px solid {DARK_BORDER}",
                },
            )

            # Create visualization for each model
            model_visualizations = []
            for model_data in audio_result.get("models", []):
                model_visualizations.append(create_model_visualization(model_data))

            if not model_visualizations:
                model_visualizations.append(
                    html.P(
                        "No model results available",
                        style={"color": TEXT_COLOR, "opacity": "0.5"},
                    )
                )

            return html.Div([audio_info] + model_visualizations)

        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return html.P(
                f"Error loading visualization: {e}",
                style={"color": COLORS[0]},
            )

    return app


def run_dashboard(
    session_file: Path | None = None,
    host: str = "127.0.0.1",
    port: int = 8050,
    debug: bool = False,
) -> None:
    """Run the visualization dashboard.

    Args:
        session_file: Optional path to a specific session file.
        host: Host address to bind to.
        port: Port number to use.
        debug: Whether to run in debug mode.
    """
    app = create_dashboard(session_file)

    print(f"\n🎵 TechnoTaggr Dashboard")
    print(f"   Running at: http://{host}:{port}")
    print(f"   Press Ctrl+C to stop\n")

    app.run(host=host, port=port, debug=debug)

