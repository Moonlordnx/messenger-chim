import sys
import socket
import threading
import struct
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QScrollArea, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont

# Игнорирование предупреждений о deprecated функциях
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def get_local_ip():
    """Получение локального IP-адреса компьютера"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "unknown"

class MessageBubble(QFrame):
    def __init__(self, message, is_own, sender, timestamp, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_own = is_own
        self.sender = sender
        self.timestamp = timestamp
        self.setup_ui()
        
    def setup_ui(self):
        self.setMaximumWidth(400)
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(4)
        
        # Отправитель (только для чужих сообщений)
        if not self.is_own:
            sender_label = QLabel(self.sender)
            sender_label.setStyleSheet("""
                QLabel {
                    color: #0088cc;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 0px;
                }
            """)
            layout.addWidget(sender_label)
        
        # Текст сообщения
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                padding: 0px;
                background: transparent;
            }
        """)
        layout.addWidget(message_label)
        
        # Время отправки
        time_label = QLabel(self.timestamp)
        time_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 11px;
                padding: 0px;
                background: transparent;
            }
        """)
        time_label.setAlignment(Qt.AlignRight if self.is_own else Qt.AlignLeft)
        layout.addWidget(time_label)
        
        self.setLayout(layout)
        
        # Стиль bubble
        if self.is_own:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0088cc, stop:1 #00a884);
                    border-radius: 18px;
                    border: none;
                    padding: 0px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: #2b5278;
                    border-radius: 18px;
                    border: none;
                    padding: 0px;
                }
            """)

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.animate_click()
        super().mousePressEvent(event)
        
    def animate_click(self):
        original_geometry = self.geometry()
        pressed_geometry = QRect(
            original_geometry.x() + 2,
            original_geometry.y() + 2,
            original_geometry.width() - 4,
            original_geometry.height() - 4
        )
        
        self._animation.setStartValue(original_geometry)
        self._animation.setEndValue(pressed_geometry)
        self._animation.start()

