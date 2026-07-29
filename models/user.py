"""
==========================================================
Lab Auto Grader
User Model
Part 1
==========================================================
"""

from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Text
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from extensions import db


class User(UserMixin, db.Model):
    """
    Base User Model
    """

    __tablename__ = "users"

    # -------------------------------------------------------
    # PRIMARY KEY
    # -------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -------------------------------------------------------
    # PERSONAL INFORMATION
    # -------------------------------------------------------

    first_name = db.Column(
        db.String(100),
        nullable=False
    )

    last_name = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
        index=True
    )

    mobile = db.Column(
        db.String(20),
        unique=True,
        nullable=True
    )

    # -------------------------------------------------------
    # AUTHENTICATION
    # -------------------------------------------------------

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # -------------------------------------------------------
    # ROLE
    # -------------------------------------------------------

    role = db.Column(
        db.String(20),
        nullable=False,
        default="Student",
        index=True
    )

    # -------------------------------------------------------
    # PROFILE
    # -------------------------------------------------------

    profile_image = db.Column(
        db.String(255),
        nullable=True
    )

    bio = db.Column(
        Text,
        nullable=True
    )

    # -------------------------------------------------------
    # ACCOUNT STATUS
    # -------------------------------------------------------

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    is_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    is_locked = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    # -------------------------------------------------------
    # LOGIN INFORMATION
    # -------------------------------------------------------

    last_login = db.Column(
        db.DateTime,
        nullable=True
    )

    login_count = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    failed_login_attempts = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    # -------------------------------------------------------
    # PASSWORD RESET
    # -------------------------------------------------------

    reset_token = db.Column(
        db.String(255),
        nullable=True
    )

    reset_token_expiry = db.Column(
        db.DateTime,
        nullable=True
    )

    # -------------------------------------------------------
    # AUDIT FIELDS
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
    # REPRESENTATION
    # -------------------------------------------------------

    def __repr__(self):

        return (

            f"<User "

            f"id={self.id} "

            f"username='{self.username}' "

            f"role='{self.role}'>"

        )
        # -------------------------------------------------------
    # ROLE CONSTANTS
    # -------------------------------------------------------

    ROLE_ADMIN = "Admin"
    ROLE_TEACHER = "Teacher"
    ROLE_STUDENT = "Student"

    VALID_ROLES = (

        ROLE_ADMIN,

        ROLE_TEACHER,

        ROLE_STUDENT

    )

    # -------------------------------------------------------
    # RELATIONSHIPS
    # -------------------------------------------------------

    student = db.relationship(

        "Student",

        back_populates="user",

        uselist=False,

        cascade="all, delete-orphan",

        lazy="joined"

    )

    teacher = db.relationship(

        "Teacher",

        back_populates="user",

        uselist=False,

        cascade="all, delete-orphan",

        lazy="joined"

    )

    submissions = db.relationship(

        "Submission",

        back_populates="user",

        lazy="dynamic",

        cascade="all, delete-orphan"

    )

    assignments_created = db.relationship(

        "Assignment",

        back_populates="creator",

        lazy="dynamic"

    )

    problems_created = db.relationship(

        "Problem",

        back_populates="creator",

        lazy="dynamic"

    )

    # -------------------------------------------------------
    # PROFILE PROPERTIES
    # -------------------------------------------------------

    @property
    def full_name(self):

        return (

            f"{self.first_name} "

            f"{self.last_name}"

        ).strip()

    @property
    def initials(self):

        first = self.first_name[0] if self.first_name else ""

        last = self.last_name[0] if self.last_name else ""

        return (

            first +

            last

        ).upper()

    @property
    def display_name(self):

        if self.full_name.strip():

            return self.full_name

        return self.username

    # -------------------------------------------------------
    # ROLE HELPERS
    # -------------------------------------------------------

    @property
    def is_admin(self):

        return self.role == self.ROLE_ADMIN

    @property
    def is_teacher(self):

        return self.role == self.ROLE_TEACHER

    @property
    def is_student(self):

        return self.role == self.ROLE_STUDENT

    # -------------------------------------------------------
    # ACCOUNT STATUS
    # -------------------------------------------------------

    @property
    def can_login(self):

        return (

            self.is_active

            and

            not self.is_locked

        )

    @property
    def account_status(self):

        if self.is_locked:

            return "Locked"

        if not self.is_active:

            return "Inactive"

        if not self.is_verified:

            return "Unverified"

        return "Active"

    @property
    def status_badge(self):

        badges = {

            "Active": "success",

            "Inactive": "secondary",

            "Locked": "danger",

            "Unverified": "warning"

        }

        return badges.get(

            self.account_status,

            "secondary"

        )

    # -------------------------------------------------------
    # ROLE MANAGEMENT
    # -------------------------------------------------------

    def make_admin(self):

        self.role = self.ROLE_ADMIN

    def make_teacher(self):

        self.role = self.ROLE_TEACHER

    def make_student(self):

        self.role = self.ROLE_STUDENT

    # -------------------------------------------------------
    # ACCOUNT MANAGEMENT
    # -------------------------------------------------------

    def verify(self):

        self.is_verified = True

    def unverify(self):

        self.is_verified = False

    def activate(self):

        self.is_active = True

    def deactivate(self):

        self.is_active = False

    def lock(self):

        self.is_locked = True

    def unlock(self):

        self.is_locked = False

        self.failed_login_attempts = 0

    # -------------------------------------------------------
    # LOGIN TRACKING
    # -------------------------------------------------------

    def update_login(self):

        self.last_login = datetime.utcnow()

        self.login_count += 1

        self.failed_login_attempts = 0

    def register_failed_login(self):

        self.failed_login_attempts += 1

        if self.failed_login_attempts >= 5:

            self.is_locked = True
        # -------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------

    @validates("first_name")
    def validate_first_name(self, key, value):

        value = value.strip()

        if len(value) < 2:
            raise ValueError(
                "First name must contain at least 2 characters."
            )

        if len(value) > 100:
            raise ValueError(
                "First name cannot exceed 100 characters."
            )

        return value

    @validates("last_name")
    def validate_last_name(self, key, value):

        value = value.strip()

        if len(value) < 1:
            raise ValueError(
                "Last name cannot be empty."
            )

        if len(value) > 100:
            raise ValueError(
                "Last name cannot exceed 100 characters."
            )

        return value

    @validates("username")
    def validate_username(self, key, value):

        import re

        value = value.strip().lower()

        if len(value) < 3:
            raise ValueError(
                "Username must contain at least 3 characters."
            )

        if len(value) > 30:
            raise ValueError(
                "Username cannot exceed 30 characters."
            )

        if not re.match(
            r"^[a-zA-Z0-9_.]+$",
            value
        ):
            raise ValueError(
                "Username contains invalid characters."
            )

        return value

    @validates("email")
    def validate_email(self, key, value):

        import re

        value = value.strip().lower()

        pattern = (
            r"^[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+"
            r"\.[A-Za-z]{2,}$"
        )

        if not re.match(pattern, value):
            raise ValueError(
                "Invalid email address."
            )

        return value

    @validates("mobile")
    def validate_mobile(self, key, value):

        if not value:
            return None

        import re

        value = value.strip()

        if not re.fullmatch(
            r"[0-9]{10,15}",
            value
        ):
            raise ValueError(
                "Invalid mobile number."
            )

        return value

    @validates("role")
    def validate_role(self, key, value):

        if value not in self.VALID_ROLES:

            raise ValueError(
                f"Role must be one of {self.VALID_ROLES}"
            )

        return value

    @validates("profile_image")
    def validate_profile_image(self, key, value):

        if not value:
            return None

        allowed = (

            ".jpg",

            ".jpeg",

            ".png",

            ".gif",

            ".webp"

        )

        if not value.lower().endswith(allowed):

            raise ValueError(
                "Unsupported profile image format."
            )

        return value

    @validates("bio")
    def validate_bio(self, key, value):

        if value is None:
            return None

        value = value.strip()

        if len(value) > 1000:

            raise ValueError(
                "Bio cannot exceed 1000 characters."
            )

        return value

    # -------------------------------------------------------
    # PASSWORD HELPERS
    # -------------------------------------------------------

    def set_password(self, password):
        """
        Hash and store password.
        """

        self.validate_password_strength(password)

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):
        """
        Verify password.
        """

        return check_password_hash(
            self.password_hash,
            password
        )

    @staticmethod
    def validate_password_strength(password):
        """
        Validate password strength.
        """

        import re

        if len(password) < 8:

            raise ValueError(
                "Password must contain at least 8 characters."
            )

        if not re.search(r"[A-Z]", password):

            raise ValueError(
                "Password must contain an uppercase letter."
            )

        if not re.search(r"[a-z]", password):

            raise ValueError(
                "Password must contain a lowercase letter."
            )

        if not re.search(r"\d", password):

            raise ValueError(
                "Password must contain a digit."
            )

        if not re.search(
            r"[!@#$%^&*(),.?\":{}|<>]",
            password
        ):

            raise ValueError(
                "Password must contain a special character."
            )

        return True

    @property
    def password_set(self):

        return bool(self.password_hash)

    @property
    def profile_completed(self):

        return all(

            [

                self.first_name,

                self.last_name,

                self.email,

                self.username

            ]

        )
        # -------------------------------------------------------
    # AUTHENTICATION HELPERS
    # -------------------------------------------------------

    def authenticate(self, password):
        """
        Authenticate user.
        """

        if not self.can_login:
            return False

        if self.check_password(password):

            self.update_login()

            return True

        self.register_failed_login()

        return False

    # -------------------------------------------------------
    # PASSWORD RESET
    # -------------------------------------------------------

    def generate_reset_token(self, expiry_minutes=30):
        """
        Generate password reset token.
        """

        import secrets
        from datetime import timedelta

        self.reset_token = secrets.token_urlsafe(32)

        self.reset_token_expiry = (

            datetime.utcnow()

            + timedelta(minutes=expiry_minutes)

        )

        return self.reset_token

    def verify_reset_token(self, token):
        """
        Verify reset token.
        """

        if not self.reset_token:

            return False

        if self.reset_token != token:

            return False

        if self.reset_token_expiry is None:

            return False

        return datetime.utcnow() <= self.reset_token_expiry

    def clear_reset_token(self):
        """
        Remove reset token.
        """

        self.reset_token = None

        self.reset_token_expiry = None

    def reset_password(self, token, new_password):
        """
        Reset password using token.
        """

        if not self.verify_reset_token(token):

            return False

        self.set_password(new_password)

        self.clear_reset_token()

        self.failed_login_attempts = 0

        self.is_locked = False

        return True

    # -------------------------------------------------------
    # LOGIN HELPERS
    # -------------------------------------------------------

    def login_success(self):
        """
        Called after successful login.
        """

        self.update_login()

        self.failed_login_attempts = 0

        self.is_locked = False

    def login_failed(self):
        """
        Called after failed login.
        """

        self.register_failed_login()

    # -------------------------------------------------------
    # SESSION HELPERS
    # -------------------------------------------------------

    @property
    def is_authenticated_user(self):

        return (

            self.is_active

            and

            not self.is_locked

        )

    @property
    def is_online(self):
        """
        Consider online if logged in within 15 minutes.
        """

        if self.last_login is None:

            return False

        from datetime import timedelta

        return (

            datetime.utcnow()

            - self.last_login

        ) <= timedelta(minutes=15)

    @property
    def account_age_days(self):

        return (

            datetime.utcnow()

            - self.created_at

        ).days

    # -------------------------------------------------------
    # PROFILE HELPERS
    # -------------------------------------------------------

    @property
    def profile_completion_percentage(self):

        completed = 0

        total = 7

        if self.first_name:
            completed += 1

        if self.last_name:
            completed += 1

        if self.username:
            completed += 1

        if self.email:
            completed += 1

        if self.mobile:
            completed += 1

        if self.profile_image:
            completed += 1

        if self.bio:
            completed += 1

        return round(

            completed * 100 / total,

            2

        )

    # -------------------------------------------------------
    # ACTIVITY
    # -------------------------------------------------------

    def touch(self):
        """
        Update modification timestamp.
        """

        self.updated_at = datetime.utcnow()

    def record_activity(self):
        """
        Record latest activity.
        """

        self.touch()

    # -------------------------------------------------------
    # DISPLAY
    # -------------------------------------------------------

    @property
    def avatar(self):

        if self.profile_image:

            return self.profile_image

        return "/static/images/default-avatar.png"

    @property
    def greeting(self):

        return f"Welcome, {self.display_name}!"

    @property
    def short_info(self):

        return (

            f"{self.display_name} "

            f"({self.role})"

        )
        # -------------------------------------------------------
    # CRUD OPERATIONS
    # -------------------------------------------------------

    def save(self, commit=True):
        """
        Save user to database.
        """

        db.session.add(self)

        if commit:
            db.session.commit()

        return self

    def update(self, commit=True, **kwargs):
        """
        Update user fields.
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
        Permanently delete user.
        """

        db.session.delete(self)

        if commit:

            db.session.commit()

    # -------------------------------------------------------
    # SOFT DELETE
    # -------------------------------------------------------

    def deactivate_account(self, commit=True):
        """
        Soft delete user.
        """

        self.is_active = False

        self.updated_at = datetime.utcnow()

        if commit:

            db.session.commit()

        return self

    def restore_account(self, commit=True):
        """
        Restore inactive account.
        """

        self.is_active = True

        self.updated_at = datetime.utcnow()

        if commit:

            db.session.commit()

        return self

    # -------------------------------------------------------
    # QUERY HELPERS
    # -------------------------------------------------------

    @classmethod
    def get_by_id(cls, user_id):

        return cls.query.get(user_id)

    @classmethod
    def get_by_username(cls, username):

        return cls.query.filter_by(

            username=username

        ).first()

    @classmethod
    def get_by_email(cls, email):

        return cls.query.filter_by(

            email=email

        ).first()

    @classmethod
    def get_by_mobile(cls, mobile):

        return cls.query.filter_by(

            mobile=mobile

        ).first()

    @classmethod
    def active_users(cls):

        return cls.query.filter_by(

            is_active=True

        )

    @classmethod
    def verified_users(cls):

        return cls.query.filter_by(

            is_verified=True

        )

    @classmethod
    def locked_users(cls):

        return cls.query.filter_by(

            is_locked=True

        )

    @classmethod
    def admins(cls):

        return cls.query.filter_by(

            role=cls.ROLE_ADMIN

        )

    @classmethod
    def teachers(cls):

        return cls.query.filter_by(

            role=cls.ROLE_TEACHER

        )

    @classmethod
    def students(cls):

        return cls.query.filter_by(

            role=cls.ROLE_STUDENT

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
    def exists(cls, username):

        return db.session.query(

            cls.query.filter_by(

                username=username

            ).exists()

        ).scalar()

    @classmethod
    def email_exists(cls, email):

        return db.session.query(

            cls.query.filter_by(

                email=email

            ).exists()

        ).scalar()

    @classmethod
    def mobile_exists(cls, mobile):

        return db.session.query(

            cls.query.filter_by(

                mobile=mobile

            ).exists()

        ).scalar()
        # -------------------------------------------------------
    # SERIALIZATION
    # -------------------------------------------------------

    def to_dict(self):
        """
        Convert user to dictionary.
        """

        return {

            "id": self.id,

            "first_name": self.first_name,

            "last_name": self.last_name,

            "full_name": self.full_name,

            "username": self.username,

            "email": self.email,

            "mobile": self.mobile,

            "role": self.role,

            "profile_image": self.profile_image,

            "bio": self.bio,

            "is_active": self.is_active,

            "is_verified": self.is_verified,

            "is_locked": self.is_locked,

            "account_status": self.account_status,

            "login_count": self.login_count,

            "failed_login_attempts":
                self.failed_login_attempts,

            "last_login":
                self.last_login.isoformat()
                if self.last_login else None,

            "created_at":
                self.created_at.isoformat()
                if self.created_at else None,

            "updated_at":
                self.updated_at.isoformat()
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

            "name": self.full_name,

            "username": self.username,

            "role": self.role,

            "status": self.account_status,

            "verified": self.is_verified

        }

    # -------------------------------------------------------
    # PROFILE
    # -------------------------------------------------------

    def profile(self):
        """
        Public profile serializer.
        """

        return {

            "id": self.id,

            "name": self.full_name,

            "username": self.username,

            "email": self.email,

            "mobile": self.mobile,

            "role": self.role,

            "avatar": self.avatar,

            "bio": self.bio,

            "profile_completion":
                self.profile_completion_percentage

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

            "name": self.full_name,

            "role": self.role,

            "status": self.account_status,

            "status_badge": self.status_badge,

            "avatar": self.avatar,

            "last_login":
                self.last_login.isoformat()
                if self.last_login else None,

            "login_count": self.login_count

        }

    # -------------------------------------------------------
    # EXPORT
    # -------------------------------------------------------

    def export_json(self):
        """
        Export as JSON-compatible dictionary.
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

            "first_name",

            "last_name",

            "username",

            "email",

            "mobile",

            "role",

            "profile_image",

            "bio",

            "is_active",

            "is_verified",

            "is_locked"

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

            "user": self.to_dict()

        }

    # -------------------------------------------------------
    # LOG ENTRY
    # -------------------------------------------------------

    def log_entry(self):
        """
        Compact log information.
        """

        return {

            "user_id": self.id,

            "username": self.username,

            "role": self.role,

            "status": self.account_status,

            "last_login":
                self.last_login.isoformat()
                if self.last_login else None

        }

    # -------------------------------------------------------
    # SAFE PUBLIC PROFILE
    # -------------------------------------------------------

    def public_profile(self):
        """
        Public information only.
        """

        return {

            "id": self.id,

            "username": self.username,

            "name": self.full_name,

            "role": self.role,

            "avatar": self.avatar

        }
        # -------------------------------------------------------
    # SEARCH & FILTER METHODS
    # -------------------------------------------------------

    @classmethod
    def search(cls, keyword):
        """
        Search users by name, username or email.
        """

        if not keyword:
            return cls.query

        keyword = f"%{keyword}%"

        return cls.query.filter(

            db.or_(

                cls.first_name.ilike(keyword),

                cls.last_name.ilike(keyword),

                cls.username.ilike(keyword),

                cls.email.ilike(keyword)

            )

        )

    @classmethod
    def by_role(cls, role):

        return cls.query.filter_by(

            role=role

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

    @classmethod
    def verified(cls):

        return cls.query.filter_by(

            is_verified=True

        )

    @classmethod
    def unverified(cls):

        return cls.query.filter_by(

            is_verified=False

        )

    @classmethod
    def locked(cls):

        return cls.query.filter_by(

            is_locked=True

        )

    @classmethod
    def unlocked(cls):

        return cls.query.filter_by(

            is_locked=False

        )

    # -------------------------------------------------------
    # RECENT USERS
    # -------------------------------------------------------

    @classmethod
    def recently_registered(cls, limit=10):

        return cls.query.order_by(

            cls.created_at.desc()

        ).limit(limit).all()

    @classmethod
    def recently_active(cls, limit=10):

        return cls.query.filter(

            cls.last_login.isnot(None)

        ).order_by(

            cls.last_login.desc()

        ).limit(limit).all()

    # -------------------------------------------------------
    # SORTING
    # -------------------------------------------------------

    @classmethod
    def sort_by_name(cls):

        return cls.query.order_by(

            cls.first_name.asc(),

            cls.last_name.asc()

        )

    @classmethod
    def sort_by_username(cls):

        return cls.query.order_by(

            cls.username.asc()

        )

    @classmethod
    def sort_by_login_count(cls):

        return cls.query.order_by(

            cls.login_count.desc()

        )

    @classmethod
    def sort_by_last_login(cls):

        return cls.query.order_by(

            cls.last_login.desc()

        )

    @classmethod
    def sort_by_created_date(cls):

        return cls.query.order_by(

            cls.created_at.desc()

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

        role=None,

        active=None,

        verified=None,

        locked=None

    ):

        query = cls.query

        if keyword:

            keyword = f"%{keyword}%"

            query = query.filter(

                db.or_(

                    cls.first_name.ilike(keyword),

                    cls.last_name.ilike(keyword),

                    cls.username.ilike(keyword),

                    cls.email.ilike(keyword)

                )

            )

        if role:

            query = query.filter_by(

                role=role

            )

        if active is not None:

            query = query.filter_by(

                is_active=active

            )

        if verified is not None:

            query = query.filter_by(

                is_verified=verified

            )

        if locked is not None:

            query = query.filter_by(

                is_locked=locked

            )

        return query

    # -------------------------------------------------------
    # ONLINE USERS
    # -------------------------------------------------------

    @classmethod
    def online_users(cls):

        from datetime import timedelta

        threshold = datetime.utcnow() - timedelta(minutes=15)

        return cls.query.filter(

            cls.last_login >= threshold,

            cls.is_active == True

        )

    # -------------------------------------------------------
    # ROLE COUNTS
    # -------------------------------------------------------

    @classmethod
    def role_statistics(cls):

        return {

            "admins": cls.admins().count(),

            "teachers": cls.teachers().count(),

            "students": cls.students().count(),

            "active": cls.active().count(),

            "inactive": cls.inactive().count(),

            "verified": cls.verified().count(),

            "locked": cls.locked().count(),

            "total": cls.count()

        }
        # -------------------------------------------------------
    # LOGIN ANALYTICS
    # -------------------------------------------------------

    @property
    def login_success_rate(self):
        """
        Successful login percentage.
        """

        total = self.login_count + self.failed_login_attempts

        if total == 0:
            return 100.0

        return round(
            (self.login_count / total) * 100,
            2
        )

    @property
    def login_failure_rate(self):

        return round(
            100 - self.login_success_rate,
            2
        )

    @property
    def total_login_attempts(self):

        return self.login_count + self.failed_login_attempts

    # -------------------------------------------------------
    # PROFILE ANALYTICS
    # -------------------------------------------------------

    @property
    def profile_score(self):

        return self.profile_completion_percentage

    @property
    def profile_grade(self):

        score = self.profile_score

        if score >= 95:
            return "Excellent"

        if score >= 80:
            return "Very Good"

        if score >= 60:
            return "Good"

        if score >= 40:
            return "Average"

        return "Poor"

    # -------------------------------------------------------
    # SECURITY
    # -------------------------------------------------------

    @property
    def security_score(self):

        score = 100

        if not self.is_verified:
            score -= 20

        if self.failed_login_attempts > 0:
            score -= min(
                self.failed_login_attempts * 5,
                30
            )

        if self.is_locked:
            score -= 20

        if not self.password_set:
            score -= 30

        return max(score, 0)

    @property
    def security_level(self):

        score = self.security_score

        if score >= 90:
            return "Excellent"

        if score >= 75:
            return "High"

        if score >= 60:
            return "Medium"

        if score >= 40:
            return "Low"

        return "Critical"

    # -------------------------------------------------------
    # ACTIVITY
    # -------------------------------------------------------

    @property
    def days_since_last_login(self):

        if self.last_login is None:

            return None

        return (

            datetime.utcnow()

            - self.last_login

        ).days

    @property
    def is_new_user(self):

        return self.account_age_days <= 7

    @property
    def is_inactive_user(self):

        if self.last_login is None:

            return True

        return self.days_since_last_login > 30

    # -------------------------------------------------------
    # USER STATISTICS
    # -------------------------------------------------------

    def statistics(self):

        return {

            "user_id": self.id,

            "role": self.role,

            "status": self.account_status,

            "login_count": self.login_count,

            "failed_logins":
                self.failed_login_attempts,

            "success_rate":
                self.login_success_rate,

            "profile_completion":
                self.profile_completion_percentage,

            "profile_grade":
                self.profile_grade,

            "security_score":
                self.security_score,

            "security_level":
                self.security_level,

            "account_age_days":
                self.account_age_days

        }

    # -------------------------------------------------------
    # DASHBOARD ANALYTICS
    # -------------------------------------------------------

    def dashboard_statistics(self):

        return {

            "name": self.display_name,

            "role": self.role,

            "status": self.account_status,

            "profile_completion":
                self.profile_completion_percentage,

            "login_count":
                self.login_count,

            "last_login":
                self.last_login.isoformat()
                if self.last_login else None,

            "security":
                self.security_level

        }

    # -------------------------------------------------------
    # USER BADGES
    # -------------------------------------------------------

    @property
    def role_badge(self):

        badges = {

            self.ROLE_ADMIN: "danger",

            self.ROLE_TEACHER: "primary",

            self.ROLE_STUDENT: "success"

        }

        return badges.get(
            self.role,
            "secondary"
        )

    @property
    def verification_badge(self):

        return (

            "success"

            if self.is_verified

            else "warning"

        )

    # -------------------------------------------------------
    # DISPLAY HELPERS
    # -------------------------------------------------------

    def greeting_message(self):

        if self.is_admin:

            return f"Welcome Admin {self.first_name}"

        if self.is_teacher:

            return f"Welcome Professor {self.last_name}"

        return f"Welcome {self.first_name}"

    def dashboard_info(self):

        return {

            "avatar": self.avatar,

            "display_name": self.display_name,

            "role": self.role,

            "role_badge": self.role_badge,

            "status_badge": self.status_badge

        }
        # -------------------------------------------------------
    # CLONE
    # -------------------------------------------------------

    def clone(self):
        """
        Create a copy of this user.
        """

        return User(

            first_name=self.first_name,

            last_name=self.last_name,

            username=f"{self.username}_copy",

            email=f"copy_{self.email}",

            mobile=None,

            role=self.role,

            profile_image=self.profile_image,

            bio=self.bio,

            is_active=False,

            is_verified=False,

            is_locked=False

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
    def identity_hash(self):
        """
        SHA256 hash for user identity.
        """

        import hashlib

        content = (

            f"{self.username}"

            f"{self.email}"

            f"{self.role}"

        )

        return hashlib.sha256(

            content.encode("utf-8")

        ).hexdigest()

    # -------------------------------------------------------
    # AUDIT
    # -------------------------------------------------------

    def audit_log(self):

        return {

            "user_id": self.id,

            "username": self.username,

            "email": self.email,

            "role": self.role,

            "status": self.account_status,

            "login_count": self.login_count,

            "failed_attempts":
                self.failed_login_attempts,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "version": self.version

        }

    # -------------------------------------------------------
    # PASSWORD HELPERS
    # -------------------------------------------------------

    def change_password(
        self,
        old_password,
        new_password
    ):
        """
        Change user password.
        """

        if not self.check_password(old_password):

            return False

        self.set_password(new_password)

        self.updated_at = datetime.utcnow()

        return True

    def clear_login_history(self):

        self.login_count = 0

        self.failed_login_attempts = 0

        self.last_login = None

    # -------------------------------------------------------
    # INTEGRITY
    # -------------------------------------------------------

    @property
    def integrity_ok(self):

        return all(

            [

                self.username,

                self.email,

                self.password_hash,

                self.role

            ]

        )

    def integrity_report(self):

        issues = []

        if not self.username:

            issues.append(

                "Username missing."

            )

        if not self.email:

            issues.append(

                "Email missing."

            )

        if not self.password_hash:

            issues.append(

                "Password not set."

            )

        if self.role not in self.VALID_ROLES:

            issues.append(

                "Invalid role."

            )

        return {

            "valid": len(issues) == 0,

            "issues": issues

        }

    # -------------------------------------------------------
    # EXPORT
    # -------------------------------------------------------

    def export(self):

        return {

            "metadata": {

                "id": self.id,

                "username": self.username,

                "version": self.version,

                "created_at":
                    self.created_at.isoformat()
                    if self.created_at else None,

                "updated_at":
                    self.updated_at.isoformat()
                    if self.updated_at else None

            },

            "profile": self.profile(),

            "statistics": self.statistics(),

            "security": {

                "score": self.security_score,

                "level": self.security_level

            }

        }

    # -------------------------------------------------------
    # DISPLAY
    # -------------------------------------------------------

    def short_description(self):

        return (

            f"{self.full_name} "

            f"({self.role})"

        )

    # -------------------------------------------------------
    # OBJECT HELPERS
    # -------------------------------------------------------

    def __eq__(self, other):

        return (

            isinstance(other, User)

            and

            self.id == other.id

        )

    def __hash__(self):

        return hash(self.id)

    def __str__(self):

        return self.display_name
        # -------------------------------------------------------
    # PRE-SAVE HELPERS
    # -------------------------------------------------------

    def before_insert(self):
        """
        Prepare user before insert.
        """

        self.created_at = datetime.utcnow()

        self.updated_at = datetime.utcnow()

        if self.version is None:

            self.version = 1

        if self.login_count is None:

            self.login_count = 0

        if self.failed_login_attempts is None:

            self.failed_login_attempts = 0

    def before_update(self):
        """
        Prepare user before update.
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

        if not self.first_name:

            raise ValueError(
                "First name is required."
            )

        if not self.last_name:

            raise ValueError(
                "Last name is required."
            )

        if not self.username:

            raise ValueError(
                "Username is required."
            )

        if not self.email:

            raise ValueError(
                "Email is required."
            )

        if not self.password_hash:

            raise ValueError(
                "Password must be set."
            )

        if self.role not in self.VALID_ROLES:

            raise ValueError(
                "Invalid role."
            )

        return True

    # -------------------------------------------------------
    # SAFE SAVE
    # -------------------------------------------------------

    def save_safe(self):
        """
        Validate and save user.
        """

        self.validate_complete()

        db.session.add(self)

        db.session.commit()

        return self

    # -------------------------------------------------------
    # COMPLETE EXPORT
    # -------------------------------------------------------

    def production_export(self):
        """
        Export complete user information.
        """

        return {

            "metadata": {

                "id": self.id,

                "username": self.username,

                "version": self.version,

                "created_at":
                    self.created_at.isoformat()
                    if self.created_at else None,

                "updated_at":
                    self.updated_at.isoformat()
                    if self.updated_at else None

            },

            "profile": self.profile(),

            "statistics": self.statistics(),

            "security": {

                "score": self.security_score,

                "level": self.security_level,

                "verified": self.is_verified,

                "locked": self.is_locked

            }

        }

    # -------------------------------------------------------
    # DEBUG
    # -------------------------------------------------------

    def debug(self):

        return {

            "id": self.id,

            "username": self.username,

            "email": self.email,

            "role": self.role,

            "status": self.account_status,

            "version": self.version

        }
# ==========================================================
# SQLALCHEMY EVENTS
# ==========================================================

from sqlalchemy import event


@event.listens_for(User, "before_insert")
def user_before_insert(mapper, connection, target):

    target.before_insert()


@event.listens_for(User, "before_update")
def user_before_update(mapper, connection, target):

    target.before_update()


# ==========================================================
# MODULE EXPORT
# ==========================================================

__all__ = [

    "User"

]