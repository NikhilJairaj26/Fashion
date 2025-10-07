#GlamDiva — Personal Styler and Wardrobe
GlamDiva is a Flask-based web app that helps organize a personal wardrobe with photos and delivers color guidance based on undertone, occasion, and seasonal analysis. Users can add items with images, save style preferences, and see tailored suggestions and palettes.

Key features
Secure accounts with login/logout; each user sees only their own data.

Wardrobe management: add, search, filter, sort, delete; upload and view item images.

Personal Styler: save skin tone, undertone, eye/hair color, and occasion; get undertone + occasion-based suggestions and palette chips.

Colour Analysis: auto-detect seasonal type (Winter/Summer/Spring/Autumn) using a simple contrast heuristic; show curated neutrals, accents, and colors to avoid; surface wardrobe items that match the season.

Tech stack
Backend: Python, Flask, Flask-Login, SQLAlchemy

Templating/UI: Jinja2, HTML, CSS, light JavaScript

Storage: SQLite by default (switchable to PostgreSQL/MySQL), local image uploads in static/uploads

How it works (brief)
Personal Styler: preferences are stored per user; suggestions are picked from undertone maps and adjusted by occasion; small color palettes render as chips; wardrobe picks are filtered by keywords.

Colour Analysis: season is inferred from undertone and a light skin/dark hair contrast rule; each season maps to curated neutrals/accents/avoid sets; matching wardrobe items are highlighted.

Wardrobe: items are stored per user; search by text, filter by category, sort by newest/name; images are saved with secure, unique filenames.

Project structure (high level)
app.py: routes, auth, wardrobe CRUD, personal styler logic, colour analysis

models.py: User, UserProfile, WardrobeItem

templates/: HTML pages (wardrobe, personal-styler, colour-analysis, auth, profile)

static/uploads/: stored item images

Getting started (local)
Create/activate a Python environment.

Install dependencies: python -m pip install -r requirements.txt

Ensure static/uploads exists.

Run: python app.py and open http://127.0.0.1:5000

Roadmap
Smarter color matching from images (auto-tag colors).

Pagination and bulk actions in Wardrobe.

Cloud storage for images; production WSGI and HTTPS.

API endpoints and a mobile-friendly wrapper.
