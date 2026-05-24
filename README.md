# 🌾 BimaSetu — Automated Crop Damage Assessment

> Automated Damage Assessment for Farmers · PMFBY-Compliant Claim Generation

[![CI](https://github.com/your-org/bimasetu/actions/workflows/deploy.yml/badge.svg)](https://github.com/your-org/bimasetu/actions)

---

## What it does

1. **Capture** — Farmer photographs damaged crops via rear camera with GPS coordinates auto-captured
2. **Assess** — YOLOv8 segmentation identifies crop vs damage areas; ResNet50 classifies damage type (waterlogging / lodging / hail / pest)
3. **Generate** — PMFBY-compliant 2-page PDF claim report is generated with photo evidence and AI analysis
4. **Track** — Farmer dashboard shows all past claims with download links

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Frontend  | React 18 + Vite + Tailwind CSS    |
| Backend   | FastAPI (Python 3.11) + Uvicorn   |
| ML        | YOLOv8 Segmentation + ResNet50    |
| Database  | SQLite (via Python stdlib)        |
| PDF       | ReportLab                         |
| Auth      | Firebase Authentication (Google)  |

---

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- A Firebase project (Auth + Firestore + Storage enabled)

### 1. Clone & configure

```bash
git clone https://github.com/your-org/bimasetu.git
cd bimasetu
```

### 2. Backend setup

```bash
cd backend
cp .env.example .env
# Edit .env — set BASE_URL if deploying remotely

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

> **No ML weights?** No problem — the system auto-falls back to HSV colour analysis (segmentation) and rule-based classification. Results will be approximate but functional.

### 3. Frontend setup

```bash
cd frontend
cp .env.example .env
# Fill in your Firebase project values in .env

npm install
npm run dev
```

App runs at `http://localhost:5173`.

### Language

Use the **globe icon** in the top navbar to switch between **English**, **हिन्दी (Hindi)**, and **ಕನ್ನಡ (Kannada)**. Your choice is saved in the browser.

### 4. Firebase configuration

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project
3. Enable **Authentication → Google** sign-in provider
4. Enable **Firestore Database** (production mode)
5. Enable **Storage**
6. Copy your web app config into `frontend/.env`

---

## Docker

```bash
# Start both services
docker compose up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

---

## Project Structure

```
bimasetu/
├── frontend/src/
│   ├── components/
│   │   ├── CameraCapture.jsx   # Rear camera + GPS capture
│   │   ├── UploadForm.jsx      # Photo upload + claim submit
│   │   ├── ResultCard.jsx      # Assessment results + PDF download
│   │   ├── ClaimDownload.jsx   # Reusable PDF download button
│   │   └── Navbar.jsx
│   ├── pages/
│   │   ├── Home.jsx            # Public marketing landing (guests)
│   │   ├── FarmerHome.jsx      # Authenticated farmer home (stats, claims)
│   │   ├── Profile.jsx         # Account settings & setup checklist
│   │   ├── Dashboard.jsx       # Claim upload & history
│   │   ├── Login.jsx           # Sign-in
│   │   └── Signup.jsx          # Registration
│   ├── context/AuthContext.jsx
│   └── i18n/                   # English, Hindi (हिन्दी), Kannada (ಕನ್ನಡ)
│
└── backend/
    ├── main.py                 # FastAPI app entry
    ├── database.py             # SQLite setup
    ├── routers/
    │   ├── analyze.py          # POST /api/analyze
    │   └── claims.py           # GET/DELETE /api/claims
    ├── ml/
    │   ├── segmentor.py        # YOLOv8 + HSV fallback
    │   └── classifier.py       # ResNet50 + rule-based fallback
    └── pdf/generator.py        # ReportLab PMFBY PDF
```

---

## API Reference

### `POST /api/analyze`

Accepts multipart form:

| Field          | Type   | Description                    |
|----------------|--------|--------------------------------|
| `image`        | file   | JPEG/PNG crop photo            |
| `lat`          | float  | GPS latitude                   |
| `lng`          | float  | GPS longitude                  |
| `timestamp`    | string | ISO 8601 capture time          |
| `uid`          | string | Firebase user UID              |
| `display_name` | string | Farmer name                    |
| `claim_id`     | string | Optional pre-generated ID      |

**Response:**
```json
{
  "success": true,
  "data": {
    "claim_id": "abc123",
    "damage_pct": 67.3,
    "damage_type": "waterlogging",
    "confidence": 0.89,
    "mask_url": "http://localhost:8000/static/masks/xyz.png",
    "image_url": "http://localhost:8000/static/uploads/abc123.jpg",
    "pdf_url": "http://localhost:8000/static/pdfs/abc123.pdf",
    "seg_method": "hsv_fallback",
    "cls_method": "rule_based",
    "status": "completed"
  },
  "error": ""
}
```

### `GET /api/claims?uid={uid}`

Returns all claims for a farmer ordered by newest first.

### `GET /api/claims/{claim_id}`

Returns a single claim by ID.

---

## Adding ML Model Weights

Place your trained weights in `backend/ml/model_weights/`:

```
backend/ml/model_weights/
├── yolov8-seg.pt         # YOLOv8 segmentation weights
└── resnet50_damage.pth   # ResNet50 fine-tuned on 4 damage classes
```

The app auto-detects weights at startup and logs whether it's using the ML model or the rule-based fallback.

**ResNet50 class mapping:**
```
0 → waterlogging
1 → lodging
2 → hail
3 → pest
```

---

## Disclaimer

Generated claim PDFs are for insurer review only and must be verified by a licensed agricultural assessor before formal claim processing. This tool is designed to assist, not replace, official PMFBY assessment procedures.

---

## License

MIT © BimaSetu Contributors
