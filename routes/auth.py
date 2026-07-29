"""
==========================================================
Lab Auto Grader
Authentication Routes
Part 1
==========================================================
"""

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
    login_user,
    logout_user,
    login_required,
    current_user
)

from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired
)

from extensions import db

from models.user import User


# ==========================================================
# BLUEPRINT
# ==========================================================

auth_bp = Blueprint(

    "auth",

    __name__,

    url_prefix="/auth"

)


# ==========================================================
# HELPERS
# ==========================================================

def serializer():

    return URLSafeTimedSerializer(

        current_app.config["SECRET_KEY"]

    )


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
# TOKEN HELPERS
# ==========================================================

def generate_token(email):

    return serializer().dumps(

        email,

        salt="auth-token"

    )


def verify_token(

    token,

    max_age=3600

):

    try:

        email = serializer().loads(

            token,

            salt="auth-token",

            max_age=max_age

        )

        return email

    except SignatureExpired:

        return None

    except BadSignature:

        return None


# ==========================================================
# REDIRECT HELPERS
# ==========================================================

def redirect_after_login(user):

    if user.is_admin:

        return redirect(

            url_for(

                "admin.dashboard"

            )

        )

    if user.is_teacher:

        return redirect(

            url_for(

                "teacher.dashboard"

            )

        )

    return redirect(

        url_for(

            "student.dashboard"

        )

    )


# ==========================================================
# CONTEXT PROCESSOR
# ==========================================================

@auth_bp.app_context_processor
def auth_context():

    return {

        "current_year":

            datetime.utcnow().year

    }


# ==========================================================
# INDEX
# ==========================================================

@auth_bp.route("/")
def index():

    if current_user.is_authenticated:

        return redirect_after_login(

            current_user

        )

    return redirect(

        url_for(

            "auth.login"

        )

    )
# ==========================================================
# LOGIN
# ==========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:

        return redirect_after_login(current_user)

    if request.method == "POST":

        username = request.form.get(

            "username",

            ""

        ).strip()

        password = request.form.get(

            "password",

            ""

        )

        remember = request.form.get(

            "remember"

        ) is not None

        if not username or not password:

            warning(

                "Username and password are required."

            )

            return render_template(

                "auth/login.html"

            )

        user = User.query.filter(

            db.or_(

                User.username == username,

                User.email == username

            )

        ).first()

        if user is None:

            error(

                "Invalid username or password."

            )

            return render_template(

                "auth/login.html"

            )

        if not user.is_active:

            error(

                "Your account has been deactivated."

            )

            return render_template(

                "auth/login.html"

            )

        if user.is_locked:

            error(

                "Your account is locked."

            )

            return render_template(

                "auth/login.html"

            )

        if not user.authenticate(password):

            db.session.commit()

            error(

                "Invalid username or password."

            )

            return render_template(

                "auth/login.html"

            )

        login_user(

            user,

            remember=remember

        )

        db.session.commit()

        success(

            f"Welcome {user.display_name}!"

        )

        next_page = request.args.get(

            "next"

        )

        if next_page:

            return redirect(next_page)

        return redirect_after_login(user)

    return render_template(

        "auth/login.html"

    )


# ==========================================================
# LOGOUT
# ==========================================================

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    success(

        "Logged out successfully."

    )

    return redirect(

        url_for(

            "auth.login"

        )

    )


# ==========================================================
# LOGIN STATUS
# ==========================================================

@auth_bp.route("/status")
@login_required
def login_status():

    return jsonify(

        {

            "authenticated": True,

            "user": current_user.to_dict()

        }

    )


# ==========================================================
# ACCESS DENIED
# ==========================================================

@auth_bp.route("/access-denied")
def access_denied():

    return render_template(

        "auth/access_denied.html"

    ), 403


# ==========================================================
# SESSION INFORMATION
# ==========================================================

@auth_bp.route("/session")
@login_required
def session_info():

    return jsonify(

        {

            "user_id": current_user.id,

            "username": current_user.username,

            "role": current_user.role,

            "last_login": (

                current_user.last_login.isoformat()

                if current_user.last_login

                else None

            ),

            "authenticated": True

        }

    )


# ==========================================================
# WHO AM I
# ==========================================================

