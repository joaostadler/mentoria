from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'mentoria'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='estudante')  # 'admin' or 'estudante'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    courses = db.relationship('Course', backref='instructor', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'


course_access = db.Table('course_access',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    schema='mentoria'
)


class Course(db.Model):
    __tablename__ = 'courses'
    __table_args__ = {'schema': 'mentoria'}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(300))
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    topics = db.relationship('Topic', backref='course', lazy=True, cascade='all, delete-orphan', order_by='Topic.order')
    allowed_users = db.relationship('User', secondary=course_access, backref=db.backref('granted_courses', lazy='dynamic'))

    def __repr__(self):
        return f'<Course {self.title}>'

    @property
    def lessons_count(self):
        return sum(len(t.lessons) for t in self.topics)

    @property
    def topics_count(self):
        return len(self.topics)

    @property
    def access_count(self):
        return len(self.allowed_users)


class Topic(db.Model):
    __tablename__ = 'topics'
    __table_args__ = {'schema': 'mentoria'}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    lessons = db.relationship('Lesson', backref='topic', lazy=True, cascade='all, delete-orphan', order_by='Lesson.order')

    def __repr__(self):
        return f'<Topic {self.title}>'


class Lesson(db.Model):
    __tablename__ = 'lessons'
    __table_args__ = {'schema': 'mentoria'}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)

    materials = db.relationship('Material', backref='lesson', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Lesson {self.title}>'


class Material(db.Model):
    __tablename__ = 'materials'
    __table_args__ = {'schema': 'mentoria'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    original_filename = db.Column(db.String(300), nullable=False)
    file_type = db.Column(db.String(50))  # 'pdf', 'video', 'image', 'other'
    file_size = db.Column(db.Integer)  # bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)

    def __repr__(self):
        return f'<Material {self.name}>'

    @property
    def file_size_formatted(self):
        if not self.file_size:
            return 'N/A'
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.1f} {unit}'
            size /= 1024
        return f'{size:.1f} TB'

    @property
    def icon(self):
        icons = {
            'pdf': '📄',
            'video': '🎬',
            'image': '🖼️',
            'other': '📁'
        }
        return icons.get(self.file_type, '📁')
