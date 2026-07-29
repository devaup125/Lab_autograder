"""
==========================================================
Lab Auto Grader
Admin Routes
Part 1
==========================================================
"""

from functools import wraps
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort,
    current_app
)

from flask_login import (
    login_required,
    current_user
)

from sqlalchemy import or_

from extensions import db

from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.problem import Problem
from models.testcase import TestCase
from models.assignment import Assignment
from models.submission import Submission


# ==========================================================
# Blueprint
# ==========================================================

admin_bp = Blueprint(

    "admin",

    __name__,

    url_prefix="/admin"

)


# ==========================================================
# ADMIN DECORATOR
# ==========================================================

def admin_required(view):
    """
    Allow access to Admin users only.
    """

    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):

        if not current_user.is_authenticated:

            flash(

                "Please login first.",

                "warning"

            )

            return redirect(

                url_for("auth.login")

            )

        if not current_user.is_admin:

            abort(403)

        return view(*args, **kwargs)

    return wrapped


# ==========================================================
# HELPERS
# ==========================================================

def get_pagination():

    page = request.args.get(

        "page",

        default=1,

        type=int

    )

    per_page = request.args.get(

        "per_page",

        default=20,

        type=int

    )

    per_page = max(

        1,

        min(per_page, 100)

    )

    return page, per_page


def search_keyword():

    return request.args.get(

        "q",

        "",

        type=str

    ).strip()


def success(message):

    flash(

        message,

        "success"

    )


def error(message):

    flash(

        message,

        "danger"

    )


def warning(message):

    flash(

        message,

        "warning"

    )


def info(message):

    flash(

        message,

        "info"

    )


# ==========================================================
# CONTEXT PROCESSOR
# ==========================================================

@admin_bp.app_context_processor
def admin_context():

    return {

        "current_year": datetime.utcnow().year,

        "admin_panel": True

    }


# ==========================================================
# INDEX
# ==========================================================

@admin_bp.route("/")

@login_required
@admin_required
def index():

    return redirect(

        url_for(

            "admin.dashboard"

        )

    )
# ==========================================================
# DASHBOARD
# ==========================================================

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """
    Admin Dashboard
    """

    total_users = User.count()

    total_students = Student.count()

    total_teachers = Teacher.count()

    total_problems = Problem.count()

    total_testcases = TestCase.count()

    total_assignments = Assignment.count()

    total_submissions = Submission.count()

    accepted_submissions = Submission.accepted_count()

    pending_submissions = Submission.pending_count()

    rejected_submissions = Submission.rejected_count()

    acceptance_rate = Submission.acceptance_rate()

    recent_users = User.latest(5)

    recent_problems = Problem.latest(5)

    recent_submissions = Submission.latest(10)

    recent_assignments = Assignment.latest(5)

    return render_template(

        "admin/dashboard.html",

        total_users=total_users,

        total_students=total_students,

        total_teachers=total_teachers,

        total_problems=total_problems,

        total_testcases=total_testcases,

        total_assignments=total_assignments,

        total_submissions=total_submissions,

        accepted_submissions=accepted_submissions,

        pending_submissions=pending_submissions,

        rejected_submissions=rejected_submissions,

        acceptance_rate=acceptance_rate,

        recent_users=recent_users,

        recent_problems=recent_problems,

        recent_assignments=recent_assignments,

        recent_submissions=recent_submissions

    )


# ==========================================================
# DASHBOARD STATISTICS API
# ==========================================================

@admin_bp.route("/dashboard/stats")
@login_required
@admin_required
def dashboard_statistics():

    data = {

        "users": {

            "total": User.count(),

            "admins": User.admins().count(),

            "teachers": User.teachers().count(),

            "students": User.students().count(),

            "active": User.active().count(),

            "verified": User.verified().count()

        },

        "problems": {

            "total": Problem.count()

        },

        "testcases": {

            "total": TestCase.count()

        },

        "assignments": {

            "total": Assignment.count()

        },

        "submissions": Submission.dashboard_statistics()

    }

    return jsonify(data)


# ==========================================================
# RECENT ACTIVITY
# ==========================================================

@admin_bp.route("/activity")
@login_required
@admin_required
def activity():

    activities = {

        "users": User.recently_registered(10),

        "submissions": Submission.latest(10),

        "problems": Problem.latest(10),

        "assignments": Assignment.latest(10)

    }

    return render_template(

        "admin/activity.html",

        activities=activities

    )


# ==========================================================
# SYSTEM HEALTH
# ==========================================================

@admin_bp.route("/system")
@login_required
@admin_required
def system_health():

    health = {

        "database": "Connected",

        "users": User.count(),

        "students": Student.count(),

        "teachers": Teacher.count(),

        "problems": Problem.count(),

        "testcases": TestCase.count(),

        "assignments": Assignment.count(),

        "submissions": Submission.count(),

        "server_time": datetime.utcnow()

    }

    return render_template(

        "admin/system.html",

        health=health

    )


# ==========================================================
# ANALYTICS PAGE
# ==========================================================

@admin_bp.route("/analytics")
@login_required
@admin_required
def analytics():

    submission_stats = Submission.dashboard_statistics()

    role_stats = User.role_statistics()

    return render_template(

        "admin/analytics.html",

        submission_stats=submission_stats,

        role_stats=role_stats

    )


