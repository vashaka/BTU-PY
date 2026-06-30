# database file for linktree project
import sqlite3
import os
import socket
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "data", "linktree.db")
SERVER_PORT = 5001


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def _migrate(conn):
    cols = {r[1] for r in conn.execute("PRAGMA table_info(links)").fetchall()}
    migrations = [
        ("start_date", "ALTER TABLE links ADD COLUMN start_date TEXT DEFAULT ''"),
        ("end_date", "ALTER TABLE links ADD COLUMN end_date TEXT DEFAULT ''"),
        ("link_type", "ALTER TABLE links ADD COLUMN link_type TEXT DEFAULT 'url'"),
        ("slug", "ALTER TABLE links ADD COLUMN slug TEXT DEFAULT ''"),
        ("group_name", "ALTER TABLE links ADD COLUMN group_name TEXT DEFAULT ''"),
        ("is_pinned", "ALTER TABLE links ADD COLUMN is_pinned INTEGER DEFAULT 0"),
    ]
    for col, sql in migrations:
        if col not in cols:
            conn.execute(sql)

    user_cols = {r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
    if "profile_views" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN profile_views INTEGER DEFAULT 0")

    conn.execute("""CREATE TABLE IF NOT EXISTS click_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_id INTEGER,
        clicked_at TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS profile_view_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        viewed_at TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_id INTEGER,
        sender_name TEXT,
        sender_email TEXT,
        message TEXT,
        created_at TEXT
    )""")


def setup_tables():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            display_name TEXT,
            bio TEXT DEFAULT '',
            profile_pic TEXT DEFAULT '',
            profile_views INTEGER DEFAULT 0
        )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                url TEXT,
                icon TEXT DEFAULT '',
                sort_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                clicks INTEGER DEFAULT 0,
                start_date TEXT DEFAULT '',
                end_date TEXT DEFAULT '',
                link_type TEXT DEFAULT 'url',
                slug TEXT DEFAULT '',
                group_name TEXT DEFAULT '',
                is_pinned INTEGER DEFAULT 0
            )""")
    _migrate(conn)
    conn.commit()
    conn.close()


class User:
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.email = row["email"]
        self.password_hash = row["password_hash"]
        self.display_name = row["display_name"]
        self.bio = row["bio"] or ""
        self.profile_pic = row["profile_pic"] if "profile_pic" in row.keys() else ""
        self.profile_views = row["profile_views"] if "profile_views" in row.keys() else 0

    @property
    def profile_url(self):
        local_ip = get_local_ip()
        return f"http://{local_ip}:{SERVER_PORT}/u/{self.username}"


class Link:
    def __init__(self, row):
        self.id = row["id"]
        self.user_id = row["user_id"]
        self.title = row["title"]
        self.url = row["url"]
        self.icon = row["icon"] if "icon" in row.keys() else ""
        self.sort_order = row["sort_order"]
        self.is_active = bool(row["is_active"])
        self.clicks = row["clicks"] if "clicks" in row.keys() else 0
        self.start_date = row["start_date"] if "start_date" in row.keys() else ""
        self.end_date = row["end_date"] if "end_date" in row.keys() else ""
        self.link_type = row["link_type"] if "link_type" in row.keys() else "url"
        self.slug = row["slug"] if "slug" in row.keys() else ""
        self.group_name = row["group_name"] if "group_name" in row.keys() else ""
        self.is_pinned = bool(row["is_pinned"]) if "is_pinned" in row.keys() else False

    @property
    def slug_url(self):
        if not self.slug:
            return ""
        local_ip = get_local_ip()
        return f"http://{local_ip}:{SERVER_PORT}/u/{{username}}/{self.slug}"


class Database:
    def __init__(self):
        setup_tables()

    def get_user_by_name(self, username):
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE username=?", (username.lower(),)).fetchone()
        conn.close()
        if row:
            return User(row)
        return None

    def get_user_by_email(self, email):
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE email=?", (email.lower(),)).fetchone()
        conn.close()
        if row:
            return User(row)
        return None

    def create_user(self, username, email, pw_hash, display_name):
        conn = get_db()
        cur = conn.execute(
            "INSERT INTO users (username,email,password_hash,display_name) VALUES (?,?,?,?)",
            (username.lower(), email.lower(), pw_hash, display_name),
        )
        uid = cur.lastrowid
        row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        conn.commit()
        conn.close()
        return User(row)

    def update_user_profile(self, user_id, display_name, bio):
        conn = get_db()
        conn.execute("UPDATE users SET display_name=?, bio=? WHERE id=?", (display_name, bio, user_id))
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        conn.commit()
        conn.close()
        return User(row)

    def get_links(self, user_id, only_active=False, apply_schedule=False):
        conn = get_db()
        order = "ORDER BY is_pinned DESC, sort_order ASC"
        if only_active:
            rows = conn.execute(
                f"SELECT * FROM links WHERE user_id=? AND is_active=1 {order}",
                (user_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                f"SELECT * FROM links WHERE user_id=? {order}", (user_id,)
            ).fetchall()
        conn.close()
        links = [Link(r) for r in rows]
        if apply_schedule:
            today = datetime.now().strftime("%Y-%m-%d")
            links = [l for l in links if _link_is_scheduled_visible(l, today)]
        return links

    def add_link(self, user_id, title, url, icon, start_date="", end_date="",
                 link_type="url", slug="", group_name=""):
        conn = get_db()
        mx = conn.execute(
            "SELECT MAX(sort_order) FROM links WHERE user_id=?", (user_id,)
        ).fetchone()[0]
        if mx is None:
            mx = -1
        cur = conn.execute(
            """INSERT INTO links
               (user_id,title,url,icon,sort_order,start_date,end_date,link_type,slug,group_name)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (user_id, title, url, icon, mx + 1, start_date, end_date, link_type, slug, group_name),
        )
        lid = cur.lastrowid
        row = conn.execute("SELECT * FROM links WHERE id=?", (lid,)).fetchone()
        conn.commit()
        conn.close()
        return Link(row)

    def get_link(self, link_id):
        conn = get_db()
        row = conn.execute("SELECT * FROM links WHERE id=?", (link_id,)).fetchone()
        conn.close()
        if row:
            return Link(row)
        return None

    def get_link_by_slug(self, user_id, slug):
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM links WHERE user_id=? AND slug=? AND slug != ''",
            (user_id, slug.lower()),
        ).fetchone()
        conn.close()
        if row:
            return Link(row)
        return None

    def slug_taken(self, user_id, slug, exclude_link_id=None):
        if not slug:
            return False
        conn = get_db()
        if exclude_link_id:
            row = conn.execute(
                "SELECT id FROM links WHERE user_id=? AND slug=? AND id!=?",
                (user_id, slug.lower(), exclude_link_id),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id FROM links WHERE user_id=? AND slug=?",
                (user_id, slug.lower()),
            ).fetchone()
        conn.close()
        return row is not None

    def update_link(self, link_id, title, url, icon, start_date="", end_date="",
                    link_type="url", slug="", group_name=""):
        conn = get_db()
        conn.execute(
            """UPDATE links SET title=?, url=?, icon=?, start_date=?, end_date=?,
               link_type=?, slug=?, group_name=? WHERE id=?""",
            (title, url, icon, start_date, end_date, link_type, slug, group_name, link_id),
        )
        row = conn.execute("SELECT * FROM links WHERE id=?", (link_id,)).fetchone()
        conn.commit()
        conn.close()
        return Link(row)

    def delete_link(self, link_id):
        conn = get_db()
        conn.execute("DELETE FROM links WHERE id=?", (link_id,))
        conn.execute("DELETE FROM click_events WHERE link_id=?", (link_id,))
        conn.execute("DELETE FROM contact_messages WHERE link_id=?", (link_id,))
        conn.commit()
        conn.close()

    def toggle_link(self, link_id):
        conn = get_db()
        row = conn.execute("SELECT is_active FROM links WHERE id=?", (link_id,)).fetchone()
        new_val = 0 if row["is_active"] else 1
        conn.execute("UPDATE links SET is_active=? WHERE id=?", (new_val, link_id))
        conn.commit()
        conn.close()

    def set_link_pinned(self, user_id, link_id, pinned):
        conn = get_db()
        if pinned:
            conn.execute("UPDATE links SET is_pinned=0 WHERE user_id=?", (user_id,))
        conn.execute("UPDATE links SET is_pinned=? WHERE id=? AND user_id=?", (1 if pinned else 0, link_id, user_id))
        conn.commit()
        conn.close()

    def reorder_links(self, user_id, id_list):
        conn = get_db()
        for i, lid in enumerate(id_list):
            conn.execute(
                "UPDATE links SET sort_order=? WHERE id=? AND user_id=?", (i, lid, user_id)
            )
        conn.commit()
        conn.close()

    def increment_click(self, link_id):
        now = datetime.now().isoformat(timespec="seconds")
        conn = get_db()
        conn.execute("UPDATE links SET clicks = clicks + 1 WHERE id=?", (link_id,))
        conn.execute("INSERT INTO click_events (link_id, clicked_at) VALUES (?, ?)", (link_id, now))
        conn.commit()
        conn.close()

    def record_profile_view(self, user_id):
        now = datetime.now().isoformat(timespec="seconds")
        conn = get_db()
        conn.execute("UPDATE users SET profile_views = profile_views + 1 WHERE id=?", (user_id,))
        conn.execute(
            "INSERT INTO profile_view_events (user_id, viewed_at) VALUES (?, ?)", (user_id, now)
        )
        conn.commit()
        conn.close()

    def get_profile_view_count(self, user_id):
        conn = get_db()
        row = conn.execute("SELECT profile_views FROM users WHERE id=?", (user_id,)).fetchone()
        conn.close()
        return row["profile_views"] if row else 0

    def get_clicks_over_time(self, user_id, days=30):
        conn = get_db()
        rows = conn.execute(
            """SELECT date(ce.clicked_at) as day, COUNT(*) as cnt
               FROM click_events ce
               JOIN links l ON l.id = ce.link_id
               WHERE l.user_id=?
                 AND date(ce.clicked_at) >= date('now', ? || ' days')
               GROUP BY date(ce.clicked_at)
               ORDER BY day ASC""",
            (user_id, f"-{int(days)}"),
        ).fetchall()
        conn.close()
        return [(r["day"], r["cnt"]) for r in rows]

    def get_link_click_stats(self, user_id, days=None):
        conn = get_db()
        if days is None:
            rows = conn.execute(
                "SELECT id, title, clicks FROM links WHERE user_id=? ORDER BY clicks DESC",
                (user_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT l.id, l.title, COUNT(ce.id) as clicks
                   FROM links l
                   LEFT JOIN click_events ce ON ce.link_id = l.id
                     AND date(ce.clicked_at) >= date('now', ? || ' days')
                   WHERE l.user_id=?
                   GROUP BY l.id
                   ORDER BY clicks DESC""",
                (f"-{int(days)}", user_id),
            ).fetchall()
        conn.close()
        return [(r["id"], r["title"], r["clicks"]) for r in rows]

    def save_contact_message(self, link_id, sender_name, sender_email, message):
        now = datetime.now().isoformat(timespec="seconds")
        conn = get_db()
        conn.execute(
            "INSERT INTO contact_messages (link_id, sender_name, sender_email, message, created_at) VALUES (?,?,?,?,?)",
            (link_id, sender_name, sender_email, message, now),
        )
        conn.commit()
        conn.close()

    def get_contact_messages(self, user_id, limit=50):
        conn = get_db()
        rows = conn.execute(
            """SELECT cm.*, l.title as link_title
               FROM contact_messages cm
               JOIN links l ON l.id = cm.link_id
               WHERE l.user_id=?
               ORDER BY cm.created_at DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_profile_pic(self, user_id, filename):
        conn = get_db()
        conn.execute("UPDATE users SET profile_pic=? WHERE id=?", (filename, user_id))
        conn.commit()
        conn.close()


def _link_is_scheduled_visible(link, today):
    if link.start_date and link.start_date > today:
        return False
    if link.end_date and link.end_date < today:
        return False
    return True


def group_links(links):
    """Group links by group_name; pinned links appear in a top section."""
    pinned = [l for l in links if l.is_pinned]
    rest = [l for l in links if not l.is_pinned]
    groups = []
    if pinned:
        groups.append({"name": "Pinned", "links": pinned})
    seen = {}
    for link in rest:
        g = link.group_name.strip() if link.group_name else ""
        if g not in seen:
            seen[g] = len(groups)
            groups.append({"name": g, "links": []})
        groups[seen[g]]["links"].append(link)
    return groups
