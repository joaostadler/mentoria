from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Course, Topic

topics_bp = Blueprint('topics', __name__, url_prefix='/courses/<int:course_id>/topics')


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso restrito a administradores.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


@topics_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_topic(course_id):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            flash('O título é obrigatório.', 'error')
            return render_template('topics/form.html', course=course, topic=None)

        order = db.session.query(db.func.max(Topic.order)).filter_by(course_id=course_id).scalar() or 0
        topic = Topic(title=title, description=description, course_id=course_id, order=order + 1)
        db.session.add(topic)
        db.session.commit()
        flash('Tópico criado com sucesso!', 'success')
        return redirect(url_for('courses.view_course', course_id=course_id))

    return render_template('topics/form.html', course=course, topic=None)


@topics_bp.route('/<int:topic_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_topic(course_id, topic_id):
    course = Course.query.get_or_404(course_id)
    topic = Topic.query.get_or_404(topic_id)

    if course.user_id != current_user.id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        topic.title = request.form.get('title', '').strip()
        topic.description = request.form.get('description', '').strip()
        db.session.commit()
        flash('Tópico atualizado!', 'success')
        return redirect(url_for('courses.view_course', course_id=course_id))

    return render_template('topics/form.html', course=course, topic=topic)


@topics_bp.route('/<int:topic_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_topic(course_id, topic_id):
    topic = Topic.query.get_or_404(topic_id)
    db.session.delete(topic)
    db.session.commit()
    flash('Tópico excluído.', 'success')
    return redirect(url_for('courses.view_course', course_id=course_id))


@topics_bp.route('/reorder', methods=['POST'])
@login_required
@admin_required
def reorder_topics(course_id):
    data = request.get_json()
    for item in data.get('order', []):
        topic = Topic.query.get(item['id'])
        if topic and topic.course_id == course_id:
            topic.order = item['order']
    db.session.commit()
    return jsonify({'success': True})
