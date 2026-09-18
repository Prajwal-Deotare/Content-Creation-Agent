import base64
import os
import time
from datetime import datetime
import io
from PIL import Image

from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

# Load .env file from the project directory
load_dotenv()

# ─────────────────────────────────────────────
#  Page configuration (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Visionary AI · Image Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  Custom CSS — premium dark glassmorphism UI
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;600;700&display=swap');

    /* Global reset */
    html, body, [data-testid="stAppViewContainer"] {
        background: #f8fafc !important;
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }

    /* Animated gradient background */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 80% 60% at 20% 10%, rgba(30,58,138,0.06) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 80%, rgba(37,99,235,0.06) 0%, transparent 55%),
            radial-gradient(ellipse 50% 40% at 50% 50%, rgba(59,130,246,0.04) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #111827 !important;
        border-right: 1px solid #1f2937 !important;
    }
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown div {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #818cf8 !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] hr {
        border-top: 1px solid #374151 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] .stat-chip {
        background: #1f2937;
        border: 1px solid #374151;
        color: #e2e8f0;
    }

    /* Main content */
    .block-container {
        padding: 2rem 2.5rem !important;
        max-width: 1400px !important;
        position: relative;
        z-index: 1;
    }

    /* App header */
    .app-header {
        text-align: center;
        padding: 2.5rem 1rem 2rem;
        margin-bottom: 0.5rem;
    }
    .app-header .logo-badge {
        display: inline-block;
        background: #ffffff;
        border: 1px solid rgba(30,58,138,0.2);
        box-shadow: 0 4px 15px rgba(30,58,138,0.08);
        border-radius: 999px;
        padding: 0.4rem 1.2rem;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #1e3a8a;
        margin-bottom: 1rem;
    }
    .app-header h1 {
        font-family: 'Outfit', sans-serif;
        font-size: clamp(2.2rem, 5vw, 3.8rem);
        font-weight: 700;
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 40%, #3b82f6 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.15;
        margin: 0 0 0.75rem;
    }
    .app-header p {
        color: #475569;
        font-size: 1.05rem;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Glass card */
    .glass-card {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.04);
        box-shadow: 0 15px 40px -10px rgba(0,0,0,0.08);
        border-radius: 20px;
        padding: 1.75rem;
        backdrop-filter: blur(12px);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    }
    .glass-card:hover { 
        transform: translateY(-2px);
        box-shadow: 0 20px 40px -10px rgba(30,58,138,0.12);
        border-color: rgba(30,58,138,0.25); 
    }

    /* Textarea */
    .stTextArea textarea {
        background: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 14px !important;
        color: #0f172a !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        padding: 1rem 1.2rem !important;
        resize: vertical !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
    }
    .stTextArea textarea::placeholder { color: #94a3b8 !important; }
    .stTextArea label { color: #475569 !important; font-size: 0.875rem !important; font-weight: 500 !important; }

    /* Selectbox */
    div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 10px !important;
        color: #0f172a !important;
    }
    div[data-baseweb="select"] * {
        color: #0f172a !important;
    }
    ul[data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
    }
    ul[data-baseweb="menu"] li, ul[data-baseweb="menu"] span {
        color: #0f172a !important;
    }
    .stSelectbox label { color: #475569 !important; font-size: 0.875rem !important; font-weight: 500 !important; }

    /* Slider */
    .stSlider label { color: #475569 !important; font-size: 0.875rem !important; font-weight: 500 !important; }

    /* Generate button */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.85rem 2.5rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.02em !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 8px 25px rgba(30,58,138,0.25) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 35px rgba(30,58,138,0.35) !important;
        filter: brightness(1.1) !important;
    }
    .stButton > button:active { transform: translateY(0px) !important; }

    /* Status boxes */
    .stSuccess { background: rgba(34,197,94,0.1) !important; border: 1px solid rgba(34,197,94,0.3) !important; border-radius: 12px !important; color: #16a34a !important; }
    .stError   { background: rgba(239,68,68,0.1) !important; border: 1px solid rgba(239,68,68,0.3) !important; border-radius: 12px !important; color: #dc2626 !important; }
    .stWarning { background: rgba(234,179,8,0.1) !important; border: 1px solid rgba(234,179,8,0.3) !important; border-radius: 12px !important; color: #ca8a04 !important; }
    .stInfo    { background: rgba(37,99,235,0.08) !important; border: 1px solid rgba(37,99,235,0.2) !important; border-radius: 12px !important; color: #2563eb !important; }

    /* Spinner */
    .stSpinner > div { border-top-color: #2563eb !important; }

    /* Download button */
    [data-testid="stDownloadButton"] button {
        background: rgba(255,255,255,1) !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        color: #1e3a8a !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: #eff6ff !important;
        border-color: rgba(30,58,138,0.2) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 15px rgba(30,58,138,0.1) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        border-radius: 12px !important;
        color: #475569 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
    }
    .streamlit-expanderContent {
        background: #f8fafc !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }

    /* Stat chips */
    .stat-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        border-radius: 999px;
        padding: 0.3rem 0.8rem;
        font-size: 0.8rem;
        color: #475569;
        margin: 0.2rem;
    }
    .stat-chip .dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #2563eb;
        box-shadow: 0 0 6px rgba(37,99,235,0.6);
        display: inline-block;
    }

    /* Dividers */
    hr { border: none !important; border-top: 1px solid rgba(0,0,0,0.08) !important; margin: 1.5rem 0 !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(30,58,138,0.2); border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(30,58,138,0.4); }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
#  Azure client (cached)
# ─────────────────────────────────────────────
# Exact endpoint from the Azure AI sample code
ENDPOINT   = "https://content-creation-1-resource.services.ai.azure.com/openai/v1"
DEPLOYMENT = "gpt-image-2.5-sunburst"


def get_client() -> OpenAI:
    """Create an OpenAI client pointed at the Azure AI Services endpoint."""
    api_key = os.getenv("AZURE_API_KEY", "")
    if not api_key:
        st.error(
            "🔑 **API key missing.** Open the `.env` file in the project folder "
            "and fill in `AZURE_API_KEY=\"your-key-here\"`, then restart the app."
        )
        st.stop()
    return OpenAI(base_url=ENDPOINT, api_key=api_key)


# ─────────────────────────────────────────────
#  Session state
# ─────────────────────────────────────────────
if "history"          not in st.session_state: st.session_state.history          = []
if "current_image"    not in st.session_state: st.session_state.current_image    = None
if "current_prompt"   not in st.session_state: st.session_state.current_prompt   = ""
if "generation_time"  not in st.session_state: st.session_state.generation_time  = None


# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="app-header">
        <div class="logo-badge">✦ Powered by GPT Image 2.5 Sunburst · Azure AI</div>
        <h1>Visionary AI<br>Image Studio</h1>
        <p>Describe your imagination in words — watch it become stunning art in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:1.2rem 0 1rem;">
            <div style="font-size:2.2rem; margin-bottom:0.4rem; color:#818cf8;">✦</div>
            <div style="font-family:'Outfit',sans-serif; font-size:1.1rem; font-weight:700;
                        background:linear-gradient(135deg,#818cf8,#c084fc);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                Visionary AI
            </div>
            <div style="font-size:0.75rem; color:#94a3b8; margin-top:0.2rem;">Image Studio</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("## 🎛️ Image Settings")

    size_options = {
        "1024 × 1024  (Square)":    "1024x1024",
        "1792 × 1024  (Landscape)": "1792x1024",
        "1024 × 1792  (Portrait)":  "1024x1792",
    }
    size_label    = st.selectbox("Image Size", list(size_options.keys()), index=0)
    selected_size = size_options[size_label]

    quality_options = {
        "Auto (Model decides)": "auto",
        "High":   "high",
        "Medium": "medium",
        "Low":    "low",
    }
    quality_label    = st.selectbox("Quality", list(quality_options.keys()), index=0)
    selected_quality = quality_options[quality_label]

    style_options = {
        "Vivid (cinematic & bold)":   "vivid",
        "Natural (realistic & calm)": "natural",
    }
    style_label    = st.selectbox("Style", list(style_options.keys()), index=0)
    selected_style = style_options[style_label]

    st.divider()
    st.markdown("## ✨ Prompt Booster")
    st.caption("Appends a style modifier to your prompt automatically.")

    modifiers = {
        "None":               "",
        "Photorealistic":     ", ultra-photorealistic, 8K DSLR, golden hour",
        "Cinematic":          ", cinematic composition, anamorphic lens, film grain",
        "Anime / Manga":      ", anime style, Studio Ghibli, vibrant colors",
        "Oil Painting":       ", oil painting, impressionist brushstrokes, gallery quality",
        "Watercolor":         ", delicate watercolor illustration, soft washes",
        "Neon Cyberpunk":     ", neon cyberpunk city, rain-slicked streets, moody lighting",
        "Minimalist":         ", minimalist design, clean lines, pastel palette",
        "Fantasy Epic":       ", epic fantasy, dramatic clouds, magical atmosphere",
        "Pencil Sketch":      ", detailed pencil sketch, cross-hatching, monochrome",
    }
    modifier_label = st.selectbox("Style Modifier", list(modifiers.keys()), index=0)
    style_modifier = modifiers[modifier_label]

    st.divider()
    st.markdown("## 📊 Status")
    n_imgs = len(st.session_state.history)
    st.markdown(
        f"""
        <span class="stat-chip"><span class="dot"></span> Azure AI Connected</span><br>
        <span class="stat-chip">🖼️ {n_imgs} image{"s" if n_imgs != 1 else ""} generated</span><br>
        <span class="stat-chip">🤖 {DEPLOYMENT}</span>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.generation_time:
        st.markdown(
            f'<span class="stat-chip">⚡ Last gen: {st.session_state.generation_time:.1f}s</span>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
#  Main layout
# ─────────────────────────────────────────────
st.markdown(
    """
    <div style="margin-bottom:1.5rem; padding:1.2rem 1.5rem; background:#ffffff;
                border:1px solid rgba(0,0,0,0.05); box-shadow: 0 4px 15px rgba(0,0,0,0.03); border-radius:12px;
                display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;">
        <strong style="color:#2563eb; font-size: 0.95rem;">💡 Pro tips:</strong>
        <div style="font-size:0.85rem; color:#475569; display: flex; gap: 1.5rem; flex-wrap: wrap;">
            <span>• Start with the <em>main subject</em>, then add <em>style</em> &amp; <em>mood</em></span>
            <span>• Use adjectives: <em>ethereal, dramatic, soft, vivid, ancient</em></span>
            <span>• Mention lighting: <em>golden hour, neon glow, studio light</em></span>
            <span>• Reference art styles: <em>Ghibli, Monet, photorealistic, 8K</em></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1, 1.15], gap="large")

# ── LEFT — prompt & controls ──────────────────
with left_col:
    st.markdown(
        """
        <div style="margin-bottom:1rem;">
            <div style="font-family:'Outfit',sans-serif; font-size:1.2rem; font-weight:600; color:#1e293b; margin-bottom:0.2rem;">
                🎨 Describe Your Image
            </div>
            <div style="font-size:0.85rem; color:#475569;">
                Be specific — include subjects, mood, setting, and artistic style.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prompt = st.text_area(
        label="Prompt",
        placeholder=(
            "e.g. A lone astronaut standing on the edge of a glowing crater on Mars "
            "at sunset, cinematic lighting, epic scale, hyper-detailed…"
        ),
        height=180,
        label_visibility="collapsed",
        key="prompt_input",
    )

    st.markdown(
        """
        <style>
        /* Add padding to text area so text doesn't go under the button */
        [data-testid="stTextArea"] textarea {
            padding-bottom: 50px !important;
        }
        
        /* Turn the file uploader into a round icon button */
        [data-testid="stFileUploader"] {
            width: 44px !important;
            height: 44px !important;
            margin: 0 !important;
            padding: 0 !important;
            min-height: 44px !important;
            /* Move it up inside the text area */
            margin-top: -90px !important;
            margin-left: 14px !important;
            margin-bottom: 45px !important;
            z-index: 99 !important;
        }
        [data-testid="stFileUploader"] label {
            display: none !important;
        }
        [data-testid="stFileUploader"] section {
            padding: 0 !important;
            background-color: #212121 !important;
            border: none !important;
            border-radius: 50% !important;
            width: 44px !important;
            height: 44px !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            transition: background-color 0.2s;
            position: relative !important;
        }
        [data-testid="stFileUploader"] section:hover {
            background-color: #333333 !important;
        }
        /* Hide default cloud icon, text, and button */
        [data-testid="stFileUploader"] section > * {
            display: none !important;
        }
        /* But keep the file input active and covering the section */
        [data-testid="stFileUploader"] section > input {
            display: block !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            opacity: 0 !important;
            z-index: 10 !important;
            cursor: pointer !important;
        }
        /* Inject the custom image+ SVG icon */
        [data-testid="stFileUploader"] section::before {
            content: '';
            display: block;
            position: absolute;
            top: 10px;
            left: 10px;
            width: 24px;
            height: 24px;
            background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23e2e8f0%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%224%22%20y%3D%224%22%20width%3D%2216%22%20height%3D%2216%22%20rx%3D%222%22%20ry%3D%222%22%3E%3C%2Frect%3E%3Cpath%20d%3D%22M4%2016l4-4%204%204%22%3E%3C%2Fpath%3E%3Cpath%20d%3D%22M10%2014l3-3%207%207%22%3E%3C%2Fpath%3E%3Ccircle%20cx%3D%227%22%20cy%3D%227%22%20r%3D%224%22%20fill%3D%22%23212121%22%20stroke%3D%22%23e2e8f0%22%3E%3C%2Fcircle%3E%3Cline%20x1%3D%227%22%20y1%3D%225%22%20x2%3D%227%22%20y2%3D%229%22%3E%3C%2Fline%3E%3Cline%20x1%3D%225%22%20y1%3D%227%22%20x2%3D%229%22%20y2%3D%227%22%3E%3C%2Fline%3E%3C%2Fsvg%3E");
            background-repeat: no-repeat;
            background-position: center;
            z-index: 5;
            pointer-events: none;
        }
        /* Style the uploaded file display below the button */
        [data-testid="stFileUploader"] [data-testid="stUploadedFile"] {
            position: absolute;
            top: 50px;
            left: 0;
            background: #212121;
            color: #e2e8f0;
            border-radius: 8px;
            border: 1px solid #333;
            width: max-content;
            padding: 4px;
            z-index: 100;
        }
        /* Tooltip container styling */
        .tooltip-container {
            display: inline-block;
            position: relative;
        }
        .tooltip-container:hover::after {
            content: 'Attach an image to use as reference for generation';
            position: absolute;
            bottom: 110%;
            left: 0;
            background: #212121;
            color: #e2e8f0;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            white-space: nowrap;
            z-index: 1000;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            pointer-events: none;
        }
        </style>
        <div class="tooltip-container">
        """,
        unsafe_allow_html=True
    )
    
    uploaded_image = st.file_uploader("Upload reference image (optional)", type=["png", "jpg", "jpeg"])
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("➕ Negative Prompt  (optional)"):
        negative_prompt = st.text_area(
            label="Negative Prompt",
            placeholder="Things to exclude: blurry, low quality, watermark, text…",
            height=80,
            label_visibility="collapsed",
            key="neg_prompt_input",
        )

    with st.expander("💡 Need inspiration? Try these prompts"):
        inspirations = [
            "A majestic dragon soaring above a medieval city at dawn, fantasy art, dramatic lighting",
            "Portrait of a cyberpunk samurai, neon-lit Tokyo alley, rain, cinematic bokeh",
            "Enchanted forest with glowing mushrooms, fireflies, moonlit mist, magical realism",
            "Abstract ocean waves made of liquid gold and sapphire, high contrast, minimalist",
            "Cozy log cabin in a snowstorm, warm light through frosted windows, oil painting style",
            "Futuristic Mars colony at sunset, silhouetted astronauts, vast crimson sky",
            "A watercolor map of an imaginary island with hidden treasures and sea monsters",
            "Black cat sitting on a stack of glowing spell books, mystical library, deep shadows",
        ]
        def set_prompt(insp_text):
            st.session_state["prompt_input"] = insp_text

        for insp in inspirations:
            st.button(
                f"→ {insp[:72]}{'…' if len(insp) > 72 else ''}",
                key=f"insp_{hash(insp)}",
                on_click=set_prompt,
                args=(insp,),
            )

    st.markdown("<div style='margin-top:1.25rem;'>", unsafe_allow_html=True)
    generate_clicked = st.button("✦ Generate Image", type="primary", width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)


# ── RIGHT — image output ──────────────────────
with right_col:

    if generate_clicked:
        raw_prompt = prompt.strip()
        final_prompt = (raw_prompt + style_modifier).strip() if raw_prompt else ""
        
        if not final_prompt and uploaded_image is None:
            st.warning("✏️ Please enter a prompt or upload an image before generating.")
        else:
            with st.spinner("✦ Conjuring your image…  (this may take 15–30 seconds)"):
                try:
                    client = get_client()

                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n{'='*60}")
                    print(f"[{now_str}] >> IMAGE GENERATION STARTED")
                    print(f"  Model   : {DEPLOYMENT}")
                    print(f"  Size    : {selected_size}")
                    print(f"  Prompt  : {final_prompt[:120]}{'...' if len(final_prompt) > 120 else ''}")
                    print(f"{'='*60}")

                    t0       = time.time()
                    
                    if uploaded_image is not None:
                        # Process image for edit or variation
                        image = Image.open(uploaded_image).convert("RGBA")
                        w, h = map(int, selected_size.split('x'))
                        # Azure/OpenAI typically requires square images, but we'll resize to selected_size
                        image = image.resize((w, h))
                        
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_bytes_payload = img_byte_arr.getvalue()
                        
                        if final_prompt:
                            # Auto-masking: Create a transparent mask
                            mask = Image.new("RGBA", image.size, (255, 255, 255, 0))
                            mask_byte_arr = io.BytesIO()
                            mask.save(mask_byte_arr, format='PNG')
                            mask_bytes_payload = mask_byte_arr.getvalue()
                            
                            response = client.images.edit(
                                model=DEPLOYMENT,
                                image=img_bytes_payload,
                                mask=mask_bytes_payload,
                                prompt=final_prompt,
                                n=1,
                                size=selected_size,
                            )
                        else:
                            # Variation
                            response = client.images.create_variation(
                                model=DEPLOYMENT,
                                image=img_bytes_payload,
                                n=1,
                                size=selected_size,
                            )
                    else:
                        response = client.images.generate(
                            model=DEPLOYMENT,
                            prompt=final_prompt,
                            n=1,
                            size=selected_size,
                        )
                        
                    elapsed  = time.time() - t0

                    # Azure returns b64_json by default
                    image_data = response.data[0]
                    if image_data.b64_json:
                        img_bytes = base64.b64decode(image_data.b64_json)
                    elif image_data.url:
                        import urllib.request
                        img_bytes = urllib.request.urlopen(image_data.url).read()
                    else:
                        raise ValueError("No image data returned from the API.")

                    done_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    img_kb = len(img_bytes) / 1024
                    print(f"\n[{done_str}] << IMAGE GENERATION COMPLETE")
                    print(f"  Time    : {elapsed:.1f}s")
                    print(f"  Size    : {img_kb:.1f} KB")
                    print(f"{'='*60}\n")

                    st.session_state.current_image   = img_bytes
                    st.session_state.current_prompt  = final_prompt
                    st.session_state.generation_time = elapsed
                    st.session_state.history.insert(
                        0,
                        {
                            "prompt":      final_prompt,
                            "image_bytes": img_bytes,
                            "size":        selected_size,
                            "ts":          datetime.now().strftime("%H:%M:%S"),
                        },
                    )
                    st.rerun()

                except Exception as exc:
                    err_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n[{err_str}] !! IMAGE GENERATION FAILED: {exc}\n")
                    st.error(f"❌ Generation failed: {exc}")

    if st.session_state.current_image:
        img_bytes = st.session_state.current_image

        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:1rem;">
                <div style="width:8px; height:8px; border-radius:50%; background:#22c55e;
                            box-shadow:0 0 8px #22c55e;"></div>
                <span style="font-size:0.9rem; color:#475569; font-weight:500;">Image ready</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.image(img_bytes, width='stretch')

        displayed_prompt = st.session_state.current_prompt
        st.markdown(
            f"""
            <div style="margin-top:0.75rem; padding:0.85rem 1rem;
                        background:#ffffff; border-radius:10px;
                        border:1px solid rgba(0,0,0,0.05); box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                <div style="font-size:0.75rem; color:#475569; font-weight:500;
                            letter-spacing:0.06em; text-transform:uppercase; margin-bottom:0.3rem;">
                    Prompt Used
                </div>
                <div style="font-size:0.88rem; color:#475569; line-height:1.55; font-style:italic;">
                    {displayed_prompt}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        dl_col, stat_col = st.columns([1, 1])
        with dl_col:
            filename = f"visionary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            st.download_button(
                label="⬇️  Download PNG",
                data=img_bytes,
                file_name=filename,
                mime="image/png",
                width='stretch',
            )
        with stat_col:
            if st.session_state.generation_time:
                st.markdown(
                    f"""
                    <div style="height:100%; display:flex; align-items:center; justify-content:center;
                                flex-direction:column; gap:0.2rem;">
                        <div style="font-size:1.5rem; font-weight:700;
                                    background:linear-gradient(135deg,#1e3a8a,#3b82f6);
                                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                            {st.session_state.generation_time:.1f}s
                        </div>
                        <div style="font-size:0.75rem; color:#475569;">Generation time</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:
        st.markdown(
            """
            <div style="
                min-height:420px; display:flex; flex-direction:column;
                align-items:center; justify-content:center;
                border:2px dashed rgba(30,58,138,0.15); border-radius:20px;
                padding:3rem; text-align:center; background:#eff6ff;">
                <div style="font-size:3.5rem; margin-bottom:1rem; opacity:0.6;">🎨</div>
                <div style="font-family:'Outfit',sans-serif; font-size:1.3rem; font-weight:600;
                            color:#475569; margin-bottom:0.6rem;">
                    Your image will appear here
                </div>
                <div style="font-size:0.9rem; color:#334155; max-width:280px; line-height:1.6;">
                    Write a prompt on the left, choose your settings,
                    then click <strong style="color:#2563eb;">Generate Image</strong>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
#  Generation History
# ─────────────────────────────────────────────
if st.session_state.history:
    st.divider()
    st.markdown(
        """
        <div style="font-family:'Outfit',sans-serif; font-size:1.15rem; font-weight:600;
                    color:#1e293b; margin-bottom:1rem;">
            🕘 Generation History
        </div>
        """,
        unsafe_allow_html=True,
    )

    items    = st.session_state.history[:8]
    num_cols = min(4, len(items))
    hist_cols = st.columns(num_cols, gap="small")

    for idx, item in enumerate(items):
        col = hist_cols[idx % num_cols]
        with col:
            st.image(item["image_bytes"], width='stretch')
            short = item["prompt"][:50] + ("…" if len(item["prompt"]) > 50 else "")
            st.markdown(
                f"""
                <div style="font-size:0.73rem; color:#475569; margin-top:0.3rem;
                            text-align:center; font-style:italic; line-height:1.4;">
                    {short}<br>
                    <span style="color:#334155;">{item['size']} · {item['ts']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                "⬇️",
                data=item["image_bytes"],
                file_name=f"visionary_{item['ts'].replace(':','')}.png",
                mime="image/png",
                key=f"hist_dl_{idx}",
                width='stretch',
            )

    if len(st.session_state.history) > 8:
        st.caption(f"Showing 8 of {len(st.session_state.history)} images this session.")

    if st.button("🗑️  Clear History", key="clear_history"):
        st.session_state.history          = []
        st.session_state.current_image    = None
        st.session_state.current_prompt   = ""
        st.session_state.generation_time  = None
        st.rerun()
