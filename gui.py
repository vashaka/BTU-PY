# pyqt gui stuff
import os
import io
import qrcode
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QPixmap, QImage
from PyQt6.QtWidgets import *


class LoginPage(QWidget):
    done = pyqtSignal()
    go_register = pyqtSignal()

    def __init__(self, logic):
        super().__init__()
        self.logic = logic

        # მთავარი Layout - ყველაფერს სვამს ფანჯრის ცენტრში
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        # სათაური
        self.title = QLabel("Sign in")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 32px; font-weight: bold; color: black; margin-bottom: 10px;")
        layout.addWidget(self.title)

        # ინპუტების საერთო სტილი
        input_style = """
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 14px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #008080;
            }
        """

        # ველების შექმნა და მაქსიმალური სიგანის შეზღუდვა
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.user_input.setStyleSheet(input_style)
        self.user_input.setMaximumWidth(400)  # 🌟 ზღუდავს სიგანეს პირდაპირ ვიჯეტზე

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet(input_style)
        self.pass_input.setMaximumWidth(400)

        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)

        # ერორების ლეიბლი
        self.err = QLabel("")
        self.err.setStyleSheet("color: red; font-size: 13px; font-weight: bold;")
        self.err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.err)

        # მთავარი ღილაკი "Sign in"
        self.btn_login = QPushButton("Sign in")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setMaximumWidth(400)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #008080;
                color: white;
                border-radius: 20px;
                padding: 14px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #006666;
            }
        """)
        self.btn_login.clicked.connect(self.do_login)
        layout.addWidget(self.btn_login)

        # "Don't have an account? Register" ლინკი
        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_ask = QLabel("Don't have an account?")
        lbl_ask.setStyleSheet("color: #6b7280; font-size: 13px;")

        self.btn_go_register = QPushButton("Register")
        self.btn_go_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_go_register.setStyleSheet(
            "QPushButton { color: #008080; font-size: 13px; font-weight: bold; border: none; background: transparent; text-decoration: underline; }")
        self.btn_go_register.clicked.connect(self.go_register.emit)

        register_layout.addWidget(lbl_ask)
        register_layout.addWidget(self.btn_go_register)
        layout.addLayout(register_layout)

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
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(40, 80, 40, 80)
        main_layout.setSpacing(12)

        # 1. სათაური "Create account"
        self.title = QLabel("Create account")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 32px; font-weight: bold; color: black; margin-bottom: 20px;")
        main_layout.addWidget(self.title)

        # 2. ინპუტების სტილი (რუხი ჩარჩო და მომრგვალება)
        input_style = """
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 14px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #008080;
            }
        """

        # 3. ველების შექმნა (ვიყენებთ ზუსტად შენს ძველ ცვლადებს, ლოგიკა რომ არ აირიოს)
        self.name = QLineEdit()
        self.name.setPlaceholderText("Name")
        self.name.setStyleSheet(input_style)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.email.setStyleSheet(input_style)

        self.pw = QLineEdit()
        self.pw.setPlaceholderText("Password")
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw.setStyleSheet(input_style)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username (@handle)")
        self.user.setStyleSheet(input_style)

        main_layout.addWidget(self.name)
        main_layout.addWidget(self.email)
        main_layout.addWidget(self.pw)
        main_layout.addWidget(self.user)

        # ერორების გამოსატანი ლეიბლი (რომელსაც შენი do_reg ფუნქცია იყენებს)
        self.err = QLabel("")
        self.err.setStyleSheet("color: red; font-size: 13px; font-weight: bold;")
        self.err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.err)

        # 4. მთავარი ღილაკი "Create account"
        self.btn_register = QPushButton("Create account")
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_register.setStyleSheet("""
            QPushButton {
                background-color: #008080;
                color: white;
                border-radius: 20px;
                padding: 14px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #006666;
            }
        """)
        self.btn_register.clicked.connect(self.do_reg)
        main_layout.addWidget(self.btn_register)

        # 5. "Already have an account? Log in" სექცია
        login_layout = QHBoxLayout()
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_ask = QLabel("Already have an account?")
        lbl_ask.setStyleSheet("color: #6b7280; font-size: 13px;")

        self.btn_go_login = QPushButton("Log in")
        self.btn_go_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_go_login.setStyleSheet("""
            QPushButton {
                color: #008080;
                font-size: 13px;
                font-weight: bold;
                border: none;
                background: transparent;
                text-decoration: underline;
            }
        """)
        self.btn_go_login.clicked.connect(self.go_login.emit)

        login_layout.addWidget(lbl_ask)
        login_layout.addWidget(self.btn_go_login)
        main_layout.addLayout(login_layout)

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
                self.err.setText("სახელი უნდა შეიცავდეს მხოლოდ ლათინურ ასოებს, ციფრებს ან _")
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

    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.selected_id = None

        # მთავარი მაკეტი (Layout)
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ფიქსირებული სიგანის ძირითადი ბლოკი
        content_widget = QWidget()
        content_widget.setFixedWidth(380)

        layout = QVBoxLayout(content_widget)
        layout.setSpacing(6)  # მჭიდრო დაშორება ელემენტებს შორის
        layout.setContentsMargins(0, 0, 0, 0)

        # --- 1. ზედა ზოლი (Dark Mode და Logout) ---
        top_layout = QHBoxLayout()
        self.btn_theme = QPushButton("Dark Mode")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.setStyleSheet("""
            QPushButton {
                background-color: white; color: black; border: 1px solid #d1d5db;
                border-radius: 12px; padding: 4px 10px; font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #f3f4f6; }
        """)
        self.btn_theme.clicked.connect(self.toggle_theme)

        self.logout_btn = QPushButton("Log out")
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                color: #6b7280; font-size: 11px; font-weight: bold;
                border: none; background: transparent; text-decoration: underline;
            }
            QPushButton:hover { color: #dc2626; }
        """)
        self.logout_btn.clicked.connect(self.logout)

        top_layout.addWidget(self.btn_theme)
        top_layout.addStretch()
        top_layout.addWidget(self.logout_btn)
        layout.addLayout(top_layout)

        # დიზაინის საერთო სტილები
        input_style = """
            QLineEdit, QTextEdit {
                border: 1px solid #d1d5db; border-radius: 10px;
                padding: 6px 12px; font-size: 12px; background-color: white; color: black;
            }
            QLineEdit:focus, QTextEdit:focus { border: 2px solid #008080; }
        """

        main_btn_style = """
            QPushButton {
                background-color: #008080; color: white; border-radius: 10px;
                padding: 8px; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #006666; }
        """

        secondary_btn_style = """
            QPushButton {
                background-color: white; color: black; border: 1px solid #d1d5db;
                border-radius: 10px; padding: 6px; font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #f3f4f6; }
            QPushButton:disabled { background-color: #f3f4f6; color: #9ca3af; border: 1px solid #e5e7eb; }
        """

        # --- 2. საჯარო პროფილის სექცია ---
        share_lbl = QLabel("Your public profile:")
        share_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #4b5563; margin-top: 2px;")
        layout.addWidget(share_lbl)

        share_layout = QHBoxLayout()
        self.share_box = QLineEdit()
        self.share_box.setReadOnly(True)
        self.share_box.setStyleSheet(input_style)

        copyb = QPushButton("Copy")
        copyb.setCursor(Qt.CursorShape.PointingHandCursor)
        copyb.setStyleSheet("""
                    QPushButton {
                        background-color: #008080; color: white; border-radius: 8px;
                        padding: 5px 12px; font-size: 11px; font-weight: bold;
                    }
                    QPushButton:hover { background-color: #006666; }
                """)
        copyb.clicked.connect(self.copy_url)
        share_layout.addWidget(self.share_box)
        share_layout.addWidget(copyb)
        layout.addLayout(share_layout)

        # 🌟 ვქმნით კონტეინერს QR კოდისთვის
        qr_container = QHBoxLayout()
        qr_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_container.setContentsMargins(0, 0, 0, 0)  # 👈 აშორებს შიდა დაშორებებს, რაც მაღლა სწევს კოდს

        self.qr_label = QLabel()
        self.qr_label.setFixedSize(160, 160)  # 👈 160x160 იდეალური ზომაა, რომ ინტერფეისი ზემოთ აიტანოს
        self.qr_label.setScaledContents(True)

        qr_container.addWidget(self.qr_label)
        layout.addLayout(qr_container)

        # --- 3. PROFILE სექცია ---
        lbl_prof = QLabel("Profile Settings")
        lbl_prof.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #111827; margin-top: 4px; border-bottom: 1px solid #e5e7eb; padding-bottom: 2px;")
        layout.addWidget(lbl_prof)

        # 🌟 ავატარის ბლოკის გასწორება ზუსტად ცენტრში
        avatar_layout = QHBoxLayout()
        avatar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(120, 120)
        self.avatar_label.setScaledContents(True)
        self.avatar_label.setStyleSheet("border: 2px solid #008080; border-radius: 30px; background-color: #f3f4f6;")

        self.btn_pic = QPushButton("Change Photo")
        self.btn_pic.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pic.setStyleSheet(secondary_btn_style)
        self.btn_pic.setFixedWidth(100)
        self.btn_pic.clicked.connect(self.choose_profile_pic)

        avatar_layout.addWidget(self.avatar_label)
        avatar_layout.addSpacing(10)
        avatar_layout.addWidget(self.btn_pic)
        layout.addLayout(avatar_layout)

        self.disp_name = QLineEdit()
        self.disp_name.setPlaceholderText("Display Name")
        self.disp_name.setStyleSheet(input_style)
        layout.addWidget(self.disp_name)

        self.bio = QTextEdit()
        self.bio.setPlaceholderText("Bio...")
        self.bio.setFixedHeight(40)
        self.bio.setStyleSheet(input_style)
        layout.addWidget(self.bio)

        sp = QPushButton("Save Profile")
        sp.setCursor(Qt.CursorShape.PointingHandCursor)
        sp.setStyleSheet(main_btn_style)
        sp.clicked.connect(self.save_profile)
        layout.addWidget(sp)

        # --- 4. LINKS სექცია ---
        lbl_links = QLabel("Manage Links")
        lbl_links.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #111827; margin-top: 4px; border-bottom: 1px solid #e5e7eb; padding-bottom: 2px;")
        layout.addWidget(lbl_links)

        # ლინკების სია
        self.list = QListWidget()
        self.list.setFixedHeight(100)
        self.list.setStyleSheet("""
            QListWidget {
                border: 1px solid #d1d5db; border-radius: 10px; padding: 2px;
                background-color: #f9fafb; color: black;
            }
            QListWidget::item { padding: 4px; border-bottom: 1px solid #f3f4f6; font-size: 11px; }
            QListWidget::item:selected { background-color: #e6f2f2; color: #008080; border-radius: 5px; }
        """)
        self.list.currentItemChanged.connect(self.pick_link)
        layout.addWidget(self.list)

        self.link_title = QLineEdit()
        self.link_title.setPlaceholderText("Link Title (e.g., GitHub)")
        self.link_title.setStyleSheet(input_style)
        layout.addWidget(self.link_title)

        self.link_url = QLineEdit()
        self.link_url.setPlaceholderText("URL (https://...)")
        self.link_url.setStyleSheet(input_style)
        layout.addWidget(self.link_url)

        self.link_icon = QComboBox()
        self.link_icon.addItems(["Default", "Facebook", "Instagram", "Twitter", "GitHub", "YouTube", "LinkedIn"])
        self.link_icon.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db; border-radius: 10px; padding: 4px 10px;
                font-size: 12px; background-color: white; color: black;
            }
        """)
        layout.addWidget(self.link_icon)

        # მართვის ღილაკები (რიგი 1)
        row = QHBoxLayout()
        row.setSpacing(5)
        self.btn_add = QPushButton("Add")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(secondary_btn_style)
        self.btn_add.clicked.connect(self.add_link)

        self.btn_upd = QPushButton("Update")
        self.btn_upd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_upd.setEnabled(False)
        self.btn_upd.setStyleSheet(secondary_btn_style)
        self.btn_upd.clicked.connect(self.upd_link)

        self.btn_hide = QPushButton("Hide/Show")
        self.btn_hide.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hide.setEnabled(False)
        self.btn_hide.setStyleSheet(secondary_btn_style)
        self.btn_hide.clicked.connect(self.tog_link)

        self.btn_del = QPushButton("Delete")
        self.btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del.setEnabled(False)
        self.btn_del.setStyleSheet("""
            QPushButton {
                background-color: #fee2e2; color: #dc2626; border: 1px solid #fca5a5;
                border-radius: 10px; padding: 6px; font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #fca5a5; }
            QPushButton:disabled { background-color: #f3f4f6; color: #9ca3af; border: 1px solid #e5e7eb; }
        """)
        self.btn_del.clicked.connect(self.del_link)

        row.addWidget(self.btn_add)
        row.addWidget(self.btn_upd)
        row.addWidget(self.btn_hide)
        row.addWidget(self.btn_del)
        layout.addLayout(row)

        # გადაადგილების ღილაკები (რიგი 2)
        row2 = QHBoxLayout()
        row2.setSpacing(5)
        up = QPushButton("Move Up ↑")
        up.setCursor(Qt.CursorShape.PointingHandCursor)
        up.setStyleSheet(secondary_btn_style)
        up.clicked.connect(lambda: self.move("up"))

        dn = QPushButton("Move Down ↓")
        dn.setCursor(Qt.CursorShape.PointingHandCursor)
        dn.setStyleSheet(secondary_btn_style)
        dn.clicked.connect(lambda: self.move("down"))

        row2.addWidget(up)
        row2.addWidget(dn)
        layout.addLayout(row2)

        self.msg = QLabel("")
        self.msg.setStyleSheet("color: #008080; font-size: 11px; font-weight: bold;")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.msg)

        main_layout.addWidget(content_widget)

        # 🌟 ეს ხაზი უზრუნველყოფს, რომ ქვემოთ დარჩეს თავისუფალი ადგილი და სქროლი არ გაჩნდეს
        main_layout.addStretch()

        self.refresh()

    def refresh(self):
        u = self.logic.current_user
        if not u:
            return

        if u.profile_pic:
            img_path = os.path.join(os.path.dirname(__file__), "static", "uploads", u.profile_pic)
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
                if not link.is_active:
                    txt += " (off)"

                # ვამატებთ კლიკების რაოდენობას ვიზუალში
                txt += f"  [ 👁 {link.clicks} clicks ]"

                item = QListWidgetItem(txt + " - " + link.url)
                item.setData(Qt.ItemDataRole.UserRole, link.id)
                self.list.addItem(item)
        except Exception as e:
            print(e)
            pass

    def pick_link(self, item, prev):
        if item == None:
            self.selected_id = None
            self.btn_upd.setEnabled(False)
            self.btn_hide.setEnabled(False)
            self.btn_del.setEnabled(False)
            return
        self.selected_id = item.data(Qt.ItemDataRole.UserRole)
        self.btn_upd.setEnabled(True)
        self.btn_hide.setEnabled(True)
        self.btn_del.setEnabled(True)
        for link in self.logic.get_my_links():
            if link.id == self.selected_id:
                self.link_title.setText(link.title)
                self.link_url.setText(link.url)
                self.link_icon.setCurrentText(link.icon if link.icon else "Default")

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
            self.logic.add_link(self.link_title.text(), self.link_url.text(), self.link_icon.currentText())
            self.link_title.clear()
            self.link_url.clear()
            self.link_icon.setCurrentIndex(0)
            self.reload_list()
            self.msg.setText("added")
        except:
            self.msg.setText("fail")

    def upd_link(self):
        if self.selected_id == None:
            return
        try:
            self.logic.update_link(
                self.selected_id, self.link_title.text(), self.link_url.text(), self.link_icon.currentText()
            )
            self.reload_list()
            self.msg.setText("updated")
        except:
            self.msg.setText("fail")

    def tog_link(self):
        try:
            self.logic.toggle_link(self.selected_id)
            self.reload_list()
        except:
            self.msg.setText("fail")

    def del_link(self):
        r = QMessageBox.question(self, "?", "delete?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r != QMessageBox.StandardButton.Yes:
            return
        try:
            self.logic.delete_link(self.selected_id)
            self.selected_id = None
            self.link_title.clear()
            self.link_url.clear()
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
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.logic.upload_profile_pic(file_path)
            self.refresh()

    def logout(self):
        self.logic.logout()
        self.logged_out.emit()

    def toggle_theme(self):
        if not hasattr(self, "is_dark") or not self.is_dark:
            self.is_dark = True
            self.btn_theme.setText("Light Mode")
            self.window().setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #ffffff; }
                QLineEdit, QTextEdit, QListWidget, QComboBox { 
                    background-color: #3b3b3b; color: #ffffff; border: 1px solid #555; 
                }
                QPushButton { 
                    background-color: #4b4b4b; color: white; border: 1px solid #555; padding: 5px; 
                }
                QPushButton:hover { background-color: #5b5b5b; }
            """)
        else:
            self.is_dark = False
            self.btn_theme.setText("Dark Mode")
            self.window().setStyleSheet("""
                QMainWindow { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(184, 255, 253, 255), 
                    stop:1 rgba(255, 186, 211, 255)); 
                }
            """)


class MainWindow(QMainWindow):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.setWindowTitle("LinkVerse")
        self.setMinimumSize(550, 1000)
        self.setStyleSheet("QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(184, 255, 253, 255), stop:1 rgba(255, 186, 211, 255));}")
        # ვქმნით მთავარ კონტეინერს
        main_container = QWidget()
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ვქმნით ზედა ზოლს (Header) ლოგოსთვის
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "static", "logo.png")

        # ვამოწმებთ, არსებობს თუ არა ლოგოს ფაილი
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pix)
        else:
            # თუ სურათი ვერ იპოვა, ლამაზ ტექსტს დაწერს მის ნაცვლად
            self.logo_label.setText("LinkVerse")
            self.logo_label.setStyleSheet("font-size: 18px;")

        header_layout.addWidget(self.logo_label)

        # ეს 'stretch' ლოგოს მარცხნივ აჩერებს. თუ გინდა რომ ლოგო მარჯვნივ იყოს,
        # ეს ხაზი `header_layout.addWidget(self.logo_label)`-ის ზემოთ აიტანე.
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # ვაბრუნებთ StackedWidget-ს (გვერდების გადასართველად) ლოგოს ქვემოთ
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

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
        self.stack.addWidget(self.dash)

    def show_dash(self):
        self.dash.refresh()
        self.stack.setCurrentIndex(2)

    def on_logout(self):
        self.login_page.clear()
        self.reg_page.clear()
        self.stack.setCurrentIndex(0)
