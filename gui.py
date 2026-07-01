# pyqt gui stuff
import os
import io
import qrcode
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QPixmap, QImage
from PyQt6.QtWidgets import *
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from themes import apply_theme


def _btn(widget, role="default"):
    widget.setProperty("btnRole", role)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    return widget


def _lbl(widget, role=""):
    if role:
        widget.setProperty("role", role)
    return widget


class LoginPage(QWidget):
    done = pyqtSignal()
    go_register = pyqtSignal()

    def __init__(self, logic):
        super().__init__()
        self.logic = logic

        # მთავარი Layout - ყველაფერს სვამს ფანჯრის ცენტრში
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setMaximumWidth(440)
        container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        # სათაური
        self.title = _lbl(QLabel("Sign in"), "pageTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)

        # ერორების ლეიბლი
        self.err = _lbl(QLabel(""), "error")
        self.err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.err)

        self.btn_login = _btn(QPushButton("Sign in"), "primary")
        self.btn_login.clicked.connect(self.do_login)
        layout.addWidget(self.btn_login)

        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_ask = _lbl(QLabel("Don't have an account?"), "muted")

        self.btn_go_register = _btn(QPushButton("Register"), "link")
        self.btn_go_register.clicked.connect(self.go_register.emit)

        register_layout.addWidget(lbl_ask)
        register_layout.addWidget(self.btn_go_register)
        layout.addLayout(register_layout)

        outer.addWidget(container)

    def do_login(self):
        self.err.setText("")
        try:
            self.logic.login(self.user_input.text(), self.pass_input.text())
            self.done.emit()
        except Exception as e:
            if "empty fields" in str(e):
                self.err.setText("გთხოვთ შეავსოთ ყველა ველი!")
            else:
                self.err.setText("არასწორი მომხმარებელი ან პაროლი!")

    def clear(self):
        self.user_input.clear()
        self.pass_input.clear()
        self.err.clear()


class RegisterPage(QWidget):
    done = pyqtSignal()
    go_login = pyqtSignal()

    def __init__(self, logic):
        super().__init__()
        self.logic = logic

        # მთავარი Layout (ელემენტების ცენტრში მოსაქცევად)
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setMaximumWidth(440)
        container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        main_layout = QVBoxLayout(container)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(40, 80, 40, 80)
        main_layout.setSpacing(12)

        # 1. სათაური "Create account"
        self.title = _lbl(QLabel("Create account"), "pageTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Name")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.pw = QLineEdit()
        self.pw.setPlaceholderText("Password")
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username (@handle)")

        main_layout.addWidget(self.name)
        main_layout.addWidget(self.email)
        main_layout.addWidget(self.pw)
        main_layout.addWidget(self.user)

        # ერორების გამოსატანი ლეიბლი (რომელსაც შენი do_reg ფუნქცია იყენებს)
        self.err = _lbl(QLabel(""), "error")
        self.err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.err)

        self.btn_register = _btn(QPushButton("Create account"), "primary")
        self.btn_register.clicked.connect(self.do_reg)
        main_layout.addWidget(self.btn_register)

        login_layout = QHBoxLayout()
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_ask = _lbl(QLabel("Already have an account?"), "muted")

        self.btn_go_login = _btn(QPushButton("Log in"), "link")
        self.btn_go_login.clicked.connect(self.go_login.emit)

        login_layout.addWidget(lbl_ask)
        login_layout.addWidget(self.btn_go_login)
        main_layout.addLayout(login_layout)

        outer.addWidget(container)

    def do_reg(self):
        self.err.setText("")
        try:
            self.logic.register(
                self.user.text(), self.email.text(), self.pw.text(), self.name.text()
            )
            self.done.emit()
        except Exception as e:
            err_msg = str(e)

            # თითოეულ შეცდომას ვუსადაგებთ ქართულ შესაბამის ტექსტს
            if "username empty" in err_msg:
                self.err.setText("მომხმარებლის სახელი ცარიელია!")
            elif "username bad" in err_msg:
                self.err.setText("მომხმარებლის სახელი უნდა იყოს მინ. 3 სიმბოლო!")
            elif "username too long" in err_msg:
                self.err.setText("მომხმარებლის სახელი ზედმეტად გრძელია (მაქს. 20)!")
            elif "username format bad" in err_msg:
                self.err.setText(
                    "სახელი უნდა შეიცავდეს მხოლოდ ლათინურ ასოებს, ციფრებს ან _"
                )
            elif "email empty" in err_msg:
                self.err.setText("ელ-ფოსტის ველი ცარიელია!")
            elif "invalid email" in err_msg:
                self.err.setText("არასწორი მეილის ფორმატი!")
            elif "password empty" in err_msg:
                self.err.setText("პაროლის ველი ცარიელია!")
            elif "password weak" in err_msg:
                self.err.setText("პაროლი სუსტია (მინ. 8 სიმბოლო, 1 ციფრი)!")
            elif "need name" in err_msg:
                self.err.setText("საჩვენებელი სახელი ცარიელია!")
            elif "display name too long" in err_msg:
                self.err.setText("სახელი ზედმეტად გრძელია (მაქს. 50)!")
            elif "username taken" in err_msg:
                self.err.setText("ეს მომხმარებლის სახელი უკვე დაკავებულია!")
            elif "email taken" in err_msg:
                self.err.setText("ეს ელ-ფოსტა უკვე დარეგისტრირებულია!")
            else:
                self.err.setText("დაფიქსირდა შეცდომა რეგისტრაციისას!")

    def clear(self):
        self.name.clear()
        self.user.clear()
        self.email.clear()
        self.pw.clear()
        self.err.clear()


