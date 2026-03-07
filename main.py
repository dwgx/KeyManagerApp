import string
import sys
import os
import json
import base64
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QMessageBox, QInputDialog, QCheckBox, QComboBox, QFileDialog,
    QHBoxLayout, QDialog, QStyle, QToolBar, QSpinBox, QStyleFactory
)
from PySide6.QtGui import QFont, QPalette, QBrush, QImage, QColor, QFontDatabase, QIcon, QPixmap, QAction
from PySide6.QtCore import Qt, QSize, QTimer, QUrl
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.fernet import Fernet
import secrets

SETTINGS_FILE = "settings.dat"
DATA_FILE = "data.dat"
SALT_FILE = "salt.dat"

def load_font():
    font_path = ""
    possible_paths = [
        "C:\\Windows\\Fonts\\UDDIGIKYOKASHON-B.TTC",
        os.path.join(os.getcwd(), "UDDIGIKYOKASHON-B.TTC")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            font_path = path
            break
    if font_path:
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                return font_families[0]
    return "Arial"

def generate_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2 ** 14,
        r=8,
        p=1,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def generate_salt() -> bytes:
    return secrets.token_bytes(16)

def save_salt(salt: bytes):
    with open(SALT_FILE, 'wb') as f:
        f.write(salt)

def load_salt() -> bytes:
    if not os.path.exists(SALT_FILE):
        salt = generate_salt()
        save_salt(salt)
    else:
        with open(SALT_FILE, 'rb') as f:
            salt = f.read()
    return salt

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("密钥管理器 - 登录")
        self.resize(400, 300)
        self.master_key = None
        self.font_family = load_font()
        self.init_ui()

    def init_ui(self):
        self.set_background_image()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("密钥管理器")
        title_font = QFont(self.font_family, 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)

        watermark_label = QLabel("Keymanager BY dwgx1337")
        watermark_font = QFont("Arial", 10)
        watermark_label.setFont(watermark_font)
        watermark_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        watermark_label.setStyleSheet("color: rgba(255, 255, 255, 80%);")
        layout.addWidget(watermark_label)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("请输入主密钥")
        self.password_edit.setStyleSheet("background-color: rgba(255, 255, 255, 180);")
        layout.addWidget(self.password_edit)

        self.login_btn = QPushButton("登录")
        self.login_btn.setIcon(QIcon("icons/login.png"))  # 使用自定义图标
        self.login_btn.clicked.connect(self.check_password)
        self.login_btn.setStyleSheet("background-color: rgba(70, 130, 180, 200); color: white;")
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def set_background_image(self):
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setScaledContents(True)
        self.background_label.lower()  # 将背景标签置于最底层

        image_url = "https://t.alcy.cc/moez"
        self.network_manager = QtNetwork.QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.on_image_downloaded)
        request = QtNetwork.QNetworkRequest(QUrl(image_url))
        self.network_manager.get(request)

    def on_image_downloaded(self, reply):
        if reply.error() == QtNetwork.QNetworkReply.NoError:
            data = reply.readAll()
            image = QImage()
            image.loadFromData(data)
            pixmap = QPixmap.fromImage(image)
            self.background_label.setPixmap(pixmap)
        else:
            self.set_default_background()

    def set_default_background(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def check_password(self):
        entered_password = self.password_edit.text()
        if not entered_password:
            QMessageBox.warning(self, "错误", "请输入主密钥！")
            return
        try:
            salt = load_salt()
            self.master_key = generate_key(entered_password, salt)
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'rb') as file:
                    encrypted_data = file.read()
                fernet = Fernet(self.master_key)
                decrypted_data = fernet.decrypt(encrypted_data).decode()
            self.open_password_manager()
        except Exception:
            QMessageBox.warning(self, "错误", "密钥验证失败。")

    def open_password_manager(self):
        self.hide()
        self.manager = PasswordManager(self.master_key)
        self.manager.show()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(600, 500)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        theme_label = QLabel("选择主题:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["亮色", "暗色", "Windows 原生", "PySideQT6 原版"])
        current_theme = self.parent.settings.get("theme", "暗色")
        index = self.theme_combo.findText(current_theme)
        if index != -1:
            self.theme_combo.setCurrentIndex(index)
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)

        bg_label = QLabel("选择背景:")
        self.bg_combo = QComboBox()
        self.bg_combo.addItems(["随机背景", "黑色背景", "本地图片"])
        current_bg = self.parent.settings.get("background_option", "随机背景")
        index = self.bg_combo.findText(current_bg)
        if index != -1:
            self.bg_combo.setCurrentIndex(index)
        layout.addWidget(bg_label)
        layout.addWidget(self.bg_combo)

        freq_label = QLabel("背景变换频率 (分钟):")
        self.freq_spinbox = QSpinBox()
        self.freq_spinbox.setRange(1, 1440)
        self.freq_spinbox.setValue(self.parent.settings.get("background_change_frequency", 10))
        layout.addWidget(freq_label)
        layout.addWidget(self.freq_spinbox)

        self.bg_path_edit = QLineEdit()
        self.bg_path_edit.setPlaceholderText("选择背景图片路径")
        self.bg_path_edit.setText(self.parent.settings.get("background_image", ""))
        self.bg_browse_btn = QPushButton("浏览")
        self.bg_browse_btn.setIcon(QIcon("icons/browse.png"))  # 使用自定义图标
        self.bg_browse_btn.clicked.connect(self.browse_image)
        self.bg_browse_layout = QHBoxLayout()
        self.bg_browse_layout.addWidget(self.bg_path_edit)
        self.bg_browse_layout.addWidget(self.bg_browse_btn)
        layout.addLayout(self.bg_browse_layout)

        key_label = QLabel("管理主密钥:")
        self.change_key_btn = QPushButton("更改主密钥")
        self.change_key_btn.setIcon(QIcon("icons/change_key.png"))  # 使用自定义图标
        self.change_key_btn.clicked.connect(self.change_master_key)
        layout.addWidget(key_label)
        layout.addWidget(self.change_key_btn)

        max_attempts_label = QLabel("最大错误尝试次数:")
        self.max_attempts_spinbox = QSpinBox()
        self.max_attempts_spinbox.setRange(1, 10)
        self.max_attempts_spinbox.setValue(self.parent.settings.get("max_attempts", 3))
        layout.addWidget(max_attempts_label)
        layout.addWidget(self.max_attempts_spinbox)

        require_key_label = QLabel("是否需要主密钥验证:")
        self.require_key_checkbox = QCheckBox("需要主密钥验证")
        self.require_key_checkbox.setChecked(self.parent.settings.get("require_master_key", True))
        self.require_key_checkbox.setIcon(QIcon("icons/require_key.png"))  # 使用自定义图标
        layout.addWidget(require_key_label)
        layout.addWidget(self.require_key_checkbox)

        # 新增设置项：是否隐藏账号、密码和添加的内容
        hide_account_label = QLabel("是否隐藏账号:")
        self.hide_account_checkbox = QCheckBox("隐藏账号")
        self.hide_account_checkbox.setChecked(self.parent.settings.get("hide_account", False))
        self.hide_account_checkbox.setIcon(QIcon("icons/hide_account.png"))  # 使用自定义图标
        layout.addWidget(hide_account_label)
        layout.addWidget(self.hide_account_checkbox)

        hide_password_label = QLabel("是否隐藏密码:")
        self.hide_password_checkbox = QCheckBox("隐藏密码")
        self.hide_password_checkbox.setChecked(self.parent.settings.get("hide_password", False))
        self.hide_password_checkbox.setIcon(QIcon("icons/hide_password.png"))  # 使用自定义图标
        layout.addWidget(hide_password_label)
        layout.addWidget(self.hide_password_checkbox)

        hide_more_info_label = QLabel("是否隐藏更多信息:")
        self.hide_more_info_checkbox = QCheckBox("隐藏更多信息")
        self.hide_more_info_checkbox.setChecked(self.parent.settings.get("hide_more_info", False))
        self.hide_more_info_checkbox.setIcon(QIcon("icons/hide_info.png"))  # 使用自定义图标
        layout.addWidget(hide_more_info_label)
        layout.addWidget(self.hide_more_info_checkbox)

        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.setIcon(QIcon("icons/save.png"))  # 使用自定义图标
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setIcon(QIcon("icons/cancel.png"))  # 使用自定义图标
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.bg_combo.currentTextChanged.connect(self.toggle_bg_browse)
        self.toggle_bg_browse(self.bg_combo.currentText())

    def toggle_bg_browse(self, text):
        if text == "本地图片":
            self.bg_path_edit.setEnabled(True)
            self.bg_browse_btn.setEnabled(True)
        else:
            self.bg_path_edit.setEnabled(False)
            self.bg_browse_btn.setEnabled(False)

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择背景图片", "", "图片文件 (*.png *.jpg *.bmp)")
        if file_path:
            self.bg_path_edit.setText(file_path)

    def change_master_key(self):
        dialog = ChangeMasterKeyDialog(self.parent)
        dialog.exec()

    def save_settings(self):
        theme = self.theme_combo.currentText()
        background_option = self.bg_combo.currentText()
        background_image = self.bg_path_edit.text() if background_option == "本地图片" else ""
        background_change_freq = self.freq_spinbox.value()
        max_attempts = self.max_attempts_spinbox.value()
        require_master_key = self.require_key_checkbox.isChecked()
        hide_account = self.hide_account_checkbox.isChecked()
        hide_password = self.hide_password_checkbox.isChecked()
        hide_more_info = self.hide_more_info_checkbox.isChecked()

        self.parent.settings["theme"] = theme
        self.parent.settings["background_option"] = background_option
        self.parent.settings["background_image"] = background_image
        self.parent.settings["background_change_frequency"] = background_change_freq
        self.parent.settings["max_attempts"] = max_attempts
        self.parent.settings["require_master_key"] = require_master_key
        self.parent.settings["hide_account"] = hide_account
        self.parent.settings["hide_password"] = hide_password
        self.parent.settings["hide_more_info"] = hide_more_info

        self.parent.apply_theme()
        self.parent.save_settings()
        self.parent.setup_background_timer()
        self.accept()

class ChangeMasterKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("更改主密钥")
        self.resize(600, 400)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        old_key_label = QLabel("请输入旧主密钥:")
        self.old_key_edit = QLineEdit()
        self.old_key_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(old_key_label)
        layout.addWidget(self.old_key_edit)

        new_key_label = QLabel("请输入新主密钥:")
        self.new_key_edit = QLineEdit()
        self.new_key_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(new_key_label)
        layout.addWidget(self.new_key_edit)

        confirm_key_label = QLabel("请确认新主密钥:")
        self.confirm_key_edit = QLineEdit()
        self.confirm_key_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(confirm_key_label)
        layout.addWidget(self.confirm_key_edit)

        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.setIcon(QIcon("icons/save.png"))  # 使用自定义图标
        self.save_btn.clicked.connect(self.change_key)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setIcon(QIcon("icons/cancel.png"))  # 使用自定义图标
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def change_key(self):
        old_key = self.old_key_edit.text()
        new_key = self.new_key_edit.text()
        confirm_key = self.confirm_key_edit.text()

        if not old_key or not new_key or not confirm_key:
            QMessageBox.warning(self, "错误", "所有字段都必须填写。")
            return

        if new_key != confirm_key:
            QMessageBox.warning(self, "错误", "新密钥与确认密钥不匹配。")
            return

        try:
            salt = load_salt()
            old_master_key = generate_key(old_key, salt)
            old_fernet = Fernet(old_master_key)

            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'rb') as file:
                    encrypted_settings = file.read()
                decrypted_settings = old_fernet.decrypt(encrypted_settings)
                settings = json.loads(decrypted_settings.decode())
            else:
                settings = {}

            data_file_location = settings.get("data_file_location", DATA_FILE)
            if os.path.exists(data_file_location):
                with open(data_file_location, 'rb') as file:
                    encrypted_passwords = file.read()
                decrypted_passwords = old_fernet.decrypt(encrypted_passwords)
                passwords = json.loads(decrypted_passwords.decode())
            else:
                passwords = {}

            new_salt = generate_salt()
            save_salt(new_salt)
            new_master_key = generate_key(new_key, new_salt)
            new_fernet = Fernet(new_master_key)

            new_encrypted_settings = new_fernet.encrypt(json.dumps(settings).encode())
            with open(SETTINGS_FILE, 'wb') as file:
                file.write(new_encrypted_settings)

            new_encrypted_passwords = new_fernet.encrypt(json.dumps(passwords).encode())
            with open(data_file_location, 'wb') as file:
                file.write(new_encrypted_passwords)

            self.parent.master_key = new_master_key
            QMessageBox.information(self, "成功", "主密钥已成功更改。")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"更改主密钥失败: {e}")

