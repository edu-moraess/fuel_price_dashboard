import streamlit as st

C = {
    "bg":         "#0D0D0D",
    "surface":    "#141414",
    "elevated":   "#1C1C1C",
    "border":     "#272727",
    "amber":      "#C87E0A",
    "amber_hi":   "#E89A0E",
    "amber_lo":   "#4A2E05",
    "text":       "#E6E2DA",
    "text_sub":   "#888480",
    "text_muted": "#4A4846",
    "green":      "#2A7A42",
    "red":        "#B83030",
    "blue":       "#2B6399",
}

PLOTLY = dict(
    paper_bgcolor=C["surface"],
    plot_bgcolor=C["elevated"],
    font=dict(family="'IBM Plex Mono', monospace", color=C["text"], size=11),
    title_font=dict(color=C["amber"], size=13,
                    family="'IBM Plex Sans Condensed', sans-serif"),
    legend=dict(bgcolor=C["elevated"], bordercolor=C["border"], borderwidth=1,
                font=dict(color=C["text_sub"], size=10)),
    colorway=[C["amber"], C["blue"], C["green"], C["red"],
              "#7B5EA7", "#1F7A8C", "#A0522D", "#4E8098"],
    margin=dict(l=50, r=20, t=48, b=40),
)


def apply(fig):
    fig.update_layout(**PLOTLY)
    fig.update_xaxes(gridcolor=C["border"], linecolor=C["border"],
                     zerolinecolor=C["border"],
                     tickfont=dict(color=C["text_sub"], size=9),
                     title_font=dict(color=C["text_sub"]))
    fig.update_yaxes(gridcolor=C["border"], linecolor=C["border"],
                     zerolinecolor=C["border"],
                     tickfont=dict(color=C["text_sub"], size=9),
                     title_font=dict(color=C["text_sub"]))
    return fig


CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans+Condensed:wght@400;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
    background-color: {C["bg"]} !important;
    color: {C["text"]} !important;
}}
.stApp {{ background-color: {C["bg"]} !important; }}

/* ── Hide default Streamlit nav chrome ── */
[data-testid="stSidebarNav"] {{ display: none !important; }}
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header {{ visibility: hidden; }}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background-color: {C["surface"]} !important;
    border-right: 1px solid {C["border"]} !important;
    min-width: 260px !important;
    max-width: 260px !important;
}}
section[data-testid="stSidebar"] * {{ color: {C["text"]} !important; }}

/* ── Headings ── */
h1 {{
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-weight: 700 !important; font-size: 1.45rem !important;
    color: {C["text"]} !important;
    border-left: 3px solid {C["amber"]}; padding-left: 11px;
    text-transform: uppercase; letter-spacing: 0.04em;
    margin-bottom: 2px !important;
}}
h2 {{
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-weight: 600 !important; font-size: 0.78rem !important;
    color: {C["amber"]} !important;
    text-transform: uppercase; letter-spacing: 0.12em;
    margin: 18px 0 6px 0 !important;
}}
h3 {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 500 !important; font-size: 0.78rem !important;
    color: {C["text_sub"]} !important;
    text-transform: uppercase; letter-spacing: 0.08em;
}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
    background: {C["elevated"]} !important;
    border: 1px solid {C["border"]} !important;
    border-top: 2px solid {C["amber"]} !important;
    border-radius: 2px !important;
    padding: 12px 14px !important;
}}
[data-testid="stMetricLabel"] {{
    color: {C["text_sub"]} !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.12em; text-transform: uppercase;
}}
[data-testid="stMetricValue"] {{
    color: {C["text"]} !important;
    font-size: 1.35rem !important; font-weight: 600 !important;
}}

/* ── Nav buttons ── */
.nav-btn button {{
    background: transparent !important;
    color: {C["text_sub"]} !important;
    border: none !important;
    border-left: 2px solid {C["border"]} !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.06em;
    text-align: left !important;
    padding: 6px 0 6px 12px !important;
    width: 100% !important;
    margin: 1px 0 !important;
    transition: all 0.12s;
}}
.nav-btn button:hover {{
    color: {C["amber_hi"]} !important;
    border-left-color: {C["amber"]} !important;
    background: {C["amber_lo"]} !important;
}}
.nav-btn-active button {{
    color: {C["amber"]} !important;
    border-left: 2px solid {C["amber"]} !important;
    background: {C["amber_lo"]} !important;
}}

