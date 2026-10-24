# Swarna Khata Book — Jewellery ERP (MVP)

A modular monolithic Jewellery ERP built with **Django REST Framework (Backend)**, **React + TypeScript + Vite (Frontend)**, and **PostgreSQL**.

Designed following [`jewellery_erp_coding_workflow_mindmap.md`](./jewellery_erp_coding_workflow_mindmap.md) to run and test locally today, and deploy to AWS/GCP/DigitalOcean without code refactoring.

---

## Features Built in this MVP

### 1. Camera Photo Capture & QR Code Barcode Tags
* **Live Camera Stream**: Uses HTML5 MediaDevices camera to snap live photos of jewelry items on counter / webcam.
* **Instant QR Generation**: Auto-generates high-resolution QR tags encoded with product metadata (SKU, Gross Weight, Net Pure Weight, Purity, HUID).
* **Jewelry Tag View & Print**: Previews ready-to-print tags styled for standard physical jewelry labels (with shop name, SKU, purity, weights, and barcode).

### 2. POS Billing & Invoicing
* **Wireless Mobile QR Scanner & POS Real-Time Sync**: Connect any smartphone camera wirelessly to the POS via a secure single-use pairing QR code. The phone's rear camera scans jewelry tag QR codes via `@zxing/browser`, resolving items directly from inventory, checking branch permissions, and pushing items in real time to the laptop cart over WebSockets without page refreshes.
* **Camera QR Scanner & Live Search**: Scan printed jewelry tags with laptop camera or search items by SKU / name / HUID.
* **Live Bullion Gold Rates**: Automatically pulls today's rate based on item purity (24KT, 22KT, 18KT, 14KT, Silver).
* **Transparent Pricing Calculation**:
  $$\text{Unit Price} = (\text{Net Weight} \times \text{Gold Rate}) + \text{Making Charges} + \text{Stone Charges}$$
* **Old Gold Exchange Deduction**: Enter customer's exchange weight & rate to instantly deduct from bill.
* **Tax Ready**: Automatically calculates 3% Jewellery GST (1.5% CGST + 1.5% SGST).
* **Payment Methods**: Cash, UPI, Card, or partial advance payments.
* **Tax Invoice PDF**: One-click generation and download of professional PDF invoices powered by ReportLab.
* **Stock Movement Audit**: Every checkout atomically decrements stock via the stock ledger.

### 3. Accounting & Day Book
* **Daily Cash Day Book**:
  * Opening balance
  * Cash In (sales receipts)
  * Cash Out (old gold buybacks, expenses)
  * Real-time drawer cash balance
  * "Close Business Day" audit lock
* **Live Metal Rates Manager**: Update daily market rates per purity across the showroom with one click.
* **Audit Trail**: Cancellations are handled via reversal movements, preserving ledger integrity.

---

## Architecture & Scalability

* **Modular Monolith**: One backend deployment split into discrete Django apps (`accounts`, `products`, `stock`, `billing`, `accounting`, `qr_tags`). Can be broken into microservices later without schema rewrites.
* **Data Integrity**: Monetary values and weights use `NUMERIC` / `DecimalField` (up to 3 decimal places for grams), never floating point.
* **Cloud-Ready Storage**: File uploads (product photos, QR code images) use Django's abstracted storage. Swapping local disk to Amazon S3 / Google Cloud Storage requires only configuring `django-storages` in `settings.py`.
* **Stateless Auth**: SimpleJWT tokens allow running behind multiple load-balanced instances in production.

---

## Quick Start (Local Development)

### Prerequisites
1. **Python 3.12 (64-bit)**
2. **[`uv`](https://docs.astral.sh/uv/)** fast Python package & project manager:
   ```powershell
   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

   # macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **Node.js 20+** & npm
4. **PostgreSQL** running locally (e.g. Docker / Rancher Desktop container on port `5433` or native PostgreSQL on `5432` per `backend/.env`)

---

### Backend Setup & Execution with `uv`

The project is configured with `pyproject.toml` and lockfile management via `uv`.

#### 1. Install Dependencies & Synchronize Environment
From the repository root:
```powershell
uv sync
```
> [!NOTE]
> `uv sync` automatically discovers Python 3.12, creates the root `.venv` virtual environment, and installs all dependencies in a fraction of a second.

#### 2. Run Database Migrations
```powershell
uv run --directory backend python manage.py migrate
```

#### 3. Seed Initial Demo Data (Showroom, Gold Rates, Categories, Sample Items)
```powershell
uv run --directory backend python seed_data.py
```

#### 4. Run Functional & Mobile Scanner Test Suites
```powershell
uv run --directory backend python test_mvp.py
uv run --directory backend python test_mobile_scanner.py
```

#### 5. Start Django Development Server (ASGI with WebSockets)
```powershell
# High-concurrency ASGI server with WebSockets
uv run --directory backend uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload

# OR using standard runserver
uv run --directory backend python manage.py runserver 0.0.0.0:8000
```

*(Alternatively, you can activate the environment manually: `.\.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on Unix, then run standard `python` or `uvicorn` commands).*

---

### Frontend Setup & Execution
In a separate terminal:
```powershell
cd frontend
npm install
npm run dev
```

---

### Wireless Mobile Scanner Usage & HTTPS Setup

1. On the laptop, navigate to **POS Billing & Invoice** (`http://localhost:5173`).
2. Click **Connect Mobile QR Scanner** in the top action bar.
3. A pairing modal opens showing a temporary, single-use pairing QR code (valid for 5 minutes).
4. Point your mobile phone camera at the pairing QR code to open the scanner URL (`http://<LAN_IP>:5173/scanner?session_id=...&code=...`).
5. The phone opens the mobile scanner interface, redeems the pairing code securely, and activates the rear camera via `@zxing/browser`.
6. Scan any physical jewelry item QR tag with your phone. The decoded item is validated by the backend and added to the laptop POS cart in real time without refreshing the page!

> [!NOTE]
> **Mobile Browser Camera Security (HTTPS Requirement)**:
> Modern mobile browsers (iOS Safari, Android Chrome) require a secure context (`https://` or `localhost`) to access camera hardware via `getUserMedia`.
> * When testing locally on the same laptop: `http://localhost:5173/scanner` works natively.
> * When connecting a real phone over local Wi-Fi (`http://192.168.x.x:5173`):
>   1. Enable Chrome flag on phone: navigate to `chrome://flags/#unsafely-treat-insecure-origin-as-secure`, enter `http://<YOUR_LAN_IP>:5173`, toggle **Enabled**, and restart Chrome.
>   2. Alternatively, run local HTTPS using tools like `ngrok http 5173` or `@vitejs/plugin-basic-ssl`.

---

### 1-Click Launch (Windows)
Double-click `run_local.bat` or run:
```powershell
.\run_local.ps1
```
This automatically verifies `uv`, syncs the `.venv` environment if needed, and launches both backend (`http://localhost:8000`) and frontend (`http://localhost:5173`) concurrently.

---

### Application Access Points
* **Frontend App**: [http://localhost:5173](http://localhost:5173)
* **Backend API**: [http://localhost:8000/api/](http://localhost:8000/api/)
* **Django Admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
* **Default Demo Login**: `admin` / `admin123`

---

## Deploying to Cloud (Docker Compose)

The repository includes production-ready Docker configurations:

```powershell
# Build and run complete stack (DB + Django + React)
docker compose up -d --build
```
