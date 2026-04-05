# OpenClaw Frontend (PoC)

This is a minimal Vue 3 + Vite frontend scaffold for OpenClaw.

Quick start (from repository root):

```bash
cd frontend
npm install
npm run dev
```

Dev server proxies `/api` to `http://localhost:8000` (see vite.config.ts).

Notes:
- This scaffold assumes the backend provides the endpoints described in the project plan (`/api/v1/skills`, `/api/v1/skills/upload`, `/api/v1/audits/run`, `/api/v1/audits/{id}`, `/api/v1/reports/{id}`).
- If backend is not available, some pages will show errors; consider adding mock adapters for offline dev.
