"""
==========================================================
Lab Auto Grader
Problem Model
Part 1
==========================================================
"""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text
from sqlalchemy.orm import validates

# Import the shared SQLAlchemy instance
# Change this import according to your project structure.
from extensions import db


class Problem(db.Model):
    """
    Programming Problem Model
    """

    __tablename__ = "problems"

    # -------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------

    title = db.Column(
        db.String(200),
        nullable=False,
        index=True
    )

    slug = db.Column(
        db.String(220),
        unique=True,
        nullable=False,
        index=True
    )

    short_description = db.Column(
        db.String(500),
        nullable=False
    )

    description = db.Column(
        Text,
        nullable=False
    )

    input_format = db.Column(
        Text,
        nullable=False
    )

    output_format = db.Column(
        Text,
        nullable=False
    )

    constraints = db.Column(
        Text,
        nullable=True
    )

    sample_input = db.Column(
        Text,
        nullable=False
    )

    sample_output = db.Column(
        Text,
        nullable=False
    )

    explanation = db.Column(
        Text,
        nullable=True
    )

    # -------------------------------------------------------
    # Difficulty
    # -------------------------------------------------------

    difficulty = db.Column(
        db.String(20),
        nullable=False,
        default="Easy",
        index=True
    )

    # -------------------------------------------------------
    # Limits
    # -------------------------------------------------------

    time_limit = db.Column(
        db.Float,
        nullable=False,
        default=2.0
    )

    memory_limit = db.Column(
        db.Integer,
        nullable=False,
        default=256
    )

    # -------------------------------------------------------
    # Marks
    # -------------------------------------------------------

    marks = db.Column(
        db.Integer,
        nullable=False,
        default=100
    )

    # -------------------------------------------------------
    # Visibility
    # -------------------------------------------------------

    is_public = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # -------------------------------------------------------
    # Audit Fields
    # -------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
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
            f"<Problem "
            f"id={self.id} "
            f"title='{self.title}' "
            f"difficulty='{self.difficulty}'>"
        )
"""
==========================================================
Lab Auto Grader
Problem Model
Part 2
Relationships & Constraints
==========================================================
"""

from sqlalchemy import CheckConstraint


