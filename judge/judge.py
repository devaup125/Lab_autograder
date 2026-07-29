"""
==========================================================
Lab Auto Grader
Judge Engine
Part 1
==========================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import logging

from extensions import db

from models.problem import Problem
from models.submission import Submission
from models.testcase import TestCase

from judge.compiler import (
    CompilationResult,
    compile_source
)

from judge.executor import (
    ExecutionResult,
    execute_program,
    cleanup_execution
)

# ==========================================================
# LOGGER
# ==========================================================

logger = logging.getLogger(__name__)

# ==========================================================
# VERDICTS
# ==========================================================

ACCEPTED = "Accepted"

WRONG_ANSWER = "Wrong Answer"

COMPILATION_ERROR = "Compilation Error"

RUNTIME_ERROR = "Runtime Error"

TIME_LIMIT_EXCEEDED = "Time Limit Exceeded"

MEMORY_LIMIT_EXCEEDED = "Memory Limit Exceeded"

INTERNAL_ERROR = "Internal Error"

PENDING = "Pending"

# ==========================================================
# JUDGE RESULT
# ==========================================================

@dataclass
class JudgeResult:

    success: bool = False

    verdict: str = PENDING

    score: float = 0.0

    passed_testcases: int = 0

    failed_testcases: int = 0

    total_testcases: int = 0

    execution_time: float = 0.0

    memory_used: float = 0.0

    compile_result: Optional[
        CompilationResult
    ] = None

    execution_results: List[
        ExecutionResult
    ] = field(default_factory=list)

    compile_error: str = ""

    runtime_error: str = ""

    message: str = ""

    judged_at: datetime = field(
        default_factory=datetime.utcnow
    )

# ==========================================================
# HELPERS
# ==========================================================

def success_result():

    return JudgeResult(

        success=True,

        verdict=ACCEPTED

    )


def failure_result(message):

    return JudgeResult(

        success=False,

        verdict=INTERNAL_ERROR,

        message=message

    )

# ==========================================================
# LOAD PROBLEM
# ==========================================================

def get_problem(problem_id):

    return Problem.query.get(problem_id)

# ==========================================================
# LOAD SUBMISSION
# ==========================================================

def get_submission(submission_id):

    return Submission.query.get(

        submission_id

    )

# ==========================================================
# LOAD TEST CASES
# ==========================================================

def get_testcases(problem_id):

    return TestCase.query.filter_by(

        problem_id=problem_id,

        is_active=True

    ).order_by(

        TestCase.order.asc()

    ).all()

# ==========================================================
# OUTPUT NORMALIZATION
# ==========================================================

def normalize(text):

    if text is None:

        return ""

    return (

        text

        .replace("\r\n", "\n")

        .replace("\r", "\n")

        .strip()

    )

# ==========================================================
# OUTPUT COMPARISON
# ==========================================================

def outputs_match(

    expected,

    actual

):

    return normalize(

        expected

    ) == normalize(

        actual

    )

# ==========================================================
# UPDATE RESULT
# ==========================================================

def update_statistics(

    result,

    execution_result,

    passed

):

    result.execution_results.append(

        execution_result

    )

    result.execution_time += (

        execution_result.execution_time

    )

    result.memory_used = max(

        result.memory_used,

        execution_result.memory_used

    )

    if passed:

        result.passed_testcases += 1

    else:

        result.failed_testcases += 1

# ==========================================================
# SCORE
# ==========================================================

def calculate_score(result):

    if result.total_testcases == 0:

        return 0

    return round(

        (

            result.passed_testcases

            /

            result.total_testcases

        )

        * 100,

        2

    )

# ==========================================================
# COMPILATION
# ==========================================================

def compile_submission(

    submission

):

    compile_result = compile_source(

        submission.language,

        submission.source_code

    )

    return compile_result
# ==========================================================
# TEST CASE VALIDATION
# ==========================================================

def validate_testcase(testcase):
    """
    Validate a testcase before execution.
    """

    if testcase is None:
        raise ValueError("Test case cannot be None.")

    if testcase.input_data is None:
        raise ValueError("Missing testcase input.")

    if testcase.expected_output is None:
        raise ValueError("Missing expected output.")

    return True


# ==========================================================
# TEST CASE RESULT
# ==========================================================

@dataclass
class TestCaseResult:

    testcase_id: int

    passed: bool = False

    verdict: str = PENDING

    input_data: str = ""

    expected_output: str = ""

    actual_output: str = ""

    execution_time: float = 0.0

    memory_used: float = 0.0

    error_message: str = ""


# ==========================================================
# EXECUTE SINGLE TEST CASE
# ==========================================================

def execute_testcase(
    compile_result,
    testcase
):
    """
    Execute a compiled program on one testcase.
    """

    validate_testcase(testcase)

    execution = execute_program(

        compile_result,

        testcase.input_data,

        getattr(
            testcase,
            "time_limit",
            2
        )

    )

    result = TestCaseResult(

        testcase_id=testcase.id,

        input_data=testcase.input_data,

        expected_output=testcase.expected_output,

        actual_output=execution.stdout,

        execution_time=execution.execution_time,

        memory_used=execution.memory_used

    )

    if execution.verdict == "Compilation Error":

        result.verdict = COMPILATION_ERROR

        result.error_message = execution.stderr

        return result, execution

    if execution.verdict == "Runtime Error":

        result.verdict = RUNTIME_ERROR

        result.error_message = execution.stderr

        return result, execution

    if execution.verdict == "Time Limit Exceeded":

        result.verdict = TIME_LIMIT_EXCEEDED

        result.error_message = execution.stderr

        return result, execution

    if execution.verdict == "Memory Limit Exceeded":

        result.verdict = MEMORY_LIMIT_EXCEEDED

        result.error_message = execution.stderr

        return result, execution

    if outputs_match(

        testcase.expected_output,

        execution.stdout

    ):

        result.passed = True

        result.verdict = ACCEPTED

    else:

        result.verdict = WRONG_ANSWER

    return result, execution


# ==========================================================
# JUDGE SINGLE TEST CASE
# ==========================================================

def judge_testcase(
    judge_result,
    compile_result,
    testcase
):
    """
    Judge one testcase.
    """

    testcase_result, execution = execute_testcase(

        compile_result,

        testcase

    )

    update_statistics(

        judge_result,

        execution,

        testcase_result.passed

    )

    if testcase_result.verdict != ACCEPTED:

        judge_result.verdict = testcase_result.verdict

        if testcase_result.verdict == RUNTIME_ERROR:

            judge_result.runtime_error = (

                testcase_result.error_message

            )

    return testcase_result


# ==========================================================
# PUBLIC TEST CASES
# ==========================================================

def public_testcases(problem_id):

    return TestCase.query.filter_by(

        problem_id=problem_id,

        is_active=True,

        is_hidden=False

    ).order_by(

        TestCase.order.asc()

    ).all()


# ==========================================================
# HIDDEN TEST CASES
# ==========================================================

def hidden_testcases(problem_id):

    return TestCase.query.filter_by(

        problem_id=problem_id,

        is_active=True,

        is_hidden=True

    ).order_by(

        TestCase.order.asc()

    ).all()


# ==========================================================
# LOAD ALL TEST CASES
# ==========================================================

def load_all_testcases(problem_id):
    """
    Load public and hidden testcases.
    """

    return (

        public_testcases(problem_id)

        +

        hidden_testcases(problem_id)

    )


# ==========================================================
# VERIFY TEST CASES
# ==========================================================

def verify_testcases(problem_id):

    testcases = load_all_testcases(

        problem_id

    )

    if not testcases:

        raise ValueError(

            "No testcases found."

        )

    return testcases
# ==========================================================
# JUDGE ALL TEST CASES
# ==========================================================

def judge_all_testcases(
    judge_result: JudgeResult,
    compile_result: CompilationResult,
    testcases
):
    """
    Execute all test cases and generate final result.
    """

    judge_result.total_testcases = len(testcases)

    testcase_results = []

    for testcase in testcases:

        testcase_result = judge_testcase(

            judge_result,

            compile_result,

            testcase

        )

        testcase_results.append(

            testcase_result

        )

        # Stop immediately for critical verdicts
        if testcase_result.verdict in (

            COMPILATION_ERROR,

            RUNTIME_ERROR,

            TIME_LIMIT_EXCEEDED,

            MEMORY_LIMIT_EXCEEDED

        ):

            break

    judge_result.score = calculate_score(

        judge_result

    )

    return testcase_results


# ==========================================================
# FINAL VERDICT
# ==========================================================

def determine_final_verdict(
    judge_result: JudgeResult
):
    """
    Determine overall submission verdict.
    """

    if judge_result.total_testcases == 0:

        return INTERNAL_ERROR

    if judge_result.failed_testcases == 0:

        return ACCEPTED

    if judge_result.verdict != PENDING:

        return judge_result.verdict

    return WRONG_ANSWER


# ==========================================================
# FINALIZE RESULT
# ==========================================================

def finalize_result(
    judge_result: JudgeResult
):
    """
    Finalize judging statistics.
    """

    judge_result.verdict = determine_final_verdict(

        judge_result

    )

    judge_result.success = (

        judge_result.verdict == ACCEPTED

    )

    judge_result.score = calculate_score(

        judge_result

    )

    return judge_result


# ==========================================================
# JUDGE COMPILED SUBMISSION
# ==========================================================

def judge_compiled_submission(
    submission: Submission,
    compile_result: CompilationResult
):
    """
    Judge a compiled submission.
    """

    result = JudgeResult(

        compile_result=compile_result

    )

    testcases = verify_testcases(

        submission.problem_id

    )

    judge_all_testcases(

        result,

        compile_result,

        testcases

    )

    finalize_result(result)

    return result


# ==========================================================
# COMPILATION FAILURE
# ==========================================================

def compilation_failed_result(
    compile_result: CompilationResult
):
    """
    Create JudgeResult from compilation failure.
    """

    result = JudgeResult()

    result.success = False

    result.verdict = COMPILATION_ERROR

    result.compile_result = compile_result

    result.compile_error = (

        compile_result.error_output

    )

    result.message = "Compilation failed."

    return result


# ==========================================================
# JUDGE SUBMISSION
# ==========================================================

def judge_submission(
    submission: Submission
):
    """
    Complete judging pipeline.
    """

    compile_result = compile_submission(

        submission

    )

    if not compile_result.success:

        return compilation_failed_result(

            compile_result

        )

    return judge_compiled_submission(

        submission,

        compile_result

    )


# ==========================================================
# QUICK JUDGE
# ==========================================================

def quick_judge(
    language,
    source_code,
    input_data,
    expected_output
):
    """
    Judge without database models.
    Useful for Run Code / Practice Mode.
    """

    compile_result = compile_source(

        language,

        source_code

    )

    if not compile_result.success:

        return compilation_failed_result(

            compile_result

        )

    execution = execute_program(

        compile_result,

        input_data

    )

    result = JudgeResult(

        compile_result=compile_result

    )

    result.total_testcases = 1

    result.execution_results.append(

        execution

    )

    result.execution_time = execution.execution_time

    result.memory_used = execution.memory_used

    if outputs_match(

        expected_output,

        execution.stdout

    ):

        result.passed_testcases = 1

    else:

        result.failed_testcases = 1

    finalize_result(result)

    cleanup_execution(

        execution

    )

    return result


# ==========================================================
# JUDGE SUMMARY
# ==========================================================

def judge_summary(
    result: JudgeResult
):
    """
    Convert JudgeResult to dictionary.
    """

    return {

        "success": result.success,

        "verdict": result.verdict,

        "score": result.score,

        "passed": result.passed_testcases,

        "failed": result.failed_testcases,

        "total": result.total_testcases,

        "execution_time": result.execution_time,

        "memory_used": result.memory_used,

        "compile_error": result.compile_error,

        "runtime_error": result.runtime_error

    }
# ==========================================================
# UPDATE SUBMISSION MODEL
# ==========================================================

def update_submission(
    submission: Submission,
    judge_result: JudgeResult
):
    """
    Persist judge result into the Submission model.
    """

    submission.complete_evaluation(

        verdict=judge_result.verdict,

        score=judge_result.score,

        execution_time=judge_result.execution_time,

        memory_used=judge_result.memory_used,

        passed_testcases=judge_result.passed_testcases,

        total_testcases=judge_result.total_testcases,

        compile_error=judge_result.compile_error,

        runtime_error=judge_result.runtime_error

    )

    db.session.commit()

    return submission


# ==========================================================
# SAVE COMPILATION FAILURE
# ==========================================================

def save_compilation_failure(
    submission: Submission,
    judge_result: JudgeResult
):

    submission.complete_evaluation(

        verdict=COMPILATION_ERROR,

        score=0,

        execution_time=0,

        memory_used=0,

        passed_testcases=0,

        total_testcases=0,

        compile_error=judge_result.compile_error,

        runtime_error=""

    )

    db.session.commit()

    return submission


# ==========================================================
# RE-EVALUATE SUBMISSION
# ==========================================================

def rejudge_submission(
    submission: Submission
):
    """
    Reset and judge again.
    """

    submission.reset()

    db.session.commit()

    result = judge_submission(

        submission

    )

    if result.verdict == COMPILATION_ERROR:

        return save_compilation_failure(

            submission,

            result

        )

    return update_submission(

        submission,

        result

    )


# ==========================================================
# RE-EVALUATE ALL SUBMISSIONS
# ==========================================================

def rejudge_problem(
    problem_id
):

    submissions = Submission.query.filter_by(

        problem_id=problem_id

    ).all()

    updated = []

    for submission in submissions:

        updated.append(

            rejudge_submission(

                submission

            )

        )

    return updated


# ==========================================================
# STORE EXECUTION RESULTS
# ==========================================================

def save_execution_results(
    submission,
    judge_result
):

    submission.last_execution_time = (

        judge_result.execution_time

    )

    submission.last_memory_usage = (

        judge_result.memory_used

    )

    submission.last_score = (

        judge_result.score

    )

    db.session.commit()

    return submission


# ==========================================================
# UPDATE BEST SCORE
# ==========================================================

def update_best_score(
    submission
):

    best = Submission.best_submission(

        submission.student_id,

        submission.problem_id

    )

    if best:

        return best.score

    return submission.score


# ==========================================================
# SUBMISSION STATUS
# ==========================================================

def submission_status(
    submission
):

    return {

        "submission_id":

            submission.id,

        "student_id":

            submission.student_id,

        "problem_id":

            submission.problem_id,

        "status":

            submission.status,

        "verdict":

            submission.verdict,

        "score":

            submission.score,

        "passed":

            submission.passed_testcases,

        "total":

            submission.total_testcases

    }


# ==========================================================
# COMPLETE JUDGE PIPELINE
# ==========================================================

def evaluate_submission(
    submission: Submission
):
    """
    Complete pipeline:
        Compile
        Execute
        Judge
        Save
    """

    result = judge_submission(

        submission

    )

    if result.verdict == COMPILATION_ERROR:

        return save_compilation_failure(

            submission,

            result

        )

    submission = update_submission(

        submission,

        result

    )

    save_execution_results(

        submission,

        result

    )

    return submission
# ==========================================================
# WEIGHTED SCORE CALCULATION
# ==========================================================

def calculate_weighted_score(
    testcase_results
):
    """
    Calculate weighted score from testcase results.
    """

    total_weight = 0.0
    earned_weight = 0.0

    for tc in testcase_results:

        weight = getattr(
            tc,
            "weight",
            1.0
        )

        total_weight += weight

        if tc.passed:
            earned_weight += weight

    if total_weight == 0:
        return 0.0

    return round(

        (earned_weight / total_weight) * 100,

        2

    )


# ==========================================================
# PERFORMANCE GRADE
# ==========================================================

def performance_grade(
    score
):

    if score >= 95:
        return "A+"

    elif score >= 90:
        return "A"

    elif score >= 80:
        return "B"

    elif score >= 70:
        return "C"

    elif score >= 60:
        return "D"

    return "F"


# ==========================================================
# PERFORMANCE LEVEL
# ==========================================================

def performance_level(
    execution_time
):

    if execution_time <= 0.10:

        return "Excellent"

    elif execution_time <= 0.30:

        return "Very Good"

    elif execution_time <= 0.75:

        return "Good"

    elif execution_time <= 1.50:

        return "Average"

    return "Slow"


# ==========================================================
# PARTIAL SCORE
# ==========================================================

def partial_score(
    passed,
    total,
    maximum_score=100
):

    if total == 0:
        return 0

    return round(

        (passed / total)

        * maximum_score,

        2

    )


# ==========================================================
# BONUS SCORE
# ==========================================================

def bonus_score(
    judge_result
):

    bonus = 0

    if judge_result.verdict == ACCEPTED:

        if judge_result.execution_time < 0.10:

            bonus += 5

        elif judge_result.execution_time < 0.25:

            bonus += 3

        if judge_result.memory_used < 32:

            bonus += 2

    return bonus


# ==========================================================
# FINAL SCORE
# ==========================================================

def final_score(
    judge_result
):

    score = judge_result.score

    score += bonus_score(

        judge_result

    )

    return min(

        round(score, 2),

        100

    )


# ==========================================================
# RANKING POINTS
# ==========================================================

def ranking_points(
    judge_result
):

    if judge_result.verdict != ACCEPTED:

        return 0

    score = final_score(

        judge_result

    )

    points = score

    points -= judge_result.execution_time * 5

    points -= judge_result.memory_used * 0.02

    return round(

        max(points, 0),

        2

    )


# ==========================================================
# ANALYTICS
# ==========================================================

def judge_analytics(
    judge_result
):

    return {

        "score":

            final_score(

                judge_result

            ),

        "grade":

            performance_grade(

                judge_result.score

            ),

        "performance":

            performance_level(

                judge_result.execution_time

            ),

        "ranking_points":

            ranking_points(

                judge_result

            ),

        "passed":

            judge_result.passed_testcases,

        "failed":

            judge_result.failed_testcases,

        "total":

            judge_result.total_testcases

    }


# ==========================================================
# SUMMARY CARD
# ==========================================================

def summary_card(
    judge_result
):

    return {

        "verdict":

            judge_result.verdict,

        "score":

            final_score(

                judge_result

            ),

        "grade":

            performance_grade(

                judge_result.score

            ),

        "execution_time":

            judge_result.execution_time,

        "memory_used":

            judge_result.memory_used,

        "ranking_points":

            ranking_points(

                judge_result

            )

    }


# ==========================================================
# LEADERBOARD SCORE
# ==========================================================

def leaderboard_score(
    submission
):

    if submission.verdict != ACCEPTED:

        return 0

    score = submission.score

    score -= submission.execution_time * 5

    score -= submission.memory_used * 0.02

    return round(

        max(score, 0),

        2

    )
# ==========================================================
# BATCH JUDGING
# ==========================================================

def judge_submissions(
    submissions
):
    """
    Judge multiple submissions.
    """

    results = []

    for submission in submissions:

        try:

            result = evaluate_submission(

                submission

            )

            results.append(result)

        except Exception as e:

            logger.exception(e)

    return results


# ==========================================================
# JUDGE ASSIGNMENT
# ==========================================================

def judge_assignment(
    assignment_id
):
    """
    Judge every submission of an assignment.
    """

    submissions = Submission.query.filter_by(

        assignment_id=assignment_id

    ).all()

    return judge_submissions(

        submissions

    )


# ==========================================================
# BULK REJUDGE
# ==========================================================

def bulk_rejudge(
    submission_ids
):

    updated = []

    for submission_id in submission_ids:

        submission = get_submission(

            submission_id

        )

        if submission:

            updated.append(

                rejudge_submission(

                    submission

                )

            )

    return updated


# ==========================================================
# PROBLEM STATISTICS
# ==========================================================

def problem_statistics(
    problem_id
):

    submissions = Submission.query.filter_by(

        problem_id=problem_id

    ).all()

    total = len(submissions)

    accepted = sum(

        1

        for s in submissions

        if s.verdict == ACCEPTED

    )

    average_score = 0

    if total:

        average_score = round(

            sum(

                s.score

                for s in submissions

            ) / total,

            2

        )

    return {

        "problem_id":

            problem_id,

        "total_submissions":

            total,

        "accepted":

            accepted,

        "acceptance_rate":

            round(

                (accepted / total) * 100,

                2

            ) if total else 0,

        "average_score":

            average_score

    }


# ==========================================================
# ASSIGNMENT STATISTICS
# ==========================================================

def assignment_statistics(
    assignment_id
):

    submissions = Submission.query.filter_by(

        assignment_id=assignment_id

    ).all()

    students = {

        s.student_id

        for s in submissions

    }

    return {

        "assignment_id":

            assignment_id,

        "submissions":

            len(submissions),

        "students":

            len(students),

        "accepted":

            sum(

                1

                for s in submissions

                if s.verdict == ACCEPTED

            )

    }


# ==========================================================
# LEADERBOARD
# ==========================================================

def generate_leaderboard(
    problem_id
):

    submissions = Submission.query.filter_by(

        problem_id=problem_id

    ).all()

    board = []

    for submission in submissions:

        board.append({

            "student_id":

                submission.student_id,

            "submission_id":

                submission.id,

            "score":

                leaderboard_score(

                    submission

                ),

            "execution_time":

                submission.execution_time,

            "memory_used":

                submission.memory_used

        })

    board.sort(

        key=lambda x: (

            -x["score"],

            x["execution_time"],

            x["memory_used"]

        )

    )

    return board


# ==========================================================
# BEST SUBMISSIONS
# ==========================================================

def best_submissions(
    problem_id,
    limit=10
):

    leaderboard = generate_leaderboard(

        problem_id

    )

    return leaderboard[:limit]


# ==========================================================
# JUDGE REPORT
# ==========================================================

def judge_report(
    problem_id
):

    return {

        "problem":

            problem_statistics(

                problem_id

            ),

        "leaderboard":

            best_submissions(

                problem_id

            )

    }


# ==========================================================
# STUDENT REPORT
# ==========================================================

def student_report(
    student_id
):

    submissions = Submission.query.filter_by(

        student_id=student_id

    ).all()

    accepted = sum(

        1

        for s in submissions

        if s.verdict == ACCEPTED

    )

    return {

        "student_id":

            student_id,

        "total_submissions":

            len(submissions),

        "accepted":

            accepted,

        "average_score":

            round(

                sum(

                    s.score

                    for s in submissions

                ) / len(submissions),

                2

            )

            if submissions else 0

    }


# ==========================================================
# SYSTEM REPORT
# ==========================================================

def system_report():

    return {

        "submissions":

            Submission.query.count(),

        "problems":

            Problem.query.count(),

        "accepted":

            Submission.query.filter_by(

                verdict=ACCEPTED

            ).count(),

        "pending":

            Submission.query.filter_by(

                verdict=PENDING

            ).count()

    }
# ==========================================================
# JUDGE LOGGER
# ==========================================================

import json
import hashlib
from datetime import datetime

judge_logger = logging.getLogger("judge")


def log_judge_result(
    submission: Submission,
    judge_result: JudgeResult
):
    """
    Log judge result.
    """

    judge_logger.info(

        "Submission=%s | Student=%s | Verdict=%s | Score=%.2f",

        submission.id,

        submission.student_id,

        judge_result.verdict,

        judge_result.score

    )


# ==========================================================
# JUDGE AUDIT ID
# ==========================================================

def audit_id(
    submission,
    judge_result
):

    text = (

        f"{submission.id}"

        f"{submission.student_id}"

        f"{judge_result.verdict}"

        f"{datetime.utcnow()}"

    )

    return hashlib.sha256(

        text.encode()

    ).hexdigest()


# ==========================================================
# AUDIT REPORT
# ==========================================================

def audit_report(
    submission,
    judge_result
):

    return {

        "audit_id":

            audit_id(

                submission,

                judge_result

            ),

        "submission_id":

            submission.id,

        "student_id":

            submission.student_id,

        "problem_id":

            submission.problem_id,

        "language":

            submission.language,

        "verdict":

            judge_result.verdict,

        "score":

            judge_result.score,

        "execution_time":

            judge_result.execution_time,

        "memory_used":

            judge_result.memory_used,

        "judged_at":

            judge_result.judged_at.isoformat()

    }


# ==========================================================
# EXPORT REPORT
# ==========================================================

def export_report(
    submission,
    judge_result,
    filename
):

    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as fp:

        json.dump(

            audit_report(

                submission,

                judge_result

            ),

            fp,

            indent=4

        )

    return filename


# ==========================================================
# JUDGE HISTORY
# ==========================================================

class JudgeHistory:

    def __init__(self):

        self.results = []

    def add(

        self,

        submission,

        judge_result

    ):

        self.results.append(

            (

                submission,

                judge_result

            )

        )

    def latest(self):

        if not self.results:

            return None

        return self.results[-1]

    def clear(self):

        self.results.clear()

    def total(self):

        return len(

            self.results

        )


# ==========================================================
# DIAGNOSTICS
# ==========================================================

def diagnostics(
    submission,
    judge_result
):

    return {

        "submission_id":

            submission.id,

        "student_id":

            submission.student_id,

        "problem_id":

            submission.problem_id,

        "compile_error":

            judge_result.compile_error,

        "runtime_error":

            judge_result.runtime_error,

        "passed":

            judge_result.passed_testcases,

        "failed":

            judge_result.failed_testcases,

        "total":

            judge_result.total_testcases,

        "score":

            judge_result.score

    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

def judge_health():

    return {

        "database":

            db.session is not None,

        "compiler":

            True,

        "executor":

            True,

        "timestamp":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# VERIFY JUDGE
# ==========================================================

def verify_judge():

    health = judge_health()

    return all(

        health.values()

    )


# ==========================================================
# EXECUTE WITH LOGGING
# ==========================================================

def judge_with_logging(
    submission
):

    result = judge_submission(

        submission

    )

    log_judge_result(

        submission,

        result

    )

    return result


# ==========================================================
# JUDGE METADATA
# ==========================================================

def judge_metadata():

    return {

        "engine":

            "Lab Auto Grader Judge",

        "version":

            "1.0.0",

        "supported_languages":

            Submission.SUPPORTED_LANGUAGES,

        "generated_at":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# REPORT SUMMARY
# ==========================================================

def report_summary(
    submission,
    judge_result
):

    return {

        "submission":

            submission.id,

        "student":

            submission.student_id,

        "verdict":

            judge_result.verdict,

        "score":

            judge_result.score,

        "grade":

            performance_grade(

                judge_result.score

            ),

        "performance":

            performance_level(

                judge_result.execution_time

            )

    }
# ==========================================================
# BATCH REPORT GENERATION
# ==========================================================

from collections import Counter
import csv


def generate_batch_reports(
    submissions
):
    """
    Generate reports for multiple submissions.
    """

    reports = []

    for submission in submissions:

        try:

            result = judge_submission(

                submission

            )

            reports.append(

                report_summary(

                    submission,

                    result

                )

            )

        except Exception as e:

            logger.exception(e)

    return reports


# ==========================================================
# ANALYTICS DASHBOARD
# ==========================================================

def analytics_dashboard(
    problem_id
):
    """
    Analytics for a problem.
    """

    submissions = Submission.query.filter_by(

        problem_id=problem_id

    ).all()

    accepted = sum(

        1

        for s in submissions

        if s.verdict == ACCEPTED

    )

    return {

        "problem_id": problem_id,

        "total_submissions": len(submissions),

        "accepted": accepted,

        "acceptance_rate": round(

            accepted * 100 / len(submissions),

            2

        ) if submissions else 0,

        "average_score": round(

            sum(

                s.score

                for s in submissions

            ) / len(submissions),

            2

        ) if submissions else 0

    }


# ==========================================================
# CONTEST LEADERBOARD
# ==========================================================

def contest_leaderboard(
    assignment_id
):
    """
    Leaderboard for an assignment.
    """

    submissions = Submission.query.filter_by(

        assignment_id=assignment_id

    ).all()

    leaderboard = {}

    for submission in submissions:

        sid = submission.student_id

        score = leaderboard_score(

            submission

        )

        if sid not in leaderboard:

            leaderboard[sid] = score

        else:

            leaderboard[sid] = max(

                leaderboard[sid],

                score

            )

    return sorted(

        leaderboard.items(),

        key=lambda x: -x[1]

    )


# ==========================================================
# VERDICT DISTRIBUTION
# ==========================================================

def verdict_distribution(
    problem_id
):

    submissions = Submission.query.filter_by(

        problem_id=problem_id

    ).all()

    counter = Counter(

        s.verdict

        for s in submissions

    )

    return dict(counter)


# ==========================================================
# PERFORMANCE ANALYTICS
# ==========================================================

def performance_analytics(
    problem_id
):

    submissions = Submission.query.filter_by(

        problem_id=problem_id

    ).all()

    if not submissions:

        return {}

    return {

        "fastest_execution": min(

            s.execution_time

            for s in submissions

        ),

        "slowest_execution": max(

            s.execution_time

            for s in submissions

        ),

        "lowest_memory": min(

            s.memory_used

            for s in submissions

        ),

        "highest_memory": max(

            s.memory_used

            for s in submissions

        ),

        "average_execution_time": round(

            sum(

                s.execution_time

                for s in submissions

            ) / len(submissions),

            4

        )

    }


# ==========================================================
# EXPORT CSV
# ==========================================================

def export_csv(
    submissions,
    filename
):
    """
    Export submission results.
    """

    with open(

        filename,

        "w",

        newline="",

        encoding="utf-8"

    ) as fp:

        writer = csv.writer(fp)

        writer.writerow([

            "Submission",

            "Student",

            "Problem",

            "Verdict",

            "Score",

            "Execution Time",

            "Memory"

        ])

        for s in submissions:

            writer.writerow([

                s.id,

                s.student_id,

                s.problem_id,

                s.verdict,

                s.score,

                s.execution_time,

                s.memory_used

            ])

    return filename


# ==========================================================
# EXPORT JSON
# ==========================================================

def export_json(
    submissions,
    filename
):

    data = []

    for s in submissions:

        data.append({

            "submission_id": s.id,

            "student_id": s.student_id,

            "problem_id": s.problem_id,

            "verdict": s.verdict,

            "score": s.score,

            "execution_time": s.execution_time,

            "memory_used": s.memory_used

        })

    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as fp:

        json.dump(

            data,

            fp,

            indent=4

        )

    return filename


# ==========================================================
# BULK EXPORT
# ==========================================================

def bulk_export(
    assignment_id,
    directory
):

    submissions = Submission.query.filter_by(

        assignment_id=assignment_id

    ).all()

    csv_file = export_csv(

        submissions,

        f"{directory}/results.csv"

    )

    json_file = export_json(

        submissions,

        f"{directory}/results.json"

    )

    return {

        "csv": csv_file,

        "json": json_file

    }


# ==========================================================
# ANALYTICS SUMMARY
# ==========================================================

def analytics_summary(
    problem_id
):

    return {

        "dashboard":

            analytics_dashboard(

                problem_id

            ),

        "verdicts":

            verdict_distribution(

                problem_id

            ),

        "performance":

            performance_analytics(

                problem_id

            )

    }
# ==========================================================
# PARALLEL JUDGING
# ==========================================================

from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics


def parallel_judge(
    submissions,
    max_workers=4
):
    """
    Judge submissions in parallel.
    """

    results = []

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        future_map = {

            executor.submit(
                evaluate_submission,
                submission
            ): submission

            for submission in submissions

        }

        for future in as_completed(future_map):

            try:

                results.append(

                    future.result()

                )

            except Exception as e:

                logger.exception(e)

    return results


# ==========================================================
# RETRY FAILED SUBMISSIONS
# ==========================================================

def retry_failed_submissions(
    submissions,
    retries=3
):
    """
    Retry failed submissions.
    """

    successful = []

    for submission in submissions:

        result = None

        for _ in range(retries):

            result = evaluate_submission(
                submission
            )

            if result.verdict == ACCEPTED:

                break

        successful.append(result)

    return successful


# ==========================================================
# JUDGE BENCHMARK
# ==========================================================

def benchmark_judge(
    submissions
):
    """
    Benchmark judge engine.
    """

    timings = []

    for submission in submissions:

        start = datetime.utcnow()

        evaluate_submission(
            submission
        )

        end = datetime.utcnow()

        timings.append(

            (end - start).total_seconds()

        )

    if not timings:

        return {}

    return {

        "runs": len(timings),

        "minimum": round(
            min(timings),
            4
        ),

        "maximum": round(
            max(timings),
            4
        ),

        "average": round(
            statistics.mean(
                timings
            ),
            4
        ),

        "median": round(
            statistics.median(
                timings
            ),
            4
        )

    }


# ==========================================================
# PERFORMANCE MONITOR
# ==========================================================

class JudgeMonitor:

    def __init__(self):

        self.total = 0

        self.accepted = 0

        self.failed = 0

        self.total_score = 0

    def update(
        self,
        judge_result
    ):

        self.total += 1

        self.total_score += judge_result.score

        if judge_result.verdict == ACCEPTED:

            self.accepted += 1

        else:

            self.failed += 1

    def report(self):

        average = 0

        if self.total:

            average = round(

                self.total_score /

                self.total,

                2

            )

        return {

            "total": self.total,

            "accepted": self.accepted,

            "failed": self.failed,

            "average_score": average

        }


# ==========================================================
# CLEANUP
# ==========================================================

def cleanup_judge(
    judge_result
):
    """
    Cleanup execution resources.
    """

    try:

        for execution in judge_result.execution_results:

            cleanup_execution(
                execution
            )

    except Exception:

        pass

    return True


# ==========================================================
# VERIFY RESULTS
# ==========================================================

def verify_result(
    judge_result
):

    return (

        judge_result.verdict
        is not None

        and

        judge_result.total_testcases >= 0

        and

        judge_result.score >= 0

    )


# ==========================================================
# PIPELINE VALIDATION
# ==========================================================

def validate_pipeline():

    return {

        "database":

            db.session is not None,

        "compiler":

            True,

        "executor":

            True,

        "judge":

            True

    }


# ==========================================================
# ENGINE STATUS
# ==========================================================

def engine_status():

    return {

        "status":

            "Running"

            if verify_judge()

            else

            "Error",

        "version":

            "1.0.0",

        "health":

            judge_health(),

        "pipeline":

            validate_pipeline()

    }


# ==========================================================
# QUICK DIAGNOSTIC
# ==========================================================

def diagnostic():

    return {

        "engine":

            engine_status(),

        "metadata":

            judge_metadata(),

        "health":

            judge_health()

    }
# ==========================================================
# VERSION INFORMATION
# ==========================================================

JUDGE_ENGINE = "Lab Auto Grader Judge"

JUDGE_VERSION = "1.0.0"

JUDGE_AUTHOR = "Devanshu Ranjan Upadhyay"


def version():
    """
    Judge engine version.
    """

    return {

        "engine": JUDGE_ENGINE,

        "version": JUDGE_VERSION,

        "author": JUDGE_AUTHOR,

        "languages": Submission.SUPPORTED_LANGUAGES

    }


# ==========================================================
# INITIALIZE
# ==========================================================

def initialize():
    """
    Initialize Judge Engine.
    """

    health = judge_health()

    if not health["database"]:

        raise RuntimeError(

            "Database connection unavailable."

        )

    logger.info(

        "Judge Engine initialized."

    )

    return health


# ==========================================================
# MAIN API
# ==========================================================

def judge(
    submission
):
    """
    Main public API.
    """

    return evaluate_submission(

        submission

    )


# ==========================================================
# JUDGE BY ID
# ==========================================================

def judge_submission_id(
    submission_id
):

    submission = get_submission(

        submission_id

    )

    if submission is None:

        raise ValueError(

            "Submission not found."

        )

    return judge(

        submission

    )


# ==========================================================
# JUDGE PROBLEM
# ==========================================================

def judge_problem(
    problem_id
):

    submissions = Submission.query.filter_by(

        problem_id=problem_id

    ).all()

    return judge_submissions(

        submissions

    )


# ==========================================================
# JUDGE ALL PENDING
# ==========================================================

def judge_pending():

    submissions = Submission.query.filter_by(

        status="Pending"

    ).all()

    return judge_submissions(

        submissions

    )


# ==========================================================
# RESET ENGINE
# ==========================================================

def reset_engine():

    logger.info(

        "Judge Engine reset."

    )

    return True


# ==========================================================
# READY CHECK
# ==========================================================

def ready():

    return verify_judge()


# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [

    # Models

    "JudgeResult",

    "TestCaseResult",

    # Main APIs

    "judge",

    "judge_submission",

    "judge_submission_id",

    "judge_problem",

    "judge_assignment",

    "judge_pending",

    "evaluate_submission",

    "quick_judge",

    "rejudge_submission",

    "bulk_rejudge",

    "parallel_judge",

    # Reports

    "judge_report",

    "student_report",

    "system_report",

    "analytics_dashboard",

    "analytics_summary",

    "performance_analytics",

    "generate_leaderboard",

    "contest_leaderboard",

    "best_submissions",

    # Diagnostics

    "diagnostic",

    "engine_status",

    "judge_health",

    "judge_metadata",

    "benchmark_judge",

    "JudgeMonitor",

    # Utilities

    "cleanup_judge",

    "verify_judge",

    "initialize",

    "version",

    "ready"

]