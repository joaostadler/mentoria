from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, abort
from flask_login import login_required, current_user
from app import db
from app.models import Course, Topic, Lesson, Material
from flask import current_app
import os
import uuid

lessons_bp = Blueprint('lessons', __name__)

ALLOWED_EXTENSIONS = {
    'pdf': 'pdf',
    'mp4': 'video', 'avi': 'video', 'mov': 'video', 'mkv': 'video', 'webm': 'video',
    'png': 'image', 'jpg': 'image', 'jpeg': 'image', 'gif': 'image', 'webp': 'image',
    'doc': 'other', 'docx': 'other', 'ppt': 'other', 'pptx': 'other',
    'xls': 'other', 'xlsx': 'other', 'txt': 'other', 'zip': 'other'
}


def get_file_type(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ALLOWED_EXTENSIONS.get(ext, 'other')


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso restrito a administradores.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


@lessons_bp.route('/courses/<int:course_id>/topics/<int:topic_id>/lessons/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_lesson(course_id, topic_id):
    course = Course.query.get_or_404(course_id)
    topic = Topic.query.get_or_404(topic_id)

    if course.user_id != current_user.id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()

        if not title:
            flash('O título é obrigatório.', 'error')
            return render_template('lessons/form.html', course=course, topic=topic, lesson=None)

        order = db.session.query(db.func.max(Lesson.order)).filter_by(topic_id=topic_id).scalar() or 0
        lesson = Lesson(title=title, description=description, content=content,
                        topic_id=topic_id, order=order + 1)
        db.session.add(lesson)
        db.session.flush()

        # Handle file uploads
        files = request.files.getlist('materials')
        for file in files:
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                file.save(save_path)
                size = os.path.getsize(save_path)
                material = Material(
                    name=file.filename,
                    filename=unique_name,
                    original_filename=file.filename,
                    file_type=get_file_type(file.filename),
                    file_size=size,
                    lesson_id=lesson.id
                )
                db.session.add(material)

        db.session.commit()
        flash('Aula criada com sucesso!', 'success')
        return redirect(url_for('lessons.view_lesson', course_id=course_id, topic_id=topic_id, lesson_id=lesson.id))

    return render_template('lessons/form.html', course=course, topic=topic, lesson=None)


@lessons_bp.route('/courses/<int:course_id>/topics/<int:topic_id>/lessons/<int:lesson_id>')
@login_required
def view_lesson(course_id, topic_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    topic = Topic.query.get_or_404(topic_id)
    lesson = Lesson.query.get_or_404(lesson_id)

    if not course.is_published and (current_user.role != 'admin' or course.user_id != current_user.id):
        abort(403)

    return render_template('lessons/view.html', course=course, topic=topic, lesson=lesson)


@lessons_bp.route('/courses/<int:course_id>/topics/<int:topic_id>/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lesson(course_id, topic_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    topic = Topic.query.get_or_404(topic_id)
    lesson = Lesson.query.get_or_404(lesson_id)

    if course.user_id != current_user.id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        lesson.title = request.form.get('title', '').strip()
        lesson.description = request.form.get('description', '').strip()
        lesson.content = request.form.get('content', '').strip()

        files = request.files.getlist('materials')
        for file in files:
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                file.save(save_path)
                size = os.path.getsize(save_path)
                material = Material(
                    name=file.filename,
                    filename=unique_name,
                    original_filename=file.filename,
                    file_type=get_file_type(file.filename),
                    file_size=size,
                    lesson_id=lesson.id
                )
                db.session.add(material)

        db.session.commit()
        flash('Aula atualizada!', 'success')
        return redirect(url_for('lessons.view_lesson', course_id=course_id, topic_id=topic_id, lesson_id=lesson_id))

    return render_template('lessons/form.html', course=course, topic=topic, lesson=lesson)


@lessons_bp.route('/courses/<int:course_id>/topics/<int:topic_id>/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_lesson(course_id, topic_id, lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    db.session.delete(lesson)
    db.session.commit()
    flash('Aula excluída.', 'success')
    return redirect(url_for('courses.view_course', course_id=course_id))


@lessons_bp.route('/materials/<int:material_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    lesson = material.lesson
    topic = lesson.topic
    course = topic.course

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], material.filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(material)
    db.session.commit()
    flash('Material excluído.', 'success')
    return redirect(url_for('lessons.view_lesson',
                            course_id=course.id, topic_id=topic.id, lesson_id=lesson.id))


@lessons_bp.route('/uploads/<filename>')
@login_required
def serve_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
