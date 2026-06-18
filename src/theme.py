"""
src/theme.py
────────────────────────────────────────────────────────────
Global visual theme for the Fuel Price Quant Research Platform.
Petro-industrial identity: dark steel, amber signal, clean data.

Inject once in every page via: inject_theme()
"""

import streamlit as st

# ── Palette tokens ──────────────────────────────────────────
COLORS = {
    "bg_base":       "#0D0D0D",   # Near-black base
    "bg_surface":    "#161616",   # Card / sidebar surface
    "bg_elevated":   "#1F1F1F",   # Elevated panels
    "border":        "#2A2A2A",   # Structural dividers
    "amber":         "#C87E0A",   # Primary accent — petroleum amber
    "amber_bright":  "#E8960E",   # Hover / highlight amber
    "amber_dim":     "#5C3A06",   # Muted amber (bands, fills)
    "text_primary":  "#E8E4DC",   # Off-white — warm, not harsh
    "text_secondary":"#8C8880",   # Subdued labels
    "text_muted":    "#555250",   # Disabled / placeholder
    "green_signal":  "#2D7D46",   # Positive / long
    "red_signal":    "#C0392B",   # Negative / short / alert
    "blue_data":     "#2E6DA4",   # Data series blue
    "orange_data":   "#C87E0A",   # Data series orange (= amber)
}

PLOTLY_THEME = dict(
    paper_bgcolor=COLORS["bg_surface"],
    plot_bgcolor=COLORS["bg_elevated"],
    font=dict(family="'IBM Plex Mono', 'Courier New', monospace",
              color=COLORS["text_primary"], size=12),
    title_font=dict(family="'IBM Plex Mono', monospace",
                    color=COLORS["amber"], size=14),
    legend=dict(bgcolor=COLORS["bg_elevated"],
                bordercolor=COLORS["border"],
                borderwidth=1,
                font=dict(color=COLORS["text_secondary"], size=11)),
    xaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"],
               tickfont=dict(color=COLORS["text_secondary"], size=10),
               title_font=dict(color=COLORS["text_secondary"])),
    yaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"],
               tickfont=dict(color=COLORS["text_secondary"], size=10),
               title_font=dict(color=COLORS["text_secondary"])),
    colorway=[COLORS["amber"], "#2E6DA4", "#2D7D46", "#C0392B",
              "#7B5EA7", "#1F7A8C", "#A0522D"],
)

