from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Course
import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso restrito a administradores.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


@courses_bp.route('/')
@login_required
def list_courses():
    if current_user.role == 'admin':
        courses = Course.query.filter_by(user_id=current_user.id).order_by(Course.created_at.desc()).all()
    else:
        courses = Course.query.filter_by(is_published=True).order_by(Course.created_at.desc()).all()
    return render_template('courses/list.html', courses=courses)


@courses_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_course():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        is_published = request.form.get('is_published') == 'on'

        if not title:
            flash('O título é obrigatório.', 'error')
            return render_template('courses/form.html', course=None)

        cover_image = None
        file = request.files.get('cover_image')
        if file and file.filename and allowed_image(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"cover_{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            cover_image = filename

        course = Course(title=title, description=description,
                        is_published=is_published, cover_image=cover_image,
                        user_id=current_user.id)
        db.session.add(course)
        db.session.commit()
        flash('Curso criado com sucesso!', 'success')
        return redirect(url_for('courses.view_course', course_id=course.id))

    return render_template('courses/form.html', course=None)


@courses_bp.route('/<int:course_id>')
@login_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    if not course.is_published and (current_user.role != 'admin' or course.user_id != current_user.id):
        flash('Este curso não está disponível.', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('courses/view.html', course=course)


@courses_bp.route('/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        flash('Você não tem permissão para editar este curso.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        course.title = request.form.get('title', '').strip()
        course.description = request.form.get('description', '').strip()
        course.is_published = request.form.get('is_published') == 'on'

        file = request.files.get('cover_image')
        if file and file.filename and allowed_image(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"cover_{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            course.cover_image = filename

        db.session.commit()
        flash('Curso atualizado com sucesso!', 'success')
        return redirect(url_for('courses.view_course', course_id=course.id))

    return render_template('courses/form.html', course=course)


@courses_bp.route('/<int:course_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        flash('Você não tem permissão para excluir este curso.', 'error')
        return redirect(url_for('main.dashboard'))
    db.session.delete(course)
    db.session.commit()
    flash('Curso excluído com sucesso.', 'success')
    return redirect(url_for('main.dashboard'))
