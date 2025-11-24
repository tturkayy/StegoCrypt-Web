# StegoCrypt Web 🌐

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stegocrypt.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**StegoCrypt Web** is the online demonstration of the [StegoCrypt Desktop Application](https://github.com/tturkayy/StegoCrypt).

It allows you to experience **AES-256 Encryption** and **LSB Steganography** directly in your browser, without installing any software.

---

## 🚀 Live Demo

Click the button below to launch the web app:

### 👉 [Launch StegoCrypt Web](https://stegocrypt.streamlit.app/)

*(Note: If the app is sleeping, give it a moment to wake up!)*

---

## ⚠️ Privacy & Security Disclaimer

**This is a cloud-based demonstration.** While the application processes files in memory and deletes them after the session, your files are uploaded to a cloud server (Streamlit Cloud) for processing.

🔒 **For Maximum Privacy & Offline Security:**
Please download the standalone Desktop version, which runs 100% offline on your machine.

👉 **[Download StegoCrypt Desktop (.exe)](https://github.com/tturkayy/StegoCrypt)**

---

## ✨ Features

* **Zero Installation:** Runs instantly in any modern web browser.
* **Same Core Engine:** Uses the exact same `crypto.py` and `stego.py` backend engines as the desktop app.
* **Modern UI:** Features a responsive, "Neon Dark" themed interface built with **Streamlit**.
* **Cross-Platform:** Works on Windows, macOS, Linux, and even Mobile devices.

---

## 🛠️ Running Locally

If you prefer to run this web interface locally on your own machine:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/tturkayy/StegoCrypt-Web.git](https://github.com/tturkayy/StegoCrypt-Web.git)
    cd StegoCrypt-Web
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Project Structure

```text
StegoCrypt-Web/
├── app.py           # The Streamlit Frontend Interface
├── crypto.py        # Shared Backend: AES-256 Logic
├── stego.py         # Shared Backend: LSB Image Logic
└── requirements.txt # Web dependencies (Streamlit, Pillow, PyCryptodome)
```

---

## 📄 License
This project is open-source and licensed under the MIT License.

---

*Developed by Turkay Yildirim*
