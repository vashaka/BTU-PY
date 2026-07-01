# business logic
import os
import shutil
import ssl
import bcrypt
import re
import certifi
import urllib.request
import urllib.error
from database import Database, group_links


def must_be_logged_in(func):
    def wrapper(self, *args, **kwargs):
        if self.logged_in_user is None:
            raise Exception("not logged in")
        return func(self, *args, **kwargs)

    return wrapper


class AppLogic:
    def __init__(self):
        self.db = Database()
        self.logged_in_user = None

    @property
    def current_user(self):
        return self.logged_in_user

    def hash_pw(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_pw(self, password, h):
        return bcrypt.checkpw(password.encode(), h.encode())

    def register(self, username, email, password, display_name):
        username = username.strip().lower()
        email = email.strip().lower()
        display_name = display_name.strip()

        # 1. სიცარიელის შემოწმება
        if not username:
            raise Exception("username empty")
        if not email:
            raise Exception("email empty")
        if not password or not password.strip():
            raise Exception("password empty")
        if not display_name:
            raise Exception("need name")

        # 2. იუზერნეიმის ვალიდაცია
        if len(username) < 3:
            raise Exception("username bad")
        if len(username) > 20:
            raise Exception("username too long")
        # ნებადართულია მხოლოდ ლათინური ასოები, ციფრები და ქვედა ტირე (_)
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise Exception("username format bad")

        # 3. მეილის ვალიდაცია
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            raise Exception("invalid email")

        # 4. პაროლის ვალიდაცია (მინ. 8 სიმბოლო და 1 ციფრი)
        if len(password) < 8 or not re.search(r"\d", password):
            raise Exception("password weak")

        # 5. საჩვენებელი სახელის ვალიდაცია
        if len(display_name) > 50:
            raise Exception("display name too long")

        # 6. ბაზაში არსებობის შემოწმება
        if self.db.get_user_by_name(username):
            raise Exception("username taken")
        if self.db.get_user_by_email(email):
            raise Exception("email taken")

        # თუ ყველაფერი სწორია, იქმნება მომხმარებელი
        u = self.db.create_user(username, email, self.hash_pw(password), display_name)
        self.logged_in_user = u
        return u

    def login(self, username, password):
        username = username.strip()
        password = password.strip()

        # ველების სიცარიელის შემოწმება
        if not username or not password:
            raise Exception("empty fields")

        u = self.db.get_user_by_name(username.lower())
        if u is None:
            raise Exception("wrong login")
        if not self.check_pw(password, u.password_hash):
            raise Exception("wrong login")
        self.logged_in_user = u
        return u

    def logout(self):
        self.logged_in_user = None

    def update_profile(self, display_name, bio):
        if not self.logged_in_user:
            raise Exception("login first")
        if not display_name.strip():
            raise Exception("bad name")
        self.logged_in_user = self.db.update_user_profile(
            self.logged_in_user.id, display_name.strip(), bio
        )

    def fix_url(self, url):
        url = url.strip()
        if not url:
            return ""
        if not url.startswith("http"):
            url = "https://" + url
        return url

    def validate_url_live(self, url):
        url = self.fix_url(url)
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (LinkVerse URL check)"}
        )
        ctx = ssl.create_default_context(cafile=certifi.where())
        try:
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                if resp.status != 200:
                    raise Exception("url not 200")
        except urllib.error.HTTPError as e:
            if e.code != 200:
                raise Exception("url not 200")
        except Exception:
            raise Exception("url unreachable")
        return url

    def validate_slug(self, slug):
        slug = slug.strip().lower()
        if not slug:
            return ""
        if not re.match(r"^[a-z0-9_-]+$", slug):
            raise Exception("slug format bad")
        if len(slug) > 30:
            raise Exception("slug too long")
        return slug

    def _validate_link_fields(self, title, url, link_type, slug, exclude_link_id=None):
        title = title.strip()
        if not title:
            raise Exception("no title")
        slug = self.validate_slug(slug)
        if slug and self.db.slug_taken(self.logged_in_user.id, slug, exclude_link_id):
            raise Exception("slug taken")
        if link_type == "url" and not url.strip():
            raise Exception("no url")
        if link_type not in ("url", "contact"):
            raise Exception("bad link type")
        fixed = self.fix_url(url) if link_type == "url" else ""
        if link_type == "url":
            fixed = self.validate_url_live(fixed)
        return title, fixed, slug

    @must_be_logged_in
    def get_my_links(self):
        return self.db.get_links(self.logged_in_user.id)

    @must_be_logged_in
    def add_link(
        self,
        title,
        url,
        icon="",
        start_date="",
        end_date="",
        link_type="url",
        slug="",
        group_name="",
    ):
        title, url, slug = self._validate_link_fields(title, url, link_type, slug)
        return self.db.add_link(
            self.logged_in_user.id,
            title,
            url,
            icon,
            start_date.strip(),
            end_date.strip(),
            link_type,
            slug,
            group_name.strip(),
        )

    @must_be_logged_in
    def update_link(
        self,
        link_id,
        title,
        url,
        icon="",
        start_date="",
        end_date="",
        link_type="url",
        slug="",
        group_name="",
    ):
        link = self.db.get_link(link_id)
        if not link or link.user_id != self.logged_in_user.id:
            raise Exception("error")
        title, url, slug = self._validate_link_fields(
            title, url, link_type, slug, link_id
        )
        return self.db.update_link(
            link_id,
            title,
            url,
            icon,
            start_date.strip(),
            end_date.strip(),
            link_type,
            slug,
            group_name.strip(),
        )

    @must_be_logged_in
    def toggle_link(self, link_id):
        link = self.db.get_link(link_id)
        if not link or link.user_id != self.logged_in_user.id:
            raise Exception("error")
        self.db.toggle_link(link_id)

    @must_be_logged_in
    def delete_link(self, link_id):
        link = self.db.get_link(link_id)
        if not link or link.user_id != self.logged_in_user.id:
            raise Exception("error")
        self.db.delete_link(link_id)

    @must_be_logged_in
    def move_link(self, link_id, direction):
        links = self.db.get_links(self.logged_in_user.id)
        ids = [l.id for l in links]
        if link_id not in ids:
            raise Exception("error")
        idx = ids.index(link_id)
        if direction == "up" and idx > 0:
            ids[idx], ids[idx - 1] = ids[idx - 1], ids[idx]
        elif direction == "down" and idx < len(ids) - 1:
            ids[idx], ids[idx + 1] = ids[idx + 1], ids[idx]
        self.db.reorder_links(self.logged_in_user.id, ids)

    @must_be_logged_in
    def toggle_pin(self, link_id):
        link = self.db.get_link(link_id)
        if not link or link.user_id != self.logged_in_user.id:
            raise Exception("error")
        self.db.set_link_pinned(self.logged_in_user.id, link_id, not link.is_pinned)

    def get_public_profile(self, username, record_view=False):
        u = self.db.get_user_by_name(username)
        if not u:
            return None, []
        if record_view:
            self.db.record_profile_view(u.id)
            u = self.db.get_user_by_name(username)
        links = self.db.get_links(u.id, only_active=True, apply_schedule=True)
        return u, links

    def get_public_profile_grouped(self, username, record_view=False):
        u, links = self.get_public_profile(username, record_view=record_view)
        if not u:
            return None, []
        return u, group_links(links)

    def get_link_by_slug(self, username, slug):
        u = self.db.get_user_by_name(username)
        if not u:
            return None, None
        link = self.db.get_link_by_slug(u.id, slug)
        if not link or not link.is_active:
            return u, None
        from database import _link_is_scheduled_visible
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        if not _link_is_scheduled_visible(link, today):
            return u, None
        return u, link

    def get_link_by_id(self, link_id):
        return self.db.get_link(link_id)

    def record_click(self, link_id):
        self.db.increment_click(link_id)

    def submit_contact(self, link_id, sender_name, sender_email, message):
        link = self.db.get_link(link_id)
        if not link or not link.is_active or link.link_type != "contact":
            raise Exception("invalid contact link")
        sender_name = sender_name.strip()
        sender_email = sender_email.strip()
        message = message.strip()
        if not sender_name or not sender_email or not message:
            raise Exception("empty fields")
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", sender_email):
            raise Exception("invalid email")
        self.db.save_contact_message(link_id, sender_name, sender_email, message)

    @must_be_logged_in
    def get_analytics(self, days=30):
        uid = self.logged_in_user.id
        profile_views = self.db.get_profile_view_count(uid)
        link_stats = self.db.get_link_click_stats(uid, days=days)
        most_popular = link_stats[0] if link_stats and link_stats[0][2] > 0 else None
        clicks_over_time = self.db.get_clicks_over_time(uid, days=days)
        return {
            "profile_views": profile_views,
            "link_stats": link_stats,
            "most_popular": most_popular,
            "clicks_over_time": clicks_over_time,
            "days": days,
        }

    @must_be_logged_in
    def get_contact_inbox(self):
        return self.db.get_contact_messages(self.logged_in_user.id)

    @must_be_logged_in
    def upload_profile_pic(self, source_path):
        if not os.path.exists(source_path):
            return

        target_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
        os.makedirs(target_dir, exist_ok=True)

        _, ext = os.path.splitext(source_path)
        filename = f"avatar_{self.logged_in_user.id}{ext.lower()}"
        target_path = os.path.join(target_dir, filename)

        shutil.copy(source_path, target_path)

        self.db.update_profile_pic(self.logged_in_user.id, filename)
        self.logged_in_user.profile_pic = filename
