import time
import sysv_ipc

from PySide6.QtCore import QThread
from .voice_utils import play_sound

shm_reverse_data = sysv_ipc.SharedMemory(1235)


class EventHandler(QThread):

    def __init__(self, tcp_client, config):

        super().__init__()
        self.tcp = tcp_client
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

            if not len(list_data) == 12:
                print("!!!!!! len error")
                time.sleep(0.05)
                continue

            if self.pre_frame == list_data[4]:

                ...

            else:

                self.pre_frame = list_data[4]
                
                if not self.reversed:

                    if int(list_data[vel_index]) < 0:
                        self.reverse_cnt = self.reverse_cnt + 1

                    if self.reverse_cnt == self.config.yaml_data['reverse_frame']:
                        print("Reverse Event")
                        self.reverse_cnt = 0
                        self.reversed = True
                        self.tcp.sendMessage(True)
                        play_sound()
            
                else:

                    if int(list_data[vel_index]) == 0:
                        self.release_cnt = self.release_cnt + 1

                    if self.release_cnt == 90:
                        self.release_cnt = 0
                        self.reversed = False
                        self.tcp.sendMessage(False)

                print(f"Reversed : {self.reversed} / rev_cnt : {self.reverse_cnt} / rel_cnt : {self.release_cnt}")

            time.sleep(0.05)
