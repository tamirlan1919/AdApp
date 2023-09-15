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
from PyQt5.QtCore import QMetaObject, Qt
from PyQt5.QtCore import Qt, QTimer, QUrl, QObject, pyqtSignal
from PyQt5.QtCore import Qt, QTimer, QUrl, QObject, pyqtSignal, QMetaObject, Q_ARG

try:
    token = '6329551488:AAHLaNLS9jLjdFknA7DbECkmWI1jEDhXoDA'
    bot=telebot.TeleBot(token)
except:
    print('Нет доступа к сети')


class AdvertisementPlayer(QMainWindow):


    def __init__(self):
        super().__init__()
        # Проверяем наличие папки "media" и создаем её, если она отсутствует
        media_folder = 'media'
        if not os.path.exists(media_folder):
            os.makedirs(media_folder)
        self.schedule_disk_check()
        self.initUI()
        self.schedule_disk_check()
        
    def run_media_timer(self):
        self.media_timer.timeout.connect(self.show_next_media)
        self.media_timer.start(self.interval * 1000)

    def initUI(self):
        self.playback_timer_interval = 60 * 1000  # в миллисекундах (1 минута)
        self.last_playback_time = QDateTime.currentDateTime()
        self.interval = 3  # Интервал по умолчанию в секундах
        self.playing = False  # Флаг для отслеживания воспроизведения
        self.player_started = False  # Флаг для отслеживания команды /start

        self.media_timer = QTimer(self)  # Создайте QTimer для медиа-таймера
        self.media_timer.timeout.connect(self.show_next_media)

                # Create a timer for changing media based on the selected interval
        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self.check_playback_status)
        self.playback_timer.start(self.playback_timer_interval)
        self.last_playback_time = QDateTime.currentDateTime()
        # Оставляем только QLabel для отображения медиаматериала
        self.setWindowTitle('Плеер рекламы')
        self.setGeometry(0, 0, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.media_label = QLabel(self)
        self.media_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.media_label)

        self.central_widget.setLayout(layout)

        self.media_files = self.load_media_files("media")
        self.current_media_index = 0

        self.media_player = None
        self.video_widget = None
        self.video_playing = False
        self.video_stopped = False
        self.auto_change_interval = 0
        try:
            self.telegram_bot_token = '6329551488:AAHLaNLS9jLjdFknA7DbECkmWI1jEDhXoDA'
            self.bot = telebot.TeleBot(token=self.telegram_bot_token)
        except:
            print('Нет досутпа к сети')

    def load_media_files(self, directory):
        media_files = []
        for filename in os.listdir(directory):
            if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mkv')):
                media_files.append(os.path.join(directory, filename))
        return media_files

    def show_media(self, index):
        if 0 <= index < len(self.media_files):
            media_file = self.media_files[index]
            if media_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                if self.media_player:
                    self.media_player.stop()
                    self.central_widget.layout().removeWidget(self.video_widget)
                    self.video_widget.deleteLater()
                    self.media_player.deleteLater()
                    self.media_player = None

                pixmap = QPixmap(media_file)
                pixmap = pixmap.scaled(self.media_label.size(), Qt.KeepAspectRatio)
                self.media_label.setPixmap(pixmap)
                self.video_playing = False
                self.video_stopped = True

            elif media_file.lower().endswith(('.mp4', '.avi', '.mkv')):
                if not self.media_player:
                    self.media_player = QMediaPlayer()
                    self.video_widget = QVideoWidget()
                    self.media_player.setVideoOutput(self.video_widget)
                    self.central_widget.layout().addWidget(self.video_widget)

                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(media_file)))
                self.video_widget.setFullScreen(True)
                self.media_player.play()
                self.video_playing = True
                self.video_stopped = False
                self.media_player.stateChanged.connect(self.media_player_state_changed)
                self.media_timer.stop()
            else:
                self.media_label.setText("Неподдерживаемый формат файла")

            self.last_playback_time = QDateTime.currentDateTime()

    def start_media_timer(self):
        QMetaObject.invokeMethod(self.media_timer, "start", Qt.QueuedConnection, Q_ARG(int, self.interval * 1000))

    def stop_media_timer(self):
        QMetaObject.invokeMethod(self.media_timer, "stop", Qt.QueuedConnection)



    def show_next_media(self):
        self.current_media_index += 1
        if self.current_media_index >= len(self.media_files):
            self.current_media_index = 0
        self.show_media(self.current_media_index)


    def start_media_change(self):
        # Start changing media automatically based on the selected interval
        interval = self.media_timer
        self.auto_change_interval = interval  # Сохраните интервал

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
                self.video_playing = False  # Устанавливаем флаг video_playing в False
                interval = self.auto_change_interval
                self.media_timer.start(interval * 1000)
                self.show_next_media()
            else:
                # Если видео было воспроизведено до конца, начать таймер для следующего медиафайла
                self.video_playing = False  # Устанавливаем флаг video_playing в False
                interval = self.auto_change_interval
                self.media_timer.start(interval * 1000)
                
  
        elif state == QMediaPlayer.PlayingState:
            # Video playback has started, stop the interval timer
            self.media_timer.stop()
            self.video_playing = True  # Устанавливаем флаг video_playing в True
        elif state == QMediaPlayer.PausedState:  # Добавьте обработку состояния паузы
            # Если видео было приостановлено пользователем, начать таймер
            self.media_timer.start(self.auto_change_interval * 1000)


            
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
        try:
            schedule.every(2).minutes.do(self.check_yandex_disk)
        except:
            print('Нет доступа к сети')

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

        if time_difference > 5 and not self.video_playing:  # 300 секунд = 5 минут
            # Если время безуспешного воспроизведения превышает 5 минут, отправьте уведомление в Telegram
            chat_id = '5455171373'  # Замените на ID вашего чата или пользователя
            message = 'Воспроизведение не работает в течение более 5 минут на компьютере.'
            self.send_telegram_notification(chat_id, message)

    def set_interval(self, interval):
            # Функция для установки интервала через Telegram бота
        self.interval = interval
        self.media_timer.stop()
        self.media_timer.start(interval * 1000)

    def start_playback(self):
            # Функция для старта воспроизведения через Telegram бота
        self.playing = True
        self.auto_change_interval = self.interval
        if not self.video_playing:  # Only start the timer if video is not playing
            self.media_timer.start(self.interval * 1000)  # Convert to milliseconds
        yandex_disk_folder = '/media'  # Путь к папке на Яндекс.Диске
        save_folder = 'media/'  # Путь к папке на вашем компьютере
        try:
            self.download_all_files_from_folder(yandex_disk_folder, save_folder)
        except:
            print('Нет доступа к сети')

    def stop_playback(self):
            # Функция для остановки воспроизведения через Telegram бота
        self.playing = False
        self.media_timer.stop()


