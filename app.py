import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.campus_agent import CampusBuddyAgent
from tools.timetable_tool import load_timetable, lookup_timetable
from tools.calculator_tool import safe_calculate, calculate_attendance
from tools.search_tool import load_campus_info, campus_search

st.set_page_config(
    page_title="Campus Buddy | AI Student Copilot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 🎨 TEMPLATE: "STUDIO CLEAN" (Vercel / Linear Minimalist Slate & Electric Cyan)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Core Background & Palette */
    .stApp {
        background: #090D16;
        color: #E2E8F0;
    }

    /* Top Studio Header */
    .hero-banner {
        background: linear-gradient(180deg, rgba(20, 27, 45, 0.9) 0%, rgba(13, 18, 30, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    }
    .hero-title {
        font-size: 1.7rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.03em;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 0.9rem;
        margin-top: 4px;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    /* Stat Cards */
    .stat-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: border-color 0.2s ease;
    }
    .stat-card:hover {
        border-color: rgba(99, 102, 241, 0.35);
    }
    .stat-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B;
        font-weight: 600;
    }
    .stat-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 4px;
    }

    /* Modern Chat Elements */
    .user-bubble {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px 14px 2px 14px;
        padding: 12px 16px;
        margin: 6px 0 12px auto;
        max-width: 85%;
        color: #F1F5F9;
        font-size: 0.95rem;
    }
    .agent-bubble {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 14px 14px 14px 2px;
        padding: 14px 18px;
        margin: 6px auto 12px 0;
        max-width: 90%;
        color: #E2E8F0;
        font-size: 0.95rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }
    .agent-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #818CF8;
        margin-bottom: 8px;
    }

    /* Tool Call Execution Card */
    .tool-receipt {
        background: #0D131F;
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 8px;
        padding: 8px 12px;
        margin: 8px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #94A3B8;
    }
    .tool-tag {
        color: #38BDF8;
        font-weight: 600;
    }

    /* Quick Action Buttons */
    .stButton>button {
        background: #131A29 !important;
        color: #CBD5E1 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.84rem !important;
        transition: all 0.15s ease !important;
    }
    .stButton>button:hover {
        background: #1E293B !important;
        border-color: #6366F1 !important;
        color: #FFFFFF !important;
    }

    /* Tab Customization */
    .stTabs [data-baseweb="tab-list"] {
        background: #0F172A;
        border-radius: 10px;
        padding: 4px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 6px 16px;
        color: #94A3B8;
        font-size: 0.88rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #2563EB !important;
        color: #FFFFFF !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #0B0F19;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session
if "agent" not in st.session_state:
    st.session_state.agent = CampusBuddyAgent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! 👋 I'm **Campus Buddy**, your college assistant. Ask me about your class schedule, room locations, attendance calculations, or campus facilities.",
            "trace": None
        }
    ]

