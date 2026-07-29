"""
==========================================================
Lab Auto Grader
Submission Model
Part 1
==========================================================
"""

from datetime import datetime

from sqlalchemy import Text
from sqlalchemy.orm import validates

from extensions import db


class Submission(db.Model):
    """
    Student Submission Model
    """

    __tablename__ = "submissions"

    # -------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -------------------------------------------------------
    # Foreign Keys
    # -------------------------------------------------------

    student_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "students.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    problem_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "problems.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "assignments.id",
            ondelete="CASCADE"
        ),
        nullable=True,
        index=True
    )

    # -------------------------------------------------------
    # Source Code
    # -------------------------------------------------------

    source_code = db.Column(
        Text,
        nullable=False
    )

    language = db.Column(
        db.String(30),
        nullable=False,
        default="Python",
        index=True
    )

    source_size = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    # -------------------------------------------------------
    # Execution Result
    # -------------------------------------------------------

    verdict = db.Column(
        db.String(50),
        nullable=False,
        default="Pending",
        index=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Queued",
        index=True
    )

    score = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    marks_awarded = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    passed_test_cases = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    total_test_cases = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    # -------------------------------------------------------
    # Performance
    # -------------------------------------------------------

    execution_time = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    memory_used = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    cpu_time = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    # -------------------------------------------------------
    # Output
    # -------------------------------------------------------

    stdout = db.Column(
        Text,
        nullable=True
    )

    stderr = db.Column(
        Text,
        nullable=True
    )

    compile_output = db.Column(
        Text,
        nullable=True
    )

    custom_input = db.Column(
        Text,
        nullable=True
    )

    # -------------------------------------------------------
    # Judge Results
    # -------------------------------------------------------

    test_case_results = db.Column(
        db.JSON,
        nullable=True
    )

    judge_response = db.Column(
        db.JSON,
        nullable=True
    )

    # -------------------------------------------------------
    # Flags
    # -------------------------------------------------------

    is_final = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    is_late = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    plagiarism_checked = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    plagiarism_score = db.Column(
        db.Float,
        default=0.0,
        nullable=False
    )

    # -------------------------------------------------------
    # Audit
    # -------------------------------------------------------

    submitted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    evaluated_at = db.Column(
        db.DateTime,
        nullable=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # -------------------------------------------------------
    # Representation
    # -------------------------------------------------------

    def __repr__(self):

        return (

            f"<Submission "

            f"id={self.id} "

            f"student={self.student_id} "

            f"problem={self.problem_id} "

            f"verdict='{self.verdict}'>"

        )
        # -------------------------------------------------------
    # RELATIONSHIPS
    # -------------------------------------------------------

    student = db.relationship(
        "Student",
        back_populates="submissions",
        lazy="joined"
    )

    problem = db.relationship(
        "Problem",
        back_populates="submissions",
        lazy="joined"
    )

    assignment = db.relationship(
        "Assignment",
        back_populates="submissions",
        lazy="joined"
    )

    # -------------------------------------------------------
    # VERDICT CONSTANTS
    # -------------------------------------------------------

    VERDICT_PENDING = "Pending"
    VERDICT_ACCEPTED = "Accepted"
    VERDICT_WRONG_ANSWER = "Wrong Answer"
    VERDICT_TIME_LIMIT = "Time Limit Exceeded"
    VERDICT_MEMORY_LIMIT = "Memory Limit Exceeded"
    VERDICT_RUNTIME_ERROR = "Runtime Error"
    VERDICT_COMPILATION_ERROR = "Compilation Error"
    VERDICT_PRESENTATION_ERROR = "Presentation Error"
    VERDICT_INTERNAL_ERROR = "Internal Error"

    VALID_VERDICTS = (

        VERDICT_PENDING,

        VERDICT_ACCEPTED,

        VERDICT_WRONG_ANSWER,

        VERDICT_TIME_LIMIT,

        VERDICT_MEMORY_LIMIT,

        VERDICT_RUNTIME_ERROR,

        VERDICT_COMPILATION_ERROR,

        VERDICT_PRESENTATION_ERROR,

        VERDICT_INTERNAL_ERROR

    )

    # -------------------------------------------------------
    # STATUS CONSTANTS
    # -------------------------------------------------------

    STATUS_QUEUED = "Queued"
    STATUS_RUNNING = "Running"
    STATUS_COMPLETED = "Completed"
    STATUS_FAILED = "Failed"

    VALID_STATUS = (

        STATUS_QUEUED,

        STATUS_RUNNING,

        STATUS_COMPLETED,

        STATUS_FAILED

    )

    # -------------------------------------------------------
    # COMPUTED PROPERTIES
    # -------------------------------------------------------

    @property
    def pass_percentage(self):

        if self.total_test_cases == 0:
            return 0.0

        return round(

            (self.passed_test_cases /
             self.total_test_cases) * 100,

            2

        )

    @property
    def failed_test_cases(self):

        return max(

            0,

            self.total_test_cases -

            self.passed_test_cases

        )

    @property
    def is_accepted(self):

        return self.verdict == self.VERDICT_ACCEPTED

    @property
    def is_compilation_error(self):

        return self.verdict == self.VERDICT_COMPILATION_ERROR

    @property
    def is_runtime_error(self):

        return self.verdict == self.VERDICT_RUNTIME_ERROR

    @property
    def is_time_limit(self):

        return self.verdict == self.VERDICT_TIME_LIMIT

    @property
    def is_memory_limit(self):

        return self.verdict == self.VERDICT_MEMORY_LIMIT

    @property
    def is_pending(self):

        return self.verdict == self.VERDICT_PENDING

    @property
    def execution_summary(self):

        return {

            "time": self.execution_time,

            "memory": self.memory_used,

            "cpu": self.cpu_time

        }

    # -------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------

    def mark_running(self):

        self.status = self.STATUS_RUNNING

    def mark_completed(self):

        self.status = self.STATUS_COMPLETED

        self.evaluated_at = datetime.utcnow()

    def mark_failed(self):

        self.status = self.STATUS_FAILED

        self.evaluated_at = datetime.utcnow()

    def mark_final(self):

        self.is_final = True

    def mark_late(self):

        self.is_late = True

    def set_verdict(self, verdict):

        if verdict not in self.VALID_VERDICTS:

            raise ValueError(

                f"Invalid verdict: {verdict}"

            )

        self.verdict = verdict

    def update_score(self, score):

        self.score = float(score)

    def update_marks(self, marks):

        self.marks_awarded = float(marks)

    def update_testcase_result(

        self,

        passed,

        total

    ):

        self.passed_test_cases = passed

        self.total_test_cases = total
        # -------------------------------------------------------
    # SUPPORTED LANGUAGES
    # -------------------------------------------------------

    SUPPORTED_LANGUAGES = (

        "Python",

        "C",

        "C++",

        "Java",

        "JavaScript"

    )

    # -------------------------------------------------------
    # FIELD VALIDATION
    # -------------------------------------------------------

    @validates("language")
    def validate_language(self, key, value):

        value = value.strip()

        if value not in self.SUPPORTED_LANGUAGES:

            raise ValueError(

                f"Unsupported language: {value}"

            )

        return value

    @validates("verdict")
    def validate_verdict(self, key, value):

        if value not in self.VALID_VERDICTS:

            raise ValueError(

                "Invalid verdict."

            )

        return value

    @validates("status")
    def validate_status(self, key, value):

        if value not in self.VALID_STATUS:

            raise ValueError(

                "Invalid execution status."

            )

        return value

    @validates("source_code")
    def validate_source_code(self, key, value):

        value = value.rstrip()

        if not value:

            raise ValueError(

                "Source code cannot be empty."

            )

        if len(value) > 200000:

            raise ValueError(

                "Source code exceeds maximum size."

            )

        self.source_size = len(value.encode("utf-8"))

        return value

    @validates("score")
    def validate_score(self, key, value):

        value = float(value)

        if value < 0:

            raise ValueError(

                "Score cannot be negative."

            )

        return value

    @validates("marks_awarded")
    def validate_marks(self, key, value):

        value = float(value)

        if value < 0:

            raise ValueError(

                "Marks cannot be negative."

            )

        return value

    @validates("execution_time")
    def validate_execution_time(self, key, value):

        value = float(value)

        if value < 0:

            raise ValueError(

                "Execution time cannot be negative."

            )

        return value

    @validates("cpu_time")
    def validate_cpu_time(self, key, value):

        value = float(value)

        if value < 0:

            raise ValueError(

                "CPU time cannot be negative."

            )

        return value

    @validates("memory_used")
    def validate_memory_used(self, key, value):

        value = float(value)

        if value < 0:

            raise ValueError(

                "Memory usage cannot be negative."

            )

        return value

    @validates("passed_test_cases")
    def validate_passed_cases(self, key, value):

        value = int(value)

        if value < 0:

            raise ValueError(

                "Passed test cases cannot be negative."

            )

        return value

    @validates("total_test_cases")
    def validate_total_cases(self, key, value):

        value = int(value)

        if value < 0:

            raise ValueError(

                "Total test cases cannot be negative."

            )

        return value

    @validates("plagiarism_score")
    def validate_plagiarism_score(self, key, value):

        value = float(value)

        if value < 0 or value > 100:

            raise ValueError(

                "Plagiarism score must be between 0 and 100."

            )

        return value

    # -------------------------------------------------------
    # VALIDATION HELPERS
    # -------------------------------------------------------

    @property
    def source_lines(self):
        """
        Number of lines in submitted source code.
        """

        if not self.source_code:
            return 0

        return len(self.source_code.splitlines())

    @property
    def source_characters(self):
        """
        Number of characters in source code.
        """

        return len(self.source_code or "")

    @property
    def source_kb(self):
        """
        Source code size in KB.
        """

        return round(

            self.source_size / 1024,

            2

        )

    def has_compile_output(self):

        return bool(self.compile_output)

    def has_runtime_output(self):

        return bool(self.stdout)

    def has_runtime_error(self):

        return bool(self.stderr)

    def has_custom_input(self):

        return bool(self.custom_input)
        # -------------------------------------------------------
    # CRUD OPERATIONS
    # -------------------------------------------------------

    def save(self, commit=True):
        """
        Save submission to database.
        """

        db.session.add(self)

        if commit:
            db.session.commit()

        return self

    def update(self, commit=True, **kwargs):
        """
        Update submission fields.
        """

        for key, value in kwargs.items():

            if hasattr(self, key):

                setattr(self, key, value)

        self.updated_at = datetime.utcnow()

        if commit:
            db.session.commit()

        return self

    def delete(self, commit=True):
        """
        Delete submission.
        """

        db.session.delete(self)

        if commit:
            db.session.commit()

    # -------------------------------------------------------
    # RESET SUBMISSION
    # -------------------------------------------------------

    def reset(self, commit=True):
        """
        Reset evaluation results.
        """

        self.verdict = self.VERDICT_PENDING

        self.status = self.STATUS_QUEUED

        self.score = 0

        self.marks_awarded = 0

        self.execution_time = 0

        self.cpu_time = 0

        self.memory_used = 0

        self.stdout = None

        self.stderr = None

        self.compile_output = None

        self.test_case_results = None

        self.judge_response = None

        self.passed_test_cases = 0

        self.total_test_cases = 0

        self.evaluated_at = None

        self.updated_at = datetime.utcnow()

        if commit:
            db.session.commit()

        return self

    # -------------------------------------------------------
    # RE-EVALUATE
    # -------------------------------------------------------

    def re_evaluate(self, commit=True):
        """
        Mark submission for re-evaluation.
        """

        self.reset(commit=False)

        self.status = self.STATUS_QUEUED

        self.updated_at = datetime.utcnow()

        if commit:
            db.session.commit()

        return self

    # -------------------------------------------------------
    # COMPLETE EVALUATION
    # -------------------------------------------------------

    def complete_evaluation(
        self,
        verdict,
        score,
        marks,
        execution_time,
        memory_used,
        passed,
        total
    ):
        """
        Store evaluation result.
        """

        self.set_verdict(verdict)

        self.score = score

        self.marks_awarded = marks

        self.execution_time = execution_time

        self.memory_used = memory_used

        self.passed_test_cases = passed

        self.total_test_cases = total

        self.status = self.STATUS_COMPLETED

        self.evaluated_at = datetime.utcnow()

        self.updated_at = datetime.utcnow()

    # -------------------------------------------------------
    # CLASS METHODS
    # -------------------------------------------------------

    @classmethod
    def get_by_id(cls, submission_id):

        return cls.query.get(submission_id)

    @classmethod
    def latest(cls, limit=20):

        return cls.query.order_by(

            cls.submitted_at.desc()

        ).limit(limit).all()

    @classmethod
    def by_student(cls, student_id):

        return cls.query.filter_by(

            student_id=student_id

        )

    @classmethod
    def by_problem(cls, problem_id):

        return cls.query.filter_by(

            problem_id=problem_id

        )

    @classmethod
    def by_assignment(cls, assignment_id):

        return cls.query.filter_by(

            assignment_id=assignment_id

        )

    @classmethod
    def accepted(cls):

        return cls.query.filter_by(

            verdict=cls.VERDICT_ACCEPTED

        )

    @classmethod
    def pending(cls):

        return cls.query.filter_by(

            verdict=cls.VERDICT_PENDING

        )

    # -------------------------------------------------------
    # BULK OPERATIONS
    # -------------------------------------------------------

    @classmethod
    def bulk_delete(cls, ids):
        """
        Delete multiple submissions.
        """

        cls.query.filter(

            cls.id.in_(ids)

        ).delete(

            synchronize_session=False

        )

        db.session.commit()

    @classmethod
    def bulk_reset(cls, ids):
        """
        Reset multiple submissions.
        """

        submissions = cls.query.filter(

            cls.id.in_(ids)

        ).all()

        for submission in submissions:

            submission.reset(commit=False)

        db.session.commit()

    # -------------------------------------------------------
    # DATABASE HELPERS
    # -------------------------------------------------------

    @classmethod
    def count(cls):

        return cls.query.count()

    @classmethod
    def exists(cls, submission_id):

        return db.session.query(

            cls.query.filter_by(

                id=submission_id

            ).exists()

        ).scalar()
        # -------------------------------------------------------
    # SERIALIZATION
    # -------------------------------------------------------

    def to_dict(self):
        """
        Serialize submission to dictionary.
        """

        return {

            "id": self.id,

            "student_id": self.student_id,

            "problem_id": self.problem_id,

            "assignment_id": self.assignment_id,

            "language": self.language,

            "verdict": self.verdict,

            "status": self.status,

            "score": self.score,

            "marks_awarded": self.marks_awarded,

            "passed_test_cases": self.passed_test_cases,

            "total_test_cases": self.total_test_cases,

            "pass_percentage": self.pass_percentage,

            "execution_time": self.execution_time,

            "memory_used": self.memory_used,

            "cpu_time": self.cpu_time,

            "stdout": self.stdout,

            "stderr": self.stderr,

            "compile_output": self.compile_output,

            "custom_input": self.custom_input,

            "source_size": self.source_size,

            "source_lines": self.source_lines,

            "is_final": self.is_final,

            "is_late": self.is_late,

            "plagiarism_checked": self.plagiarism_checked,

            "plagiarism_score": self.plagiarism_score,

            "submitted_at": self.submitted_at.isoformat()
                if self.submitted_at else None,

            "evaluated_at": self.evaluated_at.isoformat()
                if self.evaluated_at else None,

            "updated_at": self.updated_at.isoformat()
                if self.updated_at else None

        }

    # -------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------

    def summary(self):
        """
        Lightweight serializer.
        """

        return {

            "id": self.id,

            "student_id": self.student_id,

            "problem_id": self.problem_id,

            "language": self.language,

            "verdict": self.verdict,

            "score": self.score,

            "submitted_at": self.submitted_at.isoformat()
                if self.submitted_at else None

        }

    # -------------------------------------------------------
    # DASHBOARD CARD
    # -------------------------------------------------------

    def dashboard_card(self):
        """
        Dashboard serializer.
        """

        return {

            "id": self.id,

            "problem": self.problem.title
                if self.problem else None,

            "student": self.student.name
                if self.student else None,

            "language": self.language,

            "verdict": self.verdict,

            "score": self.score,

            "execution_time": self.execution_time,

            "memory_used": self.memory_used,

            "submitted_at": self.submitted_at.isoformat()
                if self.submitted_at else None

        }

    # -------------------------------------------------------
    # EXPORT
    # -------------------------------------------------------

    def export_json(self):
        """
        Export submission as JSON-compatible dict.
        """

        return self.to_dict()

    # -------------------------------------------------------
    # UPDATE FROM DICTIONARY
    # -------------------------------------------------------

    def update_from_dict(self, data):
        """
        Update editable fields.
        """

        editable_fields = [

            "language",

            "source_code",

            "custom_input",

            "score",

            "marks_awarded",

            "verdict",

            "status",

            "execution_time",

            "memory_used",

            "cpu_time",

            "stdout",

            "stderr",

            "compile_output",

            "passed_test_cases",

            "total_test_cases",

            "plagiarism_checked",

            "plagiarism_score"

        ]

        for field in editable_fields:

            if field in data:

                setattr(

                    self,

                    field,

                    data[field]

                )

        self.updated_at = datetime.utcnow()

        return self

    # -------------------------------------------------------
    # API RESPONSE
    # -------------------------------------------------------

    def api_response(self):
        """
        Standard API response.
        """

        return {

            "success": True,

            "submission": self.to_dict()

        }

    # -------------------------------------------------------
    # COPY
    # -------------------------------------------------------

    def clone_data(self):
        """
        Clone source code only.
        """

        return {

            "student_id": self.student_id,

            "problem_id": self.problem_id,

            "assignment_id": self.assignment_id,

            "language": self.language,

            "source_code": self.source_code,

            "custom_input": self.custom_input

        }

    # -------------------------------------------------------
    # LOG DATA
    # -------------------------------------------------------

    def log_entry(self):
        """
        Compact log entry.
        """

        return {

            "submission_id": self.id,

            "student_id": self.student_id,

            "problem_id": self.problem_id,

            "verdict": self.verdict,

            "score": self.score,

            "submitted_at": self.submitted_at.isoformat()
                if self.submitted_at else None

        }
        # -------------------------------------------------------
    # STATISTICS
    # -------------------------------------------------------

    @property
    def success_rate(self):
        """
        Percentage of passed test cases.
        """

        if self.total_test_cases == 0:
            return 0.0

        return round(
            (self.passed_test_cases / self.total_test_cases) * 100,
            2
        )

    @property
    def failed_test_cases_count(self):
        """
        Number of failed test cases.
        """

        return max(
            0,
            self.total_test_cases - self.passed_test_cases
        )

    @property
    def execution_summary(self):
        """
        Execution statistics.
        """

        return {
            "execution_time": self.execution_time,
            "memory_used": self.memory_used,
            "cpu_time": self.cpu_time
        }

    @property
    def performance_grade(self):
        """
        Performance grade based on score.
        """

        if self.score >= 90:
            return "A+"

        if self.score >= 80:
            return "A"

        if self.score >= 70:
            return "B"

        if self.score >= 60:
            return "C"

        if self.score >= 50:
            return "D"

        return "F"

    @property
    def verdict_color(self):
        """
        Bootstrap badge color.
        """

        colors = {

            self.VERDICT_ACCEPTED: "success",

            self.VERDICT_PENDING: "secondary",

            self.VERDICT_WRONG_ANSWER: "danger",

            self.VERDICT_RUNTIME_ERROR: "warning",

            self.VERDICT_COMPILATION_ERROR: "dark",

            self.VERDICT_TIME_LIMIT: "info",

            self.VERDICT_MEMORY_LIMIT: "primary",

            self.VERDICT_PRESENTATION_ERROR: "warning",

            self.VERDICT_INTERNAL_ERROR: "danger"

        }

        return colors.get(
            self.verdict,
            "secondary"
        )

    # -------------------------------------------------------
    # CLASS ANALYTICS
    # -------------------------------------------------------

    @classmethod
    def average_score(cls):

        value = db.session.query(
            db.func.avg(cls.score)
        ).scalar()

        return round(value or 0, 2)

    @classmethod
    def average_execution_time(cls):

        value = db.session.query(
            db.func.avg(cls.execution_time)
        ).scalar()

        return round(value or 0, 3)

    @classmethod
    def average_memory_usage(cls):

        value = db.session.query(
            db.func.avg(cls.memory_used)
        ).scalar()

        return round(value or 0, 2)

    @classmethod
    def accepted_count(cls):

        return cls.query.filter_by(
            verdict=cls.VERDICT_ACCEPTED
        ).count()

    @classmethod
    def pending_count(cls):

        return cls.query.filter_by(
            verdict=cls.VERDICT_PENDING
        ).count()

    @classmethod
    def rejected_count(cls):

        return cls.query.filter(
            cls.verdict != cls.VERDICT_ACCEPTED,
            cls.verdict != cls.VERDICT_PENDING
        ).count()

    @classmethod
    def acceptance_rate(cls):
        """
        Overall acceptance rate.
        """

        total = cls.query.count()

        if total == 0:
            return 0.0

        accepted = cls.accepted_count()

        return round(
            accepted * 100 / total,
            2
        )

    @classmethod
    def verdict_distribution(cls):
        """
        Count submissions by verdict.
        """

        result = {}

        for verdict in cls.VALID_VERDICTS:

            result[verdict] = cls.query.filter_by(
                verdict=verdict
            ).count()

        return result

    @classmethod
    def dashboard_statistics(cls):
        """
        Dashboard statistics.
        """

        return {

            "total_submissions": cls.count(),

            "accepted": cls.accepted_count(),

            "pending": cls.pending_count(),

            "rejected": cls.rejected_count(),

            "acceptance_rate": cls.acceptance_rate(),

            "average_score": cls.average_score(),

            "average_execution_time":
                cls.average_execution_time(),

            "average_memory_usage":
                cls.average_memory_usage()

        }

    # -------------------------------------------------------
    # INSTANCE ANALYTICS
    # -------------------------------------------------------

    def analytics(self):
        """
        Complete analytics for a submission.
        """

        return {

            "submission_id": self.id,

            "score": self.score,

            "grade": self.performance_grade,

            "verdict": self.verdict,

            "verdict_color": self.verdict_color,

            "success_rate": self.success_rate,

            "passed": self.passed_test_cases,

            "failed": self.failed_test_cases_count,

            "execution_time": self.execution_time,

            "memory_used": self.memory_used,

            "cpu_time": self.cpu_time

        }
        # -------------------------------------------------------
    # SEARCH & FILTER METHODS
    # -------------------------------------------------------

    @classmethod
    def search(cls, keyword):
        """
        Search submissions by ID or source code.
        """

        if not keyword:
            return cls.query

        keyword = f"%{keyword}%"

        return cls.query.filter(

            db.or_(

                cls.source_code.ilike(keyword),

                db.cast(cls.id, db.String).ilike(keyword)

            )

        )

    @classmethod
    def by_verdict(cls, verdict):

        return cls.query.filter_by(
            verdict=verdict
        )

    @classmethod
    def by_status(cls, status):

        return cls.query.filter_by(
            status=status
        )

    @classmethod
    def by_language(cls, language):

        return cls.query.filter_by(
            language=language
        )

    @classmethod
    def final_submissions(cls):

        return cls.query.filter_by(
            is_final=True
        )

    @classmethod
    def late_submissions(cls):

        return cls.query.filter_by(
            is_late=True
        )

    @classmethod
    def plagiarism_checked_submissions(cls):

        return cls.query.filter_by(
            plagiarism_checked=True
        )

    @classmethod
    def by_date_range(cls, start_date, end_date):

        return cls.query.filter(

            cls.submitted_at >= start_date,

            cls.submitted_at <= end_date

        )

    # -------------------------------------------------------
    # SORTING
    # -------------------------------------------------------

    @classmethod
    def newest(cls):

        return cls.query.order_by(
            cls.submitted_at.desc()
        )

    @classmethod
    def oldest(cls):

        return cls.query.order_by(
            cls.submitted_at.asc()
        )

    @classmethod
    def highest_score(cls):

        return cls.query.order_by(
            cls.score.desc()
        )

    @classmethod
    def fastest(cls):

        return cls.query.order_by(
            cls.execution_time.asc()
        )

    @classmethod
    def lowest_memory(cls):

        return cls.query.order_by(
            cls.memory_used.asc()
        )

    # -------------------------------------------------------
    # PAGINATION
    # -------------------------------------------------------

    @classmethod
    def paginate_results(
        cls,
        page=1,
        per_page=20,
        query=None
    ):

        if query is None:

            query = cls.query

        return query.paginate(

            page=page,

            per_page=per_page,

            error_out=False

        )

    # -------------------------------------------------------
    # LEADERBOARD
    # -------------------------------------------------------

    @classmethod
    def top_scores(cls, limit=10):

        return cls.query.order_by(

            cls.score.desc(),

            cls.execution_time.asc(),

            cls.memory_used.asc()

        ).limit(limit).all()

    @classmethod
    def best_submission(cls, student_id, problem_id):

        return cls.query.filter_by(

            student_id=student_id,

            problem_id=problem_id

        ).order_by(

            cls.score.desc(),

            cls.execution_time.asc()

        ).first()

    @classmethod
    def latest_submission(cls, student_id, problem_id):

        return cls.query.filter_by(

            student_id=student_id,

            problem_id=problem_id

        ).order_by(

            cls.submitted_at.desc()

        ).first()

    @classmethod
    def student_best_scores(cls, student_id):

        return cls.query.filter_by(

            student_id=student_id

        ).order_by(

            cls.score.desc()

        )

    # -------------------------------------------------------
    # ATTEMPTS
    # -------------------------------------------------------

    @classmethod
    def attempts(cls, student_id, problem_id):

        return cls.query.filter_by(

            student_id=student_id,

            problem_id=problem_id

        ).count()

    @classmethod
    def recent_attempts(cls, student_id, limit=10):

        return cls.query.filter_by(

            student_id=student_id

        ).order_by(

            cls.submitted_at.desc()

        ).limit(limit).all()

    # -------------------------------------------------------
    # ADVANCED FILTER
    # -------------------------------------------------------

    @classmethod
    def advanced_search(
        cls,
        student_id=None,
        problem_id=None,
        language=None,
        verdict=None,
        start_date=None,
        end_date=None
    ):

        query = cls.query

        if student_id:

            query = query.filter_by(
                student_id=student_id
            )

        if problem_id:

            query = query.filter_by(
                problem_id=problem_id
            )

        if language:

            query = query.filter_by(
                language=language
            )

        if verdict:

            query = query.filter_by(
                verdict=verdict
            )

        if start_date:

            query = query.filter(
                cls.submitted_at >= start_date
            )

        if end_date:

            query = query.filter(
                cls.submitted_at <= end_date
            )

        return query
        # -------------------------------------------------------
    # VERDICT HELPERS
    # -------------------------------------------------------

    @property
    def is_success(self):
        return self.verdict == self.VERDICT_ACCEPTED

    @property
    def is_failed(self):
        return self.verdict not in (
            self.VERDICT_ACCEPTED,
            self.VERDICT_PENDING
        )

    @property
    def is_completed(self):
        return self.status == self.STATUS_COMPLETED

    @property
    def is_running_now(self):
        return self.status == self.STATUS_RUNNING

    @property
    def is_queued(self):
        return self.status == self.STATUS_QUEUED

    # -------------------------------------------------------
    # VERDICT BADGES
    # -------------------------------------------------------

    @property
    def badge_color(self):

        mapping = {

            self.VERDICT_ACCEPTED: "success",

            self.VERDICT_PENDING: "secondary",

            self.VERDICT_WRONG_ANSWER: "danger",

            self.VERDICT_TIME_LIMIT: "warning",

            self.VERDICT_MEMORY_LIMIT: "info",

            self.VERDICT_RUNTIME_ERROR: "dark",

            self.VERDICT_COMPILATION_ERROR: "primary",

            self.VERDICT_PRESENTATION_ERROR: "warning",

            self.VERDICT_INTERNAL_ERROR: "danger"

        }

        return mapping.get(
            self.verdict,
            "secondary"
        )

    @property
    def badge_icon(self):

        mapping = {

            self.VERDICT_ACCEPTED: "check-circle",

            self.VERDICT_PENDING: "clock",

            self.VERDICT_WRONG_ANSWER: "x-circle",

            self.VERDICT_TIME_LIMIT: "stopwatch",

            self.VERDICT_MEMORY_LIMIT: "memory",

            self.VERDICT_RUNTIME_ERROR: "bug",

            self.VERDICT_COMPILATION_ERROR: "code-slash",

            self.VERDICT_PRESENTATION_ERROR: "exclamation-circle",

            self.VERDICT_INTERNAL_ERROR: "shield-exclamation"

        }

        return mapping.get(
            self.verdict,
            "question-circle"
        )

    # -------------------------------------------------------
    # PERFORMANCE
    # -------------------------------------------------------

    @property
    def execution_grade(self):

        t = self.execution_time

        if t <= 0.20:
            return "Excellent"

        if t <= 0.50:
            return "Very Good"

        if t <= 1.00:
            return "Good"

        if t <= 2.00:
            return "Average"

        return "Slow"

    @property
    def memory_grade(self):

        m = self.memory_used

        if m <= 16:
            return "Excellent"

        if m <= 32:
            return "Very Good"

        if m <= 64:
            return "Good"

        if m <= 128:
            return "Average"

        return "High"

    @property
    def score_grade(self):

        score = self.score

        if score >= 90:
            return "A+"

        if score >= 80:
            return "A"

        if score >= 70:
            return "B"

        if score >= 60:
            return "C"

        if score >= 50:
            return "D"

        return "F"

    # -------------------------------------------------------
    # EFFICIENCY
    # -------------------------------------------------------

    @property
    def efficiency_score(self):

        score = 100

        score -= min(
            self.execution_time * 5,
            40
        )

        score -= min(
            self.memory_used / 10,
            30
        )

        score += self.pass_percentage * 0.3

        return round(
            max(score, 0),
            2
        )

    @property
    def efficiency_level(self):

        value = self.efficiency_score

        if value >= 90:
            return "Excellent"

        if value >= 75:
            return "Very Good"

        if value >= 60:
            return "Good"

        if value >= 40:
            return "Average"

        return "Poor"

    # -------------------------------------------------------
    # RESULT SUMMARY
    # -------------------------------------------------------

    def result_summary(self):

        return {

            "verdict": self.verdict,

            "badge_color": self.badge_color,

            "badge_icon": self.badge_icon,

            "score": self.score,

            "marks": self.marks_awarded,

            "grade": self.score_grade,

            "passed": self.passed_test_cases,

            "failed": self.failed_test_cases_count,

            "pass_percentage": self.pass_percentage,

            "execution_time": self.execution_time,

            "execution_grade": self.execution_grade,

            "memory_used": self.memory_used,

            "memory_grade": self.memory_grade,

            "efficiency_score": self.efficiency_score,

            "efficiency_level": self.efficiency_level

        }

    # -------------------------------------------------------
    # QUICK STATUS
    # -------------------------------------------------------

    def short_status(self):

        return (

            f"{self.verdict} | "

            f"{self.score}% | "

            f"{self.execution_time:.3f}s"

        )

    # -------------------------------------------------------
    # DISPLAY STRING
    # -------------------------------------------------------

    def display_name(self):

        if self.problem:

            return (

                f"{self.problem.title} "

                f"({self.language})"

            )

        return f"Submission #{self.id}"
        # -------------------------------------------------------
    # CLONE
    # -------------------------------------------------------

    def clone(self):
        """
        Create a copy of this submission.
        """

        return Submission(

            student_id=self.student_id,

            problem_id=self.problem_id,

            assignment_id=self.assignment_id,

            source_code=self.source_code,

            language=self.language,

            custom_input=self.custom_input,

            is_final=False,

            is_late=False

        )

    # -------------------------------------------------------
    # HASH
    # -------------------------------------------------------

    @property
    def source_hash(self):
        """
        SHA-256 hash of source code.
        """

        import hashlib

        return hashlib.sha256(

            (self.source_code or "").encode("utf-8")

        ).hexdigest()

    # -------------------------------------------------------
    # AUDIT
    # -------------------------------------------------------

    def audit_log(self):

        return {

            "submission_id": self.id,

            "student_id": self.student_id,

            "problem_id": self.problem_id,

            "assignment_id": self.assignment_id,

            "language": self.language,

            "verdict": self.verdict,

            "status": self.status,

            "submitted_at": self.submitted_at,

            "evaluated_at": self.evaluated_at,

            "updated_at": self.updated_at

        }

    # -------------------------------------------------------
    # DUPLICATE CHECK
    # -------------------------------------------------------

    def is_duplicate(self):

        return Submission.query.filter(

            Submission.student_id == self.student_id,

            Submission.problem_id == self.problem_id,

            Submission.source_code == self.source_code,

            Submission.id != self.id

        ).first() is not None

    # -------------------------------------------------------
    # VERSION
    # -------------------------------------------------------

    version = db.Column(

        db.Integer,

        default=1,

        nullable=False

    )

    def increment_version(self):

        self.version += 1

        self.updated_at = datetime.utcnow()

    # -------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------

    def validate(self):

        if not self.source_code:

            raise ValueError(

                "Source code cannot be empty."

            )

        if self.language not in self.SUPPORTED_LANGUAGES:

            raise ValueError(

                "Unsupported programming language."

            )

        return True

    # -------------------------------------------------------
    # SAVE SAFE
    # -------------------------------------------------------

    def save_safe(self):

        self.validate()

        self.increment_version()

        db.session.add(self)

        db.session.commit()

        return self

    # -------------------------------------------------------
    # EXPORT
    # -------------------------------------------------------

    def export(self):

        return {

            "metadata": {

                "submission_id": self.id,

                "student_id": self.student_id,

                "problem_id": self.problem_id,

                "assignment_id": self.assignment_id,

                "version": self.version

            },

            "submission": self.to_dict(),

            "analytics": self.analytics()

        }

    # -------------------------------------------------------
    # STRING METHODS
    # -------------------------------------------------------

    def __str__(self):

        return (

            f"Submission #{self.id}"

        )

    def __eq__(self, other):

        return (

            isinstance(other, Submission)

            and

            self.id == other.id

        )

    def __hash__(self):

        return hash(self.id)