import streamlit as st
import time
import random
from utils.invoke import invoke

# --- Page Configuration ---
st.set_page_config(
    page_title="IslamQ",
    page_icon="🌙",
    layout="centered", # 'centered' lebih cocok untuk gaya Gemini
    initial_sidebar_state="auto"
)

# --- Custom CSS for Adaptive Gemini-like Theme ---
st.markdown("""
<style>
    /* Definisi variabel warna untuk LIGHT & DARK THEME */
    :root {
        --primary-bg: #f0f2f6;
        --secondary-bg: #ffffff;
        --assistant-bg: transparent; /* AI response tidak pakai bubble */
        --user-bg: #e0f0ff; /* Bubble user dengan warna biru muda */
        --text-color: #0d1117;
        --accent-color: #1a5e20;
        --expander-header-color: #2e7d32;
        --border-color: #c8e6c9;
        --shadow-color: rgba(0,0,0,0.05);
        --suggestion-card-bg: #ffffff;
        --suggestion-card-border: #e0e0e0;
        --suggestion-card-hover-bg: #f5f5f5;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --primary-bg: #0d1117;
            --secondary-bg: #21262d;
            --assistant-bg: transparent;
            --user-bg: #2c3e50; /* Bubble user di mode gelap */
            --text-color: #c9d1d9;
            --accent-color: #6cc644;
            --expander-header-color: #58a6ff;
            --border-color: #30363d;
            --shadow-color: rgba(0,0,0,0.2);
            --suggestion-card-bg: #21262d;
            --suggestion-card-border: #30363d;
            --suggestion-card-hover-bg: #30363d;
        }
    }

    /* General Styling */
    .stApp {
        background-color: var(--primary-bg);
        color: var(--text-color);
    }
    
    /* User Chat Bubble Styling */
    [data-testid="stChatMessage"][data-testid*="chat-message-user"] {
        background-color: var(--user-bg);
        border-radius: 20px;
        padding-top: 0.8rem;
        padding-bottom: 0.8rem;
        box-shadow: 0 1px 2px var(--shadow-color);
    }
    
    /* Styling untuk menghilangkan background pada AI response */
    [data-testid="stChatMessage"][data-testid*="chat-message-assistant"] {
        background-color: var(--assistant-bg);
        box-shadow: none;
    }

    [data-testid="stChatMessage"] > div > div > p {
        color: var(--text-color);
    }

    /* Expander untuk referensi */
    .stExpander {
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        background-color: var(--secondary-bg) !important;
    }
    
    .stExpander header {
        font-size: 0.9rem !important;
        color: var(--expander-header-color) !important;
    }
    
    /* Judul Aplikasi */
    h1.app-title {
        color: var(--accent-color);
        font-family: 'Georgia', serif;
        text-align: center;
        font-weight: 600;
    }
    
    .stButton > button {
        width: 100%;
        border: 1px solid var(--suggestion-card-border);
        background-color: var(--suggestion-card-bg);
        color: var(--text-color);
        transition: all 0.2s ease-in-out;
        border-radius: 8px;
        text-align: left;
        padding: 10px;
    }
    .stButton > button:hover {
        background-color: var(--suggestion-card-hover-bg);
        border-color: var(--accent-color);
        color: var(--accent-color);
    }

</style>
""", unsafe_allow_html=True)


# --- Placeholder for AI Response Logic ---
def get_ai_response_stream(user_query: str):
    """
    Generator function untuk streaming response dari AI.
    Fungsi ini akan yield response secara bertahap untuk efek streaming.
    """
    # Dapatkan response penuh dari invoke
    full_response = invoke(user_query)
    references = []  # Bisa dimodifikasi jika invoke mengembalikan referensi
    
    # Stream response kata demi kata atau chunk demi chunk
    words = full_response.split()
    streamed_response = ""
    
    for i, word in enumerate(words):
        streamed_response += word + " "
        # Yield response yang sudah dibangun sejauh ini
        yield streamed_response.strip(), references
        # Delay kecil untuk efek streaming (bisa disesuaikan)
        time.sleep(0.05)  # Delay 50ms per kata
    
    # Yield response final
    yield full_response, references

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# --- UI Rendering Logic ---

# **FIX:** Initialize prompt_from_suggestion to None before the conditional logic
prompt_from_suggestion = None

# Jika percakapan BELUM dimulai, tampilkan layar sambutan
if not st.session_state.chat_started:
    st.markdown('<h1 class="app-title">🌙 IslamQ</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Assalamu'alaikum. Ada yang bisa dibantu hari ini?</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<h3 style='text-align: center;'>Coba tanyakan:</h3>", unsafe_allow_html=True)
    
    # Kartu Saran
    suggestion_prompts = [
        "Apa itu sabar dalam Islam?",
        "Bagaimana cara bersyukur yang benar?",
        "Jelaskan tentang Rukun Iman",
        "Kisah singkat Nabi Muhammad SAW"
    ]
    
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestion_prompts):
        if cols[i % 2].button(suggestion, key=f"suggestion_{i}"):
            prompt_from_suggestion = suggestion

# Jika percakapan SUDAH dimulai, tampilkan histori chat
else:
    # (Optional) You can still show the title if you want
    # st.markdown('<h1 class="app-title">🌙 Asisten AI Islami</h1>', unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else: # Assistant's turn (no bubble)
            with st.chat_message("assistant", avatar="🌙"):
                st.markdown(message["content"])
                if message.get("references"):
                    with st.expander("Lihat Referensi 📚"):
                        for ref in message["references"]:
                            st.info(f"**{ref['title']}**: {ref['source']}", icon="📖")

# --- Input Handling ---
prompt_from_input = st.chat_input("Tulis pertanyaan Anda di sini...")
final_prompt = prompt_from_suggestion or prompt_from_input

if final_prompt:
    # Set state bahwa chat sudah dimulai
    if not st.session_state.chat_started:
        st.session_state.chat_started = True

    # Tambah pesan user ke histori
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    
    # Tampilkan pesan user yang baru
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # Buat placeholder untuk streaming response
    with st.chat_message("assistant", avatar="🌙"):
        message_placeholder = st.empty()
        references_placeholder = st.empty()
        
        # Stream the response
        full_response = ""
        references = []
        
        for response_chunk, refs in get_ai_response_stream(final_prompt):
            full_response = response_chunk
            references = refs
            # Update placeholder dengan response yang sedang dibangun
            message_placeholder.markdown(full_response + "▌")  # Cursor blinking effect
        
        # Hapus cursor dan tampilkan response final
        message_placeholder.markdown(full_response)
        
        # Tampilkan referensi jika ada
        if references:
            with references_placeholder.expander("Lihat Referensi 📚"):
                for ref in references:
                    st.info(f"**{ref['title']}**: {ref['source']}", icon="📖")

    # Tambah response ke histori setelah streaming selesai
    st.session_state.messages.append({
        "role": "assistant", 
        "content": full_response, 
        "references": references
    })
    
    # Rerun untuk me-refresh tampilan ke mode chat
    st.rerun()
