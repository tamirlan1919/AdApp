import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import os
from yadisk import YaDisk
import schedule
import time
import threading
from PyQt5.QtCore import QTimer, QDateTime, Qt
import telebot
import socket


class AdvertisementPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.schedule_disk_check()

    def initUI(self):
        self.setWindowTitle('Плеер рекламы')
        self.setGeometry(0, 0, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        # Create a label for displaying media (image or video)
        self.media_label = QLabel(self)
        self.media_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.media_label)

        # Create a toolbar
        self.create_toolbar()
        self.playback_timer_interval = 60 * 1000  # в миллисекундах (1 минута)
        self.last_playback_time = QDateTime.currentDateTime()
        # Create a line edit for inputting the interval (in seconds) between media changes
        self.interval_edit = QLineEdit(self)
        self.interval_edit.setPlaceholderText('Введите интервал в секундах')
        layout.addWidget(self.interval_edit)

        # Set the layout in the main widget
        self.central_widget.setLayout(layout)


        self.last_playback_time = QDateTime.currentDateTime()
        

        self.telegram_bot_token = '6329551488:AAHLaNLS9jLjdFknA7DbECkmWI1jEDhXoDA'
        self.bot = telebot.TeleBot(token=self.telegram_bot_token)


        # Create a timer for changing media based on the selected interval
        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self.check_playback_status)

                # Создайте таймер для автоматической смены медиафайлов
        self.media_timer = QTimer(self)
        self.media_timer.timeout.connect(self.show_next_media)

        # Начните таймер при старте приложения
        self.playback_timer.start(self.playback_timer_interval)

        # Initialize the list of media files from the "media" folder
        self.media_files = self.load_media_files("media")

        # Index of the current media
        self.current_media_index = 0

        # Initialize the media player and video widget
        self.media_player = None
        self.video_widget = None
        self.video_playing = False
        self.video_stopped = False  # Добавлено флаг для отслеживания окончания видео

        # Show the first media
        self.show_media(self.current_media_index)



    def create_toolbar(self):
        self.toolbar = QWidget(self)
        self.toolbar.setGeometry(10, 10, 200, 50)

        # Button to start automatic media change
        self.start_button = QPushButton('Старт', self.toolbar)
        self.start_button.setGeometry(0, 0, 80, 30)
        self.start_button.clicked.connect(self.start_media_change)

        # Button to stop automatic media change
        self.stop_button = QPushButton('Стоп', self.toolbar)
        self.stop_button.setGeometry(90, 0, 80, 30)
        self.stop_button.clicked.connect(self.stop_media_change)

    def load_media_files(self, directory):
        # Get a list of files in the specified folder
        media_files = []
        for filename in os.listdir(directory):
            if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mkv')):
                media_files.append(os.path.join(directory, filename))
        return media_files

        
    def show_media(self, index):
        if 0 <= index < len(self.media_files):
            media_file = self.media_files[index]
            if media_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                # Display images or GIFs
                if self.media_player:
                    # If a video is playing, stop it and remove the video widget
                    self.media_player.stop()
                    self.central_widget.layout().removeWidget(self.video_widget)
                    self.video_widget.deleteLater()
                    self.media_player.deleteLater()
                    self.media_player = None

                pixmap = QPixmap(media_file)

                # Scale the pixmap to fit the QLabel
                pixmap = pixmap.scaled(self.media_label.size(), Qt.KeepAspectRatio)

                self.media_label.setPixmap(pixmap)
                self.video_playing = False  # Set video_playing to False for images
                self.video_stopped = True  # Установить флаг окончания видео в True
                # Disconnect the mediaPlayerStateChanged signal if it was connected
                if self.media_player:
                    self.media_player.stateChanged.disconnect(self.media_player_state_changed)
            elif media_file.lower().endswith(('.mp4', '.avi', '.mkv')):
                # Play videos
                if not self.media_player:
                    # If no media player exists, create one
                    self.media_player = QMediaPlayer()
                    self.video_widget = QVideoWidget()
                    self.media_player.setVideoOutput(self.video_widget)
                    self.central_widget.layout().addWidget(self.video_widget)

                # Set the media content and play the video
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(media_file)))
                self.video_widget.setFullScreen(True)  # Display video in fullscreen
                self.media_player.play()
                self.video_playing = True  # Set video_playing to True for videos
                self.video_stopped = False  # Установить флаг окончания видео в False
                # Connect the mediaPlayerStateChanged signal to the handler
                self.media_player.stateChanged.connect(self.media_player_state_changed)
                # Остановить таймер перед воспроизведением видео
                self.media_timer.stop()
            else:
                self.media_label.setText("Неподдерживаемый формат файла")

            self.last_playback_time = QDateTime.currentDateTime()


    def show_next_media(self):
        # Switch to the next media
        self.current_media_index += 1
        if self.current_media_index >= len(self.media_files):
            self.current_media_index = 0
        self.show_media(self.current_media_index)
    

    def start_media_change(self):
        # Start changing media automatically based on the selected interval
        interval = int(self.interval_edit.text())
        
        if not self.video_playing:  # Only start the timer if video is not playing
            self.media_timer.start(interval * 1000)  # Convert to milliseconds
            # После запуска таймера, вы можете добавить вызов функции для скачивания файлов
            # из папки на Яндекс.Диске в указанную папку на вашем компьютере
        yandex_disk_folder = '/media'  # Путь к папке на Яндекс.Диске
        save_folder = 'media/'  # Путь к папке на вашем компьютере
        self.download_all_files_from_folder(yandex_disk_folder, save_folder)


    def stop_media_change(self):
        # Stop changing media
        self.media_timer.stop()

        
    def media_player_state_changed(self, state):
        # Handler for mediaPlayerStateChanged signal
        if state == QMediaPlayer.StoppedState:
            # Video playback has stopped
            if not self.video_stopped:
                # Если видео не было воспроизведено до конца, переключиться на следующий медиафайл
                self.show_next_media()
            else:
                # Если видео было воспроизведено до конца, начать таймер для следующего медиафайла
                interval = int(self.interval_edit.text())
                self.media_timer.start(interval * 1000)
        elif state == QMediaPlayer.EndOfMedia:
            # Video playback has reached the end
            self.video_stopped = True
            # Здесь добавляем код для переключения на следующий медиафайл
            self.show_next_media()
            
    def download_all_files_from_folder(self, yandex_disk_folder, save_folder):
        try:
            y = YaDisk(token='y0_AgAEA7qj-qbFAAp4SgAAAADsTMC1KDDnuQpYREyJJczUd61LFjWErLI')

            items = y.listdir(yandex_disk_folder)
            for item in items:
                if item.is_file():
                    file_name = item.name
                    save_path = os.path.join(save_folder, file_name)

                    # Проверяем, существует ли файл с таким же именем в целевой папке
                    if not os.path.exists(save_path):
                        y.download(item.path, save_path)
                        print(f'Файл "{file_name}" успешно скачан и сохранен в {save_path}')
                    else:
                        print(f'Файл "{file_name}" уже существует в целевой папке, пропускаем его.')

        except Exception as e:
            print(f'Ошибка при скачивании файлов: {str(e)}')
          # После загрузки файлов обновляем список медиафайлов
        self.media_files = self.load_media_files("media")

    def schedule_disk_check(self):
        # Расписание для проверки Яндекс.Диска каждые 30 минут
        schedule.every(2).minutes.do(self.check_yandex_disk)

    def check_yandex_disk(self):

        print("Проверка новых файлов на Яндекс.Диске и удаление старых файлов...")
        # Получите список всех файлов на Яндекс.Диске
        yandex_disk_files = set()
        yandex_disk_folder = '/media'  # Путь к папке на Яндекс.Диске
        try:
            y = YaDisk(token='y0_AgAEA7qj-qbFAAp4SgAAAADsTMC1KDDnuQpYREyJJczUd61LFjWErLI')
            items = y.listdir(yandex_disk_folder)
            for item in items:
                if item.is_file():
                    yandex_disk_files.add(item.name)
        except Exception as e:
            print(f'Ошибка при получении списка файлов на Яндекс.Диске: {str(e)}')

        # Получите список всех файлов в локальной папке
        local_files = set()
        save_folder = 'media/'  # Путь к папке на вашем компьютере
        for filename in os.listdir(save_folder):
            local_files.add(filename)

        # Удалите локальные файлы, которых нет на Яндекс.Диске
        files_to_delete = local_files - yandex_disk_files
        for file_to_delete in files_to_delete:
            file_path = os.path.join(save_folder, file_to_delete)
            try:
                os.remove(file_path)
                print(f'Файл "{file_to_delete}" удален из локальной папки.')
            except Exception as e:
                print(f'Ошибка при удалении файла "{file_to_delete}": {str(e)}')

        # Проверка и скачивание новых файлов с Яндекс.Диска
        self.download_all_files_from_folder(yandex_disk_folder, save_folder)

    def send_telegram_notification(self, chat_id, message):
        # Отправка уведомления в Telegram с указанием IP-адреса компьютера
        try:
            # Получите IP-адрес текущего компьютера
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)

            # Добавьте IP-адрес к сообщению
            message_with_ip = f'{message}\n\nIP-адрес компьютера: {ip_address}'

            self.bot.send_message(chat_id, message_with_ip)
            print('Уведомление отправлено в Telegram.')
        except Exception as e:
            print('Ошибка отправки уведомления в Telegram:', str(e))

    def check_playback_status(self):
        # Проверьте состояние воспроизведения и время последнего успешного воспроизведения
        current_time = QDateTime.currentDateTime()
        time_difference = self.last_playback_time.secsTo(current_time)

        if time_difference > 30:  # 300 секунд = 5 минут
            # Если время безуспешного воспроизведения превышает 5 минут, отправьте уведомление в Telegram
            chat_id = '5455171373'  # Замените на ID вашего чата или пользователя
            message = 'Воспроизведение не работает в течение более 5 минут на компьютере.'
            self.send_telegram_notification(chat_id, message)



def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверять каждую минуту, чтобы уменьшить нагрузку


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdvertisementPlayer()
    window.showFullScreen()
    
    # Создайте и запустите отдельный поток для выполнения расписания
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True  # Поток завершится, когда завершится главный поток
    schedule_thread.start()
    
    sys.exit(app.exec_())