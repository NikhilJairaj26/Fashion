# GlamDiva — Flask Wardrobe, Styler, and Colour Analysis

GlamDiva is a Flask-based web app that helps store wardrobe items, manage a personal style profile, and get color guidance through an undertone-aware personal styler and a dedicated colour analysis page.

## Features
- Authentication and profiles
  - Sign up, log in/out, edit profile (name and optional password).
  - Development helper login for quick testing.
- Wardrobe management
  - Add, filter, sort, edit, and delete items with name, category, color, notes.
- Personal Styler
  - Save preferences: skin tone (picker), undertone (picker), eye and hair color.
  - Undertone-based suggestions and color palette chips.
  - Quick picks from wardrobe by undertone color keywords.
- Colour Analysis
  - Seasonal inference (Winter, Summer, Spring, Autumn) from saved profile.
  - Curated palettes (neutrals, accents, avoid) with chips.
  - Client-side generator as fallback when profile data is missing.
- Consistent UI
  - Card layout, bottom navigation, accessible labels, and flash messages.

## Tech Stack
- Python, Flask, Flask-Login, Flask‑SQLAlchemy
- HTML/CSS with lightweight JavaScript
- Optional: Flask‑WTF for CSRF protection

## Project Structure (key files)
- `app.py` — Flask routes and app factory
- `models.py` — SQLAlchemy models (User, UserProfile, WardrobeItem)
- `config.py` — configuration (SECRET_KEY, SQLALCHEMY_DATABASE_URI, etc.)
- `requirements.txt` — pinned dependencies
- `templates/`
  - `index.html`
  - `login.html`, `signup.html`
  - `profile.html`, `edit-profile.html`
  - `wardrobe.html`, `wardrobe-edit.html`
  - `personal-styler.html`
  - `colour-analysis.html`
- `static/` (optional)
  - `css/base.css` (shared styles if extracted)

## Setup

### Option A: Global/base environment
- Install all dependencies using the provided requirements file:
  - `pip install -r requirements.txt`
- (Optional) Verify Flask import:
  - `python -c "import flask; print(flask.__version__, flask.__file__)"`

### Option B: Virtual environment (recommended but optional)
- Windows PowerShell:
  - `python -m venv .venv`
  - `.\\.venv\\Scripts\\Activate.ps1`
  - `pip install -r requirements.txt`

### Configure environment
- Ensure `config.py` defines:
  - `SECRET_KEY`
  - `SQLALCHEMY_DATABASE_URI` (e.g., `sqlite:///glamdiva.db`)
  - `SQLALCHEMY_TRACK_MODIFICATIONS = False`

### Initialize and run
- `python app.py`
- Visit `http://127.0.0.1:5000/`
- For quick testing during development, visit `/dev-login` to use the demo user.

## Core Routes
- `/` — home (requires login)
- `/signup` — create account
- `/login` — log in
- `/logout` — log out
- `/dev-login` — development-only quick login
- `/profile` — view profile
- `/profile/edit` — update name and optionally password
- `/wardrobe` — list/add with filters and sorting
- `/wardrobe/edit/<id>` — edit an item (GET/POST)
- `/wardrobe/delete/<id>` — delete (POST)
- `/personal-styler` — save preferences and see undertone-based suggestions/palette/picks
- `/colour-analysis` — see seasonal palette and wardrobe matches

## Key Behaviors
- Wardrobe
  - Filter by category and search by name/notes.
  - Sort by newest or name.
  - Each row has Edit and Delete actions.
- Personal Styler
  - Skin tone and undertone are pickers; eye/hair are free text.
  - Suggestions and color chips change with undertone.
  - Picks show recent or color‑matching items from the wardrobe.
- Colour Analysis
  - If undertone/skin tone are saved, the season is inferred and curated palettes render.
  - Otherwise, a client-side generator lets users explore palettes.


