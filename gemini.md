# Weeks Until Diploma - Project Overview

## Project Description
A web application for student motivation that visualizes the number of weeks remaining until the diploma defense through an interactive grid.

## Core Objective
To provide a visual tool that helps students realize the limited time left and motivates them to work regularly on their diploma.

## Tech Stack (Updated)
- **Frontend**: Vue.js 3 (Composition API, Vite, Tailwind CSS)
- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL (SQLAlchemy or Tortoise ORM)
- **State Management**: Pinia (for Vue)
- **Authentication**: JWT-based (FastAPI Users or custom implementation)

## Key Features
1. **Interactive Week Grid**: A grid where each square represents one week (Default: Jan 2026 - May 2027).
2. **User Profiles**: Simple registration with a personal emoji.
3. **Progress Marking**: Clicking a square allows marking it as "completed" with the user's emoji and an optional note.
4. **Special Periods**: Ability to mark weeks as Vacation or Business Trip (different colors).
5. **Dynamic Settings**: Custom start dates, deadlines, and emoji changes.

## Architectural Notes
- **Mobile-First**: The UI must be optimized for mobile devices (320px+).
- **Responsive Grid**: The week squares should adapt to screen size (32px to 48px).
- **API-First**: Clear separation between the FastAPI backend and Vue.js frontend.

## Roadmap Highlights
- **Phase 1**: Infrastructure & Database Schema (PostgreSQL).
- **Phase 2**: FastAPI Backend (Auth, User Profile, Weeks API).
- **Phase 3**: Vue.js Frontend (Grid visualization, Auth integration).
- **Phase 4**: Polish & Special Periods logic.
