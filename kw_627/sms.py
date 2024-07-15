
import sysv_ipc
import time
memory=sysv_ipc.SharedMemory(1234,flags=sysv_ipc.IPC_CREAT|777,size=1000)
i=0
while True:
    text=f'lkw  texts{i}'
    print(text)
    memory.write(text)
    i+=1
    time.sleep(1)