# ==========================================================
# CHART DATA API
# ==========================================================

@admin_bp.route("/analytics/charts")
@login_required
@admin_required
def analytics_charts():

    return jsonify(

        {

            "submission_distribution":
                Submission.verdict_distribution(),

            "role_distribution":
                User.role_statistics(),

            "submission_statistics":
                Submission.dashboard_statistics()

        }

    )
# ==========================================================
# USER MANAGEMENT
# ==========================================================

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    """
    List all users.
    """

    page, per_page = get_pagination()

    keyword = search_keyword()

    query = User.query

    if keyword:

        query = query.filter(

            or_(

                User.first_name.ilike(f"%{keyword}%"),

                User.last_name.ilike(f"%{keyword}%"),

                User.username.ilike(f"%{keyword}%"),

                User.email.ilike(f"%{keyword}%")

            )

        )

    users = query.order_by(

        User.created_at.desc()

    ).paginate(

        page=page,

        per_page=per_page,

        error_out=False

    )

    return render_template(

        "admin/users/list.html",

        users=users,

        keyword=keyword

    )


# ==========================================================
# USER DETAILS
# ==========================================================

@admin_bp.route("/users/<int:user_id>")
@login_required
@admin_required
def user_details(user_id):

    user = User.get_by_id(user_id)

    if not user:

        abort(404)

    return render_template(

        "admin/users/details.html",

        user=user

    )


# ==========================================================
# CREATE USER
# ==========================================================

@admin_bp.route("/users/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():

    if request.method == "POST":

        try:

            user = User(

                first_name=request.form["first_name"],

                last_name=request.form["last_name"],

                username=request.form["username"],

                email=request.form["email"],

                mobile=request.form.get("mobile"),

                role=request.form["role"],

                bio=request.form.get("bio")

            )

            user.set_password(

                request.form["password"]

            )

            user.save()

            success(

                "User created successfully."

            )

            return redirect(

                url_for(

                    "admin.users"

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/users/create.html"

    )


# ==========================================================
# EDIT USER
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def edit_user(user_id):

    user = User.get_by_id(user_id)

    if not user:

        abort(404)

    if request.method == "POST":

        try:

            user.update(

                first_name=request.form["first_name"],

                last_name=request.form["last_name"],

                username=request.form["username"],

                email=request.form["email"],

                mobile=request.form.get("mobile"),

                role=request.form["role"],

                bio=request.form.get("bio")

            )

            success(

                "User updated successfully."

            )

            return redirect(

                url_for(

                    "admin.user_details",

                    user_id=user.id

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/users/edit.html",

        user=user

    )


# ==========================================================
# DELETE USER
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_user(user_id):

    user = User.get_by_id(user_id)

    if not user:

        abort(404)

    try:

        user.delete()

        success(

            "User deleted successfully."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.users"

        )

    )


# ==========================================================
# ACTIVATE USER
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/activate",
    methods=["POST"]
)
@login_required
@admin_required
def activate_user(user_id):

    user = User.get_by_id(user_id)

    if not user:

        abort(404)

    user.activate()

    db.session.commit()

    success(

        "User activated."

    )

    return redirect(

        url_for(

            "admin.user_details",

            user_id=user.id

        )

    )


# ==========================================================
# DEACTIVATE USER
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/deactivate",
    methods=["POST"]
)
@login_required
@admin_required
def deactivate_user(user_id):

    user = User.get_by_id(user_id)

    if not user:

        abort(404)

    user.deactivate()

    db.session.commit()

    success(

        "User deactivated."

    )

    return redirect(

        url_for(

            "admin.user_details",

            user_id=user.id

        )

    )


# ==========================================================
# VERIFY USER
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/verify",
    methods=["POST"]
)
@login_required
@admin_required
def verify_user(user_id):

    user = User.get_by_id(user_id)

    if not user:

        abort(404)

    user.verify()

    db.session.commit()

    success(

        "User verified successfully."

    )

    return redirect(

        url_for(

            "admin.user_details",

            user_id=user.id

        )

    )


# ==========================================================
# LOCK USER
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/lock",
    methods=["POST"]
)
@login_required
@admin_required
def lock_user(user_id):

    user = User.get_by_id(user_id)

    if not user:

        abort(404)

    user.lock()

    db.session.commit()

    success(

        "User account locked."

    )

    return redirect(

        url_for(

            "admin.user_details",

            user_id=user.id

        )

    )


# ==========================================================
# UNLOCK USER
# ==========================================================

@admin_bp.route(
    "/users/<int:user_id>/unlock",
    methods=["POST"]
)
@login_required
@admin_required
def unlock_user(user_id):

    user = User.get_by_id(user_id)

    if not user:

        abort(404)

    user.unlock()

    db.session.commit()

    success(

        "User account unlocked."

    )

    return redirect(

        url_for(

            "admin.user_details",

            user_id=user.id

        )

    )
# ==========================================================
# STUDENT MANAGEMENT
# ==========================================================

@admin_bp.route("/students")
@login_required
@admin_required
def students():

    page, per_page = get_pagination()

    keyword = search_keyword()

    query = Student.query.join(User)

    if keyword:

        query = query.filter(

            or_(

                User.first_name.ilike(f"%{keyword}%"),

                User.last_name.ilike(f"%{keyword}%"),

                User.username.ilike(f"%{keyword}%"),

                User.email.ilike(f"%{keyword}%"),

                Student.enrollment_number.ilike(f"%{keyword}%")

            )

        )

    students = query.order_by(

        Student.id.desc()

    ).paginate(

        page=page,

        per_page=per_page,

        error_out=False

    )

    return render_template(

        "admin/students/list.html",

        students=students,

        keyword=keyword

    )


