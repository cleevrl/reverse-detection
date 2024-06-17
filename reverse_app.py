import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QLabel

from utils.tcp_sender import TCPThread
from utils.event_handler import EventHandler
from utils.voice_utils import play_sound

class StatusWidget(QGroupBox):

    def __init__(self):
        super().__init__('Status')

        self.counter = 0
        
        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def initUI(self):

        self.status = QLabel(f"TEST : {self.counter}")
        status_gbox = QGridLayout()
        status_gbox.addWidget(self.status, 0, 0)

        self.setLayout(status_gbox)

    def update(self):
        self.counter = self.counter + 1
        self.status.setText(f"TEST : {self.counter}")


class ConfigWidget(QGroupBox):

    def __init__(self):
        super().__init__('Config')

        self.initUI()
    
    def initUI(self):
        ...


class TestWidget(QGroupBox):

    def __init__(self, tcp_client):
        super().__init__('for TEST')
        self.tcp_client = tcp_client
        self.initUI()

    def initUI(self):

        self.btn_test_vms = QPushButton('VMS')
        self.btn_test_vms.setCheckable(True)
        btn_test_voice = QPushButton('VOICE')
        self.btn_test_reverse = QPushButton('REVERSE')
        self.btn_test_reverse.setCheckable(True)

        self.btn_test_vms.clicked[bool].connect(self.toggle_vms)
        btn_test_voice.clicked.connect(play_sound)
        self.btn_test_reverse.clicked[bool].connect(self.force_reversed)

        test_hbox = QHBoxLayout()
        test_hbox.addWidget(self.btn_test_vms)
        test_hbox.addWidget(btn_test_voice)
        test_hbox.addWidget(self.btn_test_reverse)

        self.setLayout(test_hbox)

    def toggle_vms(self, e):

        self.tcp_client.sendMessage(e)
        self.btn_test_vms.setChecked(e)

    def force_reversed(self, e):

        self.tcp_client.sendMessage(e)
        if e:
            play_sound()
        self.btn_test_reverse.setChecked(e)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.tcp_client = TCPThread()
        self.tcp_client.start()
        self.handler = EventHandler()
        self.handler.start()

        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Reverse Detector - DBICT')
        
        self.btn_exit = QPushButton('EXIT')
        self.btn_exit.clicked.connect(self.exit)

        status_widget = StatusWidget()
        test_widget = TestWidget(self.tcp_client)

        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.btn_exit)

        btn_widget = QWidget()
        btn_widget.setLayout(btn_hbox)

        main_vbox = QVBoxLayout()
        main_vbox.addWidget(status_widget)
        main_vbox.addWidget(test_widget)
        main_vbox.addWidget(btn_widget)

        self.setLayout(main_vbox)

    def exit(self):
        self.tcp_client.exit()
        self.handler.exit()
        self.close()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
