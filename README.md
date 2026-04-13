# 🏍️ Ride Media Manager

A Raspberry Pi 5–powered **Auto Media Offload System** for bike rides.

Automatically detects SD cards / USB devices, imports media, organizes footage into ride-based folders, and prepares it for editing.

---

## 🚀 Features (MVP)

- 🔌 Auto device detection (via mounted folders)
- 📂 Media scanning (video, images, audio)
- 🧠 Source classification (DJI, GoPro, phone, etc.)
- 📥 One-click import into ride sessions
- 🔁 Duplicate detection (fingerprint-based)
- 🛡 Safe copy with `.part` temp files
- ✅ File integrity verification (size-based)
- 📊 Import progress tracking
- 🌐 Local web dashboard (FastAPI + Jinja)

---

## ⚙️ Setup

### 1. Clone repo

```bash
git clone <your-repo-url>
cd ride-media-manager
Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
http://127.0.0.1:8000