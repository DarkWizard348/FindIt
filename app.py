"""
app.py - FindIt: College Lost & Found Portal
Main Flask Application
"""

import os
import uuid
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    abort,
)
from werkzeug.utils import secure_filename
from database import (
    CATEGORIES,
    CAMPUS_LOCATIONS,
    STATUSES,
    REPORT_TYPES,
    init_db,
    close_db,
    get_dashboard_counts,
    get_recent_reports,
    insert_item,
    get_item_by_id,
    search_and_filter_items,
    update_item_status,
)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    """Validates allowed image file extensions."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app(test_config=None):
    """
    Application factory for FindIt.
    Accepts optional test_config dictionary for isolated testing.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    upload_folder = os.path.join(base_dir, "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-findit-college-2026"),
        DATABASE=os.path.join(app.instance_path, "findit.sqlite"),
        UPLOAD_FOLDER=upload_folder,
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5 Megabytes limit
    )

    if test_config:
        app.config.update(test_config)

    # Register DB cleanup on app teardown
    app.teardown_appcontext(close_db)

    # Initialize SQLite database tables automatically
    with app.app_context():
        init_db(app.config["DATABASE"])

    # --------------------------------------------------------------------------
    # Routes
    # --------------------------------------------------------------------------

    @app.route("/")
    def index():
        """Homepage: Displays stats, search bar, and recent reports."""
        stats = get_dashboard_counts()
        recent_items = get_recent_reports(limit=6)
        return render_template("index.html", stats=stats, recent_items=recent_items)

    @app.route("/items")
    def browse_items():
        """Browse all reports with search and multi-filtering."""
        query = request.args.get("q", "").strip()
        report_type = request.args.get("type", "").strip()
        category = request.args.get("category", "").strip()
        location = request.args.get("location", "").strip()
        status = request.args.get("status", "").strip()

        items = search_and_filter_items(
            query=query,
            report_type=report_type,
            category=category,
            location=location,
            status=status,
        )

        return render_template(
            "items.html",
            items=items,
            categories=CATEGORIES,
            locations=CAMPUS_LOCATIONS,
            report_types=REPORT_TYPES,
            statuses=STATUSES,
            current_query=query,
            current_type=report_type,
            current_category=category,
            current_location=location,
            current_status=status,
        )

    @app.route("/report/lost", methods=["GET", "POST"])
    def report_lost():
        """Form to report a lost item."""
        if request.method == "POST":
            return handle_report_submission("Lost")
        return render_template(
            "report_form.html",
            report_type="Lost",
            categories=CATEGORIES,
            locations=CAMPUS_LOCATIONS,
        )

    @app.route("/report/found", methods=["GET", "POST"])
    def report_found():
        """Form to report a found item."""
        if request.method == "POST":
            return handle_report_submission("Found")
        return render_template(
            "report_form.html",
            report_type="Found",
            categories=CATEGORIES,
            locations=CAMPUS_LOCATIONS,
        )

    @app.route("/items/<int:item_id>")
    def view_item(item_id):
        """View full details of an item."""
        item = get_item_by_id(item_id)
        if item is None:
            abort(404)
        return render_template("item_detail.html", item=item)

    @app.route("/items/<int:item_id>/recover", methods=["POST"])
    def mark_recovered(item_id):
        """Update an item report's status to Recovered."""
        item = get_item_by_id(item_id)
        if item is None:
            abort(404)

        if item["status"] == "Recovered":
            flash("This item has already been marked as Recovered.", "info")
            return redirect(url_for("view_item", item_id=item_id))

        update_item_status(item_id, "Recovered")
        flash(f"Success! '{item['item_name']}' has been marked as Recovered.", "success")
        return redirect(url_for("view_item", item_id=item_id))

    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        """Safely serves uploaded item images from the uploads folder."""
        # Prevent directory traversal
        safe_name = secure_filename(filename)
        if not safe_name:
            abort(404)
        return send_from_directory(app.config["UPLOAD_FOLDER"], safe_name)

    # --------------------------------------------------------------------------
    # Helper: Form Submission Handler
    # --------------------------------------------------------------------------
    def handle_report_submission(report_type):
        item_name = request.form.get("item_name", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        item_date = request.form.get("item_date", "").strip()
        description = request.form.get("description", "").strip()

        # Validation: Required fields
        errors = []
        if not item_name:
            errors.append("Item name is required.")
        elif len(item_name) > 100:
            errors.append("Item name must be under 100 characters.")

        if not category or category not in CATEGORIES:
            errors.append("Please select a valid item category.")

        if not location:
            errors.append("Campus location is required.")
        elif len(location) > 120:
            errors.append("Location must be under 120 characters.")

        if not item_date:
            errors.append("Date is required.")

        if not description:
            errors.append("Description is required.")
        elif len(description) > 2000:
            errors.append("Description must be under 2000 characters.")

        # Image upload validation (Optional)
        image_filename = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "":
                if not allowed_file(file.filename):
                    errors.append(
                        "Unsupported image format. Allowed formats: PNG, JPG, JPEG, WEBP."
                    )
                else:
                    ext = file.filename.rsplit(".", 1)[1].lower()
                    unique_name = f"{uuid.uuid4().hex[:12]}_{secure_filename(file.filename)}"
                    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
                    file.save(upload_path)
                    image_filename = unique_name

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "report_form.html",
                report_type=report_type,
                categories=CATEGORIES,
                locations=CAMPUS_LOCATIONS,
                form_data=request.form,
            ), 400

        # Save to database
        item_dict = {
            "item_name": item_name,
            "category": category,
            "report_type": report_type,
            "location": location,
            "item_date": item_date,
            "description": description,
            "image_filename": image_filename,
            "status": report_type,
        }

        new_id = insert_item(item_dict)
        flash(
            f"Thank you! Your {report_type.lower()} item report for '{item_name}' was published successfully.",
            "success",
        )
        return redirect(url_for("view_item", item_id=new_id))

    # --------------------------------------------------------------------------
    # Error Handlers
    # --------------------------------------------------------------------------
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        flash("The uploaded file exceeds the 5MB maximum size limit.", "danger")
        return redirect(request.referrer or url_for("index"))

    return app


# Application entry point for dev server
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