class DashboardPage(QWidget):
    logged_out = pyqtSignal()
    go_analytics = pyqtSignal()

    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.selected_id = None

        # მთავარი მაკეტი (Layout)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        content_widget = QWidget()
        content_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        layout = QVBoxLayout(content_widget)
        layout.setSpacing(6)  # მჭიდრო დაშორება ელემენტებს შორის
        layout.setContentsMargins(0, 0, 0, 0)

        # --- 1. ზედა ზოლი (Dark Mode და Logout) ---
        top_layout = QHBoxLayout()
        self.btn_analytics = _btn(QPushButton("Analytics"), "chip")
        self.btn_analytics.clicked.connect(self.go_analytics.emit)

        self.logout_btn = _btn(QPushButton("Log out"), "ghost")
        self.logout_btn.clicked.connect(self.logout)

        top_layout.addWidget(self.btn_analytics)
        top_layout.addStretch()
        top_layout.addWidget(self.logout_btn)
        layout.addLayout(top_layout)

        share_lbl = _lbl(QLabel("Your public profile:"), "muted")
        layout.addWidget(share_lbl)

        share_layout = QHBoxLayout()
        self.share_box = QLineEdit()
        self.share_box.setReadOnly(True)

        copyb = _btn(QPushButton("Copy"), "primary")
        copyb.clicked.connect(self.copy_url)
        share_layout.addWidget(self.share_box)
        share_layout.addWidget(copyb)
        layout.addLayout(share_layout)

        # 🌟 ვქმნით კონტეინერს QR კოდისთვის
        qr_container = QHBoxLayout()
        qr_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_container.setContentsMargins(
            0, 0, 0, 0
        )  # 👈 აშორებს შიდა დაშორებებს, რაც მაღლა სწევს კოდს

        self.qr_label = QLabel()
        self.qr_label.setMinimumSize(120, 120)
        self.qr_label.setMaximumSize(180, 180)
        self.qr_label.setScaledContents(True)

        qr_container.addWidget(self.qr_label)
        layout.addLayout(qr_container)

        # --- 3. PROFILE სექცია ---
        lbl_prof = _lbl(QLabel("Profile Settings"), "sectionTitle")
        layout.addWidget(lbl_prof)

        avatar_layout = QHBoxLayout()
        avatar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.avatar_label = _lbl(QLabel(), "avatar")
        self.avatar_label.setMinimumSize(80, 80)
        self.avatar_label.setMaximumSize(140, 140)
        self.avatar_label.setScaledContents(True)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_pic = _btn(QPushButton("Change Photo"), "secondary")
        self.btn_pic.clicked.connect(self.choose_profile_pic)

        avatar_layout.addWidget(self.avatar_label)
        avatar_layout.addSpacing(10)
        avatar_layout.addWidget(self.btn_pic)
        layout.addLayout(avatar_layout)

        self.disp_name = QLineEdit()
        self.disp_name.setPlaceholderText("Display Name")
        layout.addWidget(self.disp_name)

        self.bio = QTextEdit()
        self.bio.setPlaceholderText("Bio...")
        self.bio.setMinimumHeight(40)
        self.bio.setMaximumHeight(120)
        layout.addWidget(self.bio)

        sp = _btn(QPushButton("Save Profile"), "primary")
        sp.clicked.connect(self.save_profile)
        layout.addWidget(sp)

        lbl_links = _lbl(QLabel("Manage Links"), "sectionTitle")
        layout.addWidget(lbl_links)

        self.list = QListWidget()
        self.list.setMinimumHeight(80)
        self.list.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.list.currentItemChanged.connect(self.pick_link)
        layout.addWidget(self.list)

        self.link_title = QLineEdit()
        self.link_title.setPlaceholderText("Link Title (e.g., GitHub)")
        layout.addWidget(self.link_title)

        self.link_url = QLineEdit()
        self.link_url.setPlaceholderText("URL (https://...)")
        layout.addWidget(self.link_url)

        self.link_icon = QComboBox()
        self.link_icon.addItems(
            [
                "Default",
                "Facebook",
                "Instagram",
                "Twitter",
                "GitHub",
                "YouTube",
                "LinkedIn",
            ]
        )
        layout.addWidget(self.link_icon)

        self.link_type = QComboBox()
        self.link_type.addItems(["URL", "Contact"])
        self.link_type.currentTextChanged.connect(self._on_link_type_changed)
        layout.addWidget(self.link_type)

        self.link_slug = QLineEdit()
        self.link_slug.setPlaceholderText("Custom slug (e.g. github) → /u/you/github")
        layout.addWidget(self.link_slug)

        self.link_group = QLineEdit()
        self.link_group.setPlaceholderText("Group / Section (e.g. Social, Work)")
        layout.addWidget(self.link_group)

        sched_row = QHBoxLayout()
        self.link_start = QLineEdit()
        self.link_start.setPlaceholderText("Start YYYY-MM-DD")
        self.link_end = QLineEdit()
        self.link_end.setPlaceholderText("End YYYY-MM-DD")
        sched_row.addWidget(self.link_start)
        sched_row.addWidget(self.link_end)
        layout.addLayout(sched_row)

        # მართვის ღილაკები (რიგი 1)
        row = QHBoxLayout()
        row.setSpacing(5)
        self.btn_add = _btn(QPushButton("Add"), "secondary")
        self.btn_add.clicked.connect(self.add_link)

        self.btn_upd = _btn(QPushButton("Update"), "secondary")
        self.btn_upd.setEnabled(False)
        self.btn_upd.clicked.connect(self.upd_link)

        self.btn_hide = _btn(QPushButton("Hide/Show"), "secondary")
        self.btn_hide.setEnabled(False)
        self.btn_hide.clicked.connect(self.tog_link)

        self.btn_del = _btn(QPushButton("Delete"), "danger")
        self.btn_del.setEnabled(False)
        self.btn_del.clicked.connect(self.del_link)

        self.btn_pin = _btn(QPushButton("Pin"), "secondary")
        self.btn_pin.setEnabled(False)
        self.btn_pin.clicked.connect(self.pin_link)

        row.addWidget(self.btn_add)
        row.addWidget(self.btn_upd)
        row.addWidget(self.btn_hide)
        row.addWidget(self.btn_pin)
        row.addWidget(self.btn_del)
        layout.addLayout(row)

        # გადაადგილების ღილაკები (რიგი 2)
        row2 = QHBoxLayout()
        row2.setSpacing(5)
        up = _btn(QPushButton("Move Up ↑"), "secondary")
        up.clicked.connect(lambda: self.move("up"))

        dn = _btn(QPushButton("Move Down ↓"), "secondary")
        dn.clicked.connect(lambda: self.move("down"))

        row2.addWidget(up)
        row2.addWidget(dn)
        layout.addLayout(row2)

        self.msg = _lbl(QLabel(""), "success")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.msg)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll, 1)

        self.refresh()

    def _on_link_type_changed(self, text):
        self.link_url.setEnabled(text == "URL")
        if text == "Contact":
            self.link_url.setPlaceholderText("(not needed for contact links)")
        else:
            self.link_url.setPlaceholderText("URL (https://...)")

    def _link_kwargs(self):
        lt = "contact" if self.link_type.currentText() == "Contact" else "url"
        return {
            "start_date": self.link_start.text().strip(),
            "end_date": self.link_end.text().strip(),
            "link_type": lt,
            "slug": self.link_slug.text().strip(),
            "group_name": self.link_group.text().strip(),
        }

    def _clear_link_form(self):
        self.link_title.clear()
        self.link_url.clear()
        self.link_icon.setCurrentIndex(0)
        self.link_type.setCurrentIndex(0)
        self.link_slug.clear()
        self.link_group.clear()
        self.link_start.clear()
        self.link_end.clear()

    def refresh(self):
        u = self.logic.current_user
        if not u:
            return

        if u.profile_pic:
            img_path = os.path.join(
                os.path.dirname(__file__), "static", "uploads", u.profile_pic
            )
            if os.path.exists(img_path):
                self.avatar_label.setPixmap(QPixmap(img_path))
            else:
                self.avatar_label.setText("No Pic")
        else:
            self.avatar_label.setText("No Pic")

        self.share_box.setText(u.profile_url)
        self.disp_name.setText(u.display_name)
        self.bio.setPlainText(u.bio)

        # QR კოდის გენერაცია
        try:
            qr = qrcode.QRCode(version=1, box_size=4, border=1)
            qr.add_data(u.profile_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # გადავიყვანოთ სურათი PyQt-ის ფორმატში დისკზე შენახვის გარეშე
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qimg = QImage()
            qimg.loadFromData(buf.getvalue(), "PNG")

            self.qr_label.setPixmap(QPixmap.fromImage(qimg))
        except Exception as e:
            self.qr_label.setText("QR Code generation failed")

        self.reload_list()

    def reload_list(self):
        self.list.clear()
        try:
            for link in self.logic.get_my_links():
                txt = link.title
                if link.is_pinned:
                    txt = "📌 " + txt
                if not link.is_active:
                    txt += " (off)"
                if link.link_type == "contact":
                    txt += " [contact]"
                if link.group_name:
                    txt += f" [{link.group_name}]"
                if link.slug:
                    txt += f" /{link.slug}"
                if link.start_date or link.end_date:
                    txt += f" ({link.start_date or '...'} → {link.end_date or '...'})"
                txt += f"  [ 👁 {link.clicks} ]"
                detail = link.url if link.link_type == "url" else "contact form"
                item = QListWidgetItem(txt + " - " + detail)
                item.setData(Qt.ItemDataRole.UserRole, link.id)
                self.list.addItem(item)
        except Exception as e:
            print(e)

    def pick_link(self, item, prev):
        if item is None:
            self.selected_id = None
            self.btn_upd.setEnabled(False)
            self.btn_hide.setEnabled(False)
            self.btn_del.setEnabled(False)
            self.btn_pin.setEnabled(False)
            return
        self.selected_id = item.data(Qt.ItemDataRole.UserRole)
        self.btn_upd.setEnabled(True)
        self.btn_hide.setEnabled(True)
        self.btn_del.setEnabled(True)
        self.btn_pin.setEnabled(True)
        for link in self.logic.get_my_links():
            if link.id == self.selected_id:
                self.btn_pin.setText("Unpin" if link.is_pinned else "Pin")
                self.link_title.setText(link.title)
                self.link_url.setText(link.url)
                self.link_icon.setCurrentText(link.icon if link.icon else "Default")
                self.link_type.setCurrentText(
                    "Contact" if link.link_type == "contact" else "URL"
                )
                self.link_slug.setText(link.slug or "")
                self.link_group.setText(link.group_name or "")
                self.link_start.setText(link.start_date or "")
                self.link_end.setText(link.end_date or "")

    def copy_url(self):
        QApplication.clipboard().setText(self.share_box.text())
        self.msg.setText("copied")

    def save_profile(self):
        try:
            self.logic.update_profile(self.disp_name.text(), self.bio.toPlainText())
            self.msg.setText("saved")
        except:
            self.msg.setText("fail")

    def add_link(self):
        try:
            self.logic.add_link(
                self.link_title.text(),
                self.link_url.text(),
                self.link_icon.currentText(),
                **self._link_kwargs(),
            )
            self._clear_link_form()
            self.reload_list()
            self.msg.setText("added")
        except Exception as e:
            self.msg.setText(self._link_err(e))

    def _link_err(self, e):
        err = str(e)
        if "url not 200" in err:
            return "URL did not return HTTP 200"
        if "url unreachable" in err:
            return "URL is unreachable"
        if "slug" in err or "url" in err:
            return err
        return "fail"

    def upd_link(self):
        if self.selected_id is None:
            return
        try:
            self.logic.update_link(
                self.selected_id,
                self.link_title.text(),
                self.link_url.text(),
                self.link_icon.currentText(),
                **self._link_kwargs(),
            )
            self.reload_list()
            self.msg.setText("updated")
        except Exception as e:
            self.msg.setText(self._link_err(e))

    def pin_link(self):
        if self.selected_id is None:
            return
        try:
            self.logic.toggle_pin(self.selected_id)
            self.reload_list()
            for link in self.logic.get_my_links():
                if link.id == self.selected_id:
                    self.btn_pin.setText("Unpin" if link.is_pinned else "Pin")
            self.msg.setText("pin updated")
        except Exception:
            self.msg.setText("fail")

    def tog_link(self):
        try:
            self.logic.toggle_link(self.selected_id)
            self.reload_list()
        except:
            self.msg.setText("fail")

    def del_link(self):
        r = QMessageBox.question(
            self,
            "?",
            "delete?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return
        try:
            self.logic.delete_link(self.selected_id)
            self.selected_id = None
            self._clear_link_form()
            self.reload_list()
        except:
            self.msg.setText("fail")

    def move(self, d):
        if self.selected_id == None:
            return
        try:
            self.logic.move_link(self.selected_id, d)
            self.reload_list()
        except:
            pass

    def choose_profile_pic(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.logic.upload_profile_pic(file_path)
            self.refresh()

    def logout(self):
        self.logic.logout()
        self.logged_out.emit()


class AnalyticsPage(QWidget):
    go_back = pyqtSignal()

    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.analytics_days = 30
        self._last_stats = []
        self._last_over_time = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        content = QWidget()
        content.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout = QVBoxLayout(content)
        layout.setSpacing(10)

        top = QHBoxLayout()
        back_btn = _btn(QPushButton("← Dashboard"), "link")
        back_btn.clicked.connect(self.go_back.emit)
        title = _lbl(QLabel("Analytics"), "sectionTitle")
        top.addWidget(back_btn)
        top.addStretch()
        top.addWidget(title)
        top.addStretch()
        layout.addLayout(top)

        self.views_lbl = _lbl(QLabel(), "stat")
        layout.addWidget(self.views_lbl)

        self.popular_lbl = _lbl(QLabel(), "substat")
        layout.addWidget(self.popular_lbl)

        filter_row = QHBoxLayout()
        filter_row.addWidget(_lbl(QLabel("Date range:"), "muted"))
        self.days_combo = QComboBox()
        self.days_combo.addItems(["Last 7 days", "Last 30 days", "Last 90 days"])
        self.days_combo.setCurrentIndex(1)
        self.days_combo.currentIndexChanged.connect(self._on_days_changed)
        filter_row.addWidget(self.days_combo)
        filter_row.addStretch()
        self.btn_export = _btn(QPushButton("Export PNG"), "primary")
        self.btn_export.clicked.connect(self.export_png)
        filter_row.addWidget(self.btn_export)
        layout.addLayout(filter_row)

        lbl1 = _lbl(QLabel("Clicks per link"), "sectionTitle")
        layout.addWidget(lbl1)

        self.link_chart_fig = Figure(figsize=(5, 3), dpi=100)
        self.link_chart_fig.subplots_adjust(
            left=0.28, right=0.95, top=0.92, bottom=0.12
        )
        self.link_chart_canvas = FigureCanvas(self.link_chart_fig)
        self.link_chart_canvas.setMinimumHeight(180)
        self.link_chart_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.link_chart_canvas)

        self.time_lbl = _lbl(QLabel("Clicks over time (last 30 days)"), "sectionTitle")
        layout.addWidget(self.time_lbl)

        self.time_table = QTableWidget(0, 2)
        self.time_table.setHorizontalHeaderLabels(["Date", "Clicks"])
        self.time_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.time_table.setMinimumHeight(100)
        self.time_table.verticalHeader().setVisible(False)
        self.time_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.time_table)

        lbl3 = _lbl(QLabel("Contact inbox"), "sectionTitle")
        layout.addWidget(lbl3)

        self.inbox = QListWidget()
        self.inbox.setMinimumHeight(80)
        layout.addWidget(self.inbox)

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

    def _on_days_changed(self, index):
        self.analytics_days = [7, 30, 90][index]
        self.refresh()

    def refresh(self):
        try:
            data = self.logic.get_analytics(days=self.analytics_days)
        except Exception:
            return

        days = data["days"]
        self.time_lbl.setText(f"Clicks over time (last {days} days)")

        self.views_lbl.setText(f"Total profile views: {data['profile_views']}")

        if data["most_popular"]:
            _, title, clicks = data["most_popular"]
            self.popular_lbl.setText(
                f"Most popular link ({days}d): {title} ({clicks} clicks)"
            )
        else:
            self.popular_lbl.setText(f"Most popular link ({days}d): —")

        stats = data["link_stats"]
        self._last_stats = stats
        self._update_link_chart(stats)

        over_time = data["clicks_over_time"]
        self._last_over_time = over_time
        self.time_table.setRowCount(len(over_time))
        for i, (day, cnt) in enumerate(over_time):
            self.time_table.setItem(i, 0, QTableWidgetItem(day or ""))
            self.time_table.setItem(i, 1, QTableWidgetItem(str(cnt)))

        self.inbox.clear()
        for msg in self.logic.get_contact_inbox():
            txt = f"{msg['created_at'][:10]} | {msg['link_title']}: {msg['sender_name']} — {msg['message'][:60]}"
            self.inbox.addItem(txt)

    def _update_link_chart(self, stats):
        dark = getattr(self.window(), "is_dark", False)
        bg = "#1e293b" if dark else "#ffffff"
        fg = "#f1f5f9" if dark else "#0f172a"
        grid = "#475569" if dark else "#e5e7eb"
        bar_color = "#2dd4bf" if dark else "#0d9488"

        self.link_chart_fig.clear()
        n = max(len(stats), 1)
        height = max(2.0, min(6.0, 0.45 * n + 1.2))
        self.link_chart_fig.set_size_inches(5, height)

        ax = self.link_chart_fig.add_subplot(111)
        ax.set_facecolor(bg)
        self.link_chart_fig.patch.set_facecolor(bg)

        if not stats:
            ax.text(
                0.5,
                0.5,
                "No link data yet",
                ha="center",
                va="center",
                transform=ax.transAxes,
                color=fg,
                fontsize=12,
            )
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
        else:
            ordered = sorted(stats, key=lambda x: x[2])
            titles = [t[:22] + ("…" if len(t) > 22 else "") for _, t, _ in ordered]
            clicks = [c for _, _, c in ordered]

            bars = ax.barh(titles, clicks, color=bar_color, height=0.6)
            ax.set_xlabel("Clicks", color=fg, fontsize=10)
            ax.tick_params(colors=fg, labelsize=9)
            ax.grid(axis="x", color=grid, linestyle="--", linewidth=0.6, alpha=0.7)
            ax.set_axisbelow(True)
            for spine in ax.spines.values():
                spine.set_color(grid)

            for bar, count in zip(bars, clicks):
                offset = max(max(clicks), 1) * 0.02
                ax.text(
                    bar.get_width() + offset,
                    bar.get_y() + bar.get_height() / 2,
                    str(count),
                    va="center",
                    ha="left",
                    color=fg,
                    fontsize=9,
                )

        self.link_chart_canvas.draw()

    def export_png(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export analytics", "analytics.png", "PNG images (*.png)"
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        try:
            user = self.logic.current_user
            name = user.username if user else "user"
            self.link_chart_fig.savefig(
                path,
                dpi=150,
                bbox_inches="tight",
                facecolor=self.link_chart_fig.patch.get_facecolor(),
            )
            QMessageBox.information(
                self,
                "Exported",
                f"Analytics chart saved to:\n{path}\n({name}, last {self.analytics_days} days)",
            )
        except Exception as e:
            QMessageBox.warning(self, "Export failed", str(e))


class MainWindow(QMainWindow):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.is_dark = False
        self.setWindowTitle("LinkVerse")
        self.setMinimumSize(380, 500)
        self.resize(480, 720)

        main_container = QWidget()
        main_container.setObjectName("root")
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 4, 12, 0)

        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "static", "logo.png")

        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(
                150,
                150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.logo_label.setPixmap(pix)
        else:
            self.logo_label.setText("LinkVerse")
            _lbl(self.logo_label, "pageTitle")

        self.btn_theme = _btn(QPushButton("🌙 Dark"), "chip")
        self.btn_theme.clicked.connect(self.toggle_theme)

        header_layout.addWidget(self.logo_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_theme)

        main_layout.addLayout(header_layout)

        # ვაბრუნებთ StackedWidget-ს (გვერდების გადასართველად) ლოგოს ქვემოთ
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self.stack, 1)

        self.login_page = LoginPage(logic)
        self.login_page.done.connect(self.show_dash)
        self.login_page.go_register.connect(lambda: self.stack.setCurrentIndex(1))
        self.stack.addWidget(self.login_page)

        self.reg_page = RegisterPage(logic)
        self.reg_page.done.connect(self.show_dash)
        self.reg_page.go_login.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.reg_page)

        self.dash = DashboardPage(logic)
        self.dash.logged_out.connect(self.on_logout)
        self.dash.go_analytics.connect(self.show_analytics)
        self.stack.addWidget(self.dash)

        self.analytics = AnalyticsPage(logic)
        self.analytics.go_back.connect(lambda: self.stack.setCurrentIndex(2))
        self.stack.addWidget(self.analytics)

        self._apply_theme()

    def _apply_theme(self):
        apply_theme(QApplication.instance(), self.is_dark)
        if self.is_dark:
            self.btn_theme.setText("☀️ Light")
            self.btn_theme.setProperty("btnRole", "chipActive")
        else:
            self.btn_theme.setText("🌙 Dark")
            self.btn_theme.setProperty("btnRole", "chip")
        self.btn_theme.style().unpolish(self.btn_theme)
        self.btn_theme.style().polish(self.btn_theme)
        if self.stack.currentIndex() == 3:
            self.analytics.refresh()

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self._apply_theme()

    def show_dash(self):
        self.dash.refresh()
        self.stack.setCurrentIndex(2)

    def show_analytics(self):
        self.analytics.refresh()
        self.stack.setCurrentIndex(3)

    def on_logout(self):
        self.login_page.clear()
        self.reg_page.clear()
        self.stack.setCurrentIndex(0)