class Problem(db.Model):
    # (Continue inside the existing Problem class)

    # -------------------------------------------------------
    # Foreign Keys
    # -------------------------------------------------------

    created_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "teachers.id",
            ondelete="SET NULL"
        ),
        nullable=True,
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
    # Relationships
    # -------------------------------------------------------

    teacher = db.relationship(
        "Teacher",
        back_populates="problems",
        lazy="joined"
    )

    assignment = db.relationship(
        "Assignment",
        back_populates="problems",
        lazy="joined"
    )

    test_cases = db.relationship(
        "TestCase",
        back_populates="problem",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="select"
    )

    submissions = db.relationship(
        "Submission",
        back_populates="problem",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="dynamic"
    )

    tags = db.relationship(
        "ProblemTag",
        secondary="problem_tag_map",
        lazy="selectin",
        back_populates="problems"
    )

    # -------------------------------------------------------
    # Database Constraints
    # -------------------------------------------------------

    __table_args__ = (

        CheckConstraint(
            "marks >= 0",
            name="ck_problem_marks_positive"
        ),

        CheckConstraint(
            "time_limit > 0",
            name="ck_problem_time_limit"
        ),

        CheckConstraint(
            "memory_limit >= 16",
            name="ck_problem_memory_limit"
        ),

        CheckConstraint(
            "difficulty IN ('Easy','Medium','Hard')",
            name="ck_problem_difficulty"
        ),

    )

    # -------------------------------------------------------
    # Convenience Properties
    # -------------------------------------------------------

    @property
    def total_test_cases(self):
        return len(self.test_cases)

    @property
    def total_submissions(self):
        return self.submissions.count()

    @property
    def accepted_submissions(self):
        return self.submissions.filter_by(
            verdict="Accepted"
        ).count()

    @property
    def has_assignment(self):
        return self.assignment_id is not None

    @property
    def author_name(self):
        if self.teacher:
            return self.teacher.name
        return "Unknown"

    # -------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------

    def add_test_case(self, testcase):
        self.test_cases.append(testcase)

    def remove_test_case(self, testcase):
        if testcase in self.test_cases:
            self.test_cases.remove(testcase)

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def publish(self):
        self.is_public = True

    def unpublish(self):
        self.is_public = False
        # -------------------------------------------------------
    # Supported Values
    # -------------------------------------------------------

    DIFFICULTY_LEVELS = (
        "Easy",
        "Medium",
        "Hard"
    )

    SUPPORTED_LANGUAGES = (
        "Python",
        "C",
        "C++",
        "Java",
        "JavaScript"
    )

    # -------------------------------------------------------
    # Language Support
    # -------------------------------------------------------

    supported_languages = db.Column(
        db.JSON,
        nullable=False,
        default=lambda: [
            "Python",
            "C",
            "C++",
            "Java"
        ]
    )

    # -------------------------------------------------------
    # Validation
    # -------------------------------------------------------

    @validates("title")
    def validate_title(self, key, value):

        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "Problem title must contain at least 3 characters."
            )

        if len(value) > 200:
            raise ValueError(
                "Problem title cannot exceed 200 characters."
            )

        return value

    @validates("slug")
    def validate_slug(self, key, value):

        value = value.strip().lower()

        if " " in value:
            raise ValueError(
                "Slug cannot contain spaces."
            )

        if len(value) < 3:
            raise ValueError(
                "Slug is too short."
            )

        return value

    @validates("difficulty")
    def validate_difficulty(self, key, value):

        if value not in self.DIFFICULTY_LEVELS:

            raise ValueError(
                f"Difficulty must be one of {self.DIFFICULTY_LEVELS}"
            )

        return value

    @validates("marks")
    def validate_marks(self, key, value):

        if value < 0 or value > 1000:

            raise ValueError(
                "Marks must be between 0 and 1000."
            )

        return value

    @validates("time_limit")
    def validate_time_limit(self, key, value):

        if value <= 0:

            raise ValueError(
                "Time limit must be greater than zero."
            )

        if value > 30:

            raise ValueError(
                "Time limit cannot exceed 30 seconds."
            )

        return value

    @validates("memory_limit")
    def validate_memory_limit(self, key, value):

        if value < 16:

            raise ValueError(
                "Memory limit must be at least 16 MB."
            )

        if value > 4096:

            raise ValueError(
                "Memory limit cannot exceed 4096 MB."
            )

        return value

    @validates("supported_languages")
    def validate_supported_languages(self, key, value):

        if not isinstance(value, list):

            raise ValueError(
                "Supported languages must be a list."
            )

        invalid = [

            language

            for language in value

            if language not in self.SUPPORTED_LANGUAGES

        ]

        if invalid:

            raise ValueError(
                f"Unsupported languages: {', '.join(invalid)}"
            )

        return value

    # -------------------------------------------------------
    # Utility Properties
    # -------------------------------------------------------

    @property
    def is_easy(self):

        return self.difficulty == "Easy"

    @property
    def is_medium(self):

        return self.difficulty == "Medium"

    @property
    def is_hard(self):

        return self.difficulty == "Hard"

    @property
    def language_count(self):

        return len(self.supported_languages or [])

    # -------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------

    def supports_language(self, language):

        return language in (self.supported_languages or [])

    def add_language(self, language):

        if language not in self.SUPPORTED_LANGUAGES:

            raise ValueError(
                "Unsupported programming language."
            )

        if language not in self.supported_languages:

            self.supported_languages.append(language)

    def remove_language(self, language):

        if language in self.supported_languages:

            self.supported_languages.remove(language)

    def set_all_languages(self):

        self.supported_languages = list(
            self.SUPPORTED_LANGUAGES
        )
        # -------------------------------------------------------
    # CRUD OPERATIONS
    # -------------------------------------------------------

    def save(self, commit=True):
        """
        Save the current problem.
        """
        db.session.add(self)

        if commit:
            db.session.commit()

        return self

    def update(self, commit=True, **kwargs):
        """
        Update problem fields.
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
        Permanently delete this problem.
        """

        db.session.delete(self)

        if commit:
            db.session.commit()

    # -------------------------------------------------------
    # SOFT DELETE
    # -------------------------------------------------------

    def soft_delete(self, commit=True):
        """
        Disable the problem without removing it.
        """

        self.is_active = False
        self.updated_at = datetime.utcnow()

        if commit:
            db.session.commit()

        return self

    def restore(self, commit=True):
        """
        Restore a soft-deleted problem.
        """

        self.is_active = True
        self.updated_at = datetime.utcnow()

        if commit:
            db.session.commit()

        return self

    # -------------------------------------------------------
    # PUBLISHING
    # -------------------------------------------------------

    def publish_problem(self, commit=True):

        self.is_public = True
        self.updated_at = datetime.utcnow()

        if commit:
            db.session.commit()

        return self

    def hide_problem(self, commit=True):

        self.is_public = False
        self.updated_at = datetime.utcnow()

        if commit:
            db.session.commit()

        return self

    # -------------------------------------------------------
    # CLASS METHODS
    # -------------------------------------------------------

    @classmethod
    def get_by_id(cls, problem_id):
        """
        Return a problem by ID.
        """

        return cls.query.get(problem_id)

    @classmethod
    def get_by_slug(cls, slug):
        """
        Return a problem by slug.
        """

        return cls.query.filter_by(
            slug=slug
        ).first()

    @classmethod
    def all(cls):
        """
        Return all problems.
        """

        return cls.query.order_by(
            cls.created_at.desc()
        ).all()

    @classmethod
    def active(cls):
        """
        Return active problems.
        """

        return cls.query.filter_by(
            is_active=True
        )

    @classmethod
    def public(cls):
        """
        Return publicly visible problems.
        """

        return cls.query.filter_by(
            is_public=True,
            is_active=True
        )

    @classmethod
    def by_difficulty(cls, difficulty):
        """
        Filter by difficulty.
        """

        return cls.query.filter_by(
            difficulty=difficulty,
            is_active=True
        )

    @classmethod
    def recent(cls, limit=10):
        """
        Recently created problems.
        """

        return cls.query.order_by(
            cls.created_at.desc()
        ).limit(limit).all()

    # -------------------------------------------------------
    # BULK OPERATIONS
    # -------------------------------------------------------

    @classmethod
    def bulk_activate(cls, ids):
        """
        Activate multiple problems.
        """

        cls.query.filter(
            cls.id.in_(ids)
        ).update(

            {
                "is_active": True,
                "updated_at": datetime.utcnow()
            },

            synchronize_session=False

        )

        db.session.commit()

    @classmethod
    def bulk_deactivate(cls, ids):
        """
        Deactivate multiple problems.
        """

        cls.query.filter(
            cls.id.in_(ids)
        ).update(

            {
                "is_active": False,
                "updated_at": datetime.utcnow()
            },

            synchronize_session=False

        )

        db.session.commit()

    @classmethod
    def bulk_delete(cls, ids):
        """
        Delete multiple problems.
        """

        cls.query.filter(
            cls.id.in_(ids)
        ).delete(
            synchronize_session=False
        )

        db.session.commit()

    # -------------------------------------------------------
    # EXISTENCE CHECKS
    # -------------------------------------------------------

    @classmethod
    def exists(cls, slug):
        """
        Check whether a slug already exists.
        """

        return db.session.query(

            cls.query.filter_by(
                slug=slug
            ).exists()

        ).scalar()

    @classmethod
    def count(cls):
        """
        Total number of problems.
        """

        return cls.query.count()
        # -------------------------------------------------------
    # SERIALIZATION
    # -------------------------------------------------------

    def to_dict(self):
        """
        Serialize the problem for API responses.
        """

        return {

            "id": self.id,

            "title": self.title,

            "slug": self.slug,

            "short_description": self.short_description,

            "description": self.description,

            "input_format": self.input_format,

            "output_format": self.output_format,

            "constraints": self.constraints,

            "sample_input": self.sample_input,

            "sample_output": self.sample_output,

            "explanation": self.explanation,

            "difficulty": self.difficulty,

            "marks": self.marks,

            "time_limit": self.time_limit,

            "memory_limit": self.memory_limit,

            "supported_languages": self.supported_languages,

            "is_public": self.is_public,

            "is_active": self.is_active,

            "assignment_id": self.assignment_id,

            "created_by": self.created_by,

            "created_at": self.created_at.isoformat()
                if self.created_at else None,

            "updated_at": self.updated_at.isoformat()
                if self.updated_at else None,

            "statistics": {

                "total_test_cases": self.total_test_cases,

                "total_submissions": self.total_submissions,

                "accepted_submissions": self.accepted_submissions

            }

        }

    # -------------------------------------------------------
    # SUMMARY SERIALIZER
    # -------------------------------------------------------

    def summary(self):
        """
        Lightweight serializer for listings.
        """

        return {

            "id": self.id,

            "title": self.title,

            "slug": self.slug,

            "difficulty": self.difficulty,

            "marks": self.marks,

            "time_limit": self.time_limit,

            "memory_limit": self.memory_limit,

            "is_public": self.is_public,

            "is_active": self.is_active

        }

    # -------------------------------------------------------
    # CARD SERIALIZER
    # -------------------------------------------------------

    def card(self):
        """
        Serializer for dashboard cards.
        """

        return {

            "id": self.id,

            "title": self.title,

            "difficulty": self.difficulty,

            "marks": self.marks,

            "submissions": self.total_submissions,

            "accepted": self.accepted_submissions,

            "test_cases": self.total_test_cases

        }

    # -------------------------------------------------------
    # JSON EXPORT
    # -------------------------------------------------------

    def export_json(self):
        """
        Export problem as JSON-compatible dictionary.
        """

        return self.to_dict()

    # -------------------------------------------------------
    # IMPORT DATA
    # -------------------------------------------------------

    def update_from_dict(self, data):
        """
        Update object from dictionary.
        """

        editable_fields = [

            "title",

            "slug",

            "short_description",

            "description",

            "input_format",

            "output_format",

            "constraints",

            "sample_input",

            "sample_output",

            "explanation",

            "difficulty",

            "marks",

            "time_limit",

            "memory_limit",

            "supported_languages",

            "is_public",

            "is_active"

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
        Standard API response object.
        """

        return {

            "success": True,

            "problem": self.to_dict()

        }

    # -------------------------------------------------------
    # CLONE DATA
    # -------------------------------------------------------

    def clone_data(self):
        """
        Return a dictionary suitable for cloning.
        """

        return {

            "title": f"{self.title} (Copy)",

            "slug": None,

            "short_description": self.short_description,

            "description": self.description,

            "input_format": self.input_format,

            "output_format": self.output_format,

            "constraints": self.constraints,

            "sample_input": self.sample_input,

            "sample_output": self.sample_output,

            "explanation": self.explanation,

            "difficulty": self.difficulty,

            "marks": self.marks,

            "time_limit": self.time_limit,

            "memory_limit": self.memory_limit,

            "supported_languages": list(
                self.supported_languages
            ),

            "is_public": False,

            "is_active": False

        }
        # -------------------------------------------------------
    # STATISTICS
    # -------------------------------------------------------

    @property
    def acceptance_rate(self):
        """
        Calculate acceptance rate (%).
        """

        total = self.total_submissions

        if total == 0:
            return 0.0

        accepted = self.accepted_submissions

        return round((accepted / total) * 100, 2)

    @property
    def rejection_rate(self):
        """
        Calculate rejection rate (%).
        """

        return round(
            100 - self.acceptance_rate,
            2
        )

    @property
    def success_ratio(self):
        """
        Accepted / Total tuple.
        """

        return {

            "accepted": self.accepted_submissions,

            "total": self.total_submissions

        }

    # -------------------------------------------------------
    # TEST CASE STATISTICS
    # -------------------------------------------------------

    @property
    def visible_test_cases(self):

        return len(

            [

                tc

                for tc in self.test_cases

                if getattr(tc, "is_hidden", False) is False

            ]

        )

    @property
    def hidden_test_cases(self):

        return len(

            [

                tc

                for tc in self.test_cases

                if getattr(tc, "is_hidden", False)

            ]

        )

    @property
    def has_test_cases(self):

        return self.total_test_cases > 0

    # -------------------------------------------------------
    # SUBMISSION ANALYTICS
    # -------------------------------------------------------

    @property
    def failed_submissions(self):

        return max(

            0,

            self.total_submissions -

            self.accepted_submissions

        )

    @property
    def average_marks(self):
        """
        Average marks awarded for this problem.
        """

        submissions = self.submissions.all()

        if not submissions:

            return 0.0

        total = sum(

            getattr(s, "marks_awarded", 0)

            for s in submissions

        )

        return round(

            total / len(submissions),

            2

        )

    @property
    def highest_score(self):

        submissions = self.submissions.all()

        if not submissions:

            return 0

        return max(

            getattr(s, "marks_awarded", 0)

            for s in submissions

        )

    # -------------------------------------------------------
    # EXECUTION METRICS
    # -------------------------------------------------------

    @property
    def average_execution_time(self):

        submissions = self.submissions.all()

        values = [

            getattr(s, "execution_time", 0)

            for s in submissions

            if getattr(s, "execution_time", None) is not None

        ]

        if not values:

            return 0

        return round(

            sum(values) / len(values),

            3

        )

    @property
    def average_memory_usage(self):

        submissions = self.submissions.all()

        values = [

            getattr(s, "memory_used", 0)

            for s in submissions

            if getattr(s, "memory_used", None) is not None

        ]

        if not values:

            return 0

        return round(

            sum(values) / len(values),

            2

        )

    # -------------------------------------------------------
    # DASHBOARD STATISTICS
    # -------------------------------------------------------

    def statistics(self):
        """
        Complete statistics dictionary.
        """

        return {

            "problem_id": self.id,

            "title": self.title,

            "difficulty": self.difficulty,

            "total_test_cases": self.total_test_cases,

            "visible_test_cases": self.visible_test_cases,

            "hidden_test_cases": self.hidden_test_cases,

            "total_submissions": self.total_submissions,

            "accepted_submissions": self.accepted_submissions,

            "failed_submissions": self.failed_submissions,

            "acceptance_rate": self.acceptance_rate,

            "average_marks": self.average_marks,

            "highest_score": self.highest_score,

            "average_execution_time":
                self.average_execution_time,

            "average_memory_usage":
                self.average_memory_usage

        }

    # -------------------------------------------------------
    # QUICK SUMMARY
    # -------------------------------------------------------

    def analytics_summary(self):

        return {

            "acceptance_rate": self.acceptance_rate,

            "submissions": self.total_submissions,

            "difficulty": self.difficulty,

            "marks": self.marks

        }
        # -------------------------------------------------------
    # SEARCH & FILTER METHODS
    # -------------------------------------------------------

    @classmethod
    def search(cls, keyword):
        """
        Search problems by title, slug or description.
        """

        if not keyword:
            return cls.query

        keyword = f"%{keyword}%"

        return cls.query.filter(

            db.or_(

                cls.title.ilike(keyword),

                cls.slug.ilike(keyword),

                cls.short_description.ilike(keyword),

                cls.description.ilike(keyword)

            )

        )

    @classmethod
    def filter_by_difficulty(cls, difficulty):
        """
        Filter problems by difficulty.
        """

        return cls.query.filter_by(

            difficulty=difficulty,

            is_active=True

        )

    @classmethod
    def filter_by_assignment(cls, assignment_id):
        """
        Filter by assignment.
        """

        return cls.query.filter_by(

            assignment_id=assignment_id

        )

    @classmethod
    def filter_by_teacher(cls, teacher_id):
        """
        Filter by creator.
        """

        return cls.query.filter_by(

            created_by=teacher_id

        )

    @classmethod
    def filter_by_language(cls, language):
        """
        Problems supporting a language.
        """

        return cls.query.filter(

            cls.supported_languages.contains([language])

        )

    @classmethod
    def public_problems(cls):
        """
        Only public active problems.
        """

        return cls.query.filter_by(

            is_public=True,

            is_active=True

        )

    @classmethod
    def private_problems(cls):
        """
        Private problems.
        """

        return cls.query.filter_by(

            is_public=False,

            is_active=True

        )

    # -------------------------------------------------------
    # SORTING
    # -------------------------------------------------------

    @classmethod
    def sort_by_latest(cls):

        return cls.query.order_by(

            cls.created_at.desc()

        )

    @classmethod
    def sort_by_oldest(cls):

        return cls.query.order_by(

            cls.created_at.asc()

        )

    @classmethod
    def sort_by_title(cls):

        return cls.query.order_by(

            cls.title.asc()

        )

    @classmethod
    def sort_by_marks(cls):

        return cls.query.order_by(

            cls.marks.desc()

        )

    @classmethod
    def sort_by_difficulty(cls):

        return cls.query.order_by(

            cls.difficulty.asc()

        )

    # -------------------------------------------------------
    # PAGINATION
    # -------------------------------------------------------

    @classmethod
    def paginate_results(

        cls,

        page=1,

        per_page=10,

        query=None

    ):
        """
        Paginate any problem query.
        """

        if query is None:

            query = cls.query

        return query.paginate(

            page=page,

            per_page=per_page,

            error_out=False

        )

    # -------------------------------------------------------
    # ADVANCED SEARCH
    # -------------------------------------------------------

    @classmethod
    def advanced_search(

        cls,

        keyword=None,

        difficulty=None,

        language=None,

        public_only=True

    ):

        query = cls.query

        if public_only:

            query = query.filter_by(

                is_public=True,

                is_active=True

            )

        if keyword:

            keyword = f"%{keyword}%"

            query = query.filter(

                db.or_(

                    cls.title.ilike(keyword),

                    cls.description.ilike(keyword),

                    cls.short_description.ilike(keyword)

                )

            )

        if difficulty:

            query = query.filter_by(

                difficulty=difficulty

            )

        if language:

            query = query.filter(

                cls.supported_languages.contains(

                    [language]

                )

            )

        return query

    # -------------------------------------------------------
    # RANDOM PROBLEM
    # -------------------------------------------------------

    @classmethod
    def random_problem(cls):

        return cls.query.filter_by(

            is_public=True,

            is_active=True

        ).order_by(

            db.func.random()

        ).first()

    # -------------------------------------------------------
    # RECENTLY UPDATED
    # -------------------------------------------------------

    @classmethod
    def recently_updated(cls, limit=10):

        return cls.query.order_by(

            cls.updated_at.desc()

        ).limit(limit).all()

    # -------------------------------------------------------
    # TOP PROBLEMS
    # -------------------------------------------------------

    @classmethod
    def top_problems(cls, limit=10):
        """
        Most attempted problems.
        """

        return sorted(

            cls.query.filter_by(

                is_active=True

            ).all(),

            key=lambda p: p.total_submissions,

            reverse=True

        )[:limit]

    # -------------------------------------------------------
    # RECOMMENDED
    # -------------------------------------------------------

    @classmethod
    def recommended(cls, difficulty="Easy", limit=5):

        return cls.query.filter_by(

            difficulty=difficulty,

            is_public=True,

            is_active=True

        ).limit(limit).all()
        # -------------------------------------------------------
    # CATEGORY & TAGS
    # -------------------------------------------------------

    category = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Draft",
        index=True
    )

    is_featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    is_archived = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # -------------------------------------------------------
    # STATUS CONSTANTS
    # -------------------------------------------------------

    STATUS_DRAFT = "Draft"
    STATUS_PUBLISHED = "Published"
    STATUS_ARCHIVED = "Archived"

    VALID_STATUSES = (
        STATUS_DRAFT,
        STATUS_PUBLISHED,
        STATUS_ARCHIVED
    )

    # -------------------------------------------------------
    # CATEGORY METHODS
    # -------------------------------------------------------

    @property
    def category_name(self):
        return self.category or "General"

    def set_category(self, category):
        self.category = category.strip()

    # -------------------------------------------------------
    # STATUS METHODS
    # -------------------------------------------------------

    @property
    def is_draft(self):
        return self.status == self.STATUS_DRAFT

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    @property
    def is_archived_status(self):
        return self.status == self.STATUS_ARCHIVED

    def publish(self):

        self.status = self.STATUS_PUBLISHED
        self.is_public = True
        self.is_active = True

    def draft(self):

        self.status = self.STATUS_DRAFT
        self.is_public = False

    def archive(self):

        self.status = self.STATUS_ARCHIVED
        self.is_archived = True
        self.is_active = False

    def restore_from_archive(self):

        self.status = self.STATUS_DRAFT
        self.is_archived = False
        self.is_active = True

    # -------------------------------------------------------
    # FEATURED
    # -------------------------------------------------------

    def feature(self):

        self.is_featured = True

    def unfeature(self):

        self.is_featured = False

    # -------------------------------------------------------
    # BADGES
    # -------------------------------------------------------

    @property
    def difficulty_badge(self):

        badges = {

            "Easy": "success",

            "Medium": "warning",

            "Hard": "danger"

        }

        return badges.get(

            self.difficulty,

            "secondary"

        )

    @property
    def status_badge(self):

        badges = {

            "Draft": "secondary",

            "Published": "success",

            "Archived": "dark"

        }

        return badges.get(

            self.status,

            "secondary"

        )

    # -------------------------------------------------------
    # CLASS METHODS
    # -------------------------------------------------------

    @classmethod
    def featured(cls):

        return cls.query.filter_by(

            is_featured=True,

            is_active=True,

            is_public=True

        )

    @classmethod
    def archived(cls):

        return cls.query.filter_by(

            is_archived=True

        )

    @classmethod
    def drafts(cls):

        return cls.query.filter_by(

            status=cls.STATUS_DRAFT

        )

    @classmethod
    def published(cls):

        return cls.query.filter_by(

            status=cls.STATUS_PUBLISHED,

            is_active=True

        )

    @classmethod
    def by_category(cls, category):

        return cls.query.filter_by(

            category=category,

            is_active=True

        )

    @classmethod
    def categories(cls):

        rows = db.session.query(

            cls.category

        ).distinct().all()

        return [

            row[0]

            for row in rows

            if row[0]

        ]

    # -------------------------------------------------------
    # DISPLAY HELPERS
    # -------------------------------------------------------

    def short_title(self, length=50):

        if len(self.title) <= length:

            return self.title

        return self.title[:length] + "..."

    def short_description_text(self, length=120):

        text = self.short_description or ""

        if len(text) <= length:

            return text

        return text[:length] + "..."

    # -------------------------------------------------------
    # DASHBOARD CARD
    # -------------------------------------------------------

    def dashboard_card(self):

        return {

            "id": self.id,

            "title": self.short_title(),

            "difficulty": self.difficulty,

            "difficulty_badge": self.difficulty_badge,

            "status": self.status,

            "status_badge": self.status_badge,

            "category": self.category_name,

            "featured": self.is_featured,

            "public": self.is_public,

            "submissions": self.total_submissions,

            "acceptance_rate": self.acceptance_rate

        }
        # -------------------------------------------------------
    # SLUG UTILITIES
    # -------------------------------------------------------

    @staticmethod
    def generate_slug(title):
        """
        Generate a URL-friendly slug.
        """

        import re

        slug = title.lower().strip()

        slug = re.sub(r"[^a-z0-9]+", "-", slug)

        slug = re.sub(r"-+", "-", slug)

        return slug.strip("-")

    @classmethod
    def slug_exists(cls, slug, exclude_id=None):
        """
        Check whether a slug already exists.
        """

        query = cls.query.filter_by(slug=slug)

        if exclude_id is not None:

            query = query.filter(cls.id != exclude_id)

        return db.session.query(query.exists()).scalar()

    @classmethod
    def generate_unique_slug(cls, title):

        base = cls.generate_slug(title)

        slug = base

        counter = 1

        while cls.slug_exists(slug):

            slug = f"{base}-{counter}"

            counter += 1

        return slug

    # -------------------------------------------------------
    # DUPLICATE DETECTION
    # -------------------------------------------------------

    def is_duplicate(self):

        return Problem.query.filter(

            Problem.id != self.id,

            db.or_(

                Problem.slug == self.slug,

                Problem.title == self.title

            )

        ).first() is not None

    # -------------------------------------------------------
    # CLONE
    # -------------------------------------------------------

    def clone(self):

        clone = Problem(

            title=f"{self.title} (Copy)",

            slug=Problem.generate_unique_slug(

                f"{self.title}-copy"

            ),

            short_description=self.short_description,

            description=self.description,

            input_format=self.input_format,

            output_format=self.output_format,

            constraints=self.constraints,

            sample_input=self.sample_input,

            sample_output=self.sample_output,

            explanation=self.explanation,

            difficulty=self.difficulty,

            marks=self.marks,

            time_limit=self.time_limit,

            memory_limit=self.memory_limit,

            supported_languages=list(

                self.supported_languages

            ),

            category=self.category,

            created_by=self.created_by,

            assignment_id=self.assignment_id,

            is_public=False,

            is_active=False,

            status=self.STATUS_DRAFT

        )

        return clone

    # -------------------------------------------------------
    # VERSIONING
    # -------------------------------------------------------

    version = db.Column(

        db.Integer,

        nullable=False,

        default=1

    )

    def increment_version(self):

        self.version += 1

        self.updated_at = datetime.utcnow()

    # -------------------------------------------------------
    # AUDIT HELPERS
    # -------------------------------------------------------

    def audit_data(self):

        return {

            "problem_id": self.id,

            "title": self.title,

            "version": self.version,

            "updated_at": self.updated_at,

            "created_by": self.created_by,

            "status": self.status

        }

    # -------------------------------------------------------
    # VALIDITY CHECKS
    # -------------------------------------------------------

    @property
    def is_complete(self):

        required = [

            self.title,

            self.description,

            self.input_format,

            self.output_format,

            self.sample_input,

            self.sample_output

        ]

        return all(required)

    @property
    def ready_for_publish(self):

        return (

            self.is_complete

            and

            self.total_test_cases > 0

        )

    # -------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------

    def summary_text(self):

        return (

            f"{self.title} "

            f"[{self.difficulty}] "

            f"({self.marks} Marks)"

        )

    # -------------------------------------------------------
    # HASH
    # -------------------------------------------------------

    def content_hash(self):

        import hashlib

        text = (

            self.title +

            self.description +

            self.sample_input +

            self.sample_output

        )

        return hashlib.sha256(

            text.encode()

        ).hexdigest()

    # -------------------------------------------------------
    # EQUALITY
    # -------------------------------------------------------

    def __eq__(self, other):

        if not isinstance(other, Problem):

            return False

        return self.id == other.id

    def __hash__(self):

        return hash(self.id)
        # -------------------------------------------------------
    # SQLALCHEMY EVENT HELPERS
    # -------------------------------------------------------

    def before_insert(self):
        """
        Prepare the object before insertion.
        """

        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)

        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def before_update(self):
        """
        Update metadata before saving.
        """

        self.updated_at = datetime.utcnow()

        if self.version is None:
            self.version = 1
        else:
            self.version += 1

    # -------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------

    def validate(self):
        """
        Validate the problem before saving.
        """

        if not self.title:
            raise ValueError("Problem title is required.")

        if not self.description:
            raise ValueError("Problem description is required.")

        if self.time_limit <= 0:
            raise ValueError("Invalid time limit.")

        if self.memory_limit < 16:
            raise ValueError("Memory limit must be at least 16 MB.")

        return True

    # -------------------------------------------------------
    # SAVE WITH VALIDATION
    # -------------------------------------------------------

    def save_safe(self):
        """
        Validate and save the object.
        """

        self.validate()

        self.before_update()

        db.session.add(self)

        db.session.commit()

        return self

    # -------------------------------------------------------
    # EXPORT
    # -------------------------------------------------------

    def export(self):
        """
        Complete export format.
        """

        return {

            "metadata": {

                "id": self.id,
                "title": self.title,
                "slug": self.slug,
                "version": self.version,
                "difficulty": self.difficulty,
                "status": self.status,
                "category": self.category

            },

            "problem": self.to_dict(),

            "statistics": self.statistics()

        }

    # -------------------------------------------------------
    # STRING REPRESENTATION
    # -------------------------------------------------------

    def __str__(self):

        return self.title

    # -------------------------------------------------------
    # DEBUG
    # -------------------------------------------------------

    def debug(self):

        return {

            "id": self.id,

            "title": self.title,

            "slug": self.slug,

            "difficulty": self.difficulty,

            "status": self.status,

            "public": self.is_public,

            "active": self.is_active,

            "version": self.version

        }


# ==========================================================
# SQLALCHEMY EVENTS
# ==========================================================

from sqlalchemy import event


@event.listens_for(Problem, "before_insert")
def problem_before_insert(mapper, connection, target):
    target.before_insert()


@event.listens_for(Problem, "before_update")
def problem_before_update(mapper, connection, target):
    target.before_update()


# ==========================================================
# MODULE EXPORT
# ==========================================================

__all__ = [

    "Problem"

]