# ── CSS injection ────────────────────────────────────────────
_CSS = f"""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans+Condensed:wght@400;600;700&display=swap');

/* ── Root variables ── */
:root {{
    --bg-base:        {COLORS["bg_base"]};
    --bg-surface:     {COLORS["bg_surface"]};
    --bg-elevated:    {COLORS["bg_elevated"]};
    --border:         {COLORS["border"]};
    --amber:          {COLORS["amber"]};
    --amber-bright:   {COLORS["amber_bright"]};
    --amber-dim:      {COLORS["amber_dim"]};
    --text-primary:   {COLORS["text_primary"]};
    --text-secondary: {COLORS["text_secondary"]};
    --text-muted:     {COLORS["text_muted"]};
    --green:          {COLORS["green_signal"]};
    --red:            {COLORS["red_signal"]};
}}

/* ── Global reset ── */
html, body, [class*="css"] {{
    font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
}}

/* ── Main app wrapper ── */
.stApp {{
    background-color: var(--bg-base) !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background-color: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}}
section[data-testid="stSidebar"] * {{
    color: var(--text-primary) !important;
}}
section[data-testid="stSidebar"] .stMarkdown p {{
    color: var(--text-secondary) !important;
    font-size: 0.82rem;
}}

/* ── Sidebar header labels ── */
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: var(--amber) !important;
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
    margin-bottom: 8px;
}}

/* ── Page titles (h1, h2, h3) ── */
h1 {{
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
    color: var(--text-primary) !important;
    border-left: 3px solid var(--amber);
    padding-left: 12px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}
h2 {{
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-weight: 600 !important;
    color: var(--amber) !important;
    font-size: 1.0rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
h3 {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}

/* ── Metric cards ── */
[data-testid="stMetric"] {{
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-top: 2px solid var(--amber) !important;
    border-radius: 2px !important;
    padding: 14px 16px !important;
}}
[data-testid="stMetricLabel"] {{
    color: var(--text-secondary) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.10em;
    text-transform: uppercase;
}}
[data-testid="stMetricValue"] {{
    color: var(--text-primary) !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
}}

/* ── Selectbox / Multiselect / Sliders ── */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {{
    background-color: var(--bg-elevated) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 2px !important;
}}
div[data-baseweb="select"] svg {{
    fill: var(--amber) !important;
}}

/* Slider track */
div[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stSlider"] {{
    background: var(--amber) !important;
}}
div[data-testid="stSlider"] div[role="slider"] {{
    background: var(--amber) !important;
    border: 2px solid var(--amber-bright) !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background-color: transparent !important;
    color: var(--amber) !important;
    border: 1px solid var(--amber) !important;
    border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 6px 16px;
    transition: background 0.15s, color 0.15s;
}}
.stButton > button:hover {{
    background-color: var(--amber-dim) !important;
    color: var(--amber-bright) !important;
    border-color: var(--amber-bright) !important;
}}

/* ── Alerts / Info / Warning / Success / Error ── */
div[data-testid="stAlert"] {{
    border-radius: 2px !important;
    font-size: 0.82rem;
    font-family: 'IBM Plex Mono', monospace !important;
}}
.stSuccess {{
    background-color: rgba(45, 125, 70, 0.15) !important;
    border-left: 3px solid var(--green) !important;
    color: #7EC8A0 !important;
}}
.stWarning {{
    background-color: rgba(200, 126, 10, 0.12) !important;
    border-left: 3px solid var(--amber) !important;
    color: var(--amber-bright) !important;
}}
.stError {{
    background-color: rgba(192, 57, 43, 0.12) !important;
    border-left: 3px solid var(--red) !important;
    color: #E87070 !important;
}}
.stInfo {{
    background-color: rgba(46, 109, 164, 0.12) !important;
    border-left: 3px solid #2E6DA4 !important;
    color: #7AAFDC !important;
}}

/* ── Dividers ── */
hr {{
    border: none;
    border-top: 1px solid var(--border) !important;
    margin: 20px 0 !important;
}}

/* ── Code blocks ── */
code, pre, .stCode {{
    background-color: var(--bg-elevated) !important;
    color: var(--amber-bright) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
}}

/* ── DataFrame / Table ── */
[data-testid="stDataFrame"] {{
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
}}

/* ── Number input ── */
input[type="number"], input[type="text"] {{
    background-color: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
    border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important;
}}

/* ── Multiselect tags ── */
span[data-baseweb="tag"] {{
    background-color: var(--amber-dim) !important;
    color: var(--amber-bright) !important;
    border-radius: 1px !important;
    font-size: 0.75rem !important;
}}

/* ── Date input ── */
div[data-testid="stDateInput"] input {{
    background-color: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
}}

/* ── Tooltip / Popover ── */
div[role="tooltip"] {{
    background-color: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
}}

/* ── Caption / helper text ── */
.stCaption, small, caption {{
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.04em;
}}

/* ── Plotly chart container ── */
[data-testid="stPlotlyChart"] {{
    border: 1px solid var(--border);
    border-radius: 2px;
    background: var(--bg-surface);
}}

/* ── Sidebar status indicator ── */
.status-ok {{
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--green);
    margin-right: 8px;
    box-shadow: 0 0 6px var(--green);
}}
.status-err {{
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--red);
    margin-right: 8px;
    box-shadow: 0 0 6px var(--red);
}}
</style>
"""

# ── Public API ───────────────────────────────────────────────

def inject_theme():
    """Inject global petro-industrial CSS. Call once per page, before any st.* output."""
    st.markdown(_CSS, unsafe_allow_html=True)


def apply_plotly_theme(fig):
    """
    Apply the dark petro-industrial template to any Plotly figure.
    Returns the modified figure (also mutates in-place).
    """
    fig.update_layout(**PLOTLY_THEME)
    # Axes: apply to all subplots
    fig.update_xaxes(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
        tickfont=dict(color=COLORS["text_secondary"], size=10),
        title_font=dict(color=COLORS["text_secondary"]),
    )
    fig.update_yaxes(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
        tickfont=dict(color=COLORS["text_secondary"], size=10),
        title_font=dict(color=COLORS["text_secondary"]),
    )
    return fig


def section_header(title: str, subtitle: str = ""):
    """Render a styled section header."""
    sub_html = f'<p style="color:{COLORS["text_muted"]};font-size:0.75rem;letter-spacing:0.08em;margin:2px 0 12px 15px;text-transform:uppercase;">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<h2 style="margin-bottom:2px;">{title}</h2>{sub_html}',
        unsafe_allow_html=True
    )


def status_badge(ok: bool, label_ok="DATA LOADED", label_err="DATA MISSING"):
    """Render a compact status indicator in the sidebar."""
    if ok:
        st.sidebar.markdown(
            f'<span class="status-ok"></span><span style="color:{COLORS["green_signal"]};font-size:0.75rem;letter-spacing:0.08em;">{label_ok}</span>',
            unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown(
            f'<span class="status-err"></span><span style="color:{COLORS["red_signal"]};font-size:0.75rem;letter-spacing:0.08em;">{label_err}</span>',
            unsafe_allow_html=True
        )
