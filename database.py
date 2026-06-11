# database file for linktree project
import sqlite3
import os
import socket

DB_FILE = os.path.join(os.path.dirname(__file__), "data", "linktree.db")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # ვცდილობთ დავუკავშირდეთ Google-ის სერვერს, რათა ჩვენი რეალური შიდა IP გავიგოთ
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_tables():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            display_name TEXT,
            bio TEXT DEFAULT '',
            profile_pic TEXT DEFAULT ''
        )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                url TEXT,
                icon TEXT DEFAULT '',
                sort_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                clicks INTEGER DEFAULT 0
            )""")
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

    @property
    def profile_url(self):
        local_ip = get_local_ip()
        return f"http://{local_ip}:5000/u/{self.username}"


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


class Database:
    # main db class
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

    def get_links(self, user_id, only_active=False):
        conn = get_db()
        if only_active:
            rows = conn.execute(
                "SELECT * FROM links WHERE user_id=? AND is_active=1 ORDER BY sort_order",
                (user_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM links WHERE user_id=? ORDER BY sort_order", (user_id,)
            ).fetchall()
        conn.close()
        return [Link(r) for r in rows]

    def add_link(self, user_id, title, url, icon):
        conn = get_db()
        mx = conn.execute(
            "SELECT MAX(sort_order) FROM links WHERE user_id=?", (user_id,)
        ).fetchone()[0]
        if mx is None:
            mx = -1
        cur = conn.execute(
            "INSERT INTO links (user_id,title,url,icon,sort_order) VALUES (?,?,?,?,?)",
            (user_id, title, url, icon, mx + 1),
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

    def update_link(self, link_id, title, url, icon):
        conn = get_db()
        conn.execute("UPDATE links SET title=?, url=?, icon=? WHERE id=?", (title, url, icon, link_id))
        row = conn.execute("SELECT * FROM links WHERE id=?", (link_id,)).fetchone()
        conn.commit()
        conn.close()
        return Link(row)

    def delete_link(self, link_id):
        conn = get_db()
        conn.execute("DELETE FROM links WHERE id=?", (link_id,))
        conn.commit()
        conn.close()

    def toggle_link(self, link_id):
        conn = get_db()
        row = conn.execute("SELECT is_active FROM links WHERE id=?", (link_id,)).fetchone()
        new_val = 0 if row["is_active"] else 1
        conn.execute("UPDATE links SET is_active=? WHERE id=?", (new_val, link_id))
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
        conn = get_db()
        conn.execute("UPDATE links SET clicks = clicks + 1 WHERE id=?", (link_id,))
        conn.commit()
        conn.close()

    def update_profile_pic(self, user_id, filename):
        conn = get_db()
        conn.execute("UPDATE users SET profile_pic=? WHERE id=?", (filename, user_id))
        conn.commit()
        conn.close()
