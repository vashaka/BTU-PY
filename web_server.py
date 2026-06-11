# flask part for public pages
import threading
from flask import Flask, render_template, abort, redirect
from logic import AppLogic

logic = AppLogic()  # separate instance for web lol

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/u/<username>")
def profile(username):
    user, links = logic.get_public_profile(username)
    if user == None:
        abort(404)
    return render_template("profile.html", user=user, links=links)

@app.route("/click/<int:link_id>")
def track_click(link_id):
    link = logic.get_link_by_id(link_id)
    if not link or not link.is_active:
        abort(404)
    logic.record_click(link_id)
    return redirect(link.url)

def start_server():
    t = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False),
        daemon=True,
    )
    t.start()
