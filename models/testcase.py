"""
==========================================================
Lab Auto Grader
TestCase Model
Part 1
==========================================================
"""

from datetime import datetime

from sqlalchemy import Text
from sqlalchemy.orm import validates

from extensions import db


class TestCase(db.Model):
    """
    Programming Problem Test Case Model
    """

    __tablename__ = "test_cases"

    # -------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -------------------------------------------------------
    # Foreign Key
    # -------------------------------------------------------

    problem_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "problems.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # -------------------------------------------------------
    # Basic Information
    # -------------------------------------------------------

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    # -------------------------------------------------------
    # Input / Output
    # -------------------------------------------------------

    input_data = db.Column(
        Text,
        nullable=False
    )

    expected_output = db.Column(
        Text,
        nullable=False
    )

    explanation = db.Column(
        Text,
        nullable=True
    )

    # -------------------------------------------------------
    # Resource Limits
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
        db.Float,
        nullable=False,
        default=0.0
    )

    weight = db.Column(
        db.Float,
        nullable=False,
        default=1.0
    )

    # -------------------------------------------------------
    # Visibility
    # -------------------------------------------------------

    is_hidden = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    is_sample = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # -------------------------------------------------------
    # Execution Order
    # -------------------------------------------------------

    execution_order = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    # -------------------------------------------------------
    # Metadata
    # -------------------------------------------------------

    tags = db.Column(
        db.JSON,
        nullable=True,
        default=list
    )

    notes = db.Column(
        Text,
        nullable=True
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

            f"<TestCase "

            f"id={self.id} "

            f"problem={self.problem_id} "

            f"name='{self.name}'>"

        )
        # -------------------------------------------------------
    # RELATIONSHIPS
    # -------------------------------------------------------

    problem = db.relationship(
        "Problem",
        back_populates="test_cases",
        lazy="joined"
    )

    # -------------------------------------------------------
    # STATUS CONSTANTS
    # -------------------------------------------------------

    STATUS_ACTIVE = "Active"
    STATUS_INACTIVE = "Inactive"

    # -------------------------------------------------------
    # COMPUTED PROPERTIES
    # -------------------------------------------------------

    @property
    def status(self):
        """
        Human-readable status.
        """
        return (
            self.STATUS_ACTIVE
            if self.is_active
            else self.STATUS_INACTIVE
        )

    @property
    def visibility(self):
        """
        Sample / Hidden / Normal
        """
        if self.is_sample:
            return "Sample"

        if self.is_hidden:
            return "Hidden"

        return "Public"

    @property
    def has_explanation(self):
        return bool(
            self.explanation and
            self.explanation.strip()
        )

    @property
    def input_size(self):
        return len(
            self.input_data or ""
        )

    @property
    def output_size(self):
        return len(
            self.expected_output or ""
        )

    @property
    def total_size(self):
        return self.input_size + self.output_size

    @property
    def tag_count(self):
        return len(
            self.tags or []
        )

    @property
    def is_weighted(self):
        return self.weight > 1

    # -------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------

    def activate(self):

        self.is_active = True

    def deactivate(self):

        self.is_active = False

    def make_hidden(self):

        self.is_hidden = True

        self.is_sample = False

    def make_public(self):

        self.is_hidden = False

        self.is_sample = False

    def make_sample(self):

        self.is_sample = True

        self.is_hidden = False

    def move_up(self):

        if self.execution_order > 1:

            self.execution_order -= 1

    def move_down(self):

        self.execution_order += 1

    def add_tag(self, tag):

        if self.tags is None:

            self.tags = []

        tag = tag.strip()

        if tag and tag not in self.tags:

            self.tags.append(tag)

    def remove_tag(self, tag):

        if self.tags and tag in self.tags:

            self.tags.remove(tag)

    def clear_tags(self):

        self.tags = []

    def has_tag(self, tag):

        return (

            self.tags is not None

            and

            tag in self.tags

        )

    # -------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------

    @property
    def summary(self):

        return {

            "id": self.id,

            "name": self.name,

            "problem_id": self.problem_id,

            "visibility": self.visibility,

            "marks": self.marks,

            "weight": self.weight,

            "execution_order":
                self.execution_order,

            "active":
                self.is_active

        }
        # -------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------

    @validates("name")
    def validate_name(self, key, value):

        value = value.strip()

        if not value:
            raise ValueError(
                "Test case name cannot be empty."
            )

        if len(value) > 100:
            raise ValueError(
                "Test case name cannot exceed 100 characters."
            )

        return value

    @validates("input_data")
    def validate_input_data(self, key, value):

        if value is None:
            raise ValueError(
                "Input data is required."
            )

        if len(value) > 500000:
            raise ValueError(
                "Input data exceeds maximum size."
            )

        return value

    @validates("expected_output")
    def validate_expected_output(self, key, value):

        if value is None:
            raise ValueError(
                "Expected output is required."
            )

        if len(value) > 500000:
            raise ValueError(
                "Expected output exceeds maximum size."
            )

        return value

    @validates("time_limit")
    def validate_time_limit(self, key, value):

        value = float(value)

        if value <= 0:
            raise ValueError(
                "Time limit must be greater than zero."
            )

        if value > 60:
            raise ValueError(
                "Time limit cannot exceed 60 seconds."
            )

        return value

    @validates("memory_limit")
    def validate_memory_limit(self, key, value):

        value = int(value)

        if value < 16:
            raise ValueError(
                "Memory limit must be at least 16 MB."
            )

        if value > 8192:
            raise ValueError(
                "Memory limit cannot exceed 8192 MB."
            )

        return value

    @validates("marks")
    def validate_marks(self, key, value):

        value = float(value)

        if value < 0:
            raise ValueError(
                "Marks cannot be negative."
            )

        if value > 1000:
            raise ValueError(
                "Marks cannot exceed 1000."
            )

        return value

    @validates("weight")
    def validate_weight(self, key, value):

        value = float(value)

        if value <= 0:
            raise ValueError(
                "Weight must be greater than zero."
            )

        return value

    @validates("execution_order")
    def validate_execution_order(self, key, value):

        value = int(value)

        if value < 1:
            raise ValueError(
                "Execution order must be at least 1."
            )

        return value

    @validates("tags")
    def validate_tags(self, key, value):

        if value is None:
            return []

        if not isinstance(value, list):
            raise ValueError(
                "Tags must be a list."
            )

        cleaned = []

        for tag in value:

            tag = str(tag).strip()

            if tag and tag not in cleaned:
                cleaned.append(tag)

        return cleaned

    # -------------------------------------------------------
    # VALIDATION HELPERS
    # -------------------------------------------------------

    @property
    def input_lines(self):
        """
        Number of input lines.
        """
        return len(
            (self.input_data or "").splitlines()
        )

    @property
    def output_lines(self):
        """
        Number of output lines.
        """
        return len(
            (self.expected_output or "").splitlines()
        )

    @property
    def input_size_kb(self):
        """
        Input size in KB.
        """
        return round(
            len((self.input_data or "").encode("utf-8")) / 1024,
            2
        )

    @property
    def output_size_kb(self):
        """
        Output size in KB.
        """
        return round(
            len((self.expected_output or "").encode("utf-8")) / 1024,
            2
        )

    @property
    def total_size_kb(self):
        """
        Combined input/output size in KB.
        """
        return round(
            self.input_size_kb + self.output_size_kb,
            2
        )

    @property
    def is_large(self):
        """
        Large test case indicator.
        """
        return self.total_size_kb > 100

    @property
    def is_small(self):
        """
        Small test case indicator.
        """
        return self.total_size_kb <= 5
        # -------------------------------------------------------
    # CRUD OPERATIONS
    # -------------------------------------------------------

    def save(self, commit=True):
        """
        Save test case.
        """

        db.session.add(self)

        if commit:
            db.session.commit()

        return self

    def update(self, commit=True, **kwargs):
        """
        Update test case fields.
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
        Delete test case.
        """

        db.session.delete(self)

        if commit:
            db.session.commit()

    # -------------------------------------------------------
    # VISIBILITY HELPERS
    # -------------------------------------------------------

    def hide(self):

        self.is_hidden = True
        self.is_sample = False

    def show(self):

        self.is_hidden = False

    def enable(self):

        self.is_active = True

    def disable(self):

        self.is_active = False

    # -------------------------------------------------------
    # EXECUTION ORDER
    # -------------------------------------------------------

    def set_execution_order(self, order):

        if order < 1:
            raise ValueError(
                "Execution order must be greater than zero."
            )

        self.execution_order = order

    # -------------------------------------------------------
    # DUPLICATE CHECK
    # -------------------------------------------------------

    def is_duplicate(self):

        return TestCase.query.filter(

            TestCase.problem_id == self.problem_id,

            TestCase.input_data == self.input_data,

            TestCase.expected_output == self.expected_output,

            TestCase.id != self.id

        ).first() is not None

    # -------------------------------------------------------
    # CLASS METHODS
    # -------------------------------------------------------

    @classmethod
    def get_by_id(cls, testcase_id):

        return cls.query.get(testcase_id)

    @classmethod
    def by_problem(cls, problem_id):

        return cls.query.filter_by(

            problem_id=problem_id,

            is_active=True

        ).order_by(

            cls.execution_order.asc()

        )

    @classmethod
    def samples(cls, problem_id):

        return cls.query.filter_by(

            problem_id=problem_id,

            is_sample=True,

            is_active=True

        ).order_by(

            cls.execution_order.asc()

        )

    @classmethod
    def hidden(cls, problem_id):

        return cls.query.filter_by(

            problem_id=problem_id,

            is_hidden=True,

            is_active=True

        ).order_by(

            cls.execution_order.asc()

        )

    @classmethod
    def public(cls, problem_id):

        return cls.query.filter_by(

            problem_id=problem_id,

            is_hidden=False,

            is_active=True

        ).order_by(

            cls.execution_order.asc()

        )

    @classmethod
    def latest(cls, limit=20):

        return cls.query.order_by(

            cls.created_at.desc()

        ).limit(limit).all()

    # -------------------------------------------------------
    # BULK OPERATIONS
    # -------------------------------------------------------

    @classmethod
    def bulk_activate(cls, ids):

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

        cls.query.filter(

            cls.id.in_(ids)

        ).delete(

            synchronize_session=False

        )

        db.session.commit()

    # -------------------------------------------------------
    # DATABASE HELPERS
    # -------------------------------------------------------

    @classmethod
    def count(cls):

        return cls.query.count()

    @classmethod
    def exists(cls, testcase_id):

        return db.session.query(

            cls.query.filter_by(

                id=testcase_id

            ).exists()

        ).scalar()

    @classmethod
    def reorder_problem(cls, problem_id):
        """
        Reassign sequential execution_order values.
        """

        testcases = cls.query.filter_by(

            problem_id=problem_id

        ).order_by(

            cls.execution_order.asc(),

            cls.id.asc()

        ).all()

        for index, testcase in enumerate(testcases, start=1):

            testcase.execution_order = index

        db.session.commit()
        # -------------------------------------------------------
    # SERIALIZATION
    # -------------------------------------------------------

    def to_dict(self):
        """
        Convert testcase to dictionary.
        """

        return {

            "id": self.id,

            "problem_id": self.problem_id,

            "name": self.name,

            "description": self.description,

            "input_data": self.input_data,

            "expected_output": self.expected_output,

            "explanation": self.explanation,

            "time_limit": self.time_limit,

            "memory_limit": self.memory_limit,

            "marks": self.marks,

            "weight": self.weight,

            "execution_order": self.execution_order,

            "is_hidden": self.is_hidden,

            "is_sample": self.is_sample,

            "is_active": self.is_active,

            "tags": self.tags or [],

            "notes": self.notes,

            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            ),

            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at else None
            )

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

            "name": self.name,

            "problem_id": self.problem_id,

            "visibility": self.visibility,

            "marks": self.marks,

            "weight": self.weight,

            "execution_order": self.execution_order,

            "active": self.is_active

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

            "name": self.name,

            "problem": (
                self.problem.title
                if self.problem else None
            ),

            "visibility": self.visibility,

            "marks": self.marks,

            "weight": self.weight,

            "execution_order": self.execution_order,

            "status": self.status

        }

    # -------------------------------------------------------
    # JSON EXPORT
    # -------------------------------------------------------

    def export_json(self):
        """
        Export testcase as JSON-compatible dict.
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

            "name",

            "description",

            "input_data",

            "expected_output",

            "explanation",

            "time_limit",

            "memory_limit",

            "marks",

            "weight",

            "execution_order",

            "is_hidden",

            "is_sample",

            "is_active",

            "tags",

            "notes"

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

            "testcase": self.to_dict()

        }

    # -------------------------------------------------------
    # CLONE DATA
    # -------------------------------------------------------

    def clone_data(self):
        """
        Return dictionary for cloning.
        """

        return {

            "problem_id": self.problem_id,

            "name": f"{self.name} (Copy)",

            "description": self.description,

            "input_data": self.input_data,

            "expected_output": self.expected_output,

            "explanation": self.explanation,

            "time_limit": self.time_limit,

            "memory_limit": self.memory_limit,

            "marks": self.marks,

            "weight": self.weight,

            "execution_order": self.execution_order,

            "is_hidden": self.is_hidden,

            "is_sample": self.is_sample,

            "is_active": False,

            "tags": list(self.tags or []),

            "notes": self.notes

        }

    # -------------------------------------------------------
    # LOG ENTRY
    # -------------------------------------------------------

    def log_entry(self):
        """
        Compact log information.
        """

        return {

            "testcase_id": self.id,

            "problem_id": self.problem_id,

            "name": self.name,

            "execution_order": self.execution_order,

            "visibility": self.visibility,

            "active": self.is_active,

            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            )

        }
        # -------------------------------------------------------
    # STATISTICS
    # -------------------------------------------------------

    @property
    def input_characters(self):
        """
        Total input characters.
        """
        return len(self.input_data or "")

    @property
    def output_characters(self):
        """
        Total expected output characters.
        """
        return len(self.expected_output or "")

    @property
    def total_characters(self):
        """
        Combined input/output size.
        """
        return self.input_characters + self.output_characters

    @property
    def complexity_level(self):
        """
        Estimate testcase complexity.
        """

        size = self.total_characters

        if size < 100:
            return "Small"

        if size < 1000:
            return "Medium"

        if size < 10000:
            return "Large"

        return "Very Large"

    @property
    def visibility_type(self):
        """
        Human readable visibility.
        """

        if self.is_sample:
            return "Sample"

        if self.is_hidden:
            return "Hidden"

        return "Public"

    @property
    def weight_percentage(self):
        """
        Percentage weight (assuming total weight = 1.0).
        """

        return round(self.weight * 100, 2)

    # -------------------------------------------------------
    # PROBLEM STATISTICS
    # -------------------------------------------------------

    @classmethod
    def total_for_problem(cls, problem_id):

        return cls.query.filter_by(

            problem_id=problem_id,

            is_active=True

        ).count()

    @classmethod
    def sample_count(cls, problem_id):

        return cls.query.filter_by(

            problem_id=problem_id,

            is_sample=True,

            is_active=True

        ).count()

    @classmethod
    def hidden_count(cls, problem_id):

        return cls.query.filter_by(

            problem_id=problem_id,

            is_hidden=True,

            is_active=True

        ).count()

    @classmethod
    def public_count(cls, problem_id):

        return cls.query.filter_by(

            problem_id=problem_id,

            is_hidden=False,

            is_sample=False,

            is_active=True

        ).count()

    @classmethod
    def total_marks(cls, problem_id):

        value = db.session.query(

            db.func.sum(cls.marks)

        ).filter_by(

            problem_id=problem_id,

            is_active=True

        ).scalar()

        return round(value or 0, 2)

    @classmethod
    def average_time_limit(cls, problem_id):

        value = db.session.query(

            db.func.avg(cls.time_limit)

        ).filter_by(

            problem_id=problem_id,

            is_active=True

        ).scalar()

        return round(value or 0, 2)

    @classmethod
    def average_memory_limit(cls, problem_id):

        value = db.session.query(

            db.func.avg(cls.memory_limit)

        ).filter_by(

            problem_id=problem_id,

            is_active=True

        ).scalar()

        return round(value or 0, 2)

    # -------------------------------------------------------
    # DASHBOARD STATISTICS
    # -------------------------------------------------------

    @classmethod
    def dashboard_statistics(cls, problem_id):

        return {

            "total_testcases":
                cls.total_for_problem(problem_id),

            "sample_testcases":
                cls.sample_count(problem_id),

            "hidden_testcases":
                cls.hidden_count(problem_id),

            "public_testcases":
                cls.public_count(problem_id),

            "total_marks":
                cls.total_marks(problem_id),

            "average_time_limit":
                cls.average_time_limit(problem_id),

            "average_memory_limit":
                cls.average_memory_limit(problem_id)

        }

    # -------------------------------------------------------
    # ANALYTICS
    # -------------------------------------------------------

    def analytics(self):

        return {

            "testcase_id": self.id,

            "name": self.name,

            "complexity": self.complexity_level,

            "visibility": self.visibility_type,

            "marks": self.marks,

            "weight": self.weight,

            "weight_percentage":
                self.weight_percentage,

            "input_lines":
                self.input_lines,

            "output_lines":
                self.output_lines,

            "input_size_kb":
                self.input_size_kb,

            "output_size_kb":
                self.output_size_kb,

            "total_size_kb":
                self.total_size_kb

        }
        # -------------------------------------------------------
    # SEARCH METHODS
    # -------------------------------------------------------

    @classmethod
    def search(cls, keyword):
        """
        Search test cases by name, description, or tags.
        """

        if not keyword:
            return cls.query

        keyword = f"%{keyword}%"

        return cls.query.filter(

            db.or_(

                cls.name.ilike(keyword),

                cls.description.ilike(keyword),

                cls.notes.ilike(keyword)

            )

        )

    @classmethod
    def by_tag(cls, tag):
        """
        Find test cases by tag.
        """

        return cls.query.filter(

            cls.tags.contains([tag])

        )

    @classmethod
    def by_problem(cls, problem_id):
        """
        Active test cases of a problem.
        """

        return cls.query.filter_by(

            problem_id=problem_id,

            is_active=True

        )

    @classmethod
    def samples(cls):
        """
        All sample test cases.
        """

        return cls.query.filter_by(

            is_sample=True,

            is_active=True

        )

    @classmethod
    def hidden(cls):
        """
        All hidden test cases.
        """

        return cls.query.filter_by(

            is_hidden=True,

            is_active=True

        )

    @classmethod
    def active(cls):

        return cls.query.filter_by(

            is_active=True

        )

    @classmethod
    def inactive(cls):

        return cls.query.filter_by(

            is_active=False

        )

    # -------------------------------------------------------
    # SORTING
    # -------------------------------------------------------

    @classmethod
    def newest(cls):

        return cls.query.order_by(

            cls.created_at.desc()

        )

    @classmethod
    def oldest(cls):

        return cls.query.order_by(

            cls.created_at.asc()

        )

    @classmethod
    def by_order(cls):

        return cls.query.order_by(

            cls.execution_order.asc()

        )

    @classmethod
    def by_marks(cls):

        return cls.query.order_by(

            cls.marks.desc()

        )

    @classmethod
    def by_weight(cls):

        return cls.query.order_by(

            cls.weight.desc()

        )

    @classmethod
    def by_name(cls):

        return cls.query.order_by(

            cls.name.asc()

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
    # ADVANCED SEARCH
    # -------------------------------------------------------

    @classmethod
    def advanced_search(

        cls,

        keyword=None,

        problem_id=None,

        hidden=None,

        sample=None,

        active=True

    ):

        query = cls.query

        if active is not None:

            query = query.filter_by(

                is_active=active

            )

        if problem_id:

            query = query.filter_by(

                problem_id=problem_id

            )

        if hidden is not None:

            query = query.filter_by(

                is_hidden=hidden

            )

        if sample is not None:

            query = query.filter_by(

                is_sample=sample

            )

        if keyword:

            keyword = f"%{keyword}%"

            query = query.filter(

                db.or_(

                    cls.name.ilike(keyword),

                    cls.description.ilike(keyword),

                    cls.notes.ilike(keyword)

                )

            )

        return query

    # -------------------------------------------------------
    # RANDOM TEST CASE
    # -------------------------------------------------------

    @classmethod
    def random_testcase(cls):

        return cls.query.filter_by(

            is_active=True

        ).order_by(

            db.func.random()

        ).first()

    # -------------------------------------------------------
    # DUPLICATE DETECTION
    # -------------------------------------------------------

    @classmethod
    def duplicates(cls, problem_id):

        seen = {}

        duplicates = []

        testcases = cls.query.filter_by(

            problem_id=problem_id

        ).all()

        for testcase in testcases:

            key = (

                testcase.input_data,

                testcase.expected_output

            )

            if key in seen:

                duplicates.append(testcase)

            else:

                seen[key] = testcase.id

        return duplicates

    # -------------------------------------------------------
    # RECENTLY UPDATED
    # -------------------------------------------------------

    @classmethod
    def recently_updated(cls, limit=10):

        return cls.query.order_by(

            cls.updated_at.desc()

        ).limit(limit).all()
        # -------------------------------------------------------
    # EXECUTION HELPERS
    # -------------------------------------------------------

    @property
    def execution_config(self):
        """
        Execution configuration.
        """

        return {

            "time_limit": self.time_limit,

            "memory_limit": self.memory_limit,

            "input": self.input_data,

            "expected_output": self.expected_output

        }

    @property
    def display_name(self):

        return f"#{self.execution_order} - {self.name}"

    @property
    def is_ready(self):

        return (

            self.is_active and

            bool(self.input_data) and

            bool(self.expected_output)

        )

    # -------------------------------------------------------
    # QUALITY SCORE
    # -------------------------------------------------------

    @property
    def quality_score(self):
        """
        Estimate testcase quality.
        """

        score = 100

        if self.is_hidden:
            score += 10

        if self.has_explanation:
            score += 5

        if self.tag_count > 0:
            score += 5

        if self.total_size_kb > 200:
            score -= 10

        return min(score, 100)

    @property
    def quality_grade(self):

        score = self.quality_score

        if score >= 95:
            return "Excellent"

        if score >= 85:
            return "Very Good"

        if score >= 70:
            return "Good"

        if score >= 50:
            return "Average"

        return "Poor"

    # -------------------------------------------------------
    # VALIDATION SUMMARY
    # -------------------------------------------------------

    def validation_summary(self):

        errors = []

        if not self.name:
            errors.append("Missing name.")

        if not self.input_data:
            errors.append("Missing input.")

        if not self.expected_output:
            errors.append("Missing expected output.")

        if self.time_limit <= 0:
            errors.append("Invalid time limit.")

        if self.memory_limit < 16:
            errors.append("Invalid memory limit.")

        return {

            "valid": len(errors) == 0,

            "errors": errors

        }

    # -------------------------------------------------------
    # EXECUTION RESULT TEMPLATE
    # -------------------------------------------------------

    def empty_result(self):

        return {

            "passed": False,

            "execution_time": 0,

            "memory_used": 0,

            "stdout": "",

            "stderr": "",

            "actual_output": "",

            "expected_output": self.expected_output

        }

    # -------------------------------------------------------
    # COPY HELPERS
    # -------------------------------------------------------

    def copy_input(self):

        return str(self.input_data)

    def copy_output(self):

        return str(self.expected_output)

    # -------------------------------------------------------
    # TAG UTILITIES
    # -------------------------------------------------------

    def replace_tags(self, tags):

        self.tags = list(

            dict.fromkeys(

                [

                    str(tag).strip()

                    for tag in tags

                    if str(tag).strip()

                ]

            )

        )

    def tag_string(self):

        return ", ".join(

            self.tags or []

        )

    # -------------------------------------------------------
    # DASHBOARD HELPERS
    # -------------------------------------------------------

    def dashboard_badge(self):

        if self.is_sample:

            return {

                "text": "Sample",

                "color": "success"

            }

        if self.is_hidden:

            return {

                "text": "Hidden",

                "color": "warning"

            }

        return {

            "text": "Public",

            "color": "primary"

        }

    def dashboard_row(self):

        return {

            "id": self.id,

            "name": self.display_name,

            "visibility": self.visibility,

            "marks": self.marks,

            "quality": self.quality_grade,

            "active": self.is_active

        }

    # -------------------------------------------------------
    # UTILITIES
    # -------------------------------------------------------

    def clear_notes(self):

        self.notes = None

    def clear_explanation(self):

        self.explanation = None

    def clear_description(self):

        self.description = None

    def reset_metadata(self):

        self.tags = []

        self.notes = None

    def duplicate(self):

        """
        Create a copy of this testcase.
        """

        return TestCase(

            problem_id=self.problem_id,

            name=f"{self.name} (Copy)",

            description=self.description,

            input_data=self.input_data,

            expected_output=self.expected_output,

            explanation=self.explanation,

            time_limit=self.time_limit,

            memory_limit=self.memory_limit,

            marks=self.marks,

            weight=self.weight,

            execution_order=self.execution_order,

            is_hidden=self.is_hidden,

            is_sample=self.is_sample,

            is_active=False,

            tags=list(self.tags or []),

            notes=self.notes

        )
        # -------------------------------------------------------
    # CLONE
    # -------------------------------------------------------

    def clone(self):
        """
        Create a clone of this test case.
        """

        return TestCase(

            problem_id=self.problem_id,

            name=f"{self.name} (Copy)",

            description=self.description,

            input_data=self.input_data,

            expected_output=self.expected_output,

            explanation=self.explanation,

            time_limit=self.time_limit,

            memory_limit=self.memory_limit,

            marks=self.marks,

            weight=self.weight,

            execution_order=self.execution_order,

            is_hidden=self.is_hidden,

            is_sample=self.is_sample,

            is_active=False,

            tags=list(self.tags or []),

            notes=self.notes

        )

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
    # HASHING
    # -------------------------------------------------------

    @property
    def content_hash(self):
        """
        SHA256 hash of testcase content.
        """

        import hashlib

        content = (

            (self.input_data or "") +

            (self.expected_output or "") +

            (self.name or "")

        )

        return hashlib.sha256(

            content.encode("utf-8")

        ).hexdigest()

    # -------------------------------------------------------
    # AUDIT
    # -------------------------------------------------------

    def audit_log(self):

        return {

            "testcase_id": self.id,

            "problem_id": self.problem_id,

            "name": self.name,

            "version": self.version,

            "execution_order": self.execution_order,

            "hidden": self.is_hidden,

            "sample": self.is_sample,

            "active": self.is_active,

            "created_at": self.created_at,

            "updated_at": self.updated_at

        }

    # -------------------------------------------------------
    # INTEGRITY
    # -------------------------------------------------------

    @property
    def integrity_ok(self):

        return (

            bool(self.input_data)

            and

            bool(self.expected_output)

            and

            self.time_limit > 0

            and

            self.memory_limit >= 16

        )

    def integrity_report(self):

        report = {

            "valid": True,

            "issues": []

        }

        if not self.input_data:

            report["issues"].append(

                "Missing input."

            )

        if not self.expected_output:

            report["issues"].append(

                "Missing expected output."

            )

        if self.time_limit <= 0:

            report["issues"].append(

                "Invalid time limit."

            )

        if self.memory_limit < 16:

            report["issues"].append(

                "Invalid memory limit."

            )

        report["valid"] = (

            len(report["issues"]) == 0

        )

        return report

    # -------------------------------------------------------
    # DUPLICATE DETECTION
    # -------------------------------------------------------

    @classmethod
    def find_duplicate(cls, problem_id, input_data, expected_output):

        return cls.query.filter_by(

            problem_id=problem_id,

            input_data=input_data,

            expected_output=expected_output

        ).first()

    @classmethod
    def duplicate_count(cls, problem_id):

        seen = set()

        duplicates = 0

        testcases = cls.query.filter_by(

            problem_id=problem_id

        ).all()

        for testcase in testcases:

            key = (

                testcase.input_data,

                testcase.expected_output

            )

            if key in seen:

                duplicates += 1

            else:

                seen.add(key)

        return duplicates

    # -------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------

    def validate(self):

        if not self.name:

            raise ValueError(

                "Test case name is required."

            )

        if not self.input_data:

            raise ValueError(

                "Input data is required."

            )

        if not self.expected_output:

            raise ValueError(

                "Expected output is required."

            )

        return True

    # -------------------------------------------------------
    # SAVE SAFE
    # -------------------------------------------------------

    def save_safe(self):

        self.validate()

        db.session.add(self)

        db.session.commit()

        return self

    # -------------------------------------------------------
    # EXPORT
    # -------------------------------------------------------

    def export(self):

        return {

            "metadata": {

                "id": self.id,

                "problem_id": self.problem_id,

                "version": self.version

            },

            "testcase": self.to_dict(),

            "analytics": self.analytics()

        }

    # -------------------------------------------------------
    # EQUALITY
    # -------------------------------------------------------

    def __eq__(self, other):

        return (

            isinstance(other, TestCase)

            and

            self.id == other.id

        )

    def __hash__(self):

        return hash(self.id)

    def __str__(self):

        return self.name
        # -------------------------------------------------------
    # PRE-SAVE HELPERS
    # -------------------------------------------------------

    def before_insert(self):
        """
        Prepare object before insert.
        """

        if self.execution_order is None:
            self.execution_order = 1

        if self.tags is None:
            self.tags = []

        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def before_update(self):
        """
        Prepare object before update.
        """

        self.updated_at = datetime.utcnow()

        if self.version is None:
            self.version = 1
        else:
            self.version += 1

    # -------------------------------------------------------
    # FINAL VALIDATION
    # -------------------------------------------------------

    def validate_complete(self):
        """
        Complete validation before saving.
        """

        self.validate()

        if self.weight <= 0:
            raise ValueError(
                "Weight must be greater than zero."
            )

        if self.marks < 0:
            raise ValueError(
                "Marks cannot be negative."
            )

        return True

    # -------------------------------------------------------
    # PRODUCTION EXPORT
    # -------------------------------------------------------

    def production_export(self):
        """
        Export complete testcase.
        """

        return {

            "metadata": {

                "id": self.id,

                "problem_id": self.problem_id,

                "version": self.version,

                "created_at": (
                    self.created_at.isoformat()
                    if self.created_at else None
                ),

                "updated_at": (
                    self.updated_at.isoformat()
                    if self.updated_at else None
                )

            },

            "testcase": self.to_dict(),

            "analytics": self.analytics(),

            "integrity": self.integrity_report()

        }

    # -------------------------------------------------------
    # DEBUG
    # -------------------------------------------------------

    def debug(self):

        return {

            "id": self.id,

            "problem_id": self.problem_id,

            "name": self.name,

            "execution_order": self.execution_order,

            "visibility": self.visibility,

            "status": self.status,

            "version": self.version

        }
# ==========================================================
# SQLALCHEMY EVENTS
# ==========================================================

from sqlalchemy import event


@event.listens_for(TestCase, "before_insert")
def testcase_before_insert(mapper, connection, target):

    target.before_insert()


@event.listens_for(TestCase, "before_update")
def testcase_before_update(mapper, connection, target):

    target.before_update()


# ==========================================================
# MODULE EXPORT
# ==========================================================

__all__ = [

    "TestCase"

]