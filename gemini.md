# Weeks Until Diploma - Project Overview

## 🌟 Vision
A minimalist, high-impact web application designed to motivate students by visualizing the finite nature of time. Each week is a square; each square is an opportunity.

## 🎯 Core Objectives
- **Visualize Time**: A grid representing the journey from start to diploma defense.
- **Micro-Progress**: Low-friction marking of weekly achievements.
- **Mindfulness**: Helping students stay aware of their timeline without overwhelming them.

## 🛠 Tech Stack
- **Backend**: FastAPI (Python 3.11+)
  - **ORM**: SQLAlchemy 2.0+ with Alembic for migrations.
  - **Validation**: Pydantic v2.
  - **Auth**: JWT-based (FastAPI Users or custom OAuth2 flow).
- **Frontend**: Vue.js 3 (Composition API, `<script setup>`)
  - **Build Tool**: Vite.
  - **Styling**: Tailwind CSS + Headless UI / Radix Vue.
  - **State**: Pinia.
  - **Icons**: Lucide Vue.
- **Database**: PostgreSQL.
- **Testing**: Pytest (Backend), Vitest (Frontend).

## 🏗 Project Structure (Proposed)
```text
diplom-monitor/
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes (v1)
│   │   ├── core/           # Config, security, constants
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic models
│   │   ├── services/       # Business logic
│   │   └── main.py         # Entry point
│   ├── migrations/         # Alembic migrations
│   └── tests/              # Pytest suite
├── frontend/               # Vue.js application
│   ├── src/
│   │   ├── api/            # Axios/Fetch clients
│   │   ├── components/     # UI Components (Atomic Design)
│   │   ├── composables/    # Reusable logic
│   │   ├── stores/         # Pinia stores
│   │   └── views/          # Page components
│   └── tests/              # Vitest suite
├── shared/                 # Shared constants/types (if applicable)
├── docker-compose.yml      # Local development environment
├── plan.md                 # Detailed development plan
└── gemini.md               # This project guide
```

## 📐 Standards & Conventions

### General Principles
- **KISS (Keep It Simple, Stupid)**: Avoid over-engineering. Use built-in solutions before adding libraries.
- **DRY (Don't Repeat Yourself)**: Extract common logic into services (backend) or composables (frontend).
- **Mobile-First**: Design and implement for small screens first (320px+).

### Backend (Python/FastAPI)
- **Style**: Follow **PEP 8**. Use **Black** for formatting and **Ruff** for linting.
- **Type Hints**: Mandatory for all function signatures and complex variables.
- **API Design**: RESTful principles. Use appropriate HTTP status codes.
- **Async**: Use `async/await` for I/O bound operations (DB, external APIs).

### Frontend (Vue/TS/JS)
- **Style**: Follow **Vue.js Style Guide**. Use **Prettier** and **ESLint**.
- **Composition API**: Use `<script setup>` syntax exclusively.
- **Components**: Small, single-responsibility components. Use Tailwind for all styling.
- **Props/Emits**: Clearly define props and emitted events.

## 🗄 Database Schema (Draft)

### Users
- `id`: UUID (PK)
- `email`: String (Unique)
- `hashed_password`: String
- `full_name`: String
- `emoji`: String (Default user icon)
- `settings`: JSONB (start_date, deadline_date, theme, etc.)

### WeekProgress
- `id`: UUID (PK)
- `user_id`: UUID (FK)
- `week_index`: Integer (Calculated from start_date)
- `is_completed`: Boolean
- `note`: Text (Optional)
- `updated_at`: Timestamp

### SpecialPeriods
- `id`: UUID (PK)
- `user_id`: UUID (FK)
- `start_date`: Date
- `end_date`: Date
- `type`: Enum (vacation, work, sick, etc.)
- `label`: String

## 🚀 Roadmap Highlights
1. **Phase 1: Foundation**: Project scaffolding, Docker setup, Auth boilerplate.
2. **Phase 2: Core Grid**: Backend week calculation logic + Frontend grid rendering.
3. **Phase 3: Interaction**: Marking weeks, adding notes, syncing with DB.
4. **Phase 4: Personalization**: Profile settings, custom dates, emoji picker.
5. **Phase 5: Polish**: Animations, PWA support, accessibility audit.

---
*Note: This document is the primary source of truth for AI agents. When in doubt, prioritize these instructions over general knowledge.*