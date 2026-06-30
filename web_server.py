# flask part for public pages
import threading
from flask import Flask, render_template, abort, redirect, request
from logic import AppLogic

logic = AppLogic()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "linkverse-dev-key"


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/u/<username>")
def profile(username):
    user, link_groups = logic.get_public_profile_grouped(username, record_view=True)
    if user is None:
        abort(404)
    return render_template("profile.html", user=user, link_groups=link_groups)


@app.route("/u/<username>/<slug>")
def profile_link_slug(username, slug):
    user, link = logic.get_link_by_slug(username, slug)
    if user is None:
        abort(404)
    if link is None:
        abort(404)
    if link.link_type == "contact":
        return render_template("contact.html", user=user, link=link)
    logic.record_click(link.id)
    return redirect(link.url)


@app.route("/click/<int:link_id>")
def track_click(link_id):
    link = logic.get_link_by_id(link_id)
    if not link or not link.is_active:
        abort(404)
    if link.link_type == "contact":
        from database import get_db, User
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE id=?", (link.user_id,)).fetchone()
        conn.close()
        if not row:
            abort(404)
        return render_template("contact.html", user=User(row), link=link)
    logic.record_click(link_id)
    return redirect(link.url)


@app.route("/contact/<int:link_id>", methods=["GET", "POST"])
def contact_form(link_id):
    link = logic.get_link_by_id(link_id)
    if not link or not link.is_active or link.link_type != "contact":
        abort(404)
    from database import get_db
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id=?", (link.user_id,)).fetchone()
    conn.close()
    if not row:
        abort(404)
    from database import User
    user = User(row)

    if request.method == "POST":
        try:
            logic.submit_contact(
                link_id,
                request.form.get("name", ""),
                request.form.get("email", ""),
                request.form.get("message", ""),
            )
            return render_template("contact.html", user=user, link=link, success=True)
        except Exception as e:
            return render_template(
                "contact.html", user=user, link=link, error=str(e)
            )
    return render_template("contact.html", user=user, link=link)


def start_server():
    t = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False),
        daemon=True,
    )
    t.start()
