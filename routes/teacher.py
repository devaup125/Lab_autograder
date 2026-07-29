"""
==========================================================
Lab Auto Grader
Teacher Routes
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

    session,

    jsonify

)

from sqlalchemy import desc

from extensions import db

from models.user import User
from models.problem import Problem
from models.submission import Submission
from models.assignment import Assignment
from models.testcase import TestCase

from judge.judge import (
    judge_submission,
    judge_assignment
)

# ==========================================================
# BLUEPRINT
# ==========================================================

teacher_bp = Blueprint(

    "teacher",

    __name__,

    url_prefix="/teacher"

)

# ==========================================================
# LOGIN REQUIRED
# ==========================================================

def teacher_login_required(view):

    @wraps(view)

    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            flash(

                "Please login first.",

                "warning"

            )

            return redirect(

                url_for("auth.login")

            )

        teacher = User.query.get(

            session["user_id"]

        )

        if teacher is None:

            session.clear()

            return redirect(

                url_for("auth.login")

            )

        if teacher.role != "teacher":

            flash(

                "Access denied.",

                "danger"

            )

            return redirect(

                url_for("auth.login")

            )

        return view(

            *args,

            **kwargs

        )

    return wrapper


# ==========================================================
# CURRENT TEACHER
# ==========================================================

def current_teacher():

    if "user_id" not in session:

        return None

    return User.query.get(

        session["user_id"]

    )


# ==========================================================
# DASHBOARD
# ==========================================================

@teacher_bp.route("/")

@teacher_login_required
def dashboard():

    teacher = current_teacher()

    total_students = User.query.filter_by(

        role="student"

    ).count()

    total_problems = Problem.query.count()

    total_assignments = Assignment.query.count()

    total_submissions = Submission.query.count()

    recent_submissions = Submission.query.order_by(

        desc(

            Submission.created_at

        )

    ).limit(

        10

    ).all()

    return render_template(

        "teacher/dashboard.html",

        teacher=teacher,

        total_students=total_students,

        total_problems=total_problems,

        total_assignments=total_assignments,

        total_submissions=total_submissions,

        recent_submissions=recent_submissions

    )


# ==========================================================
# HOME
# ==========================================================

@teacher_bp.route("/home")

@teacher_login_required
def home():

    return redirect(

        url_for(

            "teacher.dashboard"

        )

    )


# ==========================================================
# PROFILE
# ==========================================================

@teacher_bp.route("/profile")

@teacher_login_required
def profile():

    return render_template(

        "teacher/profile.html",

        teacher=current_teacher()

    )


# ==========================================================
# DASHBOARD API
# ==========================================================

@teacher_bp.route("/dashboard/api")

@teacher_login_required
def dashboard_api():

    return jsonify({

        "students":

            User.query.filter_by(

                role="student"

            ).count(),

        "problems":

            Problem.query.count(),

        "assignments":

            Assignment.query.count(),

        "submissions":

            Submission.query.count(),

        "testcases":

            TestCase.query.count()

    })


# ==========================================================
# ABOUT
# ==========================================================

@teacher_bp.route("/about")

@teacher_login_required
def about():

    return render_template(

        "teacher/about.html"

    )
# ==========================================================
# PROBLEM LIST
# ==========================================================

@teacher_bp.route("/problems")
@teacher_login_required
def problems():

    page = request.args.get(

        "page",

        1,

        type=int

    )

    keyword = request.args.get(

        "q",

        ""

    )

    difficulty = request.args.get(

        "difficulty",

        ""

    )

    query = Problem.query

    if keyword:

        query = query.filter(

            Problem.title.ilike(

                f"%{keyword}%"

            )

        )

    if difficulty:

        query = query.filter_by(

            difficulty=difficulty

        )

    pagination = query.order_by(

        Problem.id.desc()

    ).paginate(

        page=page,

        per_page=20,

        error_out=False

    )

    return render_template(

        "teacher/problems.html",

        problems=pagination.items,

        pagination=pagination,

        keyword=keyword,

        difficulty=difficulty

    )


# ==========================================================
# ADD PROBLEM
# ==========================================================

@teacher_bp.route(
    "/problem/add",

    methods=["GET", "POST"]

)
@teacher_login_required
def add_problem():

    if request.method == "POST":

        problem = Problem(

            title=request.form.get(

                "title"

            ),

            difficulty=request.form.get(

                "difficulty"

            ),

            statement=request.form.get(

                "statement"

            ),

            input_format=request.form.get(

                "input_format"

            ),

            output_format=request.form.get(

                "output_format"

            ),

            constraints=request.form.get(

                "constraints"

            ),

            sample_input=request.form.get(

                "sample_input"

            ),

            sample_output=request.form.get(

                "sample_output"

            ),

            starter_code=request.form.get(

                "starter_code"

            )

        )

        db.session.add(

            problem

        )

        db.session.commit()

        flash(

            "Problem created successfully.",

            "success"

        )

        return redirect(

            url_for(

                "teacher.problems"

            )

        )

    return render_template(

        "teacher/add_problem.html"

    )


# ==========================================================
# EDIT PROBLEM
# ==========================================================

@teacher_bp.route(
    "/problem/<int:problem_id>/edit",

    methods=["GET", "POST"]

)
@teacher_login_required
def edit_problem(problem_id):

    problem = Problem.query.get_or_404(

        problem_id

    )

    if request.method == "POST":

        problem.title = request.form.get(

            "title"

        )

        problem.difficulty = request.form.get(

            "difficulty"

        )

        problem.statement = request.form.get(

            "statement"

        )

        problem.input_format = request.form.get(

            "input_format"

        )

        problem.output_format = request.form.get(

            "output_format"

        )

        problem.constraints = request.form.get(

            "constraints"

        )

        problem.sample_input = request.form.get(

            "sample_input"

        )

        problem.sample_output = request.form.get(

            "sample_output"

        )

        problem.starter_code = request.form.get(

            "starter_code"

        )

        db.session.commit()

        flash(

            "Problem updated successfully.",

            "success"

        )

        return redirect(

            url_for(

                "teacher.problems"

            )

        )

    return render_template(

        "teacher/edit_problem.html",

        problem=problem

    )


# ==========================================================
# DELETE PROBLEM
# ==========================================================

@teacher_bp.route(
    "/problem/<int:problem_id>/delete",

    methods=["POST"]

)
@teacher_login_required
def delete_problem(problem_id):

    problem = Problem.query.get_or_404(

        problem_id

    )

    db.session.delete(

        problem

    )

    db.session.commit()

    flash(

        "Problem deleted successfully.",

        "success"

    )

    return redirect(

        url_for(

            "teacher.problems"

        )

    )


# ==========================================================
# PROBLEM DETAILS
# ==========================================================

@teacher_bp.route(
    "/problem/<int:problem_id>"
)
@teacher_login_required
def problem_details(problem_id):

    problem = Problem.query.get_or_404(

        problem_id

    )

    testcase_count = TestCase.query.filter_by(

        problem_id=problem.id

    ).count()

    submission_count = Submission.query.filter_by(

        problem_id=problem.id

    ).count()

    accepted = Submission.query.filter_by(

        problem_id=problem.id,

        verdict="Accepted"

    ).count()

    return render_template(

        "teacher/problem_details.html",

        problem=problem,

        testcase_count=testcase_count,

        submission_count=submission_count,

        accepted=accepted

    )


# ==========================================================
# SEARCH PROBLEM
# ==========================================================

@teacher_bp.route("/problem/search")
@teacher_login_required
def search_problem():

    keyword = request.args.get(

        "q",

        ""

    )

    problems = Problem.query.filter(

        Problem.title.ilike(

            f"%{keyword}%"

        )

    ).all()

    return render_template(

        "teacher/problem_search.html",

        keyword=keyword,

        problems=problems

    )


# ==========================================================
# DIFFICULTY FILTER
# ==========================================================

@teacher_bp.route("/problem/difficulty/<level>")
@teacher_login_required
def difficulty(level):

    problems = Problem.query.filter_by(

        difficulty=level

    ).all()

    return render_template(

        "teacher/problem_difficulty.html",

        problems=problems,

        level=level

    )


# ==========================================================
# PROBLEM PREVIEW
# ==========================================================

@teacher_bp.route(
    "/problem/<int:problem_id>/preview"
)
@teacher_login_required
def preview_problem(problem_id):

    problem = Problem.query.get_or_404(

        problem_id

    )

    return render_template(

        "teacher/problem_preview.html",

        problem=problem

    )
# ==========================================================
# TEST CASE LIST
# ==========================================================

@teacher_bp.route("/problem/<int:problem_id>/testcases")
@teacher_login_required
def testcases(problem_id):

    problem = Problem.query.get_or_404(problem_id)

    testcases = TestCase.query.filter_by(
        problem_id=problem.id
    ).order_by(
        TestCase.id.asc()
    ).all()

    return render_template(
        "teacher/testcases.html",
        problem=problem,
        testcases=testcases
    )


# ==========================================================
# ADD TEST CASE
# ==========================================================

@teacher_bp.route(
    "/problem/<int:problem_id>/testcase/add",
    methods=["GET", "POST"]
)
@teacher_login_required
def add_testcase(problem_id):

    problem = Problem.query.get_or_404(problem_id)

    if request.method == "POST":

        testcase = TestCase(

            problem_id=problem.id,

            input_data=request.form.get(
                "input_data"
            ),

            expected_output=request.form.get(
                "expected_output"
            ),

            is_hidden=(
                request.form.get(
                    "is_hidden"
                ) == "on"
            )

        )

        db.session.add(testcase)

        db.session.commit()

        flash(
            "Test case added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "teacher.testcases",
                problem_id=problem.id
            )
        )

    return render_template(
        "teacher/add_testcase.html",
        problem=problem
    )


# ==========================================================
# EDIT TEST CASE
# ==========================================================

@teacher_bp.route(
    "/testcase/<int:testcase_id>/edit",
    methods=["GET", "POST"]
)
@teacher_login_required
def edit_testcase(testcase_id):

    testcase = TestCase.query.get_or_404(
        testcase_id
    )

    if request.method == "POST":

        testcase.input_data = request.form.get(
            "input_data"
        )

        testcase.expected_output = request.form.get(
            "expected_output"
        )

        testcase.is_hidden = (
            request.form.get(
                "is_hidden"
            ) == "on"
        )

        db.session.commit()

        flash(
            "Test case updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "teacher.testcases",
                problem_id=testcase.problem_id
            )
        )

    return render_template(
        "teacher/edit_testcase.html",
        testcase=testcase
    )


# ==========================================================
# DELETE TEST CASE
# ==========================================================

@teacher_bp.route(
    "/testcase/<int:testcase_id>/delete",
    methods=["POST"]
)
@teacher_login_required
def delete_testcase(testcase_id):

    testcase = TestCase.query.get_or_404(
        testcase_id
    )

    problem_id = testcase.problem_id

    db.session.delete(testcase)

    db.session.commit()

    flash(
        "Test case deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "teacher.testcases",
            problem_id=problem_id
        )
    )


# ==========================================================
# BULK TEST CASE UPLOAD
# ==========================================================

@teacher_bp.route(
    "/problem/<int:problem_id>/testcases/upload",
    methods=["GET", "POST"]
)
@teacher_login_required
def upload_testcases(problem_id):

    problem = Problem.query.get_or_404(
        problem_id
    )

    if request.method == "POST":

        uploaded = request.files.get(
            "file"
        )

        if uploaded is None:

            flash(
                "Please upload a CSV file.",
                "danger"
            )

            return redirect(request.url)

        import csv
        import io

        stream = io.StringIO(

            uploaded.stream.read().decode(
                "utf-8"
            )

        )

        reader = csv.DictReader(stream)

        count = 0

        for row in reader:

            testcase = TestCase(

                problem_id=problem.id,

                input_data=row.get(
                    "input_data",
                    ""
                ),

                expected_output=row.get(
                    "expected_output",
                    ""
                ),

                is_hidden=(
                    row.get(
                        "is_hidden",
                        "false"
                    ).lower()
                    == "true"
                )

            )

            db.session.add(testcase)

            count += 1

        db.session.commit()

        flash(
            f"{count} test cases uploaded.",
            "success"
        )

        return redirect(
            url_for(
                "teacher.testcases",
                problem_id=problem.id
            )
        )

    return render_template(
        "teacher/upload_testcases.html",
        problem=problem
    )


# ==========================================================
# DOWNLOAD TEST CASES
# ==========================================================

@teacher_bp.route(
    "/problem/<int:problem_id>/testcases/download"
)
@teacher_login_required
def download_testcases(problem_id):

    import csv
    import io

    problem = Problem.query.get_or_404(
        problem_id
    )

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "input_data",
        "expected_output",
        "is_hidden"
    ])

    testcases = TestCase.query.filter_by(
        problem_id=problem.id
    ).all()

    for testcase in testcases:

        writer.writerow([
            testcase.input_data,
            testcase.expected_output,
            testcase.is_hidden
        ])

    from flask import Response

    return Response(

        output.getvalue(),

        mimetype="text/csv",

        headers={

            "Content-Disposition":

            f"attachment; filename=problem_{problem.id}_testcases.csv"

        }

    )


# ==========================================================
# TOGGLE HIDDEN TEST CASE
# ==========================================================

@teacher_bp.route(
    "/testcase/<int:testcase_id>/toggle",
    methods=["POST"]
)
@teacher_login_required
def toggle_hidden(testcase_id):

    testcase = TestCase.query.get_or_404(
        testcase_id
    )

    testcase.is_hidden = (
        not testcase.is_hidden
    )

    db.session.commit()

    return jsonify({

        "success": True,

        "hidden": testcase.is_hidden

    })
# ==========================================================
# ASSIGNMENT LIST
# ==========================================================

@teacher_bp.route("/assignments")
@teacher_login_required
def assignments():

    assignments = Assignment.query.order_by(

        Assignment.created_at.desc()

    ).all()

    return render_template(

        "teacher/assignments.html",

        assignments=assignments

    )


# ==========================================================
# CREATE ASSIGNMENT
# ==========================================================

@teacher_bp.route(
    "/assignment/add",
    methods=["GET", "POST"]
)
@teacher_login_required
def add_assignment():

    if request.method == "POST":

        assignment = Assignment(

            title=request.form.get(

                "title"

            ),

            description=request.form.get(

                "description"

            ),

            deadline=datetime.fromisoformat(

                request.form.get(

                    "deadline"

                )

            )

        )

        db.session.add(

            assignment

        )

        db.session.commit()

        flash(

            "Assignment created successfully.",

            "success"

        )

        return redirect(

            url_for(

                "teacher.assignments"

            )

        )

    return render_template(

        "teacher/add_assignment.html"

    )


# ==========================================================
# EDIT ASSIGNMENT
# ==========================================================

@teacher_bp.route(
    "/assignment/<int:assignment_id>/edit",
    methods=["GET", "POST"]
)
@teacher_login_required
def edit_assignment(assignment_id):

    assignment = Assignment.query.get_or_404(

        assignment_id

    )

    if request.method == "POST":

        assignment.title = request.form.get(

            "title"

        )

        assignment.description = request.form.get(

            "description"

        )

        assignment.deadline = datetime.fromisoformat(

            request.form.get(

                "deadline"

            )

        )

        db.session.commit()

        flash(

            "Assignment updated successfully.",

            "success"

        )

        return redirect(

            url_for(

                "teacher.assignments"

            )

        )

    return render_template(

        "teacher/edit_assignment.html",

        assignment=assignment

    )


# ==========================================================
# DELETE ASSIGNMENT
# ==========================================================

@teacher_bp.route(
    "/assignment/<int:assignment_id>/delete",
    methods=["POST"]
)
@teacher_login_required
def delete_assignment(assignment_id):

    assignment = Assignment.query.get_or_404(

        assignment_id

    )

    db.session.delete(

        assignment

    )

    db.session.commit()

    flash(

        "Assignment deleted successfully.",

        "success"

    )

    return redirect(

        url_for(

            "teacher.assignments"

        )

    )


# ==========================================================
# ASSIGNMENT DETAILS
# ==========================================================

@teacher_bp.route("/assignment/<int:assignment_id>")
@teacher_login_required
def assignment_details(assignment_id):

    assignment = Assignment.query.get_or_404(

        assignment_id

    )

    problems = Problem.query.filter_by(

        assignment_id=assignment.id

    ).all()

    submissions = Submission.query.filter_by(

        assignment_id=assignment.id

    ).count()

    return render_template(

        "teacher/assignment_details.html",

        assignment=assignment,

        problems=problems,

        submissions=submissions

    )


# ==========================================================
# ASSIGN PROBLEM
# ==========================================================

@teacher_bp.route(
    "/assignment/<int:assignment_id>/problem/<int:problem_id>/assign",
    methods=["POST"]
)
@teacher_login_required
def assign_problem(

    assignment_id,

    problem_id

):

    assignment = Assignment.query.get_or_404(

        assignment_id

    )

    problem = Problem.query.get_or_404(

        problem_id

    )

    problem.assignment_id = assignment.id

    db.session.commit()

    flash(

        "Problem assigned successfully.",

        "success"

    )

    return redirect(

        url_for(

            "teacher.assignment_details",

            assignment_id=assignment.id

        )

    )


# ==========================================================
# REMOVE PROBLEM
# ==========================================================

@teacher_bp.route(
    "/assignment/<int:assignment_id>/problem/<int:problem_id>/remove",
    methods=["POST"]
)
@teacher_login_required
def remove_problem(

    assignment_id,

    problem_id

):

    problem = Problem.query.get_or_404(

        problem_id

    )

    problem.assignment_id = None

    db.session.commit()

    flash(

        "Problem removed from assignment.",

        "success"

    )

    return redirect(

        url_for(

            "teacher.assignment_details",

            assignment_id=assignment_id

        )

    )


# ==========================================================
# ASSIGNMENT OVERVIEW
# ==========================================================

@teacher_bp.route(
    "/assignment/<int:assignment_id>/overview"
)
@teacher_login_required
def assignment_overview(

    assignment_id

):

    assignment = Assignment.query.get_or_404(

        assignment_id

    )

    total_problems = Problem.query.filter_by(

        assignment_id=assignment.id

    ).count()

    total_submissions = Submission.query.filter_by(

        assignment_id=assignment.id

    ).count()

    accepted = Submission.query.filter_by(

        assignment_id=assignment.id,

        verdict="Accepted"

    ).count()

    return jsonify({

        "assignment":

            assignment.title,

        "total_problems":

            total_problems,

        "total_submissions":

            total_submissions,

        "accepted":

            accepted,

        "deadline":

            assignment.deadline.isoformat()

    })
# ==========================================================
# STUDENT LIST
# ==========================================================

@teacher_bp.route("/students")
@teacher_login_required
def students():

    page = request.args.get(

        "page",

        1,

        type=int

    )

    students = User.query.filter_by(

        role="student"

    ).order_by(

        User.username.asc()

    ).paginate(

        page=page,

        per_page=20,

        error_out=False

    )

    return render_template(

        "teacher/students.html",

        students=students.items,

        pagination=students

    )


# ==========================================================
# STUDENT PROFILE
# ==========================================================

@teacher_bp.route("/student/<int:student_id>")
@teacher_login_required
def student_profile(student_id):

    student = User.query.get_or_404(

        student_id

    )

    submissions = Submission.query.filter_by(

        student_id=student.id

    ).order_by(

        Submission.created_at.desc()

    ).limit(20).all()

    return render_template(

        "teacher/student_profile.html",

        student=student,

        submissions=submissions

    )


# ==========================================================
# STUDENT SUBMISSIONS
# ==========================================================

@teacher_bp.route("/student/<int:student_id>/submissions")
@teacher_login_required
def student_submissions(student_id):

    student = User.query.get_or_404(

        student_id

    )

    submissions = Submission.query.filter_by(

        student_id=student.id

    ).order_by(

        Submission.created_at.desc()

    ).all()

    return render_template(

        "teacher/student_submissions.html",

        student=student,

        submissions=submissions

    )


# ==========================================================
# STUDENT PROGRESS
# ==========================================================

@teacher_bp.route("/student/<int:student_id>/progress")
@teacher_login_required
def student_progress(student_id):

    student = User.query.get_or_404(

        student_id

    )

    total = Problem.query.count()

    solved = Submission.query.filter_by(

        student_id=student.id,

        verdict="Accepted"

    ).count()

    attempted = Submission.query.filter_by(

        student_id=student.id

    ).count()

    progress = 0

    if total:

        progress = round(

            solved * 100 /

            total,

            2

        )

    return render_template(

        "teacher/student_progress.html",

        student=student,

        total=total,

        solved=solved,

        attempted=attempted,

        progress=progress

    )


# ==========================================================
# ENABLE STUDENT
# ==========================================================

@teacher_bp.route(
    "/student/<int:student_id>/enable",
    methods=["POST"]
)
@teacher_login_required
def enable_student(student_id):

    student = User.query.get_or_404(

        student_id

    )

    student.is_active = True

    db.session.commit()

    flash(

        "Student account enabled.",

        "success"

    )

    return redirect(

        url_for(

            "teacher.student_profile",

            student_id=student.id

        )

    )


# ==========================================================
# DISABLE STUDENT
# ==========================================================

@teacher_bp.route(
    "/student/<int:student_id>/disable",
    methods=["POST"]
)
@teacher_login_required
def disable_student(student_id):

    student = User.query.get_or_404(

        student_id

    )

    student.is_active = False

    db.session.commit()

    flash(

        "Student account disabled.",

        "warning"

    )

    return redirect(

        url_for(

            "teacher.student_profile",

            student_id=student.id

        )

    )


# ==========================================================
# STUDENT ANALYTICS
# ==========================================================

@teacher_bp.route("/student/<int:student_id>/analytics")
@teacher_login_required
def student_analytics(student_id):

    student = User.query.get_or_404(

        student_id

    )

    submissions = Submission.query.filter_by(

        student_id=student.id

    ).all()

    accepted = sum(

        1

        for s in submissions

        if s.verdict == "Accepted"

    )

    average_score = 0

    if submissions:

        average_score = round(

            sum(

                s.score

                for s in submissions

            ) /

            len(submissions),

            2

        )

    languages = {}

    for submission in submissions:

        languages[submission.language] = (

            languages.get(

                submission.language,

                0

            ) + 1

        )

    return jsonify({

        "student":

            student.username,

        "submissions":

            len(submissions),

        "accepted":

            accepted,

        "average_score":

            average_score,

        "languages":

            languages

    })


# ==========================================================
# TOP STUDENTS
# ==========================================================

@teacher_bp.route("/students/top")
@teacher_login_required
def top_students():

    ranking = db.session.query(

        User,

        db.func.count(

            Submission.id

        ).label(

            "accepted"

        )

    ).join(

        Submission,

        Submission.student_id == User.id

    ).filter(

        User.role == "student",

        Submission.verdict == "Accepted"

    ).group_by(

        User.id

    ).order_by(

        db.desc(

            "accepted"

        )

    ).limit(

        20

    ).all()

    return render_template(

        "teacher/top_students.html",

        ranking=ranking

    )
# ==========================================================
# SUBMISSION LIST
# ==========================================================

@teacher_bp.route("/submissions")
@teacher_login_required
def submissions():

    page = request.args.get(

        "page",

        1,

        type=int

    )

    pagination = Submission.query.order_by(

        Submission.created_at.desc()

    ).paginate(

        page=page,

        per_page=25,

        error_out=False

    )

    return render_template(

        "teacher/submissions.html",

        submissions=pagination.items,

        pagination=pagination

    )


# ==========================================================
# VIEW SUBMISSION
# ==========================================================

@teacher_bp.route("/submission/<int:submission_id>")
@teacher_login_required
def submission_details(submission_id):

    submission = Submission.query.get_or_404(

        submission_id

    )

    student = User.query.get(

        submission.student_id

    )

    problem = Problem.query.get(

        submission.problem_id

    )

    return render_template(

        "teacher/submission_details.html",

        submission=submission,

        student=student,

        problem=problem

    )


# ==========================================================
# DOWNLOAD SOURCE
# ==========================================================

@teacher_bp.route(
    "/submission/<int:submission_id>/download"
)
@teacher_login_required
def download_submission(submission_id):

    submission = Submission.query.get_or_404(

        submission_id

    )

    extension = {

        "Python": ".py",

        "C": ".c",

        "C++": ".cpp",

        "Java": ".java",

        "JavaScript": ".js"

    }.get(

        submission.language,

        ".txt"

    )

    from flask import Response

    return Response(

        submission.source_code,

        mimetype="text/plain",

        headers={

            "Content-Disposition":

            f"attachment; filename=submission_{submission.id}{extension}"

        }

    )


# ==========================================================
# MANUAL REJUDGE
# ==========================================================

@teacher_bp.route(
    "/submission/<int:submission_id>/rejudge",
    methods=["POST"]
)
@teacher_login_required
def rejudge(submission_id):

    submission = Submission.query.get_or_404(

        submission_id

    )

    result = judge_submission(

        submission

    )

    submission.verdict = result.verdict

    submission.score = result.score

    submission.execution_time = (

        result.execution_time

    )

    submission.memory_used = (

        result.memory_used

    )

    submission.passed_testcases = (

        result.passed_testcases

    )

    submission.total_testcases = (

        result.total_testcases

    )

    submission.compile_error = (

        result.compile_error

    )

    submission.runtime_error = (

        result.runtime_error

    )

    db.session.commit()

    flash(

        "Submission rejudged successfully.",

        "success"

    )

    return redirect(

        url_for(

            "teacher.submission_details",

            submission_id=submission.id

        )

    )


# ==========================================================
# DELETE SUBMISSION
# ==========================================================

@teacher_bp.route(
    "/submission/<int:submission_id>/delete",
    methods=["POST"]
)
@teacher_login_required
def delete_submission(submission_id):

    submission = Submission.query.get_or_404(

        submission_id

    )

    db.session.delete(

        submission

    )

    db.session.commit()

    flash(

        "Submission deleted.",

        "success"

    )

    return redirect(

        url_for(

            "teacher.submissions"

        )

    )


# ==========================================================
# SUBMISSION ANALYTICS
# ==========================================================

@teacher_bp.route("/submission/analytics")
@teacher_login_required
def submission_analytics():

    total = Submission.query.count()

    accepted = Submission.query.filter_by(

        verdict="Accepted"

    ).count()

    wrong_answer = Submission.query.filter_by(

        verdict="Wrong Answer"

    ).count()

    runtime_error = Submission.query.filter_by(

        verdict="Runtime Error"

    ).count()

    compile_error = Submission.query.filter_by(

        verdict="Compilation Error"

    ).count()

    return jsonify({

        "total": total,

        "accepted": accepted,

        "wrong_answer": wrong_answer,

        "runtime_error": runtime_error,

        "compile_error": compile_error,

        "acceptance_rate":

            round(

                accepted * 100 / total,

                2

            ) if total else 0

    })


# ==========================================================
# TEST CASE RESULTS
# ==========================================================

@teacher_bp.route(
    "/submission/<int:submission_id>/testcases"
)
@teacher_login_required
def testcase_results(submission_id):

    submission = Submission.query.get_or_404(

        submission_id

    )

    return render_template(

        "teacher/testcase_results.html",

        submission=submission,

        results=getattr(

            submission,

            "testcase_results",

            []

        )

    )


# ==========================================================
# JUDGE REPORT
# ==========================================================

@teacher_bp.route(
    "/submission/<int:submission_id>/report"
)
@teacher_login_required
def judge_report_view(submission_id):

    submission = Submission.query.get_or_404(

        submission_id

    )

    return jsonify({

        "submission":

            submission.id,

        "student":

            submission.student_id,

        "problem":

            submission.problem_id,

        "verdict":

            submission.verdict,

        "score":

            submission.score,

        "execution_time":

            submission.execution_time,

        "memory_used":

            submission.memory_used,

        "passed_testcases":

            submission.passed_testcases,

        "total_testcases":

            submission.total_testcases,

        "compile_error":

            submission.compile_error,

        "runtime_error":

            submission.runtime_error

    })
# ==========================================================
# LEADERBOARD
# ==========================================================

@teacher_bp.route("/leaderboard")
@teacher_login_required
def leaderboard():

    ranking = db.session.query(

        User,

        db.func.count(

            Submission.id

        ).label(

            "accepted"

        )

    ).join(

        Submission,

        Submission.student_id == User.id

    ).filter(

        User.role == "student",

        Submission.verdict == "Accepted"

    ).group_by(

        User.id

    ).order_by(

        db.desc(

            "accepted"

        )

    ).all()

    return render_template(

        "teacher/leaderboard.html",

        ranking=ranking

    )


# ==========================================================
# DASHBOARD ANALYTICS
# ==========================================================

@teacher_bp.route("/analytics")
@teacher_login_required
def analytics():

    students = User.query.filter_by(

        role="student"

    ).count()

    teachers = User.query.filter_by(

        role="teacher"

    ).count()

    problems = Problem.query.count()

    assignments = Assignment.query.count()

    submissions = Submission.query.count()

    accepted = Submission.query.filter_by(

        verdict="Accepted"

    ).count()

    acceptance_rate = 0

    if submissions:

        acceptance_rate = round(

            accepted * 100 /

            submissions,

            2

        )

    return render_template(

        "teacher/analytics.html",

        students=students,

        teachers=teachers,

        problems=problems,

        assignments=assignments,

        submissions=submissions,

        accepted=accepted,

        acceptance_rate=acceptance_rate

    )


# ==========================================================
# EXPORT CSV
# ==========================================================

@teacher_bp.route("/export/csv")
@teacher_login_required
def export_csv():

    import csv
    import io

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([

        "Submission ID",

        "Student",

        "Problem",

        "Language",

        "Verdict",

        "Score"

    ])

    submissions = Submission.query.all()

    for submission in submissions:

        student = User.query.get(

            submission.student_id

        )

        problem = Problem.query.get(

            submission.problem_id

        )

        writer.writerow([

            submission.id,

            student.username if student else "",

            problem.title if problem else "",

            submission.language,

            submission.verdict,

            submission.score

        ])

    from flask import Response

    return Response(

        output.getvalue(),

        mimetype="text/csv",

        headers={

            "Content-Disposition":

            "attachment; filename=submissions.csv"

        }

    )


# ==========================================================
# EXPORT JSON
# ==========================================================

@teacher_bp.route("/export/json")
@teacher_login_required
def export_json():

    submissions = Submission.query.all()

    data = []

    for submission in submissions:

        data.append({

            "id": submission.id,

            "student_id": submission.student_id,

            "problem_id": submission.problem_id,

            "language": submission.language,

            "verdict": submission.verdict,

            "score": submission.score,

            "execution_time": submission.execution_time,

            "memory_used": submission.memory_used

        })

    return jsonify(data)


# ==========================================================
# LANGUAGE STATISTICS
# ==========================================================

@teacher_bp.route("/statistics/languages")
@teacher_login_required
def language_statistics():

    languages = {}

    submissions = Submission.query.all()

    for submission in submissions:

        language = submission.language

        languages[language] = (

            languages.get(

                language,

                0

            ) + 1

        )

    return jsonify(languages)


# ==========================================================
# VERDICT STATISTICS
# ==========================================================

@teacher_bp.route("/statistics/verdicts")
@teacher_login_required
def verdict_statistics():

    verdicts = {}

    submissions = Submission.query.all()

    for submission in submissions:

        verdict = submission.verdict

        verdicts[verdict] = (

            verdicts.get(

                verdict,

                0

            ) + 1

        )

    return jsonify(verdicts)


# ==========================================================
# PROBLEM REPORT
# ==========================================================

@teacher_bp.route("/problem/report")
@teacher_login_required
def problem_report():

    report = []

    problems = Problem.query.all()

    for problem in problems:

        total = Submission.query.filter_by(

            problem_id=problem.id

        ).count()

        accepted = Submission.query.filter_by(

            problem_id=problem.id,

            verdict="Accepted"

        ).count()

        report.append({

            "problem": problem.title,

            "submissions": total,

            "accepted": accepted

        })

    return render_template(

        "teacher/problem_report.html",

        report=report

    )


# ==========================================================
# PERFORMANCE REPORT
# ==========================================================

@teacher_bp.route("/performance")
@teacher_login_required
def performance_report():

    average_score = db.session.query(

        db.func.avg(

            Submission.score

        )

    ).scalar() or 0

    average_time = db.session.query(

        db.func.avg(

            Submission.execution_time

        )

    ).scalar() or 0

    return render_template(

        "teacher/performance.html",

        average_score=round(

            average_score,

            2

        ),

        average_time=round(

            average_time,

            4

        )

    )
# ==========================================================
# EDIT PROFILE
# ==========================================================

@teacher_bp.route("/profile/edit", methods=["GET", "POST"])
@teacher_login_required
def edit_profile():

    teacher = current_teacher()

    if request.method == "POST":

        teacher.full_name = request.form.get("full_name")
        teacher.email = request.form.get("email")
        teacher.phone = request.form.get("phone")

        db.session.commit()

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "teacher.profile"
            )
        )

    return render_template(
        "teacher/edit_profile.html",
        teacher=teacher
    )


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@teacher_bp.route(
    "/change-password",
    methods=["GET", "POST"]
)
@teacher_login_required
def change_password():

    teacher = current_teacher()

    if request.method == "POST":

        old_password = request.form.get(
            "old_password"
        )

        new_password = request.form.get(
            "new_password"
        )

        confirm_password = request.form.get(
            "confirm_password"
        )

        if not teacher.check_password(
            old_password
        ):

            flash(
                "Old password is incorrect.",
                "danger"
            )

            return redirect(request.url)

        if new_password != confirm_password:

            flash(
                "Passwords do not match.",
                "warning"
            )

            return redirect(request.url)

        teacher.set_password(
            new_password
        )

        db.session.commit()

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect(
            url_for(
                "teacher.profile"
            )
        )

    return render_template(
        "teacher/change_password.html"
    )


# ==========================================================
# SETTINGS
# ==========================================================

@teacher_bp.route(
    "/settings",
    methods=["GET", "POST"]
)
@teacher_login_required
def settings():

    teacher = current_teacher()

    if request.method == "POST":

        teacher.theme = request.form.get(
            "theme",
            "light"
        )

        teacher.email_notifications = (

            request.form.get(
                "email_notifications"
            ) == "on"

        )

        db.session.commit()

        flash(
            "Settings updated.",
            "success"
        )

        return redirect(
            url_for(
                "teacher.settings"
            )
        )

    return render_template(
        "teacher/settings.html",
        teacher=teacher
    )


# ==========================================================
# NOTIFICATIONS
# ==========================================================

@teacher_bp.route("/notifications")
@teacher_login_required
def notifications():

    notifications = session.get(
        "teacher_notifications",
        []
    )

    return render_template(

        "teacher/notifications.html",

        notifications=notifications

    )


# ==========================================================
# MARK NOTIFICATION READ
# ==========================================================

@teacher_bp.route(
    "/notifications/read/<int:index>"
)
@teacher_login_required
def mark_notification(index):

    notifications = session.get(
        "teacher_notifications",
        []
    )

    if 0 <= index < len(notifications):

        notifications[index]["read"] = True

        session[
            "teacher_notifications"
        ] = notifications

    return redirect(
        url_for(
            "teacher.notifications"
        )
    )


# ==========================================================
# ACTIVITY LOG
# ==========================================================

@teacher_bp.route("/activity")
@teacher_login_required
def activity():

    recent_problems = Problem.query.order_by(

        Problem.id.desc()

    ).limit(10).all()

    recent_assignments = Assignment.query.order_by(

        Assignment.created_at.desc()

    ).limit(10).all()

    return render_template(

        "teacher/activity.html",

        problems=recent_problems,

        assignments=recent_assignments

    )


# ==========================================================
# SECURITY
# ==========================================================

@teacher_bp.route("/security")
@teacher_login_required
def security():

    return render_template(

        "teacher/security.html",

        teacher=current_teacher()

    )


# ==========================================================
# EMAIL PREFERENCES
# ==========================================================

@teacher_bp.route(
    "/email",
    methods=["GET", "POST"]
)
@teacher_login_required
def email_preferences():

    teacher = current_teacher()

    if request.method == "POST":

        teacher.email_notifications = (

            request.form.get(
                "enabled"
            ) == "on"

        )

        db.session.commit()

        flash(

            "Email preferences updated.",

            "success"

        )

        return redirect(

            url_for(

                "teacher.email_preferences"

            )

        )

    return render_template(

        "teacher/email_preferences.html",

        teacher=teacher

    )


# ==========================================================
# LOGOUT
# ==========================================================

@teacher_bp.route("/logout")
@teacher_login_required
def logout():

    session.clear()

    flash(

        "Logged out successfully.",

        "success"

    )

    return redirect(

        url_for(

            "auth.login"

        )

    )
# ==========================================================
# LIVE DASHBOARD API
# ==========================================================

@teacher_bp.route("/api/dashboard")
@teacher_login_required
def api_dashboard():

    return jsonify({

        "students":
            User.query.filter_by(
                role="student"
            ).count(),

        "teachers":
            User.query.filter_by(
                role="teacher"
            ).count(),

        "problems":
            Problem.query.count(),

        "assignments":
            Assignment.query.count(),

        "submissions":
            Submission.query.count(),

        "testcases":
            TestCase.query.count()

    })


# ==========================================================
# SEARCH STUDENTS API
# ==========================================================

@teacher_bp.route("/api/students")
@teacher_login_required
def api_students():

    keyword = request.args.get(

        "q",

        ""

    )

    students = User.query.filter(

        User.role == "student",

        User.username.ilike(

            f"%{keyword}%"

        )

    ).limit(20).all()

    result = []

    for student in students:

        result.append({

            "id": student.id,

            "username": student.username,

            "email": student.email

        })

    return jsonify(result)


# ==========================================================
# SEARCH PROBLEMS API
# ==========================================================

@teacher_bp.route("/api/problems")
@teacher_login_required
def api_problems():

    keyword = request.args.get(

        "q",

        ""

    )

    problems = Problem.query.filter(

        Problem.title.ilike(

            f"%{keyword}%"

        )

    ).limit(20).all()

    return jsonify([

        {

            "id": p.id,

            "title": p.title,

            "difficulty": p.difficulty

        }

        for p in problems

    ])


# ==========================================================
# LIVE STATISTICS API
# ==========================================================

@teacher_bp.route("/api/statistics")
@teacher_login_required
def api_statistics():

    total = Submission.query.count()

    accepted = Submission.query.filter_by(

        verdict="Accepted"

    ).count()

    wrong = Submission.query.filter_by(

        verdict="Wrong Answer"

    ).count()

    runtime = Submission.query.filter_by(

        verdict="Runtime Error"

    ).count()

    compile_error = Submission.query.filter_by(

        verdict="Compilation Error"

    ).count()

    return jsonify({

        "total": total,

        "accepted": accepted,

        "wrong_answer": wrong,

        "runtime_error": runtime,

        "compile_error": compile_error

    })


# ==========================================================
# RECENT SUBMISSIONS API
# ==========================================================

@teacher_bp.route("/api/recent-submissions")
@teacher_login_required
def recent_submissions_api():

    submissions = Submission.query.order_by(

        Submission.created_at.desc()

    ).limit(15).all()

    data = []

    for submission in submissions:

        data.append({

            "id": submission.id,

            "student": submission.student_id,

            "problem": submission.problem_id,

            "language": submission.language,

            "verdict": submission.verdict,

            "score": submission.score

        })

    return jsonify(data)


# ==========================================================
# SYSTEM STATUS API
# ==========================================================

@teacher_bp.route("/api/status")
@teacher_login_required
def api_status():

    return jsonify({

        "database": True,

        "judge": True,

        "compiler": True,

        "executor": True,

        "docker": True,

        "status": "Running"

    })


# ==========================================================
# HEALTH CHECK
# ==========================================================

@teacher_bp.route("/health")
def health():

    return jsonify({

        "status": "OK",

        "module": "teacher",

        "database": True

    })


# ==========================================================
# ERROR HANDLERS
# ==========================================================

@teacher_bp.errorhandler(403)
def forbidden(error):

    return render_template(

        "errors/403.html"

    ), 403


@teacher_bp.errorhandler(404)
def not_found(error):

    return render_template(

        "errors/404.html"

    ), 404


@teacher_bp.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return render_template(

        "errors/500.html"

    ), 500


# ==========================================================
# PING
# ==========================================================

@teacher_bp.route("/ping")
def ping():

    return jsonify({

        "message": "Teacher module active."

    })
# ==========================================================
# NAVIGATION HELPERS
# ==========================================================

def teacher_home():
    """
    Redirect to teacher dashboard.
    """
    return redirect(

        url_for(

            "teacher.dashboard"

        )

    )


def teacher_profile():
    """
    Redirect to teacher profile.
    """
    return redirect(

        url_for(

            "teacher.profile"

        )

    )


def teacher_problems():
    """
    Redirect to problem list.
    """
    return redirect(

        url_for(

            "teacher.problems"

        )

    )


def teacher_assignments():
    """
    Redirect to assignment list.
    """
    return redirect(

        url_for(

            "teacher.assignments"

        )

    )


def teacher_students():
    """
    Redirect to student list.
    """
    return redirect(

        url_for(

            "teacher.students"

        )

    )


# ==========================================================
# MODULE INFORMATION
# ==========================================================

def module_information():

    return {

        "module": "Teacher Routes",

        "version": "1.0.0",

        "blueprint": teacher_bp.name,

        "url_prefix": teacher_bp.url_prefix

    }


# ==========================================================
# INITIALIZE
# ==========================================================

def initialize():

    return {

        "initialized": True,

        "module": "Teacher Routes",

        "timestamp": datetime.utcnow().isoformat()

    }


# ==========================================================
# VERIFY MODULE
# ==========================================================

def verify():

    return {

        "database": db is not None,

        "blueprint": teacher_bp is not None,

        "judge": callable(judge_submission),

        "routes_loaded": True

    }


# ==========================================================
# MODULE METADATA
# ==========================================================

def metadata():

    return {

        "name": "Lab Auto Grader Teacher Module",

        "version": "1.0.0",

        "author": "Devanshu Ranjan Upadhyay"

    }


# ==========================================================
# READY CHECK
# ==========================================================

def ready():

    report = verify()

    return all(

        report.values()

    )


# ==========================================================
# SHUTDOWN
# ==========================================================

def shutdown():

    db.session.remove()

    return True


# ==========================================================
# MODULE STATUS
# ==========================================================

@teacher_bp.route("/status")
@teacher_login_required
def status():

    return jsonify({

        "status": "Running",

        "metadata": metadata(),

        "verify": verify()

    })


# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [

    # Blueprint
    "teacher_bp",

    # Authentication
    "teacher_login_required",
    "current_teacher",

    # Dashboard
    "dashboard",
    "home",
    "profile",

    # Problems
    "problems",
    "add_problem",
    "edit_problem",
    "delete_problem",
    "problem_details",
    "preview_problem",

    # Test Cases
    "testcases",
    "add_testcase",
    "edit_testcase",
    "delete_testcase",
    "upload_testcases",
    "download_testcases",
    "toggle_hidden",

    # Assignments
    "assignments",
    "add_assignment",
    "edit_assignment",
    "delete_assignment",
    "assignment_details",
    "assign_problem",
    "remove_problem",

    # Students
    "students",
    "student_profile",
    "student_submissions",
    "student_progress",
    "enable_student",
    "disable_student",

    # Submissions
    "submissions",
    "submission_details",
    "download_submission",
    "rejudge",
    "delete_submission",

    # Reports
    "leaderboard",
    "analytics",
    "performance_report",
    "problem_report",

    # APIs
    "dashboard_api",
    "api_dashboard",
    "api_students",
    "api_problems",
    "api_statistics",
    "recent_submissions_api",
    "api_status",

    # Utilities
    "initialize",
    "verify",
    "metadata",
    "module_information",
    "ready",
    "shutdown"
]