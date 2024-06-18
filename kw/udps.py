import socket
import time
import json

print('Starting the UDP sender ~~')
UDPserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPserver.settimeout(5)

def send(detector_data):
    sample_data = json.dumps(detector_data).encode()
    print("TXD :", sample_data)
    XX = UDPserver.sendto(sample_data, ('127.0.0.1', 7072))
    time.sleep(1)
frame_count=0

while True:
    frame_count+=1
    try:
        text= f'\n frm : {frame_count}  '

        send(text)
     
    except Exception as e:
        print("Excepttion Interrupt ~~~", e)
        continue
    except KeyboardInterrupt:
        print("KeyboardInterrupt ~~")
        break
print("Close the UDP server ~~~")
UDPserver.close()