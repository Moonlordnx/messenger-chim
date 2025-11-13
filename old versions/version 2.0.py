import socket
import threading
import struct
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

def get_local_ip():
    """Получение локального IP-адреса компьютера"""
    try:
        # Создаем временное соединение для определения IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        # Если не удалось определить IP, используем hostname
        try:
            return socket.gethostname()
        except:
            return "unknown"

class ChimMessenger:
    def __init__(self, root):
        self.root = root
        self.root.title("Chim Messenger")
        self.root.geometry("600x500")
        self.root.configure(bg='#2b2b2b')
        
        # Автоматическое определение имени пользователя по IP
        self.workstation_id = get_local_ip()
        self.messenger = None
        self.running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        title_frame = tk.Frame(self.root, bg='#2b2b2b')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(
            title_frame, 
            text="Chim Messenger", 
            font=('Arial', 20, 'bold'),
            fg='#4fc3f7',
            bg='#2b2b2b'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Быстрое и легкое общение",
            font=('Arial', 10),
            fg='#b0bec5',
            bg='#2b2b2b'
        )
        subtitle_label.pack()
        
        # Фрейм подключения
        self.connection_frame = tk.Frame(self.root, bg='#37474f', relief='ridge', bd=2)
        self.connection_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(
            self.connection_frame,
            text="Подключение к чату",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#37474f'
        ).pack(pady=5)
        
        input_frame = tk.Frame(self.connection_frame, bg='#37474f')
        input_frame.pack(pady=10)
        
        tk.Label(
            input_frame,
            text="Ваш идентификатор:",
            font=('Arial', 10),
            fg='#ffffff',
            bg='#37474f'
        ).grid(row=0, column=0, padx=5)
        
        self.id_entry = tk.Entry(input_frame, width=20, font=('Arial', 10))
        self.id_entry.grid(row=0, column=1, padx=5)
        self.id_entry.insert(0, self.workstation_id)  # Автозаполнение IP-адресом
        self.id_entry.bind('<Return>', lambda e: self.connect_to_chat())
        
        self.connect_btn = tk.Button(
            input_frame,
            text="Подключиться",
            command=self.connect_to_chat,
            bg='#4caf50',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=12
        )
        self.connect_btn.grid(row=0, column=2, padx=10)
        
        # Информация о пользователе
        info_frame = tk.Frame(self.connection_frame, bg='#37474f')
        info_frame.pack(pady=5)
        
        info_label = tk.Label(
            info_frame,
            text=f"Автоматически определен IP: {self.workstation_id}",
            font=('Arial', 8),
            fg='#b0bec5',
            bg='#37474f'
        )
        info_label.pack()
        
        # Фрейм чата (изначально скрыт)
        self.chat_frame = tk.Frame(self.root, bg='#2b2b2b')
        
        # Область сообщений
        self.messages_area = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=('Arial', 10),
            bg='#1e1e1e',
            fg='#e0e0e0',
            state='disabled'
        )
        self.messages_area.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Фрейм ввода сообщения
        input_frame = tk.Frame(self.chat_frame, bg='#2b2b2b')
        input_frame.pack(pady=10, padx=20, fill='x')
        
        self.message_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            bg='#37474f',
            fg='white',
            insertbackground='white'
        )
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        self.send_btn = tk.Button(
            input_frame,
            text="Отправить",
            command=self.send_message,
            bg='#2196f3',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=10
        )
        self.send_btn.pack(side='right')
        
        # Статус бар
        self.status_var = tk.StringVar(value="Не подключено")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w',
            font=('Arial', 9),
            bg='#263238',
            fg='#cfd8dc'
        )
        status_bar.pack(side='bottom', fill='x')
        
    def connect_to_chat(self):
        """Подключение к multicast чату"""
        self.workstation_id = self.id_entry.get().strip()
        
        if not self.workstation_id:
            messagebox.showerror("Ошибка", "Введите идентификатор")
            return
        
        try:
            self.messenger = MulticastMessenger(self.workstation_id)
            self.running = True
            
            # Запуск потока для прослушивания сообщений
            self.listener_thread = threading.Thread(target=self.listen_messages)
            self.listener_thread.daemon = True
            self.listener_thread.start()
            
            # Переключение на интерфейс чата
            self.connection_frame.pack_forget()
            self.chat_frame.pack(fill='both', expand=True)
            self.status_var.set(f"Подключено как: {self.workstation_id}")
            
            self.add_system_message("Вы подключились к чату")
            
        except Exception as e:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться: {e}")
    
    def send_message(self):
        """Отправка сообщения"""
        message = self.message_entry.get().strip()
        if message and self.messenger:
            # Сразу показываем свое сообщение в чате
            self.add_message(self.workstation_id, message)
            self.messenger.send_message(message)
            self.message_entry.delete(0, tk.END)
    
    def listen_messages(self):
        """Прослушивание входящих сообщений"""
        while self.running and self.messenger:
            try:
                data, addr = self.messenger.sock.recvfrom(1024)
                message = data.decode('utf-8')
                if ':' in message:
                    workstation, msg = message.split(':', 1)
                    if workstation != self.workstation_id:  # Не показывать свои же сообщения
                        # Используем after для безопасного обновления GUI из другого потока
                        self.root.after(0, self.add_message, workstation, msg)
            except Exception as e:
                if self.running:
                    print(f"Ошибка приема: {e}")
    
    def add_message(self, sender, message):
        """Добавление сообщения в чат"""
        self.messages_area.configure(state='normal')
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Форматирование сообщения
        self.messages_area.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Выделяем цветом в зависимости от отправителя
        if sender == self.workstation_id:
            self.messages_area.insert(tk.END, f"{sender}: ", 'my_message')
        else:
            self.messages_area.insert(tk.END, f"{sender}: ", 'sender')
            
        self.messages_area.insert(tk.END, f"{message}\n", 'message')
        
        self.messages_area.configure(state='disabled')
        self.messages_area.see(tk.END)
    
    def add_system_message(self, message):
        """Добавление системного сообщения"""
        self.messages_area.configure(state='normal')
        
        self.messages_area.insert(tk.END, f"● {message}\n", 'system')
        
        self.messages_area.configure(state='disabled')
        self.messages_area.see(tk.END)
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        self.running = False
        if self.messenger:
            self.messenger.running = False
            self.messenger.sock.close()
        self.root.destroy()