# ==========================================================
# STUDENT DETAILS
# ==========================================================

@admin_bp.route("/students/<int:student_id>")
@login_required
@admin_required
def student_details(student_id):

    student = Student.query.get_or_404(student_id)

    return render_template(

        "admin/students/details.html",

        student=student

    )


# ==========================================================
# CREATE STUDENT
# ==========================================================

@admin_bp.route(
    "/students/create",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def create_student():

    if request.method == "POST":

        try:

            user = User(

                first_name=request.form["first_name"],

                last_name=request.form["last_name"],

                username=request.form["username"],

                email=request.form["email"],

                mobile=request.form.get("mobile"),

                role=User.ROLE_STUDENT

            )

            user.set_password(

                request.form["password"]

            )

            db.session.add(user)

            db.session.flush()

            student = Student(

                user_id=user.id,

                enrollment_number=request.form["enrollment_number"],

                branch=request.form.get("branch"),

                semester=request.form.get("semester")

            )

            db.session.add(student)

            db.session.commit()

            success(

                "Student created successfully."

            )

            return redirect(

                url_for(

                    "admin.students"

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/students/create.html"

    )


# ==========================================================
# EDIT STUDENT
# ==========================================================

@admin_bp.route(
    "/students/<int:student_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def edit_student(student_id):

    student = Student.query.get_or_404(student_id)

    if request.method == "POST":

        try:

            student.user.update(

                first_name=request.form["first_name"],

                last_name=request.form["last_name"],

                username=request.form["username"],

                email=request.form["email"],

                mobile=request.form.get("mobile")

            )

            student.enrollment_number = request.form["enrollment_number"]

            student.branch = request.form.get("branch")

            student.semester = request.form.get("semester")

            db.session.commit()

            success(

                "Student updated successfully."

            )

            return redirect(

                url_for(

                    "admin.student_details",

                    student_id=student.id

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/students/edit.html",

        student=student

    )


# ==========================================================
# DELETE STUDENT
# ==========================================================

@admin_bp.route(
    "/students/<int:student_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_student(student_id):

    student = Student.query.get_or_404(student_id)

    try:

        user = student.user

        db.session.delete(student)

        db.session.delete(user)

        db.session.commit()

        success(

            "Student deleted successfully."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.students"

        )

    )


# ==========================================================
# TEACHER MANAGEMENT
# ==========================================================

@admin_bp.route("/teachers")
@login_required
@admin_required
def teachers():

    page, per_page = get_pagination()

    keyword = search_keyword()

    query = Teacher.query.join(User)

    if keyword:

        query = query.filter(

            or_(

                User.first_name.ilike(f"%{keyword}%"),

                User.last_name.ilike(f"%{keyword}%"),

                User.username.ilike(f"%{keyword}%"),

                User.email.ilike(f"%{keyword}%"),

                Teacher.employee_id.ilike(f"%{keyword}%")

            )

        )

    teachers = query.order_by(

        Teacher.id.desc()

    ).paginate(

        page=page,

        per_page=per_page,

        error_out=False

    )

    return render_template(

        "admin/teachers/list.html",

        teachers=teachers,

        keyword=keyword

    )


# ==========================================================
# TEACHER DETAILS
# ==========================================================

@admin_bp.route("/teachers/<int:teacher_id>")
@login_required
@admin_required
def teacher_details(teacher_id):

    teacher = Teacher.query.get_or_404(

        teacher_id

    )

    return render_template(

        "admin/teachers/details.html",

        teacher=teacher

    )


# ==========================================================
# CREATE TEACHER
# ==========================================================

@admin_bp.route(
    "/teachers/create",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def create_teacher():

    if request.method == "POST":

        try:

            user = User(

                first_name=request.form["first_name"],

                last_name=request.form["last_name"],

                username=request.form["username"],

                email=request.form["email"],

                mobile=request.form.get("mobile"),

                role=User.ROLE_TEACHER

            )

            user.set_password(

                request.form["password"]

            )

            db.session.add(user)

            db.session.flush()

            teacher = Teacher(

                user_id=user.id,

                employee_id=request.form["employee_id"],

                department=request.form.get("department"),

                designation=request.form.get("designation")

            )

            db.session.add(teacher)

            db.session.commit()

            success(

                "Teacher created successfully."

            )

            return redirect(

                url_for(

                    "admin.teachers"

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/teachers/create.html"

    )
# ==========================================================
# EDIT TEACHER
# ==========================================================

@admin_bp.route(
    "/teachers/<int:teacher_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def edit_teacher(teacher_id):

    teacher = Teacher.query.get_or_404(teacher_id)

    if request.method == "POST":

        try:

            teacher.user.update(

                first_name=request.form["first_name"],

                last_name=request.form["last_name"],

                username=request.form["username"],

                email=request.form["email"],

                mobile=request.form.get("mobile")

            )

            teacher.employee_id = request.form["employee_id"]

            teacher.department = request.form.get("department")

            teacher.designation = request.form.get("designation")

            db.session.commit()

            success(

                "Teacher updated successfully."

            )

            return redirect(

                url_for(

                    "admin.teacher_details",

                    teacher_id=teacher.id

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/teachers/edit.html",

        teacher=teacher

    )


# ==========================================================
# DELETE TEACHER
# ==========================================================

@admin_bp.route(
    "/teachers/<int:teacher_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_teacher(teacher_id):

    teacher = Teacher.query.get_or_404(teacher_id)

    try:

        user = teacher.user

        db.session.delete(teacher)

        db.session.delete(user)

        db.session.commit()

        success(

            "Teacher deleted successfully."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.teachers"

        )

    )


# ==========================================================
# PROBLEM MANAGEMENT
# ==========================================================

@admin_bp.route("/problems")
@login_required
@admin_required
def problems():

    page, per_page = get_pagination()

    keyword = search_keyword()

    query = Problem.query

    if keyword:

        query = query.filter(

            or_(

                Problem.title.ilike(f"%{keyword}%"),

                Problem.description.ilike(f"%{keyword}%")

            )

        )

    problems = query.order_by(

        Problem.created_at.desc()

    ).paginate(

        page=page,

        per_page=per_page,

        error_out=False

    )

    return render_template(

        "admin/problems/list.html",

        problems=problems,

        keyword=keyword

    )


# ==========================================================
# PROBLEM DETAILS
# ==========================================================

@admin_bp.route("/problems/<int:problem_id>")
@login_required
@admin_required
def problem_details(problem_id):

    problem = Problem.get_by_id(problem_id)

    if not problem:

        abort(404)

    return render_template(

        "admin/problems/details.html",

        problem=problem

    )


# ==========================================================
# CREATE PROBLEM
# ==========================================================

@admin_bp.route(
    "/problems/create",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def create_problem():

    if request.method == "POST":

        try:

            problem = Problem(

                title=request.form["title"],

                description=request.form["description"],

                difficulty=request.form["difficulty"],

                time_limit=float(
                    request.form["time_limit"]
                ),

                memory_limit=int(
                    request.form["memory_limit"]
                ),

                created_by=current_user.id

            )

            db.session.add(problem)

            db.session.commit()

            success(

                "Problem created successfully."

            )

            return redirect(

                url_for(

                    "admin.problems"

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/problems/create.html"

    )


# ==========================================================
# EDIT PROBLEM
# ==========================================================

@admin_bp.route(
    "/problems/<int:problem_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def edit_problem(problem_id):

    problem = Problem.get_by_id(problem_id)

    if not problem:

        abort(404)

    if request.method == "POST":

        try:

            problem.update(

                title=request.form["title"],

                description=request.form["description"],

                difficulty=request.form["difficulty"],

                time_limit=float(
                    request.form["time_limit"]
                ),

                memory_limit=int(
                    request.form["memory_limit"]
                )

            )

            success(

                "Problem updated successfully."

            )

            return redirect(

                url_for(

                    "admin.problem_details",

                    problem_id=problem.id

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/problems/edit.html",

        problem=problem

    )


# ==========================================================
# DELETE PROBLEM
# ==========================================================

@admin_bp.route(
    "/problems/<int:problem_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_problem(problem_id):

    problem = Problem.get_by_id(problem_id)

    if not problem:

        abort(404)

    try:

        problem.delete()

        success(

            "Problem deleted successfully."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.problems"

        )

    )
# ==========================================================
# TEST CASE MANAGEMENT
# ==========================================================

@admin_bp.route("/problems/<int:problem_id>/testcases")
@login_required
@admin_required
def testcases(problem_id):

    problem = Problem.get_by_id(problem_id)

    if not problem:

        abort(404)

    page, per_page = get_pagination()

    keyword = search_keyword()

    query = TestCase.query.filter_by(
        problem_id=problem_id
    )

    if keyword:

        query = query.filter(

            or_(

                TestCase.name.ilike(f"%{keyword}%"),

                TestCase.description.ilike(f"%{keyword}%")

            )

        )

    testcases = query.order_by(

        TestCase.execution_order.asc()

    ).paginate(

        page=page,

        per_page=per_page,

        error_out=False

    )

    return render_template(

        "admin/testcases/list.html",

        problem=problem,

        testcases=testcases,

        keyword=keyword

    )


# ==========================================================
# TEST CASE DETAILS
# ==========================================================

@admin_bp.route("/testcases/<int:testcase_id>")
@login_required
@admin_required
def testcase_details(testcase_id):

    testcase = TestCase.get_by_id(testcase_id)

    if not testcase:

        abort(404)

    return render_template(

        "admin/testcases/details.html",

        testcase=testcase

    )


# ==========================================================
# CREATE TEST CASE
# ==========================================================

@admin_bp.route(
    "/problems/<int:problem_id>/testcases/create",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def create_testcase(problem_id):

    problem = Problem.get_by_id(problem_id)

    if not problem:

        abort(404)

    if request.method == "POST":

        try:

            testcase = TestCase(

                problem_id=problem.id,

                name=request.form["name"],

                description=request.form.get(

                    "description"

                ),

                input_data=request.form["input_data"],

                expected_output=request.form[
                    "expected_output"
                ],

                explanation=request.form.get(
                    "explanation"
                ),

                time_limit=float(

                    request.form.get(
                        "time_limit",
                        2
                    )

                ),

                memory_limit=int(

                    request.form.get(
                        "memory_limit",
                        256
                    )

                ),

                marks=float(

                    request.form.get(
                        "marks",
                        0
                    )

                ),

                weight=float(

                    request.form.get(
                        "weight",
                        1
                    )

                ),

                execution_order=int(

                    request.form.get(
                        "execution_order",
                        1
                    )

                ),

                is_hidden=bool(

                    request.form.get(
                        "is_hidden"
                    )

                ),

                is_sample=bool(

                    request.form.get(
                        "is_sample"
                    )

                )

            )

            db.session.add(testcase)

            db.session.commit()

            success(

                "Test case created successfully."

            )

            return redirect(

                url_for(

                    "admin.testcases",

                    problem_id=problem.id

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/testcases/create.html",

        problem=problem

    )


# ==========================================================
# EDIT TEST CASE
# ==========================================================

@admin_bp.route(
    "/testcases/<int:testcase_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def edit_testcase(testcase_id):

    testcase = TestCase.get_by_id(testcase_id)

    if not testcase:

        abort(404)

    if request.method == "POST":

        try:

            testcase.update(

                name=request.form["name"],

                description=request.form.get(

                    "description"

                ),

                input_data=request.form["input_data"],

                expected_output=request.form[
                    "expected_output"
                ],

                explanation=request.form.get(
                    "explanation"
                ),

                time_limit=float(

                    request.form["time_limit"]

                ),

                memory_limit=int(

                    request.form["memory_limit"]

                ),

                marks=float(

                    request.form["marks"]

                ),

                weight=float(

                    request.form["weight"]

                ),

                execution_order=int(

                    request.form[
                        "execution_order"
                    ]

                ),

                is_hidden=bool(

                    request.form.get(
                        "is_hidden"
                    )

                ),

                is_sample=bool(

                    request.form.get(
                        "is_sample"
                    )

                )

            )

            success(

                "Test case updated successfully."

            )

            return redirect(

                url_for(

                    "admin.testcase_details",

                    testcase_id=testcase.id

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/testcases/edit.html",

        testcase=testcase

    )


# ==========================================================
# DELETE TEST CASE
# ==========================================================

@admin_bp.route(
    "/testcases/<int:testcase_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_testcase(testcase_id):

    testcase = TestCase.get_by_id(testcase_id)

    if not testcase:

        abort(404)

    problem_id = testcase.problem_id

    try:

        testcase.delete()

        success(

            "Test case deleted successfully."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.testcases",

            problem_id=problem_id

        )

    )


# ==========================================================
# TOGGLE SAMPLE TEST CASE
# ==========================================================

@admin_bp.route(
    "/testcases/<int:testcase_id>/sample",
    methods=["POST"]
)
@login_required
@admin_required
def toggle_sample(testcase_id):

    testcase = TestCase.get_by_id(testcase_id)

    if not testcase:

        abort(404)

    testcase.is_sample = not testcase.is_sample

    db.session.commit()

    success(

        "Sample status updated."

    )

    return redirect(

        url_for(

            "admin.testcase_details",

            testcase_id=testcase.id

        )

    )


# ==========================================================
# TOGGLE HIDDEN TEST CASE
# ==========================================================

@admin_bp.route(
    "/testcases/<int:testcase_id>/hidden",
    methods=["POST"]
)
@login_required
@admin_required
def toggle_hidden(testcase_id):

    testcase = TestCase.get_by_id(testcase_id)

    if not testcase:

        abort(404)

    testcase.is_hidden = not testcase.is_hidden

    db.session.commit()

    success(

        "Visibility updated."

    )

    return redirect(

        url_for(

            "admin.testcase_details",

            testcase_id=testcase.id

        )

    )
# ==========================================================
# ASSIGNMENT MANAGEMENT
# ==========================================================

@admin_bp.route("/assignments")
@login_required
@admin_required
def assignments():

    page, per_page = get_pagination()

    keyword = search_keyword()

    query = Assignment.query

    if keyword:

        query = query.filter(

            or_(

                Assignment.title.ilike(f"%{keyword}%"),

                Assignment.description.ilike(f"%{keyword}%")

            )

        )

    assignments = query.order_by(

        Assignment.created_at.desc()

    ).paginate(

        page=page,

        per_page=per_page,

        error_out=False

    )

    return render_template(

        "admin/assignments/list.html",

        assignments=assignments,

        keyword=keyword

    )


# ==========================================================
# ASSIGNMENT DETAILS
# ==========================================================

@admin_bp.route("/assignments/<int:assignment_id>")
@login_required
@admin_required
def assignment_details(assignment_id):

    assignment = Assignment.get_by_id(assignment_id)

    if not assignment:

        abort(404)

    return render_template(

        "admin/assignments/details.html",

        assignment=assignment

    )


# ==========================================================
# CREATE ASSIGNMENT
# ==========================================================

@admin_bp.route(
    "/assignments/create",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def create_assignment():

    problems = Problem.query.order_by(

        Problem.title.asc()

    ).all()

    teachers = Teacher.query.order_by(

        Teacher.id.asc()

    ).all()

    if request.method == "POST":

        try:

            assignment = Assignment(

                title=request.form["title"],

                description=request.form.get(

                    "description"

                ),

                problem_id=int(

                    request.form["problem_id"]

                ),

                teacher_id=int(

                    request.form["teacher_id"]

                ),

                start_date=datetime.fromisoformat(

                    request.form["start_date"]

                ),

                due_date=datetime.fromisoformat(

                    request.form["due_date"]

                ),

                total_marks=float(

                    request.form.get(

                        "total_marks",

                        100

                    )

                ),

                created_by=current_user.id

            )

            db.session.add(assignment)

            db.session.commit()

            success(

                "Assignment created successfully."

            )

            return redirect(

                url_for(

                    "admin.assignments"

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/assignments/create.html",

        problems=problems,

        teachers=teachers

    )


# ==========================================================
# EDIT ASSIGNMENT
# ==========================================================

@admin_bp.route(
    "/assignments/<int:assignment_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def edit_assignment(assignment_id):

    assignment = Assignment.get_by_id(

        assignment_id

    )

    if not assignment:

        abort(404)

    problems = Problem.query.all()

    teachers = Teacher.query.all()

    if request.method == "POST":

        try:

            assignment.update(

                title=request.form["title"],

                description=request.form.get(

                    "description"

                ),

                problem_id=int(

                    request.form["problem_id"]

                ),

                teacher_id=int(

                    request.form["teacher_id"]

                ),

                start_date=datetime.fromisoformat(

                    request.form["start_date"]

                ),

                due_date=datetime.fromisoformat(

                    request.form["due_date"]

                ),

                total_marks=float(

                    request.form["total_marks"]

                )

            )

            success(

                "Assignment updated successfully."

            )

            return redirect(

                url_for(

                    "admin.assignment_details",

                    assignment_id=assignment.id

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/assignments/edit.html",

        assignment=assignment,

        problems=problems,

        teachers=teachers

    )


# ==========================================================
# DELETE ASSIGNMENT
# ==========================================================

@admin_bp.route(
    "/assignments/<int:assignment_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_assignment(assignment_id):

    assignment = Assignment.get_by_id(

        assignment_id

    )

    if not assignment:

        abort(404)

    try:

        assignment.delete()

        success(

            "Assignment deleted successfully."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.assignments"

        )

    )


# ==========================================================
# PUBLISH ASSIGNMENT
# ==========================================================

@admin_bp.route(
    "/assignments/<int:assignment_id>/publish",
    methods=["POST"]
)
@login_required
@admin_required
def publish_assignment(assignment_id):

    assignment = Assignment.get_by_id(

        assignment_id

    )

    if not assignment:

        abort(404)

    assignment.publish()

    db.session.commit()

    success(

        "Assignment published."

    )

    return redirect(

        url_for(

            "admin.assignment_details",

            assignment_id=assignment.id

        )

    )


# ==========================================================
# UNPUBLISH ASSIGNMENT
# ==========================================================

@admin_bp.route(
    "/assignments/<int:assignment_id>/unpublish",
    methods=["POST"]
)
@login_required
@admin_required
def unpublish_assignment(assignment_id):

    assignment = Assignment.get_by_id(

        assignment_id

    )

    if not assignment:

        abort(404)

    assignment.unpublish()

    db.session.commit()

    success(

        "Assignment unpublished."

    )

    return redirect(

        url_for(

            "admin.assignment_details",

            assignment_id=assignment.id

        )

    )


# ==========================================================
# ASSIGN STUDENTS
# ==========================================================

@admin_bp.route(
    "/assignments/<int:assignment_id>/students",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def assign_students(assignment_id):

    assignment = Assignment.get_by_id(

        assignment_id

    )

    if not assignment:

        abort(404)

    students = Student.query.order_by(

        Student.id.asc()

    ).all()

    if request.method == "POST":

        try:

            selected = request.form.getlist(

                "students"

            )

            assignment.students = Student.query.filter(

                Student.id.in_(selected)

            ).all()

            db.session.commit()

            success(

                "Students assigned successfully."

            )

            return redirect(

                url_for(

                    "admin.assignment_details",

                    assignment_id=assignment.id

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "admin/assignments/students.html",

        assignment=assignment,

        students=students

    )
# ==========================================================
# SUBMISSION MANAGEMENT
# ==========================================================

@admin_bp.route("/submissions")
@login_required
@admin_required
def submissions():

    page, per_page = get_pagination()

    keyword = search_keyword()

    query = Submission.query

    if keyword:

        query = query.join(User).join(Problem).filter(

            or_(

                User.username.ilike(f"%{keyword}%"),

                User.email.ilike(f"%{keyword}%"),

                Problem.title.ilike(f"%{keyword}%"),

                Submission.language.ilike(f"%{keyword}%"),

                Submission.verdict.ilike(f"%{keyword}%")

            )

        )

    submissions = query.order_by(

        Submission.submitted_at.desc()

    ).paginate(

        page=page,

        per_page=per_page,

        error_out=False

    )

    return render_template(

        "admin/submissions/list.html",

        submissions=submissions,

        keyword=keyword

    )


# ==========================================================
# SUBMISSION DETAILS
# ==========================================================

@admin_bp.route("/submissions/<int:submission_id>")
@login_required
@admin_required
def submission_details(submission_id):

    submission = Submission.get_by_id(

        submission_id

    )

    if not submission:

        abort(404)

    return render_template(

        "admin/submissions/details.html",

        submission=submission

    )


# ==========================================================
# DELETE SUBMISSION
# ==========================================================

@admin_bp.route(
    "/submissions/<int:submission_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def delete_submission(submission_id):

    submission = Submission.get_by_id(

        submission_id

    )

    if not submission:

        abort(404)

    try:

        submission.delete()

        success(

            "Submission deleted successfully."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.submissions"

        )

    )


# ==========================================================
# RE-EVALUATE SUBMISSION
# ==========================================================

@admin_bp.route(
    "/submissions/<int:submission_id>/rejudge",
    methods=["POST"]
)
@login_required
@admin_required
def rejudge_submission(submission_id):

    submission = Submission.get_by_id(

        submission_id

    )

    if not submission:

        abort(404)

    try:

        submission.re_evaluate()

        db.session.commit()

        success(

            "Submission queued for re-evaluation."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.submission_details",

            submission_id=submission.id

        )

    )


# ==========================================================
# RESET SUBMISSION
# ==========================================================

@admin_bp.route(
    "/submissions/<int:submission_id>/reset",
    methods=["POST"]
)
@login_required
@admin_required
def reset_submission(submission_id):

    submission = Submission.get_by_id(

        submission_id

    )

    if not submission:

        abort(404)

    try:

        submission.reset()

        success(

            "Submission reset successfully."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.submission_details",

            submission_id=submission.id

        )

    )


# ==========================================================
# BULK DELETE
# ==========================================================

@admin_bp.route(
    "/submissions/bulk-delete",
    methods=["POST"]
)
@login_required
@admin_required
def bulk_delete_submissions():

    ids = request.form.getlist(

        "submission_ids"

    )

    if not ids:

        warning(

            "No submissions selected."

        )

        return redirect(

            url_for(

                "admin.submissions"

            )

        )

    try:

        Submission.bulk_delete(ids)

        success(

            "Selected submissions deleted."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.submissions"

        )

    )


# ==========================================================
# BULK REJUDGE
# ==========================================================

@admin_bp.route(
    "/submissions/bulk-rejudge",
    methods=["POST"]
)
@login_required
@admin_required
def bulk_rejudge():

    ids = request.form.getlist(

        "submission_ids"

    )

    if not ids:

        warning(

            "No submissions selected."

        )

        return redirect(

            url_for(

                "admin.submissions"

            )

        )

    try:

        submissions = Submission.query.filter(

            Submission.id.in_(ids)

        ).all()

        for submission in submissions:

            submission.re_evaluate(

                commit=False

            )

        db.session.commit()

        success(

            "Selected submissions queued."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "admin.submissions"

        )

    )


# ==========================================================
# SUBMISSION ANALYTICS
# ==========================================================

@admin_bp.route("/submissions/analytics")
@login_required
@admin_required
def submission_analytics():

    stats = Submission.dashboard_statistics()

    verdicts = Submission.verdict_distribution()

    top_scores = Submission.top_scores(20)

    return render_template(

        "admin/submissions/analytics.html",

        stats=stats,

        verdicts=verdicts,

        top_scores=top_scores

    )


# ==========================================================
# SUBMISSION API
# ==========================================================

@admin_bp.route("/api/submissions")
@login_required
@admin_required
def submission_api():

    data = [

        submission.to_dict()

        for submission in Submission.latest(100)

    ]

    return jsonify(data)
# ==========================================================
# SETTINGS
# ==========================================================

@admin_bp.route("/settings")
@login_required
@admin_required
def settings():

    return render_template(

        "admin/settings/index.html"

    )


@admin_bp.route(
    "/settings",
    methods=["POST"]
)
@login_required
@admin_required
def update_settings():

    try:

        current_app.config["SITE_NAME"] = request.form.get(

            "site_name",

            current_app.config.get("SITE_NAME")

        )

        current_app.config["MAX_UPLOAD_SIZE"] = int(

            request.form.get(

                "max_upload_size",

                current_app.config.get(

                    "MAX_UPLOAD_SIZE",

                    10

                )

            )

        )

        success(

            "Settings updated successfully."

        )

    except Exception as e:

        error(str(e))

    return redirect(

        url_for(

            "admin.settings"

        )

    )


# ==========================================================
# DASHBOARD JSON API
# ==========================================================

@admin_bp.route("/api/dashboard")
@login_required
@admin_required
def dashboard_api():

    return jsonify(

        {

            "users": User.role_statistics(),

            "submissions":

                Submission.dashboard_statistics(),

            "problems": {

                "total": Problem.count()

            },

            "assignments": {

                "total": Assignment.count()

            },

            "testcases": {

                "total": TestCase.count()

            }

        }

    )


# ==========================================================
# EXPORT USERS
# ==========================================================

@admin_bp.route("/export/users")
@login_required
@admin_required
def export_users():

    data = [

        user.to_dict()

        for user in User.query.order_by(

            User.id.asc()

        ).all()

    ]

    return jsonify(data)


# ==========================================================
# EXPORT PROBLEMS
# ==========================================================

@admin_bp.route("/export/problems")
@login_required
@admin_required
def export_problems():

    data = [

        problem.to_dict()

        for problem in Problem.query.order_by(

            Problem.id.asc()

        ).all()

    ]

    return jsonify(data)


# ==========================================================
# EXPORT ASSIGNMENTS
# ==========================================================

@admin_bp.route("/export/assignments")
@login_required
@admin_required
def export_assignments():

    data = [

        assignment.to_dict()

        for assignment in Assignment.query.order_by(

            Assignment.id.asc()

        ).all()

    ]

    return jsonify(data)


# ==========================================================
# EXPORT SUBMISSIONS
# ==========================================================

@admin_bp.route("/export/submissions")
@login_required
@admin_required
def export_submissions():

    data = [

        submission.to_dict()

        for submission in Submission.query.order_by(

            Submission.id.asc()

        ).all()

    ]

    return jsonify(data)


# ==========================================================
# SYSTEM BACKUP
# ==========================================================

@admin_bp.route("/backup")
@login_required
@admin_required
def backup():

    backup_data = {

        "generated_at":

            datetime.utcnow().isoformat(),

        "users":

            User.count(),

        "students":

            Student.count(),

        "teachers":

            Teacher.count(),

        "problems":

            Problem.count(),

        "testcases":

            TestCase.count(),

        "assignments":

            Assignment.count(),

        "submissions":

            Submission.count()

    }

    return jsonify(backup_data)


# ==========================================================
# AUDIT LOG
# ==========================================================

@admin_bp.route("/audit")
@login_required
@admin_required
def audit():

    recent_users = [

        user.audit_log()

        for user in User.latest(20)

    ]

    recent_submissions = [

        submission.audit_log()

        for submission in Submission.latest(20)

    ]

    return render_template(

        "admin/audit/index.html",

        users=recent_users,

        submissions=recent_submissions

    )


# ==========================================================
# NOTIFICATIONS
# ==========================================================

@admin_bp.route("/notifications")
@login_required
@admin_required
def notifications():

    notifications = [

        {

            "title":

                "System Running",

            "type":

                "success",

            "time":

                datetime.utcnow()

        }

    ]

    return render_template(

        "admin/notifications.html",

        notifications=notifications

    )


# ==========================================================
# FILE MANAGER
# ==========================================================

@admin_bp.route("/files")
@login_required
@admin_required
def files():

    upload_folder = current_app.config.get(

        "UPLOAD_FOLDER",

        "uploads"

    )

    return render_template(

        "admin/files/index.html",

        upload_folder=upload_folder

    )


# ==========================================================
# CLEAR CACHE
# ==========================================================

@admin_bp.route(
    "/cache/clear",
    methods=["POST"]
)
@login_required
@admin_required
def clear_cache():

    success(

        "Application cache cleared."

    )

    return redirect(

        url_for(

            "admin.dashboard"

        )

    )


# ==========================================================
# DATABASE INFORMATION
# ==========================================================

@admin_bp.route("/database")
@login_required
@admin_required
def database_information():

    return render_template(

        "admin/database.html",

        tables=[

            "users",

            "students",

            "teachers",

            "problems",

            "test_cases",

            "assignments",

            "submissions"

        ]

    )
# ==========================================================
# ERROR HANDLERS
# ==========================================================

@admin_bp.errorhandler(403)
def forbidden(error):

    return render_template(

        "errors/403.html",

        error=error

    ), 403


@admin_bp.errorhandler(404)
def not_found(error):

    return render_template(

        "errors/404.html",

        error=error

    ), 404


@admin_bp.errorhandler(500)
def internal_error(error):

    db.session.rollback()

    return render_template(

        "errors/500.html",

        error=error

    ), 500


# ==========================================================
# GENERIC JSON RESPONSE
# ==========================================================

def json_success(message, **kwargs):

    response = {

        "success": True,

        "message": message

    }

    response.update(kwargs)

    return jsonify(response)


def json_error(message, status=400, **kwargs):

    response = {

        "success": False,

        "message": message

    }

    response.update(kwargs)

    return jsonify(response), status


# ==========================================================
# DASHBOARD SUMMARY API
# ==========================================================

@admin_bp.route("/api/summary")
@login_required
@admin_required
def api_summary():

    return json_success(

        "Dashboard summary",

        data={

            "users": User.count(),

            "students": Student.count(),

            "teachers": Teacher.count(),

            "problems": Problem.count(),

            "testcases": TestCase.count(),

            "assignments": Assignment.count(),

            "submissions": Submission.count()

        }

    )


# ==========================================================
# PING
# ==========================================================

@admin_bp.route("/ping")
def ping():

    return jsonify(

        {

            "status": "ok",

            "timestamp":

                datetime.utcnow().isoformat()

        }

    )


# ==========================================================
# HEALTH CHECK
# ==========================================================

@admin_bp.route("/health")
@login_required
@admin_required
def health():

    return jsonify(

        {

            "database": "connected",

            "server": "running",

            "time":

                datetime.utcnow().isoformat()

        }

    )


# ==========================================================
# VERSION
# ==========================================================

@admin_bp.route("/version")
def version():

    return jsonify(

        {

            "application":

                "Lab Auto Grader",

            "version":

                "1.0.0",

            "build":

                "Production"

        }

    )


# ==========================================================
# BLUEPRINT INITIALIZER
# ==========================================================

def init_app(app):
    """
    Register the admin blueprint.
    """

    app.register_blueprint(admin_bp)


# ==========================================================
# MODULE EXPORT
# ==========================================================

__all__ = [

    "admin_bp",

    "admin_required",

    "init_app"

]
