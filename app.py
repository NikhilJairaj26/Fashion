from collections import Counter
import os
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import desc, or_, func
from config import Config
from models import db, User, WardrobeItem, UserProfile

# -----------------------------
# App Factory
# -----------------------------
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init DB
    db.init_app(app)

    # Init Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # Create tables and seed demo user (DEV-ONLY)
    with app.app_context():
        db.create_all()
        ensure_demo_user()  # DEV-ONLY: remove before production

    return app

# -----------------------------
# DEV-ONLY helper (remove later)
# -----------------------------
def ensure_demo_user():
    email = 'demo@glamdiva.dev'
    if not User.query.filter_by(email=email).first():
        u = User(name='Demo User', email=email)
        u.set_password('demo123')
        db.session.add(u)
        db.session.commit()

# Build the app instance
app = create_app()

# -----------------------------
# Uploads configuration
# -----------------------------
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -----------------------------
# DEV-ONLY route (remove later)
# -----------------------------
@app.route('/dev-login')
def dev_login():
    user = User.query.filter_by(email='demo@glamdiva.dev').first()
    if not user:
        return 'Demo user not found. Restart app to auto-create it.', 404
    login_user(user)
    return redirect(url_for('index'))

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('All fields are required!', 'error')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('signup.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered! Please login.', 'error')
            return render_template('signup.html')

        try:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required!', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    name = current_user.name
    logout_user()
    flash(f'Goodbye, {name}! You have been logged out.', 'info')
    return redirect(url_for('login'))

# -----------------------------
# Profile
# -----------------------------
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()

        if not name:
            flash('Name cannot be empty.', 'error')
            return render_template('edit-profile.html', user=current_user)

        current_user.name = name

        if password or confirm:
            if len(password) < 6:
                flash('Password must be at least 6 characters.', 'error')
                return render_template('edit-profile.html', user=current_user)
            if password != confirm:
                flash('Passwords do not match.', 'error')
                return render_template('edit-profile.html', user=current_user)
            current_user.set_password(password)

        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('profile'))
        except Exception:
            db.session.rollback()
            flash('Failed to update profile. Please try again.', 'error')
            return render_template('edit-profile.html', user=current_user)

    return render_template('edit-profile.html', user=current_user)

# -----------------------------
# Wardrobe (with image upload)
# -----------------------------
@app.route('/wardrobe', methods=['GET', 'POST'])
@login_required
def wardrobe():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        color = request.form.get('color', '').strip()
        notes = request.form.get('notes', '').strip()

        # File handling
        image_url = None
        file = request.files.get('image')
        if file and file.filename:
            if allowed_file(file.filename):
                fname = secure_filename(file.filename)
                base, ext = os.path.splitext(fname)
                # unique filename per user + timestamp
                fname = f"{current_user.id}_{base}_{int(__import__('time').time())}{ext.lower()}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                file.save(save_path)
                image_url = f"/static/uploads/{fname}"
            else:
                flash('Unsupported image format. Allowed: png, jpg, jpeg, gif, webp.', 'error')
                return redirect(url_for('wardrobe'))

        if not name or not category:
            flash('Name and category are required.', 'error')
        else:
            try:
                item = WardrobeItem(
                    user_id=current_user.id,
                    name=name,
                    category=category,
                    color=color or None,
                    notes=notes or None,
                    image_url=image_url
                )
                db.session.add(item)
                db.session.commit()
                flash('Item added to wardrobe.', 'success')
                return redirect(url_for('wardrobe'))
            except Exception:
                db.session.rollback()
                flash('Failed to add item. Please try again.', 'error')

    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'newest')

    query = WardrobeItem.query.filter_by(user_id=current_user.id)
    if category:
        query = query.filter(WardrobeItem.category == category)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(WardrobeItem.name.ilike(like), WardrobeItem.notes.ilike(like)))

    if sort == 'name':
        query = query.order_by(WardrobeItem.name.asc())
    else:
        query = query.order_by(desc(WardrobeItem.created_at))

    items = query.all()
    return render_template('wardrobe.html', items=items, q=q, category=category, sort=sort)

