import base64
import os
import time
import json
from datetime import datetime
import io
from PIL import Image

from dotenv import load_dotenv
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

from content_agent import ContentAgent
from models import ContentRequest, ContentSession

# Load .env file from the project directory
load_dotenv()

# ─────────────────────────────────────────────
#  Page configuration (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Unified AI Studio",
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
    [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stRadio label {
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] .stat-chip {
        background: #1f2937;
        border: 1px solid #374151;
        color: #e2e8f0;
    }
    
    /* Sidebar BIG Navigation buttons styling */
    div.stButton > button.big-nav-btn {
        height: auto !important;
        padding: 18px 20px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        transition: all 0.2s ease !important;
        margin-bottom: 8px !important;
        justify-content: center !important;
        text-align: center !important;
    }
    div.stButton > button.big-nav-btn p {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    div.stButton > button.big-nav-btn[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #cbd5e1 !important;
    }
    div.stButton > button.big-nav-btn[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
    }
    div.stButton > button.big-nav-btn[kind="primary"] {
        background: linear-gradient(135deg, #5b5ce2 0%, #4748c7 100%) !important;
        color: white !important;
        box-shadow: 0 6px 20px rgba(91,92,226,0.4) !important;
        border: none !important;
    }

    /* Sidebar Navigation buttons styling */
    div.stButton > button.nav-btn {
        background: transparent !important;
        color: #cbd5e1 !important;
        border: none !important;
        justify-content: flex-start !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        width: 100% !important;
        text-align: left !important;
        margin-bottom: 5px !important;
        box-shadow: none !important;
    }
    div.stButton > button.nav-btn:hover {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
    }

    /* Main content */
    .block-container {
        padding: 2rem 2.5rem !important;
        max-width: 1400px !important;
        position: relative;
        z-index: 1;
    }

    /* App header (Image Studio) */
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
    
    /* App header (Content Studio) */
    .content-header {
        padding: 1.5rem 1rem 1.5rem;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    .content-header h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 40%, #3b82f6 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.2rem;
    }
    .content-header p {
        color: #475569;
        font-size: 0.95rem;
        margin: 0;
    }
    .state-pill {
        padding: 8px 16px; 
        background: #eef0ff; 
        color: #4748c7; 
        border-radius: 999px;
        font-size: 0.8rem; 
        font-weight: 700;
        text-transform: uppercase;
        border: 1px solid #b9baff;
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

    /* Text inputs and textareas */
    .stTextInput input, .stTextArea textarea {
        background: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 12px !important;
        color: #0f172a !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 1rem !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    .stTextInput input:disabled, .stTextArea textarea:disabled {
        background: #f8fafc !important;
        color: #475569 !important;
        -webkit-text-fill-color: #475569 !important;
        opacity: 1 !important;
    }
    input::placeholder, textarea::placeholder,
    [data-baseweb="input"] input::placeholder, 
    [data-baseweb="textarea"] textarea::placeholder {
        color: #94a3b8 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #94a3b8 !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label { 
        color: #344054 !important; 
        font-size: 0.85rem !important; 
        font-weight: 600 !important; 
    }
    
    /* Selectbox */
    div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 12px !important;
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

    /* Generate button (Primary) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #5b5ce2 0%, #4748c7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 8px 18px rgba(91,92,226,0.22) !important;
        width: 100% !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(91,92,226,0.3) !important;
    }

    /* Standard Secondary Buttons (e.g. Select Option) */
    .block-container .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%) !important;
        color: #3730a3 !important;
        border: 2px solid #a5b4fc !important;
        border-radius: 14px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.08) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .block-container .stButton > button[kind="secondary"]::before {
        content: '' !important;
        position: absolute !important;
        inset: 0 !important;
        border-radius: 12px !important;
        padding: 2px !important;
        background: linear-gradient(135deg, #818cf8, #6366f1, #4f46e5) !important;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0) !important;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0) !important;
        -webkit-mask-composite: xor !important;
        mask-composite: exclude !important;
        opacity: 0 !important;
        transition: opacity 0.3s ease !important;
    }
    .block-container .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%) !important;
        border-color: #818cf8 !important;
        color: #312e81 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.2), 0 0 0 1px rgba(99, 102, 241, 0.1) !important;
    }
    .block-container .stButton > button[kind="secondary"]:hover::before {
        opacity: 1 !important;
    }
    .block-container .stButton > button[kind="secondary"]:active {
        transform: translateY(0) scale(0.98) !important;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.15) !important;
    }

    /* Option Cards */
    .option-card {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .option-badge {
        width: 32px; height: 32px;
        border-radius: 8px;
        background: #f0f1ff; color: #4b4ccf;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 14px;
        margin-bottom: 12px;
    }
    .option-title { font-weight: 600; font-size: 1.05rem; margin-bottom: 10px; color: #1e293b; }
    .option-text { font-size: 0.9rem; color: #475569; line-height: 1.6; margin-bottom: 15px; flex-grow: 1; 
                   display: -webkit-box; -webkit-line-clamp: 8; -webkit-box-orient: vertical; overflow: hidden; }

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

    /* Hide Streamlit branding */
    /* #MainMenu, footer { visibility: hidden; } */
    /* [data-testid="stToolbar"] { display: none; } */
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  State initialization
# ─────────────────────────────────────────────
# -- Image Studio State
if "history"          not in st.session_state: st.session_state.history          = []
if "current_image"    not in st.session_state: st.session_state.current_image    = None
if "current_prompt"   not in st.session_state: st.session_state.current_prompt   = ""
if "generation_time"  not in st.session_state: st.session_state.generation_time  = None

# -- Content Studio State
@st.cache_resource
def get_agent():
    return ContentAgent()

agent = get_agent()

if "text_view" not in st.session_state:
    st.session_state.text_view = "write"

if "drafts" not in st.session_state:
    st.session_state.drafts = []

if "approved" not in st.session_state:
    st.session_state.approved = []

if "session" not in st.session_state:
    st.session_state.session = None

if "revision_input" not in st.session_state:
    st.session_state.revision_input = ""

def set_text_view(view_name):
    st.session_state.text_view = view_name
    
def save_draft():
    s = st.session_state.session
    if s and s.current_content:
        draft_item = {
            "session_id": id(s), 
            "title": s.options[0].title if s.options else "Draft",
            "content": s.current_content,
            "platform": s.request.platform,
            "date": datetime.now().strftime("%I:%M %p"),
            "session_obj": s
        }
        for i, d in enumerate(st.session_state.drafts):
            if d["session_id"] == draft_item["session_id"]:
                st.session_state.drafts[i] = draft_item
                return
        st.session_state.drafts.append(draft_item)

# ─────────────────────────────────────────────
#  Sidebar unified navigation
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="padding:1.2rem 0 2rem; text-align: center;">
            <div style="font-size:2.2rem; margin-bottom:0.4rem; color:#818cf8;">✦</div>
            <div style="font-family:'Outfit',sans-serif; font-size:1.1rem; font-weight:700;
                        background:linear-gradient(135deg,#818cf8,#c084fc);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                Unified AI Studio
            </div>
            <div style="font-size:0.75rem; color:#94a3b8; margin-top:0.2rem;">Text & Image Creation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("## 🧭 Navigation")
    
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "Text Content Agent"

    if st.button("Text Content Agent", use_container_width=True, type="primary" if st.session_state.app_mode == "Text Content Agent" else "secondary"):
        st.session_state.app_mode = "Text Content Agent"
        st.rerun()
        
    if st.button("Image Creator Agent", use_container_width=True, type="primary" if st.session_state.app_mode == "Image Creator Agent" else "secondary"):
        st.session_state.app_mode = "Image Creator Agent"
        st.rerun()
        
    st.markdown(
        """<script>
        const navButtons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
        if(navButtons.length >= 2) {
            navButtons[0].classList.add('big-nav-btn');
            navButtons[1].classList.add('big-nav-btn');
        }
        </script>""", unsafe_allow_html=True
    )
    
    app_mode = st.session_state.app_mode
    st.divider()

    if app_mode == "Text Content Agent":
        # Text Agent Sidebar Navigation
        st.markdown("## 📝 Content Studio")
        if st.button("✦ Write Content", key="nav_write", use_container_width=True):
            set_text_view("write")
        if st.button(f"◫ My Drafts ({len(st.session_state.drafts)})", key="nav_drafts", use_container_width=True):
            set_text_view("drafts")
        if st.button(f"✓ Approved ({len(st.session_state.approved)})", key="nav_approved", use_container_width=True):
            set_text_view("approved")

        # Add style to make these buttons look like the sidebar navigation
        st.markdown(
            """<script>
            const buttons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
            for(let i=2; i<buttons.length; i++) {
                buttons[i].classList.add('nav-btn');
            }
            </script>""", unsafe_allow_html=True
        )
        
    elif app_mode == "Image Creator Agent":
        # Image Agent Sidebar Controls
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
            <span class="stat-chip">🖼️ {n_imgs} image{"s" if n_imgs != 1 else ""} generated</span>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.generation_time:
            st.markdown(
                f'<span class="stat-chip">⚡ Last gen: {st.session_state.generation_time:.1f}s</span>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────
#  Main Views Router
# ─────────────────────────────────────────────

if app_mode == "Text Content Agent":
    # ─────────────────────────────────────────────
    #  TEXT CONTENT AGENT VIEW
    # ─────────────────────────────────────────────
    view = st.session_state.text_view

    if view == "write":
        session: ContentSession = st.session_state.session
        current_state = session.state if session else "NEW_REQUEST"
        
        st.markdown(
            """
            <div class="content-header">
                <div>
                    <p style="color: #667085; font-size: 13px; font-weight: 500; margin-bottom: 8px;">Content Studio / <b>Write Content</b></p>
                    <h1>Create high-quality content</h1>
                    <p>Describe what you need. The AI will generate three distinct directions for you to choose from.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        left_col, right_col = st.columns([1, 1.5], gap="large")
        
        with left_col:
            with st.container():
                st.markdown(
                    """
                    <div style="margin-bottom: 12px;">
                        <h2 style="margin:0; font-size: 1.1rem; color: #1e293b;">Content brief</h2>
                    </div>
                    """, unsafe_allow_html=True
                )
                
                topic = st.text_area("What is this about?", placeholder="e.g. Artificial Intelligence in healthcare", height=80,
                                     value=session.request.topic if session else "")
                
                platform_options = ["LinkedIn", "Instagram", "Facebook", "X / Twitter", "Blog", "Website", "Email", "Newsletter", "Press Release", "Other"]
                default_index = 0
                if session and session.request.platform in platform_options:
                    default_index = platform_options.index(session.request.platform)
                platform = st.selectbox("Where will you post it?", platform_options, index=default_index)
                
                audience = st.text_input("Who is it for?", placeholder="e.g. Healthcare professionals",
                                         value=session.request.audience if session else "")
                mood = st.text_input("What mood?", placeholder="e.g. Professional and inspiring",
                                     value=session.request.mood if session else "")
                
                length_options = ["Short", "Medium", "Long"]
                default_length_index = 1
                if session and session.request.length in length_options:
                    default_length_index = length_options.index(session.request.length)
                length = st.selectbox("How long should it be?", length_options, index=default_length_index)
                
                goal = st.text_area("What should people do after reading?", placeholder="e.g. Share their opinion in the comments", height=80,
                                    value=session.request.goal if session else "")
                
                if st.button("Generate 3 options", type="primary", use_container_width=True):
                    if not topic or not audience or not mood or not goal:
                        st.error("Please fill out all fields.")
                    else:
                        with st.spinner("Creating three content directions..."):
                            try:
                                req = ContentRequest(topic=topic, platform=platform, audience=audience, mood=mood, length=length, goal=goal)
                                st.session_state.session = agent.generate_options(req)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error generating content: {e}")

        with right_col:
            if not session:
                st.markdown(
                    """
                    <div style="min-height: 500px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
                                background: white; border-radius: 16px; border: 1px solid rgba(0,0,0,0.08); padding: 50px;">
                        <div style="width: 70px; height: 70px; border-radius: 20px; background: #eef0ff; color: #5b5ce2; 
                                    display: flex; align-items: center; justify-content: center; font-size: 29px; margin-bottom: 16px;">✦</div>
                        <h3 style="margin: 0 0 8px; font-size: 19px; color: #1e293b;">Your content options will appear here</h3>
                        <p style="margin: 0; max-width: 420px; color: #667085; font-size: 14px; line-height: 1.6;">
                            Complete the brief on the left and generate three distinct options. You can then select one, refine it, and approve the final version.
                        </p>
                    </div>
                    """, unsafe_allow_html=True
                )
            elif session.state == "OPTIONS_READY":
                st.markdown(
                    """
                    <div style="margin-bottom: 18px;">
                        <h2 style="margin: 0; font-size: 1.1rem; color: #1e293b;">Choose your direction</h2>
                        <p style="margin: 4px 0 0; color: #667085; font-size: 13px;">Three distinct approaches generated from your brief.</p>
                    </div>
                    """, unsafe_allow_html=True
                )
                
                c1, c2, c3 = st.columns(3)
                cols = [c1, c2, c3]
                
                for i, opt in enumerate(session.options):
                    with cols[i]:
                        st.markdown(
                            f"""
                            <div class="option-card">
                                <div class="option-badge">{opt.id}</div>
                                <div class="option-title">{opt.title}</div>
                                <div class="option-text">{opt.content}</div>
                            </div>
                            """, unsafe_allow_html=True
                        )
                        if st.button(f"Select Option {opt.id}", key=f"sel_{opt.id}", use_container_width=True):
                            st.session_state.session = agent.select_option(session, opt.id)
                            save_draft()
                            st.rerun()

            elif session.state in ["OPTION_SELECTED", "REVISING", "REVISED", "READY_TO_SAVE"]:
                
                hc1, hc2 = st.columns([3, 1])
                with hc1:
                    st.markdown(
                        f"""
                        <div style="margin-bottom: 16px;">
                            <h2 style="margin:0; font-size: 1.1rem; color: #1e293b;">Selected content</h2>
                            <div style="color: #667085; font-size: 12px; margin-top: 4px;">Option {session.selected_option} · {session.revision_count} revisions</div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                with hc2:
                    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                    if st.button("➕ New Draft", key="new_draft_selected", use_container_width=True):
                        st.session_state.session = None
                        st.rerun()
                
                disabled = session.approved
                edited_content = st.text_area("Content", value=session.current_content, height=300, disabled=disabled, label_visibility="collapsed")
                
                if edited_content != session.current_content and not disabled:
                    session.current_content = edited_content
                    save_draft()
                
                # Show notification if just revised
                if st.session_state.get("just_revised", False):
                    st.toast("✨ Revision complete!", icon="✨")
                    st.session_state.just_revised = False

                import streamlit.components.v1 as components
                
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    safe_content = json.dumps(session.current_content).replace("<", "\\u003c")
                    copy_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <style>
                    .copy-btn {{
                        background: #f8fafc;
                        color: #1e293b;
                        border: 1px solid #cbd5e1;
                        border-radius: 12px;
                        padding: 0.65rem 1rem;
                        font-weight: 600;
                        transition: all 0.2s ease;
                        width: 100%;
                        cursor: pointer;
                        font-family: 'Inter', sans-serif;
                        font-size: 1rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 8px;
                        box-sizing: border-box;
                    }}
                    .copy-btn:hover {{
                        background: #e2e8f0;
                        border-color: #94a3b8;
                    }}
                    </style>
                    </head>
                    <body style="margin: 0; padding: 0;">
                        <button class="copy-btn" onclick="copyText()">
                            📋 <span>Copy content</span>
                        </button>
                        <script>
                        function copyText() {{
                            const text = {safe_content};
                            if (navigator.clipboard && window.isSecureContext) {{
                                navigator.clipboard.writeText(text).then(showSuccess);
                            }} else {{
                                const textArea = document.createElement("textarea");
                                textArea.value = text;
                                textArea.style.position = "absolute";
                                textArea.style.left = "-999999px";
                                document.body.prepend(textArea);
                                textArea.select();
                                try {{
                                    document.execCommand('copy');
                                    showSuccess();
                                }} catch (error) {{
                                    console.error(error);
                                }} finally {{
                                    textArea.remove();
                                }}
                            }}
                        }}
                        function showSuccess() {{
                            const span = document.querySelector('span');
                            const original = span.innerText;
                            span.innerText = 'Copied!';
                            setTimeout(() => span.innerText = original, 2000);
                        }}
                        </script>
                    </body>
                    </html>
                    """
                    components.html(copy_html, height=55)

                with col_b:
                    if not session.approved:
                        if st.button("✓ Approve content", type="primary", use_container_width=True):
                            st.session_state.session = agent.approve(session)
                            app_item = {
                                "session_id": id(session), 
                                "title": session.options[0].title if session.options else "Approved",
                                "content": session.current_content,
                                "platform": session.request.platform,
                                "date": datetime.now().strftime("%I:%M %p")
                            }
                            st.session_state.approved.insert(0, app_item)
                            st.session_state.drafts = [d for d in st.session_state.drafts if d["session_id"] != app_item["session_id"]]
                            st.rerun()
                    else:
                        st.success("✓ Content Approved and ready to use.")
                
                if not session.approved:
                    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
                    rev_req = st.text_area("What would you like to change?", placeholder="e.g. Make the opening stronger.", height=80)
                    st.markdown(
                        """
                        <style>
                        div[data-testid="stButton"].revise-btn > button {
                            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
                            color: white !important;
                            border: none !important;
                            border-radius: 12px !important;
                            padding: 0.7rem 2rem !important;
                            font-weight: 800 !important;
                            font-size: 1.05rem !important;
                            letter-spacing: 0.04em !important;
                            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35) !important;
                            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                        }
                        div[data-testid="stButton"].revise-btn > button:hover {
                            transform: translateY(-2px) !important;
                            box-shadow: 0 10px 30px rgba(79, 70, 229, 0.45) !important;
                            background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
                        }
                        div[data-testid="stButton"].revise-btn > button:active {
                            transform: translateY(0) scale(0.98) !important;
                        }
                        </style>
                        """, unsafe_allow_html=True
                    )
                    revise_container = st.container()
                    with revise_container:
                        if st.button("✏️  Revise", key="revise_btn"):
                            if rev_req:
                                with st.spinner("Revising..."):
                                    try:
                                        st.session_state.session = agent.revise(session, rev_req)
                                        save_draft()
                                        st.session_state.just_revised = True
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error revising content: {e}")
                    # Apply the revise-btn class via JS
                    st.markdown(
                        """
                        <script>
                        const allBtns = window.parent.document.querySelectorAll('[data-testid="stButton"]');
                        allBtns.forEach(btn => {
                            const inner = btn.querySelector('button');
                            if (inner && inner.textContent.includes('Revise')) {
                                btn.classList.add('revise-btn');
                            }
                        });
                        </script>
                        """, unsafe_allow_html=True
                    )
                


    elif view == "drafts":
        dc1, dc2 = st.columns([3, 1])
        with dc1:
            st.markdown(
                """
                <div class="content-header" style="margin-bottom: 0px;">
                    <div>
                        <h1>My Drafts</h1>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
        with dc2:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            if st.button("➕ New Draft", key="new_draft_page", use_container_width=True):
                st.session_state.session = None
                set_text_view("write")
                st.rerun()
        
        st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        if not st.session_state.drafts:
            st.info("No drafts yet. Generate some content first!")
        else:
            for d in st.session_state.drafts:
                with st.container():
                    st.markdown('<div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.08); margin-bottom: 16px;">', unsafe_allow_html=True)
                    
                    col_title, col_btn, col_pill = st.columns([5.5, 1, 1])
                    with col_title:
                        st.markdown(f'<h3 style="margin: 0 0 5px; font-size: 1.1rem; color: #1e293b;">{d["title"]}</h3>', unsafe_allow_html=True)
                    with col_btn:
                        st.markdown("<div style='margin-top: -10px;'></div>", unsafe_allow_html=True)
                        if st.button("📂 Open", key=f"open_draft_{d['session_id']}", use_container_width=True):
                            if d.get("session_obj"):
                                st.session_state.session = d["session_obj"]
                                set_text_view("write")
                                st.rerun()
                            else:
                                st.warning("This draft is from an older session and cannot be reopened.")
                    with col_pill:
                        st.markdown('<div style="text-align: right;"><span class="state-pill" style="font-size: 0.7rem;">DRAFT</span></div>', unsafe_allow_html=True)
                    
                    st.markdown(
                        f"""
                        <div style="color: #667085; font-size: 0.85rem; margin-bottom: 12px; margin-top: -10px;">{d['platform']} · Last updated {d['date']}</div>
                        <div style="color: #344054; font-size: 0.95rem; line-height: 1.6; max-height: 100px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                            {d['content']}
                        </div>
                        </div>
                        """, unsafe_allow_html=True
                    )

    elif view == "approved":
        st.markdown(
            """
            <div class="content-header">
                <div>
                    <h1>Approved Content</h1>
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        
        if not st.session_state.approved:
            st.info("No approved content yet.")
        else:
            for a in st.session_state.approved:
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.08); margin-bottom: 16px;">
                            <div style="display:flex; justify-content: space-between;">
                                <h3 style="margin: 0 0 5px; font-size: 1.1rem; color: #1e293b;">{a['title']}</h3>
                                <span class="state-pill" style="font-size: 0.75rem; background: #ecfdf3; color: #027a48; border-color: #a6f4c5; display: flex; align-items: center; gap: 4px;">✓ APPROVED</span>
                            </div>
                            <div style="color: #667085; font-size: 0.85rem; margin-bottom: 12px;">{a['platform']} · Approved at {a['date']}</div>
                            <div style="color: #344054; font-size: 0.95rem; line-height: 1.6;">
                                {a['content']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                    
                    safe_app_content = json.dumps(a['content']).replace("<", "\\u003c")
                    copy_html_small = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <style>
                    .copy-btn {{
                        background: #f8fafc;
                        color: #475569;
                        border: 1px solid #cbd5e1;
                        border-radius: 8px;
                        padding: 0.4rem 0.8rem;
                        font-weight: 600;
                        transition: all 0.2s ease;
                        cursor: pointer;
                        font-family: 'Inter', sans-serif;
                        font-size: 0.85rem;
                        display: inline-flex;
                        align-items: center;
                        gap: 6px;
                        margin-top: -10px;
                        margin-bottom: 20px;
                    }}
                    .copy-btn:hover {{
                        background: #f1f5f9;
                        color: #1e293b;
                        border-color: #94a3b8;
                    }}
                    </style>
                    </head>
                    <body style="margin: 0; padding: 0; text-align: right;">
                        <button class="copy-btn" onclick="copyText()">
                            📋 <span>Copy</span>
                        </button>
                        <script>
                        function copyText() {{
                            const text = {safe_app_content};
                            if (navigator.clipboard && window.isSecureContext) {{
                                navigator.clipboard.writeText(text).then(showSuccess);
                            }} else {{
                                const textArea = document.createElement("textarea");
                                textArea.value = text;
                                textArea.style.position = "absolute";
                                textArea.style.left = "-999999px";
                                document.body.prepend(textArea);
                                textArea.select();
                                try {{
                                    document.execCommand('copy');
                                    showSuccess();
                                }} catch (error) {{
                                    console.error(error);
                                }} finally {{
                                    textArea.remove();
                                }}
                            }}
                        }}
                        function showSuccess() {{
                            const span = document.querySelector('span');
                            const original = span.innerText;
                            span.innerText = 'Copied!';
                            setTimeout(() => span.innerText = original, 2000);
                        }}
                        </script>
                    </body>
                    </html>
                    """
                    components.html(copy_html_small, height=45)


elif app_mode == "Image Creator Agent":
    # Exact endpoint from the Azure AI sample code
    ENDPOINT   = os.getenv("AZURE_IMAGE_ENDPOINT", "https://content-creation-1-resource.services.ai.azure.com/openai/v1")
    DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT", "gpt-image-2.5-sunburst")

    from openai import OpenAI
    
    def get_client():
        api_key = os.getenv("AZURE_API_KEY", "")
        if not api_key:
            st.error(
                "🔑 **API key missing.** Open the `.env` file in the project folder "
                "and fill in `AZURE_API_KEY=\"your-key-here\"`, then restart the app."
            )
            st.stop()
        return OpenAI(base_url=ENDPOINT, api_key=api_key)

    # ── Chat-style layout CSS ──
    st.markdown("""
    <style>
    /* --- Image Agent: ChatGPT / Claude-style layout --- */
    .img-greeting {
        text-align: center;
        padding: 5rem 2rem 3rem;
    }
    .img-greeting .icon {
        width: 68px; height: 68px; border-radius: 22px;
        background: linear-gradient(135deg, #eef2ff, #e0e7ff);
        color: #6366f1; font-size: 30px;
        display: inline-flex; align-items: center; justify-content: center;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 15px rgba(99,102,241,0.15);
    }
    .img-greeting h1 {
        font-family: 'Outfit', sans-serif; font-size: 1.9rem; font-weight: 700;
        color: #1e293b; margin: 0 0 0.5rem;
    }
    .img-greeting p {
        color: #64748b; font-size: 0.95rem; max-width: 480px;
        margin: 0 auto; line-height: 1.6;
    }
    .img-greeting .model-tag {
        display: inline-block; margin-top: 1rem;
        padding: 5px 14px; border-radius: 999px;
        background: #f1f5f9; border: 1px solid #e2e8f0;
        font-size: 0.75rem; font-weight: 600; color: #6366f1;
        letter-spacing: 0.04em;
    }

    /* User prompt bubble (right-aligned) */
    .user-msg {
        background: linear-gradient(135deg, #eff6ff, #e0e7ff);
        border: 1px solid #c7d2fe;
        border-radius: 18px 18px 4px 18px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.25rem;
        max-width: 72%;
        margin-left: auto;
        font-size: 0.92rem; color: #1e3a8a;
        line-height: 1.55;
    }

    /* AI response label */
    .ai-msg-header {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 0.85rem; padding-left: 2px;
    }
    .ai-msg-header .ai-avatar {
        width: 28px; height: 28px; border-radius: 8px;
        background: linear-gradient(135deg, #6366f1, #818cf8);
        color: white; font-size: 14px; font-weight: 700;
        display: flex; align-items: center; justify-content: center;
    }
    .ai-msg-header .ai-name {
        font-size: 0.88rem; font-weight: 700; color: #1e293b;
    }
    .ai-msg-header .gen-time {
        font-size: 0.78rem; color: #94a3b8; font-weight: 400;
        margin-left: auto;
    }

    /* Composer area */
    .composer-divider {
        border: none; border-top: 1px solid rgba(0,0,0,0.06);
        margin: 1.5rem 0 1rem;
    }

    /* Reference image chip */
    .ref-attached {
        display: inline-flex; align-items: center; gap: 6px;
        background: #f0fdf4; border: 1px solid #bbf7d0;
        border-radius: 10px; padding: 5px 12px;
        font-size: 0.78rem; color: #166534; font-weight: 600;
        margin-bottom: 0.5rem;
    }

    /* Suggestion pills */
    .suggestion-pills {
        display: flex; flex-wrap: wrap; gap: 8px;
        justify-content: center; margin-top: 1rem;
    }
    .suggestion-pill {
        background: #ffffff; border: 1px solid #e2e8f0;
        border-radius: 999px; padding: 6px 16px;
        font-size: 0.82rem; color: #475569;
        cursor: pointer; transition: all 0.2s;
        text-decoration: none;
    }
    .suggestion-pill:hover {
        background: #f1f5f9; border-color: #818cf8; color: #4338ca;
    }

    /* File uploader custom style (Paperclip button) */
    [data-testid="stFileUploader"] {
        width: 42px !important;
        height: 42px !important;
        min-height: 42px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
        background-color: transparent !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        min-height: 42px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.2s;
        position: relative !important;
    }
    [data-testid="stFileUploader"] section:hover {
        background-color: #f1f5f9 !important;
        border-color: #94a3b8 !important;
    }
    [data-testid="stFileUploader"] section > * {
        display: none !important;
    }
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
    /* Paperclip icon SVG */
    [data-testid="stFileUploader"] section::before {
        content: '';
        display: block;
        position: absolute;
        top: 10px;
        left: 10px;
        width: 20px;
        height: 20px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13' /%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        z-index: 5;
        pointer-events: none;
    }
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"] {
        position: absolute;
        top: 50px;
        left: 0;
        background: #ffffff;
        color: #334155;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        width: max-content;
        padding: 4px 8px;
        z-index: 100;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Layout containers (display order: output first, then composer) ──
    output_area = st.container()
    st.markdown('<hr class="composer-divider">', unsafe_allow_html=True)
    composer_area = st.container()
    extras_area = st.container()

    # ═══════════════════════════════════════════
    #  COMPOSER (renders at bottom visually)
    # ═══════════════════════════════════════════
    with composer_area:
        prompt = st.text_area(
            label="Prompt",
            placeholder="Describe the image you want to create… e.g. A lone astronaut on Mars at sunset, cinematic lighting, epic scale",
            height=100,
            label_visibility="collapsed",
            key="prompt_input",
        )

        # Action row: upload | spacer | generate
        act_col1, act_col2, act_col3 = st.columns([1.2, 3, 1.2])
        
        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0
            
        with act_col1:
            uploaded_image = st.file_uploader(
                "Reference image",
                type=["png", "jpg", "jpeg"],
                label_visibility="collapsed",
                key=f"img_uploader_{st.session_state.uploader_key}"
            )
        with act_col3:
            generate_clicked = st.button("✦  Generate", type="primary", use_container_width=True)

        # Reference image preview
        if uploaded_image is not None:
            prev_col1, prev_col2 = st.columns([1, 5])
            with prev_col1:
                st.image(uploaded_image, width=80)
            with prev_col2:
                st.markdown(
                    '<div class="ref-attached" style="margin-bottom: 0.3rem;"><span style="color:#22c55e;">●</span> Reference image attached</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    """
                    <style>
                    button[kind="secondary"]:has(div:contains("✖ Remove")) {
                        background-color: #ef4444 !important;
                        color: white !important;
                        border: none !important;
                        padding: 0.2rem 0.6rem !important;
                        font-size: 0.75rem !important;
                        border-radius: 6px !important;
                        min-height: 24px !important;
                        line-height: 1 !important;
                        width: auto !important;
                    }
                    button[kind="secondary"]:has(div:contains("✖ Remove")):hover {
                        background-color: #dc2626 !important;
                        color: white !important;
                    }
                    </style>
                    """, unsafe_allow_html=True
                )
                if st.button("✖ Remove", key="remove_img"):
                    st.session_state.uploader_key += 1
                    st.rerun()

    # ═══════════════════════════════════════════
    #  EXTRAS (inspiration prompts)
    # ═══════════════════════════════════════════
    with extras_area:
        with st.expander("💡 Need inspiration? Try these prompts"):
            inspirations = [
                "A majestic dragon soaring above a medieval city at dawn, fantasy art, dramatic lighting",
                "Portrait of a cyberpunk samurai, neon-lit Tokyo alley, rain, cinematic bokeh",
                "Enchanted forest with glowing mushrooms, fireflies, moonlit mist, magical realism",
                "Abstract ocean waves made of liquid gold and sapphire, high contrast, minimalist",
                "Cozy log cabin in a snowstorm, warm light through frosted windows, oil painting style",
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

    # ═══════════════════════════════════════════
    #  OUTPUT AREA (renders at top visually)
    # ═══════════════════════════════════════════
    with output_area:
        # Handle generation
        if generate_clicked:
            raw_prompt = prompt.strip()
            final_prompt = (raw_prompt + style_modifier).strip() if raw_prompt else ""

            if not final_prompt and uploaded_image is None:
                st.warning("✏️ Please enter a prompt or upload an image before generating.")
            else:
                with st.spinner("✦ Creating your image…  (this may take 15–30 seconds)"):
                    try:
                        client = get_client()
                        t0 = time.time()

                        if uploaded_image is not None:
                            ref_image = Image.open(uploaded_image).convert("RGBA")
                            img_byte_arr = io.BytesIO()
                            ref_image.save(img_byte_arr, format='PNG')
                            img_byte_arr.seek(0)
                            img_byte_arr.name = "image.png"
                            text_prompt = final_prompt if final_prompt else "Create a creative variation of this image, maintaining its core subject and composition."
                            response = client.images.edit(
                                model=DEPLOYMENT,
                                image=img_byte_arr,
                                prompt=text_prompt,
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

                        elapsed = time.time() - t0
                        image_data = response.data[0]
                        if image_data.b64_json:
                            img_bytes = base64.b64decode(image_data.b64_json)
                        elif image_data.url:
                            import urllib.request
                            img_bytes = urllib.request.urlopen(image_data.url).read()
                        else:
                            raise ValueError("No image data returned from the API.")

                        st.session_state.current_image = img_bytes
                        st.session_state.current_prompt = final_prompt
                        st.session_state.generation_time = elapsed
                        st.session_state.history.insert(
                            0,
                            {
                                "prompt": final_prompt,
                                "image_bytes": img_bytes,
                                "size": selected_size,
                                "ts": datetime.now().strftime("%H:%M:%S"),
                            },
                        )
                        st.rerun()

                    except Exception as exc:
                        st.error(f"❌ Generation failed: {exc}")

        # Display generated image or greeting
        if st.session_state.current_image:
            img_bytes = st.session_state.current_image
            displayed_prompt = st.session_state.current_prompt

            # User's prompt as a right-aligned chat bubble
            if displayed_prompt:
                st.markdown(
                    f'<div class="user-msg">{displayed_prompt}</div>',
                    unsafe_allow_html=True,
                )

            # AI response header
            gen_time_str = f" · {st.session_state.generation_time:.1f}s" if st.session_state.generation_time else ""
            st.markdown(
                f"""
                <div class="ai-msg-header">
                    <div class="ai-avatar">✦</div>
                    <span class="ai-name">AI Studio</span>
                    <span class="gen-time">{gen_time_str}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Generated image
            st.image(img_bytes, use_container_width=True)

            # Download button
            filename = f"visionary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            st.download_button(
                label="⬇️  Download PNG",
                data=img_bytes,
                file_name=filename,
                mime="image/png",
            )

        else:
            # Empty state greeting
            st.markdown(
                """
                <div class="img-greeting">
                    <div class="icon">✦</div>
                    <h1>What would you like to create?</h1>
                    <p>Describe your vision — the subject, mood, style, and details. I'll bring it to life in seconds.</p>
                    <div class="model-tag">✦ GPT Image 2.5 Sunburst</div>
                </div>
                """,
                unsafe_allow_html=True,
            )