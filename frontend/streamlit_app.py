"""
streamlit_app.py — ChatGPT-style Healthcare AI Assistant Frontend.

Run with:  streamlit run frontend/streamlit_app.py
"""

import streamlit as st
import requests
import time

# ── Configuration ───────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Root overrides */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
    }
    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }

    /* Chat input styling */
    .stChatInput > div {
        border-color: #0D9488 !important;
    }
    .stChatInput input:focus {
        border-color: #14B8A6 !important;
        box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 16px;
        padding: 16px;
        backdrop-filter: blur(12px);
    }
    [data-testid="stMetric"]:hover {
        border-color: #0D9488;
    }

    /* Source citations */
    .source-badge {
        display: inline-block;
        background: rgba(13, 148, 136, 0.15);
        color: #14B8A6;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        margin: 2px 4px 2px 0;
    }

    /* Disclaimer box */
    .disclaimer-box {
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 13px;
        color: #94A3B8;
        margin-bottom: 16px;
    }

    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #0D9488 0%, #6366F1 100%);
        border-radius: 16px;
        padding: 40px;
        margin-bottom: 24px;
        color: white;
        position: relative;
        overflow: hidden;
    }
    .hero-section h1 {
        font-size: 36px;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .hero-section p {
        font-size: 16px;
        opacity: 0.9;
    }

    /* Feature cards */
    .feature-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
    }

    /* Success card */
    .success-card {
        background: rgba(16, 185, 129, 0.08);
        border: 2px solid #10B981;
        border-radius: 16px;
        padding: 32px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ── API Client ──────────────────────────────────────────────────────────────
def api_request(method, path, json_data=None):
    """Make a request to the FastAPI backend."""
    try:
        url = f"{API_BASE}{path}"
        if method == "GET":
            resp = requests.get(url, timeout=120)
        else:
            resp = requests.post(url, json=json_data, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        return {"error": "Cannot connect to backend. Is the FastAPI server running on port 8000?"}
    except requests.Timeout:
        return {"error": "Request timed out. The server may be processing a large request."}
    except Exception as e:
        return {"error": str(e)}


# ── Session State Init ──────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏥 HealthCare AI")
    st.markdown("<small style='color:#64748B !important;'>Intelligent Assistant</small>",
                unsafe_allow_html=True)
    st.divider()

    pages = [
        "🏠 Home",
        "💬 AI Healthcare Chatbot",
        "📅 Book Appointment",
        "📋 Appointment History",
        "📊 Admin Dashboard",
        #"ℹ️ About System",
    ]

    for page in pages:
        if st.button(page, key=f"nav_{page}", use_container_width=True,
                     type="primary" if st.session_state.current_page == page else "secondary"):
            st.session_state.current_page = page
            st.rerun()

    st.divider()
    st.markdown("<small style='color:#475569 !important;'>Built by Lokesh Kumawat</small>",
                unsafe_allow_html=True)
    st.markdown("<small style='color:#475569 !important;'>Powered by Ollama Mistral</small>",
                unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.current_page == "🏠 Home":

    st.markdown("""
    <div class="hero-section">
        <h1>🏥 Healthcare AI Assistant</h1>
        <p>Your intelligent healthcare companion powered by RAG, ChromaDB, and Ollama Mistral</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 💬 AI Chatbot")
        st.markdown("Ask medical questions and get evidence-based answers from our knowledge base.")
        if st.button("Start Chatting →", key="go_chat", use_container_width=True):
            st.session_state.current_page = "💬 AI Healthcare Chatbot"
            st.rerun()

    with col2:
        st.markdown("### 📅 Book Appointment")
        st.markdown("Schedule appointments with specialists based on your symptoms.")
        if st.button("Book Now →", key="go_apt", use_container_width=True):
            st.session_state.current_page = "📅 Book Appointment"
            st.rerun()

    with col3:
        st.markdown("### 📊 Dashboard")
        st.markdown("View appointment statistics, specialization trends, and recent bookings.")
        if st.button("View Dashboard →", key="go_dash", use_container_width=True):
            st.session_state.current_page = "📊 Admin Dashboard"
            st.rerun()

    st.divider()

    # Quick Start
    st.markdown("### ⚡ Quick Start")
    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🔄 Ingest Medical Documents", use_container_width=True, key="ingest_btn"):
            with st.spinner("Converting XML files and building vector store... This may take a few minutes."):
                result = api_request("POST", "/ingest")
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.success(f"✅ {result.get('message', 'Ingestion complete!')}")

    with col_b:
        if st.button("🩺 Check System Health", use_container_width=True, key="health_btn"):
            result = api_request("GET", "/health")
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.success(f"✅ System healthy — LLM: {result.get('llm_model', 'N/A')}")

    st.divider()
    st.markdown("""
    <div class="disclaimer-box">
        ⚕️ <strong>Disclaimer:</strong> This assistant is for informational and appointment-support
        purposes only and not a replacement for professional medical advice. Always consult a
        qualified healthcare provider for medical decisions.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: CHATBOT (ChatGPT-style)
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "💬 AI Healthcare Chatbot":

    # Header
    col_h1, col_h2 = st.columns([6, 1])
    with col_h1:
        st.markdown("## 💬 AI Healthcare Chatbot")
    with col_h2:
        if st.button("🗑️ Clear", key="clear_chat", use_container_width=True):
            st.session_state.messages = []
            api_request("POST", "/reset")
            st.rerun()

    st.markdown("""
    <div class="disclaimer-box">
        ⚕️ This assistant answers from a medical knowledge base only. It does not provide
        diagnoses or prescriptions. Type naturally — ask health questions or say
        "book an appointment".
    </div>
    """, unsafe_allow_html=True)

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🏥"):
            st.markdown(msg["content"])
            if msg.get("sources"):
                sources_html = " ".join(
                    f'<span class="source-badge">📄 {s}</span>' for s in msg["sources"]
                )
                st.markdown(f"**Sources:** {sources_html}", unsafe_allow_html=True)

    # Welcome message if empty
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🏥"):
            st.markdown(
                "Hello! I'm your Healthcare AI Assistant. 👋\n\n"
                "I can help you with:\n"
                "- **Medical questions** — Ask about diseases, symptoms, treatments\n"
                "- **Appointment booking** — Say \"book an appointment\" or describe your symptoms\n\n"
                "How can I assist you today?"
            )

    # Chat input
    if user_input := st.chat_input("Ask a healthcare question or book an appointment…"):

        # Show user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Get AI response
        with st.chat_message("assistant", avatar="🏥"):
            with st.spinner("Thinking..."):
                result = api_request("POST", "/ask", {"question": user_input})

            if "error" in result:
                response_text = f"⚠️ {result['error']}"
                sources = []
            else:
                response_text = result.get("answer", "I couldn't generate a response.")
                sources = result.get("sources", [])

            st.markdown(response_text)

            if sources:
                sources_html = " ".join(
                    f'<span class="source-badge">📄 {s}</span>' for s in sources
                )
                st.markdown(f"**Sources:** {sources_html}", unsafe_allow_html=True)

        # Save assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "sources": sources,
        })


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: BOOK APPOINTMENT
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "📅 Book Appointment":

    st.markdown("""
    <div class="hero-section">
        <h1>📅 Book an Appointment</h1>
        <p>Fill in your details and select a specialist to schedule your visit</p>
    </div>
    """, unsafe_allow_html=True)

    SLOTS = {
        "Cardiologist":       ["Monday 10:00 AM", "Monday 2:00 PM", "Wednesday 11:00 AM", "Friday 9:00 AM"],
        "Dermatologist":      ["Tuesday 11:00 AM", "Tuesday 3:00 PM", "Thursday 10:00 AM"],
        "Neurologist":        ["Monday 9:00 AM", "Wednesday 2:00 PM", "Friday 11:00 AM"],
        "Orthopedic":         ["Tuesday 9:00 AM", "Thursday 2:00 PM", "Saturday 10:00 AM"],
        "Ophthalmologist":    ["Monday 11:00 AM", "Wednesday 3:00 PM", "Friday 10:00 AM"],
        "Dentist":            ["Tuesday 10:00 AM", "Thursday 11:00 AM", "Saturday 9:00 AM"],
        "Gastroenterologist": ["Monday 3:00 PM", "Wednesday 10:00 AM", "Friday 2:00 PM"],
        "Pulmonologist":      ["Tuesday 2:00 PM", "Thursday 9:00 AM", "Saturday 11:00 AM"],
        "ENT Specialist":     ["Monday 2:00 PM", "Wednesday 9:00 AM", "Friday 3:00 PM"],
        "General Physician":  ["Daily 9:00 AM", "Daily 11:00 AM", "Daily 2:00 PM", "Daily 4:00 PM"],
    }

    with st.form("appointment_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Patient Name *", placeholder="Full name")
            age = st.number_input("Age *", min_value=0, max_value=150, value=25)
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
            email = st.text_input("Email *", placeholder="email@example.com")

        with col2:
            phone = st.text_input("Phone Number *", placeholder="+91 XXXXX XXXXX")
            preferred_date = st.date_input("Preferred Date *")
            specialization = st.selectbox("Specialization *", list(SLOTS.keys()))
            slot = st.selectbox("Available Slot *", SLOTS.get(specialization, []))

        symptoms = st.text_area("Symptoms", placeholder="Describe your symptoms…", height=80)

        submitted = st.form_submit_button("📅 Book Appointment", use_container_width=True, type="primary")

        if submitted:
            if not name or not email or not phone:
                st.error("⚠️ Please fill in all required fields (Name, Email, Phone).")
            else:
                data = {
                    "patient_name": name,
                    "age": age,
                    "gender": gender,
                    "email": email,
                    "phone": phone,
                    "symptoms": symptoms,
                    "specialization": specialization,
                    "preferred_date": str(preferred_date),
                    "slot": slot,
                }

                with st.spinner("Booking your appointment..."):
                    result = api_request("POST", "/book-appointment", data)

                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.balloons()
                    st.markdown(f"""
                    <div class="success-card">
                        <h2 style="color:#10B981;">✅ Appointment Confirmed!</h2>
                        <p style="color:#94A3B8;">{result.get('message', 'Booked successfully!')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.divider()
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Appointment ID:** `{result.get('appointment_id', 'N/A')}`")
                        st.markdown(f"**Patient:** {result.get('patient_name', 'N/A')}")
                        st.markdown(f"**Specialization:** {result.get('specialization', 'N/A')}")
                    with c2:
                        st.markdown(f"**Slot:** {result.get('slot', 'N/A')}")
                        st.markdown(f"**Date:** {result.get('preferred_date', 'N/A')}")
                        st.markdown(f"**Booked At:** {result.get('booking_timestamp', 'N/A')}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: APPOINTMENT HISTORY
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "📋 Appointment History":

    st.markdown("""
    <div class="hero-section">
        <h1>📋 Appointment History</h1>
        <p>All booked appointments</p>
    </div>
    """, unsafe_allow_html=True)

    result = api_request("GET", "/appointments")

    if "error" in result:
        st.error(f"❌ {result['error']}")
    else:
        appointments = result.get("appointments", [])
        if not appointments:
            st.info("No appointments found yet. Book one from the appointment page!")
        else:
            st.markdown(f"**Total:** {len(appointments)} appointments")
            st.dataframe(
                appointments,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "appointment_id": st.column_config.TextColumn("ID", width="small"),
                    "patient_name": "Patient Name",
                    "age": st.column_config.NumberColumn("Age", width="small"),
                    "gender": "Gender",
                    "email": "Email",
                    "phone": "Phone",
                    "symptoms": "Symptoms",
                    "specialization": "Specialization",
                    "slot": "Slot",
                    "preferred_date": "Date",
                    "booking_timestamp": "Booked At",
                },
            )


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "📊 Admin Dashboard":

    st.markdown("""
    <div class="hero-section">
        <h1>📊 Admin Dashboard</h1>
        <p>Appointment analytics and system overview</p>
    </div>
    """, unsafe_allow_html=True)

    stats = api_request("GET", "/appointments/stats")

    if "error" in stats:
        st.error(f"❌ {stats['error']}")
    else:
        # Metric cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📅 Total Appointments", stats.get("total", 0))
        with col2:
            st.metric("🏥 Specializations", len(stats.get("by_specialization", {})))
        with col3:
            st.metric("🕐 Recent Bookings", len(stats.get("recent", [])))

        st.divider()

        # Charts
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("### 📊 Appointments by Specialization")
            by_spec = stats.get("by_specialization", {})
            if by_spec:
                st.bar_chart(by_spec)
            else:
                st.info("No data yet.")

        with col_b:
            st.markdown("### 🕐 Recent Bookings")
            recent = stats.get("recent", [])
            if recent:
                for apt in recent:
                    with st.container():
                        st.markdown(
                            f"**{apt.get('appointment_id', '')}** — "
                            f"{apt.get('patient_name', 'N/A')} → "
                            f"*{apt.get('specialization', 'N/A')}* "
                            f"({apt.get('slot', 'N/A')})"
                        )
            else:
                st.info("No recent bookings.")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═══════════════════════════════════════════════════════════════════════════
# elif st.session_state.current_page == "ℹ️ About System":

#     st.markdown("""
#     <div class="hero-section" style="background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%);">
#         <h1>ℹ️ About This System</h1>
#         <p>Architecture, tech stack, and credits</p>
#     </div>
#     """, unsafe_allow_html=True)

#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown("### 🛠️ Tech Stack")
#         st.markdown("""
#         - 🐍 **Python 3.11**
#         - ⚡ **FastAPI** — REST API Backend
#         - 🎨 **Streamlit** — ChatGPT-style Frontend
#         - 🦜 **LangChain** — RAG Orchestration
#         - 🗄️ **ChromaDB** — Vector Database
#         - 🤖 **Ollama Mistral** — Local LLM
#         - 📐 **sentence-transformers** — Embeddings
#         - 🗃️ **SQLite** — Appointment Database
#         - 📧 **SMTP** — Email Confirmations
#         - 🐳 **Docker** — Containerization
#         """)

#     with col2:
#         st.markdown("### 🏗️ Architecture")
#         st.markdown("""
#         - 📄 MedQuAD XML → TXT Conversion
#         - ✂️ Document Chunking (500 tokens, 50 overlap)
#         - 🧬 Embedding with all-MiniLM-L6-v2
#         - 🔍 Semantic Search via ChromaDB
#         - 🧠 RAG: Context + Mistral LLM
#         - 🤖 AI Agent: Intent Routing
#         - 📅 Appointment Booking Pipeline
#         - 📧 Email Confirmation Service
#         - 📊 Analytics Dashboard
#         """)

#     st.divider()
#     st.markdown("### 👨‍💻 Credits")
#     st.markdown(
#         "Developed by **Lokesh Kumawat**\n\n"
#         "Healthcare AI Assistant — A production-style RAG system with appointment automation, "
#         "built for the Mindbowser Hackathon."
#     )

#     st.divider()
#     st.markdown("""
#     <div class="disclaimer-box">
#         ⚕️ <strong>Disclaimer:</strong> This assistant is for informational and appointment-support
#         purposes only and not a replacement for professional medical advice.
#     </div>
#     """, unsafe_allow_html=True)
