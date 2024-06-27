import time
import sysv_ipc

from PySide6.QtCore import QThread, Signal
from .voice_utils import play_sound
from .tcp_sender import send_tcp

shm_reverse_data = sysv_ipc.SharedMemory(1235)


class EventHandler(QThread):

    sig_quit = Signal()

    def __init__(self, config, app):

        super().__init__()
        self.app = app
        self.config = config

        self.reversed = False
        self.pre_frame = -1
        self.reverse_cnt = 0
        self.release_cnt = 0

        self.halt_cnt = 0

    def run(self):

        while True:

            data = shm_reverse_data.read()
            str_data = data.decode("utf-8")
            str_data = str_data.partition("\n")[0]
            list_data = str_data.split(" ")

            if self.config.yaml_data['rev_direction']:
                vel_index = 7
            else:
                vel_index = 9

            if not len(list_data) == 12 or self.pre_frame == list_data[4]:
                self.halt_cnt = self.halt_cnt + 1
                if self.halt_cnt == 20 * 600:
                    print("***** Quit App due to no response!!!! *****")
                    self.sig_quit.emit()
                time.sleep(0.05)
                continue

            else:

                self.halt_cnt = 0
                self.pre_frame = list_data[4]
                
                if not self.reversed:

                    if abs(int(list_data[vel_index])) > 0:
                        self.reverse_cnt = self.reverse_cnt + 1
                    else:
                        self.reverse_cnt = 0

                    if self.reverse_cnt == self.config.yaml_data['reverse_frame']:
                        print("Reverse Event")
                        self.reverse_cnt = 0
                        self.reversed = True
                        send_tcp(self.config.yaml_data['vms_host'], self.config.yaml_data['vms_port'], self.reversed)
                        play_sound()
            
                else:

                    if int(list_data[vel_index]) == 0:
                        self.release_cnt = self.release_cnt + 1

                    if self.release_cnt == 90:
                        self.release_cnt = 0
                        self.reversed = False
                        send_tcp(self.config.yaml_data['vms_host'], self.config.yaml_data['vms_port'], self.reversed)

                print(f"Reversed : {self.reversed} / rev_cnt : {self.reverse_cnt} / rel_cnt : {self.release_cnt}")

            time.sleep(0.05)