@auth_bp.route("/me")
@login_required
def me():

    return jsonify(

        current_user.to_dict()

    )
# ==========================================================
# STUDENT REGISTRATION
# ==========================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:

        return redirect_after_login(current_user)

    if request.method == "POST":

        first_name = request.form.get(

            "first_name", ""

        ).strip()

        last_name = request.form.get(

            "last_name", ""

        ).strip()

        username = request.form.get(

            "username", ""

        ).strip().lower()

        email = request.form.get(

            "email", ""

        ).strip().lower()

        mobile = request.form.get(

            "mobile", ""

        ).strip()

        password = request.form.get(

            "password", ""

        )

        confirm_password = request.form.get(

            "confirm_password", ""

        )

        enrollment_number = request.form.get(

            "enrollment_number", ""

        ).strip()

        branch = request.form.get(

            "branch", ""

        ).strip()

        semester = request.form.get(

            "semester", ""

        ).strip()

        if password != confirm_password:

            error(

                "Passwords do not match."

            )

            return render_template(

                "auth/register.html"

            )

        if User.exists(username):

            error(

                "Username already exists."

            )

            return render_template(

                "auth/register.html"

            )

        if User.email_exists(email):

            error(

                "Email already registered."

            )

            return render_template(

                "auth/register.html"

            )

        if mobile and User.mobile_exists(mobile):

            error(

                "Mobile number already registered."

            )

            return render_template(

                "auth/register.html"

            )

        try:

            user = User(

                first_name=first_name,

                last_name=last_name,

                username=username,

                email=email,

                mobile=mobile,

                role=User.ROLE_STUDENT

            )

            user.set_password(password)

            user.is_verified = False

            db.session.add(user)

            db.session.flush()

            student = User(

                user_id=user.id,

                enrollment_number=enrollment_number,

                branch=branch,

                semester=semester

            )

            db.session.add(student)

            db.session.commit()

            login_user(user)

            success(

                "Registration completed successfully."

            )

            return redirect_after_login(user)

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "auth/register.html"

    )


# ==========================================================
# TEACHER REGISTRATION
# ==========================================================

