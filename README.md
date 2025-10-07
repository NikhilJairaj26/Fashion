# GlamDiva — Personal Styler and Wardrobe

A Flask web app to organize a personal wardrobe with photos and deliver color guidance based on undertone, occasion, and seasonal analysis.

## Project Structure

The project is organized into the following directories:

- `backend/` → Flask app files:
  - `app.py` (routes for auth, wardrobe CRUD, Personal Styler, Colour Analysis)
  - `models.py` (SQLAlchemy: `User`, `UserProfile`, `WardrobeItem`)
  - `requirements.txt` (dependencies)
- `templates/` → Jinja2 pages:
  - `index.html`, `login.html`, `signup.html`, `profile.html`, `edit-profile.html`
  - `wardrobe.html` (CRUD + image uploads)
  - `personal-styler.html` (preferences, suggestions, palette chips)
  - `colour-analysis.html` (seasonal palette and matches)
- `static/uploads/` → stored item images (created at runtime)
- `scripts/` → optional helpers (e.g., seeding, checks; add as needed)

## Features

### Backend

- **Auth & Sessions**: Secure login/logout with Flask-Login; per-user data isolation.
- **Wardrobe CRUD**: Add, search, filter, sort, delete items; image uploads with secure filenames.
- **Personal Styler**: Save skin tone, undertone, eye/hair color, occasion; show undertone + occasion suggestions and color chips.
- **Colour Analysis**: Infer season (Winter/Summer/Spring/Autumn) from undertone + contrast; curated neutrals/accents/avoid; highlight matching wardrobe items.

### Frontend

- **Responsive UI**: Clean pages and bottom navigation for Home, Wardrobe, Colors, Profile.
- **Palette Chips**: Render small hex palettes as colored chips for quick cues.
- **Thumbnails**: Show uploaded images inline with wardrobe items.

## Getting Started

### Prerequisites

- **Python**: 3.11+ recommended
- **Pip or Conda**: for dependencies

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   ```
2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1   # Windows PowerShell
   # or
   source .venv/bin/activate      # macOS/Linux
   ```
3. **Install dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```
4. **Create uploads folder (if missing):**
   ```bash
   mkdir -p static/uploads        # macOS/Linux
   # Windows PowerShell:
   # New-Item -ItemType Directory -Force -Path .\static\uploads | Out-Null
   ```

### Running the Project

1. **Run the backend server:**
   ```bash
   python app.py
   ```
2. **Open the app:**
   - http://127.0.0.1:5000

## Scripts

Add optional scripts as your workflow grows:
- `seed_database.py` → seed sample users/items
- `test_palette.py` → validate palette mappings
- `export_items.py` → export wardrobe items to CSV/JSON

Made by NJ
