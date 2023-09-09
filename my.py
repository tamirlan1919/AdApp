import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

class AdvertisementPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

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

        # Create a line edit for inputting the interval (in seconds) between media changes
        self.interval_edit = QLineEdit(self)
        self.interval_edit.setPlaceholderText('Введите интервал в секундах')
        layout.addWidget(self.interval_edit)

        # Set the layout in the main widget
        self.central_widget.setLayout(layout)

        # Create a timer for changing media based on the selected interval
        self.media_timer = QTimer(self)
        self.media_timer.timeout.connect(self.show_next_media)

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
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdvertisementPlayer()
    window.showFullScreen()
    sys.exit(app.exec_())
