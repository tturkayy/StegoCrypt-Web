import streamlit as st
import crypto
import stego
import io
import struct
import re

st.set_page_config(
    page_title="StegoCrypt",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    header {visibility: hidden;}
    [data-testid="stHeader"] {visibility: hidden;}
    footer {visibility: hidden;}

    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: stretch;
        min-height: 100vh;
        max-width: 1100px;
    }

    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }

    div[data-testid="stFileUploader"] section {
        background-color: #1e293b;
        border: 2px dashed #38bdf8; 
        border-radius: 12px;
        padding: 30px;
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploader"] section:hover {
        background-color: #162032;
        border-color: #22d3ee;
    }

    .stTextInput > div > div > input {
        background-color: #1e293b;
        color: white;
        border: 1px solid #475569;
        border-radius: 8px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #38bdf8;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.8rem;
        border-radius: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.6);
        transform: scale(1.02);
    }

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: #f8fafc;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
        margin-bottom: 0;
        line-height: 1.2;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 20px;
        margin-top: 5px;
    }

    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 10px;
        margin-top: 5px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 10px 25px;
        height: auto;
        border: 1px solid transparent;
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #38bdf8;
        color: white;
        border-color: #38bdf8;
    }

    ul.pass-rules { list-style-type: none; padding: 0; margin: 8px 0; }
    li.pass-item { font-size: 0.8rem; margin-bottom: 4px; transition: color 0.3s; }
    .valid { color: #4ade80; font-weight: bold; } 
    .invalid { color: #64748b; }

    .custom-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #020617;
        color: #64748b;
        text-align: center;
        padding: 15px;
        border-top: 1px solid #1e293b;
        z-index: 9999;
    }
    a { color: #38bdf8 !important; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="main-title">StegoCrypt</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AES-256 Steganography Tool</p>', unsafe_allow_html=True)


def analyze_password(password):
    return {
        "Min 8 Characters": len(password) >= 8,
        "Uppercase Letter": bool(re.search(r"[A-Z]", password)),
        "Lowercase Letter": bool(re.search(r"[a-z]", password)),
        "Digit": bool(re.search(r"\d", password)),
        "Special Char": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
    }


def is_password_strong(analysis):
    return all(analysis.values())


tab1, tab2 = st.tabs(["ENCRYPT", "DECRYPT"])

with tab1:
    c1, c2 = st.columns([1, 1], gap="large")

    with c1:
        st.markdown('<p class="section-header">1. Select Files</p>', unsafe_allow_html=True)
        cover_image = st.file_uploader("Upload Cover Image (PNG/JPG)", type=["png", "jpg", "jpeg"], key="u1")
        secret_file = st.file_uploader("Upload Secret File (Any Format)", type=None, key="u2")

    with c2:
        st.markdown('<p class="section-header">2. Security</p>', unsafe_allow_html=True)
        password = st.text_input("Encryption Password", type="password", placeholder="Enter a strong password",
                                 key="p1")

        analysis = analyze_password(password if password else "")
        html_list = "<ul class='pass-rules'>"
        for rule, passed in analysis.items():
            css_class = "valid" if passed else "invalid"
            icon = "✔" if passed else "•"
            html_list += f"<li class='pass-item {css_class}'>{icon} {rule}</li>"
        html_list += "</ul>"
        st.markdown(html_list, unsafe_allow_html=True)

        st.write("")

        if st.button("ENCRYPT & DOWNLOAD", use_container_width=True):
            if not cover_image or not secret_file or not password:
                st.error("Missing files or password.")
            elif not is_password_strong(analysis):
                st.error("Password is too weak.")
            else:
                try:
                    with st.spinner("Encrypting..."):
                        file_bytes = secret_file.read()
                        filename = secret_file.name.encode('utf-8')
                        header = struct.pack('I', len(filename))
                        full_payload = header + filename + file_bytes

                        encrypted_payload = crypto.encrypt_message(full_payload, password)
                        output_buffer = io.BytesIO()
                        stego.encode_image(cover_image, encrypted_payload, output_buffer)

                        st.balloons()
                        st.success("Encryption Successful!")
                        st.download_button(
                            label="DOWNLOAD SECURE IMAGE",
                            data=output_buffer.getvalue(),
                            file_name="stegocrypt_secure.png",
                            mime="image/png",
                            type="primary",
                            use_container_width=True
                        )
                except ValueError as e:
                    st.error(f"Capacity Error: {e}")
                except Exception as e:
                    st.error(f"Error: {e}")

with tab2:
    c_dec1, c_dec2 = st.columns([1, 1], gap="large")

    with c_dec1:
        st.markdown('<p class="section-header">1. Source Image</p>', unsafe_allow_html=True)
        enc_image = st.file_uploader("Upload Encrypted PNG", type=["png"], key="u3")

    with c_dec2:
        st.markdown('<p class="section-header">2. Authentication</p>', unsafe_allow_html=True)
        dec_pass = st.text_input("Decryption Password", type="password", key="p2")

        st.write("")
        st.write("")

        if st.button("DECRYPT & EXTRACT", use_container_width=True):
            if not enc_image or not dec_pass:
                st.error("Missing image or password.")
            else:
                try:
                    with st.spinner("Decrypting..."):
                        encrypted_data = stego.decode_image(enc_image)
                        decrypted_payload = crypto.decrypt_message(encrypted_data, dec_pass)

                        if decrypted_payload == b"ERROR" or decrypted_payload == b"HATA":
                            st.error("Access Denied: Incorrect password.")
                        else:
                            filename_len = struct.unpack('I', decrypted_payload[:4])[0]
                            filename = decrypted_payload[4: 4 + filename_len].decode('utf-8')
                            file_data = decrypted_payload[4 + filename_len:]

                            st.success(f"File Found: {filename}")
                            st.download_button(
                                label="DOWNLOAD FILE",
                                data=file_data,
                                file_name=filename,
                                type="primary",
                                use_container_width=True
                            )
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("""
<div class="custom-footer">
    StegoCrypt Web v1.0 &nbsp;|&nbsp; Developed by <a href="https://github.com/tturkayy" target="_blank">Turkay Yildirim</a>
    <br>
    <span style="opacity: 0.5; font-size: 12px;">No data is stored on servers. Use Desktop App for max privacy.</span>
</div>
""", unsafe_allow_html=True)
