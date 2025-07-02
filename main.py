import streamlit as st
import time
import random
# Pastikan file-file ini ada di dalam folder 'utils'
from utils.invoke_lstm import invoke_lstm
from utils.invoke_distilbert import invoke_distilbert
from utils.get_references import get_references

# --- Mock Functions (for demonstration if utils are not available) ---
# Hapus atau komentari bagian ini jika Anda memiliki file invoke_... yang sebenarnya

# --- End of Mock Functions ---


# --- Page Configuration ---
st.set_page_config(
    page_title="IslamQ",
    page_icon="🌙",
    layout="centered",
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

secrets = st.secrets.get('secret_key')

# --- AI Response Logic ---
def get_ai_response_stream(user_query: str, model: str):
    """
    Generator function untuk streaming response dari AI.
    Memanggil model yang sesuai berdasarkan pilihan pengguna.
    """
    # Dapatkan response penuh dari model yang dipilih
    if model == "LSTM":
        full_response, response_tag = invoke_lstm(user_query)
    elif model == "DistilBERT":
        full_response, response_tag = invoke_distilbert(user_query)
    else:
        full_response = "Model tidak valid. Silakan pilih model yang tersedia."
        
    results = get_references(user_query, secrets, response_tag)
    
    # Stream response kata demi kata
    words = full_response.split()
    if not words: # Handle empty response
        yield "", references
        return

    streamed_response = ""
    for word in words:
        streamed_response += word + " "
        yield streamed_response.strip(), references
        time.sleep(0.05)
    
    # Yield response final
    yield full_response, results

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "DistilBERT" # Default model

# --- UI Rendering Logic ---

prompt_from_suggestion = None

# Tampilkan judul utama di semua kondisi
st.markdown('<h1 class="app-title">🌙 IslamQ</h1>', unsafe_allow_html=True)

# Jika percakapan BELUM dimulai, tampilkan layar sambutan
if not st.session_state.chat_started:
    st.markdown("<p style='text-align: center;'>Assalamu'alaikum. Ada yang bisa dibantu hari ini?</p>", unsafe_allow_html=True)

    # --- Model Selection ---
    model_choice = st.selectbox(
        'Pilih model AI yang ingin Anda gunakan:',
        ('DistilBERT', 'LSTM'),
        key='model_selector'
    )
    # Simpan pilihan ke session state
    st.session_state.selected_model = model_choice
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
    # Tampilkan model yang sedang digunakan
    st.info(f"Menggunakan model: **{st.session_state.selected_model}**", icon="🤖")
    for message in st.session_state.messages:
        avatar = "🌙" if message["role"] == "assistant" else "user"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("references"):
                with st.expander("Lihat Hadist Relevan 📚"):
                    for ref in message["references"]:
                        kitab = ref.get("kitab", "Kitab Tidak Dikenal")
                        hadits_id = ref.get("id", "ID Tidak Dikenal")
                        st.info(f"**{ref['kitab']}**, No. Hadits: `{ref['id']}` [🔗 Lihat]({ref['url']})", icon="📖")



# --- Input Handling ---
prompt_from_input = st.chat_input("Tulis pertanyaan Anda di sini...")
final_prompt = prompt_from_suggestion or prompt_from_input

# ... (sebelumnya)
if final_prompt:
    # Jika ini pesan pertama, set state chat dimulai
    if not st.session_state.chat_started:
        st.session_state.chat_started = True
        st.session_state.messages = [] # Kosongkan pesan awal

    # Tambahkan pesan user ke state
    st.session_state.messages.append({"role": "user", "content": final_prompt})

    # TAMBAHKAN: Tampilkan pesan user yang baru dikirim secara langsung
    with st.chat_message("user"):
        st.markdown(final_prompt)
    
    # Dapatkan dan tampilkan respons dari AI
    with st.chat_message("assistant", avatar="🌙"):
        message_placeholder = st.empty()
        
        full_response = ""
        references = []
        
        response_generator = get_ai_response_stream(final_prompt, st.session_state.selected_model)
        for response_chunk, refs in response_generator:
            full_response = response_chunk
            references = refs
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        
        if references:
            with st.expander("Lihat Hadist Relevan 📚"):
                for ref in references:
                    st.info(f"**{ref['kitab']}**, No. Hadits: `{ref['id']}` [🔗 Lihat]({ref['url']})", icon="📖")

    # Tambahkan respons AI yang lengkap ke state untuk riwayat percakapan
    st.session_state.messages.append({
        "role": "assistant", 
        "content": full_response, 
        "references": references
    })
    
    # HAPUS: st.rerun() tidak diperlukan lagi dan menyebabkan bug render
    # st.rerun()