class MulticastMessenger:
    def __init__(self, workstation_id, multicast_group='224.1.1.1', port=5007):
        self.workstation_id = workstation_id
        self.multicast_group = multicast_group
        self.port = port
        self.running = True
        
        # Создаем отдельный сокет для отправки
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Устанавливаем TTL для multicast пакетов
        ttl = struct.pack('b', 1)  # TTL = 1 (только локальная сеть)
        self.send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        # Создаем отдельный сокет для приема
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Присоединение к multicast группе для приема
        self.join_multicast_group()
        
    def join_multicast_group(self):
        """Присоединение к multicast группе"""
        # Привязываем сокет к порту
        self.recv_sock.bind(('', self.port))
        
        # Добавляем в multicast группу
        group = socket.inet_aton(self.multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    def send_message(self, message):
        """Отправка сообщения в multicast группу"""
        try:
            message_data = f"{self.workstation_id}:{message}"
            self.send_sock.sendto(
                message_data.encode('utf-8'), 
                (self.multicast_group, self.port)
            )
        except Exception as e:
            print(f"Ошибка отправки: {e}")
    
    @property
    def sock(self):
        """Свойство для обратной совместимости"""
        return self.recv_sock

def main():
    root = tk.Tk()
    app = ChimMessenger(root)
    
    # Настройка тегов для форматирования текста
    app.messages_area.tag_configure('timestamp', foreground='#78909c')
    app.messages_area.tag_configure('sender', foreground='#4fc3f7', font=('Arial', 10, 'bold'))
    app.messages_area.tag_configure('my_message', foreground='#81c784', font=('Arial', 10, 'bold'))
    app.messages_area.tag_configure('message', foreground='#e0e0e0')
    app.messages_area.tag_configure('system', foreground='#ffb74d', font=('Arial', 9, 'italic'))
    
    # Обработка закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Установка фокуса на поле ввода сообщения после подключения
    def focus_message_entry():
        if hasattr(app, 'message_entry'):
            app.message_entry.focus_set()
    
    root.after(100, focus_message_entry)
    
    root.mainloop()

if __name__ == "__main__":
    main()