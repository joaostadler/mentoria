from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Course

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            courses = Course.query.filter_by(user_id=current_user.id).all()
        else:
            courses = current_user.granted_courses.all()
        return render_template('main/dashboard.html', courses=courses)
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        courses = Course.query.filter_by(user_id=current_user.id).order_by(Course.created_at.desc()).all()
    else:
        courses = current_user.granted_courses.order_by(Course.created_at.desc()).all()
    return render_template('main/dashboard.html', courses=courses)