# ==============================================================================
# 🏛️ HEADER
# ==============================================================================
st.markdown(f"""
<div class="hero-banner">
    <div>
        <div class="hero-title">
            <span>🎓</span> Campus Buddy
        </div>
        <div class="hero-subtitle">AgentForge Autonomous Copilot • Timetable, Safe Math & Campus Search</div>
    </div>
    <div style="text-align: right;">
        <span class="status-pill">● System Online</span>
        <div style="font-size: 0.8rem; color: #64748B; margin-top: 4px;">{datetime.now().strftime("%A, %B %d")}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 🎛️ SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚡ Prompt Shortcuts")
    shortcuts = [
        ("📅 Today's Classes", "What classes do I have today?"),
        ("📍 CS101 Location", "Where and when is CS101?"),
        ("📊 75% Attendance Check", "I attended 23 out of 30 classes. What is my attendance?"),
        ("📚 Library Closing Time", "When does the library close?"),
        ("📶 Wi-Fi Login Info", "How do I connect to campus Wi-Fi?"),
        ("🔢 Solve Equation", "Calculate 25 * 4.5 + sqrt(144)"),
    ]

    for label, q in shortcuts:
        if st.button(label, key=f"side_{label}", use_container_width=True):
            st.session_state.active_prompt = q

    st.markdown("---")
    st.markdown("### 🛠️ Agent Tools")
    st.markdown("""
    - `college_timetable_lookup`  
    - `calculator` (safe AST + attendance)  
    - `campus_search`  
    """)

    st.markdown("---")
    if st.button("🔄 Clear History", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "History cleared. What would you like to ask?",
                "trace": None
            }
        ]
        st.rerun()

# ==============================================================================
# 📑 MAIN TABS
# ==============================================================================
tab_assistant, tab_schedule, tab_calc, tab_info = st.tabs([
    "💬 Assistant",
    "📅 Timetable",
    "🧮 Attendance & Math",
    "📍 Campus Directory"
])

# ----------------- TAB 1: ASSISTANT CHAT -----------------
with tab_assistant:
    col_convo, col_stats = st.columns([2.2, 1], gap="medium")

    with col_convo:
        # Chat Messages
        chat_box = st.container()
        with chat_box:
            for m in st.session_state.messages:
                if m["role"] == "user":
                    st.markdown(f"""
                    <div class="user-bubble">
                        {m['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="agent-bubble">
                        <div class="agent-header">
                            <span>⚡ Campus Buddy</span>
                        </div>
                        <div>{m['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if m.get("trace") and m["trace"].tool_needed:
                        tr = m["trace"]
                        st.markdown(f"""
                        <div class="tool-receipt">
                            <span class="tool-tag">TOOL DISPATCHED:</span> {tr.tool_name} &nbsp;|&nbsp; 
                            <span class="tool-tag">STATUS:</span> Verified & Applied
                        </div>
                        """, unsafe_allow_html=True)
                        with st.expander("Show Reasoning Trace", expanded=False):
                            st.caption(f"Goal: {tr.goal}")
                            st.json(tr.tool_input)
                            st.json(tr.observation)

        # Input
        user_input = st.chat_input("Type your question (e.g. classes today, attendance calculation, library hours)...")
        chosen_prompt = user_input or st.session_state.pop("active_prompt", None)

        if chosen_prompt:
            st.session_state.messages.append({"role": "user", "content": chosen_prompt, "trace": None})
            with st.spinner("Processing ReAct Loop..."):
                res = st.session_state.agent.run(chosen_prompt)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": res["answer"],
                    "trace": res["trace"]
                })
            st.rerun()

    # Right Stats & Summary Sidebar
    with col_stats:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Semester Status</div>
            <div class="stat-value">Fall 2026</div>
            <div style="font-size:0.8rem; color:#64748B; margin-top:2px;">Week 11 of 16</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-label">Attendance Policy</div>
            <div class="stat-value" style="color:#10B981;">75% Minimum</div>
            <div style="font-size:0.8rem; color:#94A3B8; margin-top:2px;">Required for final examination eligibility</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-label">Emergency Lines</div>
            <div style="font-size:0.85rem; color:#CBD5E1; margin-top:4px; line-height:1.6;">
                🏥 <b>Clinic:</b> Ext. 911<br>
                👮 <b>Security:</b> +1-800-CAMPUS<br>
                💻 <b>IT Desk:</b> Block A Room 104
            </div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- TAB 2: TIMETABLE -----------------
with tab_schedule:
    st.subheader("Class Schedule & Room Locations")
    
    entries = load_timetable()
    if entries:
        df = pd.DataFrame(entries)
        
        c_day, c_search = st.columns([1, 2])
        with c_day:
            day_opt = st.selectbox("Day of Week", ["All"] + sorted(list(set(df["day"]))))
        with c_search:
            search_term = st.text_input("Search Course or Instructor")
            
        filt_df = df.copy()
        if day_opt != "All":
            filt_df = filt_df[filt_df["day"] == day_opt]
        if search_term:
            term = search_term.lower()
            filt_df = filt_df[
                filt_df["course_code"].str.lower().str.contains(term) |
                filt_df["course_name"].str.lower().str.contains(term) |
                filt_df["instructor"].str.lower().str.contains(term) |
                filt_df["room"].str.lower().str.contains(term)
            ]
            
        st.dataframe(
            filt_df[["day", "start_time", "end_time", "course_code", "course_name", "room", "building", "instructor", "credits"]],
            use_container_width=True,
            hide_index=True
        )

# ----------------- TAB 3: ATTENDANCE & MATH LAB -----------------
with tab_calc:
    st.subheader("Attendance & Safe Bunk Calculator")
    
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("**Check 75% Rule Compliance**")
        att = st.number_input("Classes Attended", min_value=0, value=22, step=1)
        tot = st.number_input("Total Classes Held", min_value=1, value=30, step=1)
        target = st.slider("Target Percentage", 50.0, 100.0, 75.0, 5.0)
        
        if st.button("Calculate Attendance Status", type="primary"):
            res = calculate_attendance(int(att), int(tot), target)
            if res["success"]:
                st.info(res["summary"])
            else:
                st.error(res["error"])
                
    with c2:
        st.markdown("**Fast Math & Expression Evaluator**")
        expr = st.text_input("Enter math expression", value="15% * 850 + sqrt(144)")
        if st.button("Evaluate Expression"):
            m = safe_calculate(expr)
            if m["success"]:
                st.success(f"Result: **{m['result']}**")
            else:
                st.error(m["error"])

# ----------------- TAB 4: CAMPUS DIRECTORY -----------------
with tab_info:
    st.subheader("Campus Services Directory")
    
    q_dir = st.text_input("Search campus directory (e.g. library, food, shuttle, doctor)")
    if q_dir:
        s_res = campus_search(q_dir)
        if s_res["success"] and s_res["results"]:
            for item in s_res["results"]:
                st.markdown(f"### {item['title']} `({item['category']})`")
                st.markdown(item["content"])
                st.divider()
        else:
            st.info("No matching records found.")
    else:
        info_items = load_campus_info()
        for doc in info_items:
            with st.expander(f"📌 {doc['title']} — {doc['category']}"):
                st.write(doc["content"])
