import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, SiteSettings, SocialLink, Project

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///site.db")

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    settings = db.session.get(SiteSettings, 1)
    links = SocialLink.query.order_by(SocialLink.sort_order).all()
    projects = Project.query.order_by(Project.sort_order).all()
    return render_template("index.html", settings=settings, links=links, projects=projects)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

@app.route("/admin")
@login_required
def admin_dashboard():
    settings = db.session.get(SiteSettings, 1)
    links = SocialLink.query.order_by(SocialLink.sort_order).all()
    projects = Project.query.order_by(Project.sort_order).all()
    return render_template("admin.html", settings=settings, links=links, projects=projects)


# --- Site settings ---

@app.route("/admin/settings", methods=["POST"])
@login_required
def admin_settings():
    settings = db.session.get(SiteSettings, 1)
    settings.name = request.form["name"]
    settings.tagline = request.form["tagline"]
    settings.footer_text = request.form["footer_text"]
    settings.meta_description = request.form["meta_description"]
    db.session.commit()
    flash("Settings updated.", "success")
    return redirect(url_for("admin_dashboard"))


# --- Projects ---

@app.route("/admin/project/add", methods=["POST"])
@login_required
def admin_project_add():
    max_order = db.session.query(db.func.max(Project.sort_order)).scalar() or 0
    project = Project(
        title=request.form["title"],
        description=request.form["description"],
        url=request.form.get("url") or None,
        icon_svg=request.form.get("icon_svg", ""),
        icon_bg_color=request.form.get("icon_bg_color", "rgba(74, 124, 255, 0.12)"),
        icon_text_color=request.form.get("icon_text_color", "var(--accent-blue)"),
        tags=request.form.get("tags", ""),
        sort_order=max_order + 1,
    )
    db.session.add(project)
    db.session.commit()
    flash(f"Project '{project.title}' added.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/project/<int:project_id>/edit", methods=["POST"])
@login_required
def admin_project_edit(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("admin_dashboard"))
    project.title = request.form["title"]
    project.description = request.form["description"]
    project.url = request.form.get("url") or None
    project.icon_svg = request.form.get("icon_svg", project.icon_svg)
    project.icon_bg_color = request.form.get("icon_bg_color", project.icon_bg_color)
    project.icon_text_color = request.form.get("icon_text_color", project.icon_text_color)
    project.tags = request.form.get("tags", "")
    project.sort_order = int(request.form.get("sort_order", project.sort_order))
    db.session.commit()
    flash(f"Project '{project.title}' updated.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/project/<int:project_id>/delete", methods=["POST"])
@login_required
def admin_project_delete(project_id):
    project = db.session.get(Project, project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
        flash(f"Project '{project.title}' deleted.", "success")
    return redirect(url_for("admin_dashboard"))


# --- Social links ---

@app.route("/admin/link/add", methods=["POST"])
@login_required
def admin_link_add():
    max_order = db.session.query(db.func.max(SocialLink.sort_order)).scalar() or 0
    link = SocialLink(
        label=request.form["label"],
        url=request.form["url"],
        icon_svg=request.form.get("icon_svg", ""),
        sort_order=max_order + 1,
    )
    db.session.add(link)
    db.session.commit()
    flash(f"Link '{link.label}' added.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/link/<int:link_id>/edit", methods=["POST"])
@login_required
def admin_link_edit(link_id):
    link = db.session.get(SocialLink, link_id)
    if not link:
        flash("Link not found.", "error")
        return redirect(url_for("admin_dashboard"))
    link.label = request.form["label"]
    link.url = request.form["url"]
    link.icon_svg = request.form.get("icon_svg", link.icon_svg)
    link.sort_order = int(request.form.get("sort_order", link.sort_order))
    db.session.commit()
    flash(f"Link '{link.label}' updated.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/link/<int:link_id>/delete", methods=["POST"])
@login_required
def admin_link_delete(link_id):
    link = db.session.get(SocialLink, link_id)
    if link:
        db.session.delete(link)
        db.session.commit()
        flash(f"Link '{link.label}' deleted.", "success")
    return redirect(url_for("admin_dashboard"))


# --- Password change ---

@app.route("/admin/password", methods=["POST"])
@login_required
def admin_password():
    if not current_user.check_password(request.form["current_password"]):
        flash("Current password is incorrect.", "error")
        return redirect(url_for("admin_dashboard"))
    new_pw = request.form["new_password"]
    if len(new_pw) < 8:
        flash("New password must be at least 8 characters.", "error")
        return redirect(url_for("admin_dashboard"))
    current_user.set_password(new_pw)
    db.session.commit()
    flash("Password updated.", "success")
    return redirect(url_for("admin_dashboard"))


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
