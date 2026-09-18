import os
from datetime import datetime
import streamlit as st

from content_agent import ContentAgent
from models import ContentRequest, ContentSession

# ─────────────────────────────────────────────
#  Page configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Content Studio · AI Writer",
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

    /* App header */
    .app-header {
        padding: 1.5rem 1rem 1.5rem;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    .app-header h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 40%, #3b82f6 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.2rem;
    }
    .app-header p {
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

    /* Generate button */
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
                   
    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
#  State initialization
# ─────────────────────────────────────────────
@st.cache_resource
def get_agent():
    return ContentAgent()

agent = get_agent()

if "view" not in st.session_state:
    st.session_state.view = "write"

if "drafts" not in st.session_state:
    st.session_state.drafts = []

if "approved" not in st.session_state:
    st.session_state.approved = []

if "session" not in st.session_state:
    st.session_state.session = None

if "revision_input" not in st.session_state:
    st.session_state.revision_input = ""

def set_view(view_name):
    st.session_state.view = view_name
    
def new_content():
    st.session_state.session = None
    st.session_state.view = "write"

def save_draft():
    s = st.session_state.session
    if s and s.current_content:
        # Check if already in drafts, if so replace, else append
        draft_item = {
            "session_id": id(s), 
            "title": s.options[0].title if s.options else "Draft",
            "content": s.current_content,
            "platform": s.request.platform,
            "date": datetime.now().strftime("%I:%M %p")
        }
        for i, d in enumerate(st.session_state.drafts):
            if d["session_id"] == draft_item["session_id"]:
                st.session_state.drafts[i] = draft_item
                return
        st.session_state.drafts.append(draft_item)

# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="padding:1.2rem 0 2rem;">
            <div style="font-size:2rem; margin-bottom:0.4rem; color:#818cf8; font-weight:800;
                        background:linear-gradient(135deg,#7778ff,#4c4dd1); border-radius:12px;
                        width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; color: white;">C</div>
            <div style="font-family:'Outfit',sans-serif; font-size:1.1rem; font-weight:700; color: white; margin-top: 10px;">
                Content Studio
            </div>
            <div style="font-size:0.75rem; color:#94a3b8; margin-top:0.2rem;">AI Content Creation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Navigation
    if st.button("✦ Write Content", key="nav_write", use_container_width=True):
        set_view("write")
    if st.button(f"◫ My Drafts ({len(st.session_state.drafts)})", key="nav_drafts", use_container_width=True):
        set_view("drafts")
    if st.button(f"✓ Approved ({len(st.session_state.approved)})", key="nav_approved", use_container_width=True):
        set_view("approved")

    # Add style to make these buttons look like the sidebar navigation
    st.markdown(
        """<script>
        const buttons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
        buttons.forEach(b => b.classList.add('nav-btn'));
        </script>""", unsafe_allow_html=True
    )
    
    st.divider()
    st.markdown(
        """<div style="position: absolute; bottom: 20px; color:#98a2b3; font-size:12px;">Powered by Azure AI Foundry · GPT-4.1</div>""",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
#  Views
# ─────────────────────────────────────────────
view = st.session_state.view

if view == "write":
    # --- WRITE CONTENT VIEW ---
    session: ContentSession = st.session_state.session
    current_state = session.state if session else "NEW_REQUEST"
    
    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <p style="color: #667085; font-size: 13px; font-weight: 500; margin-bottom: 8px;">Content Studio / <b>Write Content</b></p>
                <h1>Create high-quality content</h1>
                <p>Describe what you need. The AI will generate three distinct directions for you to choose from.</p>
            </div>
            <div class="state-pill">{current_state.replace("_", " ")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    left_col, right_col = st.columns([1, 1.5], gap="large")
    
    with left_col:
        with st.container():
            st.markdown(
                """
                <div style="background: white; padding: 24px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.08); box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
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
                        req = ContentRequest(topic=topic, platform=platform, audience=audience, mood=mood, length=length, goal=goal)
                        st.session_state.session = agent.generate_options(req)
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

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
            st.markdown(
                f"""
                <div style="background: white; padding: 24px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.08); box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div>
                            <h2 style="margin:0; font-size: 1.1rem; color: #1e293b;">Selected content</h2>
                            <div style="color: #667085; font-size: 12px; margin-top: 4px;">Option {session.selected_option} · {session.revision_count} revisions</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True
            )
            
            # Editor
            disabled = session.approved
            edited_content = st.text_area("Content", value=session.current_content, height=300, disabled=disabled, label_visibility="collapsed")
            
            # Update session content if manually edited
            if edited_content != session.current_content and not disabled:
                session.current_content = edited_content
                save_draft()
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                pass # Placeholder for copy button (streamlit copy is tricky natively, skipping for now)
            with col_b:
                if not session.approved:
                    if st.button("✓ Approve content", type="primary", use_container_width=True):
                        st.session_state.session = agent.approve(session)
                        # Save to approved, remove from drafts
                        app_item = {
                            "session_id": id(session), 
                            "title": session.options[0].title if session.options else "Approved",
                            "content": session.current_content,
                            "platform": session.request.platform,
                            "date": datetime.now().strftime("%I:%M %p")
                        }
                        st.session_state.approved.insert(0, app_item)
                        
                        # Remove from drafts
                        st.session_state.drafts = [d for d in st.session_state.drafts if d["session_id"] != app_item["session_id"]]
                        
                        st.rerun()
                else:
                    st.success("✓ Content Approved and ready to use.")
            
            if not session.approved:
                st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
                rev_req = st.text_area("What would you like to change?", placeholder="e.g. Make the opening stronger.", height=80)
                if st.button("Revise"):
                    if rev_req:
                        with st.spinner("Revising..."):
                            st.session_state.session = agent.revise(session, rev_req)
                            save_draft()
                            st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)


elif view == "drafts":
    st.markdown(
        """
        <div class="app-header">
            <div>
                <h1>My Drafts</h1>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    
    if not st.session_state.drafts:
        st.info("No drafts yet. Generate some content first!")
    else:
        for d in st.session_state.drafts:
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.08); margin-bottom: 16px;">
                        <div style="display:flex; justify-content: space-between;">
                            <h3 style="margin: 0 0 5px; font-size: 1.1rem; color: #1e293b;">{d['title']}</h3>
                            <span class="state-pill" style="font-size: 0.7rem;">DRAFT</span>
                        </div>
                        <div style="color: #667085; font-size: 0.85rem; margin-bottom: 12px;">{d['platform']} · Last updated {d['date']}</div>
                        <div style="color: #344054; font-size: 0.95rem; line-height: 1.6; max-height: 100px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                            {d['content']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )

elif view == "approved":
    st.markdown(
        """
        <div class="app-header">
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
                            <span class="state-pill" style="font-size: 0.7rem; background: #ecfdf3; color: #027a48; border-color: #a6f4c5;">APPROVED</span>
                        </div>
                        <div style="color: #667085; font-size: 0.85rem; margin-bottom: 12px;">{a['platform']} · Approved at {a['date']}</div>
                        <div style="color: #344054; font-size: 0.95rem; line-height: 1.6;">
                            {a['content']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