@app.route('/wardrobe/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_wardrobe_item(item_id):
    item = WardrobeItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        flash('Item not found or not authorized.', 'error')
        return redirect(url_for('wardrobe'))
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted.', 'success')
    except Exception:
        db.session.rollback()
        flash('Failed to delete item.', 'error')
    return redirect(url_for('wardrobe'))

# -----------------------------
# Personal Styler (with Occasion)
# -----------------------------
@app.route('/personal-styler', methods=['GET', 'POST'])
@login_required
def personal_styler():
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    errors = []
    saved = False

    if request.method == 'POST':
        skin_tone = request.form.get('skin_tone', '').strip() or None
        undertone = request.form.get('undertone', '').strip() or None
        eye_color = request.form.get('eye_color', '').strip() or None
        hair_color = request.form.get('hair_color', '').strip() or None
        occasion = request.form.get('occasion', '').strip() or None

        if undertone and undertone not in ['cool', 'warm', 'neutral']:
            errors.append('Undertone must be one of cool, warm, neutral.')

        allowed_occasions = ['work','casual','party','wedding','festive','sports','custom']
        if occasion and occasion not in allowed_occasions:
            errors.append('Occasion is invalid.')

        if not errors:
            profile.skin_tone = skin_tone
            profile.undertone = undertone
            profile.eye_color = eye_color
            profile.hair_color = hair_color
            profile.occasion = occasion
            try:
                db.session.commit()
                saved = True
                flash('Personal Styler preferences saved.', 'success')
            except Exception:
                db.session.rollback()
                flash('Failed to save preferences.', 'error')

    undertone_map = {
        'cool': ['jewel tones', 'blue', 'emerald', 'amethyst', 'cool gray', 'crisp white'],
        'warm': ['earth tones', 'olive', 'mustard', 'rust', 'camel', 'ivory'],
        'neutral': ['soft pastels', 'taupe', 'peach', 'mauve', 'balanced grays', 'off-white'],
        None: []
    }

    occasion_map = {
        'work': ['navy', 'charcoal', 'white', 'muted blue'],
        'casual': ['denim', 'olive', 'beige', 'white'],
        'party': ['metallic', 'deep red', 'emerald', 'black'],
        'wedding': ['pastel', 'champagne', 'ivory', 'soft pink'],
        'festive': ['gold', 'maroon', 'royal blue', 'bottle green'],
        'sports': ['black', 'electric blue', 'neon accents'],
        'custom': []
    }

    base_sugs = undertone_map.get(profile.undertone, [])
    extra_sugs = occasion_map.get(profile.occasion, []) if profile.occasion else []
    undertone_suggestions = base_sugs + extra_sugs

    palette_map = {
        'cool': ['#0f52ba', '#50c7f2', '#6a0dad', '#2f4f4f', '#ffffff'],
        'warm': ['#b5651d', '#c19a6b', '#556b2f', '#8b4513', '#fffff0'],
        'neutral': ['#e6e0d4', '#d8bfd8', '#f5deb3', '#708090', '#f8f8ff'],
        None: []
    }
    palette = palette_map.get(profile.undertone, [])

    q_items = WardrobeItem.query.filter_by(user_id=current_user.id)
    items_latest = q_items.order_by(WardrobeItem.created_at.desc()).limit(6).all()

    keywords = {
        'cool': ['blue', 'navy', 'emerald', 'purple', 'amethyst', 'grey', 'gray', 'white'],
        'warm': ['brown', 'tan', 'beige', 'mustard', 'olive', 'rust', 'camel', 'ivory'],
        'neutral': ['taupe', 'peach', 'mauve', 'pastel', 'gray', 'grey', 'off-white']
    }
    match_words = keywords.get(profile.undertone, [])[:]

    occ_keywords = {
        'work': ['blazer','shirt','trouser','formal','office'],
        'casual': ['tee','t-shirt','jeans','hoodie','sneaker','casual'],
        'party': ['sequin','dress','bodycon','heels','party'],
        'wedding': ['sherwani','lehenga','sari','gown','pastel','wedding'],
        'festive': ['kurta','ethnic','embroidery','gold','festive'],
        'sports': ['track','jersey','shorts','sweat','sport'],
        'custom': []
    }
    if profile.occasion:
        match_words += occ_keywords.get(profile.occasion, [])

    picks = []
    if match_words:
        like_filters = []
        for w in match_words:
            like = f'%{w}%'
            like_filters.extend([
                WardrobeItem.color.ilike(like),
                WardrobeItem.notes.ilike(like),
                WardrobeItem.category.ilike(like)
            ])
        or_expr = or_(*like_filters) if like_filters else None
        if or_expr is not None:
            picks = (
                q_items.filter(or_expr)
                .order_by(WardrobeItem.created_at.desc())
                .limit(6).all()
            )

    return render_template(
        'personal-styler.html',
        profile=profile,
        saved=saved,
        errors=errors,
        undertone_suggestions=undertone_suggestions,
        palette=palette,
        wardrobe_picks=picks if picks else items_latest
    )

# -----------------------------
# Colour Analysis
# -----------------------------
@app.route('/colour-analysis')
@login_required
def colour_analysis():
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()

    undertone = (profile.undertone.lower() if profile and profile.undertone else None)
    skin_tone = (profile.skin_tone.lower() if profile and profile.skin_tone else None)
    eye = (profile.eye_color.lower() if profile and profile.eye_color else None)
    hair = (profile.hair_color.lower() if profile and profile.hair_color else None)

    def season_from(ut, st, eye_c, hair_c):
        if not ut:
            return None
        cool = (ut == 'cool')
        warm = (ut == 'warm')
        neutral = (ut == 'neutral')
        high_contrast = False
        if st and hair_c:
            light_skin = any(k in st for k in ['very fair','fair','light','light-medium'])
            dark_hair = any(k in hair_c for k in ['black','dark','deep'])
            high_contrast = light_skin and dark_hair
        if cool:
            return 'Winter' if high_contrast else 'Summer'
        if warm:
            return 'Spring' if high_contrast else 'Autumn'
        if neutral:
            return 'Winter' if high_contrast else 'Autumn'
        return None

    season = season_from(undertone, skin_tone, eye, hair)

    PALETTES = {
        'Winter': {
            'neutrals': ['#000000','#2F4F4F','#FFFFFF','#C0C0C0'],
            'accents':  ['#0F52BA','#228B22','#800080','#DC143C'],
            'avoid':    ['#C19A6B','#DAA520','#8B4513']
        },
        'Summer': {
            'neutrals': ['#708090','#D3D3D3','#F8F8FF','#C0C0C0'],
            'accents':  ['#87CEFA','#6A5ACD','#3CB371','#DB7093'],
            'avoid':    ['#8B4513','#B5651D','#FF8C00']
        },
        'Spring': {
            'neutrals': ['#FFF8DC','#F5F5DC','#C19A6B','#8B4513'],
            'accents':  ['#FFD700','#FF8C00','#32CD32','#FF69B4'],
            'avoid':    ['#808080','#4B0082','#2F4F4F']
        },
        'Autumn': {
            'neutrals': ['#8B4513','#654321','#C19A6B','#F5DEB3'],
            'accents':  ['#556B2F','#B8860B','#A0522D','#CD5C5C'],
            'avoid':    ['#FFFFFF','#ADD8E6','#9370DB']
        }
    }
    palette = PALETTES.get(season, None)

    color_keywords = None
    if season == 'Winter':
        color_keywords = ['black','white','navy','emerald','crimson','purple','silver','gray','grey']
    elif season == 'Summer':
        color_keywords = ['slate','lavender','rose','mint','light blue','gray','grey','soft white']
    elif season == 'Spring':
        color_keywords = ['ivory','camel','beige','gold','lime','coral','peach','brown']
    elif season == 'Autumn':
        color_keywords = ['olive','mustard','rust','terracotta','tan','brown','warm beige']

    wardrobe_hits = []
    if color_keywords:
        like_filters = [WardrobeItem.color.ilike(f'%{w}%') for w in color_keywords]
        or_expr = or_(*like_filters) if like_filters else None
        if or_expr is not None:
            wardrobe_hits = (
                WardrobeItem.query.filter_by(user_id=current_user.id)
                .filter(WardrobeItem.color.isnot(None))
                .filter(or_expr)
                .order_by(WardrobeItem.created_at.desc())
                .limit(8).all()
            )

    return render_template(
        'colour-analysis.html',
        profile=profile,
        season=season,
        palette=palette,
        wardrobe_hits=wardrobe_hits
    )

# -----------------------------
# Error Handlers
# -----------------------------
@app.errorhandler(404)
def not_found_error(error):
    return '<h1>404 - Page Not Found</h1><a href="/">Go Home</a>', 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return '<h1>500 - Server Error</h1><a href="/">Go Home</a>', 500

# -----------------------------
# Main
# -----------------------------
if __name__ == '__main__':
    print('Starting GlamDiva...')
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
