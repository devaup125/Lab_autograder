"""
==========================================================
Lab Auto Grader
Student Routes
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

from judge.compiler import compile_source
from judge.executor import execute_program
from judge.judge import judge_submission

# ==========================================================
# BLUEPRINT
# ==========================================================

student_bp = Blueprint(

    "student",

    __name__,

    url_prefix="/student"

)

# ==========================================================
# LOGIN REQUIRED
# ==========================================================

def student_login_required(view):

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

        user = User.query.get(

            session["user_id"]

        )

        if user is None:

            session.clear()

            return redirect(

                url_for("auth.login")

            )

        if user.role != "student":

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
# CURRENT USER
# ==========================================================

def current_student():

    if "user_id" not in session:

        return None

    return User.query.get(

        session["user_id"]

    )


# ==========================================================
# DASHBOARD
# ==========================================================

@student_bp.route("/")

@student_login_required
def dashboard():

    student = current_student()

    total_problems = Problem.query.count()

    solved = Submission.query.filter_by(

        student_id=student.id,

        verdict="Accepted"

    ).count()

    submissions = Submission.query.filter_by(

        student_id=student.id

    ).count()

    recent = Submission.query.filter_by(

        student_id=student.id

    ).order_by(

        desc(

            Submission.created_at

        )

    ).limit(

        10

    ).all()

    return render_template(

        "student/dashboard.html",

        student=student,

        total_problems=total_problems,

        solved=solved,

        submissions=submissions,

        recent_submissions=recent

    )


# ==========================================================
# HOME
# ==========================================================

@student_bp.route("/home")

@student_login_required
def home():

    return redirect(

        url_for(

            "student.dashboard"

        )

    )


# ==========================================================
# PROFILE
# ==========================================================

@student_bp.route("/profile")

@student_login_required
def profile():

    student = current_student()

    return render_template(

        "student/profile.html",

        student=student

    )


# ==========================================================
# ACTIVE ASSIGNMENTS
# ==========================================================

@student_bp.route("/assignments")

@student_login_required
def assignments():

    student = current_student()

    assignments = Assignment.query.order_by(

        desc(

            Assignment.created_at

        )

    ).all()

    return render_template(

        "student/assignments.html",

        student=student,

        assignments=assignments

    )


# ==========================================================
# DASHBOARD API
# ==========================================================

@student_bp.route("/dashboard/api")

@student_login_required
def dashboard_api():

    student = current_student()

    return jsonify({

        "student":

            student.username,

        "problems":

            Problem.query.count(),

        "submissions":

            Submission.query.filter_by(

                student_id=student.id

            ).count(),

        "accepted":

            Submission.query.filter_by(

                student_id=student.id,

                verdict="Accepted"

            ).count()

    })


# ==========================================================
# ABOUT
# ==========================================================

@student_bp.route("/about")

@student_login_required
def about():

    return render_template(

        "student/about.html"

    )
# ==========================================================
# PROBLEM LIST
# ==========================================================

@student_bp.route("/problems")
@student_login_required
def problems():

    student = current_student()

    page = request.args.get(

        "page",

        1,

        type=int

    )

    difficulty = request.args.get(

        "difficulty",

        ""

    )

    keyword = request.args.get(

        "q",

        ""

    )

    query = Problem.query

    if difficulty:

        query = query.filter_by(

            difficulty=difficulty

        )

    if keyword:

        query = query.filter(

            Problem.title.ilike(

                f"%{keyword}%"

            )

        )

    pagination = query.order_by(

        Problem.id.asc()

    ).paginate(

        page=page,

        per_page=20,

        error_out=False

    )

    solved = {

        s.problem_id

        for s in Submission.query.filter_by(

            student_id=student.id,

            verdict="Accepted"

        ).all()

    }

    return render_template(

        "student/problems.html",

        problems=pagination.items,

        pagination=pagination,

        solved=solved,

        difficulty=difficulty,

        keyword=keyword

    )


# ==========================================================
# PROBLEM DETAILS
# ==========================================================

@student_bp.route("/problem/<int:problem_id>")
@student_login_required
def problem(problem_id):

    student = current_student()

    problem = Problem.query.get_or_404(

        problem_id

    )

    latest_submission = Submission.query.filter_by(

        student_id=student.id,

        problem_id=problem.id

    ).order_by(

        Submission.created_at.desc()

    ).first()

    accepted = Submission.query.filter_by(

        student_id=student.id,

        problem_id=problem.id,

        verdict="Accepted"

    ).count()

    return render_template(

        "student/problem.html",

        problem=problem,

        latest_submission=latest_submission,

        accepted=accepted > 0

    )


# ==========================================================
# SEARCH
# ==========================================================

@student_bp.route("/search")
@student_login_required
def search():

    keyword = request.args.get(

        "q",

        ""

    )

    results = Problem.query.filter(

        Problem.title.ilike(

            f"%{keyword}%"

        )

    ).all()

    return render_template(

        "student/search.html",

        keyword=keyword,

        results=results

    )


# ==========================================================
# DIFFICULTY FILTER
# ==========================================================

@student_bp.route("/difficulty/<level>")
@student_login_required
def difficulty(level):

    problems = Problem.query.filter_by(

        difficulty=level

    ).all()

    return render_template(

        "student/difficulty.html",

        problems=problems,

        level=level

    )


# ==========================================================
# FAVORITE PROBLEMS
# ==========================================================

@student_bp.route("/favorites")
@student_login_required
def favorites():

    student = current_student()

    favorites = Problem.query.join(

        Submission,

        Submission.problem_id == Problem.id

    ).filter(

        Submission.student_id == student.id,

        Submission.favorite == True

    ).all()

    return render_template(

        "student/favorites.html",

        problems=favorites

    )


# ==========================================================
# PROBLEM STATS
# ==========================================================

@student_bp.route("/problem/<int:problem_id>/stats")
@student_login_required
def problem_statistics(problem_id):

    total = Submission.query.filter_by(

        problem_id=problem_id

    ).count()

    accepted = Submission.query.filter_by(

        problem_id=problem_id,

        verdict="Accepted"

    ).count()

    rate = 0

    if total:

        rate = round(

            accepted * 100 / total,

            2

        )

    return jsonify({

        "problem_id": problem_id,

        "submissions": total,

        "accepted": accepted,

        "acceptance_rate": rate

    })


# ==========================================================
# SOLVED PROBLEMS
# ==========================================================

@student_bp.route("/solved")
@student_login_required
def solved():

    student = current_student()

    solved_ids = [

        s.problem_id

        for s in Submission.query.filter_by(

            student_id=student.id,

            verdict="Accepted"

        ).all()

    ]

    problems = Problem.query.filter(

        Problem.id.in_(

            solved_ids

        )

    ).all()

    return render_template(

        "student/solved.html",

        problems=problems

    )
# ==========================================================
# CODE EDITOR
# ==========================================================

@student_bp.route("/problem/<int:problem_id>/editor")
@student_login_required
def editor(problem_id):
    """
    Online code editor.
    """

    problem = Problem.query.get_or_404(

        problem_id

    )

    student = current_student()

    last_submission = Submission.query.filter_by(

        student_id=student.id,

        problem_id=problem.id

    ).order_by(

        Submission.created_at.desc()

    ).first()

    starter_code = getattr(

        problem,

        "starter_code",

        ""

    )

    language = request.args.get(

        "language",

        "Python"

    )

    code = starter_code

    if last_submission:

        code = last_submission.source_code

        language = last_submission.language

    return render_template(

        "student/editor.html",

        problem=problem,

        language=language,

        code=code

    )


# ==========================================================
# RUN CODE
# ==========================================================

@student_bp.route("/run", methods=["POST"])
@student_login_required
def run_code():

    language = request.form.get(

        "language"

    )

    source_code = request.form.get(

        "source_code"

    )

    custom_input = request.form.get(

        "custom_input",

        ""

    )

    compile_result = compile_source(

        language,

        source_code

    )

    if not compile_result.success:

        return jsonify({

            "success": False,

            "compile_error":

                compile_result.error_output

        })

    execution = execute_program(

        compile_result,

        custom_input

    )

    return jsonify({

        "success":

            execution.success,

        "stdout":

            execution.stdout,

        "stderr":

            execution.stderr,

        "execution_time":

            execution.execution_time,

        "memory":

            execution.memory_used

    })


# ==========================================================
# COMPILE ONLY
# ==========================================================

@student_bp.route("/compile", methods=["POST"])
@student_login_required
def compile_code():

    language = request.form.get(

        "language"

    )

    source = request.form.get(

        "source_code"

    )

    result = compile_source(

        language,

        source

    )

    return jsonify({

        "success":

            result.success,

        "stdout":

            result.compile_output,

        "stderr":

            result.error_output,

        "compile_time":

            result.compile_time

    })


# ==========================================================
# SAVE DRAFT
# ==========================================================

@student_bp.route("/draft/save", methods=["POST"])
@student_login_required
def save_draft():

    session["draft"] = {

        "problem_id":

            request.form.get(

                "problem_id"

            ),

        "language":

            request.form.get(

                "language"

            ),

        "source_code":

            request.form.get(

                "source_code"

            )

    }

    return jsonify({

        "success": True

    })


# ==========================================================
# LOAD DRAFT
# ==========================================================

@student_bp.route("/draft/load/<int:problem_id>")
@student_login_required
def load_draft(problem_id):

    draft = session.get(

        "draft"

    )

    if (

        draft

        and

        int(

            draft["problem_id"]

        ) == problem_id

    ):

        return jsonify({

            "success": True,

            "language":

                draft["language"],

            "source_code":

                draft["source_code"]

        })

    return jsonify({

        "success": False

    })


# ==========================================================
# RESET EDITOR
# ==========================================================

@student_bp.route("/editor/reset/<int:problem_id>")
@student_login_required
def reset_editor(problem_id):

    problem = Problem.query.get_or_404(

        problem_id

    )

    return jsonify({

        "success": True,

        "code":

            getattr(

                problem,

                "starter_code",

                ""

            )

    })


# ==========================================================
# AVAILABLE LANGUAGES
# ==========================================================

@student_bp.route("/languages")
@student_login_required
def languages():

    return jsonify({

        "languages": [

            "Python",

            "C",

            "C++",

            "Java",

            "JavaScript"

        ]

    })


# ==========================================================
# EXECUTION STATUS
# ==========================================================

@student_bp.route("/run/status")
@student_login_required
def execution_status():

    return jsonify({

        "status": "Ready",

        "compiler": True,

        "executor": True,

        "docker": True

    })
# ==========================================================
# SUBMIT SOLUTION
# ==========================================================

@student_bp.route("/submit", methods=["POST"])
@student_login_required
def submit_solution():

    student = current_student()

    problem_id = request.form.get(

        "problem_id",

        type=int

    )

    language = request.form.get(

        "language"

    )

    source_code = request.form.get(

        "source_code"

    )

    problem = Problem.query.get_or_404(

        problem_id

    )

    submission = Submission(

        student_id=student.id,

        problem_id=problem.id,

        language=language,

        source_code=source_code,

        status="Pending",

        verdict="Pending"

    )

    db.session.add(

        submission

    )

    db.session.commit()

    judge_result = judge_submission(

        submission

    )

    submission.status = "Completed"

    submission.verdict = judge_result.verdict

    submission.score = judge_result.score

    submission.execution_time = (

        judge_result.execution_time

    )

    submission.memory_used = (

        judge_result.memory_used

    )

    submission.passed_testcases = (

        judge_result.passed_testcases

    )

    submission.total_testcases = (

        judge_result.total_testcases

    )

    submission.compile_error = (

        judge_result.compile_error

    )

    submission.runtime_error = (

        judge_result.runtime_error

    )

    db.session.commit()

    flash(

        f"Verdict: {judge_result.verdict}",

        "success"

    )

    return redirect(

        url_for(

            "student.submission_result",

            submission_id=submission.id

        )

    )


# ==========================================================
# SUBMISSION RESULT
# ==========================================================

@student_bp.route(
    "/submission/<int:submission_id>"
)
@student_login_required
def submission_result(
    submission_id
):

    student = current_student()

    submission = Submission.query.get_or_404(

        submission_id

    )

    if submission.student_id != student.id:

        flash(

            "Access denied.",

            "danger"

        )

        return redirect(

            url_for(

                "student.dashboard"

            )

        )

    return render_template(

        "student/submission_result.html",

        submission=submission

    )


# ==========================================================
# QUICK SUBMIT API
# ==========================================================

@student_bp.route(
    "/submit/api",

    methods=["POST"]

)
@student_login_required
def submit_api():

    student = current_student()

    data = request.get_json()

    submission = Submission(

        student_id=student.id,

        problem_id=data["problem_id"],

        language=data["language"],

        source_code=data["source_code"],

        status="Pending",

        verdict="Pending"

    )

    db.session.add(

        submission

    )

    db.session.commit()

    result = judge_submission(

        submission

    )

    submission.status = "Completed"

    submission.verdict = result.verdict

    submission.score = result.score

    submission.execution_time = (

        result.execution_time

    )

    submission.memory_used = (

        result.memory_used

    )

    db.session.commit()

    return jsonify({

        "success": True,

        "submission_id":

            submission.id,

        "verdict":

            result.verdict,

        "score":

            result.score,

        "execution_time":

            result.execution_time,

        "memory_used":

            result.memory_used

    })


# ==========================================================
# LAST SUBMISSION
# ==========================================================

@student_bp.route(
    "/problem/<int:problem_id>/latest"
)
@student_login_required
def latest_submission(
    problem_id
):

    student = current_student()

    submission = Submission.query.filter_by(

        student_id=student.id,

        problem_id=problem_id

    ).order_by(

        Submission.created_at.desc()

    ).first()

    if submission is None:

        return jsonify({

            "success": False

        })

    return jsonify({

        "success": True,

        "submission_id":

            submission.id,

        "verdict":

            submission.verdict,

        "score":

            submission.score,

        "language":

            submission.language

    })


# ==========================================================
# RESUBMIT
# ==========================================================

@student_bp.route(
    "/submission/<int:submission_id>/resubmit"
)
@student_login_required
def resubmit(
    submission_id
):

    student = current_student()

    submission = Submission.query.get_or_404(

        submission_id

    )

    if submission.student_id != student.id:

        flash(

            "Access denied.",

            "danger"

        )

        return redirect(

            url_for(

                "student.dashboard"

            )

        )

    return render_template(

        "student/editor.html",

        language=submission.language,

        code=submission.source_code,

        problem=Problem.query.get(

            submission.problem_id

        )

    )


# ==========================================================
# VERDICT DETAILS
# ==========================================================

@student_bp.route(
    "/submission/<int:submission_id>/verdict"
)
@student_login_required
def verdict_details(
    submission_id
):

    submission = Submission.query.get_or_404(

        submission_id

    )

    return jsonify({

        "verdict":

            submission.verdict,

        "score":

            submission.score,

        "execution_time":

            submission.execution_time,

        "memory_used":

            submission.memory_used,

        "passed":

            submission.passed_testcases,

        "total":

            submission.total_testcases,

        "compile_error":

            submission.compile_error,

        "runtime_error":

            submission.runtime_error

    })
# ==========================================================
# SUBMISSION HISTORY
# ==========================================================

@student_bp.route("/submissions")
@student_login_required
def submissions():

    student = current_student()

    page = request.args.get(

        "page",

        1,

        type=int

    )

    pagination = Submission.query.filter_by(

        student_id=student.id

    ).order_by(

        Submission.created_at.desc()

    ).paginate(

        page=page,

        per_page=20,

        error_out=False

    )

    return render_template(

        "student/submissions.html",

        submissions=pagination.items,

        pagination=pagination

    )


# ==========================================================
# SUBMISSION DETAILS
# ==========================================================

@student_bp.route(
    "/submissions/<int:submission_id>"
)
@student_login_required
def submission_details(
    submission_id
):

    student = current_student()

    submission = Submission.query.get_or_404(

        submission_id

    )

    if submission.student_id != student.id:

        flash(

            "Access denied.",

            "danger"

        )

        return redirect(

            url_for(

                "student.submissions"

            )

        )

    return render_template(

        "student/submission_details.html",

        submission=submission

    )


# ==========================================================
# VIEW SOURCE CODE
# ==========================================================

@student_bp.route(
    "/submission/<int:submission_id>/source"
)
@student_login_required
def view_source(
    submission_id
):

    student = current_student()

    submission = Submission.query.get_or_404(

        submission_id

    )

    if submission.student_id != student.id:

        return jsonify({

            "success": False

        }), 403

    return jsonify({

        "success": True,

        "language":

            submission.language,

        "source_code":

            submission.source_code

    })


# ==========================================================
# DOWNLOAD SOURCE
# ==========================================================

@student_bp.route(
    "/submission/<int:submission_id>/download"
)
@student_login_required
def download_source(
    submission_id
):

    student = current_student()

    submission = Submission.query.get_or_404(

        submission_id

    )

    if submission.student_id != student.id:

        flash(

            "Access denied.",

            "danger"

        )

        return redirect(

            url_for(

                "student.submissions"

            )

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
# DELETE SUBMISSION
# ==========================================================

@student_bp.route(
    "/submission/<int:submission_id>/delete",

    methods=["POST"]

)
@student_login_required
def delete_submission(
    submission_id
):

    student = current_student()

    submission = Submission.query.get_or_404(

        submission_id

    )

    if submission.student_id != student.id:

        flash(

            "Access denied.",

            "danger"

        )

        return redirect(

            url_for(

                "student.submissions"

            )

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

            "student.submissions"

        )

    )


# ==========================================================
# SUBMISSION SEARCH
# ==========================================================

@student_bp.route("/submission/search")
@student_login_required
def search_submission():

    student = current_student()

    verdict = request.args.get(

        "verdict",

        ""

    )

    language = request.args.get(

        "language",

        ""

    )

    query = Submission.query.filter_by(

        student_id=student.id

    )

    if verdict:

        query = query.filter_by(

            verdict=verdict

        )

    if language:

        query = query.filter_by(

            language=language

        )

    results = query.order_by(

        Submission.created_at.desc()

    ).all()

    return render_template(

        "student/submission_search.html",

        submissions=results,

        verdict=verdict,

        language=language

    )


# ==========================================================
# SUBMISSION STATISTICS
# ==========================================================

@student_bp.route("/submission/stats")
@student_login_required
def submission_stats():

    student = current_student()

    submissions = Submission.query.filter_by(

        student_id=student.id

    ).all()

    total = len(submissions)

    accepted = sum(

        1

        for s in submissions

        if s.verdict == "Accepted"

    )

    runtime_errors = sum(

        1

        for s in submissions

        if s.verdict == "Runtime Error"

    )

    wrong_answers = sum(

        1

        for s in submissions

        if s.verdict == "Wrong Answer"

    )

    return jsonify({

        "total":

            total,

        "accepted":

            accepted,

        "wrong_answers":

            wrong_answers,

        "runtime_errors":

            runtime_errors,

        "acceptance_rate":

            round(

                accepted * 100 / total,

                2

            ) if total else 0

    })
# ==========================================================
# LEADERBOARD
# ==========================================================

@student_bp.route("/leaderboard")
@student_login_required
def leaderboard():

    students = db.session.query(

        User.id,
        User.username,
        db.func.count(Submission.id).label("total"),
        db.func.sum(
            db.case(
                (Submission.verdict == "Accepted", 1),
                else_=0
            )
        ).label("accepted")

    ).join(

        Submission,
        Submission.student_id == User.id

    ).filter(

        User.role == "student"

    ).group_by(

        User.id

    ).all()

    board = []

    for student in students:

        rate = 0

        if student.total:

            rate = round(

                student.accepted * 100 /
                student.total,

                2

            )

        board.append({

            "id": student.id,

            "username": student.username,

            "total": student.total,

            "accepted": student.accepted,

            "rate": rate

        })

    board.sort(

        key=lambda x: (

            -x["accepted"],

            -x["rate"]

        )

    )

    return render_template(

        "student/leaderboard.html",

        leaderboard=board

    )


# ==========================================================
# MY RANK
# ==========================================================

@student_bp.route("/rank")
@student_login_required
def my_rank():

    student = current_student()

    students = db.session.query(

        User.id,

        db.func.sum(
            db.case(
                (Submission.verdict == "Accepted", 1),
                else_=0
            )
        ).label("accepted")

    ).join(

        Submission

    ).filter(

        User.role == "student"

    ).group_by(

        User.id

    ).all()

    ranking = sorted(

        students,

        key=lambda x: (

            x.accepted or 0

        ),

        reverse=True

    )

    rank = None

    for index, item in enumerate(

        ranking,

        start=1

    ):

        if item.id == student.id:

            rank = index

            break

    return jsonify({

        "rank": rank,

        "students": len(ranking)

    })


# ==========================================================
# PERSONAL PROGRESS
# ==========================================================

@student_bp.route("/progress")
@student_login_required
def progress():

    student = current_student()

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

        "student/progress.html",

        total=total,

        solved=solved,

        attempted=attempted,

        progress=progress

    )


# ==========================================================
# MY STATISTICS
# ==========================================================

@student_bp.route("/statistics")
@student_login_required
def statistics():

    student = current_student()

    submissions = Submission.query.filter_by(

        student_id=student.id

    ).all()

    languages = {}

    for submission in submissions:

        language = submission.language

        languages[language] = (

            languages.get(

                language,

                0

            ) + 1

        )

    average_score = 0

    if submissions:

        average_score = round(

            sum(

                s.score

                for s in submissions

            ) / len(submissions),

            2

        )

    return render_template(

        "student/statistics.html",

        submissions=len(submissions),

        average_score=average_score,

        languages=languages

    )


# ==========================================================
# PROBLEM ANALYTICS
# ==========================================================

@student_bp.route("/problem/<int:problem_id>/analytics")
@student_login_required
def problem_analytics(

    problem_id

):

    total = Submission.query.filter_by(

        problem_id=problem_id

    ).count()

    accepted = Submission.query.filter_by(

        problem_id=problem_id,

        verdict="Accepted"

    ).count()

    avg_score = db.session.query(

        db.func.avg(

            Submission.score

        )

    ).filter_by(

        problem_id=problem_id

    ).scalar()

    return jsonify({

        "problem": problem_id,

        "submissions": total,

        "accepted": accepted,

        "average_score":

            round(

                avg_score or 0,

                2

            )

    })


# ==========================================================
# ACHIEVEMENTS
# ==========================================================

@student_bp.route("/achievements")
@student_login_required
def achievements():

    student = current_student()

    accepted = Submission.query.filter_by(

        student_id=student.id,

        verdict="Accepted"

    ).count()

    badges = []

    if accepted >= 1:

        badges.append(

            "First Accepted"

        )

    if accepted >= 10:

        badges.append(

            "Problem Solver"

        )

    if accepted >= 50:

        badges.append(

            "Advanced Coder"

        )

    if accepted >= 100:

        badges.append(

            "Coding Master"

        )

    return render_template(

        "student/achievements.html",

        badges=badges,

        accepted=accepted

    )


# ==========================================================
# PERFORMANCE API
# ==========================================================

@student_bp.route("/performance/api")
@student_login_required
def performance_api():

    student = current_student()

    submissions = Submission.query.filter_by(

        student_id=student.id

    ).count()

    accepted = Submission.query.filter_by(

        student_id=student.id,

        verdict="Accepted"

    ).count()

    return jsonify({

        "submissions": submissions,

        "accepted": accepted,

        "success_rate":

            round(

                accepted * 100 /

                submissions,

                2

            )

            if submissions

            else 0

    })
# ==========================================================
# ASSIGNMENT LIST
# ==========================================================

@student_bp.route("/assignments/list")
@student_login_required
def assignment_list():

    assignments = Assignment.query.order_by(

        Assignment.deadline.asc()

    ).all()

    return render_template(

        "student/assignment_list.html",

        assignments=assignments

    )


# ==========================================================
# ASSIGNMENT DETAILS
# ==========================================================

@student_bp.route("/assignment/<int:assignment_id>")
@student_login_required
def assignment_details(

    assignment_id

):

    assignment = Assignment.query.get_or_404(

        assignment_id

    )

    problems = Problem.query.filter_by(

        assignment_id=assignment.id

    ).all()

    student = current_student()

    submissions = Submission.query.filter_by(

        student_id=student.id,

        assignment_id=assignment.id

    ).all()

    return render_template(

        "student/assignment_details.html",

        assignment=assignment,

        problems=problems,

        submissions=submissions

    )


# ==========================================================
# ASSIGNMENT PROBLEMS
# ==========================================================

@student_bp.route(
    "/assignment/<int:assignment_id>/problems"
)
@student_login_required
def assignment_problems(

    assignment_id

):

    assignment = Assignment.query.get_or_404(

        assignment_id

    )

    problems = Problem.query.filter_by(

        assignment_id=assignment.id

    ).all()

    return render_template(

        "student/assignment_problems.html",

        assignment=assignment,

        problems=problems

    )


# ==========================================================
# ASSIGNMENT SUBMISSIONS
# ==========================================================

@student_bp.route(
    "/assignment/<int:assignment_id>/submissions"
)
@student_login_required
def assignment_submissions(

    assignment_id

):

    student = current_student()

    submissions = Submission.query.filter_by(

        student_id=student.id,

        assignment_id=assignment_id

    ).order_by(

        Submission.created_at.desc()

    ).all()

    return render_template(

        "student/assignment_submissions.html",

        submissions=submissions,

        assignment_id=assignment_id

    )


# ==========================================================
# ASSIGNMENT GRADES
# ==========================================================

@student_bp.route(
    "/assignment/<int:assignment_id>/grades"
)
@student_login_required
def assignment_grades(

    assignment_id

):

    student = current_student()

    submissions = Submission.query.filter_by(

        student_id=student.id,

        assignment_id=assignment_id

    ).all()

    total_score = sum(

        s.score

        for s in submissions

    )

    max_score = len(submissions) * 100

    percentage = 0

    if max_score:

        percentage = round(

            total_score * 100 /

            max_score,

            2

        )

    return render_template(

        "student/assignment_grades.html",

        submissions=submissions,

        total_score=total_score,

        percentage=percentage

    )


# ==========================================================
# ASSIGNMENT DEADLINE
# ==========================================================

@student_bp.route(
    "/assignment/<int:assignment_id>/deadline"
)
@student_login_required
def assignment_deadline(

    assignment_id

):

    assignment = Assignment.query.get_or_404(

        assignment_id

    )

    return jsonify({

        "deadline":

            assignment.deadline.isoformat(),

        "is_closed":

            datetime.utcnow() >

            assignment.deadline

    })


# ==========================================================
# ASSIGNMENT PROGRESS
# ==========================================================

@student_bp.route(
    "/assignment/<int:assignment_id>/progress"
)
@student_login_required
def assignment_progress(

    assignment_id

):

    student = current_student()

    total = Problem.query.filter_by(

        assignment_id=assignment_id

    ).count()

    solved = Submission.query.filter_by(

        assignment_id=assignment_id,

        student_id=student.id,

        verdict="Accepted"

    ).count()

    progress = 0

    if total:

        progress = round(

            solved * 100 /

            total,

            2

        )

    return jsonify({

        "total_problems": total,

        "solved": solved,

        "progress": progress

    })


# ==========================================================
# UPCOMING DEADLINES
# ==========================================================

@student_bp.route("/deadlines")
@student_login_required
def upcoming_deadlines():

    assignments = Assignment.query.filter(

        Assignment.deadline >

        datetime.utcnow()

    ).order_by(

        Assignment.deadline.asc()

    ).all()

    return render_template(

        "student/deadlines.html",

        assignments=assignments

    )


# ==========================================================
# MY GRADES
# ==========================================================

@student_bp.route("/grades")
@student_login_required
def my_grades():

    student = current_student()

    assignments = Assignment.query.all()

    gradebook = []

    for assignment in assignments:

        submissions = Submission.query.filter_by(

            student_id=student.id,

            assignment_id=assignment.id

        ).all()

        score = sum(

            s.score

            for s in submissions

        )

        gradebook.append({

            "assignment":

                assignment,

            "score":

                score

        })

    return render_template(

        "student/grades.html",

        gradebook=gradebook

    )
# ==========================================================
# PROFILE
# ==========================================================

@student_bp.route("/profile/edit", methods=["GET", "POST"])
@student_login_required
def edit_profile():

    student = current_student()

    if request.method == "POST":

        student.full_name = request.form.get(

            "full_name"

        )

        student.email = request.form.get(

            "email"

        )

        student.phone = request.form.get(

            "phone"

        )

        db.session.commit()

        flash(

            "Profile updated successfully.",

            "success"

        )

        return redirect(

            url_for(

                "student.profile"

            )

        )

    return render_template(

        "student/edit_profile.html",

        student=student

    )


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@student_bp.route("/change-password", methods=["GET", "POST"])
@student_login_required
def change_password():

    student = current_student()

    if request.method == "POST":

        old_password = request.form.get(

            "old_password"

        )

        new_password = request.form.get(

            "new_password"

        )

        confirm = request.form.get(

            "confirm_password"

        )

        if not student.check_password(

            old_password

        ):

            flash(

                "Old password is incorrect.",

                "danger"

            )

            return redirect(

                url_for(

                    "student.change_password"

                )

            )

        if new_password != confirm:

            flash(

                "Passwords do not match.",

                "warning"

            )

            return redirect(

                url_for(

                    "student.change_password"

                )

            )

        student.set_password(

            new_password

        )

        db.session.commit()

        flash(

            "Password changed successfully.",

            "success"

        )

        return redirect(

            url_for(

                "student.profile"

            )

        )

    return render_template(

        "student/change_password.html"

    )


# ==========================================================
# ACCOUNT SETTINGS
# ==========================================================

@student_bp.route("/settings", methods=["GET", "POST"])
@student_login_required
def settings():

    student = current_student()

    if request.method == "POST":

        student.theme = request.form.get(

            "theme",

            "light"

        )

        student.editor_language = request.form.get(

            "editor_language",

            "Python"

        )

        db.session.commit()

        flash(

            "Settings updated.",

            "success"

        )

        return redirect(

            url_for(

                "student.settings"

            )

        )

    return render_template(

        "student/settings.html",

        student=student

    )


# ==========================================================
# ACTIVITY LOG
# ==========================================================

@student_bp.route("/activity")
@student_login_required
def activity():

    student = current_student()

    submissions = Submission.query.filter_by(

        student_id=student.id

    ).order_by(

        Submission.created_at.desc()

    ).limit(

        50

    ).all()

    return render_template(

        "student/activity.html",

        submissions=submissions

    )


# ==========================================================
# NOTIFICATIONS
# ==========================================================

@student_bp.route("/notifications")
@student_login_required
def notifications():

    notifications = session.get(

        "notifications",

        []

    )

    return render_template(

        "student/notifications.html",

        notifications=notifications

    )


# ==========================================================
# MARK NOTIFICATION AS READ
# ==========================================================

@student_bp.route("/notifications/read/<int:index>")
@student_login_required
def read_notification(index):

    notifications = session.get(

        "notifications",

        []

    )

    if 0 <= index < len(notifications):

        notifications[index]["read"] = True

        session["notifications"] = notifications

    return redirect(

        url_for(

            "student.notifications"

        )

    )


# ==========================================================
# EMAIL PREFERENCES
# ==========================================================

@student_bp.route("/email-preferences", methods=["GET", "POST"])
@student_login_required
def email_preferences():

    student = current_student()

    if request.method == "POST":

        student.email_notifications = (

            request.form.get(

                "email_notifications"

            ) == "on"

        )

        db.session.commit()

        flash(

            "Email preferences updated.",

            "success"

        )

        return redirect(

            url_for(

                "student.email_preferences"

            )

        )

    return render_template(

        "student/email_preferences.html",

        student=student

    )


# ==========================================================
# SECURITY SETTINGS
# ==========================================================

@student_bp.route("/security")
@student_login_required
def security():

    student = current_student()

    return render_template(

        "student/security.html",

        student=student

    )


# ==========================================================
# LOGOUT
# ==========================================================

@student_bp.route("/logout")
@student_login_required
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

@student_bp.route("/api/dashboard")
@student_login_required
def api_dashboard():

    student = current_student()

    total = Submission.query.filter_by(
        student_id=student.id
    ).count()

    accepted = Submission.query.filter_by(
        student_id=student.id,
        verdict="Accepted"
    ).count()

    solved = db.session.query(
        db.func.count(
            db.distinct(
                Submission.problem_id
            )
        )
    ).filter_by(
        student_id=student.id,
        verdict="Accepted"
    ).scalar()

    return jsonify({

        "total_submissions": total,

        "accepted": accepted,

        "solved": solved,

        "acceptance_rate":
            round(
                accepted * 100 / total,
                2
            ) if total else 0

    })


# ==========================================================
# SEARCH API
# ==========================================================

@student_bp.route("/api/problems")
@student_login_required
def api_problem_search():

    keyword = request.args.get(
        "q",
        ""
    )

    problems = Problem.query.filter(

        Problem.title.ilike(

            f"%{keyword}%"

        )

    ).limit(20).all()

    data = []

    for problem in problems:

        data.append({

            "id": problem.id,

            "title": problem.title,

            "difficulty": problem.difficulty

        })

    return jsonify(data)


# ==========================================================
# AUTOSAVE API
# ==========================================================

@student_bp.route("/api/autosave", methods=["POST"])
@student_login_required
def autosave():

    session["autosave"] = {

        "problem_id":
            request.form.get("problem_id"),

        "language":
            request.form.get("language"),

        "source_code":
            request.form.get("source_code")

    }

    return jsonify({

        "success": True

    })


# ==========================================================
# LOAD AUTOSAVE
# ==========================================================

@student_bp.route("/api/autosave/<int:problem_id>")
@student_login_required
def load_autosave(problem_id):

    data = session.get(

        "autosave"

    )

    if (

        data

        and

        int(data["problem_id"]) == problem_id

    ):

        return jsonify({

            "success": True,

            "language":

                data["language"],

            "source_code":

                data["source_code"]

        })

    return jsonify({

        "success": False

    })


# ==========================================================
# RECENT SUBMISSIONS API
# ==========================================================

@student_bp.route("/api/recent")
@student_login_required
def recent_api():

    student = current_student()

    submissions = Submission.query.filter_by(

        student_id=student.id

    ).order_by(

        Submission.created_at.desc()

    ).limit(10).all()

    result = []

    for submission in submissions:

        result.append({

            "id": submission.id,

            "problem":

                submission.problem_id,

            "verdict":

                submission.verdict,

            "score":

                submission.score,

            "time":

                submission.execution_time

        })

    return jsonify(result)


# ==========================================================
# LANGUAGE LIST API
# ==========================================================

@student_bp.route("/api/languages")
@student_login_required
def api_languages():

    return jsonify({

        "languages": [

            "Python",

            "C",

            "C++",

            "Java",

            "JavaScript"

        ]

    })


# ==========================================================
# PROFILE API
# ==========================================================

@student_bp.route("/api/profile")
@student_login_required
def api_profile():

    student = current_student()

    return jsonify({

        "id": student.id,

        "username": student.username,

        "email": student.email,

        "role": student.role

    })


# ==========================================================
# NOTIFICATION API
# ==========================================================

@student_bp.route("/api/notifications")
@student_login_required
def notification_api():

    return jsonify(

        session.get(

            "notifications",

            []

        )

    )


# ==========================================================
# ERROR HANDLERS
# ==========================================================

@student_bp.errorhandler(403)
def forbidden(error):

    return render_template(

        "errors/403.html"

    ), 403


@student_bp.errorhandler(404)
def not_found(error):

    return render_template(

        "errors/404.html"

    ), 404


@student_bp.errorhandler(500)
def internal_error(error):

    db.session.rollback()

    return render_template(

        "errors/500.html"

    ), 500


# ==========================================================
# HEALTH CHECK
# ==========================================================

@student_bp.route("/health")
def health():

    return jsonify({

        "status": "OK",

        "module": "student",

        "database": True

    })
# ==========================================================
# NAVIGATION HELPERS
# ==========================================================

def student_home():
    """
    Redirect to student dashboard.
    """
    return redirect(

        url_for(

            "student.dashboard"

        )

    )


def student_profile():

    return redirect(

        url_for(

            "student.profile"

        )

    )


def student_problems():

    return redirect(

        url_for(

            "student.problems"

        )

    )


def student_submissions():

    return redirect(

        url_for(

            "student.submissions"

        )

    )


# ==========================================================
# ROUTE INFORMATION
# ==========================================================

def route_information():

    return {

        "module":

            "Student Routes",

        "version":

            "1.0.0",

        "blueprint":

            student_bp.name,

        "url_prefix":

            student_bp.url_prefix

    }


# ==========================================================
# INITIALIZATION
# ==========================================================

def initialize():

    return {

        "initialized": True,

        "timestamp":

            datetime.utcnow().isoformat(),

        "module":

            "Student Routes"

    }


# ==========================================================
# VERIFY MODULE
# ==========================================================

def verify():

    return {

        "database":

            db is not None,

        "blueprint":

            student_bp is not None,

        "routes_loaded":

            True

    }


# ==========================================================
# MODULE METADATA
# ==========================================================

def metadata():

    return {

        "name":

            "Lab Auto Grader Student Module",

        "version":

            "1.0.0",

        "author":

            "Devanshu Ranjan Upadhyay"

    }


# ==========================================================
# STATUS
# ==========================================================

@student_bp.route("/status")
@student_login_required
def status():

    return jsonify({

        "status":

            "Running",

        "module":

            metadata(),

        "verify":

            verify()

    })


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
# PUBLIC EXPORTS
# ==========================================================

__all__ = [

    # Blueprint

    "student_bp",

    # Main Routes

    "dashboard",

    "home",

    "profile",

    "problems",

    "problem",

    "editor",

    "run_code",

    "compile_code",

    "submit_solution",

    "submission_result",

    "submissions",

    "submission_details",

    "leaderboard",

    "statistics",

    "progress",

    "assignment_list",

    "assignment_details",

    "assignment_problems",

    "assignment_submissions",

    "assignment_grades",

    "my_grades",

    "activity",

    "notifications",

    "settings",

    "edit_profile",

    "change_password",

    "logout",

    # APIs

    "dashboard_api",

    "submit_api",

    "performance_api",

    "problem_statistics",

    "api_dashboard",

    "api_problem_search",

    "autosave",

    "load_autosave",

    "recent_api",

    "api_languages",

    "api_profile",

    "notification_api",

    # Utilities

    "current_student",

    "student_login_required",

    "initialize",

    "verify",

    "metadata",

    "ready",

    "shutdown"

]