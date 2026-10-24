"""NourishBot Streamlit interface."""

from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Any

import streamlit as st

from nourishbot import MODEL_ID, analyze_with_groq


APP_DIR = Path(__file__).parent
EXAMPLES = [
    {
        "id": "veggie-bowl",
        "name": "Veggie power bowl",
        "image": APP_DIR / "assets" / "produce.jpg",
        "diet": "vegan",
        "workflow": "recipe",
    },
    {
        "id": "steak-pasta",
        "name": "Creamy steak pasta",
        "image": APP_DIR / "assets" / "pasta.jpg",
        "diet": "",
        "workflow": "analysis",
    },
    {
        "id": "low-carb-bowl",
        "name": "Fresh market bowl",
        "image": APP_DIR / "assets" / "low-carb.jpg",
        "diet": "keto",
        "workflow": "recipe",
    },
    {
        "id": "pizza",
        "name": "Chicken pizza",
        "image": APP_DIR / "assets" / "pizza.jpg",
        "diet": "",
        "workflow": "analysis",
    },
]


st.set_page_config(
    page_title="NourishBot · AI food intelligence",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

    :root {
        --bg: #090b0d;
        --panel: #121517;
        --panel-2: #171a1d;
        --line: #292d31;
        --muted: #959da5;
        --text: #f7f8f8;
        --amber: #ffa51f;
        --amber-2: #ff7a18;
        --green: #8bd18b;
    }

    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: "DM Sans", sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background:
          radial-gradient(circle at 50% -15%, rgba(255, 165, 31, .12), transparent 33rem),
          var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"], [data-testid="stToolbar"] { background: transparent; }
    [data-testid="stMainBlockContainer"] { max-width: 1240px; padding-top: 2rem; padding-bottom: 5rem; }
    #MainMenu, footer { visibility: hidden; }

    h1, h2, h3 { font-family: "Manrope", sans-serif !important; letter-spacing: -.03em; }
    h2 { margin-top: .2rem !important; }
    p { color: #c7ccd0; }

    .brand-row {
        display: flex; align-items: center; gap: .7rem; justify-content: center;
        color: #f5f6f7; font-weight: 700; letter-spacing: .04em; margin-bottom: 1.7rem;
    }
    .brand-mark {
        display: inline-grid; place-items: center; width: 34px; height: 34px;
        background: linear-gradient(135deg, var(--amber), var(--amber-2));
        border-radius: 10px; color: #111; box-shadow: 0 8px 30px rgba(255, 142, 22, .2);
    }
    .hero { text-align: center; padding: 1rem 0 2.6rem; }
    .eyebrow {
        display: inline-block; color: var(--amber); font-weight: 700; font-size: .78rem;
        letter-spacing: .13em; text-transform: uppercase; margin-bottom: .8rem;
    }
    .hero h1 { font-size: clamp(2.55rem, 5.6vw, 4.7rem); line-height: 1.02; margin: 0 auto .9rem; max-width: 920px; }
    .hero h1 span { background: linear-gradient(92deg, #ffc45b, #ff7a18); -webkit-background-clip: text; color: transparent; }
    .hero p { max-width: 720px; margin: 0 auto; font-size: 1.08rem; line-height: 1.65; color: var(--muted); }

    .section-kicker { color: var(--amber); font-size: .76rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .section-copy { color: var(--muted); margin: -.5rem 0 1.1rem; }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, rgba(23, 26, 29, .96), rgba(13, 15, 17, .96));
        border-color: var(--line) !important; border-radius: 18px !important;
        box-shadow: 0 18px 55px rgba(0,0,0,.16);
    }
    [data-testid="stFileUploaderDropzone"] {
        background: #101315; border: 1px dashed #3c4248; border-radius: 14px; min-height: 205px;
    }
    [data-testid="stFileUploaderDropzone"] button {
        color: #111 !important; background: linear-gradient(95deg, var(--amber), var(--amber-2));
        border: 0; font-weight: 700;
    }
    [data-testid="stTextInput"] input {
        background: #0d1012; border-color: #343a40; color: var(--text); border-radius: 10px;
    }
    [data-testid="stTextInput"] input:focus { border-color: var(--amber); box-shadow: 0 0 0 1px var(--amber); }
    [data-testid="stSegmentedControl"] { background: #0c0f11; border-radius: 12px; padding: 4px; }

    .example-meta { padding-top: .2rem; }
    .example-name { color: #f4f5f5; font-weight: 700; margin-bottom: .32rem; }
    .pill {
        display: inline-block; padding: .2rem .55rem; border-radius: 999px; margin-right: .35rem;
        background: #252a2e; color: #b9c0c5; font-size: .72rem; font-weight: 600; text-transform: capitalize;
    }
    .pill.accent { background: rgba(255,165,31,.13); color: #ffbd54; }

    .stButton > button[kind="primary"] {
        width: 100%; min-height: 3.2rem; border: 0; border-radius: 12px;
        background: linear-gradient(95deg, var(--amber), var(--amber-2));
        color: #141414; font-weight: 800; box-shadow: 0 12px 30px rgba(255, 131, 24, .18);
    }
    .stButton > button[kind="primary"]:hover { color: #0e0e0e; transform: translateY(-1px); }
    .stButton > button[kind="secondary"] { border-color: #373c41; background: #16191c; }

    .selected-source {
        border: 1px solid rgba(255,165,31,.45); background: rgba(255,165,31,.08);
        border-radius: 10px; padding: .65rem .8rem; color: #ffd286; font-size: .88rem; margin-bottom: .75rem;
    }
    .empty-state {
        text-align: center; border: 1px dashed #353a3f; border-radius: 18px;
        padding: 4.5rem 1.5rem; color: #7f878e; background: rgba(16,18,20,.6);
    }
    .empty-icon { font-size: 2.3rem; margin-bottom: .7rem; filter: grayscale(.2); }

    .result-head {
        border-bottom: 1px solid var(--line); padding-bottom: 1rem; margin-bottom: 1rem;
    }
    .result-head h2 { margin-bottom: .35rem; }
    .result-head p { margin: 0; color: var(--muted); }
    [data-testid="stMetric"] {
        background: #111416; border: 1px solid #292e32; padding: 1rem; border-radius: 14px;
    }
    [data-testid="stMetricLabel"] { color: #969da3; }
    [data-testid="stMetricValue"] { font-family: "Manrope"; color: #fff; }
    .confidence { color: #98a0a7; font-size: .88rem; }
    .footer-note { text-align: center; color: #646c73; font-size: .8rem; margin-top: 3rem; }

    @media (max-width: 700px) {
      [data-testid="stMainBlockContainer"] { padding-top: 1.1rem; }
      .hero { padding-top: .25rem; }
      .hero h1 { font-size: 2.7rem; }
    }
</style>
""",
    unsafe_allow_html=True,
)


def secret_or_env(name: str) -> str:
    value = os.getenv(name, "")
    if value:
        return value
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return ""


def example_by_id(example_id: str | None) -> dict[str, Any] | None:
    return next((item for item in EXAMPLES if item["id"] == example_id), None)


def select_example(item: dict[str, Any]) -> None:
    """Apply example values before Streamlit instantiates this run's widgets."""
    st.session_state.selected_example = item["id"]
    st.session_state.uploader_nonce += 1
    st.session_state.diet_input = item["diet"]
    st.session_state.workflow_control = item["workflow"]
    st.session_state.result = None
    st.session_state.result_workflow = None


def show_metric(label: str, value: Any, unit: str) -> None:
    try:
        number = float(value)
        shown = f"{number:,.0f}" if number >= 100 or number.is_integer() else f"{number:,.1f}"
    except (TypeError, ValueError):
        shown = "—"
    st.metric(label, f"{shown}{unit}")


def render_recipe(result: dict[str, Any]) -> None:
    title = html.escape(str(result.get("title", "Recipe idea")))
    summary = html.escape(str(result.get("summary", "")))
    st.markdown(f'<div class="result-head"><h2>{title}</h2><p>{summary}</p></div>', unsafe_allow_html=True)

    nutrition = result.get("nutrition_per_serving", {}) or {}
    metric_cols = st.columns(5)
    metrics = [
        ("Calories", nutrition.get("calories_kcal"), " kcal"),
        ("Protein", nutrition.get("protein_g"), " g"),
        ("Carbs", nutrition.get("carbs_g"), " g"),
        ("Fat", nutrition.get("fat_g"), " g"),
        ("Fiber", nutrition.get("fiber_g"), " g"),
    ]
    for column, metric in zip(metric_cols, metrics):
        with column:
            show_metric(*metric)

    detail_cols = st.columns(3)
    detail_cols[0].metric("Servings", result.get("servings", "—"))
    detail_cols[1].metric("Prep", f'{result.get("prep_time_minutes", "—")} min')
    detail_cols[2].metric("Cook", f'{result.get("cook_time_minutes", "—")} min')

    left, right = st.columns([1, 1.25], gap="large")
    with left:
        st.subheader("Ingredients")
        for item in result.get("ingredients", []):
            if isinstance(item, dict):
                name = item.get("item", "Ingredient")
                amount = item.get("amount", "")
                note = f' — {item.get("note")}' if item.get("note") else ""
                st.markdown(f"- **{amount} {name}**{note}")
            else:
                st.markdown(f"- {item}")

        detected = result.get("detected_items", [])
        if detected:
            with st.expander("What NourishBot detected"):
                st.write(", ".join(map(str, detected)))

    with right:
        st.subheader("Method")
        for index, step in enumerate(result.get("instructions", []), 1):
            st.markdown(f"**{index}.** {step}")

    notes = result.get("dietary_notes", [])
    warnings = result.get("warnings", [])
    if notes:
        st.info("  •  ".join(map(str, notes)), icon="🌿")
    if warnings:
        st.warning("  •  ".join(map(str, warnings)), icon="⚠️")
    st.caption(f'Confidence: {result.get("confidence", "not provided")} · Nutrition is estimated per serving.')


def render_analysis(result: dict[str, Any]) -> None:
    title = html.escape(str(result.get("dish_name", "Nutrition analysis")))
    summary = html.escape(str(result.get("summary", "")))
    portion = html.escape(str(result.get("estimated_portion", "Visible portion")))
    st.markdown(
        f'<div class="result-head"><span class="section-kicker">Estimated portion · {portion}</span><h2>{title}</h2><p>{summary}</p></div>',
        unsafe_allow_html=True,
    )

    nutrition = result.get("nutrition", {}) or {}
    first = st.columns(4)
    for column, metric in zip(
        first,
        [
            ("Calories", nutrition.get("calories_kcal"), " kcal"),
            ("Protein", nutrition.get("protein_g"), " g"),
            ("Carbs", nutrition.get("carbs_g"), " g"),
            ("Fat", nutrition.get("fat_g"), " g"),
        ],
    ):
        with column:
            show_metric(*metric)

    second = st.columns(3)
    for column, metric in zip(
        second,
        [
            ("Fiber", nutrition.get("fiber_g"), " g"),
            ("Sugar", nutrition.get("sugar_g"), " g"),
            ("Sodium", nutrition.get("sodium_mg"), " mg"),
        ],
    ):
        with column:
            show_metric(*metric)

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Likely ingredients")
        for item in result.get("likely_ingredients", []):
            st.markdown(f"- {item}")
    with right:
        st.subheader("Nutrition highlights")
        for item in result.get("nutrition_highlights", []):
            st.markdown(f"- {item}")

    flags = result.get("dietary_flags", [])
    if flags:
        st.warning("  •  ".join(map(str, flags)), icon="🔎")
    st.caption(
        f'Confidence: {result.get("confidence", "not provided")} · '
        f'{result.get("disclaimer", "Image-based nutrition values are estimates.")}'
    )


for key, default in {
    "selected_example": None,
    "uploader_nonce": 0,
    "diet_input": "",
    "workflow_control": "recipe",
    "result": None,
    "result_workflow": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


st.markdown(
    '<div class="brand-row"><span class="brand-mark">N</span><span>NOURISHBOT</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
<div class="hero">
  <span class="eyebrow">AI-powered food intelligence</span>
  <h1>See your food.<br><span>Know what to make.</span></h1>
  <p>Upload what is in your kitchen for a tailored recipe, or photograph a finished dish for a fast nutrition estimate.</p>
</div>
""",
    unsafe_allow_html=True,
)


input_col, example_col = st.columns([0.95, 1.25], gap="large")

with input_col:
    st.markdown('<span class="section-kicker">01 · Your image</span>', unsafe_allow_html=True)
    st.header("Start with a photo")
    st.markdown('<p class="section-copy">JPG, PNG, or WebP · maximum 10 MB</p>', unsafe_allow_html=True)
    with st.container(border=True):
        uploaded = st.file_uploader(
            "Upload a food or fridge image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            key=f'uploader_{st.session_state["uploader_nonce"]}',
        )
        if uploaded is not None:
            st.session_state.selected_example = None

        selected = example_by_id(st.session_state.selected_example)
        if uploaded is not None:
            image_bytes = uploaded.getvalue()
            source_name = uploaded.name
            st.image(image_bytes, caption=source_name, width="stretch")
        elif selected:
            image_bytes = selected["image"].read_bytes()
            source_name = selected["name"]
            st.markdown(
                f'<div class="selected-source">Example selected · {html.escape(source_name)}</div>',
                unsafe_allow_html=True,
            )
            st.image(str(selected["image"]), caption=source_name, width="stretch")
        else:
            image_bytes = None
            source_name = ""

        st.text_input(
            "Dietary restrictions (optional)",
            placeholder="e.g. vegan, gluten-free, nut allergy",
            key="diet_input",
            help="For allergies, always verify ingredients independently.",
        )
        st.segmented_control(
            "What would you like?",
            options=["recipe", "analysis"],
            format_func=lambda value: "🍳  Create a recipe" if value == "recipe" else "📊  Analyze nutrition",
            key="workflow_control",
            width="stretch",
        )

    analyze = st.button(
        "Analyze with NourishBot  →",
        type="primary",
        width="stretch",
        disabled=image_bytes is None,
    )

with example_col:
    st.markdown('<span class="section-kicker">02 · Or try an example</span>', unsafe_allow_html=True)
    st.header("See what NourishBot can do")
    st.markdown('<p class="section-copy">Choose a row to load its image and settings.</p>', unsafe_allow_html=True)

    with st.container(border=True):
        for index, item in enumerate(EXAMPLES):
            thumb, meta, action = st.columns([0.65, 1.55, 0.7], vertical_alignment="center")
            with thumb:
                st.image(str(item["image"]), width="stretch")
            with meta:
                diet_label = item["diet"] or "no restriction"
                st.markdown(
                    f'<div class="example-meta"><div class="example-name">{html.escape(item["name"])}</div>'
                    f'<span class="pill accent">{item["workflow"]}</span><span class="pill">{diet_label}</span></div>',
                    unsafe_allow_html=True,
                )
            with action:
                st.button(
                    "Use",
                    key=f'use_{item["id"]}',
                    width="stretch",
                    on_click=select_example,
                    args=(item,),
                )
            if index < len(EXAMPLES) - 1:
                st.divider()


st.divider()
st.markdown('<span class="section-kicker">03 · Your result</span>', unsafe_allow_html=True)
st.header("Food intelligence, made useful")

if analyze and image_bytes:
    api_key = secret_or_env("GROQ_API_KEY")
    if not api_key:
        st.error(
            "GROQ_API_KEY is not configured. Add it to your environment or Streamlit app secrets, then try again.",
            icon="🔑",
        )
    else:
        try:
            with st.spinner("NourishBot is inspecting the image…"):
                st.session_state.result = analyze_with_groq(
                    image_bytes=image_bytes,
                    workflow=st.session_state.workflow_control,
                    dietary_restrictions=st.session_state.diet_input,
                    api_key=api_key,
                )
                st.session_state.result_workflow = st.session_state.workflow_control
        except Exception as exc:
            message = str(exc)
            lower_message = message.lower()
            if "api_key" in lower_message or "authentication" in lower_message:
                message = "Groq rejected the configured API key. Check the Streamlit secret and try again."
            elif "rate limit" in lower_message or "rate_limit" in lower_message or "429" in lower_message:
                message = "Groq is receiving requests too quickly. Please wait about 30 seconds, then try again."
            elif "timed out" in lower_message or "timeout" in lower_message:
                message = "Groq took too long to respond. Please try again in a moment."
            st.error(message, icon="⚠️")

if st.session_state.result:
    with st.container(border=True):
        if st.session_state.result_workflow == "recipe":
            render_recipe(st.session_state.result)
        else:
            render_analysis(st.session_state.result)
else:
    st.markdown(
        '<div class="empty-state"><div class="empty-icon">🍽️</div><strong>Your result will appear here</strong><br>Choose an image and a workflow, then analyze.</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    f'<div class="footer-note">Powered by Groq · {MODEL_ID} · Nutrition values are visual estimates, not medical advice.</div>',
    unsafe_allow_html=True,
)

