
import sysv_ipc
import time
memory=sysv_ipc.SharedMemory(1235)
i=0
pre_frame = -1
while True:
    # text=f'lkw  texts{i}'
     
    val=memory.read()
    vstr= val.decode("utf-8")
    vstr = vstr.partition("\n")[0]
    list_ = vstr.split(" ")
    
    i += 1

    print(len(list_))
    
    if pre_frame == list_[4]:
        ...
    else:
        pre_frame = list_[4]
        print(f"{i} {list_[4]} : {list_[9]}")

    time.sleep(0.1)
