import streamlit as st
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Streamlit LLM Trace Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check CLI engine connection health
try:
    health = requests.get(f"{API_URL}/history", timeout=1)
    engine_online = health.status_code == 200
except Exception:
    engine_online = False

# Custom Styling: Streamlit Architecture Studio look & feel
st.markdown("""
<style>
    :root {
        --streamlit-red: #FF4B4B;
        --dark-bg: #0E1117;
        --dark-card: #161920;
        --dark-accent: #262730;
    }
    .stApp {
        background-color: #0E1117;
        color: #F1F5F9;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #31333F; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #FF4B4B; }

    /* Header banner */
    .studio-header {
        background-color: #161920;
        border: 1px solid #1E2128;
        border-radius: 14px;
        padding: 14px 20px;
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.35);
    }
    .studio-header-icon {
        background: linear-gradient(135deg, #FF4B4B, #d63636);
        color: #fff;
        border-radius: 12px;
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        box-shadow: 0 4px 14px rgba(255,75,75,0.25);
        flex-shrink: 0;
    }
    .studio-header h1 {
        color: #F1F5F9;
        font-size: 17px;
        font-weight: 700;
        letter-spacing: 0.4px;
        margin: 0;
    }
    .studio-header p {
        color: #9CA3AF;
        font-size: 12px;
        margin: 2px 0 0 0;
    }
    .studio-header code {
        color: #FBBF24;
        font-family: 'Fira Code', Monaco, Consolas, monospace;
        background: #0E1117;
        padding: 1px 5px;
        border-radius: 4px;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: #0E1117;
        border: 1px solid #262730;
        color: #9CA3AF;
        font-size: 11px;
        padding: 5px 12px;
        border-radius: 999px;
        white-space: nowrap;
    }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
    .status-dot.online { background: #10B981; box-shadow: 0 0 8px rgba(16,185,129,0.7); animation: pulse-dot 1.8s infinite; }
    .status-dot.offline { background: #EF4444; box-shadow: 0 0 8px rgba(239,68,68,0.7); }
    @keyframes pulse-dot { 0%,100% { opacity: 1; } 50% { opacity: 0.45; } }

    /* Metric cards */
    .metric-card {
        background-color: #161920;
        border: 1px solid #262730;
        border-radius: 12px;
        padding: 14px 10px;
        text-align: center;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: #FF4B4B; }
    .metric-value {
        font-size: 20px;
        font-weight: 700;
        color: #FF4B4B;
        font-family: 'Fira Code', Monaco, Consolas, monospace;
    }
    .metric-label {
        font-size: 10px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }

    /* Sidebar */
    div[data-testid="stSidebar"] {
        background-color: #161920;
        border-right: 1px solid #262730;
    }
    div[data-testid="stSidebar"] label { color: #D1D5DB !important; font-size: 12px !important; }
    div[data-testid="stSidebar"] .stMarkdown h3,
    div[data-testid="stSidebar"] .stMarkdown h2 { color: #F1F5F9; }

    /* Section headers like panel titles in the studio UI */
    .panel-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(22,25,32,0.85);
        border: 1px solid #1E2128;
        border-radius: 10px;
        padding: 8px 14px;
        margin-bottom: 8px;
    }
    .panel-title span.label {
        color: #9CA3AF;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    .panel-title span.badge {
        color: #6B7280;
        font-size: 10px;
        font-family: 'Fira Code', Monaco, Consolas, monospace;
        background: #262730;
        border: 1px solid #374151;
        padding: 2px 8px;
        border-radius: 6px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: #161920;
        border: 1px solid #262730;
        border-radius: 8px;
        color: #9CA3AF;
        font-size: 12px;
        padding: 6px 14px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255,75,75,0.12) !important;
        border-color: rgba(255,75,75,0.4) !important;
        color: #FF8A8A !important;
    }

    /* Buttons */
    .stButton > button {
        background: #262730;
        color: #D1D5DB;
        border: 1px solid #374151;
        border-radius: 8px;
        font-size: 12px;
        transition: all 0.15s;
    }
    .stButton > button:hover {
        background: #FF4B4B;
        color: #fff;
        border-color: #FF4B4B;
    }
    .stButton > button[kind="primary"],
    div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #FF4B4B;
        color: #fff;
        border: none;
    }
    .stButton > button[kind="primary"]:hover { background: #dc2626; }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        background: #161920;
        border: 1px solid #262730;
        border-radius: 12px;
    }
    [data-testid="stChatInput"] {
        background: #161920;
        border: 1px solid #262730;
        border-radius: 10px;
    }

    /* JSON / code blocks */
    [data-testid="stJson"],
    [data-testid="stCode"] {
        background: #0E1117 !important;
        border: 1px solid #262730;
        border-radius: 8px;
    }

    /* Selectbox / inputs */
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stTextInput"] > div > div > input,
    div[data-baseweb="select"] > div {
        background-color: #0E1117;
        border: 1px solid #262730;
        border-radius: 8px;
    }
    textarea[data-testid="stTextArea"] {
        background-color: #0E1117;
        border: 1px solid #262730;
        border-radius: 8px;
        color: #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# Studio header (matches HTML top navigation bar)
st.markdown("""
<div class="studio-header">
    <div class="studio-header-icon">⚡</div>
    <div style="flex:1">
        <h1>Streamlit LLM Trace Studio</h1>
        <p>Decoupled <code>chatbot.py</code> engine &amp; <code>app.py</code> Streamlit trace viewer</p>
    </div>
    <span class="status-pill">
        <span class="status-dot %s"></span>
        %s
    </span>
</div>
""" % ("online" if engine_online else "offline",
        "Decoupled Execution Mode Active" if engine_online else "Engine Offline"),
    unsafe_allow_html=True)

# Sidebar Config Controls
st.sidebar.title("⚡ Trace Studio")
st.sidebar.caption("Connected Engine via local API/IPC")

if engine_online:
    st.sidebar.success("🟢 Engine Connected (Port 8000)")
else:
    st.sidebar.error("🔴 Engine Offline")
    st.sidebar.info("Run in terminal:\n`uv run python chatbot.py --server`")

st.sidebar.subheader("Engine Parameters")
system_prompt = st.sidebar.text_area(
    "System Prompt",
    value="You are an AI developer assistant specializing in LLM observability and system architectures.",
    height=140
)

use_history = st.sidebar.checkbox("Include Chat History Context", value=True)

if st.sidebar.button("🧹 Clear Remote Session History", use_container_width=True):
    if engine_online:
        requests.post(f"{API_URL}/reset")
        st.sidebar.success("History reset!")
        st.rerun()

# Main Layout split
col_chat, col_traces = st.columns([1, 1.2], gap="medium")

# ------------------------------------------------------------------
# Column 1: Chat Streamlit Interface
# ------------------------------------------------------------------
with col_chat:
    st.markdown("""
    <div class="panel-title">
        <span class="label">💬 Chat Interface</span>
        <span class="badge">UI Layer</span>
    </div>
    """, unsafe_allow_html=True)
    
    if engine_online:
        history = requests.get(f"{API_URL}/history").json()
        chat_box = st.container(height=480)
        
        with chat_box:
            if not history:
                st.caption("No message history yet. Type a query below to execute.")
            for msg in history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
    else:
        st.warning("Waiting for engine connection...")

# ------------------------------------------------------------------
# Column 2: Live Execution Trace Inspector
# ------------------------------------------------------------------
with col_traces:
    st.markdown("""
    <div class="panel-title">
        <span class="label">🔍 Execution Trace Inspector</span>
        <span class="badge">from chatbot.py engine</span>
    </div>
    """, unsafe_allow_html=True)

    if engine_online:
        traces = requests.get(f"{API_URL}/traces").json()
        
        if not traces:
            st.info("No execution traces recorded yet. Start chatting to inspect payload runs.")
        else:
            traces_sorted = sorted(traces, key=lambda x: x["timestamp"], reverse=True)
            latest = traces_sorted[0]

            # Metric Cards Display
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f'<div class="metric-card"><div class="metric-value">{latest["latency_ms"]} ms</div><div class="metric-label">Latency</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="metric-card"><div class="metric-value">{latest["prompt_tokens"]}</div><div class="metric-label">Prompt Tokens</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="metric-card"><div class="metric-value">{latest["completion_tokens"]}</div><div class="metric-label">Completion</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div class="metric-card"><div class="metric-value">{latest["total_tokens"]}</div><div class="metric-label">Total Tokens</div></div>', unsafe_allow_html=True)

            st.write("")

            # Select trace run
            trace_map = {
                f"[{datetime.fromtimestamp(t['timestamp']).strftime('%H:%M:%S')}] {t['trace_id']} - '{t['user_prompt'][:20]}...'": t
                for t in traces_sorted
            }
            selected_key = st.selectbox("Select Execution Trace", list(trace_map.keys()))
            sel_trace = trace_map[selected_key]

            # Detail Tabs
            t_payload, t_history, t_raw = st.tabs(["📌 Sent Payload", "📜 History State", "⚙️ Raw Trace JSON"])

            with t_payload:
                st.caption(f"Trace ID: `{sel_trace['trace_id']}`")
                st.markdown("**System Prompt Applied:**")
                st.code(sel_trace["system_prompt"], language="text")
                st.markdown("**Full JSON Payload Sent to Model:**")
                st.json(sel_trace["full_prompt_payload"])

            with t_history:
                st.markdown(f"**History Included:** `{sel_trace['use_history']}`")
                st.markdown("**History Context State at Invocation Time:**")
                st.json(sel_trace["history_snapshot"])

            with t_raw:
                st.json(sel_trace)

# ------------------------------------------------------------------
# Global Chat Input (Must be at the root level outside columns)
# ------------------------------------------------------------------
if engine_online:
    user_input = st.chat_input("Send prompt to engine...")
    if user_input:
        payload = {
            "user_prompt": user_input,
            "system_prompt": system_prompt,
            "use_history": use_history
        }
        requests.post(f"{API_URL}/chat", json=payload)
        st.rerun()
