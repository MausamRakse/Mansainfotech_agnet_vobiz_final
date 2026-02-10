
# Mansa AI Outbound Agent Platform

An advanced autonomous outbound calling platform powered by LiveKit, Deepgram, and LLMs. Features a modern React dashboard for campaign management, transcript review, and agent monitoring.

---

## 🚀 Features

- **Outbound AI Calling Agent**
  - Human-like voice interactions (Cartesia/Deepgram/OpenAI TTS)
  - Intelligent conversation flow (Groq Llama 3/GPT-4)
  - Real-time speech-to-text (Deepgram Nova 3)
  - SIP Trunk integration (Vobiz.ai)

- **Agent Console (Dashboard)**
  - **Bulk Calling**: Upload Excel/CSV files to trigger mass outbound campaigns.
  - **Single Call**: Dial a single number instantly for testing.
  - **Transcript Viewer**: Read structured JSON/Unstructured text transcripts.
  - **Call Recordings**: Listen to and download user audio recordings.
  - **Real-time Status**: Monitor active calls and agent states.

---

## 🛠 Tech Stack

### Frontend
- **React 18** + **Vite**
- **TailwindCSS** for styling
- **Lucide React** for icons
- **Axios** for API requests

### Backend
- **FastAPI** (Python 3.10+)
- **LiveKit Server SDK** for agent dispatch
- **Pandas** for Excel processing
- **Uvicorn** as ASGI server

### Agent Infrastructure
- **LiveKit Agents Framework**
- **Deepgram** (STT), **Groq** (LLM), **Cartesia/Deepgram** (TTS)

---

## 📦 Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- LiveKit Cloud Project
- API Keys for Deepgram, Groq, Cartesia, Vobiz

### 2. Backend Setup
1. **Clone Repo**
   ```bash
   git clone <repo_url>
   cd LiveKit-Vobiz-Outbound
   ```

2. **Install Python Dependencies**
   ```bash
   # Main agent dependencies
   uv pip install -r requirements.txt
   
   # Backend API dependencies
   uv pip install -r backend/requirements.txt
   ```

3. **Configure Environment**
   Duplicate `.env.example` to `.env` and fill in your keys:
   ```env
   LIVEKIT_URL=wss://...
   LIVEKIT_API_KEY=...
   LIVEKIT_API_SECRET=...
   OPENAI_API_KEY=...
   DEEPGRAM_API_KEY=...
   GROQ_API_KEY=...
   VOBIZ_SIP_DOMAIN=...
   TTS_PROVIDER=deepgram
   ```

### 3. Frontend Setup
1. **Navigate to frontend**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure API**
   Ensure `vite.config.js` proxies `/api` to `http://127.0.0.1:8000`.

---

## 🏃 Running Globally

### Step 1: Start the Agent Worker
This process handles the actual calls.
```bash
# In Root Directory
python agent.py dev
```

### Step 2: Start the Backend API
This serves the Dashboard API and file uploads.
```bash
# In Root Directory (New Terminal)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Start the Frontend
This launches the UI.
```bash
# In Frontend Directory (New Terminal)
cd frontend
npm run dev
```

Visit **http://localhost:5173** to access the console.

---

## 🚢 Deployment (Render)

### Backend (Web Service)
1. **Build Command**: `pip install -r backend/requirements.txt`
2. **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3. **Env Vars**: Add all keys from `.env`

### Frontend (Static Site)
1. **Build Command**: `npm install && npm run build`
2. **Publish Directory**: `dist`
3. **Rewrite Rule**: `/*` -> `/index.html` (for SPA routing)

### Agent Worker (Background Worker)
1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `python agent.py start`
3. **Env Vars**: Add all keys from `.env`

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/call-single` | Trigger a call to one number |
| `POST` | `/api/bulk-call` | Trigger calls for a list of numbers |
| `POST` | `/api/upload-excel` | Parse phone numbers from Excel/CSV |
| `GET` | `/api/transcripts` | Fetch conversation logs |
| `GET` | `/api/recordings` | List audio recordings |

---

## © License
Mansa Infotech 2024. All rights reserved.
