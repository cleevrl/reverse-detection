import sys
import socket
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QLabel

from utils.dbict_udp import UDPThread, vms_message

class UDPWidget(QGroupBox):

    def __init__(self):
        super().__init__('UDP (HOST : PORT)')

        self.initUI()
        self.timer = QTimer()

        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

        self.udp_thread = UDPThread()
        self.udp_thread.start()

    def initUI(self):

        self.lb_recv = QLabel("RECV <- ")
        self.le_recv_host = QLineEdit()
        self.le_recv_port = QLineEdit()

        self.lb_send = QLabel("SEND -> ")
        self.le_send_host = QLineEdit()
        self.le_send_port = QLineEdit()

        self.btn_recv = QPushButton("RECV")
        self.btn_send = QPushButton("SEND")

        self.btn_recv.clicked.connect(self.recvUDP)
        self.btn_send.clicked.connect(self.sendUDP)

        udp_gbox = QGridLayout()
        udp_gbox.addWidget(self.lb_recv, 0, 0)
        udp_gbox.addWidget(self.le_recv_host, 0, 1)
        udp_gbox.addWidget(QLabel(" : "), 0, 2)
        udp_gbox.addWidget(self.le_recv_port, 0, 3)
        udp_gbox.addWidget(self.btn_recv, 0, 4)
        udp_gbox.addWidget(self.lb_send, 1, 0)
        udp_gbox.addWidget(self.le_send_host, 1, 1)
        udp_gbox.addWidget(QLabel(" : "), 1, 2)
        udp_gbox.addWidget(self.le_send_port, 1, 3)
        udp_gbox.addWidget(self.btn_send, 1, 4)

        self.setLayout(udp_gbox)

    def update(self):
        ...

    def recvUDP(self):
        ...
        self.udp_thread.enable_recv = True

    def sendUDP(self):
        ...
        self.udp_thread.enable_send = True

    def __del__(self):
        self.udp_thread.exit()


class TestWidget(QGroupBox):

    def __init__(self):
        super().__init__('for TEST')
        self.initUI()

    def initUI(self):

        self.btn_test_vms = QPushButton('VMS')
        self.btn_test_vms.setCheckable(True)
        btn_test_voice = QPushButton('VOICE')
        btn_test_reverse = QPushButton('REVERSE')

        self.btn_test_vms.clicked[bool].connect(self.toggle_vms)

        test_hbox = QHBoxLayout()
        test_hbox.addWidget(self.btn_test_vms)
        test_hbox.addWidget(btn_test_voice)
        test_hbox.addWidget(btn_test_reverse)

        self.setLayout(test_hbox)

    def toggle_vms(self, e):

        host = '0.0.0.0'
        port = 1234

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            if e:
                s.sendto(vms_message(False), (host, port))
                self.btn_test_vms.setChecked(True)
                
            else:
                s.sendto(vms_message(True), (host, port))
                self.btn_test_vms.setChecked(False)

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Reverse Detector - DBICT')
        
        self.btn_exit = QPushButton('EXIT')
        self.btn_exit.clicked.connect(self.exit)

        status_widget = UDPWidget()
        test_widget = TestWidget()

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
        self.close()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