class LoginWindow(QMainWindow):
    login_success = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Chim Messenger - Авторизация")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1e3c72, stop:1 #2a5298);
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        
        # Заголовок
        title_label = QLabel("Chim Messenger")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        layout.addWidget(title_label)
        
        # Иконка
        icon_label = QLabel("💬")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 64px;
                padding: 20px;
            }
        """)
        layout.addWidget(icon_label)
        
        # Подзаголовок
        subtitle_label = QLabel("Современный локальный мессенджер")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 16px;
                padding: 10px;
            }
        """)
        layout.addWidget(subtitle_label)
        
        # Поле ввода
        input_widget = QWidget()
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        
        ip_label = QLabel("Ваш идентификатор:")
        ip_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        input_layout.addWidget(ip_label)
        
        self.ip_entry = QLineEdit()
        self.ip_entry.setText(get_local_ip())
        self.ip_entry.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.1);
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 20px;
                padding: 15px;
                color: white;
                font-size: 14px;
                selection-background-color: #0088cc;
            }
            QLineEdit:focus {
                border: 2px solid #0088cc;
            }
        """)
        self.ip_entry.returnPressed.connect(self.login)
        input_layout.addWidget(self.ip_entry)
        
        input_widget.setLayout(input_layout)
        layout.addWidget(input_widget)
        
        # Кнопка входа
        self.login_btn = AnimatedButton("Подключиться к чату")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0088cc, stop:1 #00a884);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0095e0, stop:1 #00b894);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0077b3, stop:1 #009670);
            }
        """)
        self.login_btn.setFixedHeight(50)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        # Информация
        info_label = QLabel("💡 Автоматически определен ваш IP-адрес")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 12px;
                padding: 10px;
            }
        """)
        layout.addWidget(info_label)
        
        central_widget.setLayout(layout)
        
    def login(self):
        username = self.ip_entry.text().strip()
        if username:
            self.login_success.emit(username)

class ChatWindow(QMainWindow):
    message_received = pyqtSignal(str, str, bool)
    
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.messenger = None
        self.setup_ui()
        self.setup_chat()
        
        self.message_received.connect(self.add_message)
        
    def setup_ui(self):
        self.setWindowTitle(f"Chim Messenger - {self.username}")
        self.setGeometry(100, 100, 400, 700)
        self.setMinimumSize(350, 500)
        
        # Основной стиль
        self.setStyleSheet("""
            QMainWindow {
                background: #0e1621;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1e2b3c;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #2b5278;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3d6b99;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Заголовок чата
        self.create_header()
        
        # Область сообщений
        self.create_messages_area()
        
        # Панель ввода
        self.create_input_panel()
        
        central_widget.setLayout(self.main_layout)
        
    def create_header(self):
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background: #1e2b3c;
                border-bottom: 1px solid #2b5278;
            }
        """)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title_label = QLabel("Групповой чат")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(title_label)
        
        self.status_label = QLabel("● онлайн")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00d465;
                font-size: 12px;
            }
        """)
        header_layout.addWidget(self.status_label)
        
        header.setLayout(header_layout)
        self.main_layout.addWidget(header)
        
    def create_messages_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(8)
        self.messages_layout.setContentsMargins(15, 15, 15, 15)
        
        self.messages_widget.setLayout(self.messages_layout)
        self.scroll_area.setWidget(self.messages_widget)
        
        self.main_layout.addWidget(self.scroll_area)
        
    def create_input_panel(self):
        input_widget = QWidget()
        input_widget.setFixedHeight(80)
        input_widget.setStyleSheet("""
            QWidget {
                background: #1e2b3c;
                border-top: 1px solid #2b5278;
            }
        """)
        
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                background: #2b5278;
                border: none;
                border-radius: 20px;
                padding: 12px 20px;
                color: white;
                font-size: 14px;
                selection-background-color: #0088cc;
            }
            QLineEdit:focus {
                border: none;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        
        self.send_btn = AnimatedButton("↑")
        self.send_btn.setFixedSize(50, 50)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0088cc, stop:1 #00a884);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0095e0, stop:1 #00b894);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0077b3, stop:1 #009670);
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        input_widget.setLayout(input_layout)
        self.main_layout.addWidget(input_widget)
        
    def setup_chat(self):
        try:
            self.messenger = MulticastMessenger(self.username)
            # Запуск потока для прослушивания сообщений
            self.listener_thread = threading.Thread(target=self.listen_messages, daemon=True)
            self.listener_thread.start()
            
            # Добавляем приветственное сообщение
            self.add_system_message("Вы подключились к чату")
        except Exception as e:
            self.add_system_message(f"Ошибка подключения: {str(e)}")
        
    def send_message(self):
        message = self.message_input.text().strip()
        if message and self.messenger:
            try:
                self.add_message(self.username, message, True)
                self.messenger.send_message(message)
                self.message_input.clear()
            except Exception as e:
                self.add_system_message(f"Ошибка отправки: {str(e)}")
            
    def listen_messages(self):
        while self.messenger and getattr(self.messenger, 'running', True):
            try:
                data, addr = self.messenger.sock.recvfrom(4096)
                message = data.decode('utf-8', errors='ignore')
                
                if ':' in message:
                    workstation, msg = message.split(':', 1)
                    if workstation != self.username:
                        self.message_received.emit(workstation, msg, False)
                        
            except socket.timeout:
                continue
            except Exception as e:
                if self.messenger and getattr(self.messenger, 'running', True):
                    continue
                
    def add_message(self, sender, message, is_own):
        timestamp = datetime.now().strftime('%H:%M')
        bubble = MessageBubble(message, is_own, sender, timestamp)
        
        # Добавляем сообщение в layout
        if is_own:
            bubble_layout = QHBoxLayout()
            bubble_layout.addStretch()
            bubble_layout.addWidget(bubble)
            self.messages_layout.addLayout(bubble_layout)
        else:
            bubble_layout = QHBoxLayout()
            bubble_layout.addWidget(bubble)
            bubble_layout.addStretch()
            self.messages_layout.addLayout(bubble_layout)
            
        # Прокручиваем к низу
        QTimer.singleShot(50, self.scroll_to_bottom)
        
    def add_system_message(self, message):
        system_label = QLabel(f"⚡ {message}")
        system_label.setAlignment(Qt.AlignCenter)
        system_label.setStyleSheet("""
            QLabel {
                color: #ffb74d;
                font-size: 12px;
                font-style: italic;
                padding: 10px;
                background: rgba(255,183,77,0.1);
                border-radius: 10px;
            }
        """)
        system_label.setMaximumWidth(300)
        
        system_layout = QHBoxLayout()
        system_layout.addStretch()
        system_layout.addWidget(system_label)
        system_layout.addStretch()
        self.messages_layout.addLayout(system_layout)
        
    def scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def closeEvent(self, event):
        if self.messenger:
            self.messenger.close()
        event.accept()

class MulticastMessenger:
    def __init__(self, workstation_id, multicast_group='224.1.1.1', port=5007):
        self.workstation_id = workstation_id
        self.multicast_group = multicast_group
        self.port = port
        self.running = True
        
        # Создаем UDP сокет
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Устанавливаем timeout для избежания блокировки
        self.sock.settimeout(1.0)
        
        # Устанавливаем TTL для multicast
        ttl = struct.pack('b', 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        # Присоединяемся к multicast группе
        self.join_multicast_group()
        
    def join_multicast_group(self):
        try:
            self.sock.bind(('', self.port))
            group = socket.inet_aton(self.multicast_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except Exception as e:
            raise Exception(f"Не удалось присоединиться к multicast группе: {str(e)}")
    
    def send_message(self, message):
        try:
            message_data = f"{self.workstation_id}:{message}"
            self.sock.sendto(
                message_data.encode('utf-8'), 
                (self.multicast_group, self.port)
            )
        except Exception as e:
            raise Exception(f"Ошибка отправки сообщения: {str(e)}")
    
    def close(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass

class MessengerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # Устанавливаем стиль приложения
        self.app.setStyle('Fusion')
        
        self.login_window = LoginWindow()
        self.chat_window = None
        
        self.login_window.login_success.connect(self.open_chat)
        
    def run(self):
        self.login_window.show()
        return self.app.exec_()
        
    def open_chat(self, username):
        self.login_window.close()
        self.chat_window = ChatWindow(username)
        self.chat_window.show()

if __name__ == "__main__":
    # Добавляем фильтр для игнорирования предупреждений
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    messenger = MessengerApp()
    sys.exit(messenger.run())

