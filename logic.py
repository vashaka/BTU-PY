# business logic
import os
import shutil
import bcrypt
import re
from database import Database


def must_be_logged_in(func):
    # decorator for login check
    def wrapper(self, *args, **kwargs):
        if self.logged_in_user == None:
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
        if u == None:
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
        if not url.startswith("http"):
            url = "https://" + url
        return url

    @must_be_logged_in
    def get_my_links(self):
        return self.db.get_links(self.logged_in_user.id)

    @must_be_logged_in
    def add_link(self, title, url, icon=""):
        title = title.strip()
        if not title:
            raise Exception("no title")
        url = self.fix_url(url)
        return self.db.add_link(self.logged_in_user.id, title, url, icon)

    @must_be_logged_in
    def update_link(self, link_id, title, url, icon=""):
        link = self.db.get_link(link_id)
        if not link or link.user_id != self.logged_in_user.id:
            raise Exception("error")
        return self.db.update_link(link_id, title.strip(), self.fix_url(url), icon)

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

    def get_public_profile(self, username):
        u = self.db.get_user_by_name(username)
        if not u:
            return None, []
        links = self.db.get_links(u.id, only_active=True)
        return u, links

    def get_link_by_id(self, link_id):
        return self.db.get_link(link_id)

    def record_click(self, link_id):
        self.db.increment_click(link_id)

    @must_be_logged_in
    def upload_profile_pic(self, source_path):
        if not os.path.exists(source_path):
            return

        # ვქმნით static/uploads საქაღალდეს, თუ არ არსებობს
        target_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
        os.makedirs(target_dir, exist_ok=True)

        # ვიგებთ ფაილის გაფართოებას (.jpg, .png) და ვქმნით ახალ სახელს
        _, ext = os.path.splitext(source_path)
        filename = f"avatar_{self.logged_in_user.id}{ext.lower()}"
        target_path = os.path.join(target_dir, filename)

        # ვაკოპირებთ ფოტოს საჭირო ადგილას
        shutil.copy(source_path, target_path)

        # ვინახავთ სახელს ბაზაში და მიმდინარე სესიაში
        self.db.update_profile_pic(self.logged_in_user.id, filename)
        self.logged_in_user.profile_pic = filename
