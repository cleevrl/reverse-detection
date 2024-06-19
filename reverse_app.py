import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QCheckBox, QSpinBox, QButtonGroup, QRadioButton, QPushButton, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QLabel

from utils.config_parser import ConfigParser
from utils.serial_broker import SerialBroker
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

    def __init__(self, config, serial_broker):
        super().__init__('Config')
        self.config = config
        self.serial_broker = serial_broker
        self.initUI()
    
    def initUI(self):
        
        self.rbtn_disable = QRadioButton('Disable')
        self.rbtn_1_min = QRadioButton('1M')
        self.rbtn_5_min = QRadioButton('5M')
        self.rbtn_10_min = QRadioButton('10M')
        self.rbtn_30_min = QRadioButton('30M')
        self.rbtn_1_hour = QRadioButton('1H')

        self.btn_group_reset = QButtonGroup()
        self.btn_group_reset.addButton(self.rbtn_disable)
        self.btn_group_reset.addButton(self.rbtn_1_min)
        self.btn_group_reset.addButton(self.rbtn_5_min)
        self.btn_group_reset.addButton(self.rbtn_10_min)
        self.btn_group_reset.addButton(self.rbtn_30_min)
        self.btn_group_reset.addButton(self.rbtn_1_hour)

        self.init_radio_button()

        self.btn_group_reset.buttonClicked.connect(self.config_reset)
        
        # reverse frame
        self.spb_reverse_frame = QSpinBox()
        self.spb_reverse_frame.setMinimum(1)
        self.spb_reverse_frame.setMaximum(50)
        self.spb_reverse_frame.valueChanged.connect(self.config_reverse_frame)

        # reverse direction
        self.cb_rev_direction = QCheckBox("\u2191")
        self.cb_rev_direction.stateChanged.connect(self.toggle_rev_direction)

        self.spb_reverse_frame.setValue(self.config.yaml_data['reverse_frame'])
        self.cb_rev_direction.setChecked(self.config.yaml_data['rev_direction'])

        config_gbox = QGridLayout()
        config_gbox.addWidget(QLabel("Reverse Frame : "), 0, 0)
        config_gbox.addWidget(self.spb_reverse_frame, 0, 1)
        config_gbox.addWidget(QLabel("Rev Direction : "), 0, 2)
        config_gbox.addWidget(self.cb_rev_direction, 0, 3)

        config_gbox.addWidget(QLabel("Reset Cycle : "), 1, 0)
        config_gbox.addWidget(self.rbtn_disable, 1, 1)
        config_gbox.addWidget(self.rbtn_1_min, 1, 2)
        config_gbox.addWidget(self.rbtn_5_min, 1, 3)
        config_gbox.addWidget(self.rbtn_10_min, 2, 1)
        config_gbox.addWidget(self.rbtn_30_min, 2, 2)
        config_gbox.addWidget(self.rbtn_1_hour, 2, 3)

        self.setLayout(config_gbox)

    def toggle_rev_direction(self, state):

        if state == 2:
            self.config.set_rev_direction(True)
            self.cb_rev_direction.setText("\u2193")
        else:
            self.config.set_rev_direction(False)
            self.cb_rev_direction.setText("\u2191")

    def config_reverse_frame(self, value):

        self.config.set_reverse_frame(value)

    def config_reset(self, button):

        self.config.set_reset_mode(button.text())
        self.serial_broker.reset_mode = button.text()

    def init_radio_button(self):
        for btn in self.btn_group_reset.buttons():
            if btn.text() == self.config.yaml_data['reset_mode']:
                btn.setChecked(True)

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

        self.config = ConfigParser()

        self.serial_broker = SerialBroker()
        self.serial_broker.start()
        self.tcp_client = TCPThread()
        self.tcp_client.start()
        self.handler = EventHandler(self.tcp_client, self.config)
        self.handler.start()

        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Reverse Detector - DBICT')
        
        self.btn_exit = QPushButton('EXIT')
        self.btn_exit.clicked.connect(self.exit)

        status_widget = StatusWidget()
        config_widget = ConfigWidget(self.config, self.serial_broker)
        test_widget = TestWidget(self.tcp_client)

        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.btn_exit)

        btn_widget = QWidget()
        btn_widget.setLayout(btn_hbox)

        main_vbox = QVBoxLayout()
        main_vbox.addWidget(status_widget)
        main_vbox.addWidget(config_widget)
        main_vbox.addWidget(test_widget)
        main_vbox.addWidget(btn_widget)

        self.setLayout(main_vbox)

    def exit(self):
        self.config.save_yaml()
        self.tcp_client.exit()
        self.handler.exit()
        self.close()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