@auth_bp.route(
    "/register/teacher",
    methods=["GET", "POST"]
)
def register_teacher():

    if request.method == "POST":

        try:

            password = request.form["password"]

            confirm = request.form["confirm_password"]

            if password != confirm:

                error(

                    "Passwords do not match."

                )

                return redirect(

                    url_for(

                        "auth.register_teacher"

                    )

                )

            if User.exists(

                request.form["username"]

            ):

                error(

                    "Username already exists."

                )

                return redirect(

                    url_for(

                        "auth.register_teacher"

                    )

                )

            if User.email_exists(

                request.form["email"]

            ):

                error(

                    "Email already exists."

                )

                return redirect(

                    url_for(

                        "auth.register_teacher"

                    )

                )

            user = User(

                first_name=request.form["first_name"],

                last_name=request.form["last_name"],

                username=request.form["username"],

                email=request.form["email"],

                mobile=request.form.get("mobile"),

                role=User.ROLE_TEACHER

            )

            user.set_password(password)

            db.session.add(user)

            db.session.flush()

            teacher = User(

                user_id=user.id,

                employee_id=request.form["employee_id"],

                department=request.form.get("department"),

                designation=request.form.get("designation")

            )

            db.session.add(teacher)

            db.session.commit()

            success(

                "Teacher registered successfully."

            )

            return redirect(

                url_for(

                    "auth.login"

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "auth/register_teacher.html"

    )


# ==========================================================
# ADMIN REGISTRATION
# ==========================================================

@auth_bp.route(
    "/register/admin",
    methods=["GET", "POST"]
)
def register_admin():

    if User.admins().count() > 0:

        abort(403)

    if request.method == "POST":

        try:

            user = User(

                first_name=request.form["first_name"],

                last_name=request.form["last_name"],

                username=request.form["username"],

                email=request.form["email"],

                role=User.ROLE_ADMIN,

                is_verified=True

            )

            user.set_password(

                request.form["password"]

            )

            db.session.add(user)

            db.session.commit()

            success(

                "Administrator account created."

            )

            return redirect(

                url_for(

                    "auth.login"

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "auth/register_admin.html"
    )
# ==========================================================
# FORGOT PASSWORD
# ==========================================================

@auth_bp.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if current_user.is_authenticated:

        return redirect_after_login(current_user)

    if request.method == "POST":

        email = request.form.get(

            "email",

            ""

        ).strip().lower()

        if not email:

            warning(

                "Please enter your email address."

            )

            return render_template(

                "auth/forgot_password.html"

            )

        user = User.get_by_email(email)

        if user:

            token = generate_token(user.email)

            reset_url = url_for(

                "auth.reset_password",

                token=token,

                _external=True

            )

            # --------------------------------------------------
            # TODO:
            # Send email using Flask-Mail or SMTP.
            # --------------------------------------------------

            current_app.logger.info(

                f"Password reset link: {reset_url}"

            )

        success(

            "If an account with that email exists, "
            "a password reset link has been generated."

        )

        return redirect(

            url_for(

                "auth.login"

            )

        )

    return render_template(

        "auth/forgot_password.html"

    )


# ==========================================================
# RESET PASSWORD
# ==========================================================

@auth_bp.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password(token):

    if current_user.is_authenticated:

        return redirect_after_login(

            current_user

        )

    email = verify_token(

        token,

        max_age=3600

    )

    if email is None:

        error(

            "Password reset link is invalid or expired."

        )

        return redirect(

            url_for(

                "auth.forgot_password"

            )

        )

    user = User.get_by_email(email)

    if user is None:

        error(

            "User not found."

        )

        return redirect(

            url_for(

                "auth.login"

            )

        )

    if request.method == "POST":

        password = request.form.get(

            "password",

            ""

        )

        confirm = request.form.get(

            "confirm_password",

            ""

        )

        if password != confirm:

            error(

                "Passwords do not match."

            )

            return render_template(

                "auth/reset_password.html",

                token=token

            )

        try:

            user.set_password(

                password

            )

            user.failed_login_attempts = 0

            user.is_locked = False

            user.updated_at = datetime.utcnow()

            db.session.commit()

            success(

                "Password reset successfully."

            )

            return redirect(

                url_for(

                    "auth.login"

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "auth/reset_password.html",

        token=token

    )


# ==========================================================
# RESEND RESET LINK
# ==========================================================

@auth_bp.route(
    "/forgot-password/resend",
    methods=["POST"]
)
def resend_reset_link():

    email = request.form.get(

        "email",

        ""

    ).strip().lower()

    user = User.get_by_email(

        email

    )

    if user:

        token = generate_token(

            user.email

        )

        reset_url = url_for(

            "auth.reset_password",

            token=token,

            _external=True

        )

        current_app.logger.info(

            f"Password reset link: {reset_url}"

        )

    success(

        "If the email exists, a new reset link has been generated."

    )

    return redirect(

        url_for(

            "auth.login"

        )

    )


# ==========================================================
# RESET PASSWORD STATUS
# ==========================================================

@auth_bp.route(
    "/reset-password/status/<token>"
)
def reset_password_status(token):

    email = verify_token(

        token,

        max_age=3600

    )

    return jsonify(

        {

            "valid": email is not None,

            "email": email

        }

    )


# ==========================================================
# PASSWORD RESET SUCCESS
# ==========================================================

@auth_bp.route("/reset-password/success")
def reset_password_success():

    return render_template(

        "auth/reset_success.html"

    )
# ==========================================================
# EMAIL VERIFICATION
# ==========================================================

@auth_bp.route("/verify/<token>")
def verify_email(token):

    email = verify_token(

        token,

        max_age=86400

    )

    if email is None:

        error(

            "Verification link is invalid or expired."

        )

        return redirect(

            url_for(

                "auth.login"

            )

        )

    user = User.get_by_email(email)

    if user is None:

        error(

            "User not found."

        )

        return redirect(

            url_for(

                "auth.login"

            )

        )

    if user.is_verified:

        info(

            "Email is already verified."

        )

        return redirect(

            url_for(

                "auth.login"

            )

        )

    user.verify()

    db.session.commit()

    success(

        "Email verified successfully."

    )

    return redirect(

        url_for(

            "auth.login"

        )

    )


# ==========================================================
# RESEND VERIFICATION EMAIL
# ==========================================================

@auth_bp.route(
    "/verify/resend",
    methods=["GET", "POST"]
)
def resend_verification():

    if request.method == "POST":

        email = request.form.get(

            "email",

            ""

        ).strip().lower()

        user = User.get_by_email(

            email

        )

        if user:

            if user.is_verified:

                info(

                    "Your email is already verified."

                )

                return redirect(

                    url_for(

                        "auth.login"

                    )

                )

            token = generate_token(

                user.email

            )

            verify_url = url_for(

                "auth.verify_email",

                token=token,

                _external=True

            )

            # ------------------------------------------
            # TODO:
            # Send verification email here.
            # ------------------------------------------

            current_app.logger.info(

                f"Verification URL: {verify_url}"

            )

        success(

            "If your account exists, a verification email has been sent."

        )

        return redirect(

            url_for(

                "auth.login"

            )

        )

    return render_template(

        "auth/resend_verification.html"

    )


# ==========================================================
# ACTIVATE ACCOUNT
# ==========================================================

@auth_bp.route(
    "/activate/<token>"
)
def activate_account(token):

    email = verify_token(

        token,

        max_age=86400

    )

    if email is None:

        error(

            "Activation link is invalid."

        )

        return redirect(

            url_for(

                "auth.login"

            )

        )

    user = User.get_by_email(

        email

    )

    if user is None:

        error(

            "Account not found."

        )

        return redirect(

            url_for(

                "auth.login"

            )

        )

    user.activate()

    user.verify()

    db.session.commit()

    success(

        "Account activated successfully."

    )

    return redirect(

        url_for(

            "auth.login"

        )

    )


# ==========================================================
# VERIFICATION STATUS API
# ==========================================================

@auth_bp.route(
    "/verify/status/<token>"
)
def verification_status(token):

    email = verify_token(

        token,

        max_age=86400

    )

    return jsonify(

        {

            "valid":

                email is not None,

            "email":

                email

        }

    )


# ==========================================================
# VERIFY CURRENT ACCOUNT
# ==========================================================

@auth_bp.route(
    "/verify-now",
    methods=["POST"]
)
@login_required
def verify_current_account():

    if current_user.is_verified:

        info(

            "Your account is already verified."

        )

        return redirect(

            url_for(

                "auth.profile"

            )

        )

    token = generate_token(

        current_user.email

    )

    verification_url = url_for(

        "auth.verify_email",

        token=token,

        _external=True

    )

    current_app.logger.info(

        f"Verification URL: {verification_url}"

    )

    success(

        "Verification email has been generated."

    )

    return redirect(

        url_for(

            "auth.profile"

        )

    )


# ==========================================================
# EMAIL VERIFIED PAGE
# ==========================================================

@auth_bp.route("/verified")
def verified():

    return render_template(

        "auth/verified.html"

    )
# ==========================================================
# USER PROFILE
# ==========================================================

@auth_bp.route("/profile")
@login_required
def profile():

    return render_template(

        "auth/profile.html",

        user=current_user

    )


# ==========================================================
# EDIT PROFILE
# ==========================================================

@auth_bp.route(
    "/profile/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_profile():

    if request.method == "POST":

        try:

            current_user.first_name = request.form.get(

                "first_name",

                current_user.first_name

            ).strip()

            current_user.last_name = request.form.get(

                "last_name",

                current_user.last_name

            ).strip()

            current_user.mobile = request.form.get(

                "mobile",

                current_user.mobile

            ).strip()

            current_user.bio = request.form.get(

                "bio",

                current_user.bio

            ).strip()

            current_user.updated_at = datetime.utcnow()

            db.session.commit()

            success(

                "Profile updated successfully."

            )

            return redirect(

                url_for(

                    "auth.profile"

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "auth/edit_profile.html",

        user=current_user

    )


# ==========================================================
# UPDATE MOBILE
# ==========================================================

@auth_bp.route(
    "/profile/mobile",
    methods=["POST"]
)
@login_required
def update_mobile():

    try:

        current_user.mobile = request.form.get(

            "mobile"

        ).strip()

        current_user.updated_at = datetime.utcnow()

        db.session.commit()

        success(

            "Mobile number updated."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "auth.profile"

        )

    )


# ==========================================================
# UPDATE BIO
# ==========================================================

@auth_bp.route(
    "/profile/bio",
    methods=["POST"]
)
@login_required
def update_bio():

    try:

        current_user.bio = request.form.get(

            "bio",

            ""

        )

        current_user.updated_at = datetime.utcnow()

        db.session.commit()

        success(

            "Bio updated."

        )

    except Exception as e:

        db.session.rollback()

        error(str(e))

    return redirect(

        url_for(

            "auth.profile"

        )

    )


# ==========================================================
# PROFILE IMAGE UPLOAD
# ==========================================================

@auth_bp.route(
    "/profile/avatar",
    methods=["POST"]
)
@login_required
def upload_avatar():

    file = request.files.get(

        "profile_image"

    )

    if not file or file.filename == "":

        warning(

            "Please select an image."

        )

        return redirect(

            url_for(

                "auth.profile"

            )

        )

    allowed_extensions = {

        "png",

        "jpg",

        "jpeg",

        "gif",

        "webp"

    }

    extension = (

        file.filename

        .rsplit(".", 1)[-1]

        .lower()

    )

    if extension not in allowed_extensions:

        error(

            "Invalid image format."

        )

        return redirect(

            url_for(

                "auth.profile"

            )

        )

    import os
    from werkzeug.utils import secure_filename

    filename = secure_filename(

        f"user_{current_user.id}.{extension}"

    )

    upload_folder = current_app.config.get(

        "PROFILE_UPLOAD_FOLDER",

        "static/uploads/profile"

    )

    os.makedirs(

        upload_folder,

        exist_ok=True

    )

    path = os.path.join(

        upload_folder,

        filename

    )

    file.save(path)

    current_user.profile_image = (

        f"/{upload_folder}/{filename}"

    )

    current_user.updated_at = datetime.utcnow()

    db.session.commit()

    success(

        "Profile image updated successfully."

    )

    return redirect(

        url_for(

            "auth.profile"

        )

    )


# ==========================================================
# DELETE PROFILE IMAGE
# ==========================================================

@auth_bp.route(
    "/profile/avatar/delete",
    methods=["POST"]
)
@login_required
def delete_avatar():

    current_user.profile_image = None

    current_user.updated_at = datetime.utcnow()

    db.session.commit()

    success(

        "Profile image removed."

    )

    return redirect(

        url_for(

            "auth.profile"

        )

    )


# ==========================================================
# PROFILE JSON API
# ==========================================================

@auth_bp.route("/api/profile")
@login_required
def profile_api():

    return jsonify(

        current_user.profile()

    )


# ==========================================================
# ACCOUNT DASHBOARD
# ==========================================================

@auth_bp.route("/dashboard")
@login_required
def account_dashboard():

    return render_template(

        "auth/dashboard.html",

        user=current_user,

        statistics=current_user.statistics()

    )
# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@auth_bp.route(
    "/security/password",
    methods=["GET", "POST"]
)
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form.get(

            "current_password",

            ""

        )

        new_password = request.form.get(

            "new_password",

            ""

        )

        confirm_password = request.form.get(

            "confirm_password",

            ""

        )

        if not current_user.check_password(

            current_password

        ):

            error(

                "Current password is incorrect."

            )

            return render_template(

                "auth/change_password.html"

            )

        if new_password != confirm_password:

            error(

                "Passwords do not match."

            )

            return render_template(

                "auth/change_password.html"

            )

        try:

            current_user.set_password(

                new_password

            )

            current_user.updated_at = datetime.utcnow()

            db.session.commit()

            success(

                "Password changed successfully."

            )

            return redirect(

                url_for(

                    "auth.profile"

                )

            )

        except Exception as e:

            db.session.rollback()

            error(str(e))

    return render_template(

        "auth/change_password.html"

    )


# ==========================================================
# CHANGE EMAIL
# ==========================================================

@auth_bp.route(
    "/security/email",
    methods=["POST"]
)
@login_required
def change_email():

    email = request.form.get(

        "email",

        ""

    ).strip().lower()

    if User.email_exists(email):

        error(

            "Email already exists."

        )

        return redirect(

            url_for(

                "auth.profile"

            )

        )

    current_user.email = email

    current_user.is_verified = False

    current_user.updated_at = datetime.utcnow()

    db.session.commit()

    success(

        "Email updated successfully."

    )

    return redirect(

        url_for(

            "auth.profile"

        )

    )


# ==========================================================
# CHANGE USERNAME
# ==========================================================

@auth_bp.route(
    "/security/username",
    methods=["POST"]
)
@login_required
def change_username():

    username = request.form.get(

        "username",

        ""

    ).strip().lower()

    if User.exists(username):

        error(

            "Username already exists."

        )

        return redirect(

            url_for(

                "auth.profile"

            )

        )

    current_user.username = username

    current_user.updated_at = datetime.utcnow()

    db.session.commit()

    success(

        "Username updated successfully."

    )

    return redirect(

        url_for(

            "auth.profile"

        )

    )


# ==========================================================
# SECURITY SETTINGS
# ==========================================================

@auth_bp.route("/security")
@login_required
def security():

    return render_template(

        "auth/security.html",

        user=current_user

    )


# ==========================================================
# LOGIN HISTORY
# ==========================================================

@auth_bp.route("/security/history")
@login_required
def login_history():

    history = {

        "login_count":

            current_user.login_count,

        "failed_attempts":

            current_user.failed_login_attempts,

        "last_login":

            current_user.last_login

    }

    return render_template(

        "auth/login_history.html",

        history=history

    )


# ==========================================================
# DEACTIVATE ACCOUNT
# ==========================================================

@auth_bp.route(
    "/deactivate",
    methods=["GET", "POST"]
)
@login_required
def deactivate_account():

    if request.method == "POST":

        password = request.form.get(

            "password",

            ""

        )

        if not current_user.check_password(

            password

        ):

            error(

                "Incorrect password."

            )

            return render_template(

                "auth/deactivate.html"

            )

        current_user.deactivate()

        db.session.commit()

        logout_user()

        success(

            "Account deactivated successfully."

        )

        return redirect(

            url_for(

                "auth.login"

            )

        )

    return render_template(

        "auth/deactivate.html"

    )


# ==========================================================
# ENABLE TWO-FACTOR (PLACEHOLDER)
# ==========================================================

@auth_bp.route(
    "/security/2fa/enable",
    methods=["POST"]
)
@login_required
def enable_2fa():

    info(

        "Two-factor authentication "
        "will be available soon."

    )

    return redirect(

        url_for(

            "auth.security"

        )

    )


# ==========================================================
# DISABLE TWO-FACTOR (PLACEHOLDER)
# ==========================================================

@auth_bp.route(
    "/security/2fa/disable",
    methods=["POST"]
)
@login_required
def disable_2fa():

    info(

        "Two-factor authentication "
        "will be available soon."

    )

    return redirect(

        url_for(

            "auth.security"

        )

    )


# ==========================================================
# SECURITY API
# ==========================================================

@auth_bp.route("/api/security")
@login_required
def security_api():

    return jsonify(

        {

            "verified":

                current_user.is_verified,

            "locked":

                current_user.is_locked,

            "login_count":

                current_user.login_count,

            "failed_attempts":

                current_user.failed_login_attempts,

            "last_login":

                current_user.last_login.isoformat()

                if current_user.last_login

                else None,

            "security_score":

                current_user.security_score,

            "security_level":

                current_user.security_level

        }

    )
# ==========================================================
# SESSION MANAGEMENT
# ==========================================================

@auth_bp.route("/session")
@login_required
def session():

    return render_template(

        "auth/session.html",

        user=current_user,

        last_login=current_user.last_login,

        login_count=current_user.login_count,

        failed_attempts=current_user.failed_login_attempts

    )


# ==========================================================
# REMEMBER ME STATUS
# ==========================================================

@auth_bp.route("/remember")
@login_required
def remember_status():

    return jsonify(

        {

            "remember_supported": True,

            "authenticated": current_user.is_authenticated,

            "user": current_user.username

        }

    )


# ==========================================================
# LOGOUT ALL DEVICES (PLACEHOLDER)
# ==========================================================

@auth_bp.route(
    "/logout-all",
    methods=["POST"]
)
@login_required
def logout_all_devices():

    current_user.updated_at = datetime.utcnow()

    db.session.commit()

    logout_user()

    success(

        "Logged out from all devices."

    )

    return redirect(

        url_for(

            "auth.login"

        )

    )


# ==========================================================
# REFRESH SESSION
# ==========================================================

@auth_bp.route(
    "/refresh-session",
    methods=["POST"]
)
@login_required
def refresh_session():

    current_user.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify(

        {

            "success": True,

            "message": "Session refreshed.",

            "timestamp": datetime.utcnow().isoformat()

        }

    )


# ==========================================================
# CURRENT USER API
# ==========================================================

@auth_bp.route("/api/current-user")
@login_required
def current_user_api():

    return jsonify(

        current_user.to_dict()

    )


# ==========================================================
# AUTHENTICATION STATUS API
# ==========================================================

@auth_bp.route("/api/status")
def auth_status():

    if current_user.is_authenticated:

        return jsonify(

            {

                "authenticated": True,

                "user": current_user.summary()

            }

        )

    return jsonify(

        {

            "authenticated": False

        }

    )


# ==========================================================
# REFRESH TOKEN (PLACEHOLDER)
# ==========================================================

@auth_bp.route(
    "/api/token/refresh",
    methods=["POST"]
)
@login_required
def refresh_token():

    token = generate_token(

        current_user.email

    )

    return jsonify(

        {

            "success": True,

            "token": token

        }

    )


# ==========================================================
# VALIDATE TOKEN
# ==========================================================

@auth_bp.route(
    "/api/token/validate/<token>"
)
def validate_token(token):

    email = verify_token(

        token,

        max_age=3600

    )

    return jsonify(

        {

            "valid": email is not None,

            "email": email

        }

    )


# ==========================================================
# REVOKE TOKEN (PLACEHOLDER)
# ==========================================================

@auth_bp.route(
    "/api/token/revoke",
    methods=["POST"]
)
@login_required
def revoke_token():

    return jsonify(

        {

            "success": True,

            "message": "Token revoked."

        }

    )


# ==========================================================
# LOGIN STATISTICS
# ==========================================================

@auth_bp.route("/statistics")
@login_required
def login_statistics():

    return render_template(

        "auth/statistics.html",

        statistics=current_user.statistics()

    )


# ==========================================================
# ACCOUNT SUMMARY API
# ==========================================================

@auth_bp.route("/api/account")
@login_required
def account_api():

    return jsonify(

        {

            "profile": current_user.profile(),

            "statistics": current_user.statistics(),

            "security": {

                "score": current_user.security_score,

                "level": current_user.security_level

            }

        }

    )
# ==========================================================
# USER PREFERENCES
# ==========================================================

@auth_bp.route("/preferences")
@login_required
def preferences():

    return render_template(

        "auth/preferences.html",

        user=current_user

    )


@auth_bp.route(
    "/preferences",
    methods=["POST"]
)
@login_required
def update_preferences():

    try:

        session["theme"] = request.form.get(

            "theme",

            "light"

        )

        session["language"] = request.form.get(

            "language",

            "en"

        )

        session["notifications"] = (

            request.form.get(

                "notifications"

            ) == "on"

        )

        success(

            "Preferences updated successfully."

        )

    except Exception as e:

        error(str(e))

    return redirect(

        url_for(

            "auth.preferences"

        )

    )


# ==========================================================
# THEME
# ==========================================================

@auth_bp.route(
    "/theme/<string:theme>",
    methods=["POST"]
)
@login_required
def change_theme(theme):

    allowed = {

        "light",

        "dark",

        "system"

    }

    if theme not in allowed:

        abort(400)

    session["theme"] = theme

    return jsonify(

        {

            "success": True,

            "theme": theme

        }

    )


# ==========================================================
# LANGUAGE
# ==========================================================

@auth_bp.route(
    "/language/<string:language>",
    methods=["POST"]
)
@login_required
def change_language(language):

    allowed = {

        "en",

        "hi"

    }

    if language not in allowed:

        abort(400)

    session["language"] = language

    return jsonify(

        {

            "success": True,

            "language": language

        }

    )


# ==========================================================
# NOTIFICATIONS
# ==========================================================

@auth_bp.route(
    "/notifications",
    methods=["GET", "POST"]
)
@login_required
def notification_settings():

    if request.method == "POST":

        session["notifications"] = (

            request.form.get(

                "enabled"

            ) == "on"

        )

        success(

            "Notification settings updated."

        )

        return redirect(

            url_for(

                "auth.notification_settings"

            )

        )

    return render_template(

        "auth/notifications.html"

    )


# ==========================================================
# EXPORT PROFILE
# ==========================================================

@auth_bp.route("/export-profile")
@login_required
def export_profile():

    return jsonify(

        current_user.export()

    )


# ==========================================================
# ACCOUNT SUMMARY
# ==========================================================

@auth_bp.route("/summary")
@login_required
def account_summary():

    return render_template(

        "auth/account_summary.html",

        user=current_user,

        summary=current_user.summary(),

        statistics=current_user.statistics()

    )


# ==========================================================
# SOFT DELETE ACCOUNT
# ==========================================================

@auth_bp.route(
    "/delete-account",
    methods=["GET", "POST"]
)
@login_required
def delete_account():

    if request.method == "POST":

        password = request.form.get(

            "password",

            ""

        )

        if not current_user.check_password(

            password

        ):

            error(

                "Incorrect password."

            )

            return render_template(

                "auth/delete_account.html"

            )

        current_user.deactivate()

        db.session.commit()

        logout_user()

        success(

            "Account deleted successfully."

        )

        return redirect(

            url_for(

                "auth.login"

            )

        )

    return render_template(

        "auth/delete_account.html"

    )


# ==========================================================
# ACCOUNT INFO API
# ==========================================================

@auth_bp.route("/api/preferences")
@login_required
def preferences_api():

    return jsonify(

        {

            "theme":

                session.get(

                    "theme",

                    "light"

                ),

            "language":

                session.get(

                    "language",

                    "en"

                ),

            "notifications":

                session.get(

                    "notifications",

                    True

                )

        }

    )


# ==========================================================
# PROFILE EXPORT API
# ==========================================================

@auth_bp.route("/api/export")
@login_required
def export_profile_api():

    return jsonify(

        {

            "profile":

                current_user.profile(),

            "statistics":

                current_user.statistics(),

            "security":

                {

                    "score":

                        current_user.security_score,

                    "level":

                        current_user.security_level

                }

        }

    )
# ==========================================================
# ERROR HANDLERS
# ==========================================================

@auth_bp.errorhandler(400)
def bad_request(error):

    return render_template(

        "errors/400.html",

        error=error

    ), 400


@auth_bp.errorhandler(401)
def unauthorized(error):

    return render_template(

        "errors/401.html",

        error=error

    ), 401


@auth_bp.errorhandler(403)
def forbidden(error):

    return render_template(

        "errors/403.html",

        error=error

    ), 403


@auth_bp.errorhandler(404)
def not_found(error):

    return render_template(

        "errors/404.html",

        error=error

    ), 404


@auth_bp.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return render_template(

        "errors/500.html",

        error=error

    ), 500


# ==========================================================
# JSON HELPERS
# ==========================================================

def json_success(message, **kwargs):

    payload = {

        "success": True,

        "message": message

    }

    payload.update(kwargs)

    return jsonify(payload)


def json_error(message, status=400, **kwargs):

    payload = {

        "success": False,

        "message": message

    }

    payload.update(kwargs)

    return jsonify(payload), status


# ==========================================================
# HEALTH CHECK
# ==========================================================

@auth_bp.route("/health")
def health():

    return jsonify(

        {

            "status": "ok",

            "service": "authentication",

            "timestamp":

                datetime.utcnow().isoformat()

        }

    )


# ==========================================================
# VERSION
# ==========================================================

@auth_bp.route("/version")
def version():

    return jsonify(

        {

            "application":

                "Lab Auto Grader",

            "module":

                "Authentication",

            "version":

                "1.0.0"

        }

    )


# ==========================================================
# PING
# ==========================================================

@auth_bp.route("/ping")
def ping():

    return jsonify(

        {

            "status": "alive",

            "time":

                datetime.utcnow().isoformat()

        }

    )


# ==========================================================
# BLUEPRINT INITIALIZER
# ==========================================================

def init_app(app):
    """
    Register Authentication Blueprint.
    """

    app.register_blueprint(auth_bp)


# ==========================================================
# MODULE EXPORT
# ==========================================================

__all__ = [

    "auth_bp",

    "init_app",

    "generate_token",

    "verify_token",

    "redirect_after_login"

]