from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Agent
from app.game.codebreaker import generate_mission, check_answer

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        codename = request.form.get('codename', '').strip()
        password = request.form.get('password', '')

        if not codename or not password:
            flash('Codename and password required.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        if Agent.query.filter_by(codename=codename).first():
            flash('Codename already in use. Choose another.', 'error')
            return render_template('register.html')

        agent = Agent(codename=codename)
        agent.set_password(password)
        db.session.add(agent)
        db.session.commit()

        flash('Agent registered. Proceed to authentication.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        codename = request.form.get('codename', '').strip()
        password = request.form.get('password', '')

        agent = Agent.query.filter_by(codename=codename).first()
        if agent and agent.check_password(password):
            login_user(agent)
            return redirect(url_for('main.dashboard'))

        flash('Invalid credentials. Access denied.', 'error')

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', agent=current_user)


@bp.route('/mission/infiltration')
@login_required
def infiltration():
    return render_template('infiltration.html', agent=current_user)


@bp.route('/mission/hack')
@login_required
def hack():
    return render_template('hack.html', agent=current_user)


@bp.route('/mission/extraction')
@login_required
def extraction():
    return render_template('extraction.html', agent=current_user)


@bp.route('/mission/codebreaker', methods=['GET', 'POST'])
@login_required
def codebreaker():
    if 'current_mission' not in session:
        session['current_mission'] = generate_mission()

    mission = session['current_mission']
    result = None
    message = ""

    if request.method == 'POST':
        guess = request.form.get('guess', '')
        if check_answer(guess, mission['answer']):
            result = 'success'
            message = "CODE CRACKED! +50 XP AWARDED."
            current_user.xp += 50
            db.session.commit()
            session.pop('current_mission')
        else:
            result = 'failure'
            message = "ACCESS DENIED. INCORRECT CODE."

    return render_template('codebreaker.html', mission=mission, result=result, message=message)


# ==========================================
# === XP AWARD API ENDPOINT (NEW) ===
# ==========================================
@bp.route('/api/award-xp', methods=['POST'])
@login_required
def award_xp():
    data = request.get_json()
    amount = data.get('amount', 0)

    if amount > 0:
        current_user.xp += amount

        # Check for rank up
        thresholds = {'Recruit': 100, 'Operative': 300, 'Specialist': 600, 'Elite': 1000}
        if current_user.rank != 'Phantom':
            current_threshold = thresholds.get(current_user.rank)
            if current_threshold and current_user.xp >= current_threshold:
                ranks = ['Recruit', 'Operative', 'Specialist', 'Elite', 'Phantom']
                idx = ranks.index(current_user.rank)
                current_user.rank = ranks[idx + 1]

        db.session.commit()
        return jsonify({'status': 'success', 'new_xp': current_user.xp, 'new_rank': current_user.rank})

    return jsonify({'status': 'error', 'message': 'Invalid amount'}), 400