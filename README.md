# InternAI

InternAI is an AI-powered internship and job discovery platform for software engineering students. It automatically scrapes jobs, analyzes your resume via AI, provides a fit score, and tracks your applications using a Kanban board.

## Tech Stack
*   **Frontend**: Next.js 15 (App Router), Tailwind CSS, shadcn/ui
*   **Backend**: FastAPI, Python 3.12+
*   **Database & Auth**: Supabase (PostgreSQL)
*   **AI**: Groq API (Llama 3 8b) + Instructor
*   **Scraping**: Playwright

## Setup for Local Development

### Prerequisites
*   Node.js (for frontend)
*   Python 3.12+ (for backend)
*   Docker (Optional, for running backend via compose)

### 1. Supabase Setup
1. Create a [Supabase](https://supabase.com) project.
2. Go to the SQL Editor and run the queries found in `backend/database/schema.sql`.
3. Go to Storage and create a new public bucket named `resumes`.

### 2. Environment Variables
Create `.env.local` inside `frontend/`:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Create `.env` inside `backend/`:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
GROQ_API_KEY=your_groq_api_key
```

### 3. Running Locally

**Backend**:
You can run the backend via Docker Compose:
```bash
docker-compose up --build
```
*Or locally with Python*:
```bash
cd backend
pip install -r requirements.txt
playwright install --with-deps chromium
fastapi run main.py --port 8000 --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000` to view the application!

## Deployment (Free Tier)
*   **Frontend**: Push to GitHub and deploy via Vercel. Next.js App Router will be auto-detected.
*   **Backend**: Push to GitHub and link to Render.com using the provided `render.yaml` file (Docker deployment).
*   **Scraping**: GitHub Actions will automatically run `backend/scrapers/run.py` every day at 8:00 AM UTC to keep jobs fresh. Remember to add your Supabase keys to your GitHub Repo Secrets!
