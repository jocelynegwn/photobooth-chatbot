
import streamlit as st
from google import genai

try:
    google_api_key = st.secrets["GEMINI"]
except Exception:
    google_api_key = None

if not google_api_key:
    st.error("API Key kosong!")
    st.stop()

st.session_state.genai_client = genai.Client(api_key=google_api_key)

# CSS STYLING: Background studio foto hangat
st.markdown("""
<style>
    /* Mengubah seluruh halaman menjadi latar studio foto warna kuning hangat dengan efek cahaya sorot putih lembut di tengah */
    .stApp {
        background: radial-gradient(circle at 50% 35%, rgba(255, 255, 255, 0.28) 0%, rgba(230, 202, 135, 0.8) 45%, #b89342 100%),
                    radial-gradient(circle at 50% 30%, #e6ca87 0%, #d4b265 60%, #b89342 100%) !important;
        background-attachment: fixed !important;
        color: #2b2b2b !important;
    }
    
    h1 {
        color: #2b2b2b !important;
        text-shadow: 0 2px 8px rgba(255, 255, 255, 0.3);
        font-weight: 700;
    }
    
    p, .stCaption {
        color: #3f3a2a !important;
        font-weight: 500;
    }
    
    /* Styling bubble chat agar menyatu estetik dengan tema studio */
    .stChatMessage {
        background-color: rgba(255, 253, 245, 0.9) !important;
        border: 1px solid rgba(184, 147, 66, 0.3) !important;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        color: #2b2b2b !important;
    }
    
    /* Styling kotak input chat di bagian bawah */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📸 Photobooth Studio Assistant")
st.caption("Asisten virtual interaktif untuk informasi paket foto, rekomendasi kreatif, dan booking.")

if "genai_client" not in st.session_state:
    st.session_state.genai_client = genai.Client(api_key=google_api_key)

# System Instruction 
system_instruction = """
You are a helpful and friendly digital assistant for a Photobooth & Self-Photo Studio. 
Your primary goal is to assist customers with information about photo packages, pricing, studio facilities, staff, and bookings based on the data below.

--- DATA KATALOG PRODUK & PAKET FOTO ---
1. Self-Photo Basic: Rp 70.000 | Durasi: 15 Menit | Keterangan: Max 2 orang, Free All Softcopy, Dapat 2 cetak foto.
2. Self-Photo Group: Rp 125.000 | Durasi: 20 Menit | Keterangan: Max 5 orang, Free All Softcopy, Dapat 3 cetak foto.
3. Studio Pro Solo: Rp 100.000 | Durasi: 20 Menit | Keterangan: Didampingi fotografer profesional, Free All Softcopy, 2 cetak foto.
4. Studio Pro Group: Rp 500.000 | Durasi: 30 Menit | Keterangan: Max 20 orang, Didampingi fotografer profesional, Free All Softcopy, 5 cetak foto.
5. Paket Foto Wisuda: Rp 350.000 | Durasi: 30 Menit | Keterangan: Max 4 orang, include peminjaman properti wisuda, Free All Softcopy, 5 cetak foto.
6. Paket Foto Ulang Tahun: Rp 400.000 | Durasi: 30 Menit | Keterangan: Max 6 orang, include balon & properti Ultah, Free All Softcopy, 5 cetak foto.
7. Paket Foto Wedding: Rp 750.000 | Durasi: 45 Menit | Keterangan: Sesi Prewedding/Bridal, fotografer profesional, Free All Softcopy, 5 cetak foto.
8. Paket Foto Keluarga: Rp 450.000 | Durasi: 30 Menit | Keterangan: Max 10 orang, fotografer profesional, Free All Softcopy, 5 cetak foto.
9. Tambah 1 Foto Solo: Rp 15.000 | Durasi: - | Keterangan: Tambahan 1 lembar cetak foto ukuran 4R / Strip (Perorangan).
10. Tambah 1 Foto Group: Rp 25.000 | Durasi: - | Keterangan: Tambahan 1 lembar cetak foto ukuran 4R / 5R (Kelompok).
11. Tambah 1 Orang pada Foto Group: Rp 30.000 | Durasi: - | Keterangan: Biaya tambahan per orang.

--- DAFTAR STAFF & CREW ---
- Ryan (Photographer & Assistant)
- Lili (Photographer & Assistant)
- Sarah (Front Desk & Editor)
- Kevin (Front Desk & Editor)

--- INFORMASI & KONTAK STUDIO ---
- Alamat: Jl. Studio Foto No. 8, Jakarta Selatan (Dekat Area Kampus / Mall)
- Admin WhatsApp / Call: 0812-3456-7890
- Jam Operasional: Setiap Hari, 10.00 WIB - 21.00 WIB

--- ATURAN OPERASIONAL & KREATIVITAS ---
1. Jawab pertanyaan pelanggan dengan ramah, akurat berdasarkan data di atas, dan sebutkan harga dalam format Rupiah (IDR).
2. **CREATIVITY & RECOMMENDATIONS:** Jika pengguna meminta saran (misalnya tema foto, kecocokan jumlah orang dengan paket, atau outfit/pose), gunakan kreativitasmu untuk memberikan saran yang menarik, estetis, dan solutif.
3. Selalu sandingkan rekomendasi kreatifmu dengan data harga dan paket yang valid dari daftar di atas.
4. Jika pelanggan ingin melakukan booking, sesi foto, atau pertanyaan lanjutan, arahkan mereka ke Admin WhatsApp kami di **0812-3456-7890** atau kunjungi studio di Jl. Studio Foto No. 8.
"""

if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.genai_client.chats.create(
        model="gemini-3.8-flash",
        config={
            "system_instruction": system_instruction
        }
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

def handle_preset_click(preset_prompt):
    st.session_state.messages.append({"role": "user", "content": preset_prompt})
    try:
        response = st.session_state.chat.send_message(preset_prompt)
        answer = response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        answer = f"Terjadi error: {e}"
    st.session_state.messages.append({"role": "assistant", "content": answer})

# --- TAMPILAN RIWAYAT & 4 TOMBOL INTERAKTIF ---
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg["role"] == "assistant" and idx == len(st.session_state.messages) - 1:
            st.write("")
            cols = st.columns(4)
            with cols[0]:
                if st.button("🔄 Percakapan Baru", key=f"reset_{idx}"):
                    st.session_state.pop("chat", None)
                    st.session_state.pop("messages", None)
                    st.rerun()
            with cols[1]:
                if st.button("🎁 Paket Menarik", key=f"pkt_{idx}"):
                    handle_preset_click("Tolong berikan rekomendasi paket foto yang paling populer dan menarik di studio ini beserta harganya.")
                    st.rerun()
            with cols[2]:
                if st.button("🎨 Tema Foto", key=f"tema_{idx}"):
                    handle_preset_click("Berikan saya beberapa ide rekomendasi tema foto yang estetis dan kekinian.")
                    st.rerun()
            with cols[3]:
                if st.button("💃 Ide Pose", key=f"pose_{idx}"):
                    handle_preset_click("Berikan saya beberapa ide pose foto yang keren dan natural untuk sesi photobooth.")
                    st.rerun()

prompt = st.chat_input("Ketik pertanyaan atau minta rekomendasi paket foto di sini...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = st.session_state.chat.send_message(prompt)
        answer = response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        answer = f"Terjadi error: {e}"

    with st.chat_message("assistant"):
        st.markdown(answer)
        
        cols = st.columns(4)
        with cols[0]:
            if st.button("🔄 Percakapan Baru", key="reset_new"):
                st.session_state.pop("chat", None)
                st.session_state.pop("messages", None)
                st.rerun()
        with cols[1]:
            if st.button("🎁 Paket Menarik", key="pkt_new"):
                handle_preset_click("Tolong berikan rekomendasi paket foto yang paling populer dan menarik di studio ini beserta harganya.")
                st.rerun()
        with cols[2]:
            if st.button("🎨 Tema Foto", key="tema_new"):
                handle_preset_click("Berikan saya beberapa ide rekomendasi tema foto yang estetis dan kekinian.")
                st.rerun()
        with cols[3]:
            if st.button("💃 Ide Pose", key="pose_new"):
                handle_preset_click("Berikan saya beberapa ide pose foto yang keren dan natural untuk sesi photobooth.")
                st.rerun()

    st.session_state.messages.append({"role": "assistant", "content": answer})
