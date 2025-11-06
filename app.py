from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import login_required, current_user, login_user, LoginManager
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import User, Subject, Chapter, Quiz, Question, Score
from celery import Celery
from sqlalchemy import extract
from datetime import date
from flask import make_response
from models import db
from io import StringIO


app = Flask(__name__)
CORS(app, origins=["http://localhost:5175"], supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_app.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'akruti.pagar03@gmail.com'
app.config['MAIL_PASSWORD'] = 'kzst ykdo ssjo jpse'
app.config['MAIL_DEFAULT_SENDER'] = ('quiz app', 'akruti.pagar03@gmail.com')

app.config['broker_url'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

db.init_app(app)
mail = Mail(app)
login_manager = LoginManager(app)

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['broker_url'],
        backend=app.config['result_backend']
    )
    celery.conf.update(app.config)
    celery.conf.timezone = 'Asia/Kolkata'
    celery.conf.enable_utc = False

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='Admin').first():
        admin = User(
            username='Admin',
            password=generate_password_hash('akrutipagar'),
            fullname='Admin',
            qualification='Admin',
            role='admin',
            email='akruti.pagar03@gmail.com' 
        )
        db.session.add(admin)
        db.session.commit()


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'msg': 'Username already exists'}), 400
    user = User(
        username=data['username'],
        password=generate_password_hash(data['password']),
        fullname=data.get('fullname', ''),
        qualification=data.get('qualification', ''),
        role='user',
        email=data['email']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'Registration Done!!'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        login_user(user)  
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return jsonify({'msg': 'Login Done!!', 'role': user.role}), 200
    return jsonify({'msg': 'Invalid Login Again'}), 401


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    return jsonify({'msg': 'Welcome Admin', 'user': current_user.username})


@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return jsonify({'msg': 'Access denied'}), 403
    return jsonify({'msg': 'Welcome User', 'user': current_user.username})

@app.route('/admin/create_subjects', methods=['POST'])
@login_required
def create_subject():
    if current_user.role != 'admin':
       return jsonify({'msg': 'Access denied'}), 403
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    if not name:
        return jsonify({'msg': 'Please specify Subject name!'}), 400
    if Subject.query.filter_by(name=name).first():
        return jsonify({'msg': 'Subject already exists'}), 409
    new_subject = Subject(name=name, description=description)
    db.session.add(new_subject)
    db.session.commit()

    return jsonify({'msg': 'Subject successfully created'}), 201

@app.route('/admin/update_subjects/<int:subject_id>', methods=['PUT'])
@login_required
def update_subject(subject_id):
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    data = request.get_json()
    subject = Subject.query.get_or_404(subject_id)
    subject.name = data.get('name', subject.name)
    subject.description = data.get('description', subject.description)
    db.session.commit()
    return jsonify({'msg': 'Subject successfully updated'}), 200

@app.route('/admin/delete_subjects/<int:subject_id>', methods=['DELETE'])
@login_required
def delete_subject(subject_id):
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return jsonify({'msg': 'Subject successfully deleted'}), 200

@app.route('/admin/create_chapter/<int:subject_id>', methods=['POST'])
@login_required
def create_chapter(subject_id):
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    if not name:
        return jsonify({'msg': 'Chapter name is required'}), 400
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({'msg': 'Subject not found'}), 404
    chapter = Chapter(name=name, description=description, subject_id=subject_id)
    db.session.add(chapter)
    db.session.commit()
    return jsonify({'msg': 'Chapter created'}), 201

@app.route('/admin/update_chapters/<int:chapter_id>', methods=['PUT'])
@login_required
def update_chapter(chapter_id):
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    chapter = Chapter.query.get_or_404(chapter_id)
    data = request.get_json()
    chapter.name = data.get('name', chapter.name)
    chapter.description = data.get('description', chapter.description)
    db.session.commit()
    return jsonify({'msg': 'Chapter updated'}), 200

@app.route('/admin/delete_chapters/<int:chapter_id>', methods=['DELETE'])
@login_required
def delete_chapter(chapter_id):
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return jsonify({'msg': 'Chapter deleted successfully'}), 200


@app.route('/admin/create_quiz/<int:chapter_id>', methods=['POST'])
@login_required
def create_quiz(chapter_id):
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    data = request.get_json()
    quiz = Quiz(
        name=data['name'],
        description=data.get('description', ''),
        date_of_quiz=datetime.strptime(data['date_of_quiz'], "%Y-%m-%d").date(),
        time_duration=datetime.strptime(data['time_duration'], "%H:%M").time(),
        chapter_id=chapter_id
    )
    db.session.add(quiz)
    db.session.commit()
    return jsonify({"msg": "Quiz created "}), 201

@app.route("/admin/update_quizzes/<int:quiz_id>", methods=["PUT"])
@login_required
def update_quiz(quiz_id):
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    quiz.name = data.get("name", quiz.name)
    quiz.description = data.get("description", quiz.description)
    if "date_of_quiz" in data:
        try:
            quiz.date_of_quiz = datetime.strptime(data["date_of_quiz"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"msg": "Invalid format try again"}), 400
    if "time_duration" in data:
        try:
            quiz.time_duration = datetime.strptime(data["time_duration"], "%H:%M").time()
        except ValueError:
            return jsonify({"msg": "Invalid tRY AGAIN"}), 400
    db.session.commit()
    return jsonify({"msg": "Quiz updated"}), 200

@app.route('/admin/delete_quizzes/<int:quiz_id>', methods=['DELETE'])
@login_required
def delete_quiz(quiz_id):
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"msg": "Quiz not found"}), 404
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({"msg": "Quiz deleted "}), 200