/* ── Selectbox / Multiselect ── */
div[data-baseweb="select"] > div {{
    background: {C["elevated"]} !important;
    border-color: {C["border"]} !important;
    border-radius: 2px !important;
    color: {C["text"]} !important;
    font-size: 0.80rem !important;
}}
div[data-baseweb="select"] svg {{ fill: {C["amber"]} !important; }}
span[data-baseweb="tag"] {{
    background: {C["amber_lo"]} !important;
    color: {C["amber_hi"]} !important;
    border-radius: 1px !important; font-size: 0.72rem !important;
}}

/* ── Slider ── */
div[data-testid="stSlider"] div[role="slider"] {{
    background: {C["amber"]} !important;
    border: 2px solid {C["amber_hi"]} !important;
}}

/* ── Date input ── */
div[data-testid="stDateInput"] input {{
    background: {C["elevated"]} !important;
    color: {C["text"]} !important;
    border-color: {C["border"]} !important;
    border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.80rem !important;
}}

/* ── Number input ── */
input[type="number"] {{
    background: {C["elevated"]} !important;
    color: {C["text"]} !important;
    border-color: {C["border"]} !important;
    font-family: 'IBM Plex Mono', monospace !important;
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    border-radius: 2px !important; font-size: 0.78rem;
}}
.stSuccess {{ background: rgba(42,122,66,0.12) !important; border-left: 3px solid {C["green"]} !important; }}
.stWarning {{ background: rgba(200,126,10,0.10) !important; border-left: 3px solid {C["amber"]} !important; }}
.stError   {{ background: rgba(184,48,48,0.10) !important; border-left: 3px solid {C["red"]} !important; }}
.stInfo    {{ background: rgba(43,99,153,0.10) !important; border-left: 3px solid {C["blue"]} !important; }}

/* ── Divider ── */
hr {{ border: none; border-top: 1px solid {C["border"]} !important; margin: 16px 0 !important; }}

/* ── Code ── */
code, pre {{ background: {C["elevated"]} !important; color: {C["amber_hi"]} !important;
    border: 1px solid {C["border"]} !important; border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.78rem !important; }}

/* ── Plotly container ── */
[data-testid="stPlotlyChart"] {{
    border: 1px solid {C["border"]}; border-radius: 2px;
    background: {C["surface"]};
}}
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_logo():
    st.sidebar.markdown(f"""
    <div style="padding:20px 14px 16px 14px; border-bottom:1px solid {C['border']}; margin-bottom:16px;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
                    letter-spacing:0.20em; color:{C['text_muted']}; text-transform:uppercase;
                    margin-bottom:5px;">Quant Research Platform</div>
        <div style="font-family:'IBM Plex Sans Condensed',sans-serif; font-weight:700;
                    font-size:1.10rem; color:{C['text']}; text-transform:uppercase;
                    letter-spacing:0.03em; line-height:1.15;">
            Fuel Price<br><span style="color:{C['amber']};">Intelligence</span>
        </div>
        <div style="font-size:0.60rem; color:{C['text_muted']}; margin-top:6px;
                    letter-spacing:0.08em;">IEA · GLOBAL · MACRO</div>
    </div>
    """, unsafe_allow_html=True)


def nav_label(text: str):
    st.sidebar.markdown(
        f'<div style="font-size:0.60rem; letter-spacing:0.16em; color:{C["text_muted"]}; '
        f'text-transform:uppercase; margin:14px 0 4px 0;">{text}</div>',
        unsafe_allow_html=True,
    )


def status_dot(ok: bool):
    color = C["green"] if ok else C["red"]
    label = "DATA LOADED" if ok else "DATA MISSING"
    st.sidebar.markdown(
        f'<div style="margin-top:12px; display:flex; align-items:center; gap:8px;">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:{color};'
        f'box-shadow:0 0 5px {color};display:inline-block;"></span>'
        f'<span style="font-size:0.65rem; letter-spacing:0.10em; color:{color};">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    sub = (f'<p style="color:{C["text_sub"]};font-size:0.72rem;letter-spacing:0.06em;'
           f'margin:3px 0 18px 15px;text-transform:uppercase;">{subtitle}</p>') if subtitle else ""
    st.markdown(f"<h1>{title}</h1>{sub}", unsafe_allow_html=True)


def section(label: str):
    st.markdown(f"<h2>{label}</h2>", unsafe_allow_html=True)
