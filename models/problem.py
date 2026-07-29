from datetime import datetime

from sqlalchemy import Text, CheckConstraint
from sqlalchemy.orm import validates

from extensions import db


class Problem(db.Model):
    __tablename__ = "problems"

    # ===========================
    # Primary Key
    # ===========================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ===========================
    # Basic Information
    # ===========================

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

    # ===========================
    # Difficulty
    # ===========================

    difficulty = db.Column(
        db.String(20),
        nullable=False,
        default="Easy",
        index=True
    )

    # ===========================
    # Limits
    # ===========================

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

    marks = db.Column(
        db.Integer,
        nullable=False,
        default=100
    )

    # ===========================
    # Category
    # ===========================

    category = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Draft"
    )

    version = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    # ===========================
    # Flags
    # ===========================

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

    # ===========================
    # Supported Languages
    # ===========================

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

    # ===========================
    # Foreign Keys
    # ===========================

    created_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "teachers.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "assignments.id",
            ondelete="CASCADE"
        ),
        nullable=True
    )

    # ===========================
    # Audit
    # ===========================

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

    # ===========================
    # Relationships
    # ===========================

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
        cascade="all, delete-orphan"
    )

    submissions = db.relationship(
        "Submission",
        back_populates="problem",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    tags = db.relationship(
        "ProblemTag",
        secondary="problem_tag_map",
        back_populates="problems"
    )

    # ===========================
    # Constraints
    # ===========================

    __table_args__ = (

        CheckConstraint(
            "marks>=0",
            name="ck_problem_marks"
        ),

        CheckConstraint(
            "time_limit>0",
            name="ck_problem_time"
        ),

        CheckConstraint(
            "memory_limit>=16",
            name="ck_problem_memory"
        ),

        CheckConstraint(
            "difficulty IN ('Easy','Medium','Hard')",
            name="ck_problem_difficulty"
        ),
    )
        # ==========================================================
    # CONSTANTS
    # ==========================================================

    DIFFICULTY_LEVELS = (
        "Easy",
        "Medium",
        "Hard"
    )

    STATUS_DRAFT = "Draft"
    STATUS_PUBLISHED = "Published"
    STATUS_ARCHIVED = "Archived"

    VALID_STATUSES = (
        STATUS_DRAFT,
        STATUS_PUBLISHED,
        STATUS_ARCHIVED
    )

    SUPPORTED_LANGUAGES = (
        "Python",
        "C",
        "C++",
        "Java",
        "JavaScript"
    )

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(self):
        return (
            f"<Problem(id={self.id}, "
            f"title='{self.title}', "
            f"difficulty='{self.difficulty}')>"
        )

    def __str__(self):
        return self.title

    # ==========================================================
    # VALIDATORS
    # ==========================================================

    @validates("title")
    def validate_title(self, key, value):

        value = value.strip()

        if len(value) < 3:
            raise ValueError(
                "Title must contain at least 3 characters."
            )

        if len(value) > 200:
            raise ValueError(
                "Title cannot exceed 200 characters."
            )

        return value


    @validates("slug")
    def validate_slug(self, key, value):

        value = value.strip().lower()

        if " " in value:
            raise ValueError(
                "Slug cannot contain spaces."
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

        if value < 0:
            raise ValueError(
                "Marks cannot be negative."
            )

        return value


    @validates("time_limit")
    def validate_time_limit(self, key, value):

        if value <= 0:
            raise ValueError(
                "Time limit must be greater than zero."
            )

        return value


    @validates("memory_limit")
    def validate_memory_limit(self, key, value):

        if value < 16:
            raise ValueError(
                "Memory limit must be at least 16 MB."
            )

        return value


    @validates("supported_languages")
    def validate_languages(self, key, value):

        if not isinstance(value, list):
            raise ValueError(
                "supported_languages must be a list."
            )

        for language in value:

            if language not in self.SUPPORTED_LANGUAGES:
                raise ValueError(
                    f"{language} is not supported."
                )

        return value

    # ==========================================================
    # HELPER PROPERTIES
    # ==========================================================

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
    def acceptance_rate(self):

        total = self.total_submissions

        if total == 0:
            return 0

        return round(
            self.accepted_submissions * 100 / total,
            2
        )


    @property
    def author_name(self):

        if self.teacher:
            return self.teacher.name

        return "Unknown"

    # ==========================================================
    # LANGUAGE METHODS
    # ==========================================================

    def supports_language(self, language):
        return language in self.supported_languages


    def add_language(self, language):

        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError("Unsupported language.")

        if language not in self.supported_languages:
            self.supported_languages.append(language)


    def remove_language(self, language):

        if language in self.supported_languages:
            self.supported_languages.remove(language)

    # ==========================================================
    # STATUS METHODS
    # ==========================================================

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


    def restore(self):

        self.status = self.STATUS_DRAFT
        self.is_archived = False
        self.is_active = True

    # ==========================================================
    # CRUD METHODS
    # ==========================================================

    def save(self, commit=True):

        db.session.add(self)

        if commit:
            db.session.commit()

        return self


    def delete(self, commit=True):

        db.session.delete(self)

        if commit:
            db.session.commit()


    def update(self, commit=True, **kwargs):

        for key, value in kwargs.items():

            if hasattr(self, key):
                setattr(self, key, value)

        self.updated_at = datetime.utcnow()

        if commit:
            db.session.commit()

        return self

    # ==========================================================
    # SERIALIZER
    # ==========================================================

    def to_dict(self):

        return {

            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "short_description": self.short_description,
            "description": self.description,
            "difficulty": self.difficulty,
            "marks": self.marks,
            "time_limit": self.time_limit,
            "memory_limit": self.memory_limit,
            "supported_languages": self.supported_languages,
            "category": self.category,
            "status": self.status,
            "is_public": self.is_public,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "assignment_id": self.assignment_id,
            "created_at": self.created_at.isoformat()
                if self.created_at else None,
            "updated_at": self.updated_at.isoformat()
                if self.updated_at else None
        }
        # ==========================================================
    # SEARCH METHODS
    # ==========================================================

    @classmethod
    def get_by_id(cls, problem_id):
        return cls.query.get(problem_id)

    @classmethod
    def get_by_slug(cls, slug):
        return cls.query.filter_by(slug=slug).first()

    @classmethod
    def all(cls):
        return cls.query.order_by(
            cls.created_at.desc()
        ).all()

    @classmethod
    def active(cls):
        return cls.query.filter_by(
            is_active=True
        )

    @classmethod
    def public(cls):
        return cls.query.filter_by(
            is_public=True,
            is_active=True
        )

    @classmethod
    def by_difficulty(cls, difficulty):
        return cls.query.filter_by(
            difficulty=difficulty,
            is_active=True
        )

    @classmethod
    def by_category(cls, category):
        return cls.query.filter_by(
            category=category,
            is_active=True
        )

    @classmethod
    def search(cls, keyword):

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

    # ==========================================================
    # PAGINATION
    # ==========================================================

    @classmethod
    def paginate_results(
        cls,
        page=1,
        per_page=10,
        query=None
    ):

        if query is None:
            query = cls.query

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    # ==========================================================
    # RANDOM / RECENT
    # ==========================================================

    @classmethod
    def random_problem(cls):

        return cls.query.filter_by(
            is_public=True,
            is_active=True
        ).order_by(
            db.func.random()
        ).first()

    @classmethod
    def recent(cls, limit=10):

        return cls.query.order_by(
            cls.created_at.desc()
        ).limit(limit).all()

    @classmethod
    def recently_updated(cls, limit=10):

        return cls.query.order_by(
            cls.updated_at.desc()
        ).limit(limit).all()

    # ==========================================================
    # FEATURED
    # ==========================================================

    @classmethod
    def featured(cls):

        return cls.query.filter_by(
            is_featured=True,
            is_public=True,
            is_active=True
        )

    @classmethod
    def drafts(cls):

        return cls.query.filter_by(
            status=cls.STATUS_DRAFT
        )

    @classmethod
    def archived(cls):

        return cls.query.filter_by(
            is_archived=True
        )

    # ==========================================================
    # SLUG UTILITIES
    # ==========================================================

    @staticmethod
    def generate_slug(title):

        import re

        slug = title.lower().strip()

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            slug
        )

        slug = re.sub(
            r"-+",
            "-",
            slug
        )

        return slug.strip("-")

    @classmethod
    def slug_exists(
        cls,
        slug,
        exclude_id=None
    ):

        query = cls.query.filter_by(
            slug=slug
        )

        if exclude_id is not None:
            query = query.filter(
                cls.id != exclude_id
            )

        return db.session.query(
            query.exists()
        ).scalar()

    @classmethod
    def generate_unique_slug(
        cls,
        title
    ):

        base = cls.generate_slug(title)

        slug = base

        counter = 1

        while cls.slug_exists(slug):

            slug = f"{base}-{counter}"

            counter += 1

        return slug

    # ==========================================================
    # CLONE
    # ==========================================================

    def clone(self):

        clone = Problem(

            title=f"{self.title} (Copy)",

            slug=Problem.generate_unique_slug(
                self.title + "-copy"
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

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def statistics(self):

        return {

            "problem_id": self.id,

            "title": self.title,

            "difficulty": self.difficulty,

            "total_test_cases": self.total_test_cases,

            "total_submissions": self.total_submissions,

            "accepted_submissions": self.accepted_submissions,

            "acceptance_rate": self.acceptance_rate
        }

    # ==========================================================
    # DASHBOARD CARD
    # ==========================================================

    def dashboard_card(self):

        return {

            "id": self.id,

            "title": self.title,

            "difficulty": self.difficulty,

            "marks": self.marks,

            "status": self.status,

            "category": self.category,

            "public": self.is_public,

            "active": self.is_active,

            "submissions": self.total_submissions,

            "acceptance_rate": self.acceptance_rate
        }

    # ==========================================================
    # BEFORE INSERT / UPDATE
    # ==========================================================

    def before_insert(self):

        if not self.slug:
            self.slug = self.generate_unique_slug(
                self.title
            )

        self.created_at = datetime.utcnow()

        self.updated_at = datetime.utcnow()

    def before_update(self):

        self.updated_at = datetime.utcnow()

        self.version += 1
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
# VALIDATION
# ==========================================================

def validate_problem(problem):

    if not problem.title:
        raise ValueError("Problem title is required.")

    if not problem.description:
        raise ValueError("Problem description is required.")

    if problem.time_limit <= 0:
        raise ValueError("Time limit must be greater than zero.")

    if problem.memory_limit < 16:
        raise ValueError("Memory limit must be at least 16 MB.")

    if problem.difficulty not in Problem.DIFFICULTY_LEVELS:
        raise ValueError("Invalid difficulty.")

    return True


# ==========================================================
# EXPORT
# ==========================================================

def export_problem(problem):

    return {

        "id": problem.id,

        "title": problem.title,

        "slug": problem.slug,

        "difficulty": problem.difficulty,

        "marks": problem.marks,

        "category": problem.category,

        "status": problem.status,

        "description": problem.description,

        "input_format": problem.input_format,

        "output_format": problem.output_format,

        "constraints": problem.constraints,

        "sample_input": problem.sample_input,

        "sample_output": problem.sample_output,

        "explanation": problem.explanation,

        "supported_languages": problem.supported_languages,

        "created_by": problem.created_by,

        "assignment_id": problem.assignment_id,

        "created_at": (
            problem.created_at.isoformat()
            if problem.created_at else None
        ),

        "updated_at": (
            problem.updated_at.isoformat()
            if problem.updated_at else None
        )
    }


# ==========================================================
# IMPORT
# ==========================================================

def import_problem(problem, data):

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
        "category",
        "status",
        "supported_languages",
        "is_public",
        "is_active"

    ]

    for field in editable_fields:

        if field in data:
            setattr(problem, field, data[field])

    return problem


# ==========================================================
# DEBUG
# ==========================================================

def debug_problem(problem):

    return {

        "id": problem.id,

        "title": problem.title,

        "slug": problem.slug,

        "difficulty": problem.difficulty,

        "status": problem.status,

        "public": problem.is_public,

        "active": problem.is_active,

        "version": problem.version
    }


# ==========================================================
# MODULE EXPORT
# ==========================================================

__all__ = [
    "Problem",
    "validate_problem",
    "export_problem",
    "import_problem",
    "debug_problem"
]