def run_bot_thread():
    # Обработчики команд для Telegram бота
    @bot.message_handler(commands=['start'])
    def start(message):
        # Обработчик команды /start
        window.player_started = True  # Set the player started flag to True
        window.start_playback()
        window.start_media_timer()  # Start the media timer
        bot.send_message(message.chat.id, 'Воспроизведение медиаматериала начато.')

    @bot.message_handler(commands=['stop'])
    def stop(message):
        # Обработчик команды /stop
        window.stop_playback()
        window.stop_media_timer()  # Stop the media timer
        bot.send_message(message.chat.id, 'Воспроизведение медиаматериала остановлено.')

    @bot.message_handler(commands=['set_interval'])
    def set_interval(message):
        # Обработчик команды /set_interval
        try:
            interval = int(message.text.split()[-1])
            window.set_interval(interval)
            bot.send_message(message.chat.id, f'Интервал установлен на {interval} секунд.')
        except ValueError:
            bot.send_message(message.chat.id, 'Некорректное значение интервала.')

    bot.polling()

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверять каждую минуту, чтобы уменьшить нагрузку


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdvertisementPlayer()
    window.showFullScreen()
    try:
        bot = telebot.TeleBot(token='6329551488:AAHLaNLS9jLjdFknA7DbECkmWI1jEDhXoDA')  # Replace with your actual bot token
    except:
        print('Нет досутпа к сети')

        # Создайте и запустите отдельный поток для выполнения расписания
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True  # Поток завершится, когда завершится главный поток
    schedule_thread.start()
    try:
        # Start the Telegram bot thread
        bot_thread = threading.Thread(target=run_bot_thread)
        bot_thread.daemon = True
        bot_thread.start()
    except:
        print('Нет досутпа к сети')



    sys.exit(app.exec_())