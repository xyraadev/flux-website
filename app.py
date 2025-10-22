import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import socket
import threading
from datetime import datetime
import os
import uuid

class FluxPCClient:
    def __init__(self):
        # Настройка темы
        ctk.set_appearance_mode("Dark")  # Темная тема
        ctk.set_default_color_theme("blue")  # Синяя цветовая схема
        
        self.root = ctk.CTk()
        self.root.title("FLUX Messenger - PC Version")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Переменные
        self.server_ip = tk.StringVar(value="127.0.0.1")
        self.server_port = tk.StringVar(value="5555")
        self.username = tk.StringVar(value="User")
        self.connected = False
        self.client_socket = None
        
        self.create_ui()
        self.center_window()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_ui(self):
        # Главный контейнер
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Левая панель (список чатов)
        left_frame = ctk.CTkFrame(main_frame, width=200)
        left_frame.pack(side="left", fill="y", padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # Заголовок чатов
        chats_label = ctk.CTkLabel(left_frame, text="Чаты", font=ctk.CTkFont(size=16, weight="bold"))
        chats_label.pack(pady=10)
        
        # Список чатов
        self.chats_list = tk.Listbox(left_frame, bg="#2b2b2b", fg="white", border=0, 
                                   selectbackground="#1f6aa5", font=("Arial", 11))
        self.chats_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.chats_list.insert(tk.END, "Общий чат")
        
        # Правая панель (чат)
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Заголовок чата
        chat_header = ctk.CTkFrame(right_frame, height=50)
        chat_header.pack(fill="x", padx=5, pady=5)
        chat_header.pack_propagate(False)
        
        self.chat_title = ctk.CTkLabel(chat_header, text="Общий чат", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
        self.chat_title.pack(side="left", padx=10, pady=10)
        
        # Статус подключения
        self.status_label = ctk.CTkLabel(chat_header, text="Не подключено", 
                                       text_color="red", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="right", padx=10, pady=10)
        
        # Окно чата
        self.chat_display = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, 
                                                    bg="#1e1e1e", fg="white", 
                                                    font=("Arial", 11), border=0)
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        # Панель ввода
        input_frame = ctk.CTkFrame(right_frame, height=80)
        input_frame.pack(fill="x", padx=5, pady=5)
        input_frame.pack_propagate(False)
        
        self.message_entry = ctk.CTkEntry(input_frame, placeholder_text="Введите сообщение...",
                                        font=ctk.CTkFont(size=12))
        self.message_entry.pack(fill="x", padx=10, pady=10)
        self.message_entry.bind("<Return>", self.send_message)
        
        # Панель кнопок
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.connect_btn = ctk.CTkButton(button_frame, text="Подключиться", 
                                       command=self.toggle_connection)
        self.connect_btn.pack(side="left", padx=(0, 5))
        
        self.send_btn = ctk.CTkButton(button_frame, text="Отправить", 
                                    command=self.send_message)
        self.send_btn.pack(side="left", padx=5)
        
        # Кнопка отправки файла
        self.file_btn = ctk.CTkButton(button_frame, text="📎 Файл", 
                                    width=60, command=self.send_file_dialog)
        self.file_btn.pack(side="left", padx=5)
        
        # Панель настроек
        settings_frame = ctk.CTkFrame(left_frame, height=150)
        settings_frame.pack(fill="x", side="bottom", pady=5)
        settings_frame.pack_propagate(False)
        
        ctk.CTkLabel(settings_frame, text="Настройки:", 
                    font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Поле имени пользователя
        ctk.CTkLabel(settings_frame, text="Имя:").pack(anchor="w", padx=5)
        username_entry = ctk.CTkEntry(settings_frame, textvariable=self.username)
        username_entry.pack(fill="x", padx=5, pady=2)
        
        # Поле IP сервера
        ctk.CTkLabel(settings_frame, text="IP сервера:").pack(anchor="w", padx=5)
        ip_entry = ctk.CTkEntry(settings_frame, textvariable=self.server_ip)
        ip_entry.pack(fill="x", padx=5, pady=2)
        
        # Поле порта
        ctk.CTkLabel(settings_frame, text="Порт:").pack(anchor="w", padx=5)
        port_entry = ctk.CTkEntry(settings_frame, textvariable=self.server_port)
        port_entry.pack(fill="x", padx=5, pady=2)
        
    def send_file_dialog(self):
        """Диалог выбора файла для отправки"""
        if not self.connected:
            self.add_message("Ошибка", "Сначала подключитесь к серверу!")
            return
            
        file_path = filedialog.askopenfilename(
            title="Выберите файл для отправки",
            filetypes=[("Все файлы", "*.*")]
        )
        
        if file_path:
            # Запускаем отправку файла в отдельном потоке
            threading.Thread(target=self.send_file, args=(file_path,), daemon=True).start()
            
    def send_file(self, file_path):
        """Отправка файла на сервер"""
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_id = str(uuid.uuid4())
            
            # Проверяем размер файла (макс. 10 МБ)
            if file_size > 10 * 1024 * 1024:
                self.add_message("Ошибка", "Файл слишком большой (макс. 10 МБ)")
                return
                
            # Отправляем метаданные файла
            file_metadata = {
                "type": "file_metadata",
                "file_id": file_id,
                "file_name": file_name,
                "file_size": file_size,
                "username": self.username.get()
            }
            self.send_json(file_metadata)
            
            # Отправляем сам файл
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(4096)
                    if not chunk:
                        break
                    self.client_socket.send(chunk)
                    
            self.add_message("Система", f"Файл {file_name} отправлен")
            
        except Exception as e:
            self.add_message("Ошибка", f"Ошибка отправки файла: {str(e)}")
            
    def download_file(self, file_id, file_name):
        """Скачивание файла с сервера"""
        try:
            request_data = {
                "type": "file_request",
                "file_id": file_id,
                "file_name": file_name
            }
            self.send_json(request_data)
            
            # Файл будет получен в receive_messages
            self.add_message("Система", f"Запрос на скачивание {file_name} отправлен")
            
        except Exception as e:
            self.add_message("Ошибка", f"Ошибка запроса файла: {str(e)}")
            
    def save_downloaded_file(self, file_data, file_name):
        """Сохранение скачанного файла"""
        try:
            downloads_dir = "downloads"
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
                
            file_path = filedialog.asksaveasfilename(
                initialdir=downloads_dir,
                initialfile=file_name,
                title="Сохранить файл как"
            )
            
            if file_path:
                with open(file_path, 'wb') as file:
                    file.write(file_data)
                self.add_message("Система", f"Файл сохранен: {file_path}")
                
        except Exception as e:
            self.add_message("Ошибка", f"Ошибка сохранения файла: {str(e)}")
            
    def toggle_connection(self):
        if not self.connected:
            self.connect_to_server()
        else:
            self.disconnect_from_server()
            
    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip.get(), int(self.server_port.get())))
            self.connected = True
            
            # Отправляем информацию о пользователе
            join_data = {
                "type": "join",
                "username": self.username.get()
            }
            self.send_json(join_data)
            
            self.status_label.configure(text="Подключено", text_color="green")
            self.connect_btn.configure(text="Отключиться")
            
            # Запускаем поток для приема сообщений
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
            self.add_message("Система", "Успешно подключено к серверу!")
            
        except Exception as e:
            self.add_message("Ошибка", f"Не удалось подключиться: {str(e)}")
            
    def disconnect_from_server(self):
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
                
        self.connected = False
        self.status_label.configure(text="Не подключено", text_color="red")
        self.connect_btn.configure(text="Подключиться")
        self.add_message("Система", "Отключено от сервера")
        
    def send_message(self, event=None):
        if not self.connected:
            self.add_message("Ошибка", "Сначала подключитесь к серверу!")
            return
            
        message = self.message_entry.get().strip()
        if message:
            try:
                message_data = {
                    "type": "message",
                    "username": self.username.get(),
                    "message": message
                }
                self.send_json(message_data)
                self.add_message("Вы", message)
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                self.add_message("Ошибка", f"Не удалось отправить сообщение: {str(e)}")
                
    def send_json(self, data):
        import json
        json_data = json.dumps(data).encode('utf-8')
        header = f"{len(json_data):<1024}".encode('utf-8')
        self.client_socket.send(header + json_data)
        
    def receive_messages(self):
        file_transfer_mode = False
        current_file_data = b""
        current_file_size = 0
        current_file_name = ""
        current_file_id = ""
        
        while self.connected:
            try:
                if file_transfer_mode:
                    # Режим приема файла
                    chunk = self.client_socket.recv(4096)
                    if not chunk:
                        break
                        
                    current_file_data += chunk
                    
                    if len(current_file_data) >= current_file_size:
                        # Файл полностью получен
                        self.root.after(0, lambda: self.save_downloaded_file(current_file_data, current_file_name))
                        
                        # Сбрасываем режим передачи файла
                        file_transfer_mode = False
                        current_file_data = b""
                        current_file_size = 0
                        current_file_name = ""
                        current_file_id = ""
                        
                    continue
                
                # Получаем заголовок
                header = self.client_socket.recv(1024).decode('utf-8')
                if not header:
                    break
                    
                data_length = int(header.strip())
                
                # Получаем данные
                data = b""
                while len(data) < data_length:
                    chunk = self.client_socket.recv(min(4096, data_length - len(data)))
                    if not chunk:
                        break
                    data += chunk
                    
                if data:
                    import json
                    message_data = json.loads(data.decode('utf-8'))
                    
                    message_type = message_data.get("type")
                    
                    if message_type == "message":
                        username = message_data.get("username", "Неизвестный")
                        message = message_data.get("message", "")
                        self.add_message(username, message)
                        
                    elif message_type == "system":
                        message = message_data.get("message", "")
                        self.add_message("Система", message)
                        
                    elif message_type == "file_announce":
                        username = message_data.get("username", "")
                        file_name = message_data.get("file_name", "")
                        file_size = message_data.get("file_size", 0)
                        file_id = message_data.get("file_id", "")
                        
                        # Показываем уведомление о загрузке файла
                        size_mb = file_size / (1024 * 1024)
                        self.add_message("Система", 
                                       f"{username} загружает файл: {file_name} ({size_mb:.2f} MB)")
                                       
                    elif message_type == "file_ready":
                        username = message_data.get("username", "")
                        file_name = message_data.get("file_name", "")
                        file_id = message_data.get("file_id", "")
                        
                        # Показываем файл как доступный для скачивания
                        self.add_file_message(username, file_name, file_id)
                        
                    elif message_type == "file_transfer":
                        # Начинаем прием файла
                        file_transfer_mode = True
                        current_file_name = message_data.get("file_name", "")
                        current_file_size = message_data.get("file_size", 0)
                        current_file_id = message_data.get("file_id", "")
                        current_file_data = b""
                        
                        self.add_message("Система", f"Начинается загрузка файла: {current_file_name}")
                        
            except:
                if self.connected:
                    self.root.after(0, self.disconnect_from_server)
                break
                
    def add_message(self, username, message):
        timestamp = datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {username}: {message}\n"
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, formatted_message)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def add_file_message(self, username, file_name, file_id):
        timestamp = datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {username} отправил файл: {file_name}\n"
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, formatted_message)
        
        # Создаем фрейм для кнопки скачивания
        button_frame = ctk.CTkFrame(self.chat_display)
        
        # Добавляем кнопку для скачивания
        download_btn = ctk.CTkButton(button_frame, text="📥 Скачать", 
                                    command=lambda fid=file_id, fn=file_name: self.download_file(fid, fn))
        download_btn.pack(padx=5, pady=2)
        
        # Вставляем кнопку в текстовое поле
        self.chat_display.window_create(tk.END, window=button_frame)
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FluxPCClient()
    app.run()