
import sysv_ipc
import time
memory=sysv_ipc.SharedMemory(1235)
i=0
while True:
    # text=f'lkw  texts{i}'
   
    val=memory.read()
    vstr= val.decode("utf-8")
    vstr = vstr.partition("\n")[0]
    print(vstr)
    # print(text)
    i+=1
    time.sleep(.09)
