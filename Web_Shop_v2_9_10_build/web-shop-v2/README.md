# Web Shop v2 — Premium Build

Web Shop is the parent ecosystem. DOOM AI is the flagship product. Webnor is the public website guide. DOOM internals remain outside this repository and are owned by Codex.

## Run
1. Install Docker Desktop.
2. From this directory run `docker compose up --build`.
3. Open http://localhost:3000.
4. Backend health: http://localhost:8000/api/health.

## Environment
Copy backend `.env.example` to your deployment environment. Never commit API keys. `WEBNOR_OPENROUTER_KEY` is optional; without it Webnor uses a bounded local fallback response system.

## Architecture
- Frontend: Next.js / React / TypeScript
- Backend: FastAPI / Python
- PostgreSQL: users, contact inquiries, Webnor usage and future commerce/content entities
- Redis: reserved for sessions/cache/queues
- Webnor: `/api/webnor/chat`
- DOOM integration boundary: intentionally separate; no DOOM provider/model implementation is included.

## v2 quality pass
- DOOM-first public hierarchy
- Deep charcoal + controlled ambient blue illumination
- DOOM green/black identity
- Section-specific motion language
- Dedicated capability pages
- Contact persistence
- Auth + profile/dashboard foundation
- Responsive layouts
- Native Webnor component with navigation actions
- Production-oriented container topology

## Production hardening still required before launch
Configure real OAuth/OTP, email delivery, Razorpay, object storage, Redis-backed rate limiting, secret management, CSRF/session strategy, database migrations, structured logging, monitoring, CSP, and deployment domains. DOOM's actual API is integrated only after Codex exposes the agreed contract.