@app.route('/admin/create_question/<int:quiz_id>', methods=['POST', 'OPTIONS'])
@login_required
def create_question(quiz_id):
    if request.method == 'OPTIONS':
        response = make_response()
        origin = request.headers.get("Origin")
        if origin == "http://localhost:5175":
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    required_fields = ['question_statement', 'option1', 'option2', 'correct_option']
    if not all(data.get(field) for field in required_fields):
        return jsonify({"msg": "Missing required fields"}), 400
    question = Question(
        quiz_id=quiz.id,
        question_statement=data['question_statement'],
        option1=data.get('option1'),
        option2=data.get('option2'),
        option3=data.get('option3'),
        option4=data.get('option4'),
        correct_option=data.get('correct_option')
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({
        "msg": "Question created",
        "question_id": question.id
    }), 201

@app.route('/admin/update_question/<int:question_id>', methods=['PUT'])
@login_required
def update_question(question_id):
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    question = Question.query.get_or_404(question_id)
    data = request.get_json()
    question.question_statement = data.get('question_statement', question.question_statement)
    question.option1 = data.get('option1', question.option1)
    question.option2 = data.get('option2', question.option2)
    question.option3 = data.get('option3', question.option3)
    question.option4 = data.get('option4', question.option4)
    question.correct_option = data.get('correct_option', question.correct_option)
    db.session.commit()
    return jsonify({'msg': 'Question successfully updated'}), 200

@app.route('/admin/delete_questions/<int:question_id>', methods=['DELETE'])
@login_required
def delete_question(question_id):
    if current_user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    if current_user.role != 'admin':
        return jsonify({'msg': 'Unauthorized'}), 403
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({'msg': 'Question deleted successfully'}), 200

@app.route('/subjects',methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    result = []
    for subject in subjects:
        chapters = []
        for chapter in subject.chapters:
            quizzes = []
            for quiz in chapter.quizzes:
                questions = [{
                    'id': i.id,
                    'question_statement': i.question_statement,
                    'option1': i.option1,
                    'option2': i.option2,
                    'option3': i.option3,
                    'option4': i.option4,
                    'correct_option': i.correct_option
                } for i in quiz.questions]
                quizzes.append({
                    'id': quiz.id,
                    'title': quiz.name,
                    'description': quiz.description,
                    'date_of_quiz': str(quiz.date_of_quiz),
                    'time_duration': str(quiz.time_duration),
                    'questions': questions
                })
            chapters.append({
                'id': chapter.id,
                'title': chapter.name,
                'content': chapter.description,
                'quizzes': quizzes
            })
        result.append({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'chapters': chapters
        })
    return jsonify({'subjects': result})


@app.route('/user/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    if current_user.role != 'user':
        return jsonify({'msg': 'Access denied'}), 403
    data = request.get_json()
    submitted_answers = data.get('answers', {})
    correct_count = 0
    total_questions = 0
    correct_answers = {}

    for question in Question.query.filter_by(quiz_id=quiz_id).all():
        total_questions += 1
        correct_answers[str(question.id)] = question.correct_option 
        selected = submitted_answers.get(str(question.id))
        if selected and selected.strip().lower() == question.correct_option.strip().lower():
            correct_count += 1
    score = (correct_count / total_questions) * 100 if total_questions else 0
    attempt = Score(
        quiz_id=quiz_id,
        user_id=current_user.id,
        total_score=score,
        total_questions=total_questions,
        correct_answers=correct_count
    )
    db.session.add(attempt)
    db.session.commit()
    return jsonify({
        'msg': 'Quiz submitted',
        'total_questions': total_questions,
        'correct': correct_count,
        'score': score,
        'correct_answers': correct_answers  
    }), 200


@app.route('/admin/users/scores')
@login_required
def user_scores():
    if current_user.role != 'admin':
        return jsonify({'msg': 'Unauthorized'}), 404
    users = User.query.all()
    result = []
    for user in users:
        scores = Score.query.filter_by(user_id=user.id).all()
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'scores': [{
                'quiz_id': score.quiz_id,
                'quiz_title': score.quiz.name,
                'total_score': score.total_score,
                'correct_answers': score.correct_answers,
                'total_questions': score.total_questions,
                'timestamp': score.time_stamp.isoformat()
            } for score in scores]
        }
        result.append(user_data)
    return jsonify({'users': result})


@app.route('/user/monthly-report', methods=['GET'])
@login_required
def send_monthly_reports():
    now = datetime.utcnow()
    user_id = current_user.id  
    user = User.query.get(user_id)
    submissions = Score.query.filter_by(user_id=user.id).filter(
        extract('month', Score.time_stamp) == now.month,
        extract('year', Score.time_stamp) == now.year
    ).all()

    if not submissions:
        if request.args.get("format") == "csv":
            response = make_response("Quiz Title,Date,Score (%),Correct Answers,Total Questions\n")
            response.headers["Content-Disposition"] = "attachment; filename=monthly_report.csv"
            response.headers["Content-type"] = "text/csv"
            return response
        else:
            return jsonify({"report": [], "total_quizzes": 0})
    report = []
    correct_sum = 0
    total_sum = 0

    for s in submissions:
        quiz = Quiz.query.get(s.quiz_id)
        score_percent = round((s.correct_answers / s.total_questions) * 100, 2)
        correct_sum += s.correct_answers
        total_sum += s.total_questions
        report.append({
            "quiz_title": quiz.name,
            "date": quiz.date_of_quiz.strftime('%Y-%m-%d'),
            "score": score_percent,
            "correct_answers": s.correct_answers,
            "questions": s.total_questions
        })

    if request.args.get("format") == "csv":
        csv_output = StringIO()
        csv_output.write('Quiz Title,Date,Score (%),Correct Answers,Total Questions\n')
        for item in report:
            csv_output.write(f"{item['quiz_title']},{item['date']},{item['score']},{item['correct_answers']},{item['total_questions']}\n")
        csv_output.seek(0)
        response = make_response(csv_output.read())
        response.headers["Content-Disposition"] = "attachment; filename=monthly_report.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    return jsonify({
        "report": report,
        "total_quizzes": len(submissions)
    })




@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'msg': 'Logged out successfully'})


if __name__ == '__main__':
    app.run(debug=True)
    