class PasswordVerificationDialog(QDialog):
    def __init__(self, master_key):
        super().__init__()
        self.setWindowTitle("验证主密钥")
        self.resize(500, 300)
        self.master_key = master_key
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        key_label = QLabel("请输入主密钥以查看详情:")
        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(key_label)
        layout.addWidget(self.key_edit)

        buttons_layout = QHBoxLayout()
        self.verify_btn = QPushButton("验证")
        self.verify_btn.setIcon(QIcon("icons/verify.png"))  # 使用自定义图标
        self.verify_btn.clicked.connect(self.verify_key)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setIcon(QIcon("icons/cancel.png"))  # 使用自定义图标
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.verify_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def verify_key(self):
        entered_key = self.key_edit.text()
        if not entered_key:
            QMessageBox.warning(self, "错误", "请输入主密钥。")
            return
        try:
            salt = load_salt()
            entered_master_key = generate_key(entered_key, salt)
            entered_fernet = Fernet(entered_master_key)
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'rb') as file:
                    encrypted_data = file.read()
                decrypted_data = entered_fernet.decrypt(encrypted_data).decode()
            self.accept()
        except Exception:
            QMessageBox.warning(self, "错误", "主密钥验证失败。")

class PasswordManager(QWidget):
    def __init__(self, master_key):
        super().__init__()
        self.setWindowTitle("密钥管理器")
        self.resize(800, 600)
        self.master_key = master_key
        self.passwords = {}
        self.data_file = DATA_FILE
        self.settings_file = SETTINGS_FILE
        self.settings = {
            "require_master_key": True,
            "max_attempts": 3,
            "data_file_location": os.path.abspath(self.data_file),
            "background_option": "随机背景",
            "background_image": "",
            "background_change_frequency": 10,
            "theme": "暗色",
            "hide_account": False,
            "hide_password": False,
            "hide_more_info": False,
        }
        self.incorrect_attempts = 0
        self.font_family = load_font()
        self.load_settings()
        self.init_ui()
        self.load_passwords()
        self.setup_background_timer()

    def init_ui(self):
        self.apply_theme()
        self.apply_font()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))

        add_icon = QIcon("icons/add.png")  # 使用自定义图标
        add_action = QAction(add_icon, "添加密码", self)
        add_action.triggered.connect(self.add_password)
        toolbar.addAction(add_action)

        delete_icon = QIcon("icons/delete.png")  # 使用自定义图标
        delete_action = QAction(delete_icon, "删除密码", self)
        delete_action.triggered.connect(self.delete_password)
        toolbar.addAction(delete_action)

        settings_icon = QIcon("icons/settings.png")  # 使用自定义图标
        settings_action = QAction(settings_icon, "设置", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)

        clear_icon = QIcon("icons/clear.png")  # 使用自定义图标
        clear_action = QAction(clear_icon, "一键清除数据", self)
        clear_action.triggered.connect(self.clear_data_files)
        toolbar.addAction(clear_action)

        main_layout.addWidget(toolbar)

        title_label = QLabel("密钥管理器")
        title_font = QFont(self.font_family, 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")
        main_layout.addWidget(title_label)

        watermark_label = QLabel("Keymanager BY dwgx1337")
        watermark_font = QFont("Arial", 10)
        watermark_label.setFont(watermark_font)
        watermark_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        watermark_label.setStyleSheet("color: rgba(255, 255, 255, 80%);")
        main_layout.addWidget(watermark_label)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.show_details)
        self.list_widget.setStyleSheet("background-color: rgba(255, 255, 255, 180);")
        main_layout.addWidget(self.list_widget)

        self.setLayout(main_layout)
        self.setMinimumSize(600, 400)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def apply_theme(self):
        theme = self.settings.get("theme", "暗色")
        if theme == "亮色":
            self.set_light_theme()
        elif theme == "暗色":
            self.set_dark_theme()
        elif theme == "Windows 原生":
            self.set_native_theme()
        elif theme == "PySideQT6 原版":
            self.set_default_pyside_theme()
        else:
            self.set_dark_theme()
        self.apply_background()

    def set_light_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QListWidget {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
            }
        """)

    def set_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QListWidget {
                background-color: #3c3c3c;
                border: 1px solid #555555;
            }
        """)

    def set_native_theme(self):
        QApplication.setStyle(QStyleFactory.create("Windows"))
        self.setStyleSheet("")

    def set_default_pyside_theme(self):
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        self.setStyleSheet("")

    def apply_background(self):
        background_option = self.settings.get("background_option", "随机背景")
        if background_option == "随机背景":
            self.load_random_background()
        elif background_option == "黑色背景":
            self.set_default_background()
        elif background_option == "本地图片":
            self.load_local_background()

    def load_random_background(self):
        image_url = "https://t.alcy.cc/moez"
        self.network_manager = QtNetwork.QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.on_random_background_downloaded)
        request = QtNetwork.QNetworkRequest(QUrl(image_url))
        self.network_manager.get(request)

    def on_random_background_downloaded(self, reply):
        if reply.error() == QtNetwork.QNetworkReply.NoError:
            data = reply.readAll()
            image = QImage()
            image.loadFromData(data)
            pixmap = QPixmap.fromImage(image)
            palette = QPalette()
            scaled_pixmap = pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
        else:
            QMessageBox.warning(self, "警告", "无法加载随机背景图片。")

    def load_local_background(self):
        image_path = self.settings.get("background_image", "")
        if os.path.exists(image_path):
            try:
                pixmap = QPixmap(image_path)
                palette = QPalette()
                scaled_pixmap = pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
                self.setPalette(palette)
                self.setAutoFillBackground(True)
            except Exception:
                QMessageBox.warning(self, "警告", "无法加载本地背景图片。")
        else:
            QMessageBox.warning(self, "警告", "无法找到背景图片文件。")

    def set_default_background(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def setup_background_timer(self):
        if hasattr(self, 'background_timer'):
            self.background_timer.stop()
        self.background_timer = QTimer()
        freq_minutes = self.settings.get("background_change_frequency", 10)
        self.background_timer.timeout.connect(self.change_background)
        self.background_timer.start(freq_minutes * 60 * 1000)

    def change_background(self):
        background_option = self.settings.get("background_option", "随机背景")
        if background_option == "随机背景":
            self.load_random_background()

    def resizeEvent(self, event):
        self.apply_background()
        super().resizeEvent(event)

    def apply_font(self):
        font_size = 12
        app_font = QFont(self.font_family, font_size)
        QApplication.instance().setFont(app_font)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                fernet = Fernet(self.master_key)
                with open(self.settings_file, 'rb') as file:
                    encrypted_data = file.read()
                decrypted_data = fernet.decrypt(encrypted_data).decode()
                loaded_settings = json.loads(decrypted_data)
                self.settings.update(loaded_settings)
            except Exception:
                QMessageBox.warning(self, "错误", "设置加载失败，可能是密钥不正确或数据已损坏。使用默认设置。")
                self.settings = {
                    "require_master_key": True,
                    "max_attempts": 3,
                    "data_file_location": os.path.abspath(self.data_file),
                    "background_option": "随机背景",
                    "background_image": "",
                    "background_change_frequency": 10,
                    "theme": "暗色",
                    "hide_account": False,
                    "hide_password": False,
                    "hide_more_info": False,
                }
                self.save_settings()
        else:
            self.save_settings()

    def save_settings(self):
        try:
            fernet = Fernet(self.master_key)
            data = json.dumps(self.settings).encode()
            encrypted_data = fernet.encrypt(data)
            with open(self.settings_file, 'wb') as file:
                file.write(encrypted_data)
        except Exception:
            QMessageBox.warning(self, "错误", "设置保存失败！")

    def load_passwords(self):
        data_file_location = self.settings.get("data_file_location", self.data_file)
        if os.path.exists(data_file_location):
            try:
                with open(data_file_location, 'rb') as file:
                    encrypted_data = file.read()
                fernet = Fernet(self.master_key)
                decrypted_data = fernet.decrypt(encrypted_data).decode()
                self.passwords = json.loads(decrypted_data)
                self.update_list()
            except Exception:
                QMessageBox.warning(self, "错误", "数据加载失败，密钥不正确或数据已损坏。")
                self.destroy_data()
        else:
            self.passwords = {}
            self.update_list()

    def save_passwords(self):
        try:
            fernet = Fernet(self.master_key)
            data = json.dumps(self.passwords).encode()
            encrypted_data = fernet.encrypt(data)
            data_file_location = self.settings.get("data_file_location", self.data_file)
            with open(data_file_location, 'wb') as file:
                file.write(encrypted_data)
        except Exception:
            QMessageBox.warning(self, "错误", "数据保存失败！")

    def update_list(self):
        self.list_widget.clear()
        for remark in self.passwords:
            self.list_widget.addItem(remark)

    def add_password(self):
        remark, ok1 = QInputDialog.getText(self, "添加密码", "备注：")
        if not ok1 or not remark:
            return
        if remark in self.passwords:
            QMessageBox.warning(self, "警告", "该备注已存在。")
            return
        account, ok2 = QInputDialog.getText(self, "添加密码", "账号：")
        if not ok2:
            return
        password, ok3 = QInputDialog.getText(self, "添加密码", "密码：")
        if not ok3:
            return

        more_info = {}
        while True:
            reply = QMessageBox.question(self, '添加更多信息', '是否需要为此备注添加更多信息？', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                key, ok4 = QInputDialog.getText(self, "添加更多信息", "信息名称：")
                if not ok4 or not key:
                    break
                value, ok5 = QInputDialog.getText(self, "添加更多信息", "信息内容：")
                if not ok5:
                    break
                more_info[key] = value
            else:
                break

        creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.passwords[remark] = {
            "account": account,
            "password": password,
            "more_info": more_info,
            "creation_time": creation_time
        }
        self.save_passwords()
        self.update_list()

    def delete_password(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择要删除的密码。")
            return
        for item in selected_items:
            remark = item.text()
            del self.passwords[remark]
        self.save_passwords()
        self.update_list()

    def show_details(self, item):
        remark = item.text()
        details = self.passwords.get(remark, {})
        account = details.get("account", "")
        password = details.get("password", "")
        more_info = details.get("more_info", {})
        creation_time = details.get("creation_time", "")

        if self.settings.get("require_master_key", True):
            dialog = PasswordVerificationDialog(self.master_key)
            if dialog.exec() != QDialog.Accepted:
                return

        details_dialog = QDialog(self)
        details_dialog.setWindowTitle("密码详情")
        details_dialog.resize(600, 500)
        dialog_layout = QVBoxLayout()

        basic_info_label = QLabel(f"备注: {remark}\n创建时间: {creation_time}")
        basic_info_label.setWordWrap(True)
        dialog_layout.addWidget(basic_info_label)

        if not self.settings.get("hide_account", False):
            account_layout = QHBoxLayout()
            account_label = QLabel("账号: ")
            self.account_display = QLineEdit()
            self.account_display.setText(account)
            self.account_display.setEchoMode(QLineEdit.Normal)
            self.account_display.setReadOnly(True)
            self.account_toggle_btn = QPushButton()
            self.account_toggle_btn.setIcon(QIcon("icons/view_hidden.png"))  # 使用自定义图标
            self.account_toggle_btn.setCheckable(True)
            self.account_toggle_btn.setFixedWidth(30)
            self.account_toggle_btn.clicked.connect(self.toggle_account_visibility)
            account_layout.addWidget(account_label)
            account_layout.addWidget(self.account_display)
            account_layout.addWidget(self.account_toggle_btn)
            dialog_layout.addLayout(account_layout)

        if not self.settings.get("hide_password", False):
            password_layout = QHBoxLayout()
            password_label = QLabel("密码: ")
            self.password_display = QLineEdit()
            self.password_display.setText(password)
            self.password_display.setEchoMode(QLineEdit.Password)
            self.password_display.setReadOnly(True)
            self.password_toggle_btn = QPushButton()
            self.password_toggle_btn.setIcon(QIcon("icons/view_hidden.png"))  # 使用自定义图标
            self.password_toggle_btn.setCheckable(True)
            self.password_toggle_btn.setFixedWidth(30)
            self.password_toggle_btn.clicked.connect(self.toggle_password_visibility)
            password_layout.addWidget(password_label)
            password_layout.addWidget(self.password_display)
            password_layout.addWidget(self.password_toggle_btn)
            dialog_layout.addLayout(password_layout)

        if not self.settings.get("hide_more_info", False) and more_info:
            more_info_label = QLabel("更多信息:")
            more_info_label.setStyleSheet("font-weight: bold;")
            dialog_layout.addWidget(more_info_label)
            for key, value in more_info.items():
                info_layout = QHBoxLayout()
                info_key_label = QLabel(f"{key}: ")
                info_value_label = QLabel(value)
                info_value_label.setWordWrap(True)
                info_layout.addWidget(info_key_label)
                info_layout.addWidget(info_value_label)
                dialog_layout.addLayout(info_layout)

        buttons_layout = QHBoxLayout()
        if not self.settings.get("hide_account", False):
            copy_account_btn = QPushButton("复制账号")
            copy_account_btn.setIcon(QIcon("icons/copy.png"))  # 使用自定义图标
            copy_account_btn.clicked.connect(lambda: QApplication.clipboard().setText(account))
            buttons_layout.addWidget(copy_account_btn)
        if not self.settings.get("hide_password", False):
            copy_password_btn = QPushButton("复制密码")
            copy_password_btn.setIcon(QIcon("icons/copy.png"))  # 使用自定义图标
            copy_password_btn.clicked.connect(lambda: QApplication.clipboard().setText(password))
            buttons_layout.addWidget(copy_password_btn)
        if not self.settings.get("hide_more_info", False) and more_info:
            # 为每个更多信息添加复制按钮
            for key, value in more_info.items():
                copy_info_btn = QPushButton(f"复制 {key}")
                copy_info_btn.setIcon(QIcon("icons/copy.png"))  # 使用自定义图标
                copy_info_btn.clicked.connect(lambda checked, v=value: QApplication.clipboard().setText(v))
                buttons_layout.addWidget(copy_info_btn)
        close_btn = QPushButton("关闭")
        close_btn.setIcon(QIcon("icons/close.png"))  # 使用自定义图标
        close_btn.clicked.connect(details_dialog.close)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        dialog_layout.addLayout(buttons_layout)

        details_dialog.setLayout(dialog_layout)
        details_dialog.setStyleSheet(self.get_current_theme_stylesheet())
        details_dialog.exec()

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_display.setEchoMode(QLineEdit.Normal)
            self.password_toggle_btn.setIcon(QIcon("icons/view_visible.png"))  # 使用自定义图标
        else:
            self.password_display.setEchoMode(QLineEdit.Password)
            self.password_toggle_btn.setIcon(QIcon("icons/view_hidden.png"))  # 使用自定义图标

    def toggle_account_visibility(self, checked):
        if checked:
            self.account_display.setEchoMode(QLineEdit.Normal)
            self.account_toggle_btn.setIcon(QIcon("icons/view_visible.png"))  # 使用自定义图标
        else:
            self.account_display.setEchoMode(QLineEdit.Password)
            self.account_toggle_btn.setIcon(QIcon("icons/view_hidden.png"))  # 使用自定义图标

    def get_current_theme_stylesheet(self):
        theme = self.settings.get("theme", "暗色")
        if theme == "暗色":
            return """
                QLabel {
                    color: #f0f0f0;
                }
                QLineEdit {
                    background-color: #3c3c3c;
                    color: #f0f0f0;
                    border: 1px solid #555555;
                    border-radius: 4px;
                }
                QPushButton {
                    background-color: #555555;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
            """
        else:
            return ""

    def open_settings(self):
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.exec()
        self.apply_theme()
        self.save_settings()
        self.setup_background_timer()

    def clear_data_files(self):
        reply = QMessageBox.question(self, '确认清除', '确定要一键清除所有数据文件吗？此操作不可撤销！', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(self.settings.get("data_file_location", self.data_file)):
                    os.remove(self.settings.get("data_file_location", self.data_file))
                if os.path.exists(self.settings_file):
                    os.remove(self.settings_file)
                if os.path.exists(SALT_FILE):
                    os.remove(SALT_FILE)
                QMessageBox.information(self, "成功", "所有数据文件已清除。")
                self.passwords = {}
                self.update_list()
                self.settings = {
                    "require_master_key": True,
                    "max_attempts": 3,
                    "data_file_location": os.path.abspath(self.data_file),
                    "background_option": "随机背景",
                    "background_image": "",
                    "background_change_frequency": 10,
                    "theme": "暗色",
                    "hide_account": False,
                    "hide_password": False,
                    "hide_more_info": False,
                }
                self.save_settings()
                self.apply_theme()
                self.setup_background_timer()
            except Exception:
                QMessageBox.warning(self, "错误", "清除数据文件失败。")

    def destroy_data(self):
        try:
            if os.path.exists(self.settings.get("data_file_location", self.data_file)):
                os.remove(self.settings.get("data_file_location", self.data_file))
            if os.path.exists(SETTINGS_FILE):
                os.remove(SETTINGS_FILE)
            if os.path.exists(SALT_FILE):
                os.remove(SALT_FILE)
            QMessageBox.critical(self, "数据已销毁", "由于多次输入错误，所有数据已被销毁。")
            self.close()
        except Exception:
            QMessageBox.warning(self, "错误", "销毁数据文件失败。")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
