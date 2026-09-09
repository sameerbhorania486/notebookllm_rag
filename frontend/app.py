import streamlit as st
import requests
from datetime import datetime


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="NotebookLLM",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://127.0.0.1:8000"

ICONS = {
    "Website": "🌐",
    "YouTube": "▶️",
    "PDF": "📄",
    "TXT": "📝",
    "CSV": "📊",
}

NAV_ITEMS = [
    ("workspace", "⌂  Overview", "Overview"),
    ("workspace", "✦  AI Chat", "AI Chat"),
    ("workspace", "▣  Sources", "Sources"),
    ("knowledge", "🌐  Website", "Website"),
    ("knowledge", "▶️  YouTube", "YouTube"),
    ("knowledge", "📄  PDF", "PDF"),
    ("knowledge", "📝  TXT", "TXT"),
    ("knowledge", "📊  CSV", "CSV"),
    ("system", "◴  Analytics", "Analytics"),
    ("system", "⚙️  Settings", "Settings"),
]


# =========================================================
# PREMIUM THEME
# =========================================================

st.markdown("""
<style>

:root {
    --bg: #0A0A0B;
    --surface: #17171A;
    --surface-raised: #212124;
    --border: #3A3A40;
    --border-strong: #55555C;
    --text: #FFFFFF;
    --text-muted: #B4B4BA;
    --accent: #FFFFFF;
    --accent-strong: #D6D6DA;
    --accent-dim: rgba(255, 255, 255, 0.12);
    --accent-ink: #0A0A0B;
}

/* Button text must always inherit the button's own color, not the
   generic paragraph color rule below — this was making primary
   button labels unreadable. */
.stButton > button p,
.stButton > button div,
.stButton > button span {
    color: inherit !important;
}

/* ---------- MAIN ---------- */

.stApp {
    background: var(--bg);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1450px;
}

h1, h2, h3 {
    color: var(--text) !important;
    font-weight: 600;
    letter-spacing: -0.01em;
}

p, label, span {
    color: var(--text-muted);
}

hr {
    border-color: var(--border) !important;
}

/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: #000000;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid transparent;
    border-left: 2px solid transparent;
    color: #9C9CA0;
    text-align: left;
    border-radius: 6px;
    min-height: 46px;
    font-weight: 500;
    font-size: 1.05rem;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small {
    font-size: 0.95rem !important;
    letter-spacing: 0.04em;
}

section[data-testid="stSidebar"] h1 {
    font-size: 1.7rem !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--surface);
    border-left: 2px solid var(--border-strong);
    color: var(--text);
}

section[data-testid="stSidebar"] .stButton > button:disabled {
    background: var(--accent-dim);
    border-left: 2px solid var(--accent);
    color: var(--text) !important;
    opacity: 1;
    font-weight: 600;
}

/* ---------- ALL BUTTONS ---------- */

.stButton > button {
    background: var(--surface-raised);
    border: 1px solid var(--border-strong);
    color: var(--text);
    border-radius: 8px;
    min-height: 42px;
    font-weight: 600;
    transition: 0.15s ease;
}

.stButton > button:hover {
    background: #232326;
    border-color: var(--accent);
    color: var(--text);
}

/* Primary buttons: the one accent moment on each page */
.stButton > button[kind="primary"] {
    background: var(--accent);
    border-color: var(--accent);
    color: var(--accent-ink);
}

.stButton > button[kind="primary"]:hover {
    background: var(--accent-strong);
    border-color: var(--accent-strong);
    color: var(--accent-ink);
}

/* ---------- INPUTS ---------- */

.stTextInput input,
.stTextArea textarea {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 2px solid var(--border-strong) !important;
    border-radius: 8px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}

/* ---------- FILE UPLOADER ---------- */

[data-testid="stFileUploader"] {
    background: var(--surface);
    border: 1px dashed var(--border-strong);
    border-radius: 10px;
}

/* ---------- METRICS ---------- */

[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px;
}

[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
}

[data-testid="stMetricValue"] {
    color: var(--text) !important;
}

/* ---------- CHAT ---------- */

[data-testid="stChatMessage"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
}

/* ---------- INFO / SUCCESS / ERROR ---------- */

div[data-testid="stAlert"] {
    border-radius: 8px;
}

/* ---------- CONTAINERS / CARDS ---------- */

[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
}

/* ---------- TABS ---------- */

.stTabs [data-baseweb="tab"] {
    color: var(--text-muted);
}

.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
}

/* ---------- CHECKBOX / MULTISELECT TAGS ---------- */

[data-baseweb="tag"] {
    background: var(--accent) !important;
    border-radius: 6px !important;
}

[data-baseweb="tag"] span {
    color: var(--accent-ink) !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Overview"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "sources" not in st.session_state:
    st.session_state.sources = []

if "active_source_ids" not in st.session_state:
    st.session_state.active_source_ids = []


# =========================================================
# BACKEND FUNCTIONS  (unchanged API contracts)
# =========================================================

def backend_online():

    try:

        response = requests.get(
            f"{BACKEND_URL}/",
            timeout=3
        )

        return response.status_code == 200

    except Exception:

        return False


def ask_backend(question):

    if not st.session_state.active_source_ids:

        return (
            "Please connect at least one source "
            "before starting a chat."
        )

    try:

        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "question": question,
                "source_ids": st.session_state.active_source_ids
            },
            timeout=180
        )

        if response.status_code == 200:

            data = response.json()

            return data.get("answer", "No answer received.")

        return f"Backend Error: {response.text}"

    except requests.exceptions.ConnectionError:

        return (
            "Backend is not connected. "
            "Please start the FastAPI server first."
        )

    except Exception as e:

        return f"Error: {str(e)}"


def ingest_source(source):

    try:

        return requests.post(
            f"{BACKEND_URL}/ingest",
            json={"documents": [source]},
            timeout=180
        )

    except Exception:

        return None


def upload_file(uploaded_file):

    try:

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        return requests.post(
            f"{BACKEND_URL}/upload",
            files=files,
            timeout=180
        )

    except Exception:

        return None


# =========================================================
# STATE HELPERS  (frontend-only, no API impact)
# =========================================================

def add_active_source(source_id):

    if source_id and source_id not in st.session_state.active_source_ids:

        st.session_state.active_source_ids.append(source_id)


def add_source(name, source_type, source_id):

    st.session_state.sources.append(
        {
            "name": name,
            "type": source_type,
            "source_id": source_id,
            "added": datetime.now().strftime("%d %b %Y, %H:%M")
        }
    )


def source_label(source):

    icon = ICONS.get(source["type"], "📁")

    return f"{icon} {source['type']} · {source['name']}"


def go_to(page_name):

    st.session_state.page = page_name
    st.rerun()


def handle_ingest_result(response, name, source_type):

    if response and response.status_code == 200:

        data = response.json()

        # The backend can return a 200 OK with an "error" key in the
        # body (e.g. no documents could be loaded) instead of an HTTP
        # error status. Treat that as a failure, not a success.
        if data.get("error"):

            st.error(f"{source_type} could not be connected: {data['error']}")

            return

        new_id = data.get("source_id")

        if not new_id:

            st.error(
                f"{source_type} did not return a source_id — "
                "nothing was indexed. Check the backend logs."
            )

            return

        chunks = data.get("chunks")

        add_active_source(new_id)
        add_source(name, source_type, new_id)

        if chunks is not None:
            st.success(f"{source_type} connected successfully — {chunks} chunk(s) indexed.")
        else:
            st.success(f"{source_type} connected successfully.")

        go_to("AI Chat")

    elif response:

        st.error(response.text)

    else:

        st.error("Backend is not connected.")


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:

    st.title("📚 NotebookLLM")
    st.caption("AI Knowledge Workspace")

    st.divider()

    st.caption("WORKSPACE")

    for group, label, target in NAV_ITEMS:

        if group != "workspace":
            continue

        if st.button(
            label,
            use_container_width=True,
            disabled=(st.session_state.page == target),
            key=f"nav_{target}"
        ):
            go_to(target)

    st.divider()

    st.caption("ADD KNOWLEDGE")

    for group, label, target in NAV_ITEMS:

        if group != "knowledge":
            continue

        if st.button(
            label,
            use_container_width=True,
            disabled=(st.session_state.page == target),
            key=f"nav_{target}"
        ):
            go_to(target)

    st.divider()

    st.caption("SYSTEM")

    for group, label, target in NAV_ITEMS:

        if group != "system":
            continue

        if st.button(
            label,
            use_container_width=True,
            disabled=(st.session_state.page == target),
            key=f"nav_{target}"
        ):
            go_to(target)

    st.divider()

    if backend_online():

        st.success("● Backend Online")

    else:

        st.error("○ Backend Offline")

    if st.session_state.sources:

        st.caption(
            f"{len(st.session_state.active_source_ids)} / "
            f"{len(st.session_state.sources)} sources active"
        )


# =========================================================
# OVERVIEW
# =========================================================

if st.session_state.page == "Overview":

    st.title("Welcome to NotebookLLM")

    st.caption(
        "Manage your knowledge workspace and interact with your AI assistant."
    )

    st.divider()

    questions = len([x for x in st.session_state.messages if x["role"] == "user"])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Sources", len(st.session_state.sources))

    with c2:
        st.metric("Active Sources", len(st.session_state.active_source_ids))

    with c3:
        st.metric("Questions", questions)

    with c4:
        st.metric("Engine", "RAG")

    st.write("")
    st.subheader("Add Knowledge")

    cols = st.columns(5)
    quick_links = [
        ("🌐", "Website"),
        ("▶️", "YouTube"),
        ("📄", "PDF"),
        ("📝", "TXT"),
        ("📊", "CSV"),
    ]

    for col, (icon, name) in zip(cols, quick_links):

        with col:

            with st.container(border=True):

                st.markdown(f"### {icon}")
                st.write(name)

                if st.button("Open", key=f"quick_{name}", use_container_width=True):
                    go_to(name)

    st.write("")
    st.subheader("Recent Sources")

    if not st.session_state.sources:

        st.info("No knowledge sources connected yet. Add one above to get started.")

    else:

        recent = list(reversed(st.session_state.sources))[:4]

        for source in recent:

            with st.container(border=True):

                col1, col2, col3 = st.columns([5, 2, 1])

                with col1:
                    st.write(f"**{source_label(source)}**")
                    st.caption(f"Added {source['added']}")

                with col2:
                    if source["source_id"] in st.session_state.active_source_ids:
                        st.success("Active")
                    else:
                        st.warning("Inactive")

                with col3:
                    pass


# =========================================================
# AI CHAT
# =========================================================

elif st.session_state.page == "AI Chat":

    st.title("AI Chat")
    st.caption("Ask questions across your connected knowledge sources.")

    if st.session_state.sources:

        with st.expander(
            f"🔎 Source selection — {len(st.session_state.active_source_ids)} active",
            expanded=not st.session_state.active_source_ids
        ):

            options = {source["source_id"]: source_label(source) for source in st.session_state.sources}

            selected = st.multiselect(
                "Choose which sources this chat should use",
                options=list(options.keys()),
                default=st.session_state.active_source_ids,
                format_func=lambda sid: options.get(sid, sid)
            )

            st.session_state.active_source_ids = selected

    if st.session_state.active_source_ids:

        st.success(
            f"{len(st.session_state.active_source_ids)} source(s) connected to this conversation."
        )

    else:

        st.info(
            "Connect a Website, YouTube video, PDF, TXT or CSV source to start chatting."
        )

    st.divider()

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    prompt = st.chat_input("Ask anything about your connected sources...")

    if prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Searching your knowledge..."):
                answer = ask_backend(prompt)

            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})


# =========================================================
# WEBSITE
# =========================================================

elif st.session_state.page == "Website":

    st.title("🌐 Website")
    st.caption("Connect a website and make its content available to AI.")

    with st.container(border=True):

        url = st.text_input("Website URL", placeholder="https://example.com")

        if st.button("🌐  Connect Website", use_container_width=True, type="primary"):

            website_url = url.strip()

            if not website_url:
                st.warning("Please enter a website URL.")

            elif not (website_url.startswith("http://") or website_url.startswith("https://")):
                st.warning("Please enter a valid URL.")

            else:

                with st.spinner("Loading website..."):
                    response = ingest_source(website_url)

                handle_ingest_result(response, website_url, "Website")


# =========================================================
# YOUTUBE
# =========================================================

elif st.session_state.page == "YouTube":

    st.title("▶️ YouTube")
    st.caption("Connect a YouTube video and add its transcript to NotebookLLM.")

    with st.container(border=True):

        url = st.text_input("YouTube URL", placeholder="https://youtu.be/VIDEO_ID")

        if st.button("▶  Connect YouTube", use_container_width=True, type="primary"):

            youtube_url = url.strip()

            if not youtube_url:
                st.warning("Please enter a YouTube URL.")

            elif not ("youtube.com/" in youtube_url or "youtu.be/" in youtube_url):
                st.warning("Please enter a valid YouTube URL.")

            else:

                with st.spinner("Loading and processing YouTube transcript..."):
                    response = ingest_source(youtube_url)

                handle_ingest_result(response, youtube_url, "YouTube")


# =========================================================
# PDF
# =========================================================

elif st.session_state.page == "PDF":

    st.title("📄 PDF")
    st.caption("Upload a PDF and make its content searchable by AI.")

    with st.container(border=True):

        uploaded_file = st.file_uploader("Choose PDF", type=["pdf"])

        if uploaded_file:

            st.info(f"Selected: {uploaded_file.name}")

            if st.button("⬆  Process PDF", use_container_width=True, type="primary"):

                with st.spinner("Processing PDF..."):
                    response = upload_file(uploaded_file)

                handle_ingest_result(response, uploaded_file.name, "PDF")


# =========================================================
# TXT
# =========================================================

elif st.session_state.page == "TXT":

    st.title("📝 TXT")
    st.caption("Upload a text file and add it to your knowledge workspace.")

    with st.container(border=True):

        uploaded_file = st.file_uploader("Choose TXT", type=["txt"])

        if uploaded_file:

            st.info(f"Selected: {uploaded_file.name}")

            if st.button("⬆  Process TXT", use_container_width=True, type="primary"):

                with st.spinner("Processing text file..."):
                    response = upload_file(uploaded_file)

                handle_ingest_result(response, uploaded_file.name, "TXT")


# =========================================================
# CSV
# =========================================================

elif st.session_state.page == "CSV":

    st.title("📊 CSV")
    st.caption("Upload structured CSV data to your knowledge workspace.")

    with st.container(border=True):

        uploaded_file = st.file_uploader("Choose CSV", type=["csv"])

        if uploaded_file:

            st.info(f"Selected: {uploaded_file.name}")

            if st.button("⬆  Process CSV", use_container_width=True, type="primary"):

                with st.spinner("Processing CSV..."):
                    response = upload_file(uploaded_file)

                handle_ingest_result(response, uploaded_file.name, "CSV")


# =========================================================
# SOURCES
# =========================================================

elif st.session_state.page == "Sources":

    st.title("▣ Sources")
    st.caption("Manage knowledge sources connected to NotebookLLM.")

    st.divider()

    if not st.session_state.sources:

        st.info("No knowledge sources connected yet.")

    else:

        col1, col2, col3 = st.columns([2, 2, 6])

        with col1:

            if st.button("Select all", use_container_width=True):

                st.session_state.active_source_ids = [
                    s["source_id"] for s in st.session_state.sources
                ]
                st.rerun()

        with col2:

            if st.button("Clear selection", use_container_width=True):

                st.session_state.active_source_ids = []
                st.rerun()

        st.write("")

        for source in reversed(st.session_state.sources):

            with st.container(border=True):

                col1, col2, col3 = st.columns([5, 2, 2])

                with col1:

                    st.subheader(f"{ICONS.get(source['type'], '📁')}  {source['name']}")
                    st.caption(f"{source['type']}  ·  Added {source['added']}")

                with col2:

                    is_active = source["source_id"] in st.session_state.active_source_ids

                    toggled = st.checkbox(
                        "Use in chat",
                        value=is_active,
                        key=f"toggle_{source['source_id']}_{source['added']}"
                    )

                    if toggled and not is_active:
                        add_active_source(source["source_id"])

                    elif not toggled and is_active:
                        st.session_state.active_source_ids.remove(source["source_id"])

                with col3:

                    if source["source_id"] in st.session_state.active_source_ids:
                        st.success("Active")
                    else:
                        st.warning("Inactive")


# =========================================================
# ANALYTICS
# =========================================================

elif st.session_state.page == "Analytics":

    st.title("◴ Analytics")
    st.caption("Monitor your current NotebookLLM activity.")

    questions = len([x for x in st.session_state.messages if x["role"] == "user"])
    answers = len([x for x in st.session_state.messages if x["role"] == "assistant"])

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Connected Sources", len(st.session_state.sources))

    with c2:
        st.metric("Questions", questions)

    with c3:
        st.metric("AI Answers", answers)

    st.write("")

    if st.session_state.sources:

        st.subheader("Sources by Type")

        counts = {}

        for source in st.session_state.sources:

            counts[source["type"]] = counts.get(source["type"], 0) + 1

        st.bar_chart(counts)

    else:

        st.info("Connect sources to see analytics.")


# =========================================================
# SETTINGS
# =========================================================

elif st.session_state.page == "Settings":

    st.title("⚙️ Settings")
    st.caption("Manage your NotebookLLM workspace preferences.")

    st.divider()

    with st.container(border=True):

        st.subheader("Workspace")

        st.write("Your connected knowledge sources are used during AI conversations.")

        st.info(f"{len(st.session_state.sources)} source(s) connected.")

        st.caption(f"Backend URL: {BACKEND_URL}")

    st.write("")

    with st.container(border=True):

        st.subheader("Conversation")

        st.write("Manage your current AI conversation history.")

        if st.button("🗑️  Clear Chat History", use_container_width=True):

            st.session_state.messages = []
            st.success("Chat history cleared successfully.")
            st.rerun()

    st.write("")

    with st.container(border=True):

        st.subheader("System")

        st.write(
            "NotebookLLM uses Retrieval Augmented Generation (RAG) "
            "to answer questions from connected knowledge sources."
        )

        if backend_online():
            st.success("Backend connection is healthy.")
        else:
            st.error("Backend is currently offline.")